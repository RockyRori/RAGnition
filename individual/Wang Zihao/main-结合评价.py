from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uvicorn
from sqlalchemy import create_engine, Column, String, Text, Integer, TIMESTAMP, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.mysql import JSON
from sentence_transformers import SentenceTransformer  # WZH: 新增依赖
import numpy as np
import logging

# ====================== 配置部分（需修改） ======================
DATABASE_URL = "mysql+mysqlconnector://root:qwertyuiop@localhost:3306/ragnition"  #!!!!! 数据库连接信息
# ==============================================================

# ====================== 初始化数据库 ======================
Base = declarative_base()

class DBSession(Base):
    """会话记录表"""
    __tablename__ = "sessions"
    session_id = Column(String(255), primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_activity = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class DBQuestion(Base):
    """问题记录表（已添加评估字段）"""
    __tablename__ = "questions"
    session_id = Column(String(255), primary_key=True)
    question_id = Column(String(255), primary_key=True)
    previous_questions = Column(JSON)
    current_question = Column(Text)
    answer = Column(Text)
    reference = Column(JSON)
    reference_links = Column(JSON)
    rating = Column(Integer)        # WZH: 用户评分（1-5）
    cosine_score = Column(Float)     # WZH: 余弦相似度评分
    created_at = Column(TIMESTAMP, server_default=func.now())

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)  # 注：若表已存在需手动添加字段
# ========================================================

# ====================== 余弦评估模块 ======================
class CosineEvaluator:
    """答案质量评估器"""
    def __init__(self):
        # WZH: 嵌入模型配置（与独立脚本一致）
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')  #!!!!! 可更换模型
    
    def evaluate(self, generated_answer: str, reference_answer: str) -> float:
        """计算余弦相似度"""
        emb_gen = self.model.encode(generated_answer)
        emb_ref = self.model.encode(reference_answer)
        return float(np.dot(emb_gen, emb_ref).round(4))
# ========================================================

# ====================== 精标数据集检索 ======================
def get_reference_answer(question: str) -> str:
    """从精标数据集中获取参考答案（示例实现）"""
    #!!!!! 需根据实际数据源修改此函数
    reference_data = {
        "岭南大学地址": "广东省广州市番禺区外环西路230号",
        "岭南大学王牌专业": "商科、数据科学、社会科学",
        "岭南大学成立年份": "1888年"
    }
    return reference_data.get(question, "暂无标准答案")
# ========================================================

app = FastAPI()

# ====================== CORS配置 ======================
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# =======================================================

# ====================== 依赖项 ======================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# ====================================================

# ====================== 数据模型 ======================
class QuestionRequest(BaseModel):
    session_id: str = Field(..., min_length=6)
    question_id: str = Field(..., min_length=10)
    previous_questions: List[str] = []
    current_question: str = Field(..., min_length=1)

class QuestionResponse(BaseModel):
    session_id: str
    question_id: str
    answer: str
    references: List[str]
    reference_links: List[str]
    cosine_score: float  # WZH: 返回评估分数

class FeedbackRequest(BaseModel):
    session_id: str
    question_id: str
    rating: int = Field(..., ge=1, le=5)  # WZH: 评分范围1-5

class FeedbackResponse(BaseModel):
    session_id: str
    question_id: str
# ====================================================

# ====================== 核心接口 ======================
@app.post("/api/v1/questions", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest, db: Session = Depends(get_db)):
    # 频率限制检查
    last_question = db.query(DBQuestion).filter(
        DBQuestion.session_id == request.session_id
    ).order_by(DBQuestion.created_at.desc()).first()
    
    if last_question and (datetime.now() - last_question.created_at).total_seconds() < 1:
        raise HTTPException(status_code=429, detail="请求过于频繁")

    # 创建/更新会话
    db_session = db.query(DBSession).filter(DBSession.session_id == request.session_id).first()
    if not db_session:
        db_session = DBSession(session_id=request.session_id)
        db.add(db_session)
        db.commit()

    # 生成答案（假设answer()函数已实现）
    answer_text, reference, reference_links = answer(request.current_question, request.previous_questions)  #!!!!! 需替换为实际生成逻辑
    
    # 余弦相似度评估
    reference_answer = get_reference_answer(request.current_question)
    evaluator = CosineEvaluator()
    cosine_score = evaluator.evaluate(answer_text, reference_answer)

    # 保存到数据库
    db_question = DBQuestion(
        session_id=request.session_id,
        question_id=request.question_id,
        previous_questions=request.previous_questions,
        current_question=request.current_question,
        answer=answer_text,
        reference=reference,
        reference_links=reference_links,
        cosine_score=cosine_score,  # WZH: 新增字段
        rating=None
    )
    db.add(db_question)
    db.commit()

    return {
        "session_id": request.session_id,
        "question_id": request.question_id,
        "answer": answer_text,
        "references": reference,
        "reference_links": reference_links,
        "cosine_score": cosine_score  # WZH: 返回评估结果
    }

@app.post("/api/v1/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    db_question = db.query(DBQuestion).filter(
        DBQuestion.session_id == feedback.session_id,
        DBQuestion.question_id == feedback.question_id
    ).first()
    
    if not db_question:
        raise HTTPException(status_code=404, detail="未找到对应问题")
    
    db_question.user_rating = feedback.rating
    db.commit()
    
    return {"session_id": feedback.session_id, "question_id": feedback.question_id}

@app.get("/api/v1/sessions")
async def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(DBSession).all()
    return {
        "sessions": [{
            "session_id": session.session_id,
            "last_activity": session.last_activity,
            "question_count": db.query(DBQuestion).filter(
                DBQuestion.session_id == session.session_id
            ).count()
        } for session in sessions]
    }
# ====================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)