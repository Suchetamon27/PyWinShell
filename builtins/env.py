import os
import sys
from typing import List, TextIO
from rich.console import Console
from rich.table import Table
from .base import BuiltinCommand, builtin_registry

class WinEnvCommand(BuiltinCommand):
    name = "winenv"
    description = "View and modify shell environment variables (winenv [get/set/list])"

    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        if not args or args[0].lower() in ("list", "ls"):
            return self._list_env(stdout)

        subcmd = args[0].lower()
        if subcmd == "get":
            if len(args) < 2:
                stdout.write("winenv get: missing variable name\n")
                return 1
            var_name = args[1]
            val = os.environ.get(var_name, os.environ.get(var_name.upper()))
            if val is not None:
                stdout.write(f"{var_name} = {val}\n")
                return 0
            else:
                stdout.write(f"Environment variable '{var_name}' not set.\n")
                return 1

        elif subcmd == "set":
            if len(args) < 3:
                stdout.write("winenv set: missing variable name or value (usage: winenv set VAR VALUE)\n")
                return 1
            var_name = args[1]
            val = " ".join(args[2:])
            os.environ[var_name] = val
            stdout.write(f"Set environment variable {var_name} = {val}\n")
            return 0

        else:
            stdout.write(f"winenv: unknown command '{subcmd}'. Usage: winenv [list|get VAR|set VAR VAL]\n")
            return 1

    def _list_env(self, stdout: TextIO) -> int:
        console = Console(file=stdout)
        table = Table(title="Environment Variables", show_header=True, header_style="bold green")
        table.add_column("Variable", style="bold cyan", width=25)
        table.add_column("Value", style="dim")

        for k in sorted(os.environ.keys()):
            val = os.environ[k]
            if len(val) > 70:
                val = val[:67] + "..."
            table.add_row(k, val)

        console.print(table)
        return 0

builtin_registry.register(WinEnvCommand())
