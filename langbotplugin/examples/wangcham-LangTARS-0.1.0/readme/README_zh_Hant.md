<p align="center">
  <img src="assets/icon.svg" alt="LangTARS" width="128">
</p>

<p align="center">
  <strong>LangTARS</strong> — LangBot 原生插件
</p>

<p align="center">
  <a href="../README.md">English</a>&nbsp; • &nbsp;
  <a href="README_zh_Hans.md">简体中文</a>&nbsp; • &nbsp;
  <a href="README_ja_JP.md">日本語</a>&nbsp; • &nbsp;
  <a href="https://github.com/langbot-app/LangTARS">GitHub</a>
</p>

> ⚠️ **注意**：功能仍在積極開發中。如遇任何問題，請提交 [issue](https://github.com/langbot-app/LangTARS/issues)。
> 目前使用此插件，會遇到很多問題，比如 stop 命令有時會無法執行，請手動關閉插件再重啟，後續 LangBot 官方插件 SDK 更新後，LangTARS 會繼續更新相關的命令和功能。

---

## 什麼是 LangTARS？

LangTARS 是借鑒 **Nanobot** 的 ReAct 理念開發的 **LangBot 原生插件**，旨在為 LangBot 用戶帶來 **OpenClaw** 般的體驗。它使您能夠透過 IM 訊息使用自主 AI 任務規劃來控制您的 Mac。如同《星際穿越》中的 **塔斯(TARS)** 一樣，為您忠誠工作。

與 [OpenClaw](https://github.com/openclaw/openclaw) 類似，LangTARS 允許 AI 助手在您的 Mac 上執行真實操作——但具有 LangBot 插件的簡潔與優雅。

## 為什麼選擇 LangTARS？

[OpenClaw](https://github.com/openclaw/openclaw) 是一個具有遠見卓識的出色專案。然而，執行如此複雜的軟體並賦予其訪問您數位生活的權限，需要您信任可能不完全理解的系統。

LangTARS 採用不同的方式：
- **原生 LangBot 整合** — 使用 Nanobot 核心直接在 LangBot 內執行
- **輕量級** — 最少的程式碼庫，您可以直接理解和審計
- **自主規劃** — 使用 ReAct 循環實現智慧任務執行
- **安全優先** — 內建命令限制、工作區隔離和危險命令攔截

## 快速開始

1. 透過 LangBot 的插件系統安裝 LangTARS
2. 設定您偏好的 LLM 模型用於任務規劃
3. 開始透過 IM 訊息控制您的 Mac！

## 首次設定 - Mac 權限

首次使用前，需要授予一些權限：

### AppleScript automation 權限
- 開啟 **系統偏好設定** > **隱私與安全性** > **輔助功能**
- 點擊左下角 🔒 解鎖
- 新增 **Terminal** 或您的聊天應用 (如 WeChat, Telegram 等)

### Safari JavaScript 權限 (可選)
- 開啟 **Safari** > **設定** > **進階**
- 勾選 **允許 Apple Events 中的 JavaScript**

## 主要命令

### `!tars auto` — 自主任務規劃

這是使 LangTARS 與眾不同的**主要命令**。只需描述您想要做的事情，AI 就會自主規劃並使用可用工具執行任務。

- `!tars auto 打開 Safari，訪問 langbot.app, 擷取元素並告訴我`
- `!tars auto 新建一個備忘錄，標題和內容為你好`
- `!tars auto 幫我整理桌面上的檔案`
- <code><del>!tars auto 給我炒倆菜。</del></code>

### 瀏覽器控制

LangTARS 支援三種瀏覽器控制方式：

| 命令範例 | 瀏覽器 | 說明 |
|----------|--------|------|
| `!tars auto 訪問 github.com` | Playwright (Chromium) | 預設方式，無需額外權限 |
| `!tars auto 開啟 Safari 並訪問 github` | Safari 瀏覽器 | 使用真實 Safari，需要 AppleScript 權限 |
| `!tars auto 開啟 Chrome 並訪問 github` | Chrome 瀏覽器 | 使用真實 Chrome，需要 AppleScript 權限 |

AI 將：
1. 理解您的請求
2. 規劃必要的步驟
3. 使用 shell 命令、檔案操作、應用控制等逐一執行
4. 傳回結果

您可以隨時**停止**正在執行的任務：
```
!tars stop
```

查看任務狀態：
```
!tars status
```

## 測試命令

這些命令可用於測試和直接控制：

| 命令 | 描述 |
|------|------|
| `!tars auto <task>` | 自主任務規劃 (AI驅動) |
| `!tars shell <command>` | 執行 shell 命令 |
| `!tars ps [filter]` | 列出執行中的程序 |
| `!tars kill <pid\|name>` | 終止程序 |
| `!tars ls [path]` | 列出目錄內容 |
| `!tars cat <path>` | 讀取檔案內容 |
| `!tars write <path> <content>` | 寫入檔案內容 |
| `!tars open <app\|url>` | 開啟應用程式或 URL |
| `!tars close <app>` | 關閉應用程式 |
| `!tars apps [limit]` | 列出執行中的應用程式 |
| `!tars info` | 顯示系統資訊 |
| `!tars search <pattern>` | 搜尋檔案 |

## 設定

透過 LangBot 的設定配置 LangTARS：

| 選項 | 描述 | 預設值 |
|------|------|--------|
| `allowed_users` | 允許控制此 Mac 的使用者 ID | [] |
| `command_whitelist` | 允許的 shell 命令（留空 = 在限制下允許所有） | [] |
| `workspace_path` | 檔案操作的工作區目錄 | ~/.langtars |
| `enable_shell` | 啟用 shell 命令執行 | true |
| `enable_process` | 啟用程序管理 | true |
| `enable_file` | 啟用檔案操作 | true |
| `enable_app` | 啟用應用控制 | true |
| `planner_max_iterations` | 最大 ReAct 循環迭代次數 | 5 |
| `planner_model_uuid` | 用於任務規劃的 LLM 模型 | （第一個可用） |
| `planner_rate_limit_seconds` | LLM 呼叫之間的速率限制 | 1 |
| `planner_auto_load_mcp` | 自動載入 MCP 工具 | true |

## 安全特性

- **危險命令攔截** — 預設阻止 `rm -rf /` 等命令
- **工作區隔離** — 檔案操作限制在設定的工作區
- **命令白名單** — 可選擇限制為特定命令
- **使用者存取控制** — 可選擇限制為特定使用者

## 架構

```
IM 訊息 --> LangBot --> PlannerTool (ReAct 循環) --> 工具 --> Mac 操作
```

- **PlannerTool** — 使用 LLM 進行自主任務規劃的 ReAct 循環
- **工具註冊表** — 從 MCP 伺服器和插件動態載入工具
- **內建工具** — Shell、程序、檔案、應用控制

## 授權

MIT
