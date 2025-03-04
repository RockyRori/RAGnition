from typing import List, Tuple

from backend.model.ask_llm import get_llm_answer
from backend.model.doc_analysis import splitting
from backend.model.doc_search import search_documents, load_segments_from_folder
from backend.model.ques_assemble import generate_search_query


# RAG回答用户提问
def answer(question: str, history: List[str]) -> Tuple[str, List[str], List[str]]:
    # 拆分文档
    # splitting()
    # 识别用户问题
    search_query, assembled_question = generate_search_query(question, history)
    # 从现有资料库中查找段落
    # references = search_documents(search_query, load_segments_from_folder(), top_k=4)
    references = ["""来源: pieces/MScDS_Student_Handbook_2024-25_segmented.txt
相似度: 0.2256139841037395
内容: 4 At the end of the term in which the student on academic probation has cumulatively 
enrolled in 6 or more credits, if he/she obtains a Cumulative GPA of 2.""","""来源: pieces/MScDS_Student_Handbook_2024-25_segmented.txt
相似度: 0.20356099465154112
内容: 6 A warning concerning the need to improve his/her academic performance should be 
issued to a student whose Cumulative GPA is at or above the level required for 
progression but below the level for graduation. The warning should be sent to a student 
whose Cum ulative GPA is at or above 2. 33 but below 2. 67 (which is the minimum 
required for graduation). 2. 9. Graduation Requirements""","""来源: pieces/MScDS_Student_Handbook_2024-25_segmented.txt
相似度: 0.19267734743316595
内容: A student is required to graduate as soon as he/she satisfies all the conditions for an award . 9 
 2. 9. 7."""]

    # 把用户问题和参考资料打包发给大模型拼装回答
    answer_text = get_llm_answer(assembled_question, [])

    return answer_text, references, references
