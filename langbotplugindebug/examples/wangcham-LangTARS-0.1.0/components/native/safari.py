# Safari Control - Native Safari browser control via AppleScript

from __future__ import annotations

from typing import Any


class SafariController:
    """Controller for native Safari browser control."""

    def __init__(self, run_applescript_func):
        """Initialize with a function that executes AppleScript."""
        self._run_applescript = run_applescript_func

    async def open(self, url: str | None = None) -> dict[str, Any]:
        """Open Safari (optionally with URL)."""
        if url:
            return await self.navigate(url)

        script = '''tell application "Safari" to activate'''
        return await self._run_applescript(script)

    async def navigate(self, url: str) -> dict[str, Any]:
        """Navigate to URL in Safari using AppleScript."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # Escape quotes for AppleScript
        url_escaped = url.replace('"', '\\"')
        script = f'''
tell application "Safari"
    activate
    if (count of windows) = 0 then
        make new document
    end if
    tell window 1
        set current tab to (make new tab with properties {{URL:"{url_escaped}"}})
    end tell
end tell
'''
        return await self._run_applescript(script)

    async def get_content(self) -> dict[str, Any]:
        """Get content from Safari using AppleScript."""
        # First try with JavaScript (requires user to enable in Safari settings)
        script = '''
tell application "Safari"
    if (count of windows) is 0 then
        return "No Safari windows"
    end if
    set tabTitle to name of current tab of front window
    set tabURL to URL of current tab of front window
    set tabContent to do JavaScript "document.body.innerText" in current tab of front window
    return "Title: " & tabTitle & ", URL: " & tabURL & ", Content: " & tabContent
end tell
'''
        result = await self._run_applescript(script)

        # Check if it's the JavaScript permission error
        error_msg = result.get("error", "")
        if "Allow JavaScript from Apple Events" in error_msg:
            # Fall back to getting just title and URL without JavaScript
            script_no_js = '''
tell application "Safari"
    if (count of windows) is 0 then
        return "No Safari windows"
    end if
    set tabTitle to name of current tab of front window
    set tabURL to URL of current tab of front window
    return "Title: " & tabTitle & ", URL: " & tabURL & " (Enable Safari > Settings > Advanced > Allow JavaScript from Apple Events to get page content)"
end tell
'''
            result = await self._run_applescript(script_no_js)
            if result.get("success"):
                return {
                    "success": True,
                    "text": result.get("stdout", ""),
                    "warning": "JavaScript disabled in Safari. Enable it in Settings > Privacy & Security > Allow JavaScript from Apple Events",
                }

        if result.get("success"):
            return {"success": True, "text": result.get("stdout", "")}
        return result

    async def click(self, selector: str) -> dict[str, Any]:
        """Click element in Safari using JavaScript."""
        # Escape quotes
        selector_escaped = selector.replace("'", "\\'")
        script = f'''
tell application "Safari"
    activate
    tell front window
        tell current tab
            do JavaScript "document.querySelector('{selector_escaped}')?.click()"
        end tell
    end tell
end tell
'''
        return await self._run_applescript(script)

    async def type(self, selector: str, text: str) -> dict[str, Any]:
        """Type text into element in Safari."""
        # Escape quotes
        selector_escaped = selector.replace("'", "\\'")
        text_escaped = text.replace("'", "\\'")
        script = f'''
tell application "Safari"
    activate
    tell front window
        tell current tab
            do JavaScript "document.querySelector('{selector_escaped}').value = '{text_escaped}'"
        end tell
    end tell
end tell
'''
        return await self._run_applescript(script)

    async def press_key(self, key: str) -> dict[str, Any]:
        """Press key in Safari."""
        script = f'''
tell application "Safari"
    activate
    tell front window
        tell current tab
            do JavaScript "document.activeElement.dispatchEvent(new KeyboardEvent('keydown', {{key:'{key}', bubbles:true}}))"
        end tell
    end tell
end tell
'''
        return await self._run_applescript(script)
