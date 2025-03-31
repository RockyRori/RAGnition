from backend.model.llm_tongyiqianwen import qwen_plus_query
from backend.model.model import LLMModel


def get_llm_answer(question, references, model_type: LLMModel):
    """
    使用免费 LLM 根据问题和参考文献生成自然语言答案，
    并在答案中加入引用数字。

    输入:
      - question: 组装后的完整用户问题字符串
      - references: 参考文献列表，每个元素为字典，格式为：
            {'content': 文档片段内容, 'source': 来源, 'similarity': 相似度分数}

    输出:
      - answer: 包含引用数字的自然语言答案字符串
    """
    # 构造参考文献文本，每个参考文献以 [n] 开头，包含来源和内容摘要
    ref_text = ""
    for i, ref in enumerate(references, start=1):
        ref_text += f"[{i}] Source: {ref['source']} Similarity: {ref['similarity']} Content: {ref['content']} \n"

    # 构造给 LLM 的提示
    prompt = f"""You are a helpful assistant.
Answer the following question based on the provided references. If you think the question is not related to the references, please answer "你的问题和学校政策无关，我无法回答。".
In your answer, please include citation numbers in square brackets corresponding to the references.
Example Answer Format: Students are responsible for notifying 『1』 the University of any changes to their personal details after registration. For changes like name, HKID Card 『2』 or Passport information, legal documentary evidence is required 『3』.
{question}
References:
{ref_text}
"""
    if model_type is LLMModel.QWEN_PLUS:
        return qwen_plus_query(prompt)
    else:
        return "backend error, no such model"


if __name__ == "__main__":
    # 示例输入：组装后的完整用户问题
    question = ("Based on your previous inquiries: What are the famous potato chip brands?; "
                "I want you to recommend some delicious snack. And your current question: "
                "Which brand is tasty?")

    # 示例参考文献列表
    references = []
    references.append({
        'content': "Coco is the best chips with a crunchy texture and rich flavor.",
        'source': "doc1.txt",
        'similarity': "89%"
    })
    references.append({
        'content': "Violet offers chips that are also popular and known for their quality.",
        'source': "doc2.txt",
        'similarity': "76%"
    })

    answer = get_llm_answer(question, references)

    print("LLM Answer with citations:")
    print(answer)
