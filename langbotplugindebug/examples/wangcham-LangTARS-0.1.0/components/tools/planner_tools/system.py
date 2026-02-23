# System tools for planner
# Shell, file, process, app management tools

from __future__ import annotations

from typing import Any

from . import BasePlannerTool


class ShellTool(BasePlannerTool):
    """Execute shell commands"""

    @property
    def name(self) -> str:
        return "shell"

    @property
    def description(self) -> str:
        return "Execute a shell command on this Mac. Use this for running terminal commands like ls, ps, grep, curl, etc."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute"
                },
                "timeout": {
                    "type": "number",
                    "description": "Timeout in seconds (default: 30)",
                    "default": 30
                }
            },
            "required": ["command"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.run_shell(
            command=arguments.get('command', ''),
            timeout=arguments.get('timeout', 30)
        )


class ListProcessesTool(BasePlannerTool):
    """List running processes"""

    @property
    def name(self) -> str:
        return "list_processes"

    @property
    def description(self) -> str:
        return "List running processes on this Mac."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "description": "Filter processes by name (optional)"
                },
                "limit": {
                    "type": "number",
                    "description": "Maximum number of processes to return (default: 20)",
                    "default": 20
                }
            }
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.list_processes(
            filter_pattern=arguments.get('filter'),
            limit=arguments.get('limit', 20)
        )


class KillProcessTool(BasePlannerTool):
    """Kill a process"""

    @property
    def name(self) -> str:
        return "kill_process"

    @property
    def description(self) -> str:
        return "Kill a process by name or PID."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "Process name or PID to kill"
                },
                "force": {
                    "type": "boolean",
                    "description": "Force kill (default: false)",
                    "default": False
                }
            },
            "required": ["target"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.kill_process(
            target=arguments.get('target', ''),
            force=arguments.get('force', False)
        )


class OpenAppTool(BasePlannerTool):
    """Open an application or URL"""

    @property
    def name(self) -> str:
        return "open_app"

    @property
    def description(self) -> str:
        return "Open an application or URL on this Mac."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "Application name (e.g., 'Safari') or URL (e.g., 'https://...')"
                }
            },
            "required": ["target"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        target = arguments.get('target', '')
        is_url = target.startswith(('http://', 'https://', 'mailto:', 'tel:'))
        return await helper_plugin.open_app(
            app_name=None if is_url else target,
            url=target if is_url else None
        )


class CloseAppTool(BasePlannerTool):
    """Close an application"""

    @property
    def name(self) -> str:
        return "close_app"

    @property
    def description(self) -> str:
        return "Close an application by name."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "The name of the application to close"
                },
                "force": {
                    "type": "boolean",
                    "description": "Force quit (default: false)",
                    "default": False
                }
            },
            "required": ["app_name"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.close_app(
            app_name=arguments.get('app_name', ''),
            force=arguments.get('force', False)
        )


class ListAppsTool(BasePlannerTool):
    """List running applications"""

    @property
    def name(self) -> str:
        return "list_apps"

    @property
    def description(self) -> str:
        return "List running applications on this Mac."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "number",
                    "description": "Maximum number of apps to return (default: 20)",
                    "default": 20
                }
            }
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.list_apps(limit=arguments.get('limit', 20))


class GetSystemInfoTool(BasePlannerTool):
    """Get system information"""

    @property
    def name(self) -> str:
        return "get_system_info"

    @property
    def description(self) -> str:
        return "Get system information about this Mac."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.get_system_info()


class AppleScriptTool(BasePlannerTool):
    """Execute AppleScript to control macOS applications"""

    @property
    def name(self) -> str:
        return "applescript"

    @property
    def description(self) -> str:
        return """Execute AppleScript to control macOS applications. Use this to:
- Control applications (open, close, activate)
- Interact with UI elements (click, type, select)
- Automate browser operations in Chrome/Safari
- Control system settings
- Manipulate files and folders

Example for Chrome search:
tell application "Google Chrome"
    activate
    tell window 1
        set searchURL to "https://www.google.com/search?q=your+search+terms"
        set URL of active tab to searchURL
    end tell
end tell

Example for clicking UI element:
tell application "System Events"
    keystroke "hello"
end tell"""

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "The AppleScript script to execute"
                }
            },
            "required": ["script"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        script = arguments.get('script', '')
        if not script:
            return {"success": False, "error": "No script provided"}

        # Basic safety check - block potentially dangerous commands
        dangerous_patterns = ['rm -rf', 'format:', 'diskutil erase', 'do shell script "rm']
        for pattern in dangerous_patterns:
            if pattern.lower() in script.lower():
                return {"success": False, "error": f"Potentially dangerous command blocked: {pattern}"}

        return await helper_plugin.run_applescript(script)
