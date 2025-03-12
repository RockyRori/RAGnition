from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uvicorn
from sqlalchemy import create_engine, Column, String, Text, Integer, TIMESTAMP, func, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.mysql import JSON

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


@app.post("/api/v1/files/upload")
async def upload_file(file_name: str = Field(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_content = await file.read()
    file_id = f"file-{int(datetime.now().timestamp())}"

    new_file = DBFile(
        file_id=file_id,
        file_name=file_name,
        file_content=file_content,
        file_description=""
    )
    db.add(new_file)
    db.commit()

    return {"file_id": file_id}


@app.get("/api/v1/files/list")
async def list_files(db: Session = Depends(get_db)):
    files = db.query(DBFile).all()
    return {"files": [{"file_id": file.file_id, "file_name": file.file_name, "file_description": file.file_description} for file in files]}


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

