# Tool registry for planner
# Central registry for all available tools

from __future__ import annotations

from typing import Any

from . import BasePlannerTool
from .system import (
    ShellTool,
    ListProcessesTool,
    KillProcessTool,
    OpenAppTool,
    CloseAppTool,
    ListAppsTool,
    GetSystemInfoTool,
    AppleScriptTool,
)
from .file import (
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
    SearchFilesTool,
)
from .network import FetchURLTool
from .browser import (
    BrowserNavigateTool,
    BrowserClickTool,
    BrowserTypeTool,
    BrowserScreenshotTool,
    BrowserGetContentTool,
    BrowserWaitTool,
    BrowserScrollTool,
    BrowserExecuteScriptTool,
    BrowserNewTabTool,
    BrowserCloseTabTool,
    BrowserGetUrlTool,
    BrowserReloadTool,
    BrowserPressKeyTool,
    BrowserSelectOptionTool,
    BrowserGetAttributeTool,
    # Safari tools
    SafariOpenTool,
    SafariNavigateTool,
    SafariGetContentTool,
    SafariClickTool,
    SafariTypeTool,
    SafariPressKeyTool,
    # Chrome tools
    ChromeOpenTool,
    ChromeNavigateTool,
    ChromeGetContentTool,
    ChromeClickTool,
    ChromeTypeTool,
    ChromePressKeyTool,
)
from .dynamic import DynamicToolLoader
from .skills import SkillLoader, SkillToToolConverter


# Built-in tools that are always available
BUILTIN_TOOLS: list[type[BasePlannerTool]] = [
    # System tools
    ShellTool,
    ListProcessesTool,
    KillProcessTool,
    OpenAppTool,
    CloseAppTool,
    ListAppsTool,
    GetSystemInfoTool,
    AppleScriptTool,
    # File tools
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
    SearchFilesTool,
    # Network tools
    FetchURLTool,
    # Browser tools
    BrowserNavigateTool,
    BrowserClickTool,
    BrowserTypeTool,
    BrowserScreenshotTool,
    BrowserGetContentTool,
    BrowserWaitTool,
    BrowserScrollTool,
    BrowserExecuteScriptTool,
    BrowserNewTabTool,
    BrowserCloseTabTool,
    BrowserGetUrlTool,
    BrowserReloadTool,
    BrowserPressKeyTool,
    BrowserSelectOptionTool,
    BrowserGetAttributeTool,
    # Safari native tools
    SafariOpenTool,
    SafariNavigateTool,
    SafariGetContentTool,
    SafariClickTool,
    SafariTypeTool,
    SafariPressKeyTool,
    # Chrome native tools
    ChromeOpenTool,
    ChromeNavigateTool,
    ChromeGetContentTool,
    ChromeClickTool,
    ChromeTypeTool,
    ChromePressKeyTool,
]


class ToolRegistry:
    """Registry for all planner tools"""

    def __init__(self, plugin: Any):
        self.plugin = plugin
        self._builtin_tools: dict[str, BasePlannerTool] = {}
        self._dynamic_loader: DynamicToolLoader | None = None
        self._skill_loader: SkillLoader | None = None
        self._initialized = False

    async def initialize(self):
        """Initialize the tool registry"""
        if self._initialized:
            return

        import logging
        logger = logging.getLogger(__name__)

        # Register built-in tools
        logger.info(f"开始初始化工具注册表，BUILTIN_TOOLS 数量: {len(BUILTIN_TOOLS)}")
        for tool_class in BUILTIN_TOOLS:
            try:
                tool = tool_class()
                self._builtin_tools[tool.name] = tool
                logger.debug(f"注册工具: {tool.name}")
            except Exception as e:
                logger.error(f"注册工具失败 {tool_class}: {e}")

        logger.info(f"注册了 {len(self._builtin_tools)} 个内置工具")

        # Initialize dynamic tool loader
        self._dynamic_loader = DynamicToolLoader(self.plugin)

        # Initialize skill loader
        config = self.plugin.get_config() if self.plugin else {}
        self._skill_loader = SkillLoader(config)
        await self._skill_loader.initialize()

        # Register skills as tools
        await self._register_skills()

        self._initialized = True
        logger.info(f"工具注册表初始化完成，共 {len(self._builtin_tools)} 个工具")

    async def _register_skills(self):
        """Register loaded skills as tools"""
        if not self._skill_loader:
            return

        skills = self._skill_loader.get_all_skills()
        for skill in skills:
            tool = SkillToToolConverter.convert(skill)
            if tool:
                self._builtin_tools[tool.name] = tool
                print(f"[DEBUG] Registered skill as tool: {tool.name}")

    def get_tool(self, name: str) -> BasePlannerTool | None:
        """Get a tool by name"""
        return self._builtin_tools.get(name)

    def get_all_tools(self) -> list[BasePlannerTool]:
        """Get all registered tools"""
        return list(self._builtin_tools.values())

    def to_openai_format(self) -> list[dict[str, Any]]:
        """Convert all tools to OpenAI function calling format"""
        return [tool.to_openai_format() for tool in self._builtin_tools.values()]

    async def load_dynamic_tools(self) -> list[BasePlannerTool]:
        """Load dynamic tools from MCP servers and plugins"""
        if not self._dynamic_loader:
            return []

        dynamic_tools = await self._dynamic_loader.load_all_tools()

        # Register dynamic tools (they override built-ins with same name)
        for tool in dynamic_tools:
            if tool.name not in self._builtin_tools:
                self._builtin_tools[tool.name] = tool

        return dynamic_tools

    def get_tools_description(self) -> str:
        """Generate a description of all available tools for the LLM"""
        lines = []
        for tool in self._builtin_tools.values():
            lines.append(f"- {tool.name}: {tool.description}")
            params = tool.parameters.get("properties", {})
            for param_name, param_info in params.items():
                required = " (required)" if param_name in tool.parameters.get("required", []) else ""
                lines.append(f"  - {param_name}: {param_info.get('description', '')}{required}")

        return "\n".join(lines)
