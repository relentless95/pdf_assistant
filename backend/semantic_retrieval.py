"""Rank PDF chunks using pretrained embeddings."""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from backend.embeddings import MODEL_NAME, embed_passages, embed_question


def add_embeddings(chunks: list[dict]) -> None:
    """Attach current-model embeddings to chunks missing them."""
    missing = [
        chunk for chunk in chunks
        if chunk.get("embedding") is None
        or chunk.get("embedding_model") != MODEL_NAME
    ]

    if not missing:
        return

    vectors = embed_passages([
        chunk["content"] for chunk in missing
    ])

    for chunk, vector in zip(missing, vectors):
        chunk["embedding"] = vector.tolist()
        chunk["embedding_model"] = MODEL_NAME


def search_semantic(
    chunks: list[dict],
    question: str,
    top_k: int = 3
) -> list[dict]:
    """Rank chunks whose embeddings have already been prepared."""
    if not chunks:
        return []

    passage_vectors = np.asarray(
        [chunk["embedding"] for chunk in chunks],
        dtype=np.float32
    )

    question_vector = embed_question(question)
    scores = cosine_similarity(
        question_vector,
        passage_vectors
    )[0]

    results = []

    for chunk, score in zip(chunks, scores):
        results.append({
            "chunk_id": chunk["chunk_id"],
            "page_number": chunk["page_number"],
            "content": chunk["content"],
            "score": float(score)
        })

    results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    return results[:top_k]