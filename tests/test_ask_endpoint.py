"""Exercise /ask with a temporary database and mocked retrieval/generation."""

import pytest
from fastapi.testclient import TestClient

from backend import main
from backend import storage

client = TestClient(main.app)


@pytest.fixture
def saved_document(monkeypatch):
    storage.save_document(
        "test-document", "sample.pdf",
        [{"page_number": 1, "content": "Batteries store energy."}],
        [{
            "chunk_id": "chunk-1",
            "page_number": 1,
            "content": "Batteries store energy.",
            "embedding": [1.0, 0.0],
            "embedding_model": main.MODEL_NAME
        }]
    )

    # The tiny vector is a placeholder; mocked retrieval does no vector arithmetic.
    def fake_search(chunks, question, top_k=3):
        return chunks[:top_k]

    monkeypatch.setattr(main, "search_semantic", fake_search)
    return "test-document"


def test_ask_returns_answer_and_sources(monkeypatch, saved_document):
    def fake_answer(question, passages):
        assert question == "How is energy stored?"
        assert passages[0]["chunk_id"] == "chunk-1"
        return {
            "answer": "Batteries store energy.",
            "insufficient_evidence": False,
            "sources": [{
                "chunk_id": "chunk-1",
                "page_number": 1,
                "content": passages[0]["content"]
            }]
        }

    monkeypatch.setattr(main, "generate_answer", fake_answer)
    response = client.post(
        f"/documents/{saved_document}/ask",
        json={"question": "How is energy stored?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == saved_document
    assert data["question"] == "How is energy stored?"
    assert data["answer"] == "Batteries store energy."
    assert data["sources"][0]["page_number"] == 1


def test_ask_provider_failure_returns_502(monkeypatch, saved_document):
    def fake_answer(question, passages):
        raise main.AnsweringError("Provider unavailable.")

    monkeypatch.setattr(main, "generate_answer", fake_answer)
    response = client.post(
        f"/documents/{saved_document}/ask",
        json={"question": "How is energy stored?"}
    )
    assert response.status_code == 502
    assert response.json()["detail"] == "Provider unavailable."


@pytest.mark.parametrize("body, expected_status", [
    ({}, 422),
    ({"question": "   "}, 400)
])
def test_ask_rejects_invalid_questions(saved_document, body, expected_status):
    response = client.post(f"/documents/{saved_document}/ask", json=body)
    assert response.status_code == expected_status


def test_ask_unknown_document_returns_404():
    response = client.post(
        "/documents/missing/ask", json={"question": "How is energy stored?"}
    )
    assert response.status_code == 404
