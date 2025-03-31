from typing import List, Tuple

from backend.model.ask_llm import get_llm_answer
from backend.model.doc_analysis import splitting
from backend.model.doc_search import search_documents, load_segments_from_folder
from backend.model.model import LLMModel
from backend.model.ques_assemble import generate_search_query

# RAG回答用户提问
import time


def answer(question: str, history: List[str]) -> Tuple[str, List[str]]:
    # Measure splitting time
    start_split = time.time()
    # 拆分文档，预先完成
    # splitting()
    split_time = time.time() - start_split

    # Measure query generation time
    start_generate = time.time()
    search_query, assembled_question = generate_search_query(question, history)
    generate_time = time.time() - start_generate

    # Measure document search time
    start_search = time.time()
    input_folder = "C:/File/岭南大学/Project/RAGnition/code/backend/model/pieces"
    references = search_documents(search_query,
                                  load_segments_from_folder(input_folder=input_folder),
                                  top_k=4)
    search_time = time.time() - start_search

    # Measure LLM response time
    start_llm = time.time()
    answer_text = get_llm_answer(assembled_question, references, LLMModel.QWEN_PLUS)
    llm_time = time.time() - start_llm

    # Print timing results
    print(f"1. Document Splitting Time: {split_time:.2f}s")
    print(f"2. Query Generation Time: {generate_time:.2f}s")
    print(f"3. Document Search Time: {search_time:.2f}s")
    print(f"4. LLM Response Generation Time: {llm_time:.2f}s")

    return answer_text, references


if __name__ == "__main__":
    answer_text, reference = answer("how can I graduate from lingnan university", [""])
    print("answer_text: \t", answer_text)
    print("reference: \t", reference)
