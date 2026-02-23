# LangTARS Plugin for LangBot
# Control your Mac through IM messages

from __future__ import annotations

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from langbot_plugin.api.definition.components.command.command import Command, Subcommand
from langbot_plugin.api.definition.plugin import BasePlugin
from langbot_plugin.api.entities.builtin.command.context import ExecuteContext, CommandReturn

from components.helpers.browser import BrowserController
from components.native.safari import SafariController
from components.native.chrome import ChromeController
from components.commands.langtars import LanTARSCommand


class LangTARS(Command, BasePlugin):
    """LangTARS Plugin - Control your Mac through IM messages"""

    DANGEROUS_PATTERNS = [
        r'rm\s+-rf\s+/', r'mkfs', r'dd\s+if=/dev/zero', r':(){:|:&};:',
        r'chmod\s+777\s+/', r'sudo\s+.*', r'>\s*/dev/', r'&\s*>/dev/',
    ]

    def __init__(self):
        super().__init__()
        self.config: dict = {}
        self._workspace_path = None
        self._allowed_users: set = set()
        self._command_whitelist: list = []
        self._initialized = False

        # Controllers
        self._browser: BrowserController | None = None
        self._safari: SafariController | None = None
        self._chrome: ChromeController | None = None

        # Register subcommands - delegate to LanTARSCommand
        self.registered_subcommands = {
            "info": Subcommand(subcommand=LanTARSCommand.info, help="Get system info", usage="!tars info", aliases=["system"]),
            "shell": Subcommand(subcommand=LanTARSCommand.shell, help="Execute shell", usage="!tars shell <cmd>", aliases=["sh", "exec"]),
            "ps": Subcommand(subcommand=LanTARSCommand.ps, help="List processes", usage="!tars ps [filter]", aliases=["processes"]),
            "ls": Subcommand(subcommand=LanTARSCommand.ls, help="List directory", usage="!tars ls [path]", aliases=["dir"]),
            "cat": Subcommand(subcommand=LanTARSCommand.cat, help="Read file", usage="!tars cat <path>", aliases=["read"]),
            "kill": Subcommand(subcommand=LanTARSCommand.kill, help="Kill process", usage="!tars kill <pid|name>", aliases=[]),
            "open": Subcommand(subcommand=LanTARSCommand.open, help="Open app/URL", usage="!tars open <app|url>", aliases=["launch"]),
            "close": Subcommand(subcommand=LanTARSCommand.close, help="Close app", usage="!tars close <app>", aliases=["quit"]),
            "apps": Subcommand(subcommand=LanTARSCommand.top, help="List apps", usage="!tars apps", aliases=["top"]),
            "stop": Subcommand(subcommand=LanTARSCommand.stop, help="Stop task", usage="!tars stop", aliases=["pause"]),
            "config": Subcommand(subcommand=self.cmd_config, help="Config", usage="!tars config [save]", aliases=["cfg"]),
            "search": Subcommand(subcommand=LanTARSCommand.search, help="Search files", usage="!tars search <pattern>", aliases=["find"]),
            "write": Subcommand(subcommand=LanTARSCommand.write, help="Write file", usage="!tars write <path> <content>", aliases=["save"]),
            "auto": Subcommand(subcommand=LanTARSCommand.auto, help="AI planning", usage="!tars auto <task>", aliases=["plan", "run"]),
            "*": Subcommand(subcommand=LanTARSCommand.default, help="Help", usage="!tars help", aliases=[]),
        }

    # ========== Config ==========

    def get_config(self) -> dict:
        return self.config

    def _get_config_file_path(self):
        from pathlib import Path
        config_dir = Path.home() / ".langtars"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    def _load_config_from_file(self) -> dict:
        import json
        config_file = self._get_config_file_path()
        if config_file.exists():
            try:
                return json.loads(config_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save_config_to_file(self, config: dict) -> None:
        import json
        config_file = self._get_config_file_path()
        try:
            config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.debug(f"Failed to save config: {e}")

    def set_config(self, config: dict) -> None:
        self.config = config
        self._save_config_to_file(config)

    async def initialize(self) -> None:
        local_config = self._load_config_from_file()

        for key in ['planner_max_iterations', 'planner_rate_limit_seconds', 'browser_timeout']:
            if key in local_config and isinstance(local_config[key], str):
                try:
                    local_config[key] = int(local_config[key])
                except (ValueError, TypeError):
                    pass

        self.config = self.config or {}
        if local_config:
            self.config = {**local_config, **self.config}

        if 'planner_rate_limit_seconds' not in self.config:
            self.config['planner_rate_limit_seconds'] = 3
        elif isinstance(self.config['planner_rate_limit_seconds'], str):
            try:
                self.config['planner_rate_limit_seconds'] = int(self.config['planner_rate_limit_seconds'])
            except (ValueError, TypeError):
                self.config['planner_rate_limit_seconds'] = 3

        from pathlib import Path
        workspace = self.config.get('workspace_path', '~/.langtars')
        self._workspace_path = Path(workspace).expanduser()
        self._workspace_path.mkdir(parents=True, exist_ok=True)
        self._allowed_users = set(self.config.get('allowed_users', []))
        self._command_whitelist = self.config.get('command_whitelist', [])
        self._initialized = True
        self._save_config_to_file(self.config)

        # Initialize controllers
        self._browser = BrowserController(self.config)
        self._safari = SafariController(self.run_applescript)
        self._chrome = ChromeController(self.run_applescript)

    # ========== Safety ==========

    def is_user_allowed(self, user_id: str) -> bool:
        return not self._allowed_users or user_id in self._allowed_users

    def is_command_allowed(self, command: str) -> bool:
        if not self._command_whitelist:
            return True
        cmd_base = command.strip().split()[0] if command.strip() else ''
        return cmd_base in self._command_whitelist

    def check_dangerous_pattern(self, command: str) -> tuple[bool, str]:
        import re
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return True, f"Dangerous pattern: {pattern}"
        return False, ""

    # ========== Shell Execution ==========

    async def run_shell(self, command: str, timeout: int = 30, working_dir: str | None = None) -> dict:
        import asyncio
        from pathlib import Path

        if not self.config.get('enable_shell', True):
            return {'success': False, 'error': 'Shell disabled', 'stdout': '', 'stderr': '', 'returncode': -1}
        if not self.is_command_allowed(command):
            return {'success': False, 'error': 'Command not in whitelist', 'stdout': '', 'stderr': '', 'returncode': -1}
        is_dangerous, danger_msg = self.check_dangerous_pattern(command)
        if is_dangerous:
            return {'success': False, 'error': f'Blocked: {danger_msg}', 'stdout': '', 'stderr': '', 'returncode': -1}

        working_path = self._workspace_path
        if working_dir:
            wp = Path(working_dir).expanduser().resolve()
            if str(wp).startswith(str(self._workspace_path.resolve())):
                working_path = wp

        try:
            process = await asyncio.create_subprocess_shell(
                command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=str(working_path))
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                process.kill()
                return {'success': False, 'error': f'Timeout after {timeout}s', 'stdout': '', 'stderr': '', 'returncode': -1}
            return {
                'success': process.returncode == 0,
                'stdout': stdout.decode('utf-8', errors='replace'),
                'stderr': stderr.decode('utf-8', errors='replace'),
                'returncode': process.returncode, 'error': '',
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'stdout': '', 'stderr': '', 'returncode': -1}

    def _resolve_path(self, path: str):
        from pathlib import Path
        if not self._workspace_path:
            return None
        try:
            requested = Path(path).expanduser()
            if requested.is_absolute():
                resolved = requested.resolve()
                if not str(resolved).startswith(str(self._workspace_path.resolve())):
                    return None
                return resolved
            return (self._workspace_path / requested).resolve()
        except Exception:
            return None

    # ========== Helper Methods ==========

    async def list_processes(self, filter_pattern: str | None = None, limit: int = 20) -> dict:
        if not self.config.get('enable_process', True):
            return {'success': False, 'error': 'Disabled', 'processes': []}
        cmd = f'ps aux | grep -E "{filter_pattern}" | grep -v grep | head -n {limit}' if filter_pattern else f'ps aux | head -n {limit + 1}'
        result = await self.run_shell(cmd)
        if not result['success']:
            return {'success': False, 'error': result.get('error'), 'processes': []}
        processes = []
        for line in result['stdout'].strip().split('\n'):
            parts = line.split(None, 10)
            if len(parts) >= 11:
                processes.append({'user': parts[0], 'pid': parts[1], 'cpu': parts[2], 'mem': parts[3], 'command': parts[10]})
        return {'success': True, 'processes': processes[:limit]}

    async def kill_process(self, target: str, force: bool = False) -> dict:
        if not self.config.get('enable_process', True):
            return {'success': False, 'error': 'Disabled'}
        cmd = f'kill -{"KILL" if force else "TERM"} {target}' if target.isdigit() else f'pkill -{"KILL" if force else "TERM"} "{target}"'
        result = await self.run_shell(cmd)
        return {'success': result['success'], 'message': f'Killed {target}' if result['success'] else result.get('error')}

    async def list_directory(self, path: str = ".", show_hidden: bool = False) -> dict:
        if not self.config.get('enable_file', True):
            return {'success': False, 'error': 'Disabled', 'items': []}
        dir_path = self._resolve_path(path)
        if not dir_path:
            return {'success': False, 'error': 'Access denied', 'items': []}
        try:
            items = [{'name': i.name, 'type': 'directory' if i.is_dir() else 'file', 'size': i.stat().st_size if i.is_file() else 0}
                     for i in dir_path.iterdir() if not i.name.startswith('.') or show_hidden]
            return {'success': True, 'path': str(dir_path), 'items': items, 'count': len(items)}
        except Exception as e:
            return {'success': False, 'error': str(e), 'items': []}

    async def read_file(self, path: str) -> dict:
        if not self.config.get('enable_file', True):
            return {'success': False, 'error': 'Disabled'}
        fp = self._resolve_path(path)
        if not fp:
            return {'success': False, 'error': 'Access denied'}
        try:
            if not fp.is_file():
                return {'success': False, 'error': 'Not a file'}
            content = fp.read_text(encoding='utf-8')
            return {'success': True, 'path': str(fp), 'content': content, 'size': len(content)}
        except UnicodeDecodeError:
            return {'success': True, 'path': str(fp), 'is_binary': True, 'size': fp.stat().st_size}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def write_file(self, path: str, content: str, mode: str = "w") -> dict:
        if not self.config.get('enable_file', True):
            return {'success': False, 'error': 'Disabled'}
        fp = self._resolve_path(path)
        if not fp:
            return {'success': False, 'error': 'Access denied'}
        try:
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(content, encoding='utf-8')
            return {'success': True, 'path': str(fp)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def open_app(self, app_name: str | None = None, url: str | None = None) -> dict:
        if not self.config.get('enable_app', True):
            return {'success': False, 'error': 'Disabled'}
        cmd = f'open "{url}"' if url else f'open -a "{app_name}"' if app_name else None
        if not cmd:
            return {'success': False, 'error': 'No target'}
        result = await self.run_shell(cmd)
        return {'success': result['success'], 'message': f'Opened {url or app_name}' if result['success'] else result.get('error')}

    async def close_app(self, app_name: str, force: bool = False) -> dict:
        if not self.config.get('enable_app', True):
            return {'success': False, 'error': 'Disabled'}
        result = await self.run_shell(f'pkill -{"9" if force else "TERM"} "{app_name}"')
        return {'success': result['success'], 'message': f'Closed {app_name}' if result['success'] else result.get('error')}

    async def list_apps(self, limit: int = 20) -> dict:
        if not self.config.get('enable_app', True):
            return {'success': False, 'error': 'Disabled', 'apps': []}
        result = await self.run_shell(f"osascript -e 'tell app \"System Events\" to get name of every process' | tr ',' '\\n' | head -n {limit}")
        if result['success']:
            apps = [a.strip() for a in result['stdout'].strip().split('\n') if a.strip()]
            return {'success': True, 'apps': apps, 'count': len(apps)}
        return {'success': False, 'error': result.get('error'), 'apps': []}

    async def get_system_info(self) -> dict:
        import platform
        try:
            info = {'platform': platform.system(), 'platform_version': platform.version(), 'architecture': platform.architecture()[0],
                   'processor': platform.processor(), 'hostname': platform.node(), 'python_version': platform.python_version()}
            ur = await self.run_shell('uptime')
            if ur['success']:
                info['uptime'] = ur['stdout'].strip()
            return {'success': True, 'info': info}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def search_files(self, pattern: str, path: str = ".", recursive: bool = True) -> dict:
        if not self.config.get('enable_file', True):
            return {'success': False, 'error': 'Disabled', 'files': []}
        sp = self._resolve_path(path)
        if not sp:
            return {'success': False, 'error': 'Access denied', 'files': []}
        cmd = f'find "{sp}" -name "*{pattern}*" -type f 2>/dev/null | head -n 50' if recursive else f'ls "{sp}" | grep -i "*{pattern}*" | head -n 50'
        result = await self.run_shell(cmd)
        if result['success']:
            files = [f.strip() for f in result['stdout'].strip().split('\n') if f.strip()]
            return {'success': True, 'files': files, 'count': len(files)}
        return {'success': False, 'error': result.get('error'), 'files': []}

    async def run_applescript(self, script: str) -> dict:
        import tempfile, os
        if not self.config.get('enable_applescript', True):
            return {'success': False, 'error': 'Disabled'}
        if not script:
            return {'success': False, 'error': 'No script'}
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.scpt', delete=False) as f:
                f.write(script)
                temp_file = f.name
            try:
                result = await self.run_shell(f'osascript "{temp_file}"')
            finally:
                try: os.unlink(temp_file)
                except: pass
            if result['success']:
                return {'success': True, 'stdout': result['stdout'], 'stderr': result['stderr'], 'returncode': result['returncode']}
            return {'success': False, 'error': result.get('stderr', result.get('error')), 'stdout': result.get('stdout')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ========== Browser/Safari/Chrome Delegates ==========

    async def browser_navigate(self, url: str): return await self._browser.navigate(url) if self._browser else {'success': False}
    async def browser_click(self, s): return await self._browser.click(s) if self._browser else {'success': False}
    async def browser_type(self, s, t, c=True): return await self._browser.type_text(s, t, c) if self._browser else {'success': False}
    async def browser_screenshot(self, p=None): return await self._browser.screenshot(p) if self._browser else {'success': False}
    async def browser_get_content(self, s=None): return await self._browser.get_content(s) if self._browser else {'success': False}
    async def browser_wait(self, s, t=30): return await self._browser.wait_for_selector(s, t) if self._browser else {'success': False}
    async def browser_scroll(self, x=0, y=500): return await self._browser.scroll(x, y) if self._browser else {'success': False}
    async def browser_execute_script(self, s): return await self._browser.execute_script(s) if self._browser else {'success': False}
    async def browser_new_tab(self, u="about:blank"): return await self._browser.new_tab(u) if self._browser else {'success': False}
    async def browser_close_tab(self): return await self._browser.close_tab() if self._browser else {'success': False}
    async def browser_get_url(self): return await self._browser.get_current_url() if self._browser else {'success': False}
    async def browser_reload(self): return await self._browser.reload() if self._browser else {'success': False}
    async def browser_press_key(self, s, k): return await self._browser.press_key(s, k) if self._browser else {'success': False}
    async def browser_select_option(self, s, v): return await self._browser.select_option(s, v) if self._browser else {'success': False}
    async def browser_get_attribute(self, s, a): return await self._browser.get_attribute(s, a) if self._browser else {'success': False}
    async def browser_cleanup(self): return await self._browser.cleanup() if self._browser else {'success': True}

    async def safari_open(self, u=None): return await self._safari.open(u) if self._safari else {'success': False}
    async def safari_navigate(self, u): return await self._safari.navigate(u) if self._safari else {'success': False}
    async def safari_get_content(self): return await self._safari.get_content() if self._safari else {'success': False}
    async def safari_click(self, s): return await self._safari.click(s) if self._safari else {'success': False}
    async def safari_type(self, s, t): return await self._safari.type(s, t) if self._safari else {'success': False}
    async def safari_press_key(self, k): return await self._safari.press_key(k) if self._safari else {'success': False}

    async def chrome_open(self, u=None): return await self._chrome.open(u) if self._chrome else {'success': False}
    async def chrome_navigate(self, u): return await self._chrome.navigate(u) if self._chrome else {'success': False}
    async def chrome_get_content(self): return await self._chrome.get_content() if self._chrome else {'success': False}
    async def chrome_click(self, s): return await self._chrome.click(s) if self._chrome else {'success': False}
    async def chrome_type(self, s, t): return await self._chrome.type(s, t) if self._chrome else {'success': False}
    async def chrome_press_key(self, k): return await self._chrome.press_key(k) if self._chrome else {'success': False}

    # ========== Commands ==========

    async def cmd_config(self, ctx: ExecuteContext) -> "CommandReturn":
        from langbot_plugin.api.entities.builtin.command.context import CommandReturn
        action = ctx.crt_params[0] if ctx.crt_params else "show"
        if action == "save":
            self._save_config_to_file(self.config)
            return CommandReturn(text=f"Saved to {self._get_config_file_path()}")
        keys = ['enable_shell', 'enable_process', 'enable_file', 'enable_app', 'planner_max_iterations', 'workspace_path']
        return CommandReturn(text="\n".join(f"{k}: {self.config.get(k)}" for k in keys))
