import os

from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime
import uvicorn
from fastapi.responses import StreamingResponse
from backend.model.rag_stream import stream_answer
import json
from sqlalchemy import create_engine, Column, String, Text, Integer, TIMESTAMP, func, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.mysql import JSON
from backend.model.rag import answer
from backend.model.ques_assemble import generate_search_query
from backend.model.doc_search import search_documents, load_segments_from_folder
from backend.root_path import PROJECT_ROOT, PIECES_DIR

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
    references = Column(JSON)  # 更新字段名
    rating = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())


class DBFile(Base):
    __tablename__ = "files"
    file_id = Column(String(255), primary_key=True)
    file_name = Column(String(255), nullable=False)
    file_description = Column(Text)
    file_content = Column(LargeBinary, nullable=False)
    uploaded_at = Column(TIMESTAMP, server_default=func.now())
    file_size = Column(String(50), nullable=False)  # 新增字段


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
    references: List[Dict[str, str]]


class FeedbackRequest(BaseModel):
    session_id: str
    question_id: str
    rating: int = Field(..., ge=1, le=10)


class FeedbackResponse(BaseModel):
    session_id: str
    question_id: str


@app.post("/api/v1/questions", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest, db: Session = Depends(get_db)):
    last_question = db.query(DBQuestion).filter(
        DBQuestion.session_id == request.session_id
    ).order_by(DBQuestion.created_at.desc()).first()

    if last_question and (datetime.now() - last_question.created_at).total_seconds() < 1:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁"
        )

    db_session = db.query(DBSession).filter(DBSession.session_id == request.session_id).first()
    if not db_session:
        db_session = DBSession(session_id=request.session_id)
        db.add(db_session)
        db.commit()

    answer_text, references = answer(request.current_question, request.previous_questions)

    db_question = DBQuestion(
        session_id=request.session_id,
        question_id=request.question_id,
        previous_questions=request.previous_questions,
        current_question=request.current_question,
        answer=answer_text,
        references=references,
        rating=None
    )
    db.add(db_question)
    db.commit()

    return {
        "session_id": request.session_id,
        "question_id": request.question_id,
        "answer": answer_text,
        "references": references
    }


@app.get("/api/v1/questions/stream")
async def stream_question(session_id: str, question_id: str, current_question: str, previous_questions: str):
    previous_questions_list = json.loads(previous_questions)

    search_query, _ = generate_search_query(current_question, previous_questions_list)
    input_folder = PIECES_DIR
    references = search_documents(search_query,
                                  load_segments_from_folder(input_folder=input_folder),
                                  top_k=4)

    async def event_generator():
        async for token in stream_answer(current_question, previous_questions_list):
            yield f"data: {json.dumps({'token': token})}\n\n"

        # 发送引用文献消息，字段名为 references
        yield f"data: {json.dumps({'references': references})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/v1/files/list")
async def list_files(db: Session = Depends(get_db)):
    files = db.query(DBFile).all()
    return {
        "files": [
            {
                "file_id": file.file_id,
                "file_name": file.file_name,
                "file_description": file.file_description,
                "uploaded_at": file.uploaded_at,
                "file_size": file.file_size
            }
            for file in files
        ]
    }


@app.post("/api/v1/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    question = db.query(DBQuestion).filter(
        DBQuestion.session_id == request.session_id,
        DBQuestion.question_id == request.question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="问题不存在"
        )

    if question.rating is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该问题已经评分过"
        )

    question.rating = request.rating
    db.commit()

    return {
        "session_id": request.session_id,
        "question_id": request.question_id
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8536)
