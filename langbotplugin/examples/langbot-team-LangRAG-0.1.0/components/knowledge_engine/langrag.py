import logging

from langbot_plugin.api.definition.components.knowledge_engine import KnowledgeEngine, KnowledgeEngineCapability
from langbot_plugin.api.entities.builtin.rag import (
    IngestionContext,
    IngestionResult,
    RetrievalContext,
    RetrievalResponse,
    RetrievalResultEntry,
    DocumentStatus,
    SearchType,
)

from .parser import FileParser
from .query_rewrite import retrieve_with_rewrite
from .strategies import get_strategy

logger = logging.getLogger(__name__)

# Batch size for embedding API calls.
# Larger batches = fewer round-trips.  Keep under ~64 to avoid IPC response
# timeouts.
EMBEDDING_BATCH_SIZE = 32


class LangRAG(KnowledgeEngine):
    """Simple Knowledge Engine implementation using Plugin IPC.

    Provides:
    - Document ingestion with parsing, chunking, embedding, and vector storage
    - Vector-based retrieval
    - Full integration with Host's embedding models and vector database
    """

    @classmethod
    def get_capabilities(cls) -> list[str]:
        """Declare supported capabilities."""
        return [KnowledgeEngineCapability.DOC_INGESTION, KnowledgeEngineCapability.DOC_PARSING]

    # ========== Lifecycle Hooks ==========

    async def on_knowledge_base_create(self, kb_id: str, config: dict) -> None:
        logger.info(f"Knowledge base created: {kb_id} with config: {config}")

    async def on_knowledge_base_delete(self, kb_id: str) -> None:
        logger.info(f"Knowledge base deleted: {kb_id}")

    # ========== Helpers ==========

    async def _embed_and_upsert(
        self,
        collection_id: str,
        embedding_model_uuid: str,
        texts: list[str],
        ids: list[str],
        metas: list[dict],
    ) -> int:
        """Embed a batch of texts and upsert into the vector store.

        Returns the number of vectors stored.
        """
        vectors = await self.plugin.invoke_embedding(embedding_model_uuid, texts)
        await self.plugin.vector_upsert(
            collection_id=collection_id,
            vectors=vectors,
            ids=ids,
            metadata=metas,
            documents=texts,
        )
        return len(texts)

    # ========== Core Methods ==========

    async def ingest(self, context: IngestionContext) -> IngestionResult:
        """Handle document ingestion: Read -> Parse -> Chunk -> Embed -> Store.

        Uses an async generator pipeline: the strategy yields batches
        incrementally, and each batch is embedded and upserted as soon as it
        is ready.  This ensures partial results are persisted early.
        """
        doc_id = context.file_object.metadata.document_id
        filename = context.file_object.metadata.filename
        collection_id = context.get_collection_id()

        logger.info(f"Ingesting file: {filename} (doc={doc_id}) into collection: {collection_id}")

        # 1. Get file content from Host
        try:
            content_bytes = await self.plugin.get_knowledge_file_stream(context.file_object.storage_path)
        except Exception as e:
            logger.error(f"Failed to get file content: {e}")
            return IngestionResult(
                document_id=doc_id,
                status=DocumentStatus.FAILED,
                error_message=f"Could not read file: {e}",
            )

        try:
            # 2. Parse file content
            parser = FileParser()
            text_content = await parser.parse(content_bytes, filename)

            if not text_content:
                logger.warning(f"No text content extracted from file: {filename}")
                return IngestionResult(
                    document_id=doc_id,
                    status=DocumentStatus.COMPLETED,
                    chunks_created=0,
                )

            # 3. Build chunks via strategy (async generator)
            index_type = context.creation_settings.get("index_type") or "chunk"
            strategy = get_strategy(index_type)
            embedding_model_uuid = context.creation_settings.get("embedding_model_uuid", "")
            logger.info(f"Strategy: {index_type} ({strategy.__class__.__name__})")

            # 4. Progressive ingest: consume generator → accumulate → embed+upsert
            #    when a full batch is ready.  Embedding happens between generator
            #    yields (sequential, not concurrent) to avoid IPC timeout issues.
            pending_texts: list[str] = []
            pending_ids: list[str] = []
            pending_metas: list[dict] = []
            total_stored = 0

            async for batch_texts, batch_ids, batch_metas in strategy.build_chunks_and_metadata(
                text_content, doc_id, filename, context.creation_settings,
                plugin=self.plugin,
            ):
                pending_texts.extend(batch_texts)
                pending_ids.extend(batch_ids)
                pending_metas.extend(batch_metas)

                # Flush full batches immediately
                while len(pending_texts) >= EMBEDDING_BATCH_SIZE:
                    t = pending_texts[:EMBEDDING_BATCH_SIZE]
                    i = pending_ids[:EMBEDDING_BATCH_SIZE]
                    m = pending_metas[:EMBEDDING_BATCH_SIZE]
                    pending_texts = pending_texts[EMBEDDING_BATCH_SIZE:]
                    pending_ids = pending_ids[EMBEDDING_BATCH_SIZE:]
                    pending_metas = pending_metas[EMBEDDING_BATCH_SIZE:]
                    total_stored += await self._embed_and_upsert(
                        collection_id, embedding_model_uuid, t, i, m,
                    )

            # Flush remaining
            if pending_texts:
                total_stored += await self._embed_and_upsert(
                    collection_id, embedding_model_uuid,
                    pending_texts, pending_ids, pending_metas,
                )

            if total_stored:
                unit = "Q&A pairs" if index_type == "qa" else "chunks"
                logger.info(f"Ingestion complete: {total_stored} {unit} stored")

            return IngestionResult(
                document_id=doc_id,
                status=DocumentStatus.COMPLETED,
                chunks_created=total_stored,
            )

        except Exception as e:
            logger.error(f"Ingestion failed for {filename}: {e}")
            return IngestionResult(
                document_id=doc_id,
                status=DocumentStatus.FAILED,
                error_message=str(e),
            )

    async def retrieve(self, context: RetrievalContext) -> RetrievalResponse:
        """Retrieve relevant content with support for vector, full-text, and hybrid search."""
        query = context.query
        top_k = context.retrieval_settings.get("top_k", 5)
        collection_id = context.get_collection_id()
        search_type = context.retrieval_settings.get("search_type", SearchType.VECTOR)

        # Determine strategy for post-processing
        index_type = context.creation_settings.get("index_type") or "chunk"
        strategy = get_strategy(index_type)
        logger.info(
            f"Retrieve: strategy={index_type}, top_k={top_k}, "
            f"query_rewrite={context.retrieval_settings.get('query_rewrite', 'off')}, "
            f"query={query!r}"
        )

        # For parent_child, over-fetch to allow dedup to still yield top_k results
        fetch_k = top_k * 3 if index_type in ("parent_child", "qa") else top_k

        # Check query rewrite settings
        query_rewrite = context.retrieval_settings.get("query_rewrite", "off")
        rewrite_llm = context.retrieval_settings.get("rewrite_llm_model_uuid", "")

        if query_rewrite != "off" and rewrite_llm:
            logger.info(f"Query rewrite enabled: strategy={query_rewrite}")
            results = await retrieve_with_rewrite(
                plugin=self.plugin,
                query=query,
                query_rewrite=query_rewrite,
                rewrite_llm=rewrite_llm,
                collection_id=collection_id,
                embedding_model_uuid=context.creation_settings.get("embedding_model_uuid", ""),
                fetch_k=fetch_k,
                filters=context.filters or None,
                search_type=search_type,
            )
        else:
            # Original logic: embed query → vector_search
            query_vector: list[float] = []
            if search_type != SearchType.FULL_TEXT:
                embedding_model_uuid = context.creation_settings.get("embedding_model_uuid", "")
                query_vectors = await self.plugin.invoke_embedding(embedding_model_uuid, [query])
                query_vector = query_vectors[0]

            results = await self.plugin.vector_search(
                collection_id=collection_id,
                query_vector=query_vector,
                top_k=fetch_k,
                filters=context.filters or None,
                search_type=search_type,
                query_text=query,
            )

        # Post-process (strategy may deduplicate / re-rank)
        raw_count = len(results)
        results = strategy.postprocess_results(results, top_k)
        logger.info(
            f"Retrieve post-process: {raw_count} raw → {len(results)} after dedup "
            f"(fetch_k={fetch_k})"
        )

        # Format results
        entries: list[RetrievalResultEntry] = []
        for res in results:
            content_text = res.get("metadata", {}).get("text", "")
            raw_score = res.get("score")
            distance = res.get("distance", raw_score)

            doc_name = res.get("metadata", {}).get("document_name", "")
            entries.append(
                RetrievalResultEntry(
                    id=res["id"],
                    content=[{"type": "text", "text": content_text, "file_name": doc_name}],
                    metadata=res.get("metadata", {}),
                    score=raw_score,
                    distance=distance,
                )
            )

        return RetrievalResponse(results=entries, total_found=len(entries))

    async def delete_document(self, kb_id: str, document_id: str) -> bool:
        """Delete a document's vectors by file_id."""
        count = await self.plugin.vector_delete(
            collection_id=kb_id,
            file_ids=[document_id],
        )
        return count > 0
