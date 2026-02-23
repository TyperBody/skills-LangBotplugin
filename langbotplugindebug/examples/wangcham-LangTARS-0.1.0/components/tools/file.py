# LangTARS File Tool
# File operations tool for LLM

from __future__ import annotations

from typing import Any

from langbot_plugin.api.definition.components.tool.tool import Tool
from langbot_plugin.api.entities.builtin.provider import session as provider_session


class FileTool(Tool):
    """File operations tool for LLM"""

    __kind__ = "Tool"

    async def call(
        self,
        params: dict[str, Any],
        session: provider_session.Session,
        query_id: int,
    ) -> str:
        """Perform file operations on this Mac."""
        from main import LangTARS
        plugin = LangTARS()
        await plugin.initialize()

        action = params.get('action', 'read')

        if action == 'read':
            path = params.get('path', '')
            result = await plugin.read_file(path)
        elif action == 'write':
            path = params.get('path', '')
            content = params.get('content', '')
            mode = params.get('mode', 'w')
            result = await plugin.write_file(path, content, mode)
        elif action == 'list':
            path = params.get('path', '.')
            show_hidden = params.get('show_hidden', False)
            result = await plugin.list_directory(path, show_hidden)
        elif action == 'search':
            pattern = params.get('pattern', '')
            path = params.get('path', '.')
            recursive = params.get('recursive', True)
            result = await plugin.search_files(pattern, path, recursive)
        else:
            return f"Unknown action: {action}. Supported actions: read, write, list, search"

        if result['success']:
            if 'content' in result:
                return result.get('content', '(empty)')
            elif 'items' in result:
                # List action
                items = result.get('items', [])
                if not items:
                    return f"Directory is empty: {result.get('path', '')}"
                output = [f"Contents of {result.get('path', '')}:"]
                for item in items:
                    icon = '📁' if item['type'] == 'directory' else '📄'
                    output.append(f"  {icon} {item['name']}")
                return '\n'.join(output)
            elif 'files' in result:
                # Search action
                files = result.get('files', [])
                if not files:
                    return f"No files found matching '{params.get('pattern', '')}'"
                return f"Found {result.get('count', len(files))} files:\n" + '\n'.join(f"  {f}" for f in files[:20])
            else:
                return result.get('message', 'Success')
        else:
            return f"Failed: {result.get('error', 'Unknown error')}"
