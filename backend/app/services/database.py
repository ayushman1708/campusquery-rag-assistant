import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

# Load environment variables
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """Initialize the chunks table with pgvector."""
    conn = get_connection()
    cur = conn.cursor()

    # Enable pgvector extension
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Create chunks table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id SERIAL PRIMARY KEY,
            chunk_index INTEGER NOT NULL,
            document_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            char_count INTEGER NOT NULL,
            embedding vector(384) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


def insert_chunks(chunks_with_embeddings: list[dict]):
    """Insert chunks with embeddings into the database."""
    conn = get_connection()
    cur = conn.cursor()

    query = """
        INSERT INTO chunks 
        (chunk_index, document_id, filename, page_number, chunk_text, char_count, embedding)
        VALUES %s
    """

    values = [
        (
            chunk["chunk_index"],
            chunk["document_id"],
            chunk["filename"],
            chunk["page_number"],
            chunk["chunk_text"],
            chunk["char_count"],
            chunk["embedding"],
        )
        for chunk in chunks_with_embeddings
    ]

    execute_values(cur, query, values)
    conn.commit()
    cur.close()
    conn.close()