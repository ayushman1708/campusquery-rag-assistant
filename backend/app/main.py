import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.services.pdf_extractor import extract_pages

app = FastAPI(
    title="CampusQuery API",
    description="Citation-grounded university knowledge assistant",
    version="0.1.0",
)

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"
ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class HealthResponse(BaseModel):
    status: str
    service: str


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_size: int
    uploaded_at: str
    file_path: str


class PageExtractionResponse(BaseModel):
    document_id: str
    filename: str
    total_pages: int
    pages: list[dict]


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to CampusQuery API",
        "status": "running",
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    return HealthResponse(
        status="healthy",
        service="CampusQuery backend",
    )


@app.post("/upload", response_model=DocumentUploadResponse, tags=["Documents"])
async def upload_document(
    file: UploadFile = File(..., description="PDF document to upload"),
):
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are allowed. Received extension: {file_ext}",
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE} bytes, received: {file_size} bytes",
        )

    # Generate unique document ID
    document_id = str(uuid.uuid4())
    safe_filename = f"{document_id}{file_ext}"
    file_path = UPLOAD_DIR / safe_filename

    # Ensure upload directory exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        file_size=file_size,
        uploaded_at=datetime.utcnow().isoformat(),
        file_path=str(file_path),
    )


@app.post("/extract", response_model=PageExtractionResponse, tags=["Documents"])
async def extract_document(
    document_id: str = File(..., description="Document ID from /upload response"),
):
    # Find file by document_id
    file_path = None
    filename = None
    for file in UPLOAD_DIR.glob("*.pdf"):
        if file.stem == document_id:
            file_path = file
            filename = file.name
            break

    if file_path is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID {document_id} not found",
        )

    # Extract pages
    pages = extract_pages(file_path)

    return PageExtractionResponse(
        document_id=document_id,
        filename=filename,
        total_pages=len(pages),
        pages=pages,
    )