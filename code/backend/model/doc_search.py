import asyncio
import os
import random
import re
import time

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.root_path import PROJECT_ROOT, PIECES_DIR


def load_segments_from_file(file_path):
    """
    从单个文件中加载文档片段。
    文件格式要求：文本中以 "--- Segment 数字 ---" 作为片段分隔标识。
    返回一个列表，每个元素是包含 'content' 和 'source' 的字典。
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # 利用正则表达式分割文本，模式：行首以"--- Segment"开头，后面跟数字，再跟"---"
    segments = re.split(r'(?m)^--- Segment \d+ ---\s*$', text)
    # 去除空段落，并去掉首尾空白
    segments = [seg.strip() for seg in segments if seg.strip()]
    # 构造包含内容和来源的字典列表
    seg_dicts = [{'content': seg, 'source': file_path} for seg in segments]
    return seg_dicts


def load_segments_from_folder(input_folder):
    """
    遍历指定文件夹，读取所有文件或子文件夹中的文档片段。
    返回所有片段构成的列表。
    """
    document_segments = []

    for entry in os.listdir(input_folder):
        entry_path = os.path.join(input_folder, entry)

        if os.path.isfile(entry_path):
            # 直接读取文件
            try:
                segs = load_segments_from_file(entry_path)
                document_segments.extend(segs)
            except Exception as e:
                print(f"读取文件 {entry_path} 时发生错误：{e}")

        elif os.path.isdir(entry_path):
            # 读取子文件夹中的所有文件
            for sub_file in os.listdir(entry_path):
                sub_file_path = os.path.join(entry_path, sub_file)
                if os.path.isfile(sub_file_path):
                    try:
                        segs = load_segments_from_file(sub_file_path)
                        document_segments.extend(segs)
                    except Exception as e:
                        print(f"读取子文件夹文件 {sub_file_path} 时发生错误：{e}")

    return document_segments


async def search_documents(search_query, document_segments, top_k=12):
    """
    根据搜索查询内容，从文档片段中检索与查询最相关的片段。

    输入:
      - search_query: 搜索查询字符串。
      - document_segments: 文档片段列表，每个片段为{'content': ..., 'source': ...}。
      - top_k: 返回相关片段的数量（默认5个）。

    输出:
      - results: 每个结果包含 'content', 'source' 以及相似度 'similarity' 分数。
    """
    start_search = time.time()

    # 构造语料库：文档片段内容列表
    corpus = [seg['content'] for seg in document_segments]

    # 将所有文档片段与查询一起向量化
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus + [search_query])

    # 查询向量为最后一行，其余为文档片段向量
    query_vector = tfidf_matrix[-1]
    doc_vectors = tfidf_matrix[:-1]

    # 计算查询与每个文档片段之间的余弦相似度
    similarities = cosine_similarity(query_vector, doc_vectors).flatten()

    # 选择相似度最高的 top_k 个文档片段索引
    top_indices = similarities.argsort()[-top_k:][::-1]

    results = []
    for idx in top_indices:
        # 原始相似度转换成百分比
        orig_percent = similarities[idx] * 100

        # 根据规则修改相似度数值
        if orig_percent < 10:
            new_percent = orig_percent
        elif orig_percent < 30:
            new_percent = orig_percent * 2
        elif orig_percent < 50:
            new_percent = orig_percent + 50
        else:  # orig_percent >= 50
            new_percent = 90 + (orig_percent * 0.1)

        # 格式化结果（保留一位小数，若小数点后为0可按需调整）
        similarity_str = f"{new_percent:.1f}%"

        results.append({
            'content': document_segments[idx]['content'],
            'source': document_segments[idx]['source'],
            'similarity': similarity_str
        })

    # if results:
    #     first_similarity = float(results[0]['similarity'].strip('%'))
    #     if first_similarity < 60:
    #         results = results[:2]
    #     else:
    #         high_similarity_results = [item for item in results if float(item['similarity'].strip('%')) > 60]
    #         if len(high_similarity_results) > 5:
    #             high_similarity_results = high_similarity_results[:5]
    #         results = high_similarity_results
    results = results[:random.randint(5, 10)]
    search_time = time.time() - start_search
    return results, search_time


if __name__ == "__main__":
    # 配置参数
    input_folder_test = PIECES_DIR  # 输入文件夹，里面包含按 --- Segment 数字 --- 格式分割的文件
    search_query_test = "student card pass graduate academic"  # 用户的查询问题
    top_k_test = 10  # 选中相似度最高的前 10 个片段

    # 加载文件夹中所有文档片段
    document_segments_test = load_segments_from_folder(input_folder_test)
    if not document_segments_test:
        print("未在文件夹中找到任何文档片段。")

    # 根据查询搜索相关文档片段
    results_test, _ = asyncio.run(search_documents(search_query_test, document_segments_test, top_k=top_k_test))

    # 输出结果
    print("与查询问题相关的文档片段：")
    print(results_test)
