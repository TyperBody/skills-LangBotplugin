# ClawHub Skills Loader
# Loads and manages skills from local skills directory and remote hub

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

import aiohttp
import yaml

from . import BasePlannerTool


class Skill:
    """Represents a ClawHub Skill"""

    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        path: Path,
        manifest: dict[str, Any],
        source: str = "local",  # "local" or "remote"
    ):
        self.name = name
        self.version = version
        self.description = description
        self.path = path
        self.manifest = manifest
        self.source = source
        self.parameters = manifest.get("parameters", {})
        self.returns = manifest.get("returns", {})
        self.dependencies = manifest.get("npm_dependencies", {})


class SkillLoader:
    """Loads skills from local directory and remote ClawHub"""

    # Fallback skill mappings when remote API is unavailable
    # Format: skill_keyword -> (github_repo, skill_name)
    FALLBACK_SKILLS = {
        "weather": ("langbot-app/clawhub-weather", "weather"),
        "email": ("langbot-app/clawhub-email", "email"),
        "note": ("langbot-app/clawhub-notes", "notes"),
        "notes": ("langbot-app/clawhub-notes", "notes"),
        "reminder": ("langbot-app/clawhub-reminder", "reminder"),
        "calendar": ("langbot-app/clawhub-calendar", "calendar"),
        "slack": ("langbot-app/clawhub-slack", "slack"),
        "discord": ("langbot-app/clawhub-discord", "discord"),
    }

    def __init__(self, config: dict[str, Any]):
        self.config = config
        # Default skills directory: ~/.claude/skills
        self.skills_dir = Path(os.path.expanduser(config.get("skills_path", "~/.claude/skills")))
        # Try multiple possible API endpoints
        self.hub_urls = [
            config.get("clawhub_url", "https://api.clawhub.ai"),
            "https://api.clawhub.dev",  # Legacy, may not work
        ]
        self._loaded_skills: dict[str, Skill] = {}

    async def initialize(self) -> None:
        """Initialize and scan for skills"""
        if not self.skills_dir.exists():
            return

        # Scan local skills
        await self._scan_local_skills()

    async def _scan_local_skills(self) -> None:
        """Scan local skills directory"""
        if not self.skills_dir.exists():
            return

        try:
            for item in self.skills_dir.iterdir():
                if not item.is_dir():
                    continue

                manifest_path = item / "manifest.yaml"
                if not manifest_path.exists():
                    continue

                try:
                    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
                    if not manifest:
                        continue

                    skill = Skill(
                        name=manifest.get("skill", item.name),
                        version=manifest.get("version", "1.0.0"),
                        description=manifest.get("description", ""),
                        path=item,
                        manifest=manifest,
                        source="local",
                    )
                    self._loaded_skills[skill.name] = skill
                    print(f"[DEBUG] Loaded local skill: {skill.name}")
                except Exception as e:
                    print(f"[DEBUG] Failed to load skill from {item}: {e}")
        except Exception as e:
            print(f"[DEBUG] Failed to scan skills directory: {e}")

    async def search_skills(self, query: str) -> list[Skill]:
        """Search skills by query (name or description)"""
        query_lower = query.lower()
        results = []

        # Search in loaded local skills
        for skill in self._loaded_skills.values():
            if query_lower in skill.name.lower() or query_lower in skill.description.lower():
                results.append(skill)

        # Try to search remote if no local results
        if not results:
            # Try each hub URL
            for hub_url in self.hub_urls:
                try:
                    remote_skills = await self._search_remote(query, hub_url)
                    if remote_skills:
                        results.extend(remote_skills)
                        break
                except Exception as e:
                    print(f"[DEBUG] Failed to search {hub_url}: {e}")
                    continue

        # If still no results, try fallback skills from GitHub
        if not results:
            results = self._search_fallback_skills(query_lower)

        return results

    def _search_fallback_skills(self, query: str) -> list[Skill]:
        """Search fallback skills from known GitHub repos"""
        results = []
        for keyword, (repo, name) in self.FALLBACK_SKILLS.items():
            if keyword in query or query in keyword:
                # Create a temporary skill object for fallback
                skill = Skill(
                    name=name,
                    version="1.0.0",
                    description=f"Skill from {repo} (fallback)",
                    path=Path(f"~/.claude/skills/{name}").expanduser(),
                    manifest={"skill": name, "source": "fallback", "repo": repo},
                    source="fallback",
                )
                results.append(skill)
        return results

    async def _search_remote(self, query: str, hub_url: str = None) -> list[Skill]:
        """Search remote ClawHub for skills"""
        if hub_url is None:
            hub_url = self.hub_urls[0] if self.hub_urls else ""

        skills = []
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{hub_url}/skills/search"
                params = {"q": query}
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        for item in data.get("skills", []):
                            skill = Skill(
                                name=item.get("name", ""),
                                version=item.get("version", "1.0.0"),
                                description=item.get("description", ""),
                                path=Path(item.get("path", "")),
                                manifest=item,
                                source="remote",
                            )
                            skills.append(skill)
        except Exception as e:
            print(f"[DEBUG] Remote search error: {e}")
        return skills

    async def download_skill(self, skill_name: str) -> Skill | None:
        """Download a skill from remote hub or GitHub"""
        # Try to download from GitHub first (most common case)
        if "/" in skill_name:
            # Assume it's a GitHub repo URL or owner/repo format
            return await self._download_from_github(skill_name)

        # Try fallback skills first (most reliable for known skills)
        for keyword, (repo, name) in self.FALLBACK_SKILLS.items():
            if skill_name.lower() == name.lower() or skill_name.lower() == keyword:
                print(f"[DEBUG] Using fallback: {repo} for skill {skill_name}")
                result = await self._download_from_github(repo)
                if result:
                    return result

        # Try each hub URL
        for hub_url in self.hub_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"{hub_url}/skills/{skill_name}/download"
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status == 200:
                            return await self._extract_skill(await response.read(), skill_name)
            except Exception as e:
                print(f"[DEBUG] Failed to download skill from {hub_url}: {e}")
                continue

        # Try GitHub as final fallback
        return await self._download_from_github(f"langbot-app/clawhub-{skill_name}")

    async def _download_from_github(self, repo: str) -> Skill | None:
        """Download skill from GitHub"""
        import shutil
        import tempfile

        # Parse owner/repo
        if repo.startswith("https://github.com/"):
            repo = repo.replace("https://github.com/", "")
        if repo.endswith(".git"):
            repo = repo[:-4]

        parts = repo.split("/")
        if len(parts) != 2:
            return None

        owner, repo_name = parts
        download_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/main.zip"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        # Try master branch
                        download_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/master.zip"
                        async with session.get(download_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                            if response.status != 200:
                                print(f"[DEBUG] Failed to download from GitHub: {response.status}")
                                return None

                    # Download and extract
                    return await self._extract_skill(await response.read(), repo_name)

        except Exception as e:
            print(f"[DEBUG] Failed to download from GitHub: {e}")
            return None

    async def _extract_skill(self, zip_data: bytes, skill_name: str) -> Skill | None:
        """Extract skill from zip data"""
        import io
        import shutil
        import zipfile

        try:
            # Create skills directory if not exists
            self.skills_dir.mkdir(parents=True, exist_ok=True)

            # Extract zip
            with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                # Find the skill directory in the zip
                for name in zf.namelist():
                    if "manifest.yaml" in name:
                        # This is the skill root
                        skill_root = name.split("/")[0] if "/" in name else ""
                        break
                else:
                    # No manifest found, use default
                    skill_root = f"{skill_name}-main"

                # Extract to skills directory
                skill_path = self.skills_dir / skill_root.replace("-main", "").replace("-master", "")
                skill_path.mkdir(parents=True, exist_ok=True)

                for member in zf.namelist():
                    if member.startswith(skill_root):
                        filename = member[len(skill_root):].lstrip("/")
                        if filename:
                            target = skill_path / filename
                            if member.endswith("/"):
                                target.mkdir(parents=True, exist_ok=True)
                            else:
                                target.parent.mkdir(parents=True, exist_ok=True)
                                with zf.open(member) as source:
                                    with open(target, "wb") as f:
                                        shutil.copyfileobj(source, f)

            # Reload skills
            await self._scan_local_skills()

            print(f"[DEBUG] Successfully installed skill: {skill_name}")
            return self.get_skill(skill_name.replace("-main", "").replace("-master", ""))

        except Exception as e:
            print(f"[DEBUG] Failed to extract skill: {e}")
            return None

    async def install_skill(self, skill_identifier: str) -> dict[str, Any]:
        """Install a skill by name or GitHub URL"""
        skill = await self.download_skill(skill_identifier)

        if skill:
            return {
                "success": True,
                "skill": skill.name,
                "message": f"Successfully installed skill: {skill.name}"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to install skill: {skill_identifier}"
            }

    def get_skill(self, name: str) -> Skill | None:
        """Get a skill by name"""
        return self._loaded_skills.get(name)

    def get_all_skills(self) -> list[Skill]:
        """Get all loaded skills"""
        return list(self._loaded_skills.values())


class SkillToToolConverter:
    """Converts a Skill to a BasePlannerTool"""

    @staticmethod
    def convert(skill: Skill) -> BasePlannerTool | None:
        """Convert a Skill to a PlannerTool"""
        if not skill.manifest:
            return None

        tool_class = type(
            f"{skill.name.title().replace('-', '')}SkillTool",
            (BasePlannerTool,),
            {
                "_skill": skill,
                "name": skill.name.replace("-", "_"),
                "description": skill.description or f"Skill: {skill.name}",
                "parameters": SkillToToolConverter._convert_parameters(skill.parameters),
                "execute": SkillToToolConverter._create_execute_method(skill),
            },
        )

        return tool_class()

    @staticmethod
    def _convert_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
        """Convert skill parameters to tool parameters schema"""
        if not parameters:
            return {
                "type": "object",
                "properties": {},
            }

        properties = {}
        required = []

        for param_name, param_info in parameters.items():
            prop = {}
            if isinstance(param_info, dict):
                param_type = param_info.get("type", "string")
                param_desc = param_info.get("description", "")
                param_enum = param_info.get("enum")

                prop["type"] = param_type
                if param_desc:
                    prop["description"] = param_desc
                if param_enum:
                    prop["enum"] = param_enum

                if param_info.get("required", False):
                    required.append(param_name)
            else:
                prop["type"] = "string"
                if param_info:
                    prop["description"] = str(param_info)

            properties[param_name] = prop

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }

    @staticmethod
    def _create_execute_method(skill: Skill):
        """Create an execute method for the skill tool"""

        async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
            """Execute the skill"""
            skill_manifest = skill.manifest

            # Check if skill has implementation files
            adds = skill_manifest.get("adds", [])
            modifies = skill_manifest.get("modifies", [])

            if not adds and not modifies:
                return {
                    "success": False,
                    "error": f"Skill '{skill.name}' has no implementation files. This is a code transformation skill that cannot be executed directly.",
                }

            # Check for shell commands in the skill
            # Many skills have commands that can be executed
            # For now, we'll return a message about what the skill does
            return {
                "success": True,
                "skill": skill.name,
                "version": skill.version,
                "description": skill.description,
                "message": f"Skill '{skill.name}' is available. This skill adds: {adds}, modifies: {modifies}. "
                f"To apply this skill to your project, it needs to be executed as a code transformation.",
            }

        return execute
