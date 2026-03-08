"""Text chunking utilities using recursive character splitting.

Extracted from langrag.py to allow reuse across different index strategies.
"""

import logging

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50

# Separators in order of semantic significance (paragraph → sentence → word → char)
_SEPARATORS = [
    "\n\n",  # Paragraphs
    "\n",    # Lines
    ". ",    # Sentences
    "。",    # Chinese/Japanese sentence end
    "! ",    # Exclamations
    "? ",    # Questions
    "; ",    # Semicolons
    "；",    # Chinese semicolon
    "，",    # Chinese comma
    ", ",    # Commas
    " ",     # Spaces (words)
    "",      # Characters (fallback)
]


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text into overlapping chunks using recursive character splitting.

    Attempts to split at natural semantic boundaries (paragraphs, sentences,
    words) before falling back to character-level splitting. This preserves
    readability and context compared to a naive sliding-window approach.

    Args:
        text: The text to split.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of overlapping characters between consecutive chunks.

    Returns:
        List of text chunks.
    """
    if not text:
        return []

    if chunk_overlap >= chunk_size:
        logger.warning(
            f"chunk_overlap ({chunk_overlap}) >= chunk_size ({chunk_size}), "
            "clamping overlap to chunk_size - 1"
        )
        chunk_overlap = chunk_size - 1

    return _split_recursive(text, _SEPARATORS, chunk_size, chunk_overlap)


def _split_recursive(
    text: str,
    separators: list[str],
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """Recursively split *text* trying each separator in priority order."""
    final_chunks: list[str] = []
    separator = separators[0] if separators else ""
    remaining_separators = separators[1:] if len(separators) > 1 else []

    splits = _split_by_separator(text, separator)

    current_parts: list[str] = []
    current_len = 0

    for part in splits:
        part_len = len(part)

        # Single piece already exceeds limit → recurse with finer separator
        if part_len > chunk_size:
            # Flush accumulated parts first
            if current_parts:
                final_chunks.append("".join(current_parts))
                current_parts = _overlap_parts(current_parts, chunk_overlap)
                current_len = sum(len(p) for p in current_parts)

            if remaining_separators:
                final_chunks.extend(
                    _split_recursive(part, remaining_separators, chunk_size, chunk_overlap)
                )
            else:
                final_chunks.extend(_split_by_char(part, chunk_size, chunk_overlap))
            continue

        # Would adding this part exceed the limit?
        if current_parts and current_len + part_len > chunk_size:
            final_chunks.append("".join(current_parts))
            current_parts = _overlap_parts(current_parts, chunk_overlap)
            current_len = sum(len(p) for p in current_parts)

        current_parts.append(part)
        current_len += part_len

    if current_parts:
        final_chunks.append("".join(current_parts))

    return final_chunks


def _split_by_separator(text: str, separator: str) -> list[str]:
    """Split *text* by *separator*, keeping the separator attached to the left piece."""
    if separator == "":
        return list(text)

    parts = text.split(separator)
    result: list[str] = []
    for piece in parts[:-1]:
        if piece or separator.strip():
            result.append(piece + separator)
    if parts[-1]:
        result.append(parts[-1])
    return result


def _overlap_parts(parts: list[str], overlap: int) -> list[str]:
    """Return trailing *parts* whose combined length fits within *overlap*."""
    if overlap <= 0:
        return []

    kept: list[str] = []
    total = 0
    for part in reversed(parts):
        if total + len(part) > overlap:
            break
        kept.insert(0, part)
        total += len(part)
    return kept


def _split_by_char(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Last-resort character-level split."""
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += chunk_size - overlap
    return chunks
