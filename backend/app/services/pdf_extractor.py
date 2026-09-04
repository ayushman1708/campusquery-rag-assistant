from pathlib import Path
from typing import List, Dict, Any

import fitz  # PyMuPDF


def extract_pages(file_path: Path) -> List[Dict[str, Any]]:
    """
    Extract text from each page of a PDF.

    Returns a list of dicts:
    [
        {
            "page_number": 1,
            "text": "Page 1 text...",
            "char_count": 1234
        },
        ...
    ]
    """
    doc = fitz.open(file_path)
    pages = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text")
        pages.append(
            {
                "page_number": page_number,
                "text": text,
                "char_count": len(text),
            }
        )

    doc.close()
    return pages