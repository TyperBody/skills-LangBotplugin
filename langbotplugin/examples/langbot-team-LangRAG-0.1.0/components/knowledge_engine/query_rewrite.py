"""Query rewriting strategies for retrieval augmentation.

Provides HyDE, Multi-Query, and Step-Back rewriting to improve recall quality.
Each strategy rewrites/expands the user query before embedding and searching.
"""

import logging

from langbot_plugin.api.entities.builtin.provider.message import Message

logger = logging.getLogger(__name__)

MULTI_QUERY_COUNT = 3

HYDE_PROMPT = """Please write a short passage that would answer the following question.
Write as if you are writing a paragraph from a reference document.
Do not say "I don't know" — just write a plausible answer.

Question: {query}

Passage:"""

MULTI_QUERY_PROMPT = """Given the following user question, generate {n} different search queries
that could help find relevant information. Each query should approach the question from a
different angle or use different terminology.

User question: {query}

Output exactly {n} queries, one per line (no numbering, no bullets):"""

STEP_BACK_PROMPT = """Given the following specific question, generate a more general/abstract
question that would help retrieve broader background context.

Specific question: {query}

General question:"""


def _extract_text(msg: Message) -> str:
    """Extract plain text from an LLM response Message."""
    if isinstance(msg.content, str):
        return msg.content.strip()
    if isinstance(msg.content, list):
        return "".join(
            e.text for e in msg.content if e.type == "text"
        ).strip()
    return ""


async def retrieve_with_rewrite(
    plugin,
    query: str,
    query_rewrite: str,
    rewrite_llm: str,
    collection_id: str,
    embedding_model_uuid: str,
    fetch_k: int,
    filters,
    search_type,
) -> list[dict]:
    """Route to the appropriate rewrite strategy and return raw search results."""
    if query_rewrite == "hyde":
        return await _retrieve_hyde(
            plugin, query, rewrite_llm, collection_id, embedding_model_uuid,
            fetch_k, filters, search_type,
        )
    elif query_rewrite == "multi_query":
        return await _retrieve_multi_query(
            plugin, query, rewrite_llm, collection_id, embedding_model_uuid,
            fetch_k, filters, search_type,
        )
    elif query_rewrite == "step_back":
        return await _retrieve_step_back(
            plugin, query, rewrite_llm, collection_id, embedding_model_uuid,
            fetch_k, filters, search_type,
        )
    else:
        logger.warning(f"Unknown query_rewrite strategy: {query_rewrite}, falling back to direct search")
        query_vectors = await plugin.invoke_embedding(embedding_model_uuid, [query])
        return await plugin.vector_search(
            collection_id=collection_id,
            query_vector=query_vectors[0],
            top_k=fetch_k,
            filters=filters,
            search_type=search_type,
            query_text=query,
        )


async def _retrieve_hyde(
    plugin, query, rewrite_llm, collection_id, embedding_model_uuid,
    fetch_k, filters, search_type,
) -> list[dict]:
    """HyDE: generate a hypothetical document, embed it, and search with that vector."""
    logger.info(f"[HyDE] Generating hypothetical document for query: {query!r}")
    prompt = HYDE_PROMPT.format(query=query)
    resp = await plugin.invoke_llm(rewrite_llm, [Message(role="user", content=prompt)])
    hypothetical_doc = _extract_text(resp)
    logger.info(f"[HyDE] Hypothetical document:\n{hypothetical_doc}")
    logger.info("[HyDE] Embedding hypothetical document and searching...")

    hyde_vectors = await plugin.invoke_embedding(embedding_model_uuid, [hypothetical_doc])
    results = await plugin.vector_search(
        collection_id=collection_id,
        query_vector=hyde_vectors[0],
        top_k=fetch_k,
        filters=filters,
        search_type=search_type,
        query_text=query,
    )
    logger.info(f"[HyDE] Search returned {len(results)} results")
    return results


async def _retrieve_multi_query(
    plugin, query, rewrite_llm, collection_id, embedding_model_uuid,
    fetch_k, filters, search_type,
) -> list[dict]:
    """Multi-Query: generate N query variants, search with each, merge and deduplicate."""
    logger.info(f"[Multi-Query] Generating {MULTI_QUERY_COUNT} sub-queries for: {query!r}")
    prompt = MULTI_QUERY_PROMPT.format(query=query, n=MULTI_QUERY_COUNT)
    resp = await plugin.invoke_llm(rewrite_llm, [Message(role="user", content=prompt)])
    raw_text = _extract_text(resp)
    sub_queries = [line.strip() for line in raw_text.splitlines() if line.strip()]
    sub_queries = sub_queries[:MULTI_QUERY_COUNT]
    logger.info("[Multi-Query] Generated sub-queries:")
    for i, sq in enumerate(sub_queries):
        logger.info(f"  [{i+1}] {sq}")

    # Embed original query + sub-queries
    all_queries = [query] + sub_queries
    logger.info(f"[Multi-Query] Embedding {len(all_queries)} queries (1 original + {len(sub_queries)} generated)")
    all_vectors = await plugin.invoke_embedding(embedding_model_uuid, all_queries)

    # Search with each vector and merge results
    seen_ids: set[str] = set()
    merged: list[dict] = []
    for i, vec in enumerate(all_vectors):
        results = await plugin.vector_search(
            collection_id=collection_id,
            query_vector=vec,
            top_k=fetch_k,
            filters=filters,
            search_type=search_type,
            query_text=query,
        )
        new_count = sum(1 for r in results if r["id"] not in seen_ids)
        logger.info(f"[Multi-Query] Query [{i}] returned {len(results)} results ({new_count} new)")
        for r in results:
            rid = r["id"]
            if rid not in seen_ids:
                seen_ids.add(rid)
                merged.append(r)

    # Sort by score descending and truncate to fetch_k
    merged.sort(key=lambda r: r.get("score", 0), reverse=True)
    merged = merged[:fetch_k]
    logger.info(f"[Multi-Query] Merged: {len(seen_ids)} unique results, returning {len(merged)}")
    return merged


async def _retrieve_step_back(
    plugin, query, rewrite_llm, collection_id, embedding_model_uuid,
    fetch_k, filters, search_type,
) -> list[dict]:
    """Step-Back: generate a broader question, search with both original and abstract queries."""
    logger.info(f"[Step-Back] Generating abstract question for: {query!r}")
    prompt = STEP_BACK_PROMPT.format(query=query)
    resp = await plugin.invoke_llm(rewrite_llm, [Message(role="user", content=prompt)])
    abstract_query = _extract_text(resp)
    logger.info(f"[Step-Back] Abstract query: {abstract_query!r}")

    # Embed both original and abstract queries
    logger.info("[Step-Back] Embedding original + abstract queries and searching...")
    both_vectors = await plugin.invoke_embedding(
        embedding_model_uuid, [query, abstract_query],
    )

    # Search with both vectors and merge
    seen_ids: set[str] = set()
    merged: list[dict] = []
    for i, vec in enumerate(both_vectors):
        label = "original" if i == 0 else "abstract"
        results = await plugin.vector_search(
            collection_id=collection_id,
            query_vector=vec,
            top_k=fetch_k,
            filters=filters,
            search_type=search_type,
            query_text=query,
        )
        new_count = sum(1 for r in results if r["id"] not in seen_ids)
        logger.info(f"[Step-Back] {label} query returned {len(results)} results ({new_count} new)")
        for r in results:
            rid = r["id"]
            if rid not in seen_ids:
                seen_ids.add(rid)
                merged.append(r)

    merged.sort(key=lambda r: r.get("score", 0), reverse=True)
    merged = merged[:fetch_k]
    logger.info(f"[Step-Back] Merged: {len(seen_ids)} unique results, returning {len(merged)}")
    return merged
