# DifyDatasetsRetriever

使用 Dify API 从 Dify 知识库中检索知识。

## 配置

请在 LangBot 中添加外部知识库，并选择"DifyDatasetsRetriever"作为知识检索器类型。

### 必填参数

- **api_base_url**：Dify API 的基础 URL
  - Dify Cloud：`https://api.dify.ai/v1`（默认）
  - 自托管实例：您的服务器 URL（例如 `http://localhost/api` 或 `https://your-domain.com/api`）
- **dify_apikey**：您的 Dify 实例的 API 密钥
- **dataset_id**：您的 Dify 知识库/数据集的 ID

### 可选参数

- **top_k**（默认：5）：返回的最大检索结果数量
- **score_threshold**（默认：0.5）：最低相关度分数（0-1）
- **search_method**（默认：hybrid_search）：使用的搜索方法
  - `hybrid_search`：混合搜索（默认）
  - `keyword_search`：基于关键词的搜索
  - `semantic_search`：语义相似度搜索
  - `full_text_search`：全文搜索

## 如何获取配置值

### 获取您的 Dify API 密钥

1. 访问 https://cloud.dify.ai/
2. 导航到您的知识库页面
3. 点击左侧边栏中的"API ACCESS"
4. 从"API Keys"部分创建或复制您的 API 密钥

### 获取您的数据集 ID

1. 在 Dify 知识库列表中，点击您的知识库
2. 数据集 ID 在 URL 中：`https://cloud.dify.ai/datasets/{dataset_id}`
3. 或者您可以在知识库的 API 文档页面中找到它

## API 参考

本插件使用 Dify 数据集检索 API：
- 端点：`POST https://api.dify.ai/v1/datasets/{dataset_id}/retrieve`
- 文档：https://docs.dify.ai/
