<p align="center">
  <img src="assets/icon.svg" alt="LangTARS" width="128">
</p>

<p align="center">
  <strong>LangTARS</strong> — LangBot ネイティブプラグイン
</p>

<p align="center">
  <a href="../README.md">English</a>&nbsp; • &nbsp;
  <a href="README_zh_Hans.md">简体中文</a>&nbsp; • &nbsp;
  <a href="README_zh_Hant.md">繁體中文</a>&nbsp; • &nbsp;
  <a href="https://github.com/langbot-app/LangTARS">GitHub</a>
</p>

> ⚠️ **注意**: 機能は現在も開発中です。バグを発見した場合は、[issue](https://github.com/langbot-app/LangTARS/issues) を報告してください。
> 現在このプラグインを使用すると、多くの問題が発生します。例えば、stop コマンドが実行できない場合があります。プラグインを手動で閉じて再起動してください。LangBot 公式プラグイン SDK が更新された後、LangTARS は関連するコマンドと機能を更新し続けます。

---

## LangTARS とは？

LangTARS は **Nanobot** の ReAct コンセプトを元に開発された **LangBot ネイティブプラグイン**で、LangBot ユーザーに **OpenClaw** のような体験を提供します。IM メッセージを通じて自律的な AI タスクプランニングで Mac を制御できます。《インターステラー》の **タース(TARS)** のように忠実にサービスを提供します。

[OpenClaw](https://github.com/openclaw/openclaw) と同様に、LangTARS は AI アシスタントが Mac で実際の操作を実行できますが、LangBot プラグインの洗練さと洗練さを備えています。

## なぜ LangTARS なのか？

[OpenClaw](https://github.com/openclaw/openclaw) は優れた先見的なプロジェクトです。しかし、そのような複雑なソフトウェアを実行し、デジタルライフへのアクセスを許可するには、十分に理解していないシステムを信頼する必要があります。

LangTARS は異なるアプローチを取ります：
- **ネイティブ LangBot 統合** — Nanobot カーネルを使用して LangBot 内で直接実行
- **軽量** — 最小のコードベースで、理解し監査的可能
- **自律プランニング** — ReAct ループによるインテリジェントなタスク実行
- **セキュリティ第一** — 組み込みのコマンド制限、ワークスペース分離、危険なコマンド遮断

## クイックスタート

1. LangBot のプラグインシステムから LangTARS をインストール
2. タスクプランニング用に好みの LLM モデルを構成
3. IM メッセージで Mac の制御を開始！

## 初回セットアップ - Mac 権限

初めて使用する前に、いくつかの権限を付与する必要があります：

### AppleScript  automation 権限
- **システム設定** > **プライバシーとセキュリティ** > **アクセシビリティ** を開く
- 左下の 🔒 をクリックしてロックを解除
- **ターミナル** やチャットアプリ（WeChat、Telegram など）を追加

### Safari JavaScript 権限（オプション）
- **Safari** > **設定** > **詳細** を開く
- **Apple Events からの JavaScript を許可** にチェックを入れる

## メインコマンド

### `!tars auto` — 自律タスクプランニング

これが LangTARS を他のツールと差別化する**メインコマンド**です。したいことを説明するだけで、AI が利用可能なツールを使って自律的にタスクをプランニングし実行します。

- `!tars auto Safariを開いて、langbot.appにアクセスして、要素を取得して教えて`
- `!tars auto 新規メモを作成して、タイトルと内容を「こんにちは」にして`
- `!tars auto デスクトップのファイルを整理して`
- <code><del>!tars auto 料理を作ってください。</del></code>

### ブラウザ制御

LangTARS は3つのブラウザ制御方法をサポートしています：

| コマンド例 | ブラウザ | 説明 |
|----------|---------|------|
| `!tars auto github.com にアクセス` | Playwright (Chromium) | デフォルト、追加権限不要 |
| `!tars auto Safari を開いて github に行く` | Safari ブラウザ | 実際の Safari を使用、AppleScript 権限が必要 |
| `!tars auto Chrome を開いて github に行く` | Chrome ブラウザ | 実際の Chrome を使用、AppleScript 権限が必要 |

AI は以下を行います：
1. リクエストを理解する
2. 必要なステップをプランニングする
3. シェルコマンド、ファイル操作、アプリ制御などを使って一つずつ実行する
4. 結果を返す

実行中のタスクはいつでも**停止**できます：
```
!tars stop
```

タスクの状態を確認：
```
!tars status
```

## テストコマンド

これらはテストや直接制御に使用できます：

| コマンド | 説明 |
|---------|------|
| `!tars auto <task>` | 自律タスクプランニング (AI駆動) |
| `!tars shell <command>` | シェルコマンドを実行 |
| `!tars ps [filter]` | 実行中のプロセスを一覧表示 |
| `!tars kill <pid\|name>` | プロセスを終了 |
| `!tars ls [path]` | ディレクトリの内容を表示 |
| `!tars cat <path>` | ファイルの内容を読み取る |
| `!tars write <path> <content>` | ファイルに書き込む |
| `!tars open <app\|url>` | アプリや URL を開く |
| `!tars close <app>` | アプリを閉じる |
| `!tars apps [limit]` | 実行中のアプリを一覧表示 |
| `!tars info` | システム情報を表示 |
| `!tars search <pattern>` | ファイルを検索 |

## 設定

LangBot の設定で LangTARS を構成：

| オプション | 説明 | デフォルト |
|-----------|------|------------|
| `allowed_users` | この Mac を制御できるユーザー ID | [] |
| `command_whitelist` | 許可するシェルコマンド（空 = 制限付きで全て許可） | [] |
| `workspace_path` | ファイル操作用のワークスペースディレクトリ | ~/.langtars |
| `enable_shell` | シェルコマンド実行を有効化 | true |
| `enable_process` | プロセス管理を有効化 | true |
| `enable_file` | ファイル操作を有効化 | true |
| `enable_app` | アプリ制御を有効化 | true |
| `planner_max_iterations | 最大 ReAct ループ反復回数 | 5 |
| `planner_model_uuid` | タスクプランニング用の LLM モデル | （最初の利用可能なモデル） |
| `planner_rate_limit_seconds` | LLM 呼び出し間のレート制限 | 1 |
| `planner_auto_load_mcp` | MCP ツールを自動読み込み | true |

## セキュリティ機能

- **危険コマンド遮断** — `rm -rf /` などのコマンドをデフォルトでブロック
- **ワークスペース分離** — ファイル操作を設定されたワークスペースに制限
- **コマンドホワイトリスト** — 特定のコマンドに制限可能
- **ユーザーアクセス制御** — 特定のユーザーに制限可能

## アーキテクチャ

```
IM メッセージ --> LangBot --> PlannerTool (ReAct ループ) --> ツール --> Mac 操作
```

- **PlannerTool** — LLM を使用した自律タスクプランニングの ReAct ループ
- **ツールレジストリ** — MCP サーバーとプラグインからツールを動的に読み込み
- **組み込みツール** — シェル、プロセス、ファイル、アプリ制御

## ライセンス

MIT
