# File tools for planner
# File read, write, list operations

from __future__ import annotations

from typing import Any

from . import BasePlannerTool


class ReadFileTool(BasePlannerTool):
    """Read file content"""

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the content of a file. Returns the file content or error message."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to read"
                }
            },
            "required": ["path"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.read_file(arguments.get('path', ''))


class WriteFileTool(BasePlannerTool):
    """Write content to a file"""

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file. Creates new file or overwrites existing file."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                }
            },
            "required": ["path", "content"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.write_file(
            path=arguments.get('path', ''),
            content=arguments.get('content', '')
        )


class ListDirectoryTool(BasePlannerTool):
    """List directory contents"""

    @property
    def name(self) -> str:
        return "list_directory"

    @property
    def description(self) -> str:
        return "List the contents of a directory."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the directory (default: current directory)",
                    "default": "."
                },
                "show_hidden": {
                    "type": "boolean",
                    "description": "Show hidden files (default: false)",
                    "default": False
                }
            }
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.list_directory(
            path=arguments.get('path', '.'),
            show_hidden=arguments.get('show_hidden', False)
        )


class SearchFilesTool(BasePlannerTool):
    """Search for files"""

    @property
    def name(self) -> str:
        return "search_files"

    @property
    def description(self) -> str:
        return "Search for files matching a pattern."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "File pattern to search for (e.g., '*.py')"
                },
                "path": {
                    "type": "string",
                    "description": "Directory to search in (default: current)",
                    "default": "."
                }
            },
            "required": ["pattern"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.search_files(
            pattern=arguments.get('pattern', ''),
            path=arguments.get('path', '.')
        )
