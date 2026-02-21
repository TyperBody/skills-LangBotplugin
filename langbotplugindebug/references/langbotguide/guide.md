## LangBot 插件开发指南文档分析

已完成对 `langbotplugin/references/langbotguide` 目录下所有文档的分析，以下是详细内容总结：

---

### 📁 目录结构

```
langbotguide/
├── compatibility.md          # 系统兼容性处理
├── plugin-intro.md           # 插件系统介绍
└── dev/                      # 开发文档
    ├── basic-info.md         # 配置信息
    ├── directory-structure.md # 目录规范
    ├── migration.md          # 迁移指南
    ├── style.md              # 代码规范
    ├── tutor.md              # 开发教程
    ├── apis/                 # API 文档
    │   ├── common.md         # 通用 API
    │   ├── messages.md       # 消息实体
    │   ├── pipeline-events.md # 流水线事件
    │   └── tech-details.md   # 技术细节
    ├── components/           # 组件文档
    │   ├── add.md            # 添加组件
    │   ├── command.md        # 命令组件
    │   ├── event-listener.md # 事件监听器
    │   ├── knowledge-retriever.md # 知识检索器
    │   └── tool.md           # 工具组件
    └── publish/              # 发布文档
        ├── github.md         # GitHub 发布
        └── market.md         # 插件市场发布
```

---

### 🔧 核心概念

#### 1. 插件架构 (4.0版本)
- **Plugin Runtime**: 插件运行时，管理插件生命周期
- **两种运行模式**: 
  - `stdio` 模式 - 个人用户/轻量级环境
  - `websocket` 模式 - 生产级/容器环境
- **Windows 兼容**: 自动采用 子进程 + WebSocket 通信方式

#### 2. 插件组件类型
| 组件类型 | 功能 |
|---------|------|
| **EventListener** | 监听流水线事件，修改上下文 |
| **Command** | 用户通过 `!` 前缀触发的命令 |
| **Tool** | LLM 调用的外部工具 |
| **KnowledgeRetriever** | 外部知识库检索能力 |

---

### 📋 插件目录结构

```
MyPlugin/
├── manifest.yaml          # 插件清单文件（必需）
├── main.py               # 插件主入口（必需）
├── README.md             # 英文说明（必需）
├── readme/               # 多语言 README
│   ├── README_zh_Hans.md
│   └── README_ja_JP.md
├── assets/               # 资源文件
│   └── icon.svg
├── components/           # 组件目录
│   ├── event_listener/
│   ├── commands/
│   ├── tools/
│   └── knowledge_retriever/
└── requirements.txt      # Python 依赖
```

---

### 🛠️ 开发流程

1. **安装 CLI**: `pip install -U langbot_plugin`
2. **初始化插件**: `lbp init`
3. **添加组件**: `lbp comp <组件类型>`
4. **调试运行**: `lbp run`
5. **打包发布**: `lbp build` / `lbp publish`

---

### 📝 manifest.yaml 配置项类型

| 类型 | 说明 |
|------|------|
| `string` | 字符串 |
| `array[string]` | 字符串数组 |
| `integer` | 整数 |
| `float` | 浮点数 |
| `boolean` | 布尔值 |
| `select` | 下拉选择框 |
| `text` | 大段文本 |
| `file` / `array[file]` | 文件上传 |
| `prompt-editor` | 提示词编辑器 |
| `llm-model-selector` | LLM 模型选择器 |
| `bot-selector` | Bot 选择器 |

---

### 🔌 通用 API 分类

#### 请求 API (EventListener/Command 可用)
- `reply()` - 直接回复消息
- `get_bot_uuid()` - 获取机器人 UUID
- `set_query_var()` / `get_query_var()` - 请求变量操作

#### LangBot API (所有组件可用)
- `get_config()` - 获取插件配置
- `send_message()` - 发送主动消息
- `invoke_llm()` - 调用 LLM 模型
- `set_plugin_storage()` / `get_plugin_storage()` - 插件持久化存储
- `set_workspace_storage()` / `get_workspace_storage()` - 工作空间存储

---

### 📨 消息链组件

```python
from langbot_plugin.api.entities.platform.message import *

msg_chain = MessageChain([
    Plain(text="Hello"),
    Image(url='https://...'),
    At(target=123456),
    AtAll(),
])
```

支持: `Source`, `Plain`, `Quote`, `Image`, `AtAll`, `At`, `Voice`, `Forward`, `File`

---

### 📡 可监听的流水线事件

| 事件 | 触发时机 |
|------|---------|
| `PersonMessageReceived` / `GroupMessageReceived` | 收到私聊/群聊任何消息 |
| `PersonNormalMessageReceived` / `GroupNormalMessageReceived` | 收到需要 LLM 处理的消息 |
| `PersonCommandSent` / `GroupCommandSent` | 收到命令消息 |
| `NormalMessageResponded` | LLM 响应完成 |
| `PromptPreProcessing` | 构建 Prompt 时 |

---

### 🔄 迁移注意事项

从 3.x 迁移到 4.x:
- 注册方式改为清单文件注册
- 消息链元素需使用**具名参数**
- 不再提供 `query: Query` 对象
- 所有 IO 操作改为异步写法

---

### 📤 发布方式

1. **GitHub Release**: 打包 `.lbpkg` 文件上传到 Release
2. **插件市场**: 通过 `lbp login` + `lbp publish` 发布到 [LangBot Space](https://space.langbot.app/market)
