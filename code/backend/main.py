import io
import mimetypes
import os
import random
import json
from urllib.parse import unquote

import uvicorn
import markdown as md_lib
import mammoth

from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse, HTMLResponse, PlainTextResponse
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime, timezone
from fastapi.responses import StreamingResponse

from backend.model.doc_analysis import split
from backend.model.rag_stream import stream_answer
from sqlalchemy import create_engine, Column, String, Text, Integer, TIMESTAMP, func, LargeBinary, text, orm, Index
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.mysql import JSON

from backend.model.ques_assemble import generate_search_query
from backend.model.doc_search import search_documents, load_segments_from_folder
from backend.root_path import PIECES_DIR, locate_path, policy_file, piece_file, piece_dir

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
    # 复合主键 (base, file_name)
    base = Column(String(28), primary_key=True, nullable=False, server_default="lingnan",
                  comment="文件来源于哪个知识库")
    file_name = Column(String(255), primary_key=True, nullable=False, comment="文件名称")
    file_description = Column(Text, comment="文件简介")
    file_path = Column(String(512), nullable=False, comment="文件在存储系统里的路径或 URL")
    file_size = Column(String(28), nullable=False, comment="文件大小")
    uploaded_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.current_timestamp(),
        comment="上传/更新文件时间"
    )
    __table_args__ = (
        # 加速按 base 查询
        Index("idx_base", "base"),
    )


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


# @app.post("/api/v1/questions", response_model=QuestionResponse)
# async def ask_question(request: QuestionRequest, db: Session = Depends(get_db)):
#     last_question = db.query(DBQuestion).filter(
#         DBQuestion.session_id == request.session_id
#     ).order_by(DBQuestion.created_at.desc()).first()
#
#     if last_question and (datetime.now() - last_question.created_at).total_seconds() < 1:
#         raise HTTPException(
#             status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#             detail="请求过于频繁"
#         )
#
#     db_session = db.query(DBSession).filter(DBSession.session_id == request.session_id).first()
#     if not db_session:
#         db_session = DBSession(session_id=request.session_id)
#         db.add(db_session)
#         db.commit()
#
#     answer_text, references = answer(request.current_question, request.previous_questions)
#
#     db_question = DBQuestion(
#         session_id=request.session_id,
#         question_id=request.question_id,
#         previous_questions=request.previous_questions,
#         current_question=request.current_question,
#         answer=answer_text,
#         references=references,
#         rating=None
#     )
#     db.add(db_question)
#     db.commit()
#
#     return {
#         "session_id": request.session_id,
#         "question_id": request.question_id,
#         "answer": answer_text,
#         "references": references
#     }


@app.get("/api/v1/questions/stream")
async def stream_question(session_id, question_id, previous_questions, current_question: str, language="en",
                          base="lingnan"):
    previous_questions_list = json.loads(previous_questions)

    # 检索向量
    search_query, assembled_question, generate_time = await generate_search_query(current_question,
                                                                                  previous_questions_list)

    # 参考文献
    references, search_time = await search_documents(search_query,
                                                     load_segments_from_folder(input_folder=piece_dir(base=base)))

    # 生成流式回答
    async def event_generator():
        async for token in stream_answer(assembled_question, generate_time, references, search_time,
                                         target_language=language):
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
                "file_name": file.file_name,
                "file_description": file.file_description,
                "file_path": file.file_path,
                "file_size": file.file_size,
                "uploaded_at": file.uploaded_at,
                "base": file.base
            }
            for file in files
        ]
    }


@app.post("/api/v1/files")
async def upload_file(
        base: str = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    size_kb = len(content) / 1024
    file_size = f"{size_kb:.1f}KB" if size_kb < 1024 else f"{size_kb / 1024:.1f}MB"

    # 文件保存到 policies 目录
    policies_dir = locate_path("knowledge_base", base, "policies")
    os.makedirs(policies_dir, exist_ok=True)
    pieces_dir = locate_path("knowledge_base", base, "pieces")
    os.makedirs(pieces_dir, exist_ok=True)

    policy_path = policy_file(base=base, filename=file.filename)
    pieces_path = piece_dir(base=base)

    with open(policy_path, "wb") as f:
        f.write(content)

    file_description = await split(policy_path, pieces_path)

    # 先看看同名文件是否已存在
    existing = (
        db.query(DBFile)
        .filter(DBFile.base == base,
                DBFile.file_name == file.filename)
        .first()
    )
    if existing:
        existing.file_size = file_size
        existing.file_description = file_description
        existing.uploaded_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return {
            "base": existing.base,
            "file_name": existing.file_name,
            "file_description": existing.file_description,
            "file_path": existing.file_path,
            "uploaded_at": existing.uploaded_at,
            "file_size": existing.file_size,
            "message": "Existing file overwritten"
        }

    # 不存在则新建，显式传入 base，让 SQL 默认值生效也会回填
    new_file = DBFile(
        base=base,
        file_name=file.filename,
        file_description=file_description,
        file_path=policy_path,
        file_size=file_size
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return {
        "base": new_file.base,
        "file_name": new_file.file_name,
        "file_description": new_file.file_description,
        "file_path": new_file.file_path,
        "uploaded_at": new_file.uploaded_at,
        "file_size": new_file.file_size,
        "message": "File uploaded"
    }


@app.get("/api/v1/files/preview")
async def preview_file(
        file_name: str = Query(...),
        base: str = Query(...)
):
    clean_name = unquote(file_name)
    file_path = policy_file(base=base, filename=unquote(file_name))
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")

    ext = os.path.splitext(clean_name)[1].lower()

    # --- PDF 直接流式返回，让浏览器原生渲染 ---
    if ext == ".pdf":
        f = open(file_path, "rb")
        return StreamingResponse(f, media_type="application/pdf",
                                 headers={"Content-Disposition": f'inline; filename="{clean_name}"'})

    # --- Markdown 转 HTML ---
    if ext in {".md", ".markdown"}:
        text = open(file_path, "r", encoding="utf-8").read()
        html = md_lib.markdown(text, extensions=["fenced_code", "tables"])
        return HTMLResponse(content=html, media_type="text/html")

    # --- DOCX 转 HTML（使用 mammoth） ---
    if ext == ".docx":
        with open(file_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value  # 生成的 HTML
        return HTMLResponse(content=html, media_type="text/html")

    # --- 其它纯文本类型（.txt/.csv/...） ---
    if ext in {".txt", ".csv"}:
        text = open(file_path, "r", encoding="utf-8").read()
        return PlainTextResponse(text)

    # --- 其它二进制，直接下载 ---
    f = open(file_path, "rb")
    mt, _ = mimetypes.guess_type(clean_name)
    return StreamingResponse(f, media_type=mt or "application/octet-stream",
                             headers={"Content-Disposition": f'attachment; filename="{clean_name}"'})


@app.delete("/api/v1/files")
async def delete_file(
        base: str = Query(...),
        file_name: str = Query(...),
        db: Session = Depends(get_db)
):
    # 查找数据库记录
    existing = (
        db.query(DBFile)
        .filter(DBFile.base == base, DBFile.file_name == file_name)
        .first()
    )

    if not existing:
        raise HTTPException(status_code=404, detail="File not found in database")

    # 构造文件路径
    policy_path = policy_file(base=base, filename=file_name)

    deleted_path = os.path.basename(policy_path)
    file_base, _ = os.path.splitext(deleted_path)
    output_format = "txt"
    pieces_path = os.path.join(piece_dir(base=base), f"{file_base}_segmented.{output_format}")

    # 删除 policy 文件
    if os.path.exists(policy_path):
        os.remove(policy_path)

    # 删除 pieces 文件
    if os.path.exists(pieces_path):
        os.remove(pieces_path)

    # 删除数据库记录
    db.delete(existing)
    db.commit()

    return {
        "base": base,
        "file_name": file_name,
        "message": "File and related data deleted successfully"
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
