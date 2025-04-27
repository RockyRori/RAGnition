import os

from backend.model.llm_stream_tongyiqianwen import stream_qwen_plus_query
from backend.model.doc_analysis import splitting
from backend.model.doc_search import search_documents, load_segments_from_folder
from backend.model.ques_assemble import generate_search_query
from backend.model.model import LLMModel
import time
import asyncio
import json

from backend.model.translation import sync_translate, async_translate
from backend.root_path import PROJECT_ROOT, PIECES_DIR


async def stream_answer(question: str, history: list):
    # Measure splitting time
    start_split = time.time()
    # 拆分文档，预先完成
    # splitting()
    split_time = time.time() - start_split

    # Measure query generation time
    start_generate = time.time()
    question = await async_translate(question)
    search_query, assembled_question = generate_search_query(question, history)
    generate_time = time.time() - start_generate

    # Measure document search time
    start_search = time.time()
    input_folder = PIECES_DIR
    references = search_documents(search_query,
                                  load_segments_from_folder(input_folder=input_folder),
                                  top_k=4)
    search_time = time.time() - start_search

    # Measure LLM response time
    start_llm = time.time()
    llm_time = time.time() - start_llm

    # Print timing results
    print(f"1. Document Splitting Time: {split_time:.2f}s")
    print(f"2. Query Generation Time: {generate_time:.2f}s")
    print(f"3. Document Search Time: {search_time:.2f}s")
    print(f"4. LLM Response Generation Time: {llm_time:.2f}s")

    prompt = f"""You are a helpful assistant.
If you think the none of the references are related to the question, please only return this double quotation marked sentence "目前为止小助手没有查询到岭南大学有相关政策，很抱歉我不能帮你解答。" .
Otherwise start to generate answer, in your answer, please include citation numbers in square brackets corresponding to the references.
Example Answer Format: Students are responsible for notifying 『1』 the University of any changes to their personal details after registration. For changes like name, HKID Card 『2』 or Passport information, legal documentary evidence is required 『3』.
{assembled_question}
References:
{" ".join([f"[{i + 1}] {ref['content']}" for i, ref in enumerate(references)])}
"""

    # 流式调用LLM
    previous_text = ""
    async for token in stream_qwen_plus_query(prompt):
        # token 是累计的完整文本，取出新部分
        new_part = token[len(previous_text):]
        previous_text = token
        yield new_part


if __name__ == "__main__":
    test_question = "How can I graduate from Lingnan University?"
    test_history = ["What are the requirements to enroll?", "What credits are necessary for graduation?"]

    print("开始流式调用测试:\n")


    async def main():
        async for token in stream_answer(test_question, test_history):
            print(token, end='', flush=True)
        print("\n\n流式调用测试完成")


    asyncio.run(main())
