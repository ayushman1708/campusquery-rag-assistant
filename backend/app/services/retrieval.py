from app.services.database import get_connection
from app.services.embeddings import generate_embedding


def search_chunks(query: str, top_k: int = 5) -> list[dict]:
    """Search for chunks most similar to the query."""
    # Generate query embedding
    query_embedding = generate_embedding(query)

    # Connect to database
    conn = get_connection()
    cur = conn.cursor()

    # Perform similarity search using cosine distance
    # Cast the query embedding to vector type
    cur.execute("""
        SELECT 
            chunk_index,
            document_id,
            filename,
            page_number,
            chunk_text,
            char_count,
            1 - (embedding <=> %s::vector) AS similarity
        FROM chunks
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (query_embedding, query_embedding, top_k))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Convert to list of dicts
    results = []
    for row in rows:
        results.append({
            "chunk_index": row[0],
            "document_id": row[1],
            "filename": row[2],
            "page_number": row[3],
            "chunk_text": row[4],
            "char_count": row[5],
            "similarity": float(row[6]),
        })

    return results