from typing import List, Tuple
import openai  # 需要安装openai库

# 模拟文档库（实际应替换为真实数据源）
DOCUMENT_DB = [
    ("大型语言模型(LLM)是使用深度学习处理自然语言的人工智能系统。", "https://ai.example/llm"),
    ("RAG(Retrieval-Augmented Generation)通过检索外部知识增强生成结果。", "https://ai.example/rag"),
    ("向量数据库使用相似度搜索实现高效信息检索。", "https://db.example/vector"),
]


def answer(question: str, history: List[str]) -> Tuple[str, List[str], List[str]]:
    # 1. 问题处理（示例：简单小写处理）
    processed_question = question.lower().strip()

    # 2. 文档检索（实际应使用向量搜索）
    ref_paragraphs, ref_links = zip(*retrieve_documents(processed_question))

    # 3. 构造上下文提示
    context = build_context(history, ref_paragraphs)

    # 4. 生成最终回答
    answer_text = generate_llm_response(
        context=context,
        question=question,
        references=ref_paragraphs
    )

    return answer_text, list(ref_paragraphs), list(ref_links)


def retrieve_documents(question: str, top_k: int = 3) -> List[Tuple[str, str]]:
    """文档检索示例（实际应使用向量数据库）"""
    # 此处简化为返回固定文档，真实场景应：
    # 1. 将问题编码为向量
    # 2. 执行相似度搜索
    # 3. 返回top_k相关文档
    return DOCUMENT_DB[:top_k]


def build_context(history: List[str], references: List[str]) -> str:
    """构建对话上下文"""
    dialog_context = []
    for i, text in enumerate(history):
        role = "用户" if i % 2 == 0 else "助手"
        dialog_context.append(f"{role}: {text}")

    reference_context = "\n".join([f"[参考{i + 1}] {text}" for i, text in enumerate(references)])

    return "\n".join([
        "对话历史：",
        "\n".join(dialog_context),
        "\n参考资料：",
        reference_context
    ])


def generate_llm_response(context: str, question: str, references: List[str]) -> str:
    """调用大语言模型生成回答"""
    prompt = f"""{context}

请根据以上对话历史和参考资料，用中文回答以下问题：
问题：{question}
回答时应：
1. 优先使用参考资料中的信息
2. 保持回答简洁专业
3. 在括号注明参考来源如[1]
4. 不要透露算法过程

最终回答："""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"生成回答时出错：{str(e)}"


# 示例用法
if __name__ == "__main__":
    example_question = "请解释什么是RAG？"
    example_history = ["深度学习的核心是什么？", "深度学习的核心是通过多层神经网络学习数据表征。"]

    answer_text, refs, links = answer(example_question, example_history)

    print("问题:", example_question)
    print("回答:", answer_text)
    print("参考链接:", links)