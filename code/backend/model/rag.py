from typing import List, Tuple

from backend.model.ask_llm import get_llm_answer
from backend.model.doc_analysis import splitting
from backend.model.doc_search import search_documents, load_segments_from_folder
from backend.model.ques_assemble import generate_search_query


# RAG回答用户提问
def answer(question: str, history: List[str]) -> Tuple[str, List[str]]:
    # 拆分文档，预先完成。
    # splitting()
    # 识别用户问题
    search_query, assembled_question = generate_search_query(question, history)
    # 从现有资料库中查找段落
    input_folder = "C:/File/岭南大学/Project/RAGnition/code/backend/model/pieces"
    references = search_documents(search_query, load_segments_from_folder(input_folder=input_folder), top_k=4)

    # 把用户问题和参考资料打包发给大模型拼装回答
    answer_text = get_llm_answer(assembled_question, references)

    return answer_text, references


if __name__ == "__main__":
    answer_text, reference = answer("how can I graduate from lingnan university", [""])
    print("answer_text: \t", answer_text)
    print("reference: \t", reference)
