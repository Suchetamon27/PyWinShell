from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TextIO
import sys

class BuiltinCommand(ABC):
    """Base class for all PyWinShell built-in commands."""
    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        """
        Execute the command.
        Returns returncode (0 for success, non-zero for error).
        """
        pass

class BuiltinRegistry:
    """Registry managing available built-in commands."""

    def __init__(self):
        self._commands: Dict[str, BuiltinCommand] = {}

    def register(self, command: BuiltinCommand):
        self._commands[command.name.lower()] = command

    def get(self, name: str) -> Optional[BuiltinCommand]:
        return self._commands.get(name.lower())

    def has(self, name: str) -> bool:
        return name.lower() in self._commands

    def list_all(self) -> Dict[str, str]:
        return {cmd.name: cmd.description for cmd in self._commands.values()}

# Global singleton registry
builtin_registry = BuiltinRegistry()
