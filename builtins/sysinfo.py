import sys
from typing import List, TextIO
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from .base import BuiltinCommand, builtin_registry
from ..win32_utils import get_system_summary

WINDOWS_LOGO = """\
[bold blue]
  ████████  ████████
  ████████  ████████
  ████████  ████████

  ████████  ████████
  ████████  ████████
  ████████  ████████
[/bold blue]"""

class SysInfoCommand(BuiltinCommand):
    name = "sysinfo"
    description = "Display Windows system specs and status summary (neofetch style)"

    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        summary = get_system_summary()
        console = Console(file=stdout)

        info_text = Text()
        info_text.append(f"OS: ", style="bold cyan")
        info_text.append(f"{summary['os']} ({summary['arch']})\n")

        info_text.append(f"Host: ", style="bold cyan")
        info_text.append(f"{summary['hostname']}\n")

        info_text.append(f"Privileges: ", style="bold cyan")
        admin_str = "[bold red]Administrator ⚡[/bold red]" if summary['admin'] else "[green]Standard User 👤[/green]"
        info_text.append_text(Text.from_markup(f"{admin_str}\n"))

        info_text.append(f"Uptime: ", style="bold cyan")
        info_text.append(f"{summary['uptime_hours']} hours\n")

        info_text.append(f"CPU: ", style="bold cyan")
        info_text.append(f"{summary['cpu_cores']} @ {summary['cpu_usage']} usage\n")

        info_text.append(f"Memory: ", style="bold cyan")
        info_text.append(f"{summary['mem_used_gb']} GB / {summary['mem_total_gb']} GB ({summary['mem_percent']})\n")

        info_text.append(f"Disk (C:): ", style="bold cyan")
        info_text.append(f"{summary['disk_free_gb']} GB free / {summary['disk_total_gb']} GB total ({summary['disk_percent']} used)\n")

        panel = Panel(
            info_text,
            title="[bold yellow]PyWinShell System Dashboard[/bold yellow]",
            border_style="bright_blue",
            expand=False
        )

        console.print(Columns([WINDOWS_LOGO, panel]))
        return 0

builtin_registry.register(SysInfoCommand())
