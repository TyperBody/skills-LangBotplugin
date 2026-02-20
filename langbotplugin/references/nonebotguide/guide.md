## NoneBot 插件配置完整指南

### 一、配置加载机制

#### 配置来源（优先级从高到低）

1. **直接传入** - `nonebot.init()` 参数
2. **系统环境变量** - 环境变量设置
3. **dotenv 配置文件** - `.env` 和 `.env.{ENVIRONMENT}` 文件

```python
# 1. 直接传入（最高优先级）
import nonebot
nonebot.init(custom_config="value on init")

# 初始化后修改
config = nonebot.get_driver().config
config.custom_config = "changed value"
```

```bash
# 2. 系统环境变量
# Windows cmd
set CUSTOM_CONFIG="value from env"
# Windows PowerShell
$Env:CUSTOM_CONFIG="value from env"
# Linux/macOS
export CUSTOM_CONFIG="value from env"
```

```dotenv
# 3. dotenv 配置文件（最低优先级）
CUSTOM_CONFIG=value from dotenv
```

### 二、dotenv 配置文件详解

#### 文件结构

```
📦 my-bot/
├── 📜 .env                # 基础配置（所有环境都加载）
├── 📜 .env.prod           # 生产环境配置
├── 📜 .env.dev            # 开发环境配置
└── 📜 .env.test           # 测试环境配置
```

#### 环境切换

```dotenv
# .env 文件
ENVIRONMENT=prod  # 决定加载 .env.prod
```

```python
# 或在代码中指定
nonebot.init(_env_file=".env.dev")
```

#### 配置值解析规则

配置值使用 **JSON 解析**，无法解析则作为字符串：

```dotenv
# 字符串（无法 JSON 解析，直接作为字符串）
STRING_CONFIG=some string
ANOTHER_STRING=hello world

# 数字
INT_CONFIG=42
FLOAT_CONFIG=3.14

# 布尔值
BOOL_TRUE=true
BOOL_FALSE=false

# 列表（JSON 数组）
LIST_CONFIG=[1, 2, 3]
STRING_LIST=["a", "b", "c"]
MIXED_LIST=[1, "two", true]

# 字典（JSON 对象）
DICT_CONFIG={"key": "value", "num": 123}

# 多行配置（用引号包裹）
MULTILINE_CONFIG='
[
  {"name": "item1"},
  {"name": "item2"}
]
'

# 空值
EMPTY_STRING=
NULL_VALUE
```

**解析结果：**
```python
{
    "string_config": "some string",
    "another_string": "hello world",
    "int_config": 42,
    "float_config": 3.14,
    "bool_true": True,
    "bool_false": False,
    "list_config": [1, 2, 3],
    "string_list": ["a", "b", "c"],
    "mixed_list": [1, "two", True],
    "dict_config": {"key": "value", "num": 123},
    "multiline_config": [{"name": "item1"}, {"name": "item2"}],
    "empty_string": "",
    "null_value": None,
}
```

#### 嵌套配置（使用 `__` 分隔）

```dotenv
# 基础字典
DICT={"k1": "v1", "k2": null}

# 嵌套覆盖和添加
DICT__K2=v2
DICT__K3=v3
DICT__INNER__K4=v4
```

**解析结果：**
```python
{
    "dict": {
        "k1": "v1",
        "k2": "v2",        # null 被覆盖
        "k3": "v3",        # 新增
        "inner": {
            "k4": "v4"     # 嵌套字典
        }
    }
}
```

### 三、插件配置定义

#### 基础配置类

```python
# plugins/weather/config.py
from pydantic import BaseModel

class Config(BaseModel):
    """插件配置类 - 继承自 pydantic.BaseModel"""
    
    # 必填配置（无默认值）
    weather_api_key: str
    
    # 可选配置（有默认值）
    weather_command_priority: int = 10
    weather_plugin_enabled: bool = True
    weather_timeout: float = 30.0
    weather_supported_cities: list[str] = ["北京", "上海", "广州"]
```

#### 配置验证

```python
from pydantic import BaseModel, field_validator, model_validator

class Config(BaseModel):
    weather_api_key: str
    weather_command_priority: int = 10
    weather_max_retries: int = 3
    weather_timeout: float = 30.0

    # 单字段验证
    @field_validator("weather_command_priority")
    @classmethod
    def check_priority(cls, v: int) -> int:
        if v < 1:
            raise ValueError("priority must be >= 1")
        if v > 100:
            raise ValueError("priority must be <= 100")
        return v

    @field_validator("weather_api_key")
    @classmethod
    def check_api_key(cls, v: str) -> str:
        if not v or len(v) < 10:
            raise ValueError("api_key must be at least 10 characters")
        return v

    # 多字段验证
    @model_validator(mode="after")
    def check_retry_timeout(self):
        if self.weather_max_retries * 10 > self.weather_timeout:
            raise ValueError("timeout too short for retries")
        return self
```

#### 使用 Pydantic Field 进行更细粒度控制

```python
from pydantic import BaseModel, Field

class Config(BaseModel):
    weather_api_key: str = Field(
        ...,  # 必填
        min_length=10,
        max_length=100,
        description="Weather API Key"
    )
    
    weather_command_priority: int = Field(
        default=10,
        ge=1,      # >= 1
        le=100,    # <= 100
        description="Command priority"
    )
    
    weather_timeout: float = Field(
        default=30.0,
        gt=0,      # > 0
        le=300,    # <= 300
        description="Request timeout in seconds"
    )
    
    weather_cache_ttl: int = Field(
        default=3600,
        alias="WEATHER_CACHE_TIME",  # 环境变量别名
        description="Cache TTL in seconds"
    )
```

### 四、嵌套配置（推荐方式）

避免配置名冲突，简化访问：

```python
# plugins/weather/config.py
from pydantic import BaseModel

class WeatherConfig(BaseModel):
    """嵌套配置 - 不带前缀"""
    api_key: str
    command_priority: int = 10
    enabled: bool = True
    timeout: float = 30.0
    supported_cities: list[str] = ["北京", "上海"]

class Config(BaseModel):
    """主配置类"""
    weather: WeatherConfig
```

```python
# plugins/weather/__init__.py
from nonebot import get_plugin_config
from .config import Config

# 获取嵌套配置
plugin_config = get_plugin_config(Config).weather

# 简洁访问
api_key = plugin_config.api_key
priority = plugin_config.command_priority
```

**对应的 dotenv 配置：**
```dotenv
# 使用双下划线表示嵌套
WEATHER__API_KEY=your_api_key_here
WEATHER__COMMAND_PRIORITY=5
WEATHER__ENABLED=true
WEATHER__TIMEOUT=60.0
WEATHER__SUPPORTED_CITIES=["北京", "上海", "深圳"]
```

### 五、在插件中使用配置

#### 完整示例

```python
# plugins/weather/__init__.py
from nonebot import on_command, get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg, ArgPlainText
from nonebot.matcher import Matcher
from nonebot.rule import to_me

from .config import Config

# 获取插件配置（启动时执行一次）
plugin_config = get_plugin_config(Config)

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="天气查询",
    description="查询城市天气信息",
    usage="/天气 [城市名]",
    type="application",
    homepage="https://github.com/...",
    config=Config,  # 关联配置类
    supported_adapters={"~onebot.v11", "~onebot.v12"},
    extra={"author": "your_name"},
)

# 使用配置创建响应器
weather = on_command(
    "天气",
    rule=to_me() if plugin_config.weather_require_at else None,
    aliases={"weather", "查天气"},
    priority=plugin_config.weather_command_priority,
    block=True,
)

@weather.handle()
async def handle_first(matcher: Matcher, args: Message = CommandArg()):
    # 检查插件是否启用
    if not plugin_config.weather_enabled:
        await matcher.finish("天气插件已禁用")
    
    if city := args.extract_plain_text():
        matcher.set_arg("city", args)

@weather.got("city", prompt="请输入要查询的城市名")
async def handle_city(city: str = ArgPlainText()):
    # 使用配置中的支持城市列表
    if city not in plugin_config.weather_supported_cities:
        await weather.reject(f"暂不支持查询 {city}")
    
    # 使用配置中的 API Key 和超时设置
    result = await fetch_weather(
        city,
        api_key=plugin_config.weather_api_key,
        timeout=plugin_config.weather_timeout,
    )
    await weather.finish(f"{city}天气：{result}")
```

#### 配置定义

```python
# plugins/weather/config.py
from pydantic import BaseModel, Field, field_validator

class Config(BaseModel):
    # API 配置
    weather_api_key: str = Field(..., min_length=10)
    weather_api_url: str = "https://api.weather.com"
    weather_timeout: float = Field(default=30.0, gt=0, le=300)
    
    # 功能配置
    weather_enabled: bool = True
    weather_require_at: bool = False
    weather_command_priority: int = Field(default=10, ge=1, le=100)
    
    # 数据配置
    weather_supported_cities: list[str] = ["北京", "上海", "广州", "深圳"]
    weather_cache_ttl: int = 3600
    
    @field_validator("weather_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v.startswith("sk-"):
            raise ValueError("API key must start with 'sk-'")
        return v
```

### 六、读取全局配置

```python
import nonebot
from nonebot import get_driver

# 方式1：通过 driver 获取
driver = get_driver()
global_config = driver.config

# 方式2：直接获取
global_config = nonebot.get_driver().config

# 访问配置项
superusers = global_config.superusers
command_start = global_config.command_start
log_level = global_config.log_level
host = global_config.host
port = global_config.port
```

### 七、内置配置项完整列表

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `DRIVER` | str | `"~fastapi"` | 驱动器，如 `~fastapi+~httpx+~websockets` |
| `HOST` | IPvAnyAddress | `127.0.0.1` | 服务器监听地址 |
| `PORT` | int | `8080` | 服务器监听端口（1-65535） |
| `LOG_LEVEL` | int/str | `INFO` | 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL） |
| `API_TIMEOUT` | float/None | `30.0` | 调用平台接口超时时间（秒），None 表示无限 |
| `SUPERUSERS` | set[str] | `set()` | 超级用户 ID 集合 |
| `NICKNAME` | set[str] | `set()` | 机器人昵称集合 |
| `COMMAND_START` | set[str] | `{"/"}` | 命令消息起始符集合 |
| `COMMAND_SEP` | set[str] | `{"."}` | 命令消息分隔符集合 |
| `SESSION_EXPIRE_TIMEOUT` | timedelta | `2分钟` | 用户会话超时时间 |

### 八、配置文件示例

#### .env（通用配置）

```dotenv
# 环境设置
ENVIRONMENT=prod

# 通用配置
LOG_LEVEL=INFO
```

#### .env.prod（生产环境）

```dotenv
# 服务器配置
HOST=0.0.0.0
PORT=8080
DRIVER=~fastapi+~httpx+~websockets

# 机器人配置
SUPERUSERS=["123456789", "987654321"]
NICKNAME=["bot", "小助手"]
COMMAND_START=["/", ""]
COMMAND_SEP=[".", " "]

# API 配置
API_TIMEOUT=60.0

# 会话配置
SESSION_EXPIRE_TIMEOUT=00:05:00

# 插件配置
WEATHER__API_KEY=sk-your-production-key
WEATHER__ENABLED=true
WEATHER__TIMEOUT=30.0
```

#### .env.dev（开发环境）

```dotenv
# 服务器配置
HOST=127.0.0.1
PORT=8080
DRIVER=~fastapi

# 调试配置
LOG_LEVEL=DEBUG
API_TIMEOUT=10.0

# 开发用超级用户
SUPERUSERS=["console_user"]

# 插件配置（开发环境）
WEATHER__API_KEY=sk-your-dev-key
WEATHER__ENABLED=true
WEATHER__TIMEOUT=5.0
```

### 九、配置注意事项

1. **环境变量覆盖**：同名配置，环境变量会覆盖 dotenv 文件
2. **大小写不敏感**：`WEATHER_API_KEY` 和 `weather_api_key` 等价
3. **类型自动转换**：Pydantic 会自动进行类型转换
4. **必填项缺失**：启动时报错 `ValidationError`
5. **配置热更新**：配置在启动时加载，运行时修改 `.env` 不会生效
6. **敏感信息**：API Key 等敏感信息建议使用环境变量而非文件
