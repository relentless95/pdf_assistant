"""Learning API: upload PDFs, extract numbered pages, and build searchable chunks.

Document metadata, extracted pages, and chunks persist in SQLite.
Original PDF files are not permanently saved. Run storage.py to create tables.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from pypdf.errors import PdfReadError
from uuid import uuid4
from pydantic import BaseModel
from retrieval import search_chunks
from extraction import extract_pages, validate_pdf
from chunking import chunk_text
from storage import save_document
from storage import list_documents
from storage import load_document, delete_document
from typing import Literal

from embeddings import MODEL_NAME
from semantic_retrieval import add_embeddings, search_semantic
from storage import save_chunk_embeddings


class SearchRequest(BaseModel):
    """Expected search JSON; the endpoint separately rejects blank questions."""

    question: str
    method: Literal["tfidf", "semantic"] = "tfidf"


app = FastAPI(title="PDF assistant")

# Storage functions read and write SQLite; no global document cache is needed.


@app.get("/health")
def health():
    """Report that the API is running."""
    return {"status": "ok"}


@app.post("/files/")
async def upload_file(file: UploadFile = File(...)):
    """Validate, extract, chunk, and save one uploaded PDF's data in SQLite.

    File(...) declares a required upload. Return its generated ID, metadata, and
    a short preview. Reject oversized files with 413 and unsupported PDFs with 400.
    """
    max_size = 10 * 1024 * 1024  # 10 MiB in bytes

    # This checks an already received upload before PDF parsing.
    if file.size is not None and file.size > max_size:
        raise HTTPException(
            status_code=413, detail="File size exceeds the maximum limit of 10 MiB"
        )

    reader = validate_pdf(file)

    pages = extract_pages(reader)

    # Blank pages are allowed, but at least one page must contain actual text.
    if not any(page["content"].strip() for page in pages):
        raise HTTPException(
            status_code=400,
            detail="The PDF has no extractable text. Scanned PDFs require OCR.",
        )

    # Use an independent ID so uploads with identical filenames stay separate.
    document_id = str(uuid4())

    # Build chunks locally, then save document, pages, and chunks together.
    chunks = []

    # Here page is one of our dictionaries, rather than a pypdf PageObject.
    # Chunk each page separately so every chunk has an unambiguous page number.
    for page in pages:
        for text in chunk_text(page["content"]):
            chunks.append(
                {
                    # Keep the source ID if chunks are later collected into a separate list.
                    "document_id": document_id,
                    "page_number": page["page_number"],
                    "chunk_id": str(uuid4()),
                    "content": text,
                }
            )

    # Commit the processed data before reporting a successful upload.
    save_document(
        document_id=document_id,
        filename=file.filename or "unnamed.pdf",
        pages=pages,
        chunks=chunks,
    )

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "page_count": len(pages),
        "document_id": document_id,
        # The no-text check above guarantees a nonblank page exists.
        # next selects the first one; [:200] limits only the response preview.
        "preview": next(page["content"] for page in pages if page["content"].strip())[
            :200
        ],
        "message": "File uploaded and processed successfully",
    }


@app.get("/documents/{document_id}")
def get_document(document_id: str):
    """Return a stored document's ID, filename, and pages; return 404 if unknown.

    document_id comes from the URL path. This retrieves extracted data without
    reopening the PDF; stored chunks are currently omitted from the response.
    """

    document = load_document(document_id)
    # load_document returns a dictionary built from database rows, or None.

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": document_id,
        "filename": document["filename"],
        "pages": document["pages"],
    }


@app.post("/documents/{document_id}/search")
def search_document(document_id: str, body: SearchRequest):
    """Search saved chunks using TF-IDF or semantic similarity."""
    document = load_document(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    question = body.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    chunks = document["chunks"]

    if body.method == "semantic":
        needs_embeddings = any(
            chunk.get("embedding") is None or chunk.get("embedding_model") != MODEL_NAME
            for chunk in chunks
        )

        if needs_embeddings:
            add_embeddings(chunks)
            save_chunk_embeddings(chunks)

        results = search_semantic(chunks, question)
    else:
        results = search_chunks(chunks, question)

    return {
        "document_id": document_id,
        "question": question,
        "method": body.method,
        "results": results,
    }


@app.get("/documents/")
def get_all_documents():
    """List saved documents without their full pages or chunks."""
    return {"documents": list_documents()}


@app.delete("/documents/{document_id}", status_code=204)
def remove_document(document_id: str):
    """Delete document data via foreign-key cascades; return 204 or 404."""
    deleted = delete_document(document_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
