from fastapi import FastAPI, File, UploadFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError


app = FastAPI(title = "PDF assistant")


def validate_pdf(file: UploadFile) -> PdfReader:
    try:
        reader = PdfReader(file.file)

        if reader.is_encrypted:
            raise HTTPException(
                status_code = 400, 
                detail = "Encrypted PDF files are not allowed"

            )
    except PdfReadError:
        raise HTTPException(
            status_code = 400, 
            detail = "Invalid PDF file"
        )   

        

def validate_pdf(file: UploadFile):
    if not file.content_type == "application/pdf":
        raise ValueError("Only PDF files are allowed")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/files/")
async def upload_file(file: UploadFile = File(...)):
    # Here you can process the uploaded file as needed
    return {"filename": file.filename, "content_type": file.content_type}

@app.get("/documents/{document_id}")
def get_document(document_id: int):
    # Here you can retrieve the document based on the document_id
    return {"document_id": document_id, "message": "Document retrieved successfully"}