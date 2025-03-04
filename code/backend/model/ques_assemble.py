def generate_search_query(user_question, history_questions):
    """
    生成用于文档搜索的查询内容

    输入:
      - user_question: 用户输入的问题字符串
      - history_questions: 历史问题字符串列表

    输出:
      - search_query: 一个由 TF-IDF 提取的关键词组合，适合用于文档搜索
      - assembled_question: 组装后的完整用户问题，结合了历史问题和当前问题的信息
    """
    from sklearn.feature_extraction.text import TfidfVectorizer

    # 构造语料库，将历史问题和当前问题合并
    corpus = history_questions + [user_question]

    # 使用英文停用词，可以根据需要调整或替换为中文停用词列表
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()

    # 获取当前问题（最后一项）的 TF-IDF 分数
    user_vector = tfidf_matrix[-1].toarray().flatten()

    # 选择 TF-IDF 得分最高的前 5 个关键词（可根据需要调整）
    top_n = 5
    top_indices = user_vector.argsort()[-top_n:][::-1]
    top_terms = [feature_names[i] for i in top_indices if user_vector[i] > 0]

    # 组合关键词作为搜索查询
    search_query = " ".join(top_terms)

    # 组装完整用户问题（简单将历史问题和当前问题拼接在一起）
    assembled_question = ("Based on your previous inquiries: " +
                          "; ".join(history_questions) +
                          ". And your current question: " +
                          user_question)

    return search_query, assembled_question


if __name__ == "__main__":
    # 示例：用户输入的问题和历史问题列表
    user_question = "Which brand is tasty?"
    history_questions = [
        "What are the famous potato chip brands?",
        "I want you to recommend some delicious snack."
    ]

    search_query, assembled_question = generate_search_query(user_question, history_questions)
    print("生成的搜索查询内容：")
    print(search_query)
    print("\n组装后的完整用户问题：")
    print(assembled_question)
