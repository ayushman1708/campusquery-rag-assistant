import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

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