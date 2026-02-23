# Dynamic tool loader for planner
# Loads tools from MCP servers and other plugins

from __future__ import annotations

import json
from typing import Any

from . import BasePlannerTool


class DynamicTool(BasePlannerTool):
    """Dynamic tool loaded from external source (MCP, Skill, etc.)"""

    def __init__(self, name: str, description: str, parameters: dict[str, Any], source: str):
        self._name = name
        self._description = description
        self._parameters = parameters
        self._source = source  # "mcp", "skill", "plugin"

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def parameters(self) -> dict[str, Any]:
        return self._parameters

    @property
    def source(self) -> str:
        return self._source

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"error": f"Dynamic tool '{self.name}' from {self.source} needs special execution context"}


class DynamicToolLoader:
    """Load dynamic tools from MCP servers and plugins"""

    def __init__(self, plugin: Any):
        self.plugin = plugin
        self._cached_tools: list[BasePlannerTool] | None = None

    async def load_all_tools(self) -> list[BasePlannerTool]:
        """Load all available tools from LangBot"""
        tools: list[BasePlannerTool] = []

        # Load plugin tools from the runtime
        try:
            plugin_tools = await self._load_plugin_tools()
            tools.extend(plugin_tools)
        except Exception as e:
            print(f"[DEBUG] Failed to load plugin tools: {e}")

        # Load MCP tools
        try:
            mcp_tools = await self._load_mcp_tools()
            tools.extend(mcp_tools)
        except Exception as e:
            print(f"[DEBUG] Failed to load MCP tools: {e}")

        # Load plugin commands (as they are also capabilities)
        try:
            command_tools = await self._load_commands()
            tools.extend(command_tools)
        except Exception as e:
            print(f"[DEBUG] Failed to load commands: {e}")

        self._cached_tools = tools
        return tools

    async def _load_plugin_tools(self) -> list[BasePlannerTool]:
        """Load tools from plugins"""
        tools: list[BasePlannerTool] = []

        try:
            # Get all available tools from the plugin runtime
            result = await self.plugin.plugin_runtime_handler.call_action(
                "list_tools",
                {}
            )
            tool_list = result.get('tools', [])

            for tool in tool_list:
                tool_name = tool.get('metadata', {}).get('name', '')
                if not tool_name:
                    continue

                # Get tool spec
                spec = tool.get('spec', {})
                description = tool.get('metadata', {}).get('description', {}).get('en_US', '')
                if not description:
                    description = spec.get('llm_prompt', '')

                parameters = spec.get('parameters', {})

                if tool_name and parameters:
                    tools.append(DynamicTool(
                        name=tool_name,
                        description=description,
                        parameters=parameters,
                        source="plugin"
                    ))

        except Exception as e:
            print(f"[DEBUG] Error loading plugin tools: {e}")

        return tools

    async def _load_mcp_tools(self) -> list[BasePlannerTool]:
        """Load tools from MCP servers"""
        tools: list[BasePlannerTool] = []

        try:
            # Try to get MCP tools from the tool manager
            # This requires access to the LangBot application
            result = await self.plugin.plugin_runtime_handler.call_action(
                "list_mcp_tools",
                {}
            )
            mcp_tool_list = result.get('tools', [])

            for tool in mcp_tool_list:
                tool_name = tool.get('name', '')
                description = tool.get('description', '')
                parameters = tool.get('parameters', {})

                if tool_name:
                    tools.append(DynamicTool(
                        name=tool_name,
                        description=description,
                        parameters=parameters,
                        source="mcp"
                    ))

        except Exception as e:
            # MCP tools might not be available, which is fine
            pass

        return tools

    def get_tools_by_source(self, source: str) -> list[BasePlannerTool]:
        """Get tools filtered by source"""
        if self._cached_tools is None:
            return []
        return [t for t in self._cached_tools if t.source == source]
