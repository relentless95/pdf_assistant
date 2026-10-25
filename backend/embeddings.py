"""Create embeddings for PDF passages and search questions."""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-small-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Load the model once per Python process."""
    return SentenceTransformer(MODEL_NAME)


def embed_passages(texts: list[str]) -> np.ndarray:
    """Return one normalized embedding per passage."""
    model = get_model()

    if not texts:
        return np.empty(
            (0, model.get_embedding_dimension()),
            dtype=np.float32
        )

    return model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    )


def embed_question(question: str) -> np.ndarray:
    """Return a normalized embedding with shape (1, 384)."""
    question = question.strip()

    if not question:
        raise ValueError("Question must not be empty.")

    return get_model().encode(
        [QUERY_PREFIX + question],
        normalize_embeddings=True,
        convert_to_numpy=True
    )