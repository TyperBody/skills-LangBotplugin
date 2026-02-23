# Chrome Control - Native Chrome browser control via AppleScript

from __future__ import annotations

from typing import Any


class ChromeController:
    """Controller for native Chrome browser control."""

    def __init__(self, run_applescript_func):
        """Initialize with a function that executes AppleScript."""
        self._run_applescript = run_applescript_func

    async def open(self, url: str | None = None) -> dict[str, Any]:
        """Open Chrome (optionally with URL)."""
        if url:
            return await self.navigate(url)

        script = '''tell application "Google Chrome" to activate'''
        return await self._run_applescript(script)

    async def navigate(self, url: str) -> dict[str, Any]:
        """Navigate to URL in Chrome using AppleScript."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Escape quotes for AppleScript
        url_escaped = url.replace('"', '\\"')
        script = f'''
tell application "Google Chrome"
    activate
    if (count of windows) = 0 then
        make new window
    end if
    tell window 1
        set current tab to (make new tab with properties {{URL:"{url_escaped}"}})
    end tell
end tell
'''
        return await self._run_applescript(script)

    async def get_content(self) -> dict[str, Any]:
        """Get content from Chrome using AppleScript."""
        script = '''
tell application "Google Chrome"
    if (count of windows) is 0 then
        return "No Chrome windows"
    end if
    set tabTitle to title of active tab of front window
    set tabURL to URL of active tab of front window
    execute front window's active tab javascript "document.body.innerText"
    return "Title: " & tabTitle & ", URL: " & tabURL
end tell
'''
        result = await self._run_applescript(script)
        if result.get("success"):
            return {"success": True, "text": result.get("stdout", "")}
        return result

    async def click(self, selector: str) -> dict[str, Any]:
        """Click element in Chrome using JavaScript."""
        # Escape quotes
        selector_escaped = selector.replace("'", "\\'")
        script = f'''
tell application "Google Chrome"
    activate
    tell front window
        tell active tab
            execute javascript "document.querySelector('{selector_escaped}')?.click()"
        end tell
    end tell
end tell
'''
        return await self._run_applescript(script)

    async def type(self, selector: str, text: str) -> dict[str, Any]:
        """Type text into element in Chrome."""
        # Escape quotes
        selector_escaped = selector.replace("'", "\\'")
        text_escaped = text.replace("'", "\\'")
        script = f'''
tell application "Google Chrome"
    activate
    tell front window
        tell active tab
            execute javascript "document.querySelector('{selector_escaped}').value = '{text_escaped}'"
        end tell
    end tell
end tell
'''
        return await self._run_applescript(script)

    async def press_key(self, key: str) -> dict[str, Any]:
        """Press key in Chrome."""
        script = f'''
tell application "Google Chrome"
    activate
    tell front window
        tell active tab
            execute javascript "document.activeElement.dispatchEvent(new KeyboardEvent('keydown', {{key:'{key}', bubbles:true}}))"
        end tell
    end tell
end tell
'''
        return await self._run_applescript(script)
