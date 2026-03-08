"""Parent-Child index strategy.

Uses two-level chunking: large parent chunks for context richness, small child
chunks for precise embedding matches.  Child chunks are embedded, but the
metadata ``text`` field stores the parent chunk so that retrieval automatically
returns full context.
"""

import logging
from collections.abc import AsyncGenerator

from .base import IndexStrategy
from ..chunker import chunk_text, DEFAULT_CHUNK_OVERLAP

logger = logging.getLogger(__name__)

DEFAULT_PARENT_CHUNK_SIZE = 2048
DEFAULT_CHILD_CHUNK_SIZE = 256


class ParentChildStrategy(IndexStrategy):
    """Two-level parent / child chunking strategy.

    - Parent chunks are large (default 2048 chars), split with no overlap.
    - Each parent is further split into small child chunks (default 256 chars)
      with configurable overlap.
    - Child chunks are the units that get embedded.
    - The ``text`` metadata field on each child stores the **parent** chunk,
      so search results automatically carry richer context.
    - ``postprocess_results`` deduplicates by parent, keeping only the
      highest-scoring child per parent.
    """

    async def build_chunks_and_metadata(
        self,
        text: str,
        doc_id: str,
        filename: str,
        creation_settings: dict,
        plugin=None,
    ) -> AsyncGenerator[tuple[list[str], list[str], list[dict]], None]:
        parent_size = creation_settings.get("parent_chunk_size") or DEFAULT_PARENT_CHUNK_SIZE
        child_size = creation_settings.get("child_chunk_size") or DEFAULT_CHILD_CHUNK_SIZE
        overlap = creation_settings.get("overlap") or DEFAULT_CHUNK_OVERLAP

        # Split into parent chunks (no overlap between parents)
        parent_chunks = chunk_text(text, parent_size, 0)

        texts_to_embed: list[str] = []
        ids: list[str] = []
        metadatas: list[dict] = []

        for p_idx, parent in enumerate(parent_chunks):
            child_chunks = chunk_text(parent, child_size, overlap)
            for c_idx, child in enumerate(child_chunks):
                texts_to_embed.append(child)
                ids.append(f"{doc_id}_p{p_idx}_c{c_idx}")
                metadatas.append({
                    "file_id": doc_id,
                    "document_id": doc_id,
                    "document_name": filename,
                    "parent_index": p_idx,
                    "child_text": child,
                    "text": parent,  # retrieval returns parent context
                    "index_type": "parent_child",
                })

        yield texts_to_embed, ids, metadatas

    def postprocess_results(self, results: list[dict], top_k: int) -> list[dict]:
        """Deduplicate by parent chunk, keeping the highest-scoring child."""
        seen: dict[str, dict] = {}  # key → best result
        for res in results:
            meta = res.get("metadata", {})
            doc_id = meta.get("document_id", "")
            parent_idx = meta.get("parent_index", "")
            key = f"{doc_id}:{parent_idx}"

            if key not in seen:
                seen[key] = res
            else:
                existing_score = seen[key].get("score") or 0
                current_score = res.get("score") or 0
                if current_score > existing_score:
                    seen[key] = res

        deduped = list(seen.values())
        return deduped[:top_k]
