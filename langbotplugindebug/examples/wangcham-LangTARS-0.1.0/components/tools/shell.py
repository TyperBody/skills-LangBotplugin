# LangTARS Shell Tool
# Shell command execution tool for LLM

from __future__ import annotations

from typing import Any

from langbot_plugin.api.definition.components.tool.tool import Tool
from langbot_plugin.api.entities.builtin.provider import session as provider_session


class ShellTool(Tool):
    """Shell command execution tool for LLM"""

    __kind__ = "Tool"

    async def call(
        self,
        params: dict[str, Any],
        session: provider_session.Session,
        query_id: int,
    ) -> str:
        """Execute a shell command safely."""
        command = params.get('command', '')
        timeout = params.get('timeout', 30)
        working_dir = params.get('working_dir')

        # Import main module to use plugin methods
        from main import LangTARS
        plugin = LangTARS()
        await plugin.initialize()

        result = await plugin.run_shell(command, timeout, working_dir)

        if result['success']:
            output = result.get('stdout', '') or result.get('stderr', '')
            return f"Command executed successfully:\n{output}"
        else:
            return f"Command failed: {result.get('error', 'Unknown error')}\nstderr: {result.get('stderr', '')}"
