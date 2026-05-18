---
name: langbotworkflow
description: 蒸馏整个LangBot工作系统的完整架构文档，细致到每一个接口与请求。涵盖后端核心模块(pkg目录)、前端核心模块(web目录)、API接口与路由、工作流系统(entities/executor/nodes)、配置与持久化系统、插件系统、平台管理、模型提供商等全部核心组件。
license: Apache-2.0
trigger_keywords:
  - langbot架构
  - langbot工作流
  - langbot系统
  - langbot核心
  - langbot完整文档
  - langbot全栈
  - langbot后端
  - langbot前端
  - langbot API
  - langbot工作系统
metadata:
  author: rockqinQ
  version: "1.0 Beta"
---

# langbotworkflow

你现在是「LangBot核心开发者rockqinQ」
你精通LangBot整个工作系统，包括后端架构、前端架构、API接口、工作流引擎、插件系统、平台管理、模型提供商、持久化层等全部核心组件。

## 指令

1. 本skill文档是LangBot完整工作系统的蒸馏文档，涵盖从启动到运行的全部流程
2. 所有代码示例必须基于 LangBot_copy 项目的实际代码
3. 接口文档必须包含完整的请求参数、响应格式、错误码
4. 工作流系统文档必须包含节点类型、执行流程、状态管理
5. 持久化层文档必须包含数据库模型、迁移策略、CRUD操作
6. 配置系统文档必须包含配置项、验证规则、默认值
7. 插件系统文档必须包含插件生命周期、组件类型、事件系统
8. 平台管理文档必须包含适配器、机器人、会话管理
9. 模型提供商文档必须包含LLM、Embedding、Rerank模型管理
10. 前端架构文档必须包含状态管理、组件结构、HTTP客户端
11. 所有文档必须使用中文编写
12. 代码示例必须包含完整的导入语句
13. API接口必须包含认证方式、限流策略
14. 工作流节点必须包含输入输出端口定义、配置schema
15. 持久化模型必须包含字段类型、索引、约束

## LangBot 系统架构概览

### 项目结构

```
LangBot_copy/
├── src/langbot/                    # 后端源码
│   ├── pkg/                        # 核心包
│   │   ├── api/                    # HTTP API层
│   │   │   ├── http/
│   │   │   │   ├── controller/     # 路由控制器
│   │   │   │   │   ├── groups/     # 路由组
│   │   │   │   │   │   ├── workflows/    # 工作流路由
│   │   │   │   │   │   ├── pipelines/    # 管道路由
│   │   │   │   │   │   ├── platform/     # 平台路由
│   │   │   │   │   │   ├── provider/     # 提供商路由
│   │   │   │   │   │   ├── knowledge/    # 知识库路由
│   │   │   │   │   │   ├── resources/    # 资源路由
│   │   │   │   │   │   └── ...
│   │   │   │   │   └── main.py     # HTTP控制器主类
│   │   │   │   └── service/        # 业务服务层
│   │   │   │       ├── workflow.py # 工作流服务
│   │   │   │       ├── pipeline.py # 管道服务
│   │   │   │       ├── bot.py      # 机器人服务
│   │   │   │       ├── provider.py # 提供商服务
│   │   │   │       ├── model.py    # 模型服务
│   │   │   │       ├── knowledge.py# 知识库服务
│   │   │   │       ├── mcp.py      # MCP服务
│   │   │   │       ├── user.py     # 用户服务
│   │   │   │       ├── apikey.py   # API密钥服务
│   │   │   │       ├── webhook.py  # Webhook服务
│   │   │   │       └── monitoring.py# 监控服务
│   │   ├── core/                   # 核心启动与运行时
│   │   │   ├── boot.py             # 启动入口
│   │   │   ├── app.py              # 应用主类
│   │   │   ├── stage.py            # 启动阶段
│   │   │   ├── stages/             # 启动阶段实现
│   │   │   │   ├── load_config.py  # 加载配置
│   │   │   │   ├── migrate.py      # 数据库迁移
│   │   │   │   ├── genkeys.py      # 生成密钥
│   │   │   │   ├── setup_logger.py # 设置日志
│   │   │   │   ├── build_app.py    # 构建应用
│   │   │   │   └── show_notes.py   # 显示提示
│   │   │   ├── entities.py         # 核心实体
│   │   │   ├── taskmgr.py          # 任务管理
│   │   │   └── migration.py        # 迁移管理
│   │   ├── workflow/               # 工作流引擎
│   │   │   ├── entities.py         # 工作流实体
│   │   │   ├── executor.py         # 执行引擎
│   │   │   ├── node.py             # 节点基类
│   │   │   ├── metadata.py         # 节点元数据
│   │   │   ├── registry.py         # 节点注册表
│   │   │   └── nodes/              # 节点实现
│   │   │       ├── message_trigger.py   # 消息触发器
│   │   │       ├── cron_trigger.py      # 定时触发器
│   │   │       ├── event_trigger.py     # 事件触发器
│   │   │       ├── webhook_trigger.py   # Webhook触发器
│   │   │       ├── llm_call.py          # LLM调用
│   │   │       ├── http_request.py      # HTTP请求
│   │   │       ├── code_executor.py     # 代码执行
│   │   │       ├── condition.py         # 条件分支
│   │   │       ├── switch.py            # 开关
│   │   │       ├── loop.py              # 循环
│   │   │       ├── parallel.py          # 并行
│   │   │       ├── iterator.py          # 迭代器
│   │   │       ├── merge.py             # 合并
│   │   │       ├── wait.py              # 等待
│   │   │       ├── end.py               # 结束
│   │   │       ├── reply_message.py     # 回复消息
│   │   │       ├── send_message.py      # 发送消息
│   │   │       ├── set_variable.py      # 设置变量
│   │   │       ├── store_data.py        # 存储数据
│   │   │       ├── call_pipeline.py     # 调用管道
│   │   │       ├── plugin_call.py       # 插件调用
│   │   │       ├── knowledge_retrieval.py# 知识检索
│   │   │       ├── parameter_extractor.py# 参数提取
│   │   │       ├── question_classifier.py# 问题分类
│   │   │       ├── data_transform.py    # 数据转换
│   │   │       ├── variable_aggregator.py# 变量聚合
│   │   │       ├── opening_statement.py # 开场白
│   │   │       ├── memory_store.py      # 记忆存储
│   │   │       ├── mcp_tool.py          # MCP工具
│   │   │       ├── dify_workflow.py     # Dify工作流
│   │   │       ├── n8n_workflow.py      # n8n工作流
│   │   │       ├── langflow_flow.py     # Langflow流程
│   │   │       ├── coze_bot.py          # Coze机器人
│   │   │       └── dify_knowledge_query.py# Dify知识查询
│   │   ├── entity/                 # 实体定义
│   │   │   ├── persistence/        # 持久化实体
│   │   │   │   ├── workflow.py     # 工作流模型
│   │   │   │   ├── pipeline.py     # 管道模型
│   │   │   │   ├── bot.py          # 机器人模型
│   │   │   │   ├── model.py        # 模型模型
│   │   │   │   ├── user.py         # 用户模型
│   │   │   │   ├── apikey.py       # API密钥模型
│   │   │   │   ├── webhook.py      # Webhook模型
│   │   │   │   ├── mcp.py          # MCP模型
│   │   │   │   ├── plugin.py       # 插件模型
│   │   │   │   ├── rag.py          # RAG模型
│   │   │   │   ├── vector.py       # 向量模型
│   │   │   │   └── monitoring.py   # 监控模型
│   │   │   ├── dto/                # 数据传输对象
│   │   │   └── errors/             # 错误定义
│   │   ├── persistence/            # 持久化层
│   │   │   ├── mgr.py              # 持久化管理器
│   │   │   └── migrations/         # 数据库迁移
│   │   ├── config/                 # 配置系统
│   │   │   ├── manager.py          # 配置管理器
│   │   │   ├── model.py            # 配置模型
│   │   │   └── impls/              # 配置实现
│   │   │       ├── yaml.py         # YAML配置
│   │   │       ├── json.py         # JSON配置
│   │   │       └── pymodule.py     # Python模块配置
│   │   ├── platform/               # 平台管理
│   │   │   ├── botmgr.py           # 机器人管理器
│   │   │   └── webhook_pusher.py   # Webhook推送器
│   │   ├── provider/               # 模型提供商
│   │   │   ├── modelmgr/           # 模型管理
│   │   │   │   ├── modelmgr.py     # 模型管理器
│   │   │   │   ├── requester.py    # 请求器基类
│   │   │   │   └── requesters/     # 请求器实现
│   │   │   └── session/            # 会话管理
│   │   │       └── sessionmgr.py   # 会话管理器
│   │   ├── plugin/                 # 插件系统
│   │   │   ├── connector.py        # 插件连接器
│   │   │   └── handler.py          # 插件处理器
│   │   ├── pipeline/               # 管道系统
│   │   │   ├── controller.py       # 管道控制器
│   │   │   ├── pipelinemgr.py      # 管道管理器
│   │   │   ├── pool.py             # 查询池
│   │   │   ├── aggregator.py       # 消息聚合器
│   │   │   ├── bansess/            # 封禁会话
│   │   │   ├── longtext/           # 长文本处理
│   │   │   ├── resprule/           # 响应规则
│   │   │   └── wrapper/            # 包装器
│   │   ├── rag/                    # RAG系统
│   │   │   ├── knowledge/          # 知识库
│   │   │   │   ├── kbmgr.py        # 知识库管理器
│   │   │   │   └── base.py         # 基础类
│   │   │   └── service/            # RAG服务
│   │   │       └── runtime.py      # 运行时服务
│   │   ├── vector/                 # 向量数据库
│   │   │   └── mgr.py              # 向量管理器
│   │   ├── storage/                # 存储系统
│   │   │   ├── mgr.py              # 存储管理器
│   │   │   ├── provider.py         # 存储提供商
│   │   │   └── providers/          # 存储实现
│   │   │       ├── localstorage.py # 本地存储
│   │   │       └── s3storage.py    # S3存储
│   │   ├── command/                # 命令系统
│   │   │   └── cmdmgr.py           # 命令管理器
│   │   ├── discover/               # 发现引擎
│   │   │   └── engine.py           # 组件发现引擎
│   │   ├── telemetry/              # 遥测
│   │   │   └── telemetry.py        # 遥测管理
│   │   ├── survey/                 # 调查
│   │   │   └── manager.py          # 调查管理器
│   │   └── utils/                  # 工具类
│   │       ├── constants.py        # 常量
│   │       ├── importutil.py       # 导入工具
│   │       ├── version.py          # 版本管理
│   │       ├── proxy.py            # 代理管理
│   │       └── logcache.py         # 日志缓存
│   └── templates/                  # 模板
│       └── metadata/               # 元数据
│           └── nodes/              # 节点元数据(YAML)
│               ├── message_trigger.yaml
│               ├── cron_trigger.yaml
│               ├── event_trigger.yaml
│               ├── webhook_trigger.yaml
│               ├── llm_call.yaml
│               ├── http_request.yaml
│               ├── code_executor.yaml
│               ├── condition.yaml
│               ├── switch.yaml
│               ├── loop.yaml
│               ├── parallel.yaml
│               ├── iterator.yaml
│               ├── merge.yaml
│               ├── wait.yaml
│               ├── end.yaml
│               ├── reply_message.yaml
│               ├── send_message.yaml
│               ├── set_variable.yaml
│               ├── store_data.yaml
│               ├── call_pipeline.yaml
│               ├── plugin_call.yaml
│               ├── knowledge_retrieval.yaml
│               ├── parameter_extractor.yaml
│               ├── question_classifier.yaml
│               ├── data_transform.yaml
│               ├── variable_aggregator.yaml
│               ├── opening_statement.yaml
│               ├── memory_store.yaml
│               ├── mcp_tool.yaml
│               ├── dify_workflow.yaml
│               ├── n8n_workflow.yaml
│               ├── langflow_flow.yaml
│               ├── coze_bot.yaml
│               └── dify_knowledge_query.yaml
├── web/                            # 前端源码
│   ├── src/
│   │   ├── app/
│   │   │   ├── home/               # 主页
│   │   │   │   ├── workflows/      # 工作流页面
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   ├── WorkflowDetailContent.tsx
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── workflow-editor/    # 工作流编辑器
│   │   │   │   │   │   │   ├── WorkflowEditorComponent.tsx
│   │   │   │   │   │   │   ├── WorkflowNodeComponent.tsx
│   │   │   │   │   │   │   ├── PropertyPanel.tsx
│   │   │   │   │   │   │   ├── NodePalette.tsx
│   │   │   │   │   │   │   ├── workflow-constants.ts
│   │   │   │   │   │   │   ├── workflow-i18n.ts
│   │   │   │   │   │   │   └── workflow-node-metadata.ts
│   │   │   │   │   │   ├── workflow-debug-dialog/ # 调试对话框
│   │   │   │   │   │   ├── workflow-debugger/    # 调试器
│   │   │   │   │   │   ├── workflow-executions/  # 执行记录
│   │   │   │   │   │   └── workflow-form/        # 工作流表单
│   │   │   │   │   └── store/
│   │   │   │   │       └── useWorkflowStore.ts   # 状态管理
│   │   │   │   ├── bots/           # 机器人页面
│   │   │   │   ├── pipelines/      # 管道页面
│   │   │   │   ├── plugins/        # 插件页面
│   │   │   │   ├── knowledge/      # 知识库页面
│   │   │   │   ├── mcp/            # MCP页面
│   │   │   │   ├── monitoring/     # 监控页面
│   │   │   │   └── components/     # 共享组件
│   │   │   ├── infra/              # 基础设施
│   │   │   │   ├── entities/       # 实体定义
│   │   │   │   │   ├── api/index.ts        # API实体
│   │   │   │   │   ├── workflow/index.ts   # 工作流实体
│   │   │   │   │   ├── pipeline/index.ts   # 管道实体
│   │   │   │   │   ├── plugin/index.ts     # 插件实体
│   │   │   │   │   ├── message/index.ts    # 消息实体
│   │   │   │   │   └── common.ts           # 通用实体
│   │   │   │   ├── http/           # HTTP客户端
│   │   │   │   │   ├── BackendClient.ts    # 后端客户端
│   │   │   │   │   ├── BaseHttpClient.ts   # 基础HTTP客户端
│   │   │   │   │   ├── HttpClient.ts       # HTTP客户端
│   │   │   │   │   └── CloudServiceClient.ts# 云服务客户端
│   │   │   │   └── websocket/      # WebSocket客户端
│   │   │   │       ├── WebSocketClient.ts
│   │   │   │       └── WorkflowWebSocketClient.ts
│   │   │   ├── login/              # 登录页面
│   │   │   ├── register/           # 注册页面
│   │   │   ├── reset-password/     # 重置密码
│   │   │   └── wizard/             # 向导
│   │   ├── components/             # UI组件
│   │   │   └── ui/                 # shadcn/ui组件
│   │   ├── hooks/                  # React Hooks
│   │   ├── i18n/                   # 国际化
│   │   │   ├── locales/            # 语言包
│   │   │   │   ├── zh-Hans.ts      # 简体中文
│   │   │   │   ├── en-US.ts        # 英文
│   │   │   │   ├── ja-JP.ts        # 日文
│   │   │   │   ├── es-ES.ts        # 西班牙文
│   │   │   │   ├── ru-RU.ts        # 俄文
│   │   │   │   ├── th-TH.ts        # 泰文
│   │   │   │   ├── vi-VN.ts        # 越南文
│   │   │   │   └── zh-Hant.ts      # 繁体中文
│   │   │   └── I18nProvider.tsx
│   │   └── lib/                    # 工具库
│   └── package.json
├── tests/                          # 测试
├── plans/                          # 计划文档
├── docs/                           # 文档
└── docker/                         # Docker配置
```

## 一、后端核心模块

### 1.1 启动流程 (boot.py)

LangBot 启动流程按以下阶段顺序执行：

```python
# src/langbot/pkg/core/boot.py

stage_order = [
    'LoadConfigStage',      # 1. 加载配置
    'MigrationStage',       # 2. 数据库迁移
    'GenKeysStage',         # 3. 生成密钥
    'SetupLoggerStage',     # 4. 设置日志
    'BuildAppStage',        # 5. 构建应用
    'ShowNotesStage',       # 6. 显示提示
]

async def make_app(loop: asyncio.AbstractEventLoop) -> app.Application:
    # 检查调试模式
    if 'DEBUG' in os.environ and os.environ['DEBUG'] in ['true', '1']:
        constants.debug_mode = True

    ap = app.Application()
    ap.event_loop = loop

    # 按顺序执行启动阶段
    for stage_name in stage_order:
        stage_cls = stage.preregistered_stages[stage_name]
        stage_inst = stage_cls()
        await stage_inst.run(ap)

    await ap.initialize()
    return ap
```

### 1.2 应用主类 (app.py)

Application 类是运行时上下文，包含所有管理器和服务：

```python
# src/langbot/pkg/core/app.py

class Application:
    """运行时应用对象和上下文"""

    event_loop: asyncio.AbstractEventLoop = None
    task_mgr: taskmgr.AsyncTaskManager = None
    discover: discover_engine.ComponentDiscoveryEngine = None

    # 平台管理
    platform_mgr: im_mgr.PlatformManager = None
    webhook_pusher: WebhookPusher = None

    # 命令管理
    cmd_mgr: cmdmgr.CommandManager = None

    # 会话管理
    sess_mgr: llm_session_mgr.SessionManager = None

    # 模型管理
    model_mgr: llm_model_mgr.ModelManager = None

    # RAG管理
    rag_mgr: rag_mgr.RAGManager = None
    rag_runtime_service: RAGRuntimeService = None

    # 工具管理
    tool_mgr: llm_tool_mgr.ToolManager = None

    # 配置管理
    instance_config: config_mgr.ConfigManager = None
    instance_id: config_mgr.ConfigManager = None

    # 插件系统
    plugin_connector: plugin_connector.PluginRuntimeConnector = None

    # 管道系统
    query_pool: pool.QueryPool = None
    msg_aggregator: message_aggregator.MessageAggregator = None
    ctrl: controller.Controller = None
    pipeline_mgr: pipelinemgr.PipelineManager = None

    # 持久化
    persistence_mgr: persistencemgr.PersistenceManager = None

    # HTTP服务
    http_ctrl: http_controller.HTTPController = None
    user_service: user_service.UserService = None
    space_service: space_service.SpaceService = None
    llm_model_service: model_service.LLMModelsService = None
    embedding_models_service: model_service.EmbeddingModelsService = None
    rerank_models_service: model_service.RerankModelsService = None
    provider_service: provider_service.ModelProviderService = None
    pipeline_service: pipeline_service.PipelineService = None
    bot_service: bot_service.BotService = None
    knowledge_service: knowledge_service.KnowledgeService = None
    mcp_service: mcp_service.MCPService = None
    apikey_service: apikey_service.ApiKeyService = None
    webhook_service: webhook_service.WebhookService = None
    workflow_service: workflow_service.WorkflowService = None
    monitoring_service: monitoring_service.MonitoringService = None
    maintenance_service: maintenance_service.MaintenanceService = None

    # 遥测与调查
    telemetry: telemetry_module.TelemetryManager = None
    survey: survey_module.SurveyManager = None

    async def run(self):
        """启动应用"""
        await self.plugin_connector.initialize_plugins()

        # 启动平台管理器
        self.task_mgr.create_task(
            self.platform_mgr.run(),
            name='platform-manager',
        )
        # 启动查询控制器
        self.task_mgr.create_task(
            self.ctrl.run(),
            name='query-controller',
        )
        # 启动HTTP API控制器
        self.task_mgr.create_task(
            self.http_ctrl.run(),
            name='http-api-controller',
        )
```

### 1.3 配置系统 (config/)

配置系统支持 YAML、JSON、Python 模块三种配置方式：

```python
# src/langbot/pkg/config/manager.py

class ConfigManager:
    """配置管理器"""

    def __init__(self, impl: ConfigImpl, data: dict = None):
        self.impl = impl
        self.data = data or {}

    async def load(self) -> dict:
        """加载配置"""
        self.data = await self.impl.load()
        return self.data

    async def save(self) -> None:
        """保存配置"""
        await self.impl.save(self.data)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
```

### 1.4 持久化层 (persistence/)

持久化层使用 SQLAlchemy ORM，支持 SQLite、PostgreSQL、MySQL：

```python
# src/langbot/pkg/persistence/mgr.py

class PersistenceManager:
    """持久化管理器"""

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = None
        self.async_session = None

    async def initialize(self):
        """初始化数据库连接"""
        self.engine = sqlalchemy.ext.asyncio.create_async_engine(self.db_url)
        self.async_session = sqlalchemy.orm.sessionmaker(
            self.engine, class_=sqlalchemy.ext.asyncio.AsyncSession
        )
        # 自动创建表
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def execute_async(self, statement):
        """执行异步查询"""
        async with self.async_session() as session:
            result = await session.execute(statement)
            await session.commit()
            return result
```

## 二、工作流系统

### 2.1 工作流实体 (workflow/entities.py)

```python
# src/langbot/pkg/workflow/entities.py

class Position(pydantic.BaseModel):
    """节点在画布上的位置"""
    x: float = 0
    y: float = 0

class PortDefinition(pydantic.BaseModel):
    """节点端口定义"""
    name: str
    type: str = 'any'  # any, string, number, boolean, object, array
    description: str = ''
    required: bool = True

class NodeDefinition(pydantic.BaseModel):
    """工作流节点定义"""
    id: str
    type: str
    name: str = ''
    position: Position = Position()
    config: dict[str, Any] = {}
    inputs: list[PortDefinition] = []
    outputs: list[PortDefinition] = []
    description: str = ''
    comment: str = ''  # 用户注释

class EdgeDefinition(pydantic.BaseModel):
    """工作流边定义（节点间连接）"""
    id: str
    source_node: str
    source_port: str = 'output'
    target_node: str
    target_port: str = 'input'
    condition: Optional[str] = None  # 可选条件表达式

class TriggerDefinition(pydantic.BaseModel):
    """工作流触发器定义"""
    id: str
    type: str  # message, cron, event, webhook
    config: dict[str, Any] = {}
    enabled: bool = True

class WorkflowSettings(pydantic.BaseModel):
    """工作流设置"""
    max_execution_time: int = 300  # 秒
    max_retries: int = 3
    retry_delay: int = 5  # 秒
    error_handling: str = 'stop'  # stop, continue, retry
    log_level: str = 'info'
    save_execution_history: bool = True
    max_concurrent_executions: int = 10

class WorkflowDefinition(pydantic.BaseModel):
    """完整工作流定义"""
    uuid: str
    name: str
    description: str = ''
    emoji: str = '🔄'
    version: int = 1
    nodes: list[NodeDefinition] = []
    edges: list[EdgeDefinition] = []
    variables: dict[str, Any] = {}  # 全局变量
    conversation_variables: list[ConversationVariable] = []  # 会话级变量
    settings: WorkflowSettings = WorkflowSettings()
    triggers: list[TriggerDefinition] = []
    global_config: WorkflowGlobalConfig = WorkflowGlobalConfig()
    extensions_preferences: ExtensionsPreferences = ExtensionsPreferences()
    is_enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    source: Optional[str] = None  # dify, n8n, langflow 等来源
    source_id: Optional[str] = None

class ExecutionStatus(enum.Enum):
    """工作流执行状态"""
    PENDING = 'pending'
    RUNNING = 'running'
    WAITING = 'waiting'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class NodeStatus(enum.Enum):
    """节点执行状态"""
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    SKIPPED = 'skipped'
```

### 2.2 工作流执行引擎 (workflow/executor.py)

```python
# src/langbot/pkg/workflow/executor.py

class WorkflowExecutor:
    """工作流执行引擎"""

    def __init__(self, ap: 'app.Application'):
        self.ap = ap
        self.registry = NodeTypeRegistry.instance()

    async def execute(
        self,
        workflow: WorkflowDefinition,
        trigger_type: str,
        trigger_data: dict = None,
        session_id: str = None,
        user_id: str = None,
        bot_id: str = None,
    ) -> str:
        """执行工作流，返回 execution_id"""
        execution_id = str(uuid.uuid4())

        # 创建执行上下文
        context = ExecutionContext(
            execution_id=execution_id,
            workflow_uuid=workflow.uuid,
            workflow_version=workflow.version,
            status=ExecutionStatus.RUNNING,
            trigger_type=trigger_type,
            trigger_data=trigger_data or {},
            session_id=session_id,
            user_id=user_id,
            bot_id=bot_id,
            variables=dict(workflow.variables),
        )

        # 保存执行记录
        await self._save_execution(context)

        try:
            # 找到触发器节点
            trigger_nodes = [n for n in workflow.nodes if n.type.endswith('_trigger')]
            if not trigger_nodes:
                raise ValueError('No trigger node found')

            # 执行触发器节点
            for trigger_node in trigger_nodes:
                node_instance = self.registry.create_instance(
                    trigger_node.type, trigger_node.id, trigger_node.config, ap=self.ap
                )
                if node_instance:
                    outputs = await node_instance.execute(trigger_data or {}, context)
                    # 传播到下游节点
                    await self._propagate(trigger_node.id, outputs, workflow, context)

            # 更新执行状态
            context.status = ExecutionStatus.COMPLETED
        except Exception as e:
            context.status = ExecutionStatus.FAILED
            context.error = str(e)
        finally:
            await self._update_execution(context)

        return execution_id

    async def _propagate(
        self,
        source_node_id: str,
        outputs: dict,
        workflow: WorkflowDefinition,
        context: ExecutionContext,
    ):
        """将输出传播到下游节点"""
        # 找到所有从源节点出发的边
        outgoing_edges = [e for e in workflow.edges if e.source_node == source_node_id]

        for edge in outgoing_edges:
            # 检查条件
            if edge.condition:
                if not _safe_eval(edge.condition, outputs):
                    continue

            # 找到目标节点
            target_node = next((n for n in workflow.nodes if n.id == edge.target_node), None)
            if not target_node:
                continue

            # 创建节点实例并执行
            node_instance = self.registry.create_instance(
                target_node.type, target_node.id, target_node.config, ap=self.ap
            )
            if node_instance:
                # 验证输入
                validation_errors = await node_instance.validate_inputs(outputs)
                if validation_errors:
                    context.add_log('error', f'Node {target_node.id} validation failed: {validation_errors}')
                    continue

                # 执行节点
                node_outputs = await node_instance.execute(outputs, context)

                # 继续传播
                await self._propagate(target_node.id, node_outputs, workflow, context)
```

### 2.3 节点基类 (workflow/node.py)

```python
# src/langbot/pkg/workflow/node.py

class WorkflowNode(abc.ABC):
    """所有工作流节点的基类"""

    type_name: str = ''  # 由 @workflow_node 装饰器设置
    category: str = 'misc'
    config_schema_source: Optional[str] = None
    config_stages: list[str] = []

    def __init__(self, node_id: str, config: dict[str, Any], ap: Optional['app.Application'] = None):
        self.node_id = node_id
        self.config = config
        self.ap = ap

    @abc.abstractmethod
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        """执行节点逻辑"""
        pass

    async def validate_inputs(self, inputs: dict[str, Any]) -> list[str]:
        """验证输入数据"""
        metadata = self._get_metadata()
        if metadata is None:
            return []
        errors = []
        for port in metadata.get('inputs', []):
            if port.get('required', True) and port.get('name') and port['name'] not in inputs:
                errors.append(f"Missing required input: {port['name']}")
        return errors

    async def validate_config(self) -> list[str]:
        """验证节点配置"""
        metadata = self._get_metadata()
        if metadata is None:
            return []
        errors = []
        for cfg in metadata.get('config', []):
            name = cfg.get('name', '')
            if not name:
                continue
            required = cfg.get('required', False)
            cfg_type = cfg.get('type', 'string')
            if required and name not in self.config:
                errors.append(f'Missing required config: {name}')
        return errors

    def _get_metadata(self) -> Optional[dict[str, Any]]:
        """从注册表获取YAML元数据"""
        from .registry import NodeTypeRegistry
        registry = NodeTypeRegistry.instance()
        return registry.get_metadata(self.type_name)

def workflow_node(type_name: str) -> Callable[[type[WorkflowNode]], type[WorkflowNode]]:
    """注册工作流节点类型的装饰器"""
    def decorator(cls: type[WorkflowNode]) -> type[WorkflowNode]:
        cls.type_name = type_name
        _pending_registrations.append((type_name, cls))
        return cls
    return decorator
```

### 2.4 节点注册表 (workflow/registry.py)

```python
# src/langbot/pkg/workflow/registry.py

class NodeTypeRegistry:
    """工作流节点类型注册表（单例）"""

    _instance: Optional['NodeTypeRegistry'] = None

    def __init__(self):
        self._nodes: dict[str, type[WorkflowNode]] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._metadata_sources: dict[str, str] = {}
        self._categories: dict[str, list[str]] = {
            'trigger': [],
            'process': [],
            'control': [],
            'action': [],
            'integration': [],
            'misc': [],
        }

    @classmethod
    def instance(cls) -> 'NodeTypeRegistry':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_metadata(self, metadata: dict[str, Any], source: str = 'core') -> bool:
        """注册YAML元数据"""
        node_type = build_node_type(metadata)
        existing_source = self._metadata_sources.get(node_type)
        if existing_source:
            if existing_source == 'core' and source != 'core':
                logger.error('Plugin source %s attempted to override core workflow node %s', source, node_type)
                return False
        self._metadata[node_type] = copy.deepcopy(metadata)
        self._metadata_sources[node_type] = source
        self._add_to_category(metadata.get('category', 'misc'), node_type)
        return True

    def register(self, node_type: str, node_class: type[WorkflowNode]):
        """注册Python节点实现类"""
        self._nodes[node_type] = node_class
        metadata = self.get_metadata(node_type)
        category = metadata.get('category', getattr(node_class, 'category', 'misc'))
        self._add_to_category(category, node_type)

    def create_instance(
        self, node_type: str, node_id: str, config: dict[str, Any], ap: Optional['app.Application'] = None
    ) -> Optional[WorkflowNode]:
        """创建节点实例"""
        node_class = self.get(node_type)
        if node_class:
            return node_class(node_id, config, ap=ap)
        return None

    def get_merged_schema(self, node_type: str) -> Optional[dict[str, Any]]:
        """获取前端schema（从YAML元数据）"""
        metadata = self.get_metadata(node_type)
        if metadata:
            return self._metadata_to_schema(metadata)
        return None

    def list_all(self) -> list[dict[str, Any]]:
        """获取所有已注册的节点类型schema"""
        node_types = self._ordered_node_types(set(self._metadata.keys()) | set(self._nodes.keys()))
        return [schema for node_type in node_types if (schema := self.get_merged_schema(node_type)) is not None]
```

### 2.5 节点元数据 (workflow/metadata.py)

节点元数据从 YAML 文件加载，是 UI 展示的唯一真实来源：

```python
# src/langbot/pkg/workflow/metadata.py

class NodeMetadataLoader:
    """从YAML文件加载和缓存工作流节点元数据"""

    async def load_core_metadata(self, resource_dir: str = 'metadata/nodes') -> int:
        """从 langbot.templates 包加载核心节点元数据"""
        return await self.load_package_directory('langbot.templates', resource_dir, source='core')

    async def load_package_directory(self, package: str, resource_dir: str, source: str = 'core') -> int:
        """从包资源目录加载YAML文件"""
        root = resources.files(package).joinpath(resource_dir)
        yaml_files = sorted(
            (item for item in root.iterdir() if item.is_file() and item.name.endswith(('.yaml', '.yml'))),
            key=lambda item: item.name,
        )
        return self._load_files(yaml_files, source=source)

class NodeMetadataValidator:
    """验证工作流节点元数据"""

    REQUIRED_FIELDS = ('name', 'category', 'inputs', 'outputs', 'config')
    VALID_CATEGORIES = {'trigger', 'process', 'control', 'action', 'integration', 'misc'}
    VALID_PORT_TYPES = {'any', 'string', 'number', 'integer', 'boolean', 'object', 'array', 'datetime', 'null'}
    VALID_CONFIG_TYPES = {
        'string', 'integer', 'number', 'float', 'boolean', 'select', 'json',
        'textarea', 'text', 'secret', 'array[string]', 'file', 'array[file]',
        'llm-model-selector', 'embedding-model-selector', 'rerank-model-selector',
        'pipeline-selector', 'knowledge-base-selector', 'bot-selector', 'tools-selector',
        'model-fallback-selector', 'prompt-editor', 'plugin-selector', 'webhook-url', 'embed-code',
    }
```

## 三、API 接口与路由

### 3.1 路由组结构 (api/http/controller/groups/)

```
api/http/controller/groups/
├── workflows/          # 工作流路由
│   ├── workflows.py    # CRUD + 执行
│   └── websocket_chat.py  # WebSocket 聊天
├── pipelines/          # 管道路由
│   ├── pipelines.py    # CRUD
│   ├── embed.py        # 嵌入
│   └── websocket_chat.py  # WebSocket 聊天
├── platform/           # 平台路由
│   ├── bots.py         # 机器人管理
│   └── adapters.py     # 适配器管理
├── provider/           # 提供商路由
│   ├── providers.py    # 模型提供商
│   ├── models.py       # 模型管理
│   └── requesters.py   # 请求器
├── knowledge/          # 知识库路由
│   ├── base.py         # 基础CRUD
│   ├── engines.py      # 引擎管理
│   ├── parsers.py      # 解析器
│   └── migration.py    # 迁移
├── resources/          # 资源路由
│   ├── mcp.py          # MCP服务器
│   └── tools.py        # 工具
├── plugins.py          # 插件路由
├── apikeys.py          # API密钥路由
├── webhooks.py         # Webhook路由
├── webhook_mgmt.py     # Webhook管理
├── user.py             # 用户路由
├── system.py           # 系统路由
├── stats.py            # 统计路由
├── monitoring.py       # 监控路由
├── logs.py             # 日志路由
├── files.py            # 文件路由
└── survey.py           # 调查路由
```

### 3.2 工作流 API (api/http/controller/groups/workflows/workflows.py)

```python
# 基础路由: /api/v1/workflows

@group.group_class('workflows', '/api/v1/workflows')
class WorkflowsRouterGroup(group.RouterGroup):

    async def initialize(self) -> None:
        # GET /api/v1/workflows - 获取所有工作流
        @self.route('', methods=['GET', 'POST'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _() -> str:
            if quart.request.method == 'GET':
                sort_by = quart.request.args.get('sort_by', 'created_at')
                sort_order = quart.request.args.get('sort_order', 'DESC')
                enabled_only = quart.request.args.get('enabled_only', 'false').lower() == 'true'
                return self.success(
                    data={'workflows': await self.ap.workflow_service.get_workflows(sort_by, sort_order, enabled_only)}
                )
            elif quart.request.method == 'POST':
                json_data = await quart.request.json
                workflow_uuid = await self.ap.workflow_service.create_workflow(json_data)
                return self.success(data={'uuid': workflow_uuid})

        # GET /api/v1/workflows/_/node-types - 获取节点类型
        @self.route('/_/node-types', methods=['GET'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _() -> str:
            return self.success(
                data={
                    'node_types': await self.ap.workflow_service.get_node_types(),
                    'categories': await self.ap.workflow_service.get_node_types_by_category_meta(),
                }
            )

        # GET/PUT/DELETE /api/v1/workflows/<workflow_uuid> - 单个工作流操作
        @self.route('/<workflow_uuid>', methods=['GET', 'PUT', 'DELETE'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str) -> str:
            if quart.request.method == 'GET':
                workflow = await self.ap.workflow_service.get_workflow(workflow_uuid)
                return self.success(data={'workflow': workflow}) if workflow else self.http_status(404, -1, 'workflow not found')
            elif quart.request.method == 'PUT':
                json_data = await quart.request.json
                await self.ap.workflow_service.update_workflow(workflow_uuid, json_data)
                return self.success()
            elif quart.request.method == 'DELETE':
                await self.ap.workflow_service.delete_workflow(workflow_uuid)
                return self.success()

        # POST /api/v1/workflows/<workflow_uuid>/publish - 发布工作流
        @self.route('/<workflow_uuid>/publish', methods=['POST'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str) -> str:
            await self.ap.workflow_service.publish_workflow(workflow_uuid)
            return self.success()

        # POST /api/v1/workflows/<workflow_uuid>/unpublish - 取消发布
        @self.route('/<workflow_uuid>/unpublish', methods=['POST'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str) -> str:
            await self.ap.workflow_service.unpublish_workflow(workflow_uuid)
            return self.success()

        # POST /api/v1/workflows/<workflow_uuid>/copy - 复制工作流
        @self.route('/<workflow_uuid>/copy', methods=['POST'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str) -> str:
            new_uuid = await self.ap.workflow_service.copy_workflow(workflow_uuid)
            return self.success(data={'uuid': new_uuid})

        # POST /api/v1/workflows/<workflow_uuid>/execute - 执行工作流
        @self.route('/<workflow_uuid>/execute', methods=['POST'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str) -> str:
            json_data = await quart.request.json or {}
            trigger_data = json_data.get('trigger_data', {})
            session_id = json_data.get('session_id')
            user_id = json_data.get('user_id')
            bot_id = json_data.get('bot_id')
            execution_id = await self.ap.workflow_service.execute_workflow(
                workflow_uuid, trigger_type='manual', trigger_data=trigger_data,
                session_id=session_id, user_id=user_id, bot_id=bot_id,
            )
            return self.success(data={'execution_id': execution_id})

        # GET /api/v1/workflows/<workflow_uuid>/executions - 获取执行记录
        @self.route('/<workflow_uuid>/executions', methods=['GET'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str) -> str:
            limit = int(quart.request.args.get('limit', 50))
            offset = int(quart.request.args.get('offset', 0))
            executions = await self.ap.workflow_service.get_executions(workflow_uuid=workflow_uuid, limit=limit, offset=offset)
            return self.success(data=executions)

        # GET /api/v1/workflows/<workflow_uuid>/executions/<execution_uuid> - 获取执行详情
        @self.route('/<workflow_uuid>/executions/<execution_uuid>', methods=['GET'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str, execution_uuid: str) -> str:
            execution = await self.ap.workflow_service.get_execution(execution_uuid)
            return self.success(data={'execution': execution}) if execution else self.http_status(404, -1, 'execution not found')

        # GET /api/v1/workflows/<workflow_uuid>/versions - 获取版本历史
        @self.route('/<workflow_uuid>/versions', methods=['GET'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str) -> str:
            versions = await self.ap.workflow_service.get_versions(workflow_uuid)
            return self.success(data={'versions': versions})

        # POST /api/v1/workflows/<workflow_uuid>/rollback/<int:version> - 回滚版本
        @self.route('/<workflow_uuid>/rollback/<int:version>', methods=['POST'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str, version: int) -> str:
            await self.ap.workflow_service.rollback_to_version(workflow_uuid, version)
            return self.success()

        # GET/PUT /api/v1/workflows/<workflow_uuid>/extensions - 扩展配置
        @self.route('/<workflow_uuid>/extensions', methods=['GET', 'PUT'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str) -> str:
            if quart.request.method == 'GET':
                workflow = await self.ap.workflow_service.get_workflow(workflow_uuid)
                plugins = await self.ap.plugin_connector.list_plugins(component_kinds=['Command', 'EventListener', 'Tool'])
                mcp_servers = await self.ap.mcp_service.get_mcp_servers(contain_runtime_info=True)
                return self.success(data={
                    'enable_all_plugins': extensions_prefs.get('enable_all_plugins', True),
                    'enable_all_mcp_servers': extensions_prefs.get('enable_all_mcp_servers', True),
                    'bound_plugins': extensions_prefs.get('plugins', []),
                    'available_plugins': plugins,
                    'bound_mcp_servers': extensions_prefs.get('mcp_servers', []),
                    'available_mcp_servers': mcp_servers,
                })
            elif quart.request.method == 'PUT':
                json_data = await quart.request.json
                await self.ap.workflow_service.update_workflow_extensions(
                    workflow_uuid,
                    json_data.get('bound_plugins', []),
                    json_data.get('bound_mcp_servers', []),
                    json_data.get('enable_all_plugins', True),
                    json_data.get('enable_all_mcp_servers', True),
                )
                return self.success()

        # POST /api/v1/workflows/<workflow_uuid>/debug/start - 开始调试
        @self.route('/<workflow_uuid>/debug/start', methods=['POST'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str) -> str:
            json_data = await quart.request.json or {}
            execution_id = await self.ap.workflow_service.start_debug(
                workflow_uuid, json_data.get('trigger_data', {}), json_data.get('breakpoints', []),
            )
            return self.success(data={'execution_id': execution_id})

        # POST /api/v1/workflows/<workflow_uuid>/debug/pause - 暂停调试
        @self.route('/<workflow_uuid>/debug/pause', methods=['POST'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str) -> str:
            await self.ap.workflow_service.pause_debug(workflow_uuid)
            return self.success()

        # POST /api/v1/workflows/<workflow_uuid>/debug/resume - 恢复调试
        @self.route('/<workflow_uuid>/debug/resume', methods=['POST'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str) -> str:
            await self.ap.workflow_service.resume_debug(workflow_uuid)
            return self.success()

        # POST /api/v1/workflows/<workflow_uuid>/debug/stop - 停止调试
        @self.route('/<workflow_uuid>/debug/stop', methods=['POST'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str) -> str:
            await self.ap.workflow_service.stop_debug(workflow_uuid)
            return self.success()

        # GET /api/v1/workflows/<workflow_uuid>/debug/logs - 获取调试日志
        @self.route('/<workflow_uuid>/debug/logs', methods=['GET'], auth_type=group.AuthType.USER_TOKEN_OR_API_KEY)
        async def _(workflow_uuid: str) -> str:
            logs = await self.ap.workflow_service.get_debug_logs(workflow_uuid)
            return self.success(data={'logs': logs})
```

### 3.3 工作流服务 (api/http/service/workflow.py)

```python
# src/langbot/pkg/api/http/service/workflow.py

class WorkflowService:
    """工作流服务，管理CRUD和执行"""

    DEFAULT_MAX_EXECUTION_TIME = 300
    STALE_EXECUTION_TIMEOUT_SECONDS = 300

    def __init__(self, ap: 'app.Application') -> None:
        self.ap = ap
        self.executor = WorkflowExecutor(ap)
        self.registry = NodeTypeRegistry.instance()
        from ....workflow import nodes  # 导入节点触发注册

    async def get_workflows(self, sort_by: str = 'created_at', sort_order: str = 'DESC', enabled_only: bool = False) -> list[dict]:
        """获取所有工作流"""
        query = sqlalchemy.select(persistence_workflow.Workflow)
        if enabled_only:
            query = query.where(persistence_workflow.Workflow.is_enabled == True)
        # 排序...
        result = await self.ap.persistence_mgr.execute_async(query)
        return [self._serialize_workflow(w) for w in result.all()]

    async def get_workflow(self, workflow_uuid: str) -> Optional[dict]:
        """获取单个工作流"""
        result = await self.ap.persistence_mgr.execute_async(
            sqlalchemy.select(persistence_workflow.Workflow).where(persistence_workflow.Workflow.uuid == workflow_uuid)
        )
        workflow = result.first()
        return self._serialize_workflow(workflow) if workflow else None

    async def create_workflow(self, workflow_data: dict) -> str:
        """创建工作流"""
        workflow_uuid = str(uuid.uuid4())
        new_workflow = {
            'uuid': workflow_uuid,
            'name': workflow_data.get('name', 'New Workflow'),
            'description': workflow_data.get('description', ''),
            'emoji': workflow_data.get('emoji', '🔄'),
            'version': 1,
            'is_enabled': workflow_data.get('is_enabled', True),
            'definition': workflow_data.get('definition', {'nodes': [], 'edges': [], 'variables': {}}),
            'global_config': workflow_data.get('global_config', {}),
            'extensions_preferences': workflow_data.get('extensions_preferences', {
                'enable_all_plugins': True, 'enable_all_mcp_servers': True, 'plugins': [], 'mcp_servers': [],
            }),
        }
        await self.ap.persistence_mgr.execute_async(
            sqlalchemy.insert(persistence_workflow.Workflow).values(**new_workflow)
        )
        return workflow_uuid

    async def update_workflow(self, workflow_uuid: str, workflow_data: dict) -> None:
        """更新工作流"""
        # 移除受保护字段
        protected_fields = ['uuid', 'created_at']
        for field in protected_fields:
            workflow_data.pop(field, None)

        # 处理 nodes, edges, variables 字段
        nodes = workflow_data.pop('nodes', None)
        edges = workflow_data.pop('edges', None)
        variables = workflow_data.pop('variables', None)

        if nodes is not None or edges is not None or variables is not None:
            definition = workflow_data.get('definition', {})
            if nodes is not None:
                definition['nodes'] = nodes
            if edges is not None:
                definition['edges'] = edges
            if variables is not None:
                definition['variables'] = variables
            workflow_data['definition'] = definition

        # 版本号递增
        if 'definition' in workflow_data:
            current = await self.get_workflow(workflow_uuid)
            workflow_data['version'] = current.get('version', 0) + 1
            # 保存版本历史
            await self._save_version_history(workflow_uuid, current.get('version', 1), current.get('definition', {}), current.get('global_config', {}))

        await self.ap.persistence_mgr.execute_async(
            sqlalchemy.update(persistence_workflow.Workflow).where(persistence_workflow.Workflow.uuid == workflow_uuid).values(**workflow_data)
        )

    async def delete_workflow(self, workflow_uuid: str) -> None:
        """删除工作流"""
        await self.ap.persistence_mgr.execute_async(
            sqlalchemy.delete(persistence_workflow.Workflow).where(persistence_workflow.Workflow.uuid == workflow_uuid)
        )

    async def execute_workflow(
        self, workflow_uuid: str, trigger_type: str = 'manual', trigger_data: dict = None,
        session_id: str = None, user_id: str = None, bot_id: str = None,
    ) -> str:
        """执行工作流"""
        workflow = await self.get_workflow(workflow_uuid)
        if workflow is None:
            raise ValueError(f'Workflow {workflow_uuid} not found')

        execution_id = await self.executor.execute(
            workflow, trigger_type, trigger_data, session_id, user_id, bot_id,
        )
        return execution_id

    def _serialize_workflow(self, workflow) -> dict:
        """序列化工作流"""
        return {
            'uuid': workflow.uuid,
            'name': workflow.name,
            'description': workflow.description,
            'emoji': workflow.emoji,
            'version': workflow.version,
            'is_enabled': workflow.is_enabled,
            'definition': workflow.definition,
            'global_config': workflow.global_config,
            'extensions_preferences': workflow.extensions_preferences,
            'created_at': workflow.created_at.isoformat() if workflow.created_at else None,
            'updated_at': workflow.updated_at.isoformat() if workflow.updated_at else None,
        }
```

## 四、持久化模型

### 4.1 工作流模型 (entity/persistence/workflow.py)

```python
# src/langbot/pkg/entity/persistence/workflow.py

class Workflow(Base):
    """工作流定义"""
    __tablename__ = 'workflows'

    uuid = sqlalchemy.Column(sqlalchemy.String(255), primary_key=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    emoji = sqlalchemy.Column(sqlalchemy.String(10), nullable=True, default='🔄')
    version = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=1)
    is_enabled = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)
    definition = sqlalchemy.Column(sqlalchemy.JSON, nullable=False, default={})  # nodes, edges, variables
    global_config = sqlalchemy.Column(sqlalchemy.JSON, nullable=False, default={})  # safety, output
    extensions_preferences = sqlalchemy.Column(sqlalchemy.JSON, nullable=False, default={
        'enable_all_plugins': True, 'enable_all_mcp_servers': True, 'plugins': [], 'mcp_servers': [],
    })
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now())
    updated_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now())

class WorkflowVersion(Base):
    """工作流版本历史"""
    __tablename__ = 'workflow_versions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    workflow_uuid = sqlalchemy.Column(sqlalchemy.String(255), nullable=False, index=True)
    version = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    definition = sqlalchemy.Column(sqlalchemy.JSON, nullable=False)
    global_config = sqlalchemy.Column(sqlalchemy.JSON, nullable=False, default={})
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now())
    created_by = sqlalchemy.Column(sqlalchemy.String(255), nullable=True)
    __table_args__ = (sqlalchemy.UniqueConstraint('workflow_uuid', 'version', name='uq_workflow_version'),)

class WorkflowTrigger(Base):
    """工作流触发器配置"""
    __tablename__ = 'workflow_triggers'

    uuid = sqlalchemy.Column(sqlalchemy.String(255), primary_key=True, unique=True)
    workflow_uuid = sqlalchemy.Column(sqlalchemy.String(255), nullable=False, index=True)
    type = sqlalchemy.Column(sqlalchemy.String(50), nullable=False)  # message, cron, event, webhook
    config = sqlalchemy.Column(sqlalchemy.JSON, nullable=False, default={})
    is_enabled = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)
    priority = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now())
    updated_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now())

class WorkflowExecution(Base):
    """工作流执行记录"""
    __tablename__ = 'workflow_executions'

    uuid = sqlalchemy.Column(sqlalchemy.String(255), primary_key=True, unique=True)
    workflow_uuid = sqlalchemy.Column(sqlalchemy.String(255), nullable=False, index=True)
    workflow_version = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String(20), nullable=False)  # pending, running, completed, failed, cancelled
    trigger_type = sqlalchemy.Column(sqlalchemy.String(50), nullable=True)
    trigger_data = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    variables = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    start_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    end_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    error = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now())

class WorkflowNodeExecution(Base):
    """工作流节点执行记录"""
    __tablename__ = 'workflow_node_executions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    execution_uuid = sqlalchemy.Column(sqlalchemy.String(255), nullable=False, index=True)
    node_id = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    node_type = sqlalchemy.Column(sqlalchemy.String(50), nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String(20), nullable=False)  # pending, running, completed, failed, skipped
    inputs = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    outputs = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    start_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    end_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    error = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    retry_count = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)

class ScheduledJob(Base):
    """定时任务（用于cron触发器）"""
    __tablename__ = 'workflow_scheduled_jobs'

    uuid = sqlalchemy.Column(sqlalchemy.String(255), primary_key=True, unique=True)
    trigger_uuid = sqlalchemy.Column(sqlalchemy.String(255), nullable=False, index=True)
    cron_expression = sqlalchemy.Column(sqlalchemy.String(100), nullable=True)
    next_run_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    last_run_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    is_enabled = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)
```

## 五、前端架构

### 5.1 前端实体 (web/src/app/infra/entities/)

```typescript
// web/src/app/infra/entities/workflow/index.ts

// 节点位置
export interface Position {
  x: number;
  y: number;
}

// 端口定义
export interface PortDefinition {
  name: string;
  type: string;
  description?: string;
  required?: boolean;
}

// 节点定义
export interface NodeDefinition {
  id: string;
  type: string;
  name: string;
  position: Position;
  config: Record<string, unknown>;
}

// 边定义
export interface EdgeDefinition {
  id: string;
  source: string;
  sourceHandle?: string;
  target: string;
  targetHandle?: string;
  condition?: string;
}

// 工作流定义
export interface WorkflowDefinition {
  uuid: string;
  name: string;
  emoji?: string;
  description?: string;
  version: number;
  nodes: NodeDefinition[];
  edges: EdgeDefinition[];
  variables?: Record<string, unknown>;
  settings?: WorkflowSettings;
  triggers?: TriggerDefinition[];
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
}

// 节点类型元数据
export interface NodeTypeMetadata {
  type: string;
  name: I18nObject;
  description?: I18nObject;
  category: NodeCategory;
  icon?: string;
  color?: string;
  inputs: PortDefinition[];
  outputs: PortDefinition[];
  config_schema: IDynamicFormItemSchema[];
}

// 节点类别
export type NodeCategory = 'trigger' | 'process' | 'control' | 'action' | 'integration';

// 工作流执行状态
export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

// 工作流执行记录
export interface WorkflowExecution {
  id: string;
  workflow_uuid: string;
  workflow_version: number;
  status: ExecutionStatus;
  trigger_type?: string;
  trigger_data?: Record<string, unknown>;
  variables?: Record<string, unknown>;
  start_time?: string;
  end_time?: string;
  error?: string;
  created_at: string;
}

// API响应类型
export interface ApiRespWorkflows {
  workflows: WorkflowDefinition[];
}

export interface ApiRespWorkflow {
  workflow: WorkflowDefinition;
}

export interface ApiRespNodeTypes {
  node_types: NodeTypeMetadata[];
  categories: NodeCategoryInfo[];
}

export interface ApiRespWorkflowExecutions {
  executions: WorkflowExecution[];
  total: number;
}
```

### 5.2 状态管理 (web/src/app/home/workflows/store/useWorkflowStore.ts)

```typescript
// 使用 Zustand 进行状态管理

interface WorkflowState {
  // 当前编辑的工作流
  currentWorkflow: Workflow | null;

  // React Flow 节点和边
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];

  // 节点类型元数据
  nodeTypes: WorkflowNodeTypeMetadata[];
  nodeCategories: WorkflowNodeCategory[];

  // 选择状态
  selectedNodeId: string | null;
  selectedEdgeId: string | null;

  // UI状态
  isDirty: boolean;
  isSaving: boolean;
  isLoading: boolean;

  // 撤销/重做历史
  history: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }[];
  historyIndex: number;

  // 调试状态
  debugMode: boolean;
  debugState: DebugState;
  debugExecutionId: string | null;
  currentNodeId: string | null;
  nodeExecutionResults: Record<string, NodeExecutionResult>;
  breakpoints: Record<string, boolean>;
  debugLogs: DebugLog[];
  debugContext: DebugContext;
  watchedVariables: string[];

  // Actions
  setCurrentWorkflow: (workflow: Workflow | null) => void;
  setNodes: (nodes: WorkflowNode[]) => void;
  setEdges: (edges: WorkflowEdge[]) => void;
  setNodeTypes: (types: WorkflowNodeTypeMetadata[], categories: WorkflowNodeCategory[]) => void;

  // 节点操作
  addNode: (type: string, position: { x: number; y: number }) => void;
  updateNodeConfig: (nodeId: string, config: Record<string, unknown>) => void;
  deleteNode: (nodeId: string) => void;

  // 边操作
  deleteEdge: (edgeId: string) => void;
  updateEdgeCondition: (edgeId: string, condition: string) => void;

  // 撤销/重做
  undo: () => void;
  redo: () => void;
  pushHistory: () => void;

  // 调试操作
  setDebugMode: (enabled: boolean) => void;
  toggleBreakpoint: (nodeId: string) => void;
  addDebugLog: (log: Omit<DebugLog, 'id' | 'timestamp'>) => void;
}
```

### 5.3 HTTP 客户端 (web/src/app/infra/http/BackendClient.ts)

```typescript
// 后端API客户端

export class BackendClient extends BaseHttpClient {
  // ============ 工作流 API ============

  public getWorkflows(params?: {
    sort_by?: string;
    sort_order?: string;
    enabled_only?: boolean;
  }): Promise<ApiRespWorkflows> {
    return this.get('/api/v1/workflows', params);
  }

  public getWorkflow(uuid: string): Promise<ApiRespWorkflow> {
    return this.get(`/api/v1/workflows/${uuid}`);
  }

  public createWorkflow(request: CreateWorkflowRequest): Promise<{ uuid: string }> {
    return this.post('/api/v1/workflows', request);
  }

  public updateWorkflow(uuid: string, request: UpdateWorkflowRequest): Promise<object> {
    return this.put(`/api/v1/workflows/${uuid}`, request);
  }

  public deleteWorkflow(uuid: string): Promise<object> {
    return this.delete(`/api/v1/workflows/${uuid}`);
  }

  public publishWorkflow(uuid: string): Promise<object> {
    return this.post(`/api/v1/workflows/${uuid}/publish`);
  }

  public unpublishWorkflow(uuid: string): Promise<object> {
    return this.post(`/api/v1/workflows/${uuid}/unpublish`);
  }

  public copyWorkflow(uuid: string): Promise<{ uuid: string }> {
    return this.post(`/api/v1/workflows/${uuid}/copy`);
  }

  public executeWorkflow(uuid: string, request: ExecuteWorkflowRequest): Promise<{ execution_id: string }> {
    return this.post(`/api/v1/workflows/${uuid}/execute`, request);
  }

  public getWorkflowExecutions(
    uuid: string,
    params?: { limit?: number; offset?: number },
  ): Promise<ApiRespWorkflowExecutions> {
    return this.get(`/api/v1/workflows/${uuid}/executions`, params);
  }

  public getWorkflowExecution(
    workflowUuid: string,
    executionUuid: string,
  ): Promise<ApiRespWorkflowExecution> {
    return this.get(`/api/v1/workflows/${workflowUuid}/executions/${executionUuid}`);
  }

  public getWorkflowVersions(uuid: string): Promise<ApiRespWorkflowVersions> {
    return this.get(`/api/v1/workflows/${uuid}/versions`);
  }

  public rollbackWorkflow(uuid: string, version: number): Promise<object> {
    return this.post(`/api/v1/workflows/${uuid}/rollback/${version}`);
  }

  public getWorkflowExtensions(uuid: string): Promise<ApiRespWorkflowExtensions> {
    return this.get(`/api/v1/workflows/${uuid}/extensions`);
  }

  public updateWorkflowExtensions(
    uuid: string,
    request: UpdateWorkflowExtensionsRequest,
  ): Promise<object> {
    return this.put(`/api/v1/workflows/${uuid}/extensions`, request);
  }

  public getWorkflowNodeTypes(): Promise<ApiRespNodeTypes> {
    return this.get('/api/v1/workflows/_/node-types');
  }

  // ============ 调试 API ============

  public startDebug(
    uuid: string,
    triggerData?: Record<string, unknown>,
    breakpoints?: string[],
  ): Promise<{ execution_id: string }> {
    return this.post(`/api/v1/workflows/${uuid}/debug/start`, {
      trigger_data: triggerData,
      breakpoints,
    });
  }

  public pauseDebug(uuid: string): Promise<object> {
    return this.post(`/api/v1/workflows/${uuid}/debug/pause`);
  }

  public resumeDebug(uuid: string): Promise<object> {
    return this.post(`/api/v1/workflows/${uuid}/debug/resume`);
  }

  public stopDebug(uuid: string): Promise<object> {
    return this.post(`/api/v1/workflows/${uuid}/debug/stop`);
  }

  public getDebugLogs(uuid: string): Promise<{ logs: DebugLog[] }> {
    return this.get(`/api/v1/workflows/${uuid}/debug/logs`);
  }
}
```

## 六、插件系统

### 6.1 插件生命周期

```python
# src/langbot/pkg/plugin/connector.py

class PluginRuntimeConnector:
    """插件运行时连接器"""

    async def initialize_plugins(self):
        """初始化所有插件"""
        # 1. 发现插件
        plugins = await self.discover_plugins()

        # 2. 加载插件
        for plugin in plugins:
            await self.load_plugin(plugin)

        # 3. 注册插件组件
        for plugin in plugins:
            await self.register_plugin_components(plugin)

    async def load_plugin(self, plugin_path: str):
        """加载单个插件"""
        # 读取 manifest.yaml
        manifest = await self.read_manifest(plugin_path)

        # 验证 manifest
        self.validate_manifest(manifest)

        # 导入插件模块
        module = await self.import_plugin_module(plugin_path)

        # 创建插件实例
        plugin_instance = module.PluginClass(self.ap)

        # 调用插件初始化
        await plugin_instance.initialize()

        # 注册插件组件
        await self.register_components(plugin_instance)

    async def unload_plugin(self, plugin_name: str):
        """卸载插件"""
        plugin = self.plugins.get(plugin_name)
        if plugin:
            # 调用插件清理
            await plugin.cleanup()

            # 注销组件
            await self.unregister_components(plugin)

            # 移除插件
            del self.plugins[plugin_name]
```

### 6.2 插件组件类型

```python
# 插件可注册的组件类型

COMPONENT_TYPES = {
    'Command': '命令组件',
    'EventListener': '事件监听器',
    'Tool': '工具组件',
    'KnowledgeRetriever': '知识检索器',
}

# 组件注册示例

@plugin.register_component('Command')
class MyCommand(CommandComponent):
    """命令组件示例"""

    name = 'mycommand'
    description = '我的命令'

    async def execute(self, context: CommandContext) -> CommandReturn:
        """执行命令"""
        return CommandReturn(text='Hello from my command!')
```

## 七、平台管理

### 7.1 平台管理器 (platform/botmgr.py)

```python
# src/langbot/pkg/platform/botmgr.py

class PlatformManager:
    """平台管理器，管理所有机器人适配器"""

    def __init__(self, ap: 'app.Application'):
        self.ap = ap
        self.adapters: dict[str, Adapter] = {}
        self.bots: dict[str, Bot] = {}

    async def run(self):
        """启动平台管理器"""
        # 加载所有启用的机器人
        bots = await self.load_bots()

        for bot in bots:
            if bot.enable:
                await self.start_bot(bot)

    async def start_bot(self, bot: Bot):
        """启动单个机器人"""
        # 获取适配器
        adapter = self.adapters.get(bot.adapter)
        if not adapter:
            logger.error(f'Adapter {bot.adapter} not found')
            return

        # 启动适配器
        await adapter.start(bot)

    async def stop_bot(self, bot_uuid: str):
        """停止机器人"""
        bot = self.bots.get(bot_uuid)
        if bot:
            adapter = self.adapters.get(bot.adapter)
            if adapter:
                await adapter.stop(bot)
```

## 八、模型提供商

### 8.1 模型管理器 (provider/modelmgr/modelmgr.py)

```python
# src/langbot/pkg/provider/modelmgr/modelmgr.py

class ModelManager:
    """模型管理器"""

    def __init__(self, ap: 'app.Application'):
        self.ap = ap
        self.providers: dict[str, ModelProvider] = {}
        self.models: dict[str, LLMModel] = {}

    async def load_providers(self):
        """加载所有模型提供商"""
        # 从数据库加载
        providers = await self.ap.persistence_mgr.execute_async(
            sqlalchemy.select(ModelProvider)
        )
        for provider in providers.all():
            self.providers[provider.uuid] = provider

    async def get_model(self, model_uuid: str) -> Optional[LLMModel]:
        """获取模型"""
        return self.models.get(model_uuid)

    async def call_model(
        self, model: LLMModel, messages: list[dict], **kwargs
    ) -> ChatCompletion:
        """调用模型"""
        provider = self.providers.get(model.provider_uuid)
        if not provider:
            raise ValueError(f'Provider {model.provider_uuid} not found')

        requester = provider.get_requester()
        return await requester.chat(messages, **kwargs)
```

## 九、工作流节点完整列表

### 9.1 触发器节点

| 节点类型 | 名称 | 描述 | 输入端口 | 输出端口 |
|---------|------|------|---------|---------|
| message_trigger | 消息触发器 | 当收到消息时触发 | 无 | message: 消息内容, sender: 发送者, platform: 平台 |
| cron_trigger | 定时触发器 | 按cron表达式定时触发 | 无 | trigger_time: 触发时间 |
| event_trigger | 事件触发器 | 当特定事件发生时触发 | 无 | event: 事件数据 |
| webhook_trigger | Webhook触发器 | 当收到Webhook请求时触发 | 无 | request: 请求数据 |

### 9.2 处理节点

| 节点类型 | 名称 | 描述 | 输入端口 | 输出端口 |
|---------|------|------|---------|---------|
| llm_call | LLM调用 | 调用大语言模型 | prompt: 提示词, model: 模型 | response: 响应内容, tokens: 令牌数 |
| http_request | HTTP请求 | 发送HTTP请求 | url: URL, method: 方法, body: 请求体 | response: 响应内容, status: 状态码 |
| code_executor | 代码执行 | 执行Python代码 | code: 代码, inputs: 输入 | outputs: 输出结果 |
| knowledge_retrieval | 知识检索 | 从知识库检索相关内容 | query: 查询, kb_uuid: 知识库UUID | results: 检索结果 |
| parameter_extractor | 参数提取 | 从文本中提取参数 | text: 文本, schema: 参数schema | params: 提取的参数 |
| question_classifier | 问题分类 | 对问题进行分类 | question: 问题, categories: 分类 | category: 分类结果, confidence: 置信度 |
| data_transform | 数据转换 | 转换数据格式 | data: 输入数据, transform: 转换规则 | result: 转换结果 |
| variable_aggregator | 变量聚合 | 聚合多个变量 | variables: 变量列表 | result: 聚合结果 |

### 9.3 控制节点

| 节点类型 | 名称 | 描述 | 输入端口 | 输出端口 |
|---------|------|------|---------|---------|
| condition | 条件分支 | 根据条件选择执行路径 | input: 输入, condition: 条件 | true: 条件为真, false: 条件为假 |
| switch | 开关 | 多路分支 | input: 输入, selector: 选择器 | case_1, case_2, ...: 各分支输出 |
| loop | 循环 | 循环执行 | items: 循环项, body: 循环体 | results: 循环结果 |
| parallel | 并行 | 并行执行多个节点 | inputs: 输入列表 | outputs: 输出列表 |
| iterator | 迭代器 | 遍历列表 | list: 列表, body: 迭代体 | results: 迭代结果 |
| merge | 合并 | 合并多个分支 | inputs: 输入列表 | result: 合并结果 |
| wait | 等待 | 等待指定时间 | duration: 等待时间 | completed: 完成信号 |

### 9.4 动作节点

| 节点类型 | 名称 | 描述 | 输入端口 | 输出端口 |
|---------|------|------|---------|---------|
| reply_message | 回复消息 | 回复用户消息 | message: 回复内容, session_id: 会话ID | success: 是否成功 |
| send_message | 发送消息 | 发送消息给用户 | message: 消息内容, user_id: 用户ID | success: 是否成功 |
| set_variable | 设置变量 | 设置工作流变量 | name: 变量名, value: 值 | success: 是否成功 |
| store_data | 存储数据 | 存储数据到数据库 | data: 数据, table: 表名 | success: 是否成功 |
| call_pipeline | 调用管道 | 调用另一个管道 | pipeline_uuid: 管道UUID, input: 输入 | output: 输出结果 |
| plugin_call | 插件调用 | 调用插件功能 | plugin_name: 插件名, method: 方法, args: 参数 | result: 结果 |
| opening_statement | 开场白 | 发送开场白消息 | message: 开场白内容 | success: 是否成功 |
| memory_store | 记忆存储 | 存储对话记忆 | content: 内容, session_id: 会话ID | success: 是否成功 |

### 9.5 集成节点

| 节点类型 | 名称 | 描述 | 输入端口 | 输出端口 |
|---------|------|------|---------|---------|
| mcp_tool | MCP工具 | 调用MCP服务器工具 | server: 服务器名, tool: 工具名, args: 参数 | result: 结果 |
| dify_workflow | Dify工作流 | 调用Dify工作流 | workflow_uuid: 工作流UUID, input: 输入 | output: 输出 |
| n8n_workflow | n8n工作流 | 调用n8n工作流 | webhook_url: Webhook URL, input: 输入 | output: 输出 |
| langflow_flow | Langflow流程 | 调用Langflow流程 | flow_id: 流程ID, input: 输入 | output: 输出 |
| coze_bot | Coze机器人 | 调用Coze机器人 | bot_id: 机器人ID, message: 消息 | response: 响应 |
| dify_knowledge_query | Dify知识查询 | 查询Dify知识库 | kb_id: 知识库ID, query: 查询 | results: 结果 |

### 9.6 结束节点

| 节点类型 | 名称 | 描述 | 输入端口 | 输出端口 |
|---------|------|------|---------|---------|
| end | 结束 | 结束工作流执行 | input: 输入 | 无 |

## 十、节点元数据 YAML 格式

```yaml
# templates/metadata/nodes/llm_call.yaml

name: llm_call
label:
  zh_Hans: LLM调用
  en_US: LLM Call
description:
  zh_Hans: 调用大语言模型进行推理
  en_US: Call LLM for inference
category: process
icon: brain
color: '#6366f1'

inputs:
  - name: prompt
    type: string
    required: true
    description:
      zh_Hans: 提示词
      en_US: Prompt
  - name: model
    type: string
    required: false
    description:
      zh_Hans: 模型选择
      en_US: Model selection

outputs:
  - name: response
    type: string
    description:
      zh_Hans: 模型响应
      en_US: Model response
  - name: tokens
    type: integer
    description:
      zh_Hans: 使用的令牌数
      en_US: Tokens used

config:
  - name: model
    type: llm-model-selector
    required: true
    label:
      zh_Hans: 模型
      en_US: Model
  - name: temperature
    type: number
    required: false
    default: 0.7
    min_value: 0
    max_value: 2
    label:
      zh_Hans: 温度
      en_US: Temperature
  - name: max_tokens
    type: integer
    required: false
    default: 2048
    min_value: 1
    max_value: 32000
    label:
      zh_Hans: 最大令牌数
      en_US: Max Tokens
```

## 十一、认证与授权

### 11.1 认证方式

```python
# API 支持两种认证方式

class AuthType(enum.Enum):
    USER_TOKEN = 'user_token'      # 用户Token认证
    API_KEY = 'api_key'            # API密钥认证
    USER_TOKEN_OR_API_KEY = 'user_token_or_api_key'  # 两者皆可
    PUBLIC = 'public'              # 公开（无需认证）
```

### 11.2 限流策略

```python
# 限流配置在 instance_config 中

rate_limit = {
    'enable': True,
    'requests_per_minute': 60,
    'burst_limit': 10,
}
```

## 十二、错误码

### 12.1 通用错误码

| 错误码 | 描述 |
|-------|------|
| 0 | 成功 |
| -1 | 通用错误 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

## 十三、WebSocket 接口

### 13.1 工作流调试 WebSocket

```
ws://host/api/v1/workflows/<workflow_uuid>/debug/ws
```

消息格式：

```json
// 客户端发送
{
  "type": "pause" | "resume" | "stop" | "set_breakpoint" | "clear_breakpoint",
  "data": {}
}

// 服务端推送
{
  "type": "log" | "node_start" | "node_end" | "execution_complete" | "execution_failed",
  "data": {
    "node_id": "node_xxx",
    "status": "running" | "completed" | "failed",
    "inputs": {},
    "outputs": {},
    "error": "错误信息"
  }
}
```

## 十四、最佳实践

### 14.1 创建工作流

1. 使用 `POST /api/v1/workflows` 创建工作流
2. 使用 `PUT /api/v1/workflows/<uuid>` 更新节点和边
3. 使用 `POST /api/v1/workflows/<uuid>/publish` 发布工作流
4. 使用 `POST /api/v1/workflows/<uuid>/execute` 执行工作流

### 14.2 调试工作流

1. 使用 `POST /api/v1/workflows/<uuid>/debug/start` 开始调试
2. 通过 WebSocket 连接接收实时日志
3. 使用 `set_breakpoint` 设置断点
4. 使用 `pause`/`resume` 控制执行流程
5. 使用 `stop` 停止调试

### 14.3 节点开发

1. 创建 YAML 元数据文件定义节点 UI
2. 创建 Python 类实现节点逻辑
3. 使用 `@workflow_node` 装饰器注册节点
4. 实现 `execute` 方法
5. 可选实现 `validate_inputs` 和 `validate_config`

## 十五、常见问题

### 15.1 节点元数据不生效

确保 YAML 文件放在 `templates/metadata/nodes/` 目录下，且文件名与节点类型名一致。

### 15.2 工作流执行失败

检查：
1. 触发器节点是否存在
2. 节点连接是否正确
3. 节点配置是否完整
4. 查看执行日志获取详细错误信息

### 15.3 插件组件未注册

确保插件的 `manifest.yaml` 中正确声明了组件类型，并且插件已正确加载。
