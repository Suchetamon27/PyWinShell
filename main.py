import os
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.panel import Panel

from .prompt import ShellPrompt
from .completion import PyWinShellCompleter
from .parser import parse_line, ParseError
from .executor import Executor
from .builtins.history import add_to_history
from .win32_utils import is_admin, get_system_summary

WELCOME_BANNER = """\
[bold cyan]PyWinShell v1.0.0[/bold cyan] — [dim]A modern interactive shell for Windows[/dim]
Type [bold yellow]'sysinfo'[/bold yellow] for dashboard, [bold yellow]'task'[/bold yellow] for process monitor, [bold yellow]'help'[/bold yellow] for builtins, [bold yellow]'exit'[/bold yellow] to quit.
"""

def print_help():
    console = Console()
    console.print(Panel.fit(
        "[bold cyan]PyWinShell Built-in Commands:[/bold cyan]\n\n"
        "  [bold yellow]sysinfo[/bold yellow]       - Windows hardware, CPU, RAM, & OS status dashboard\n"
        "  [bold yellow]task[/bold yellow]          - Windows Task Manager (list, kill, tree, suspend, resume)\n"
        "  [bold yellow]reg[/bold yellow]           - Inspect Windows Registry keys (e.g. reg query HKCU Software)\n"
        "  [bold yellow]winenv[/bold yellow]        - View and modify shell environment variables\n"
        "  [bold yellow]cd / pwd / dir[/bold yellow]- File system navigation (supports Windows drive letters e.g. D:)\n"
        "  [bold yellow]cat / mkdir[/bold yellow]   - Display file content / Create directories\n"
        "  [bold yellow]alias[/bold yellow]         - Create custom command shortcuts (e.g. alias ps='task list')\n"
        "  [bold yellow]history / cls[/bold yellow] - Command history and clear screen\n"
        "  [bold yellow]exit / quit[/bold yellow]   - Close PyWinShell session\n\n"
        "[dim]Pipelines (|) and Redirection (>, >>, <) and Background execution (&) are fully supported.[/dim]",
        title="[bold yellow]PyWinShell Help[/bold yellow]",
        border_style="cyan"
    ))

def main():
    console = Console()
    console.print(WELCOME_BANNER)

    if is_admin():
        console.print("[bold red]⚡ Running with Elevated Administrator Privileges[/bold red]\n")

    history_path = os.path.expanduser("~/.pywinshell_history")
    session = PromptSession(
        history=FileHistory(history_path),
        completer=PyWinShellCompleter(),
    )

    while True:
        try:
            line = session.prompt(ShellPrompt.get_prompt_tokens())
            line_str = line.strip()

            if not line_str:
                continue

            add_to_history(line_str)

            if line_str.lower() in ("exit", "quit"):
                console.print("[bold yellow]Goodbye![/bold yellow]")
                break

            if line_str.lower() == "help":
                print_help()
                continue

            # Parse and Execute AST
            pipeline_ast = parse_line(line_str)
            if pipeline_ast:
                Executor.execute_pipeline(pipeline_ast)

        except ParseError as pe:
            console.print(f"[bold red]{pe}[/bold red]")
        except KeyboardInterrupt:
            console.print("\n[dim]Use 'exit' or Ctrl+D to quit.[/dim]")
            continue
        except EOFError:
            console.print("\n[bold yellow]Goodbye![/bold yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]PyWinShell Error: {e}[/bold red]")

if __name__ == "__main__":
    main()
