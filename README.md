# CampusQuery

CampusQuery is a citation-grounded Retrieval-Augmented Generation (RAG) assistant for university information.

It is designed to help students find reliable answers from university regulations, examination notices, admission guidelines, academic calendars, course documents, and frequently asked questions.

## Problem

University information is often spread across many PDFs and web pages. Students may struggle to find accurate answers about attendance, examinations, admission, syllabus, fees, and academic regulations.

CampusQuery will retrieve relevant official university content and generate answers supported by source citations.

## Planned Features

- PDF and approved university web-page ingestion
- Document cleaning and structure-aware chunking
- Metadata extraction and filtering
- PostgreSQL and pgvector vector storage
- Hybrid semantic and keyword retrieval
- Passage reranking
- Grounded LLM answers
- Page-level citations
- Unsupported-question detection
- User feedback collection and query logging
- RAG evaluation using a custom benchmark

## Planned Architecture

```text
University PDFs / web pages
          |
          v
Document ingestion and cleaning
          |
          v
Structure-aware chunking + metadata
          |
          v
Embedding model --> PostgreSQL + pgvector
          |
          v
User question --> intent classification --> hybrid retrieval
          |
          v
Reranking top passages
          |
          v
Grounded LLM answer + citations
          |
          v
Web interface, feedback, and logging
```

## Tech Stack

- Backend: Python, FastAPI
- Frontend: React, Vite, Tailwind CSS
- Database: PostgreSQL with pgvector
- Embeddings: SentenceTransformers
- Reranking: Cross-encoder model
- LLM: Gemini API
- PDF Processing: PyMuPDF
- Evaluation: Ragas

## Current Status

**Day 1 of 24 — Complete**

- Project structure created
- Python virtual environment configured
- FastAPI backend initialized
- Health endpoint tested successfully

## Local Setup

```bash
cd backend
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
fastapi dev app/main.py
```

Open the backend documentation at:

```text
http://127.0.0.1:8000/docs
```

## License

This project is being developed as a student portfolio project.