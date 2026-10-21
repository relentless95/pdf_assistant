from fastapi import FastAPI, File, UploadFile, HTTPException
from pypdf import PdfReader
from pypdf.errors import PdfReadError

app = FastAPI(title="PDF assistant")


def validate_pdf(file: UploadFile) -> PdfReader:
    """Open an uploaded PDF, rejecting encrypted, zero-page, or unreadable files."""
    try:
        # Give pypdf the readable file object contained in UploadFile.
        reader = PdfReader(file.file)

        if reader.is_encrypted:
            raise HTTPException(
                status_code=400, detail="Encrypted PDF files are not allowed"
            )

        if len(reader.pages) == 0:
            raise HTTPException(status_code=400, detail="|The PDF has no page")

        return reader

    except PdfReadError:
        raise HTTPException(status_code=400, detail="Invalid PDF file")





@app.get("/health")
def health():
    """Report that the API is running."""
    return {"status": "ok"}


@app.post("/files/")
async def upload_file(file: UploadFile = File(...)):
    """Check upload size and PDF readability, then return file metadata."""
    max_size = 10 * 1024 * 1024  # 10 MiB in bytes

    # This checks an already received upload before PDF parsing.
    if file.size is not None and file.size > max_size:
        raise HTTPException(
            status_code=413, detail="File size exceeds the maximum limit of 10 MB"
        )

    reader = validate_pdf(file)

    return {"filename": file.filename, "content_type": file.content_type, "page_count": len(reader.pages)}


@app.get("/documents/{document_id}")
def get_document(document_id: int):
    """Echo a document ID; document storage and lookup are not implemented yet."""
    return {"document_id": document_id, "message": "Document retrieved successfully"}
