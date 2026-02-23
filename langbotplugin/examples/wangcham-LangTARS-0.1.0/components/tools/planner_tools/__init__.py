# Base tool class for planner
# All planner tools should inherit from this class

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BasePlannerTool(ABC):
    """Base class for planner tools"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for LLM"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """Tool parameters schema"""
        pass

    @abstractmethod
    async def execute(self, helper_plugin: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute the tool"""
        pass

    def to_openai_format(self) -> dict[str, Any]:
        """Convert to OpenAI function calling format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
