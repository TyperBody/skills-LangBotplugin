# RAGFlowRetriever

Retrieve knowledge from RAGFlow knowledge bases using the RAGFlow API.

## About RAGFlow

RAGFlow is an open-source RAG (Retrieval-Augmented Generation) engine based on deep document understanding. It provides truthful question-answering capabilities with well-founded citations from various complex formatted data.

## Features

- Retrieve knowledge chunks from RAGFlow datasets/knowledge bases
- Support for multiple datasets in a single query
- Configurable similarity thresholds and vector weights
- Hybrid search combining keyword and vector similarity
- Returns results with rich metadata including term and vector similarity scores

## Configuration

This plugin requires the following configuration parameters:

### Required Parameters

- **api_base_url**: Base URL for RAGFlow API
  - For local deployment: `http://localhost:9380` (default)
  - For remote server: Your server URL (e.g., `http://your-domain.com:9380`)
- **api_key**: Your RAGFlow API key from your RAGFlow instance
- **dataset_ids**: Comma-separated dataset IDs to search
  - Format: `"dataset_id1,dataset_id2,dataset_id3"`
  - Example: `"b2a62730759d11ef987d0242ac120004,a3b52830859d11ef887d0242ac120005"`

### Optional Parameters

- **top_k** (default: 1024): Maximum number of retrieved results
- **similarity_threshold** (default: 0.2): Minimum similarity score (0-1)
- **vector_similarity_weight** (default: 0.3): Weight for vector similarity in hybrid search (0-1)
- **page_size** (default: 30): Number of results per page

## How to Get Configuration Values

### Getting your RAGFlow API Key

1. Access your RAGFlow instance (e.g., `http://localhost:9380`)
2. Navigate to the settings or API section
3. Generate or copy your API key

### Getting your Dataset IDs

1. In RAGFlow, go to your knowledge base/dataset list
2. Click on a dataset to view its details
3. The dataset ID is typically shown in the URL or dataset details
4. For multiple datasets, collect all IDs and join them with commas

## API Reference

This plugin uses the RAGFlow Retrieval API:
- Endpoint: `POST /api/v1/retrieval`
- Documentation: https://ragflow.io/docs/dev/http_api_reference

## Retrieval Method

RAGFlow employs a hybrid retrieval approach:
- **Keyword Similarity**: Traditional keyword-based matching
- **Vector Similarity**: Semantic similarity using embeddings
- **Weighted Combination**: Combines both methods with configurable weights

The `vector_similarity_weight` parameter controls the balance between these two methods.
