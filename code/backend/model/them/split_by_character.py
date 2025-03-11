import re
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 定义文件路径
pdf_path = "D:/TPg_Student_Handbook_2024-25.pdf"  
output_txt_path = "D:/txt_chunks/output_chunks.txt"  

# 从 PDF 文件读取文本
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# 提取 PDF 文本
text = extract_text_from_pdf(pdf_path)

# 使用正则表达式按小节分割文本
# 匹配模式：数字+点+数字（如 5.1, 5.2）
section_pattern = re.compile(r"(\d+\.\d+ .+)")
sections = section_pattern.split(text)

# 将标题和内容配对
section_chunks = []
for i in range(1, len(sections), 2):
    title = sections[i].strip()  # 小节标题
    content = sections[i + 1].strip()  # 小节内容
    section_chunks.append({"title": title, "content": content})

# 合并短小节
merged_chunks = []
current_chunk = ""
current_title = ""

for chunk in section_chunks:
    title = chunk["title"]
    content = chunk["content"]
    
    # 如果当前块的内容较短，则合并
    if len(current_chunk) < 300:  
        if current_chunk:
            current_chunk += "\n\n" + title + "\n" + content
        else:
            current_chunk = title + "\n" + content
    else:
        # 如果当前块已达到合并阈值，则保存当前块并开始新块
        merged_chunks.append(current_chunk)
        current_chunk = title + "\n" + content

# 添加最后一个块
if current_chunk:
    merged_chunks.append(current_chunk)

# 创建 RecursiveCharacterTextSplitter 实例，用于分割大块
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,  # 每个文本块的最大长度
    chunk_overlap=100,  # 文本块之间的重叠长度
    separators=["\n\n", "\n"]  # 按段落分割
)

# 对合并后的块进一步分割
final_chunks = []
for chunk in merged_chunks:
    if len(chunk) > 1000:  # 如果块太大，则进一步分割
        sub_chunks = splitter.split_text(chunk)
        final_chunks.extend(sub_chunks)
    else:
        final_chunks.append(chunk)

# 将分割后的块写入 TXT 文件
with open(output_txt_path, "w", encoding="utf-8") as output_file:
    for i, chunk in enumerate(final_chunks):
        output_file.write(f"Chunk {i + 1}:\n{chunk}\n{'-' * 40}\n\n")

print(f"分割完成，结果已保存到 {output_txt_path}")
