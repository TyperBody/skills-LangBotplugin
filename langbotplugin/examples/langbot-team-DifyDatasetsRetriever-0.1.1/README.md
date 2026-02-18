# DifyDatasetsRetriever

Retrieve knowledge from Dify knowledge bases using the Dify API.

## Configuration

Please add an external knowledge base in LangBot and select "DifyDatasetsRetriever" as the knowledge retriever type.

### Required Parameters

- **api_base_url**: Base URL for Dify API
  - For Dify Cloud: `https://api.dify.ai/v1` (default)
  - For self-hosted instances: Your server URL (e.g., `http://localhost/api` or `https://your-domain.com/api`)
- **dify_apikey**: Your Dify API key from your Dify instance
- **dataset_id**: The ID of your Dify knowledge base/dataset

### Optional Parameters

- **top_k** (default: 5): Maximum number of retrieved results
- **score_threshold** (default: 0.5): Minimum relevance score (0-1)
- **search_method** (default: hybrid_search): The search method to use
  - `hybrid_search`: Hybrid search (default)
  - `keyword_search`: Keyword-based search
  - `semantic_search`: Semantic similarity search
  - `full_text_search`: Full-text search

## How to Get Configuration Values

### Getting your Dify API Key

1. Go to https://cloud.dify.ai/
2. Navigate to your knowledge base page
3. Click on "API ACCESS" in the left sidebar
4. Create or copy your API key from the "API Keys" section

### Getting your Dataset ID

1. In the Dify knowledge base list, click on your knowledge base
2. The dataset ID is in the URL: `https://cloud.dify.ai/datasets/{dataset_id}`
3. Or you can find it in the API documentation page of your knowledge base

## API Reference

This plugin uses the Dify Dataset Retrieval API:
- Endpoint: `POST https://api.dify.ai/v1/datasets/{dataset_id}/retrieve`
- Documentation: https://docs.dify.ai/
