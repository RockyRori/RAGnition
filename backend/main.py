from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()


class QuestionRequest(BaseModel):
    question: str


class FeedbackRequest(BaseModel):
    question_id: int
    rating: int
    comments: str


@app.post("/api/v1/questions")
async def ask_question(request: QuestionRequest):
    """
    用户提问接口：
    输入包括当前会话窗口id、多轮对话历史问题列表和当前对话问题
    输出包括当前会话窗口id、当前回答、回答参考的原文片段列表和回答引用的原文链接列表
    """
    session_id = request.session_id
    previous_questions = request.previous_questions
    current_question = request.current_question

    # 返回的硬编码数据（可以根据需求修改为从模型或数据库获取）
    answer = "This is a hardcoded response to the question."
    references = [
        "Reference 1: Content snippet from the policy document.",
        "Reference 2: Content snippet from the campus rules."
    ]
    reference_links = [
        "http://example.com/policy1",
        "http://example.com/rules"
    ]

    return {
        "session_id": session_id,
        "answer": answer,
        "references": references,
        "reference_links": reference_links
    }

# Define the input schema for the request body
class QuestionRequest(BaseModel):
    session_id: str
    previous_questions: list
    current_question: str



@app.post("/api/v1/feedback")
async def submit_feedback(request: FeedbackRequest):
    return {"message": "Thank you for your feedback."}


@app.post("/api/v1/policies/upload")
async def upload_policy():
    return {"message": "Policy document uploaded successfully."}


@app.get("/api/v1/policies")
async def get_policies():
    return [
        {"policy_id": 1, "title": "Thesis Submission Rules", "published_at": "2024-12-01"},
        {"policy_id": 2, "title": "Student Conduct Policy", "published_at": "2024-11-15"}
    ]


# To run the application with `uvicorn`, add the line below
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
