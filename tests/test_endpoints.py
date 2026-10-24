from pathlib import Path

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_document_returns_404():
    response = client.get("/documents/unknown_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_upload_pdf():
    # Use a sample PDF file for testing
    pdf_path = Path(__file__).parent / "sample.pdf"

    with pdf_path.open("rb") as pdf:
        response = client.post(
            "/files", files={"file": ("sample.pdf", pdf, "application/pdf")}
        )

    assert response.status_code == 200

    data = response.json()
    print("---------", data)

    assert "document_id" in data
    assert data["filename"] == "sample.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["page_count"] > 0
    assert "preview" in data
    assert data["preview"].strip()
    assert data["message"] == "File uploaded and processed successfully"


def test_search_uploaded_document():
    """Upload known PDF text, then verify the search response and score order."""
    pdf_path = Path(__file__).parent / "sample.pdf"

    # Upload first so the test uses a real ID, independent of manual uploads.
    with pdf_path.open("rb") as pdf:
        upload_response = client.post(
            "/files/",
            files={"file": ("sample.pdf", pdf, "application/pdf")}
        )

    assert upload_response.status_code == 200
    document_id = upload_response.json()["document_id"]
    question = "How do batteries store energy?"

    response = client.post(
        f"/documents/{document_id}/search",
        json={"question": question}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == document_id
    assert data["question"] == question

    results = data["results"]
    assert 1 <= len(results) <= 3
    first_result = results[0]
    assert first_result["page_number"] == 1
    assert "Batteries store energy" in first_result["content"]
    assert first_result["chunk_id"]
    assert first_result["score"] > 0

    # Compare the returned order with a new list sorted highest-score-first.
    scores = [result["score"] for result in results]
    assert scores == sorted(scores, reverse=True)
