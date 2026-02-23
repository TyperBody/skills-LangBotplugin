<p align="center">
  <img src="assets/icon.svg" alt="LangTARS" width="128">
</p>

<p align="center">
  <strong>LangTARS</strong> — Native Claw-Like Plugin
</p>

<p align="center">
  <a href="readme/README_zh_Hans.md">简体中文</a>&nbsp; • &nbsp;
  <a href="readme/README_zh_Hant.md">繁體中文</a>&nbsp; • &nbsp;
  <a href="readme/README_ja_JP.md">日本語</a>&nbsp; • &nbsp;
  <a href="https://github.com/langbot-app/LangTARS">GitHub</a>
</p>

> ⚠️ **Note**: Features are still under active development. If you encounter any bugs, please submit an [issue](https://github.com/langbot-app/LangTARS/issues).
> Currently, using this plugin may encounter many issues, such as the stop command sometimes failing to execute. Please manually close the plugin and restart it. After the LangBot official plugin SDK is updated, LangTARS will continue to update related commands and features.

---

## What is LangTARS?

LangTARS is a **native Claw-like plugin** inspired by Nanobot's ReAct philosophy, designed to bring the **OpenClaw** experience to LangBot users. It enables you to control your Mac through IM messages using autonomous AI task planning. Like **TARS** from *Interstellar*, it works faithfully for you.

Like [OpenClaw](https://github.com/openclaw/openclaw), LangTARS allows AI assistants to execute real actions on your Mac—but with the simplicity and elegance of a LangBot plugin.

## Why LangTARS?

[OpenClaw](https://github.com/openclaw/openclaw) is an impressive project with a great vision. However, running such complex software with access to your digital life requires trust in systems you may not fully understand.

LangTARS takes a different approach:
- **Native LangBot integration** — Runs directly within LangBot using the Nanobot kernel
- **Lightweight** — Minimal codebase you can understand and audit
- **Autonomous planning** — Uses ReAct loop for intelligent task execution
- **Safety-first** — Built-in command restrictions, workspace isolation, and dangerous command blocking

## Quick Start

1. Install LangTARS through LangBot's plugin system
2. Configure your preferred LLM model for task planning
3. Start controlling your Mac via IM messages!

## Main Command

### `!tars auto` — Autonomous Task Planning

This is the **primary command** that makes LangTARS special. Simply describe what you want to do, and the AI will autonomously plan and execute the task using available tools.

- `!tars auto Open Safari, visit langbot.app, scrape elements and tell me`
- `!tars auto Create a new note with title and content "hello"`
- `!tars auto Help me organize the files on my desktop`

- <code><del>!tars auto Cook me some dishes.</del></code>

### Browser Control

LangTARS supports three browser control methods:

| Command Example | Browser | Description |
|----------|---------|------|
| `!tars auto Visit github.com` | Playwright (Chromium) | Default, no extra permissions needed |
| `!tars auto Open Safari and visit github` | Safari Browser | Uses real Safari, requires AppleScript permission |
| `!tars auto Open Chrome and visit github` | Chrome Browser | Uses real Chrome, requires AppleScript permission |

The AI will:
1. Understand your request
2. Plan the necessary steps
3. Execute them one by one using shell commands, file operations, app control, etc.
4. Report back with results

You can **stop** a running task at any time:
```
!tars stop
```

Check task status:
```
!tars status
```

## Testing Commands

These commands are available for testing and direct control:

| Command | Description |
|---------|-------------|
| `!tars auto <task>` | Autonomous task planning (AI-powered) |
| `!tars shell <command>` | Execute a shell command |
| `!tars ps [filter]` | List running processes |
| `!tars kill <pid\|name>` | Kill a process |
| `!tars ls [path]` | List directory contents |
| `!tars cat <path>` | Read file content |
| `!tars write <path> <content>` | Write file content |
| `!tars open <app\|url>` | Open an application or URL |
| `!tars close <app>` | Close an application |
| `!tars apps [limit]` | List running applications |
| `!tars info` | Show system information |
| `!tars search <pattern>` | Search files |

## Configuration

Configure LangTARS through LangBot's settings:

| Option | Description | Default |
|--------|-------------|---------|
| `allowed_users` | User IDs allowed to control this Mac | [] |
| `command_whitelist` | Allowed shell commands (empty = all with restrictions) | [] |
| `workspace_path` | Working directory for file operations | ~/.langtars |
| `enable_shell` | Enable shell command execution | true |
| `enable_process` | Enable process management | true |
| `enable_file` | Enable file operations | true |
| `enable_app` | Enable app control | true |
| `enable_applescript` | Enable AppleScript execution | true |
| `enable_browser` | Enable browser automation (Playwright) | true |
| `browser_type` | Browser engine (chromium/firefox/webkit) | chromium |
| `browser_headless` | Run browser in headless mode | false |
| `browser_timeout` | Browser operation timeout (seconds) | 30 |
| `planner_max_iterations` | Max ReAct loop iterations | 5 |
| `planner_model_uuid` | LLM model for task planning | (first available) |
| `planner_rate_limit_seconds` | Rate limit between LLM calls | 1 |
| `planner_auto_load_mcp` | Auto-load MCP tools | true |
| `planner_auto_load_skills` | Auto-load skills from ~/.claude/skills | true |
| `skills_path` | Skills directory path | ~/.claude/skills |

## Safety Features

- **Dangerous command blocking** — Commands like `rm -rf /` are blocked by default
- **Workspace isolation** — File operations restricted to configured workspace
- **Command whitelist** — Optionally restrict to specific commands
- **User access control** — Optionally limit to specific users

## Architecture

```
IM Message --> LangBot --> PlannerTool (ReAct Loop) --> Tools --> Mac Actions
```

- **PlannerTool** — ReAct loop for autonomous task planning using LLM
- **Tool Registry** — Dynamic tool loading from MCP servers and plugins
- **Built-in Tools** — Shell, process, file, app control

## License

MIT
