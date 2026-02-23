# Browser automation tools for planner

from __future__ import annotations

from typing import Any

from . import BasePlannerTool


class BrowserNavigateTool(BasePlannerTool):
    """Navigate to a URL in the browser"""

    @property
    def name(self) -> str:
        return "browser_navigate"

    @property
    def description(self) -> str:
        return "Navigate to a URL in the browser. Use this to open websites. When searching the web, use https://www.bing.com instead of Google."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to navigate to (e.g., 'https://www.bing.com' or 'https://www.bing.com/search?q=your+search+terms')"
                }
            },
            "required": ["url"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_navigate(arguments.get('url', ''))


class BrowserClickTool(BasePlannerTool):
    """Click an element on the page"""

    @property
    def name(self) -> str:
        return "browser_click"

    @property
    def description(self) -> str:
        return "Click an element on the page using a CSS selector or XPath."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector or XPath of the element to click"
                }
            },
            "required": ["selector"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_click(arguments.get('selector', ''))


class BrowserTypeTool(BasePlannerTool):
    """Type text into an element"""

    @property
    def name(self) -> str:
        return "browser_type"

    @property
    def description(self) -> str:
        return "Type text into an input field or element identified by a CSS selector."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector of the input element"
                },
                "text": {
                    "type": "string",
                    "description": "Text to type"
                },
                "clear_first": {
                    "type": "boolean",
                    "description": "Clear the input before typing (default: true)",
                    "default": True
                }
            },
            "required": ["selector", "text"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_type(
            selector=arguments.get('selector', ''),
            text=arguments.get('text', ''),
            clear_first=arguments.get('clear_first', True)
        )


class BrowserScreenshotTool(BasePlannerTool):
    """Take a screenshot of the current page"""

    @property
    def name(self) -> str:
        return "browser_screenshot"

    @property
    def description(self) -> str:
        return "Take a screenshot of the current page. Returns base64 encoded image."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Optional path to save screenshot (if not provided, returns base64)"
                }
            }
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_screenshot(arguments.get('path'))


class BrowserGetContentTool(BasePlannerTool):
    """Get page content or element content"""

    @property
    def name(self) -> str:
        return "browser_get_content"

    @property
    def description(self) -> str:
        return "Get the text content of the page or a specific element."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "Optional CSS selector to get specific element content (if not provided, gets full page text)"
                }
            }
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_get_content(arguments.get('selector'))


class BrowserWaitTool(BasePlannerTool):
    """Wait for an element to appear"""

    @property
    def name(self) -> str:
        return "browser_wait"

    @property
    def description(self) -> str:
        return "Wait for an element to appear on the page."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector of the element to wait for"
                },
                "timeout": {
                    "type": "number",
                    "description": "Timeout in seconds (default: 30)",
                    "default": 30
                }
            },
            "required": ["selector"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_wait(
            selector=arguments.get('selector', ''),
            timeout=arguments.get('timeout', 30)
        )


class BrowserScrollTool(BasePlannerTool):
    """Scroll the page"""

    @property
    def name(self) -> str:
        return "browser_scroll"

    @property
    def description(self) -> str:
        return "Scroll the page horizontally or vertically."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "x": {
                    "type": "number",
                    "description": "Horizontal scroll amount (default: 0)",
                    "default": 0
                },
                "y": {
                    "type": "number",
                    "description": "Vertical scroll amount (default: 500)",
                    "default": 500
                }
            }
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_scroll(
            x=arguments.get('x', 0),
            y=arguments.get('y', 500)
        )


class BrowserExecuteScriptTool(BasePlannerTool):
    """Execute JavaScript"""

    @property
    def name(self) -> str:
        return "browser_execute_script"

    @property
    def description(self) -> str:
        return "Execute arbitrary JavaScript code in the browser context."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "JavaScript code to execute"
                }
            },
            "required": ["script"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_execute_script(arguments.get('script', ''))


class BrowserNewTabTool(BasePlannerTool):
    """Create a new browser tab"""

    @property
    def name(self) -> str:
        return "browser_new_tab"

    @property
    def description(self) -> str:
        return "Open a new browser tab with an optional URL."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to open in new tab (default: about:blank)",
                    "default": "about:blank"
                }
            }
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_new_tab(arguments.get('url', 'about:blank'))


class BrowserCloseTabTool(BasePlannerTool):
    """Close the current browser tab"""

    @property
    def name(self) -> str:
        return "browser_close_tab"

    @property
    def description(self) -> str:
        return "Close the current browser tab."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_close_tab()


class BrowserGetUrlTool(BasePlannerTool):
    """Get current URL"""

    @property
    def name(self) -> str:
        return "browser_get_url"

    @property
    def description(self) -> str:
        return "Get the current URL of the browser."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_get_url()


class BrowserReloadTool(BasePlannerTool):
    """Reload the current page"""

    @property
    def name(self) -> str:
        return "browser_reload"

    @property
    def description(self) -> str:
        return "Reload the current page."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_reload()


class BrowserPressKeyTool(BasePlannerTool):
    """Press a keyboard key"""

    @property
    def name(self) -> str:
        return "browser_press"

    @property
    def description(self) -> str:
        return "Press a keyboard key on an element (e.g., Enter, Tab, Escape)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector of the element (optional, if not provided presses on page)"
                },
                "key": {
                    "type": "string",
                    "description": "Key to press (e.g., 'Enter', 'Tab', 'Escape', 'ArrowDown')"
                }
            },
            "required": ["key"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_press_key(
            arguments.get('selector', ''),
            arguments.get('key', '')
        )


class BrowserSelectOptionTool(BasePlannerTool):
    """Select an option in a dropdown"""

    @property
    def name(self) -> str:
        return "browser_select"

    @property
    def description(self) -> str:
        return "Select an option in a dropdown (select element) by value."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector of the select element"
                },
                "value": {
                    "type": "string",
                    "description": "Value of the option to select"
                }
            },
            "required": ["selector", "value"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_select_option(
            arguments.get('selector', ''),
            arguments.get('value', '')
        )


class BrowserGetAttributeTool(BasePlannerTool):
    """Get an element's attribute"""

    @property
    def name(self) -> str:
        return "browser_get_attribute"

    @property
    def description(self) -> str:
        return "Get an attribute value from an element."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector of the element"
                },
                "attribute": {
                    "type": "string",
                    "description": "Name of the attribute to get"
                }
            },
            "required": ["selector", "attribute"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.browser_get_attribute(
            arguments.get('selector', ''),
            arguments.get('attribute', '')
        )


# ========== Safari Native Browser Tools ==========
# Control the actual Safari app on Mac


class SafariOpenTool(BasePlannerTool):
    """Open Safari browser"""

    @property
    def name(self) -> str:
        return "safari_open"

    @property
    def description(self) -> str:
        return "Open Safari browser. Use when user explicitly says 'Safari'."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Optional URL to open in Safari"
                }
            }
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.safari_open(arguments.get('url'))


class SafariNavigateTool(BasePlannerTool):
    """Navigate to URL in Safari"""

    @property
    def name(self) -> str:
        return "safari_navigate"

    @property
    def description(self) -> str:
        return "Navigate to a URL in Safari. Use when user explicitly wants to use Safari."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to navigate to (e.g., 'https://github.com')"
                }
            },
            "required": ["url"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.safari_navigate(arguments.get('url', ''))


class SafariGetContentTool(BasePlannerTool):
    """Get content from Safari"""

    @property
    def name(self) -> str:
        return "safari_get_content"

    @property
    def description(self) -> str:
        return "Get the current page content from Safari."

    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.safari_get_content()


class SafariClickTool(BasePlannerTool):
    """Click element in Safari"""

    @property
    def name(self) -> str:
        return "safari_click"

    @property
    def description(self) -> str:
        return "Click an element in Safari using CSS selector."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector of the element to click"
                }
            },
            "required": ["selector"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.safari_click(arguments.get('selector', ''))


class SafariTypeTool(BasePlannerTool):
    """Type text in Safari"""

    @property
    def name(self) -> str:
        return "safari_type"

    @property
    def description(self) -> str:
        return "Type text into an input field in Safari."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector of the input element"
                },
                "text": {
                    "type": "string",
                    "description": "Text to type"
                }
            },
            "required": ["selector", "text"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.safari_type(
            arguments.get('selector', ''),
            arguments.get('text', '')
        )


class SafariPressKeyTool(BasePlannerTool):
    """Press key in Safari"""

    @property
    def name(self) -> str:
        return "safari_press"

    @property
    def description(self) -> str:
        return "Press a keyboard key in Safari."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Key to press (e.g., 'Enter', 'Tab')"
                }
            },
            "required": ["key"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.safari_press_key(arguments.get('key', ''))


# ========== Chrome Native Browser Tools ==========
# Control the actual Google Chrome app on Mac


class ChromeOpenTool(BasePlannerTool):
    """Open Google Chrome browser"""

    @property
    def name(self) -> str:
        return "chrome_open"

    @property
    def description(self) -> str:
        return "Open Google Chrome browser. Use when user explicitly says 'Chrome'."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Optional URL to open in Chrome"
                }
            }
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.chrome_open(arguments.get('url'))


class ChromeNavigateTool(BasePlannerTool):
    """Navigate to URL in Chrome"""

    @property
    def name(self) -> str:
        return "chrome_navigate"

    @property
    def description(self) -> str:
        return "Navigate to a URL in Google Chrome. Use when user explicitly wants to use Chrome."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to navigate to (e.g., 'https://github.com')"
                }
            },
            "required": ["url"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.chrome_navigate(arguments.get('url', ''))


class ChromeGetContentTool(BasePlannerTool):
    """Get content from Chrome"""

    @property
    def name(self) -> str:
        return "chrome_get_content"

    @property
    def description(self) -> str:
        return "Get the current page content from Google Chrome."

    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.chrome_get_content()


class ChromeClickTool(BasePlannerTool):
    """Click element in Chrome"""

    @property
    def name(self) -> str:
        return "chrome_click"

    @property
    def description(self) -> str:
        return "Click an element in Chrome using CSS selector."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector of the element to click"
                }
            },
            "required": ["selector"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.chrome_click(arguments.get('selector', ''))


class ChromeTypeTool(BasePlannerTool):
    """Type text in Chrome"""

    @property
    def name(self) -> str:
        return "chrome_type"

    @property
    def description(self) -> str:
        return "Type text into an input field in Chrome."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector of the input element"
                },
                "text": {
                    "type": "string",
                    "description": "Text to type"
                }
            },
            "required": ["selector", "text"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.chrome_type(
            arguments.get('selector', ''),
            arguments.get('text', '')
        )


class ChromePressKeyTool(BasePlannerTool):
    """Press key in Chrome"""

    @property
    def name(self) -> str:
        return "chrome_press"

    @property
    def description(self) -> str:
        return "Press a keyboard key in Chrome."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Key to press (e.g., 'Enter', 'Tab')"
                }
            },
            "required": ["key"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        return await helper_plugin.chrome_press_key(arguments.get('key', ''))
