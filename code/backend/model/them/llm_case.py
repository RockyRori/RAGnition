if __name__ == "__main__":
    prompt = """You are a helpful assistant.
Answer the following question based on the provided references.
In your answer, please include citation numbers in square brackets corresponding to the references.
Question: Based on your previous inquiries: What are the famous potato chip brands?; I want you to recommend some delicious snack. And your current question: Which brand is tasty?
References:
[1] Source: doc1.txt. Content: Coco is the best chips with a crunchy texture and rich flavor. 
[2] Source: doc2.txt. Content: Violet offers chips that are also popular and known for their quality. 

Answer:"""
    print(
        "Some famous potato chip brands include Coco and Violet. Among them, Coco is known for its crunchy texture and rich flavor, making it a great choice for a tasty snack [1]. Violet is also a popular brand recognized for its quality chips [2]. If you're looking for a delicious snack, both brands are excellent options."
    )
