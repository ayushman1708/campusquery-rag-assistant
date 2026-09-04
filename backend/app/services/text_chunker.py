from typing import List, Dict, Any


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> List[str]:
    """
    Split text into fixed-size chunks with overlap.

    Args:
        text: Input text to chunk
        chunk_size: Target chunk size in characters
        overlap: Number of overlapping characters between chunks

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


def chunk_pages_with_metadata(
    pages: List[Dict[str, Any]],
    document_id: str,
    filename: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> List[Dict[str, Any]]:
    """
    Chunk extracted pages and attach metadata.

    Args:
        pages: List of page dicts from extract_pages()
        document_id: Unique document identifier
        filename: Original filename
        chunk_size: Target chunk size in characters
        overlap: Overlap in characters

    Returns:
        List of chunk dicts with metadata
    """
    all_chunks = []
    chunk_index = 0

    for page in pages:
        page_number = page["page_number"]
        page_text = page["text"]

        if not page_text.strip():
            continue

        page_chunks = chunk_text(page_text, chunk_size, overlap)

        for chunk_text_content in page_chunks:
            if not chunk_text_content.strip():
                continue

            all_chunks.append(
                {
                    "chunk_index": chunk_index,
                    "document_id": document_id,
                    "filename": filename,
                    "page_number": page_number,
                    "chunk_text": chunk_text_content,
                    "char_count": len(chunk_text_content),
                }
            )
            chunk_index += 1

    return all_chunks