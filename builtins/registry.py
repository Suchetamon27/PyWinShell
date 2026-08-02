import sys
from typing import List, TextIO
from rich.console import Console
from rich.table import Table
from .base import BuiltinCommand, builtin_registry
from ..win32_utils import query_registry_key

class RegCommand(BuiltinCommand):
    name = "reg"
    description = "Inspect Windows Registry keys (e.g., reg query HKCU Software)"

    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        if not args or len(args) < 2 or args[0].lower() != "query":
            stdout.write("Usage: reg query <HIVE> <PATH>\n")
            stdout.write("Example: reg query HKCU Software\\Microsoft\\Windows\\CurrentVersion\n")
            return 1

        hive = args[1]
        key_path = args[2] if len(args) > 2 else ""

        try:
            entries = query_registry_key(hive, key_path)
            console = Console(file=stdout)
            table = Table(title=f"Registry: {hive.upper()}\\{key_path}", show_header=True, header_style="bold yellow")
            table.add_column("Value Name", style="bold cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Data", style="green")

            for name, val, val_type in entries:
                val_str = str(val)
                if len(val_str) > 60:
                    val_str = val_str[:57] + "..."
                table.add_row(name, val_type, val_str)

            console.print(table)
            return 0
        except Exception as e:
            stdout.write(f"reg query error: {e}\n")
            return 1

builtin_registry.register(RegCommand())
