# Browser automation using Playwright
# Provides browser control capabilities for LangTARS

from __future__ import annotations

import asyncio
import base64
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright


class BrowserManager:
    """Manages Playwright browser instances"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._initialized = False

    @property
    def browser_type(self) -> str:
        return self.config.get('browser_type', 'chromium')

    @property
    def headless(self) -> bool:
        return self.config.get('browser_headless', False)

    @property
    def timeout(self) -> int:
        return self.config.get('browser_timeout', 30) * 1000  # Convert to ms

    def _get_browser_channel(self) -> str | None:
        """Get browser channel for installation"""
        # Use system browser if available (no installation needed)
        if self.browser_type == 'chromium':
            return 'chromium'  # Will use system chromium if available
        return None

    async def _try_auto_install(self) -> dict[str, Any]:
        """Try to automatically install Playwright browsers"""
        import subprocess
        import sys

        try:
            # Try to install the browser
            result = subprocess.run(
                [sys.executable, '-m', 'playwright', 'install', self.browser_type],
                capture_output=True,
                text=True,
                timeout=180
            )
            if result.returncode == 0:
                return {'success': True, 'message': f'Installed {self.browser_type}'}
            else:
                return {'success': False, 'error': result.stderr}
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Installation timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def initialize(self) -> dict[str, Any]:
        """Initialize Playwright and launch browser"""
        if self._initialized:
            return {'success': True, 'message': 'Browser already initialized'}

        if not self.config.get('enable_browser', True):
            return {'success': False, 'error': 'Browser automation is disabled'}

        try:
            self._playwright = await async_playwright().start()

            # Try to launch browser
            browser_launch_error = None
            try:
                if self.browser_type == 'firefox':
                    self._browser = await self._playwright.firefox.launch(headless=self.headless)
                elif self.browser_type == 'webkit':
                    self._browser = await self._playwright.webkit.launch(headless=self.headless)
                else:
                    # Default to chromium
                    self._browser = await self._playwright.chromium.launch(headless=self.headless)
            except Exception as e:
                browser_launch_error = str(e)
                # Check if it's a missing browser error
                if 'Executable doesn\'t exist' in browser_launch_error or 'no browser' in browser_launch_error.lower():
                    # Try to auto-install
                    install_result = await self._try_auto_install()
                    if install_result['success']:
                        # Retry launching
                        if self.browser_type == 'firefox':
                            self._browser = await self._playwright.firefox.launch(headless=self.headless)
                        elif self.browser_type == 'webkit':
                            self._browser = await self._playwright.webkit.launch(headless=self.headless)
                        else:
                            self._browser = await self._playwright.chromium.launch(headless=self.headless)
                        browser_launch_error = None
                    else:
                        return {'success': False, 'error': f'Browser not installed. Please run: playwright install {self.browser_type}\n\nError: {browser_launch_error}'}

            if browser_launch_error:
                await self.cleanup()
                return {'success': False, 'error': browser_launch_error}

            # Create context and page
            self._context = await self._browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            self._page = await self._context.new_page()

            self._initialized = True
            return {'success': True, 'message': f'Browser ({self.browser_type}) initialized'}

        except Exception as e:
            await self.cleanup()
            return {'success': False, 'error': str(e)}

    async def cleanup(self) -> None:
        """Cleanup browser resources"""
        if self._page:
            await self._page.close()
            self._page = None
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        self._initialized = False

    async def navigate(self, url: str) -> dict[str, Any]:
        """Navigate to a URL"""
        if not self._initialized or not self._page:
            init_result = await self.initialize()
            if not init_result['success']:
                return init_result

        try:
            # Wait for network idle to ensure dynamic content is loaded
            response = await self._page.goto(url, timeout=self.timeout, wait_until='networkidle')
            return {
                'success': True,
                'url': self._page.url,
                'title': await self._page.title(),
                'status': response.status if response else None
            }
        except Exception as e:
            # Fallback to domcontentloaded if networkidle fails
            try:
                response = await self._page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')
                # Wait a bit for dynamic content
                await asyncio.sleep(2)
                return {
                    'success': True,
                    'url': self._page.url,
                    'title': await self._page.title(),
                    'status': response.status if response else None
                }
            except Exception as e2:
                return {'success': False, 'error': str(e2)}

    async def click(self, selector: str) -> dict[str, Any]:
        """Click an element"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            await self._page.click(selector, timeout=self.timeout)
            return {'success': True, 'selector': selector}
        except Exception as e:
            return {'success': False, 'error': str(e), 'selector': selector}

    async def type_text(self, selector: str, text: str, clear_first: bool = True) -> dict[str, Any]:
        """Type text into an element"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            if clear_first:
                await self._page.fill(selector, '', timeout=self.timeout)
            await self._page.fill(selector, text, timeout=self.timeout)
            return {'success': True, 'selector': selector, 'text': text}
        except Exception as e:
            return {'success': False, 'error': str(e), 'selector': selector}

    async def screenshot(self, path: str | None = None) -> dict[str, Any]:
        """Take a screenshot"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            if path:
                # Save to file
                await self._page.screenshot(path=path, full_page=True)
                return {'success': True, 'path': path}
            else:
                # Return as base64
                screenshot_bytes = await self._page.screenshot(full_page=True)
                base64_data = base64.b64encode(screenshot_bytes).decode('utf-8')
                return {'success': True, 'base64': base64_data}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def get_content(self, selector: str | None = None) -> dict[str, Any]:
        """Get page content or element content"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            if selector:
                element = await self._page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    return {'success': True, 'selector': selector, 'text': text}
                else:
                    return {'success': False, 'error': f'Element not found: {selector}'}
            else:
                # Get full page text
                text = await self._page.evaluate('document.body.innerText')
                return {'success': True, 'text': text}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def wait_for_selector(self, selector: str, timeout: int | None = None) -> dict[str, Any]:
        """Wait for an element to appear"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        wait_timeout = timeout * 1000 if timeout else self.timeout

        try:
            await self._page.wait_for_selector(selector, timeout=wait_timeout)
            return {'success': True, 'selector': selector}
        except Exception as e:
            return {'success': False, 'error': str(e), 'selector': selector}

    async def scroll(self, x: int = 0, y: int = 500) -> dict[str, Any]:
        """Scroll the page"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            await self._page.evaluate(f'window.scrollBy({x}, {y})')
            return {'success': True, 'x': x, 'y': y}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def execute_script(self, script: str) -> dict[str, Any]:
        """Execute JavaScript"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            result = await self._page.evaluate(script)
            return {'success': True, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def new_tab(self, url: str = 'about:blank') -> dict[str, Any]:
        """Create a new tab"""
        if not self._initialized or not self._browser or not self._context:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            new_page = await self._context.new_page()
            if url != 'about:blank':
                await new_page.goto(url, timeout=self.timeout)
            return {'success': True, 'url': new_page.url}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def close_tab(self, target: str = 'current') -> dict[str, Any]:
        """Close a tab"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            if target == 'current':
                # Check if it's the last page
                pages = self._context.pages
                if len(pages) <= 1:
                    return {'success': False, 'error': 'Cannot close the last tab'}
                await self._page.close()
                self._page = pages[0] if pages else None
                return {'success': True}
            else:
                # Close by URL or index (future enhancement)
                return {'success': False, 'error': 'Not implemented'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def get_current_url(self) -> dict[str, Any]:
        """Get current URL"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        return {'success': True, 'url': self._page.url}

    async def reload(self) -> dict[str, Any]:
        """Reload the page"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            await self._page.reload(timeout=self.timeout)
            return {'success': True, 'url': self._page.url}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def go_back(self) -> dict[str, Any]:
        """Go back in history"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            await self._page.go_back(timeout=self.timeout)
            return {'success': True, 'url': self._page.url}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def go_forward(self) -> dict[str, Any]:
        """Go forward in history"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            await self._page.go_forward(timeout=self.timeout)
            return {'success': True, 'url': self._page.url}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def press_key(self, selector: str, key: str) -> dict[str, Any]:
        """Press a key"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            await self._page.press(selector, key, timeout=self.timeout)
            return {'success': True, 'selector': selector, 'key': key}
        except Exception as e:
            return {'success': False, 'error': str(e), 'selector': selector}

    async def select_option(self, selector: str, value: str) -> dict[str, Any]:
        """Select an option in a dropdown"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            await self._page.select_option(selector, value, timeout=self.timeout)
            return {'success': True, 'selector': selector, 'value': value}
        except Exception as e:
            return {'success': False, 'error': str(e), 'selector': selector}

    async def get_attribute(self, selector: str, attribute: str) -> dict[str, Any]:
        """Get an element's attribute"""
        if not self._page:
            return {'success': False, 'error': 'Browser not initialized'}

        try:
            value = await self._page.get_attribute(selector, attribute, timeout=self.timeout)
            return {'success': True, 'selector': selector, 'attribute': attribute, 'value': value}
        except Exception as e:
            return {'success': False, 'error': str(e), 'selector': selector}
