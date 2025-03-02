from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uvicorn
from sqlalchemy import create_engine, Column, String, Text, Integer, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.mysql import JSON

# 数据库配置
DATABASE_URL = "mysql+mysqlconnector://root:qwertyuiop@localhost:3306/ragnition"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# 数据库模型
class DBSession(Base):
    __tablename__ = "sessions"
    session_id = Column(String(255), primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_activity = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class DBQuestion(Base):
    __tablename__ = "questions"
    session_id = Column(String(255), primary_key=True)
    question_id = Column(String(255), primary_key=True)
    previous_questions = Column(JSON)
    current_question = Column(Text)
    answer = Column(Text)
    reference = Column(JSON)
    reference_links = Column(JSON)
    rating = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())


Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS配置
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 数据模型
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


class FeedbackRequest(BaseModel):
    session_id: str
    question_id: str
    rating: int = Field(..., ge=1, le=10)


class FeedbackResponse(BaseModel):
    session_id: str
    question_id: str


@app.post("/api/v1/questions", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest, db: Session = Depends(get_db)):
    # 频率限制检查
    last_question = db.query(DBQuestion).filter(
        DBQuestion.session_id == request.session_id
    ).order_by(DBQuestion.created_at.desc()).first()

    if last_question and (datetime.now() - last_question.created_at).total_seconds() < 1:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁"
        )

    # 创建或更新会话
    db_session = db.query(DBSession).filter(DBSession.session_id == request.session_id).first()
    if not db_session:
        db_session = DBSession(session_id=request.session_id)
        db.add(db_session)
        db.commit()

    # 保存问题到数据库
    db_question = DBQuestion(
        session_id=request.session_id,
        question_id=request.question_id,
        previous_questions=request.previous_questions,
        current_question=request.current_question,
        answer="",  # 这里需要替换为实际的回答生成逻辑
        reference=[],
        reference_links=[],
        rating=None
    )
    db.add(db_question)
    db.commit()

    # 模拟响应数据
    return {
        "session_id": request.session_id,
        "question_id": request.question_id,
        "answer": f"这是『1』对‘{request.current_question}’的示例『2』回答",
        "references": [
            "参考片段1：根据XX规定...",
            "参考片段2：根据YY政策...",
            "参考片段3：https://example.com"
        ],
        "reference_links": [
            "http://example.com/doc1",
            "http://example.com/doc2"
        ]
    }


@app.post("/api/v1/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    # 更新评分
    db_question = db.query(DBQuestion).filter(
        DBQuestion.session_id == feedback.session_id,
        DBQuestion.question_id == feedback.question_id
    ).first()

    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到对应问题"
        )

    db_question.rating = feedback.rating
    db.commit()

    return {
        "session_id": feedback.session_id,
        "question_id": feedback.question_id
    }


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
