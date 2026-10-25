from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend import storage

client = TestClient(app)


def upload_sample():
    """Upload the known PDF and return its ID for database endpoint tests."""
    with (Path(__file__).parent / "sample.pdf").open("rb") as pdf:
        response = client.post(
            "/files/", files={"file": ("sample.pdf", pdf, "application/pdf")}
        )
    assert response.status_code == 200
    return response.json()["document_id"]


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


def test_saved_document_can_be_listed_and_retrieved():
    """Check SQLite-backed list and GET responses after an upload."""
    document_id = upload_sample()

    listing = client.get("/documents/")
    assert listing.status_code == 200
    assert listing.json()["documents"] == [
        {"document_id": document_id, "filename": "sample.pdf"}
    ]

    response = client.get(f"/documents/{document_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == document_id
    assert data["pages"][0]["page_number"] == 1
    assert "Batteries store energy" in data["pages"][0]["content"]


def test_delete_document_removes_related_data():
    """Delete through the API and verify pages/chunks are removed by SQLite."""
    document_id = upload_sample()

    # Confirm related data existed, so empty tables afterward prove deletion.
    saved = storage.load_document(document_id)
    assert saved["pages"] and saved["chunks"]

    response = client.delete(f"/documents/{document_id}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/documents/{document_id}").status_code == 404
    assert client.get("/documents/").json() == {"documents": []}

    connection = storage.get_connection()
    try:
        assert connection.execute("SELECT COUNT(*) FROM pages").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0] == 0
    finally:
        connection.close()

    assert client.delete(f"/documents/{document_id}").status_code == 404
