from typing import List, Tuple


# RAG回答用户提问
def answer(question: str, history: List[str]) -> Tuple[str, List[str], List[str]]:
    # 识别用户问题
    #TODO

    # 从现有资料库中查找段落
    # TODO

    # 把用户问题和参考资料打包发给大模型拼装回答
    # TODO

    return answer_text, reference, reference_links
    return f"这是『1』对‘{question}’的示例『2』回答", ["请求过于频繁","参考片段1：根据XX规定..."], ["https://www.bing.com/search?"]


def ask() -> str:
    return "nah"
