import sys
from typing import Dict, List, TextIO
from .base import BuiltinCommand, builtin_registry

alias_map: Dict[str, str] = {
    "ll": "dir",
    "ls": "dir",
    "ps": "task list",
    "neofetch": "sysinfo",
    "grep": "findstr",
}

class AliasCommand(BuiltinCommand):
    name = "alias"
    description = "Manage command aliases (usage: alias name='target_command')"

    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        if not args:
            for k, v in sorted(alias_map.items()):
                stdout.write(f"alias {k}='{v}'\n")
            return 0

        arg_str = " ".join(args)
        if "=" in arg_str:
            name, target = arg_str.split("=", 1)
            name = name.strip()
            target = target.strip().strip("'\"")
            alias_map[name] = target
            stdout.write(f"Alias registered: {name} -> '{target}'\n")
            return 0
        else:
            name = args[0]
            if name in alias_map:
                stdout.write(f"alias {name}='{alias_map[name]}'\n")
                return 0
            else:
                stdout.write(f"alias: '{name}' not found\n")
                return 1

class UnaliasCommand(BuiltinCommand):
    name = "unalias"
    description = "Remove a command alias"

    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        if not args:
            stdout.write("unalias: missing alias name\n")
            return 1
        name = args[0]
        if name in alias_map:
            del alias_map[name]
            stdout.write(f"Removed alias: {name}\n")
            return 0
        else:
            stdout.write(f"unalias: '{name}' not found\n")
            return 1

builtin_registry.register(AliasCommand())
builtin_registry.register(UnaliasCommand())
