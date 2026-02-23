# Plugin Helper - Singleton wrapper for LangTARS plugin functionality
# Provides shared access to plugin methods without repeated initialization

from __future__ import annotations

import asyncio
import platform
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from main import LangTARS


class PluginHelper:
    """Singleton helper for accessing LangTARS plugin functionality."""

    _instance: "PluginHelper | None" = None
    _plugin: "LangTARS | None" = None
    _initialized: bool = False

    def __new__(cls) -> "PluginHelper":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def get_instance(cls) -> "PluginHelper":
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        if not cls._initialized:
            await cls._instance._initialize()
        return cls._instance

    async def _initialize(self) -> None:
        """Initialize the plugin instance."""
        if self._initialized:
            return

        from main import LangTARS
        self._plugin = LangTARS()
        await self._plugin.initialize()
        self._initialized = True

    @property
    def plugin(self) -> LangTARS:
        """Get the underlying plugin instance."""
        return self._plugin

    @property
    def config(self) -> dict[str, Any]:
        """Get plugin config."""
        return self._plugin.config if self._plugin else {}

    # ========== Shell Execution ==========

    async def run_shell(
        self,
        command: str,
        timeout: int = 30,
        working_dir: str | None = None,
    ) -> dict[str, Any]:
        """Execute a shell command safely."""
        return await self._plugin.run_shell(command, timeout, working_dir)

    # ========== Process Management ==========

    async def list_processes(self, filter_pattern: str | None = None, limit: int = 20) -> dict[str, Any]:
        """List running processes."""
        return await self._plugin.list_processes(filter_pattern, limit)

    async def kill_process(self, target: str, force: bool = False) -> dict[str, Any]:
        """Kill a process by name or PID."""
        return await self._plugin.kill_process(target, force)

    # ========== File Operations ==========

    async def list_directory(self, path: str = ".", show_hidden: bool = False) -> dict[str, Any]:
        """List directory contents."""
        return await self._plugin.list_directory(path, show_hidden)

    async def read_file(self, path: str) -> dict[str, Any]:
        """Read file content."""
        return await self._plugin.read_file(path)

    async def write_file(self, path: str, content: str, _mode: str = "w") -> dict[str, Any]:
        """Write content to a file."""
        return await self._plugin.write_file(path, content, _mode)

    async def search_files(self, pattern: str, path: str = ".", recursive: bool = True) -> dict[str, Any]:
        """Search for files matching a pattern."""
        return await self._plugin.search_files(pattern, path, recursive)

    # ========== App Control ==========

    async def open_app(self, app_name: str | None = None, url: str | None = None) -> dict[str, Any]:
        """Open an application or URL."""
        return await self._plugin.open_app(app_name, url)

    async def close_app(self, app_name: str, force: bool = False) -> dict[str, Any]:
        """Close an application."""
        return await self._plugin.close_app(app_name, force)

    async def list_apps(self, limit: int = 20) -> dict[str, Any]:
        """List running applications."""
        return await self._plugin.list_apps(limit)

    # ========== System Info ==========

    async def get_system_info(self) -> dict[str, Any]:
        """Get system information."""
        return await self._plugin.get_system_info()

    # ========== Browser Control (Playwright) ==========

    async def browser_navigate(self, url: str) -> dict[str, Any]:
        """Navigate to a URL."""
        return await self._plugin.browser_navigate(url)

    async def browser_click(self, selector: str) -> dict[str, Any]:
        """Click an element."""
        return await self._plugin.browser_click(selector)

    async def browser_type(self, selector: str, text: str, clear_first: bool = True) -> dict[str, Any]:
        """Type text into an element."""
        return await self._plugin.browser_type(selector, text, clear_first)

    async def browser_screenshot(self, path: str | None = None) -> dict[str, Any]:
        """Take a screenshot."""
        return await self._plugin.browser_screenshot(path)

    async def browser_get_content(self, selector: str | None = None) -> dict[str, Any]:
        """Get page content."""
        return await self._plugin.browser_get_content(selector)

    async def browser_wait(self, selector: str, timeout: int = 30) -> dict[str, Any]:
        """Wait for element."""
        return await self._plugin.browser_wait(selector, timeout)

    async def browser_scroll(self, x: int = 0, y: int = 500) -> dict[str, Any]:
        """Scroll the page."""
        return await self._plugin.browser_scroll(x, y)

    async def browser_execute_script(self, script: str) -> dict[str, Any]:
        """Execute JavaScript."""
        return await self._plugin.browser_execute_script(script)

    async def browser_new_tab(self, url: str = "about:blank") -> dict[str, Any]:
        """Create new tab."""
        return await self._plugin.browser_new_tab(url)

    async def browser_close_tab(self) -> dict[str, Any]:
        """Close current tab."""
        return await self._plugin.browser_close_tab()

    async def browser_get_url(self) -> dict[str, Any]:
        """Get current URL."""
        return await self._plugin.browser_get_url()

    async def browser_reload(self) -> dict[str, Any]:
        """Reload page."""
        return await self._plugin.browser_reload()

    async def browser_press_key(self, selector: str, key: str) -> dict[str, Any]:
        """Press a key."""
        return await self._plugin.browser_press_key(selector, key)

    async def browser_select_option(self, selector: str, value: str) -> dict[str, Any]:
        """Select option in dropdown."""
        return await self._plugin.browser_select_option(selector, value)

    async def browser_get_attribute(self, selector: str, attribute: str) -> dict[str, Any]:
        """Get element attribute."""
        return await self._plugin.browser_get_attribute(selector, attribute)

    async def browser_cleanup(self) -> dict[str, Any]:
        """Cleanup browser resources."""
        return await self._plugin.browser_cleanup()

    # ========== Safari Control ==========

    async def safari_open(self, url: str | None = None) -> dict[str, Any]:
        """Open Safari (optionally with URL)."""
        return await self._plugin.safari_open(url)

    async def safari_navigate(self, url: str) -> dict[str, Any]:
        """Navigate to URL in Safari."""
        return await self._plugin.safari_navigate(url)

    async def safari_get_content(self) -> dict[str, Any]:
        """Get content from Safari."""
        return await self._plugin.safari_get_content()

    async def safari_click(self, selector: str) -> dict[str, Any]:
        """Click element in Safari."""
        return await self._plugin.safari_click(selector)

    async def safari_type(self, selector: str, text: str) -> dict[str, Any]:
        """Type text into element in Safari."""
        return await self._plugin.safari_type(selector, text)

    async def safari_press_key(self, key: str) -> dict[str, Any]:
        """Press key in Safari."""
        return await self._plugin.safari_press_key(key)

    # ========== Chrome Control ==========

    async def chrome_open(self, url: str | None = None) -> dict[str, Any]:
        """Open Chrome (optionally with URL)."""
        return await self._plugin.chrome_open(url)

    async def chrome_navigate(self, url: str) -> dict[str, Any]:
        """Navigate to URL in Chrome."""
        return await self._plugin.chrome_navigate(url)

    async def chrome_get_content(self) -> dict[str, Any]:
        """Get content from Chrome."""
        return await self._plugin.chrome_get_content()

    async def chrome_click(self, selector: str) -> dict[str, Any]:
        """Click element in Chrome."""
        return await self._plugin.chrome_click(selector)

    async def chrome_type(self, selector: str, text: str) -> dict[str, Any]:
        """Type text into element in Chrome."""
        return await self._plugin.chrome_type(selector, text)

    async def chrome_press_key(self, key: str) -> dict[str, Any]:
        """Press key in Chrome."""
        return await self._plugin.chrome_press_key(key)

    # ========== AppleScript ==========

    async def run_applescript(self, script: str) -> dict[str, Any]:
        """Execute an AppleScript script."""
        return await self._plugin.run_applescript(script)

    # ========== Permission Check ==========

    async def check_permissions(self) -> dict[str, Any]:
        """Check if required permissions are granted."""
        return await self._plugin.check_permissions()

    def get_permission_instructions(self) -> str:
        """Get instructions for granting permissions."""
        return self._plugin.get_permission_instructions()


# Convenience function for easy access
async def get_helper() -> PluginHelper:
    """Get the singleton PluginHelper instance."""
    return await PluginHelper.get_instance()
