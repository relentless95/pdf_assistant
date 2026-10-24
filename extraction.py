"""Validate PDF structure and extract numbered text pages without saving files."""

from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
from pypdf.errors import PdfReadError


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
def extract_pages(reader: PdfReader) -> list[dict]:
    """Return extracted text and page numbers without modifying a caller's list."""
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

    return pages
