from typing import List, Tuple
import os
import glob
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import torch
from transformers import RagTokenizer, RagTokenForGeneration

# 设定设备（GPU/CPU）
device = "cuda" if torch.cuda.is_available() else "cpu"

# 初始化 tokenizer 和 RAG 模型
# tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-base")
# model = RagTokenForGeneration.from_pretrained("facebook/rag-token-base").to(device)


def load_documents(directory: str) -> List[Tuple[str, str]]:
    """
    加载指定目录下的所有文档，支持 PDF、DOC/DOCX、TXT、MD 文件。
    返回一个列表，每个元素为 (文件路径, 文档内容)。
    """
    documents = []
    # 定义支持的文件扩展名
    extensions = ["*.pdf", "*.doc", "*.docx", "*.txt", "*.md"]
    for ext in extensions:
        for filepath in glob.glob(os.path.join(directory, ext)):
            text = ""
            if filepath.lower().endswith(".pdf"):
                try:
                    import PyPDF2
                    with open(filepath, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                except Exception as e:
                    print(f"读取 PDF 文件 {filepath} 失败：{e}")
                    continue
            elif filepath.lower().endswith((".doc", ".docx")):
                try:
                    import docx2txt
                    text = docx2txt.process(filepath)
                except Exception as e:
                    print(f"读取 DOC/DOCX 文件 {filepath} 失败：{e}")
                    continue
            else:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        text = f.read()
                except Exception as e:
                    print(f"读取 TXT/MD 文件 {filepath} 失败：{e}")
                    continue
            if text:
                documents.append((filepath, text))
    return documents


def retrieve_local_documents(query: str, directory: str, top_k: int = 2) -> Tuple[List[str], List[str]]:
    """
    根据查询从本地文件中检索相关文档，采用 TF-IDF 计算余弦相似度。
    返回：
      references: 检索到的文档内容列表
      reference_links: 对应的文件路径列表
    """
    docs = load_documents(directory)
    if not docs:
        return [], []
    filepaths, texts = zip(*docs)

    # 利用 TF-IDF 计算文本向量
    vectorizer = TfidfVectorizer().fit(texts)
    doc_vectors = vectorizer.transform(texts)
    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, doc_vectors)[0]

    # 选取得分最高的 top_k 个文档
    top_indices = np.argsort(scores)[::-1][:top_k]
    references = [texts[i] for i in top_indices]
    reference_links = [filepaths[i] for i in top_indices]

    return references, reference_links


def answer(question: str, history: List[str]) -> Tuple[str, List[str], List[str]]:
    """
    使用 RAG 模型生成回答，并从本地文件中检索参考文档。

    参数:
      question: 用户的提问
      history: 对话历史记录列表（可选）

    返回:
      answer_text: 模型生成的回答文本
      references: 检索到的参考文档内容列表
      reference_links: 对应的文件路径列表
    """
    # 组合历史对话和当前问题
    combined_input = " ".join(history + [question]) if history else question

    # 使用 RAG 模型生成回答
    # inputs = tokenizer(combined_input, return_tensors="pt").to(device)
    # generated_ids = model.generate(
    #     input_ids=inputs["input_ids"],
    #     num_beams=5,
    #     max_length=200
    # )
    # answer_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    answer_text = "none"

    # 从本地文件中检索参考文档（假设文档存放在 "./documents" 目录下）
    directory = "./documents"  # 根据需要修改目录路径
    references, reference_links = retrieve_local_documents(question, directory, top_k=2)

    return answer_text, references, reference_links


# 示例调用（测试用）
if __name__ == "__main__":
    sample_question = "in order to graduate , what gpa should i reach at least ?"
    sample_history = ["", ""]
    ans, refs, links = answer(sample_question, sample_history)
    print("Answer:", ans)
    print("\nReferences (部分内容预览):")
    for ref in refs:
        print(" -", ref[:20000])  # 打印前200个字符预览
    print("\nReference Links:", links)
