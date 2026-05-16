## 安装 CLI

请确保您已安装 Python 3.10 或更高版本，并已安装 [uv 包管理器](https://docs.astral.sh/uv/)。

在任意空目录执行命令，安装 LangBot CLI 和 SDK

```bash
pip install -U langbot_plugin
```

## 初始化插件目录

假设您的插件名称为 `HelloPlugin`，则在任意目录下创建目录`HelloPlugin`，并进入该目录，执行命令初始化插件：

```bash
lbp init
```

按照提示输入`Author(作者)`、`Description(描述)`等信息

## 插件结构

插件根据具体功能可提供以下组件：

- 事件监听器（EventListener）：监听流水线执行期间的事件，对上下文或流水线进行修改。
- 命令（Command）：由用户通过`!`（或其他已设置的前缀）开头的命令消息触发。
- 工具（Tool）：供 LangBot 内置的 Local Agent 在执行期间由 LLM 调用。
- 知识引擎（Knowledge Engine）：为 LangBot 提供外部知识库检索能力，支持接入各类 RAG 系统。
- 解析器（Parser）：用于解析和处理消息内容。
- 页面（Page）：为插件提供 Web 管理界面，运行在 LangBot WebUI 的侧边栏中。

# 添加组件

插件由一种或多种组件构成，为 LangBot 提供不同的功能。目前支持的组件类型有：

- 事件监听器（EventListener）：监听流水线执行期间的事件，对上下文或流水线进行修改。
- 命令（Command）：由用户通过`!`（或其他已设置的前缀）开头的命令消息触发。
- 工具（Tool）：供 LangBot 内置的 Local Agent 在执行期间由 LLM 调用。
- 知识引擎（Knowledge Engine）：为 LangBot 提供外部知识库检索能力，支持接入各类 RAG 系统。
- 解析器（Parser）：用于解析和处理消息内容。
- 页面（Page）：为插件提供 Web 管理界面，运行在 LangBot WebUI 的侧边栏中。

## 添加组件

在插件目录下执行命令：

```bash
lbp comp <component_type>
```

例如，添加一个事件监听器：

```bash
lbp comp EventListener
```

请根据提示输入组件的配置（若有）。

```bash
➜  HelloPlugin > lbp comp EventListener
Generating component EventListener...
Component EventListener generated successfully.
组件 EventListener 生成成功。
➜  HelloPlugin >
```

:::info
CLI 将在插件目录下生成一个 `components` 目录，并在其中创建组件对应目录

```
.
├── assets
│   └── icon.svg
├── components
│   ├── __init__.py
│   └── event_listener
│       ├── __init__.py
│       ├── default.py
│       └── default.yaml
├── main.py
├── manifest.yaml
├── README.md
└── requirements.txt
```

同时，会在插件的`manifest.yaml`中添加组件发现配置：

```yaml
...
components:
    EventListener:
      fromDirs:
      - path: components/event_listener/
...
```
如需删除组件，可自行删除对应信息。
:::


## Page 组件（Web 界面）

Page 组件用于为插件提供 Web 管理界面，运行在 LangBot WebUI 的侧边栏中。

### 创建 Page 组件

在插件目录下执行命令：

```bash
lbp comp Page
```

按照提示输入页面配置（名称、标签等）。

### Page 组件结构

Page 组件由以下文件构成：

```
components/pages/
└── dashboard/
    ├── dashboard.yaml    # 页面配置
    ├── dashboard.py      # 页面后端逻辑
    ├── index.html        # 页面前端
    └── i18n/             # 国际化文件
        ├── zh_Hans.json
        └── en_US.json
```

### dashboard.yaml 配置示例

```yaml
apiVersion: v1
kind: Page
metadata:
  name: dashboard
  label:
    en_US: Dashboard
    zh_Hans: 仪表盘
spec:
  path: index.html
execution:
  python:
    path: dashboard.py
    attr: DashboardPage
```

### dashboard.py 后端示例

```python
from langbot_plugin.api.definition.components.page import Page, PageRequest, PageResponse

class DashboardPage(Page):
    """仪表盘页面"""
    
    async def handle_api(self, request: PageRequest) -> PageResponse:
        if request.endpoint == '/stats':
            # 处理 API 请求
            return PageResponse.ok({
                'total_entries': 100,
                'avg_answer_length': 50,
            })
        
        return PageResponse.fail(f'Unknown endpoint: {request.method} {request.endpoint}')
```

### index.html 前端示例

```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <title>仪表盘</title>
  <style>
    body {
      background: var(--langbot-bg, #ffffff);
      color: var(--langbot-text, #0a0a0a);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      padding: 24px;
    }
  </style>
</head>
<body>
  <h1 data-i18n="title">仪表盘</h1>
  <div id="content">加载中...</div>

  <!-- 引入 page-sdk.js -->
  <script src="/api/v1/plugins/_sdk/page-sdk.js"></script>
  <script>
    langbot.onReady(async function(ctx) {
      // 页面就绪后执行
      const stats = await langbot.api('/stats', null, 'GET');
      document.getElementById('content').textContent = JSON.stringify(stats);
    });
  </script>
</body>
</html>
```

### page-sdk.js API

page-sdk.js 提供了前端与 LangBot 后端通信的 API：

| 方法 | 说明 |
|------|------|
| `langbot.onReady(callback)` | 页面就绪时执行回调 |
| `langbot.api(endpoint, data, method)` | 调用后端 API |
| `langbot.t(key, fallback)` | 国际化翻译 |
| `langbot.theme` | 当前主题信息 |
| `langbot.language` | 当前语言 |

### CSP 和 iframe 注意事项

Page 组件运行在 sandboxed iframe 中，需要注意：

1. **CSP 策略**：页面只能加载同源脚本和 `/api` 路径下的脚本（如 page-sdk.js）
2. **iframe sandbox**：默认包含 `allow-scripts`、`allow-forms` 和 `allow-modals`，允许使用 `prompt()` 和 `confirm()`
3. **样式变量**：使用 `--langbot-bg`、`--langbot-text`、`--langbot-accent` 等 CSS 变量以适配主题

### manifest.yaml 中的 Page 配置

```yaml
components:
  Page:
    fromDirs:
      - path: components/pages/
        maxDepth: 2
```

## 组件类型

各个组件的详细使用方式请参考：

- [EventListener](./event-listener.mdx)
- [Command](./command.mdx)
- [Tool](./tool.mdx)
- [KnowledgeRetriever](./knowledge-retriever.mdx)
- [Parser](./parser.mdx)
- [Page](./page.mdx)

## 启动调试

您需要先部署并启动 LangBot，确保 Plugin Runtime 正在运行并监听 `5401` 端口。

::: info
Runtime 有两种启动方式：

- `Stdio` 模式：当您使用源代码启动 LangBot 并未携带启动参数`--standalone-runtime`时，LangBot 会自动以子进程的形式启动 Plugin Runtime，并通过 `stdio`（标准输入输出流）模式与 Plugin Runtime 通信。此时 Runtime 会加载 LangBot 根目录的`data/plugins`目录下的插件。并监听 LangBot 运行主机的`5401`端口作为调试端口。

- `WebSocket` 模式：
    - 生产环境：当您使用官方提供的`docker-compose.yaml`启动 LangBot 时，会在独立的容器运行 Plugin Runtime，LangBot 也会因为携带启动参数`--standalone-runtime`而以 WebSocket 模式与 Plugin Runtime 通信。默认情况下，Runtime 容器的 5401 端口会被映射到宿主机的 5401 端口。
    - 开发环境：若您通过源代码启动 LangBot，并携带启动参数`--standalone-runtime`，LangBot 按照`data/config.yaml`中配置的`plugin.runtime_ws_url`地址（端口通常是5400）连接到已启动的 Plugin Runtime。您需要自行启动独立运行的 Plugin Runtime，见[开发 Plugin Runtime](/zh/develop/plugin-runtime)。

无论是`stdio`或`websocket`模式，Plugin Runtime 都会监听其所在的主机的`5401`端口作为调试端口供插件调试时连接。

当您在开发插件时，推荐您按照[开发配置](/zh/develop/dev-config)中的方式 LangBot，此方式将以 Stdio 形式启动 Plugin Runtime，便于插件开发。
:::

复制插件目录下的`.env.example`文件为`.env`，检查或修改`DEBUG_RUNTIME_WS_URL`为您的 Plugin Runtime 的 WebSocket 地址。

```bash
cp .env.example .env
```

启动插件调试，您将看到插件的输出：

```bash
lbp run
```

并可以在 LangBot 的 WebUI 中看到此插件已被加载。
