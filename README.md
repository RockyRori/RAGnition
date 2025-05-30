# RAGnition

LU Graduation Project RAGnition Team

# CDS536 Data Science Project

Group Name:            RAGnition

Director:              Prof. LI

Project:        Developing a Policy QA System Using Retrieval-Augmented Generation (RAG) Framework

| English Name | Email Address (Lingnan Email) |
|--------------|-------------------------------|
| LUO Suhai    | suhailuo@ln.hk                |
| WEI Fansen   | fansenwei@ln.hk               |
| LI Junrong   | junrongli@ln.hk               |
| WANG Jiawei  | jiaweiwang2@ln.hk             |
| Wang Zihao   | zihaowang3@ln.hk              |
| GUAN Yuqi    | yuqiguan@ln.hk                |

# RAGnition

Policies are often complex, lengthy, and filled with technical language, making it challenging for individuals to
extract the specific information they need efficiently. A policy QA System aims to bridge this gap by providing concise,
accurate, and user-friendly answers to policy-related queries. Traditional QA systems typically have pre-defined QA
pairs and then use information retrieval techniques to find QA pairs related to users’ questions. As LLM becomes
popular, a machine can generate answers without retrieving information. However, generation-based systems often face a
significant challenge –hallucinations, where the system generates incorrect or fabricated information that lacks
grounding in factual data, which is a critical problem for a policy QA system.

This project addresses the hallucination problem by developing a QA system based on the Retrieval-Augmented Generation (
RAG) framework. RAG combines the best of retrieval-based and generation-based approaches, aiming to significantly reduce
hallucinations in language model outputs by grounding answers in factual, retrieved data. The RAG framework operates
through two main components: the retrieved part and the generation part. The retrieval part retrieves relevant policy
documents or sections from policy documents on user queries. The generation part synthesizes an easy-to-understand
response based on the retrieved content. Unlike standalone generative models that may invent fake details when faced
with incomplete information, the RAG approach ensures that all answers are firmly rooted in the retrieved policy data.
This enhances the credibility and reliability of the system.An additional challenge in building such a system is
balancing speed and accuracy. While users often expect rapid responses, the system must also ensure that answers are
precise and factually grounded. Students will explore various techniques to optimize this trade-off, ensuring that the
QA system is both efficient and accurate for real-time policy inquiries.

# Reference

1. Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... & Kiela, D. (2020). Retrieval-augmented
   generation for knowledge-intensive nlp tasks. Advances in Neural Information Processing Systems, 33, 9459-9474.
2. Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., ... & Wang, H. (2023). Retrieval-augmented generation for
   large language models: A survey. arXiv preprint arXiv:2312.10997.
3. Wu, J., Zhu, J., Qi, Y., Chen, J., Xu, M., Menolascina, F., & Grau, V. (2024). Medical Graph RAG: Towards safe
   medical large language model via graph retrieval-augmented generation. arXiv preprint arXiv:2408.04187.
4. https://www.cnblogs.com/tgltt/p/18512586
5. https://mp.weixin.qq.com/s/qfw44Yu9b9hHXu7hOURwJw
6. https://mp.weixin.qq.com/s/G0Zr_rOZARdMkY4Cuh1opA
7. https://mp.weixin.qq.com/s/Kxoho142yXTiW4jdZntVlQ
8. https://mp.weixin.qq.com/s/3_a97BTspZuZpFQNLt50gA
9. https://mp.weixin.qq.com/s/NzcWykZ46oOFKRjalTuKIA
10. https://mp.weixin.qq.com/s/NzcWykZ46oOFKRjalTuKIA
11. https://mp.weixin.qq.com/s/dmiwvA8Rtl6MR4EVHS88Eg
12. https://mp.weixin.qq.com/s/qPiPeWLIzlIbQlb2ZdAVcg
13. https://mp.weixin.qq.com/s/BmJMVgxj7YwmTj6X3Dkd6Q
14. https://mp.weixin.qq.com/s/g7mbN5Uh-w6jyxQC61-DRQ

# System Architecture

![architecture.png](figuras/architecture.png)

# RAGnition Talk Series

### RAGnition Talk 1

| Time   | 周二 2025-01-14 14:00 - 16:00          |
|--------|--------------------------------------|
| Period | 0101-0112                            |
| Output | Literacy Review in everyone's folder |

### RAGnition Talk 2

| Time   | 周五 2025-01-17 13:00 - 15:00 |
|--------|-----------------------------|
| Period | 0113-0119                   |
| Output | Roadmap                     |

![solution](figuras/solution.jpg)

### Chinese New Year Festival

| Time   | -         |
|--------|-----------|
| Period | 0120-0131 |
| Output | Rest      |

### RAGnition Talk 3

| Time   | 周一 2025-02-10 10:00 - 12:00                                     |
|--------|-----------------------------------------------------------------|
| Period | 0201-0209                                                       |
| Output | Current Model Effects & Division of labour in everyone's folder |

### RAGnition Talk 4

| Time   | 周五 2025-02-21 13:00 - 15:00                            |
|--------|--------------------------------------------------------|
| Period | 0210-0216                                              |
| Output | We ask some questions and get answers from instructors |

![architecture_comparison.png](figuras/architecture_comparison.png)

### RAGnition Talk 5

| Time   | 周二 2025-03-04 13:00 - 15:00   |
|--------|-------------------------------|
| Period | 0217-0302                     |
| Output | Report the first stage effort |

### RAGnition Talk 6

| Time   | 周五 2025-03-14 13:00 - 15:00     |
|--------|---------------------------------|
| Period | 0303-0316                       |
| Output | complete version one rag system |

### RAGnition Talk 7

| Time   | 周二 2025-04-01 13:30 - 15:00                  |
|--------|----------------------------------------------|
| Period | 0317-0330                                    |
| Output | add stream answer output,use qdrant database |

[//]: # (![rehearsal.jpg]&#40;figuras/rehearsal.jpg&#41;)

### RAGnition Rehearsal

| Time   | 周三 2025-05-07 14:00 - 18:00                                                                                                                                                                                                                                                              |
|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Period | 0331-0430                                                                                                                                                                                                                                                                                |
| Output | 1. Avoid plosives (popping sounds) by mastering microphone technique.<br/>2. Speak without heavy reliance on notes—minimize reading verbatim.<br/>3. Engage the audience: Blend Q&A, polls, or rhetorical questions.<br/>4. Deliver fluent English—practice to eliminate pauses/fillers. |

### RAGnition Presentation

| Time   | 周四 2025-05-08 11:30 - 12:00 |
|--------|-----------------------------|
| Period | 0501-0508                   |
| Output | Well Done !                 |

[//]: # (![presentation.jpg]&#40;figuras/presentation.jpg&#41;)

### HongKong AI+ Power 2025 PoliSage Exhibition

| Time   | 周四 2025-06-05 到 周五 2025-06-06                                                                             |
|--------|-----------------------------------------------------------------------------------------------------------|
| Period | 0509-0606                                                                                                 |
| Output | 1. Designing promotional posters.<br/>2. Pitching to investors.<br/>3. Representing LU at the exhibition. |

| Time   | To Be Done |
|--------|------------|
| Period | 0509-0603  |
| Output | To Be Done |

# Obstacles

1. 政策的实时性？
   网页上的政策是实时的。

2. 文档分割算法效果和时间
3. 向量数据库 QDRANT

4. 问题意图识别和关键词提取和时间
   建立同义词库，关键词库。

5. 参考文献的相似度和时间
6. 参考文献的相似度隐藏
7. 参考文档的关联度的排序。

8. 大模型的调用的稳定性和时间
   修改调用的方式，流失调用。不同的模型。首个token调用就快。答案里面没有换行符。前端对于回答答案的渲染。
   同一个问题的不同问法的回答。
   处理问题与政策无关的时候的参考文献。

部署到服务器，录视频，ppt，report，参加比赛。
遇到了哪些问题和响应的解决方法

future direction
网络部署的时候的流式传输
用户输入多语言

9. 多个文档表达相同意思
10. 文档时序，过期政策更新