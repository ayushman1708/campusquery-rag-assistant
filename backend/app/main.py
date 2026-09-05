import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from pydantic import BaseModel

from app.services.pdf_extractor import extract_pages
from app.services.text_chunker import chunk_pages_with_metadata
from app.services.database import init_db, insert_chunks
from app.services.embeddings import generate_embedding

app = FastAPI(
    title="CampusQuery API",
    description="Citation-grounded university knowledge assistant",
    version="0.1.0",
)

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"
ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP = 50


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


class ChunkingResponse(BaseModel):
    document_id: str
    filename: str
    total_chunks: int
    chunks: list[dict]


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
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are allowed. Received extension: {file_ext}",
        )

    content = await file.read()
    file_size = len(content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE} bytes, received: {file_size} bytes",
        )

    document_id = str(uuid.uuid4())
    safe_filename = f"{document_id}{file_ext}"
    file_path = UPLOAD_DIR / safe_filename

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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

    pages = extract_pages(file_path)

    return PageExtractionResponse(
        document_id=document_id,
        filename=filename,
        total_pages=len(pages),
        pages=pages,
    )


@app.post("/chunk", response_model=ChunkingResponse, tags=["Documents"])
async def chunk_document(
    document_id: str = File(..., description="Document ID from /upload response"),
    chunk_size: int = Form(
        default=DEFAULT_CHUNK_SIZE,
        ge=100,
        le=2000,
        description="Chunk size in characters",
    ),
    overlap: int = Form(
        default=DEFAULT_OVERLAP,
        ge=0,
        le=500,
        description="Overlap in characters",
    ),
):
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

    pages = extract_pages(file_path)
    chunks = chunk_pages_with_metadata(
        pages,
        document_id,
        filename,
        chunk_size,
        overlap,
    )

    return ChunkingResponse(
        document_id=document_id,
        filename=filename,
        total_chunks=len(chunks),
        chunks=chunks,
    )
@app.post("/embed-and-store", tags=["Documents"])
async def embed_and_store(
    document_id: str = File(..., description="Document ID from /upload response"),
    chunk_size: int = Form(default=500, ge=100, le=2000),
    overlap: int = Form(default=50, ge=0, le=500),
):
    # Initialize database (first time only)
    init_db()

    # Find file
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

    # Extract and chunk
    pages = extract_pages(file_path)
    chunks = chunk_pages_with_metadata(
        pages,
        document_id,
        filename,
        chunk_size,
        overlap,
    )

    # Generate embeddings
    chunks_with_embeddings = []
    for chunk in chunks:
        embedding = generate_embedding(chunk["chunk_text"])
        chunk_with_embedding = {**chunk, "embedding": embedding}
        chunks_with_embeddings.append(chunk_with_embedding)

    # Store in database
    insert_chunks(chunks_with_embeddings)

    return {
        "document_id": document_id,
        "filename": filename,
        "total_chunks_stored": len(chunks_with_embeddings),
        "embedding_model": "all-MiniLM-L6-v2",
        "embedding_dimension": 384,
    }