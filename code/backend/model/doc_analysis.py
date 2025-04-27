import os
import re
import json
import pickle

# 文档读取相关库
import docx
import PyPDF2
from bs4 import BeautifulSoup

# 用于文本向量化和计算余弦相似度
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.root_path import PROJECT_ROOT, PIECES_DIR, POLICIES_DIR


def read_txt(file_path):
    """读取 txt 或 md 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def read_pdf(file_path):
    """读取 pdf 文件"""
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def read_docx(file_path):
    """读取 docx 文件（仅支持 docx 格式）"""
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


def read_html(file_path):
    """
    读取 html 文件，去掉脚本/导航等常见非正文标签，提取纯文本并去除多余空行
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 删除非正文标签
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
        tag.decompose()

    # 抽取文本，以换行分隔
    raw_text = soup.get_text(separator="\n")

    # 过滤掉空行和只有 1-2 个字符的行
    lines = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if len(stripped) > 2:
            lines.append(stripped)

    return "\n".join(lines)


def read_file(file_path):
    """根据文件扩展名选择合适的读取方式"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.txt', '.md']:
        return read_txt(file_path)
    elif ext == '.pdf':
        return read_pdf(file_path)
    elif ext in ['.doc', '.docx']:
        return read_docx(file_path)
    elif ext in ['.html', '.htm']:
        return read_html(file_path)
    else:
        raise ValueError(f"不支持的文件格式：{ext}")


def split_sentences(text):
    """
    利用正则表达式将文本拆分成句子。
    支持中文及英文标点。注：该方法简单处理缩写可能会有问题。
    """
    sentences = re.split(r'(?<=[。！？\.\?!])\s*', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def segment_text(text, similarity_threshold=0.3):
    """
    使用 TF-IDF 对句子向量化，计算相邻句子的余弦相似度进行分割。
    分割后增加以下两条规则：
    1. 如果当前段落的字数不足300字，则将下一段落的内容合并进来。
    2. 每个段落的开头复制上一段的最后一个完整句子作为冗余。
    """
    # 多个空格合并成一个空格
    text = re.sub(r'\s+', ' ', text)
    # 假定 split_sentences 是已定义的函数，用于将文本分割为句子列表
    sentences = split_sentences(text)
    if not sentences:
        return []

    # 使用 TF-IDF 对句子进行向量化
    vectorizer = TfidfVectorizer().fit(sentences)
    vectors = vectorizer.transform(sentences)

    # 根据相邻句子的余弦相似度初步进行分段
    segments = []
    current_segment = sentences[0]
    for i in range(len(sentences) - 1):
        sim = cosine_similarity(vectors[i], vectors[i + 1])[0][0]
        if sim < similarity_threshold:
            segments.append(current_segment)
            current_segment = sentences[i + 1]
        else:
            current_segment += " " + sentences[i + 1]
    segments.append(current_segment)

    # 后处理规则1：如果当前段落字数不足300字，则将下一段的内容合并进来
    i = 0
    while i < len(segments) - 1:
        if len(segments[i]) < 300:
            segments[i] = segments[i] + " " + segments[i + 1]
            del segments[i + 1]
        else:
            i += 1

    # 后处理规则2：每个段落的开头复制上一段的最后一个完整句子作为冗余
    for i in range(1, len(segments)):
        prev_segment = segments[i - 1]
        # 使用 split_sentences 提取上一段的句子列表
        prev_sentences = split_sentences(prev_segment)
        redundancy = prev_sentences[-1] if prev_sentences else ""
        segments[i] = redundancy + " " + segments[i]

    return segments


def output_segments(segments, output_path, output_format="txt"):
    """
    将分割结果输出为指定格式：
      - txt：写入文本文件，每个片段以分隔符标识；
      - json：写入 JSON 文件，存储为字符串数组；
      - pickle：序列化为 pickle 文件。
    """
    if output_format == "txt":
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, seg in enumerate(segments):
                f.write(f"--- Segment {i + 1} ---\n")
                f.write(seg + "\n\n")
    elif output_format == "json":
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
    elif output_format == "pickle":
        with open(output_path, 'wb') as f:
            pickle.dump(segments, f)
    else:
        raise ValueError(f"不支持的输出格式：{output_format}")


def get_supported_files(folder):
    """
    扫描指定文件夹，返回所有支持格式的文件路径。
    支持格式：.txt, .md, .pdf, .doc, .docx, .html, .htm
    """
    supported_extensions = {'.txt', '.md', '.pdf', '.doc', '.docx', '.html', '.htm'}
    files = []
    for file in os.listdir(folder):
        ext = os.path.splitext(file)[1].lower()
        if ext in supported_extensions:
            files.append(os.path.join(folder, file))
    return files


def splitting():
    # 硬编码配置参数
    input_folder = POLICIES_DIR  # 输入文件夹路径，文件夹下所有支持格式的文件将参与处理
    output_folder = PIECES_DIR  # 输出文件夹路径，分割后的文件将存储于此文件夹内
    output_format = "txt"  # 输出格式：可选 "txt", "json", "pickle"
    similarity_threshold = 0.2  # 句子相似度阈值

    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取输入文件夹内所有支持的文件
    files = get_supported_files(input_folder)
    if not files:
        print("在输入文件夹中未找到支持的文件格式。")
        return

    for file_path in files:
        try:
            print(f"处理文件：{file_path}")
            text = read_file(file_path)
            segments = segment_text(text, similarity_threshold=similarity_threshold)
            filename = os.path.basename(file_path)
            base, _ = os.path.splitext(filename)
            output_path = os.path.join(output_folder, f"{base}_segmented.{output_format}")
            output_segments(segments, output_path, output_format=output_format)
            print(f"完成处理，输出文件：{output_path}\n")
        except Exception as e:
            print(f"处理 {file_path} 时发生错误：{e}")


if __name__ == "__main__":
    splitting()
