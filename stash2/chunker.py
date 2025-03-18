# chunker.py
"""
Module: chunker.py

Description:
    Provides a function to split (chunk) a long string into smaller
    pieces so that each piece remains below a specified maximum length.
"""

def chunk_text(text: str, max_length: int = 900000) -> list[str]:
    """
    Splits a given text into smaller chunks, each at most `max_length` characters.

    :param text: The input text to chunk.
    :param max_length: The maximum length (in characters) for each chunk.
    :return: A list of string chunks.
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + max_length
        chunk = text[start:end]
        chunks.append(chunk)
        start = end

    return chunks
