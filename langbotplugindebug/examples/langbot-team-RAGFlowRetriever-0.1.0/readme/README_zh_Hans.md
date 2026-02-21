# RAGFlowRetriever

使用 RAGFlow API 从 RAGFlow 知识库中检索知识。

## 关于 RAGFlow

RAGFlow 是一个基于深度文档理解的开源 RAG（检索增强生成）引擎。它提供真实的问答能力，并从各种复杂格式的数据中提供有据可查的引用。

## 功能特性

- 从 RAGFlow 数据集/知识库中检索知识块
- 单次查询支持多个数据集
- 可配置的相似度阈值和向量权重
- 结合关键词和向量相似度的混合搜索
- 返回包含术语和向量相似度分数的丰富元数据结果

## 配置

本插件需要以下配置参数：

### 必填参数

- **api_base_url**：RAGFlow API 的基础 URL
  - 本地部署：`http://localhost:9380`（默认）
  - 远程服务器：您的服务器 URL（例如 `http://your-domain.com:9380`）
- **api_key**：您的 RAGFlow 实例的 API 密钥
- **dataset_ids**：要搜索的数据集 ID，用逗号分隔
  - 格式：`"dataset_id1,dataset_id2,dataset_id3"`
  - 示例：`"b2a62730759d11ef987d0242ac120004,a3b52830859d11ef887d0242ac120005"`

### 可选参数

- **top_k**（默认：1024）：返回的最大检索结果数量
- **similarity_threshold**（默认：0.2）：最低相似度分数（0-1）
- **vector_similarity_weight**（默认：0.3）：混合搜索中向量相似度的权重（0-1）
- **page_size**（默认：30）：每页结果数量

## 如何获取配置值

### 获取您的 RAGFlow API 密钥

1. 访问您的 RAGFlow 实例（例如 `http://localhost:9380`）
2. 导航到设置或 API 部分
3. 生成或复制您的 API 密钥

### 获取您的数据集 ID

1. 在 RAGFlow 中，进入您的知识库/数据集列表
2. 点击数据集查看其详细信息
3. 数据集 ID 通常显示在 URL 或数据集详情中
4. 对于多个数据集，收集所有 ID 并用逗号连接

## API 参考

本插件使用 RAGFlow 检索 API：
- 端点：`POST /api/v1/retrieval`
- 文档：https://ragflow.io/docs/dev/http_api_reference

## 检索方法

RAGFlow 采用混合检索方法：
- **关键词相似度**：传统的基于关键词的匹配
- **向量相似度**：使用嵌入的语义相似度
- **加权组合**：将两种方法结合，权重可配置

`vector_similarity_weight` 参数控制这两种方法之间的平衡。
