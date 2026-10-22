"""Learning API: upload PDFs, extract numbered pages, and build searchable chunks.

Document data lives in memory; original PDF files are not permanently saved.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from uuid import uuid4
from retrieval import score_chunks
from pydantic import BaseModel
from retrieval import search_chunks


class SearchRequest(BaseModel):
    question: str

app = FastAPI(title="PDF assistant")

# In-memory storage: restarting the server clears all uploaded document data.
# Structure: {document_id: {"filename": ..., "pages": [...], "chunks": [...]}}
documents = {}


def validate_pdf(file: UploadFile) -> PdfReader:
    """Return a PdfReader for an acceptable upload, or raise an HTTP 400 error.

    UploadFile wraps the upload; file.file is its underlying readable file object.
    This checks PDF structure, not whether its pages contain extractable text.
    """
    try:
        # Give pypdf the readable file object contained in UploadFile.
        reader = PdfReader(file.file)

        if reader.is_encrypted:
            raise HTTPException(
                status_code=400, detail="Encrypted PDF files are not allowed"
            )

        if len(reader.pages) == 0:
            raise HTTPException(status_code=400, detail="The PDF has no page")

    except PdfReadError:
        raise HTTPException(status_code=400, detail="Invalid PDF file")

    return reader


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

    pages = []
    try:
        # enumerate supplies human-facing page numbers; page is a pypdf page object.
        for page_number, page in enumerate(reader.pages, start=1):
            # Keep the page number beside the text for later source references.
            # If extraction returns None, store an empty string instead.
            pages.append(
                {"page_number": page_number, "content": page.extract_text() or ""}
            )
    except PdfReadError:
        # Opening the PDF can succeed even if a page fails during extraction.
        raise HTTPException(
            status_code=400, detail="The PDF is damaged and its text could not be read."
        )

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
            chunks.append({
            # Keep the source ID if chunks are later collected into a separate list.
            "document_id": document_id,
            "page_number": page["page_number"],
            "chunk_id": str(uuid4()),
            "content": text
        })

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


def chunk_text(
    text: str, chunk_size: int = 1000, chunk_overlap: int = 200
) -> list[str]:
    """Return nonblank text slices, with sizes measured in characters.

    Defaults: up to 1,000 characters per slice, with 200 characters of overlap
    before stripping edge whitespace. Overlap repeats boundary context between
    neighboring slices. Return an empty list for empty or whitespace-only text.
    Raise ValueError for a nonpositive size or overlap outside [0, chunk_size).
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    # Chained comparison: overlap must be >= 0 AND < chunk_size.
    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("chunk_overlap must be non-negative and less than chunk_size")

    chunks = []
    step = chunk_size - chunk_overlap

    # With the defaults, starting positions are 0, 800, 1600, and so on.
    for start in range(0, len(text), step):
        # Slicing includes start and excludes the end; strip removes edge whitespace.
        chunk = text[start : start + chunk_size].strip()

        if chunk:
            chunks.append(chunk)

        # Once a slice reaches the end, avoid another slice of only repeated text.
        if start + chunk_size >=len(text):
            break   
    

    return chunks

@app.post("/documents/{document_id}/search")
def search_document(document_id: str, body: SearchRequest):
    """Score this document's chunks against a nonblank question."""
    document = documents.get(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    results = search_chunks(document["chunks"], question)

    return {
        "document_id": document_id,
        "question": question,
        "results": results
    }






