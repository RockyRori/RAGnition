import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 文件路径
file_path = "D:/TPg_Student_Handbook_2024-25.txt"  
with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

# 按小节分割文本如 5.1, 5.2
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
    if len(current_chunk) < 200:  # 合并阈值
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

# 用于分割大块
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,  # 每个文本块的最大长度
    chunk_overlap=100,  # 文本块之间的重叠长度
    separators=["\n\n", "\n"]  # 按段落分割
)

# 对合并后的块进一步分割
final_chunks = []
for chunk in merged_chunks:
    if len(chunk) > 800:  # 如果块太大，则进一步分割
        sub_chunks = splitter.split_text(chunk)
        final_chunks.extend(sub_chunks)
    else:
        final_chunks.append(chunk)

# 输出分割后的文本块
for i, chunk in enumerate(final_chunks):
    print(f"Chunk {i + 1}:\n{chunk}\n{'-' * 40}")