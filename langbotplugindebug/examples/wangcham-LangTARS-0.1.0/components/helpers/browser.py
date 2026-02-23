# Browser Controller - Delegates to BrowserManager for Playwright control

from __future__ import annotations

from typing import Any

from components.tools.browser import BrowserManager


class BrowserController:
    """Controller for Playwright browser automation."""

    def __init__(self, config: dict[str, Any], browser_manager: BrowserManager | None = None):
        self.config = config
        self._browser_manager = browser_manager

    def _get_manager(self) -> BrowserManager:
        if self._browser_manager is None:
            self._browser_manager = BrowserManager(self.config)
        return self._browser_manager

    async def navigate(self, url: str) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().navigate(url)

    async def click(self, selector: str) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().click(selector)

    async def type_text(self, selector: str, text: str, clear_first: bool = True) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().type_text(selector, text, clear_first)

    async def screenshot(self, path: str | None = None) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().screenshot(path)

    async def get_content(self, selector: str | None = None) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().get_content(selector)

    async def wait_for_selector(self, selector: str, timeout: int = 30) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().wait_for_selector(selector, timeout)

    async def scroll(self, x: int = 0, y: int = 500) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().scroll(x, y)

    async def execute_script(self, script: str) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().execute_script(script)

    async def new_tab(self, url: str = "about:blank") -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().new_tab(url)

    async def close_tab(self) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().close_tab()

    async def get_current_url(self) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().get_current_url()

    async def reload(self) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().reload()

    async def press_key(self, selector: str, key: str) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().press_key(selector, key)

    async def select_option(self, selector: str, value: str) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().select_option(selector, value)

    async def get_attribute(self, selector: str, attribute: str) -> dict[str, Any]:
        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}
        return await self._get_manager().get_attribute(selector, attribute)

    async def cleanup(self) -> dict[str, Any]:
        if self._browser_manager:
            await self._browser_manager.cleanup()
            self._browser_manager = None
        return {'success': True, 'message': 'Browser cleaned up'}
