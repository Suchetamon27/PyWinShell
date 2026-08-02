import os
import sys
from typing import List, TextIO
from .base import BuiltinCommand, builtin_registry

history_list: List[str] = []

def add_to_history(command_line: str):
    if command_line and command_line.strip():
        history_list.append(command_line.strip())

class HistoryCommand(BuiltinCommand):
    name = "history"
    description = "View command history"

    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        for idx, cmd in enumerate(history_list, 1):
            stdout.write(f"{idx:4d}  {cmd}\n")
        return 0

class ClearCommand(BuiltinCommand):
    name = "clear"
    description = "Clear terminal screen"

    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        os.system("cls" if sys.platform == "win32" else "clear")
        return 0

class ClsCommand(ClearCommand):
    name = "cls"

builtin_registry.register(HistoryCommand())
builtin_registry.register(ClearCommand())
builtin_registry.register(ClsCommand())
