from __future__ import annotations

import asyncio
from typing import Callable, Any

import chardet


def decode_text(file_bytes: bytes) -> str:
    """Decode bytes to text with encoding detection."""
    detected = chardet.detect(file_bytes)
    encoding = detected['encoding'] or 'utf-8'
    return file_bytes.decode(encoding, errors='ignore')


def find_page(position: int, page_positions: list[tuple[int, int]]) -> int | None:
    """Find which page a text position belongs to.

    page_positions is a sorted list of (char_position, page_number).
    Returns the page number for the largest marker position <= the given position.
    """
    result = None
    for pos, page in page_positions:
        if pos <= position:
            result = page
        else:
            break
    return result


async def run_sync(sync_func: Callable, *args: Any, **kwargs: Any) -> Any:
    """Run a synchronous function in a thread to avoid blocking the event loop."""
    return await asyncio.to_thread(sync_func, *args, **kwargs)
