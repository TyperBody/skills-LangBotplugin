# LangTARS App Tool
# Application control tool for LLM

from __future__ import annotations

from typing import Any

from langbot_plugin.api.definition.components.tool.tool import Tool
from langbot_plugin.api.entities.builtin.provider import session as provider_session


class AppTool(Tool):
    """Application control tool for LLM"""

    __kind__ = "Tool"

    async def call(
        self,
        params: dict[str, Any],
        session: provider_session.Session,
        query_id: int,
    ) -> str:
        """Control applications on this Mac."""
        from main import LangTARS
        plugin = LangTARS()
        await plugin.initialize()

        action = params.get('action', 'open')

        if action == 'open':
            app_name = params.get('app_name', '')
            url = params.get('url')
            result = await plugin.open_app(app_name, url)
        elif action == 'close':
            app_name = params.get('app_name', '')
            force = params.get('force', False)
            result = await plugin.close_app(app_name, force)
        elif action == 'list':
            limit = params.get('limit', 20)
            result = await plugin.list_apps(limit)
        elif action == 'frontmost':
            result = await plugin.get_frontmost_app()
        else:
            return f"Unknown action: {action}. Supported actions: open, close, list, frontmost"

        if result['success']:
            if 'apps' in result:
                return f"Running applications:\n" + '\n'.join(f"  • {app}" for app in result.get('apps', []))
            elif 'app_name' in result:
                return f"Frontmost application: {result.get('app_name', 'Unknown')}"
            else:
                return result.get('message', 'Success')
        else:
            return f"Failed: {result.get('error', 'Unknown error')}"
