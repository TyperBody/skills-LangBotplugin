# LangRAG

Simple RAG (Retrieval-Augmented Generation) Engine demo plugin for LangBot.

This plugin demonstrates how to build a Knowledge Engine that handles document ingestion and vector retrieval using LangBot Host's built-in infrastructure (Embedding models and Vector Database).

## Features

- **Multi-format Document Parsing** - PDF, DOCX, Markdown, HTML, TXT
- **Configurable Chunking** - Sliding window with custom chunk size and overlap
- **Vector Retrieval** - Embed query -> vector similarity search -> Top-K results
- **Document Management** - Delete indexed vectors by document

## Architecture

```
┌─────────────────────────────────┐
│         LangBot Core            │
│  (Embedding / VDB / Storage)    │
└──────────┬──────────────────────┘
           │ RPC (IPC)
┌──────────▼──────────────────────┐
│      LangRAG            │
│  ┌───────────────────────────┐  │
│  │       LangKnowledge Engine      │  │
│  │  Parse → Chunk → Embed    │  │
│  │       → Store / Search    │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

## Configuration

### Knowledge Base Creation

| Parameter | Description | Default |
|-----------|-------------|---------|
| `embedding_model_uuid` | Embedding model | Required |
| `chunk_size` | Characters per chunk | 512 |
| `overlap` | Overlap between chunks | 50 |

### Retrieval

| Parameter | Description | Default |
|-----------|-------------|---------|
| `top_k` | Number of results to return | 5 |

## Development

```bash
pip install -r requirements.txt
cp .env.example .env
```

Configure `DEBUG_RUNTIME_WS_URL` and `PLUGIN_DEBUG_KEY` in `.env`, then launch with your IDE debugger.
