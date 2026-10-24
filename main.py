"""Learning API: upload PDFs, extract numbered pages, and build searchable chunks.

Document data lives in memory; original PDF files are not permanently saved.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from pypdf.errors import PdfReadError
from uuid import uuid4
from pydantic import BaseModel
from retrieval import search_chunks
from extraction import extract_pages, validate_pdf
from chunking import chunk_text


class SearchRequest(BaseModel):
    question: str


app = FastAPI(title="PDF assistant")

# In-memory storage: restarting the server clears all uploaded document data.
# Structure: {document_id: {"filename": ..., "pages": [...], "chunks": [...]}}
documents = {}


@app.get("/health")
def health():
    """Report that the API is running."""
    return {"status": "ok"}


@app.post("/files/")
async def upload_file(file: UploadFile = File(...)):
    """Validate, extract, chunk, and store one uploaded PDF in memory.

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

    # Store only after validation/extraction succeed; the original PDF is not saved.
    documents[document_id] = {"filename": file.filename, "pages": pages}

    # This references the same dictionary stored under document_id; it is not a copy.
    document = documents[document_id]
    chunks = []

    # Here page is one of our dictionaries, rather than a pypdf PageObject.
    # Chunk each page separately so every chunk has an unambiguous page number.
    for page in document["pages"]:
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

    # Attach the list to this specific document, not to the outer documents dictionary.
    documents[document_id]["chunks"] = chunks

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
    document = documents.get(document_id)
    # dict.get returns None for an unknown ID rather than raising KeyError.

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": document_id,
        "filename": document["filename"],
        "pages": document["pages"],
    }



@app.post("/documents/{document_id}/search")
def search_document(document_id: str, body: SearchRequest):
    """Score this document's chunks against a non blank question."""
    document = documents.get(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    results = search_chunks(document["chunks"], question)

    return {"document_id": document_id, "question": question, "results": results}
