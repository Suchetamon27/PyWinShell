import os
import sys
import datetime
from typing import List, TextIO
from rich.console import Console
from rich.table import Table
from .base import BuiltinCommand, builtin_registry

class CdCommand(BuiltinCommand):
    name = "cd"
    description = "Change current directory (supports Windows drive letters e.g. D:)"

    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        if not args:
            target = os.path.expanduser("~")
        else:
            target = args[0]

        # Check drive letter switch like "D:" or "D:\"
        if len(target) == 2 and target[1] == ":" and target[0].isalpha():
            target = target + "\\"

        try:
            os.chdir(os.path.expanduser(target))
            return 0
        except FileNotFoundError:
            stdout.write(f"cd: directory not found: {target}\n")
            return 1
        except PermissionError:
            stdout.write(f"cd: permission denied: {target}\n")
            return 1
        except Exception as e:
            stdout.write(f"cd: error changing directory: {e}\n")
            return 1

class PwdCommand(BuiltinCommand):
    name = "pwd"
    description = "Print working directory"

    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        stdout.write(f"{os.getcwd()}\n")
        return 0

class DirCommand(BuiltinCommand):
    name = "dir"
    description = "List directory contents with rich formatting"

    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        target_dir = args[0] if args else "."
        try:
            entries = os.listdir(target_dir)
        except Exception as e:
            stdout.write(f"dir: error reading '{target_dir}': {e}\n")
            return 1

        console = Console(file=stdout)
        table = Table(title=f"Directory: {os.path.abspath(target_dir)}", show_header=True, header_style="bold blue")
        table.add_column("Mode", style="dim", width=8)
        table.add_column("Last Write Time", width=20)
        table.add_column("Size", justify="right", width=12)
        table.add_column("Name")

        for name in sorted(entries):
            full_path = os.path.join(target_dir, name)
            try:
                stat = os.stat(full_path)
                is_dir = os.path.pathsep if os.path.isdir(full_path) else False
                is_dir_flag = os.path.isdir(full_path)

                mode = "d-----" if is_dir_flag else "-a----"
                mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")

                if is_dir_flag:
                    size_str = "<DIR>"
                    name_styled = f"[bold cyan]{name}/[/bold cyan]"
                else:
                    size = stat.st_size
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size / 1024:.1f} KB"
                    else:
                        size_str = f"{size / (1024 * 1024):.1f} MB"
                    name_styled = f"[green]{name}[/green]"

                table.add_row(mode, mtime, size_str, name_styled)
            except Exception:
                table.add_row("??????", "????-??-?? ??:??", "?", name)

        console.print(table)
        return 0

class CatCommand(BuiltinCommand):
    name = "cat"
    description = "Concatenate and display file content"

    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        if not args:
            stdout.write(stdin.read())
            return 0

        for filepath in args:
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    stdout.write(f.read())
            except Exception as e:
                stdout.write(f"cat: error reading '{filepath}': {e}\n")
                return 1
        return 0

class MkdirCommand(BuiltinCommand):
    name = "mkdir"
    description = "Create a directory"

    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        if not args:
            stdout.write("mkdir: missing operand\n")
            return 1
        for path in args:
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                stdout.write(f"mkdir: error creating '{path}': {e}\n")
                return 1
        return 0

# Register commands
builtin_registry.register(CdCommand())
builtin_registry.register(PwdCommand())
builtin_registry.register(DirCommand())
builtin_registry.register(CatCommand())
builtin_registry.register(MkdirCommand())
