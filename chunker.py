# chunker.py
"""
Module: chunker.py

Description:
    Provides a function to split (chunk) a long string into smaller
    pieces so that each piece remains below a specified maximum length.
"""

import re


def chunk_text(
    text: str, max_length: int = 5000
) -> list[str]:  # ADDED: Reduced max_length
    """
    Splits text into chunks, ensuring it breaks at sentence or paragraph boundaries.
    """
    sentences = re.split(r"(?<=[.!?]) +", text)  # Split at sentence endings
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
