<p align="center">
  <img src="assets/icon.svg" alt="LangTARS" width="128">
</p>

<p align="center">
  <strong>LangTARS</strong> — LangBot 原生插件
</p>

<p align="center">
  <a href="../README.md">English</a>&nbsp; • &nbsp;
  <a href="README_zh_Hant.md">繁體中文</a>&nbsp; • &nbsp;
  <a href="README_ja_JP.md">日本語</a>&nbsp; • &nbsp;
  <a href="https://github.com/langbot-app/LangTARS">GitHub</a>
</p>

> ⚠️ **注意**：功能仍在积极开发中，如遇 bug 请提交 [issue](https://github.com/langbot-app/LangTARS/issues)。
> 目前使用此插件，会遇到很多问题，比如stop命令有时会无法执行，请手动关闭插件再重启，后续 LangBot 官方插件SDK更新后，LangTARS会继续更新相关的命令和功能。

---

## 什么是 LangTARS？

LangTARS 是借鉴 **Nanobot** 的 ReAct 理念开发的 **LangBot 原生插件**，旨在为 LangBot 用户带来 **OpenClaw** 般的体验。它使您能够通过 IM 消息使用自主 AI 任务规划来控制您的 Mac。如同《星际穿越》中的 **塔斯(TARS)** 一样，为您忠诚工作。

与 [OpenClaw](https://github.com/openclaw/openclaw) 类似，LangTARS 允许 AI 助手在您的 Mac 上执行真实操作——但具有 LangBot 插件的简洁与优雅。

## 为什么选择 LangTARS？

[OpenClaw](https://github.com/openclaw/openclaw) 是一个具有远见卓识的出色项目。然而，运行如此复杂的软件并赋予其访问您数字生活的权限，需要您信任可能不完全理解的系统。

LangTARS 采用不同的方式：
- **原生 LangBot 集成** — 使用 Nanobot 内核直接在 LangBot 内运行
- **轻量级** — 最少的代码库，您可以直接理解和审计
- **自主规划** — 使用 ReAct 循环实现智能任务执行
- **安全优先** — 内置命令限制、工作区隔离和危险命令拦截

## 快速开始

1. 通过 LangBot 的插件系统安装 LangTARS
2. 配置您偏好的 LLM 模型用于任务规划
3. 开始通过 IM 消息控制您的 Mac！

## 首次设置 - Mac 权限

首次使用前，需要授予一些权限：

### AppleScript  automation 权限
- 打开 **系统偏好设置** > **隐私与安全性** > **辅助功能**
- 点击左下角 🔒 解锁
- 添加 **Terminal** 或你的聊天应用 (如 WeChat, Telegram 等)

### Safari JavaScript 权限 (可选)
- 打开 **Safari** > **设置** > **高级**
- 勾选 **允许 Apple Events 中的 JavaScript**

## 主要命令

### `!tars auto` — 自主任务规划

这是使 LangTARS 与众不同的**主要命令**。只需描述您想要做的事情，AI 就会自主规划并使用可用工具执行任务。

- `!tars auto 打开 Safari，访问 langbot.app,抓取元素并且告诉我`
- `!tars auto 新建一个备忘录，标题和内容为你好`
- `!tars auto 帮我整理桌面上的文件`
- <code><del>!tars auto 给我炒俩菜。</del></code>

### 浏览器控制

LangTARS 支持三种浏览器控制方式：

| 命令示例 | 浏览器 | 说明 |
|----------|--------|------|
| `!tars auto 访问 github.com` | Playwright (Chromium) | 默认方式，无需额外权限 |
| `!tars auto 打开 Safari 并访问 github` | Safari 浏览器 | 使用真实 Safari，需要 AppleScript 权限 |
| `!tars auto 打开 Chrome 并访问 github` | Chrome 浏览器 | 使用真实 Chrome，需要 AppleScript 权限 |

AI 将：
1. 理解您的请求
2. 规划必要的步骤
3. 使用 shell 命令、文件操作、应用控制等逐一执行
4. 返回结果

您可以随时**停止**正在运行的任务：
```
!tars stop
```

查看任务状态：
```
!tars status
```

## 测试命令

这些命令可用于测试和直接控制：

| 命令 | 描述 |
|------|------|
| `!tars shell <command>` | 执行 shell 命令 |
| `!tars ps [filter]` | 列出运行中的进程 |
| `!tars kill <pid\|name>` | 终止进程 |
| `!tars ls [path]` | 列出目录内容 |
| `!tars cat <path>` | 读取文件内容 |
| `!tars open <app\|url>` | 打开应用程序或 URL |
| `!tars close <app>` | 关闭应用程序 |
| `!tars apps [limit]` | 列出运行中的应用程序 |
| `!tars info` | 显示系统信息 |

## 配置

通过 LangBot 的设置配置 LangTARS：

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `allowed_users` | 允许控制此 Mac 的用户 ID | [] |
| `command_whitelist` | 允许的 shell 命令（留空 = 在限制下允许所有） | [] |
| `workspace_path` | 文件操作的工作区目录 | ~/.langtars |
| `enable_shell` | 启用 shell 命令执行 | true |
| `enable_process` | 启用进程管理 | true |
| `enable_file` | 启用文件操作 | true |
| `enable_app` | 启用应用控制 | true |
| `planner_max_iterations` | 最大 ReAct 循环迭代次数 | 5 |
| `planner_model_uuid` | 用于任务规划的 LLM 模型 | （第一个可用） |
| `planner_rate_limit_seconds` | LLM 调用之间的速率限制 | 1 |
| `planner_auto_load_mcp` | 自动加载 MCP 工具 | true |

## 安全特性

- **危险命令拦截** — 默认阻止 `rm -rf /` 等命令
- **工作区隔离** — 文件操作限制在配置的工作区
- **命令白名单** — 可选择限制为特定命令
- **用户访问控制** — 可选择限制为特定用户

## 架构

```
IM 消息 --> LangBot --> PlannerTool (ReAct 循环) --> 工具 --> Mac 操作
```

- **PlannerTool** — 使用 LLM 进行自主任务规划的 ReAct 循环
- **工具注册表** — 从 MCP 服务器和插件动态加载工具
- **内置工具** — Shell、进程、文件、应用控制

## 许可证

MIT
