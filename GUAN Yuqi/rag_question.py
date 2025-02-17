from transformers import RagTokenizer, RagRetriever, RagSequenceForGeneration
import torch
from datasets import load_dataset

# 加载标记器和模型
tokenizer = RagTokenizer.from_pretrained("facebook/rag-sequence-base")
model = RagSequenceForGeneration.from_pretrained("facebook/rag-sequence-base")

# 加载数据集，指定配置名称
dataset = load_dataset("facebook/wiki_dpr", "psgs_w100.nq.exact", trust_remote_code=True)  # 加载数据集时信任远程代码

# 设置检索器
retriever = RagRetriever.from_pretrained("facebook/rag-sequence-base", use_dummy_dataset=True)

# 加载学生手册文本
with open("student_handbook.txt", "r", encoding="utf-8") as file:
    handbook_text = file.read()

# 将手册文本添加到检索器
retriever.add_texts([handbook_text])

# 设置问题
question = "What is the minimum CGPA requirement for students to enter higher education?"  # 您的问题
input_ids = tokenizer(question, return_tensors="pt").input_ids

# 获取上下文
docs = retriever(input_ids.numpy(), n_docs=5)

# 生成答案
with torch.no_grad():
    output = model.generate(input_ids=input_ids, context_input_ids=docs['context_input_ids'])

answer = tokenizer.decode(output[0], skip_special_tokens=True)

print("模型回答:", answer)