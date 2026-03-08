"""Default flat chunking strategy — preserves the original LangRAG behavior."""

from collections.abc import AsyncGenerator

from .base import IndexStrategy
from ..chunker import chunk_text, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


class ChunkStrategy(IndexStrategy):
    """Simple fixed-size chunking with overlap.

    Each chunk is independently embedded and stored.  This is the original
    behaviour of LangRAG prior to strategy modularisation.
    """

    async def build_chunks_and_metadata(
        self,
        text: str,
        doc_id: str,
        filename: str,
        creation_settings: dict,
        plugin=None,
    ) -> AsyncGenerator[tuple[list[str], list[str], list[dict]], None]:
        chunk_size = creation_settings.get("chunk_size") or DEFAULT_CHUNK_SIZE
        overlap = creation_settings.get("overlap") or DEFAULT_CHUNK_OVERLAP

        chunks = chunk_text(text, chunk_size, overlap)

        ids: list[str] = []
        metadatas: list[dict] = []
        for i, chunk in enumerate(chunks):
            ids.append(f"{doc_id}_{i}")
            metadatas.append({
                "file_id": doc_id,
                "document_id": doc_id,
                "document_name": filename,
                "chunk_index": i,
                "text": chunk,
                "index_type": "chunk",
            })

        yield chunks, ids, metadatas
