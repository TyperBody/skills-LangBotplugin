# LangTARS Command Handler
# Handle direct commands like /shell, /ps, /ls, etc.

from __future__ import annotations

import logging
from typing import Any, AsyncGenerator

from langbot_plugin.api.definition.components.command.command import Command, Subcommand
from langbot_plugin.api.entities.builtin.command.context import ExecuteContext, CommandReturn
from langbot_plugin.api.entities.builtin.platform.message import MessageChain, Plain

from components.helpers.plugin import get_helper

logger = logging.getLogger(__name__)


class LangTARS(Command):
    """LangTARS Command Handler"""

    async def initialize(self):
        await super().initialize()

        # Register subcommands with class methods (unbound)
        self.registered_subcommands["shell"] = Subcommand(
            subcommand=LanTARSCommand.shell,
            help="Execute a shell command",
            usage="!tars shell <command>",
            aliases=["sh", "exec"],
        )

        self.registered_subcommands["ps"] = Subcommand(
            subcommand=LanTARSCommand.ps,
            help="List running processes",
            usage="!tars ps [filter] [limit]",
            aliases=["processes", "process"],
        )

        self.registered_subcommands["kill"] = Subcommand(
            subcommand=LanTARSCommand.kill,
            help="Kill a process by name or PID",
            usage="!tars kill <name|PID> [-f]",
            aliases=[],
        )

        self.registered_subcommands["ls"] = Subcommand(
            subcommand=LanTARSCommand.ls,
            help="List directory contents",
            usage="!tars ls [path] [-a]",
            aliases=["list", "dir"],
        )

        self.registered_subcommands["cat"] = Subcommand(
            subcommand=LanTARSCommand.cat,
            help="Read file content",
            usage="!tars cat <path>",
            aliases=["read", "view"],
        )

        self.registered_subcommands["write"] = Subcommand(
            subcommand=LanTARSCommand.write,
            help="Write content to a file",
            usage="!tars write <path> <content>",
            aliases=["save", "create"],
        )

        self.registered_subcommands["open"] = Subcommand(
            subcommand=LanTARSCommand.open,
            help="Open an application or URL",
            usage="!tars open <app|url>",
            aliases=["launch", "start"],
        )

        self.registered_subcommands["close"] = Subcommand(
            subcommand=LanTARSCommand.close,
            help="Close an application",
            usage="!tars close <app_name> [-f]",
            aliases=["quit"],
        )

        self.registered_subcommands["stop"] = Subcommand(
            subcommand=LanTARSCommand.stop,
            help="Stop the current running task",
            usage="!tars stop",
            aliases=["pause", "cancel"],
        )

        self.registered_subcommands["top"] = Subcommand(
            subcommand=LanTARSCommand.top,
            help="Show running applications",
            usage="!tars top",
            aliases=["apps"],
        )

        self.registered_subcommands["info"] = Subcommand(
            subcommand=LanTARSCommand.info,
            help="Show system information",
            usage="!tars info",
            aliases=["system", "status"],
        )

        self.registered_subcommands["search"] = Subcommand(
            subcommand=LanTARSCommand.search,
            help="Search for files",
            usage="!tars search <pattern> [path]",
            aliases=["find"],
        )

        self.registered_subcommands["auto"] = Subcommand(
            subcommand=LanTARSCommand.auto,
            help="Autonomous task planning (AI-powered)",
            usage="!tars auto <task description>",
            aliases=["plan", "run"],
        )

        # Wildcard subcommand to handle no subcommand
        self.registered_subcommands["*"] = Subcommand(
            subcommand=LanTARSCommand.default,
            help="Show help or handle default",
            usage="!tars help",
            aliases=[],
        )


# Separate class for command handlers - uses singleton PluginHelper
class LanTARSCommand:
    """Static command handlers that delegate to shared PluginHelper."""

    @staticmethod
    async def shell(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle shell command execution."""
        params = context.crt_params
        if not params:
            yield CommandReturn(text="Usage: !tars shell <command>")
            return

        command = " ".join(params)
        yield CommandReturn(text=f"Executing: `{command}`\n\n")

        helper = await get_helper()
        result = await helper.run_shell(command)

        if result["success"]:
            output = result.get("stdout", "") or result.get("stderr", "")
            yield CommandReturn(text=f"Command executed successfully\n\n```\n{output}\n```")
        else:
            yield CommandReturn(text=f"Command failed: {result.get('error', 'Unknown error')}")

    @staticmethod
    async def ps(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle process listing."""
        params = context.crt_params
        filter_pattern = params[0] if params else None
        limit = 20

        helper = await get_helper()
        result = await helper.list_processes(filter_pattern, limit)

        if result["success"]:
            processes = result.get("processes", [])
            if not processes:
                yield CommandReturn(text="No processes found.")
                return

            lines = ["**Processes:**\n"]
            lines.append(f"{'PID':<8} {'CPU%':<8} {'MEM%':<8} {'COMMAND'}")
            lines.append("-" * 60)
            for p in processes[:15]:
                cmd = p.get("command", "")[:30]
                lines.append(f"{p.get('pid',''):<8} {p.get('cpu',''):<8} {p.get('mem',''):<8} {cmd}")

            if len(processes) > 15:
                lines.append(f"... and {len(processes) - 15} more")

            yield CommandReturn(text="\n".join(lines))
        else:
            yield CommandReturn(text=f"Failed: {result.get('error', 'Unknown error')}")

    @staticmethod
    async def kill(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle process killing."""
        params = context.crt_params
        if not params:
            yield CommandReturn(text="Usage: !tars kill <name|PID> [-f]")
            return

        target = params[0]
        force = "-f" in params

        helper = await get_helper()
        result = await helper.kill_process(target, force=force)

        if result["success"]:
            yield CommandReturn(text=f"Process terminated: {target}")
        else:
            yield CommandReturn(text=f"Failed: {result.get('error', 'Unknown error')}")

    @staticmethod
    async def ls(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle directory listing."""
        params = context.crt_params
        path = params[0] if params else "."
        show_hidden = "-a" in params

        helper = await get_helper()
        result = await helper.list_directory(path, show_hidden)

        if result["success"]:
            items = result.get("items", [])
            if not items:
                yield CommandReturn(text=f"Directory is empty: {result.get('path', path)}")
                return

            lines = [f"**Contents of `{result.get('path', path)}`**\n"]
            for item in items:
                icon = "📁" if item["type"] == "directory" else "📄"
                size_str = f" ({item['size']} bytes)" if item["size"] > 0 else ""
                lines.append(f"{icon} {item['name']}{size_str}")

            lines.append(f"\nTotal: {result.get('count', 0)} items")
            yield CommandReturn(text="\n".join(lines))
        else:
            yield CommandReturn(text=f"Failed: {result.get('error', 'Access denied')}")

    @staticmethod
    async def cat(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle file reading."""
        params = context.crt_params
        if not params:
            yield CommandReturn(text="Usage: !tars cat <path>")
            return

        path = params[0]

        helper = await get_helper()
        result = await helper.read_file(path)

        if result["success"]:
            content = result.get("content", "")
            if result.get("is_binary"):
                yield CommandReturn(text=f"Binary file: {result.get('path', path)} ({result.get('size', 0)} bytes)")
            elif len(content) > 2000:
                yield CommandReturn(text=f"```\n{content[:2000]}\n```\n\n... (truncated)")
            else:
                yield CommandReturn(text=f"```\n{content}\n```")
        else:
            yield CommandReturn(text=f"Failed: {result.get('error', 'Access denied')}")

    @staticmethod
    async def write(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle file writing."""
        params = context.crt_params
        if len(params) < 2:
            yield CommandReturn(text="Usage: !tars write <path> <content>")
            return

        path = params[0]
        content = " ".join(params[1:])

        helper = await get_helper()
        result = await helper.write_file(path, content)

        if result["success"]:
            yield CommandReturn(text=f"File written: {result.get('path', path)}")
        else:
            yield CommandReturn(text=f"Failed: {result.get('error', 'Unknown error')}")

    @staticmethod
    async def open(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle app/URL opening."""
        params = context.crt_params
        if not params:
            yield CommandReturn(text="Usage: !tars open <app_name|url>")
            return

        target = params[0]
        is_url = target.startswith(("http://", "https://", "mailto:", "tel:"))

        helper = await get_helper()
        result = await helper.open_app(
            target if not is_url else None,
            url=target if is_url else None
        )

        if result["success"]:
            yield CommandReturn(text=f"Opened: {target}")
        else:
            yield CommandReturn(text=f"Failed: {result.get('error', 'Unknown error')}")

    @staticmethod
    async def close(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle app closing."""
        params = context.crt_params
        if not params:
            yield CommandReturn(text="Usage: !tars close <app_name> [-f]")
            return

        app_name = params[0]
        force = "-f" in params

        helper = await get_helper()
        result = await helper.close_app(app_name, force=force)

        if result["success"]:
            yield CommandReturn(text=f"Closed: {app_name}")
        else:
            yield CommandReturn(text=f"Failed: {result.get('error', 'Unknown error')}")

    @staticmethod
    async def stop(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle task stopping."""
        from components.tools.planner import PlannerTool, SubprocessPlanner

        # Set stop flag and remove run file
        PlannerTool.stop_task()
        SubprocessPlanner._remove_run_file()

        # Clear thread reference to allow new tasks
        if SubprocessPlanner._thread:
            SubprocessPlanner._thread = None

        yield CommandReturn(text="🛑 Stop signal sent.\n\nIf the task doesn't stop, run in terminal:\n  touch /tmp/langtars_user_stop")

    @staticmethod
    async def top(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle app listing."""
        helper = await get_helper()
        result = await helper.list_apps()

        if result["success"]:
            apps = result.get("apps", [])
            if not apps:
                yield CommandReturn(text="No applications running.")
                return

            lines = ["**Running Applications:**\n"]
            lines.append("\n".join(f"• {app}" for app in apps))
            yield CommandReturn(text="\n".join(lines))
        else:
            yield CommandReturn(text=f"Failed: {result.get('error', 'Unknown error')}")

    @staticmethod
    async def info(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle system info display."""
        helper = await get_helper()
        result = await helper.get_system_info()

        if result["success"]:
            info = result.get("info", {})
            lines = ["**System Information:**\n"]
            for key, value in info.items():
                if isinstance(value, dict):
                    continue
                lines.append(f"• **{key}**: {value}")
            yield CommandReturn(text="\n".join(lines))
        else:
            yield CommandReturn(text=f"Failed: {result.get('error', 'Unknown error')}")

    @staticmethod
    async def search(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle file search."""
        params = context.crt_params
        if not params:
            yield CommandReturn(text="Usage: !tars search <pattern> [path]")
            return

        pattern = params[0]
        path = params[1] if len(params) > 1 else "."

        helper = await get_helper()
        result = await helper.search_files(pattern, path)

        if result["success"]:
            files = result.get("files", [])
            if not files:
                yield CommandReturn(text=f"No files found matching '{pattern}'")
                return

            lines = [f"**Search Results for '{pattern}':**\n"]
            for f in files[:20]:
                lines.append(f"• {f}")

            if len(files) > 20:
                lines.append(f"... and {len(files) - 20} more")

            yield CommandReturn(text="\n".join(lines))
        else:
            yield CommandReturn(text=f"Failed: {result.get('error', 'Unknown error')}")

    @staticmethod
    async def default(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle default case - show help."""
        help_text = """LangTARS - Control your Mac through IM messages

Available commands:
  !tars shell <command>   - Execute shell command
  !tars ps [filter]       - List running processes
  !tars kill <pid|name>   - Kill a process
  !tars ls [path]         - List directory contents
  !tars cat <path>        - Read file content
  !tars write <path> <content> - Write file
  !tars open <app|url>   - Open an application or URL
  !tars close <app>      - Close an application
  !tars top              - List running applications
  !tars info             - Show system information
  !tars search <pattern> - Search files
  !tars auto <task>      - Autonomous task planning (AI-powered)

To stop a running task, run in terminal:
  touch /tmp/langtars_user_stop

Examples:
  !tars info
  !tars shell ls -la
  !tars ps python
  !tars open Safari
  !tars auto Open Safari and search for AI news
"""
        yield CommandReturn(text=help_text)

    @staticmethod
    async def auto(_self_cmd: Command, context: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        """Handle autonomous task planning using ReAct loop."""
        params = context.crt_params
        if not params:
            yield CommandReturn(text="""Usage: !tars auto <task description>

Example:
  !tars auto Open Safari and search for AI news
""")
            return

        task = " ".join(params)

        # Get config from the command's plugin instance
        config = _self_cmd.plugin.get_config()
        max_iterations = int(config.get("planner_max_iterations", 5) or 5)

        configured_model_uuid = config.get("planner_model_uuid", "")

        # Get available models
        try:
            models = await _self_cmd.plugin.get_llm_models()
            if not models:
                yield CommandReturn(text="""Error: No LLM models available.

Please configure an LLM model in the pipeline settings first.
Go to Pipelines → Configure → Select LLM Model
""")
                return

            if configured_model_uuid:
                for model in models:
                    if isinstance(model, dict) and model.get("uuid") == configured_model_uuid:
                        llm_model_uuid = configured_model_uuid
                        break
                else:
                    first_model = models[0]
                    llm_model_uuid = first_model.get("uuid", "") if isinstance(first_model, dict) else first_model
            else:
                first_model = models[0]
                if isinstance(first_model, dict):
                    llm_model_uuid = first_model.get("uuid", "")
                else:
                    llm_model_uuid = first_model

            if not llm_model_uuid:
                yield CommandReturn(text="Error: Model does not have a valid UUID")
                return
        except Exception as e:
            yield CommandReturn(text=f"Error: Failed to get available models: {str(e)}")
            return

        # Check if a task is already running
        from components.tools.planner import PlannerTool, SubprocessPlanner

        # Only check if thread is actually running
        if SubprocessPlanner.is_running():
            yield CommandReturn(text="⚠️ A task is already running. Use !tars stop to stop it first.")
            return

        # Always reset state before starting a new task
        PlannerTool.reset_task_state()
        SubprocessPlanner._thread = None

        # Check if we should use subprocess mode for better stop support
        # Default to True for better stop command support
        use_subprocess = config.get("planner_use_subprocess", "true").lower() == "true"

        # Execute the planner
        try:
            from components.tools.planner import PlannerExecutor, SubprocessPlanner
            executor = PlannerExecutor()

            if use_subprocess:
                # Use subprocess mode - allows stop command to work better
                async for partial_result in SubprocessPlanner.execute_in_subprocess(
                    task=task,
                    max_iterations=max_iterations,
                    llm_model_uuid=llm_model_uuid,
                    plugin=_self_cmd.plugin,
                    helper_plugin=_self_cmd.plugin,
                    session=context.session,
                    query_id=context.query_id
                ):
                    yield CommandReturn(text=partial_result)
            else:
                # Execute directly (default)
                async for partial_result in executor.execute_task_streaming(
                    task=task,
                    max_iterations=max_iterations,
                    llm_model_uuid=llm_model_uuid,
                    plugin=_self_cmd.plugin,
                    helper_plugin=_self_cmd.plugin,
                    session=context.session,
                    query_id=context.query_id
                ):
                    yield CommandReturn(text=partial_result)

        except Exception as e:
            import traceback
            yield CommandReturn(text=f"Error executing task: {str(e)}\n\n{traceback.format_exc()}")
