import io
import mimetypes
import os
import random
import json
import uvicorn

from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Form, Query
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime, timezone
from fastapi.responses import StreamingResponse

from backend.model.doc_analysis import split
from backend.model.rag_stream import stream_answer
from sqlalchemy import create_engine, Column, String, Text, Integer, TIMESTAMP, func, LargeBinary, text, orm
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.mysql import JSON
from backend.model.rag import answer
from backend.model.ques_assemble import generate_search_query
from backend.model.doc_search import search_documents, load_segments_from_folder
from backend.root_path import PIECES_DIR, locate_path, policy_file, piece_file

# 数据库配置
DATABASE_URL = "mysql+mysqlconnector://root:qwertyuiop@localhost:3306/ragnition"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = orm.declarative_base()


# 数据库模型
class DBSession(Base):
    __tablename__ = "sessions"
    session_id = Column(String(28), primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_activity = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class DBQuestion(Base):
    __tablename__ = "questions"
    session_id = Column(String(28), primary_key=True)
    question_id = Column(String(28), primary_key=True)
    previous_questions = Column(JSON)
    current_question = Column(Text)
    answer = Column(Text)
    references = Column(JSON)  # 更新字段名
    rating = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())


class DBFile(Base):
    __tablename__ = "files"
    base = Column(String(28), nullable=False, server_default="lingnan")
    file_id = Column(String(28), primary_key=True)
    file_name = Column(String(255), nullable=False)
    file_description = Column(Text)
    file_content = Column(LargeBinary, nullable=False)
    file_size = Column(String(28), nullable=False)
    uploaded_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


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
async def list_files(
        base: str = Query("lingnan"),
        db: Session = Depends(get_db)
):
    # 只查询指定 base 下的文件
    files = (
        db.query(DBFile)
        .filter(DBFile.base == base)
        .all()
    )

    return {
        "files": [
            {
                "file_id": file.file_id,
                "file_name": file.file_name,
                "file_description": file.file_description,
                "file_size": file.file_size,
                "uploaded_at": file.uploaded_at,
                "base": file.base
            }
            for file in files
        ]
    }


def generate_file_id() -> str:
    """生成 file_id: file- + YYYYMMDDHHMMSS + 三位随机数"""
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    rand_part = f"{random.randint(0, 999):03d}"
    return f"file-{date_part}-{rand_part}"


@app.post("/api/v1/files")
async def upload_file(
        base: str = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    file_id = generate_file_id()
    size_kb = len(content) / 1024
    file_size = f"{size_kb:.1f}KB" if size_kb < 1024 else f"{size_kb / 1024:.1f}MB"

    # 文件保存到 policies 目录
    policies_dir = locate_path("knowledge_base", base, "policies")
    os.makedirs(policies_dir, exist_ok=True)
    pieces_dir = locate_path("knowledge_base", base, "pieces")
    os.makedirs(pieces_dir, exist_ok=True)

    policy_path = policy_file(base=base, filename=file.filename)
    pieces_path = piece_file(base=base, filename=file.filename)

    with open(policy_path, "wb") as f:
        f.write(content)

    file_description = split(policy_path, pieces_path)

    # 先看看同名文件是否已存在
    existing = (
        db.query(DBFile)
        .filter(DBFile.base == base,
                DBFile.file_name == file.filename)
        .first()
    )
    if existing:
        existing.file_content = content
        existing.file_size = file_size
        existing.file_description = file_description
        existing.uploaded_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return {
            "base": existing.base,
            "file_id": existing.file_id,
            "file_name": existing.file_name,
            "file_description": existing.file_description,
            "uploaded_at": existing.uploaded_at,
            "file_size": existing.file_size,
            "message": "Existing file overwritten"
        }

    # 不存在则新建，显式传入 base，让 SQL 默认值生效也会回填
    new_file = DBFile(
        base=base,
        file_id=file_id,
        file_name=file.filename,
        file_description=file_description,
        file_content=content,
        file_size=file_size
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return {
        "base": new_file.base,
        "file_id": new_file.file_id,
        "file_name": new_file.file_name,
        "file_description": new_file.file_description,
        "uploaded_at": new_file.uploaded_at,
        "file_size": new_file.file_size,
        "message": "File uploaded"
    }


@app.get("/api/v1/files/{file_id}/preview")
async def preview_file(
        file_id: str,
        base: str = Query("lingnan"),
        db: Session = Depends(get_db)
):
    # 1. 查库：按 base + file_id 唯一定位
    file = (
        db.query(DBFile)
        .filter(DBFile.base == base, DBFile.file_id == file_id)
        .first()
    )
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # 2. 根据后缀猜 MIME 类型，默认 application/octet-stream
    mime_type, _ = mimetypes.guess_type(file.file_name)
    mime_type = mime_type or "application/octet-stream"

    # 3. 返回 StreamingResponse，把二进制直接流给前端，设置 inline 以内嵌预览
    headers = {
        "Content-Disposition": f'inline; filename="{file.file_name}"'
    }
    return StreamingResponse(
        io.BytesIO(file.file_content),
        media_type=mime_type,
        headers=headers
    )


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
