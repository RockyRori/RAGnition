import os
from typing import Literal

from backend.model.llm_stream_tongyiqianwen import stream_qwen_plus_query
import asyncio


async def stream_answer(assembled_question: str, generate_time: float, references: list[dict[str, str]],
                        search_time: float, target_language: Literal['en', 'zh-cn', 'zh-tw'] = 'en'):
    # Measure doc analysis time
    split_time = 0.0
    # Measure query generation time
    # Measure document search time
    # Measure LLM response time
    llm_time = 0.0

    # Print timing results
    print(f"1. Document Splitting Time: {split_time:.2f}s")
    print(f"2. Query Generation Time: {generate_time:.2f}s")
    print(f"3. Document Search Time: {search_time:.2f}s")
    print(f"4. LLM Response Generation Time: {llm_time:.2f}s")

    prompt = promt_select(target_language, assembled_question, references)

    # 流式调用LLM
    previous_text = ""
    async for token in stream_qwen_plus_query(prompt):
        # token 是累计的完整文本，取出新部分
        new_part = token[len(previous_text):]
        previous_text = token
        yield new_part


def promt_select(language: Literal['en', 'zh-cn', 'zh-tw'], assembled_question, references) -> str:
    if language == "zh-cn":
        return f"""你现在的角色是岭南大学政策问答助手。请根据用户问题和参考资料来回答。如果参考资料能够解答用户的提问，就模拟RAG系统，在回答中用『1』『2』『3』来标记参考文献的出处。否则回复目前为止小助手没有查询到岭南大学有相关政策，很抱歉我不能帮你解答。
        {assembled_question}参考资料:{" ".join([f"[{i + 1}] {ref['content']}" for i, ref in enumerate(references)])}"""
    elif language == "zh-tw":
        return f"""你現在的角色是嶺南大學政策問答助手。請根據用戶問題和參考資料來回答。如果參考資料能夠解答用戶的提問，就模擬RAG系統，在回答中用『1』『2』『3』來標記參考文獻的出處。否則回復目前為止小助手沒有查詢到嶺南大學有相關政策，很抱歉我不能幫你解答。
         {assembled_question}參考資料:{" ".join([f"[{i + 1}] {ref['content']}" for i, ref in enumerate(references)])}"""
    return f"""You are now a Lingnan University policy QA assistant. Please answer based on the user's questions and references. If the references can answer the user's question, simulate the RAG system and use 『1』『2』『3』 to mark the source of the reference in the answer. Otherwise, reply that the assistant has not found any relevant policies of Lingnan University so far. I'm sorry that I can't help you.
    {assembled_question}References:{" ".join([f"[{i + 1}] {ref['content']}" for i, ref in enumerate(references)])}"""


if __name__ == "__main__":
    print("开始流式调用测试:\n")

    assembled_question_test = "History Questions: null;Current Questions: Can I use student card after graduated?"
    generate_time_test = 2.2
    references_test = [{'content': 'The Card will also be invalid once a student has terminated his/her studies.',
                        'source': 'TPg_Student_Handbook_2024-25_segmented.txt', 'similarity': '80.2%'}]
    search_time_test = 1.1
    language_test = "zh-tw"


    async def main():
        async for token in stream_answer(assembled_question_test, generate_time_test, references_test, search_time_test,
                                         language_test):
            print(token, end='', flush=True)
        print("\n\n流式调用测试完成")


    asyncio.run(main())
