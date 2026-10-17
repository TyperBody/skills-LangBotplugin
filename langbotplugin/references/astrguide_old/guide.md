## AstrBot 插件开发指南文档分析

已完成对 `langbotplugin/references/astrguide` 目录下所有文档的分析。

---

### 📋 AstrBot 插件配置详解 ([`plugin-config.md`](langbotplugin/references/astrguide/plugin-config.md:1))

#### 配置定义

在插件目录下创建 `_conf_schema.json` 文件：

```json
{
  "token": {
    "description": "Bot Token",
    "type": "string",
    "hint": "请输入您的 Bot Token",
    "obvious_hint": true,
    "default": "",
    "required": true
  },
  "sub_config": {
    "description": "嵌套配置",
    "type": "object",
    "items": {
      "name": {"description": "名称", "type": "string"},
      "id": {"description": "ID", "type": "int"}
    }
  }
}
```

#### Schema 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `type` | ✅ | 配置类型 |
| `description` | ❌ | 配置描述 |
| `hint` | ❌ | 鼠标悬浮提示 |
| `obvious_hint` | ❌ | 是否醒目显示提示 |
| `default` | ❌ | 默认值 |
| `invisible` | ❌ | 是否隐藏 |
| `options` | ❌ | 下拉选项列表 |
| `items` | ❌ | object 类型的子 Schema |
| `editor_mode` | ❌ | 代码编辑器模式 |
| `editor_language` | ❌ | 代码语言 (默认 json) |
| `editor_theme` | ❌ | 编辑器主题 (vs-light/vs-dark) |
| `_special` | ❌ | 特殊选择器 (v4.0.0+) |

#### 支持的配置类型

| 类型 | 说明 | 默认值 |
|------|------|--------|
| `string` | 字符串 | `""` |
| `text` | 大文本 (textarea) | `""` |
| `int` | 整数 | `0` |
| `float` | 浮点数 | `0.0` |
| `bool` | 布尔值 | `False` |
| `object` | 嵌套对象 | `{}` |
| `list` | 列表 | `[]` |
| `dict` | 字典 (v4.10.4+) | `{}` |
| `file` | 文件上传 (v4.13.0+) | `[]` |
| `template_list` | 模板列表 (v4.10.4+) | - |

#### 特殊选择器 `_special` (v4.0.0+)

| 值 | 说明 |
|----|------|
| `select_provider` | 选择已配置的模型提供商 |
| `select_provider_tts` | 选择 TTS 提供商 |
| `select_provider_stt` | 选择 STT 提供商 |
| `select_persona` | 选择人设 |

#### dict 类型示例 (带滑块)

```json
{
  "custom_extra_body": {
    "type": "dict",
    "description": "自定义请求体参数",
    "template_schema": {
      "temperature": {
        "name": "Temperature",
        "type": "float",
        "default": 0.6,
        "slider": {"min": 0, "max": 2, "step": 0.1}
      }
    }
  }
}
```

#### file 类型示例 (v4.13.0+)

```json
{
  "demo_files": {
    "type": "file",
    "description": "上传文件",
    "default": [],
    "file_types": ["pdf", "docx"]
  }
}
```

#### template_list 类型示例 (v4.10.4+)

```json
{
  "field_id": {
    "type": "template_list",
    "templates": {
      "template_1": {
        "name": "模板一",
        "items": {
          "attr_a": {"type": "int", "default": 10},
          "attr_b": {"type": "bool", "default": true}
        }
      }
    }
  }
}
```

#### 在插件中使用配置

```python
from astrbot.api import AstrBotConfig

@register("config", "Soulter", "配置示例", "1.0.0")
class ConfigPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        
        # 读取配置
        token = self.config.get("token", "")
        
        # 保存配置
        self.config.save_config()
```

配置文件自动保存在 `data/config/<plugin_name>_config.json`。

---

### 其他核心功能摘要

- **最小实例**: 继承 `Star` 类，使用 `@register` + `@filter.command` 装饰器
- **消息处理**: 支持指令、指令组、带参指令、事件过滤器、事件钩子
- **消息发送**: 被动消息 (`yield`)、主动消息 (`send_message`)、富媒体 (`MessageChain`)
- **AI 集成**: LLM 调用、Tool 定义、Agent 调用、Multi-Agent、对话/人格管理器
- **会话控制**: `session_waiter` 装饰器实现多轮对话
- **存储**: KV 存储 (`put_kv_data/get_kv_data`)、大文件存储规范
- **文转图**: `text_to_image()` 和 `html_render()` (Jinja2 + HTML)
