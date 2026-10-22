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