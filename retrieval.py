# retrieval.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def score_chunks(chunks: list[dict], question: str):
    """Return one similarity score per chunk, in the same order."""
    texts = [chunk["content"] for chunk in chunks]

    vectorizer = TfidfVectorizer()
    chunk_vectors = vectorizer.fit_transform(texts)
    question_vector = vectorizer.transform([question])

    return cosine_similarity(question_vector, chunk_vectors)[0]

def search_chunks(
        chunks: list[dict], 
        question: str, 
        top_k: int = 3
        ) -> list[dict]:

    scores = score_chunks(chunks, question)

    results = []

    for chunk, score in zip(chunks, scores):
        if score>0: 
            results.append({
                "chunk_id": chunk["chunk_id"],
                "page_number": chunk["page_number"],
                "content": chunk["content"],
                "score": float(score)
                
            })

            results.sort(key=lambda result: result["score"], reverse=True)
            
    return results[:top_k]