# Network tools for planner
# URL fetching and web scraping

from __future__ import annotations

import aiohttp
from typing import Any

from . import BasePlannerTool


class FetchURLTool(BasePlannerTool):
    """Fetch content from a URL"""

    @property
    def name(self) -> str:
        return "fetch_url"

    @property
    def description(self) -> str:
        return "Fetch content from a URL. Returns the HTML/text content of the webpage."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch content from"
                }
            },
            "required": ["url"]
        }

    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        url = arguments.get('url', '')
        if not url:
            return {"error": "URL is required"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    content = await response.text()
                    # Limit content length to avoid too large responses
                    if len(content) > 10000:
                        content = content[:10000] + "\n... (truncated)"
                    return {
                        "success": True,
                        "url": url,
                        "status_code": response.status,
                        "content": content
                    }
        except Exception as e:
            return {"error": f"Failed to fetch URL: {str(e)}"}
