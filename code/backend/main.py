from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File
from flask import Response
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uvicorn
from sqlalchemy import create_engine, Column, String, Text, Integer, TIMESTAMP, func, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.mysql import JSON
from fastapi import UploadFile, File, Form
from backend.model.rag import answer

# 数据库配置123
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


class DBFile(Base):
    __tablename__ = "files"
    file_id = Column(String(255), primary_key=True)
    file_name = Column(String(255), nullable=False)
    file_description = Column(Text)
    file_content = Column(LargeBinary, nullable=False)
    uploaded_at = Column(TIMESTAMP, server_default=func.now())


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

    answer_text, reference, reference_links = answer(request.current_question, request.previous_questions)

    # 保存问题到数据库
    db_question = DBQuestion(
        session_id=request.session_id,
        question_id=request.question_id,
        previous_questions=request.previous_questions,
        current_question=request.current_question,
        answer=answer_text,
        reference=reference,
        reference_links=reference_links,
        rating=None
    )
    db.add(db_question)
    db.commit()

    # 模拟响应数据
    return {
        "session_id": request.session_id,
        "question_id": request.question_id,
        "answer": answer_text,
        "references": reference,
        "reference_links": reference_links
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


@app.post("/api/v1/files/upload")
async def upload_file(
        file_name: str = Form(...),  # 明确声明来自表单
        file: UploadFile = File(...),  # 明确声明为文件上传
        db: Session = Depends(get_db)
):
    file_content = await file.read()
    file_record = DBFile(
        file_id=f"file-{int(datetime.now().timestamp())}",
        file_name=file_name,
        file_content=file_content,
        file_description=""
    )
    db.add(file_record)
    db.commit()

    return {"file_id": file_record.file_id}


@app.get("/api/v1/files/list")
async def list_files(db: Session = Depends(get_db)):
    files = db.query(DBFile).all()
    return {
        "files": [{"file_id": file.file_id, "file_name": file.file_name, "file_description": file.file_description} for
                  file in files]}


@app.get("/api/v1/files/download/{file_id}")
async def download_file(file_id: str, db: Session = Depends(get_db)):
    file_record = db.query(DBFile).filter(DBFile.file_id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    return Response(content=file_record.file_content,
                    media_type="application/octet-stream",
                    headers={"Content-Disposition": f"attachment; filename={file_record.file_name}"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
