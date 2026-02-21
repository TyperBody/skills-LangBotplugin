# DifyDatasetsRetriever

Dify APIを使用してDifyナレッジベースから知識を取得します。

## 設定

LangBotで外部ナレッジベースを追加し、ナレッジリトリーバータイプとして「DifyDatasetsRetriever」を選択してください。

### 必須パラメータ

- **api_base_url**：Dify APIのベースURL
  - Dify Cloudの場合：`https://api.dify.ai/v1`（デフォルト）
  - セルフホストインスタンスの場合：サーバーのURL（例：`http://localhost/api` または `https://your-domain.com/api`）
- **dify_apikey**：DifyインスタンスのAPIキー
- **dataset_id**：Difyナレッジベース/データセットのID

### オプションパラメータ

- **top_k**（デフォルト：5）：取得する結果の最大数
- **score_threshold**（デフォルト：0.5）：最小関連度スコア（0-1）
- **search_method**（デフォルト：hybrid_search）：使用する検索方法
  - `hybrid_search`：ハイブリッド検索（デフォルト）
  - `keyword_search`：キーワードベースの検索
  - `semantic_search`：セマンティック類似度検索
  - `full_text_search`：全文検索

## 設定値の取得方法

### Dify APIキーの取得

1. https://cloud.dify.ai/ にアクセス
2. ナレッジベースページに移動
3. 左サイドバーの「API ACCESS」をクリック
4. 「API Keys」セクションからAPIキーを作成またはコピー

### データセットIDの取得

1. Difyナレッジベース一覧でナレッジベースをクリック
2. データセットIDはURLに含まれています：`https://cloud.dify.ai/datasets/{dataset_id}`
3. またはナレッジベースのAPIドキュメントページで確認できます

## APIリファレンス

このプラグインはDify Dataset Retrieval APIを使用します：
- エンドポイント：`POST https://api.dify.ai/v1/datasets/{dataset_id}/retrieve`
- ドキュメント：https://docs.dify.ai/
