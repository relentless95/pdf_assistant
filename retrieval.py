"""Rank supplied chunks using TF-IDF and cosine similarity, without an LLM."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def score_chunks(chunks: list[dict], question: str):
    """Return one similarity score per chunk, in the same order."""
    texts = [chunk["content"] for chunk in chunks]

    # Learn vocabulary from chunks; transform the question with that same vocabulary.
    vectorizer = TfidfVectorizer()
    chunk_vectors = vectorizer.fit_transform(texts)
    question_vector = vectorizer.transform([question])

    return cosine_similarity(question_vector, chunk_vectors)[0]

def search_chunks(
        chunks: list[dict], 
        question: str, 
        top_k: int = 3
        ) -> list[dict]:
    """Return up to top_k positive matches with text, source page, and score."""

    scores = score_chunks(chunks, question)

    results = []

    # Scores follow input chunk order, so zip pairs each passage with its score.
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
