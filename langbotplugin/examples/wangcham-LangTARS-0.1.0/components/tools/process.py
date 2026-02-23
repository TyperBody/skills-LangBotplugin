# LangTARS Process Tool
# Process management tool for LLM

from __future__ import annotations

from typing import Any

from langbot_plugin.api.definition.components.tool.tool import Tool
from langbot_plugin.api.entities.builtin.provider import session as provider_session


class ProcessTool(Tool):
    """Process management tool for LLM"""

    __kind__ = "Tool"

    async def call(
        self,
        params: dict[str, Any],
        session: provider_session.Session,
        query_id: int,
    ) -> str:
        """Manage processes on this Mac."""
        from main import LangTARS
        plugin = LangTARS()
        await plugin.initialize()

        action = params.get('action', 'list')

        if action == 'list':
            filter_pattern = params.get('filter')
            limit = params.get('limit', 20)
            result = await plugin.list_processes(filter_pattern, limit)
        elif action == 'kill':
            target = params.get('target', '')
            signal = params.get('signal', 'TERM')
            force = params.get('force', False)
            result = await plugin.kill_process(target, signal, force)
        else:
            return f"Unknown action: {action}. Supported actions: list, kill"

        if result['success']:
            if 'processes' in result:
                # List action
                processes = result.get('processes', [])
                if not processes:
                    return "No processes found."
                output = ["Processes:"]
                for p in processes[:15]:
                    output.append(f"  {p.get('pid', '?')} {p.get('cpu', '?')}% {p.get('mem', '?')}% {p.get('command', '?')[:40]}")
                return '\n'.join(output)
            else:
                # Kill action
                return result.get('message', 'Success')
        else:
            return f"Failed: {result.get('error', 'Unknown error')}"
