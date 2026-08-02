import sys
from typing import List, TextIO
import psutil
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from .base import BuiltinCommand, builtin_registry

class TaskCommand(BuiltinCommand):
    name = "task"
    description = "Windows Task Manager utility (list, kill, tree, suspend, resume)"

    def execute(self, args: List[str], stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
        if not args:
            return self._list_tasks(stdout)

        subcmd = args[0].lower()
        if subcmd in ("list", "ls"):
            return self._list_tasks(stdout, filter_term=args[1] if len(args) > 1 else None)
        elif subcmd == "kill":
            if len(args) < 2:
                stdout.write("task kill: missing PID or process name\n")
                return 1
            return self._kill_task(args[1], stdout)
        elif subcmd == "tree":
            return self._task_tree(stdout)
        elif subcmd == "suspend":
            if len(args) < 2:
                stdout.write("task suspend: missing PID\n")
                return 1
            return self._change_state(args[1], suspend=True, stdout=stdout)
        elif subcmd == "resume":
            if len(args) < 2:
                stdout.write("task resume: missing PID\n")
                return 1
            return self._change_state(args[1], suspend=False, stdout=stdout)
        else:
            stdout.write(f"task: unknown subcommand '{subcmd}'. Options: list, kill, tree, suspend, resume\n")
            return 1

    def _list_tasks(self, stdout: TextIO, filter_term: str = None) -> int:
        console = Console(file=stdout)
        table = Table(title="Active Windows Processes", show_header=True, header_style="bold magenta")
        table.add_column("PID", justify="right", style="cyan", width=8)
        table.add_column("Name", style="bold green", width=25)
        table.add_column("Status", width=12)
        table.add_column("Memory (MB)", justify="right", width=14)
        table.add_column("Threads", justify="right", width=10)

        count = 0
        for proc in psutil.process_iter(['pid', 'name', 'status', 'memory_info', 'num_threads']):
            try:
                pinfo = proc.info
                pname = pinfo['name'] or "Unknown"

                if filter_term and filter_term.lower() not in pname.lower():
                    continue

                pid = str(pinfo['pid'])
                status = pinfo['status'] or "running"
                mem_mb = round((pinfo['memory_info'].rss if pinfo['memory_info'] else 0) / (1024 * 1024), 1)
                threads = str(pinfo['num_threads'] or 0)

                table.add_row(pid, pname, status, str(mem_mb), threads)
                count += 1
                if count >= 50 and not filter_term:
                    table.caption = "Showing top 50 processes. Use 'task list <filter>' to search."
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        console.print(table)
        return 0

    def _kill_task(self, target: str, stdout: TextIO) -> int:
        killed = 0
        if target.isdigit():
            pid = int(target)
            try:
                proc = psutil.Process(pid)
                pname = proc.name()
                proc.kill()
                stdout.write(f"Successfully killed process '{pname}' (PID: {pid})\n")
                return 0
            except Exception as e:
                stdout.write(f"Failed to kill PID {pid}: {e}\n")
                return 1
        else:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() == target.lower():
                        proc.kill()
                        killed += 1
                except Exception:
                    pass
            stdout.write(f"Killed {killed} process(es) matching '{target}'\n")
            return 0 if killed > 0 else 1

    def _change_state(self, target: str, suspend: bool, stdout: TextIO) -> int:
        if not target.isdigit():
            stdout.write("Error: PID must be a number\n")
            return 1
        pid = int(target)
        try:
            proc = psutil.Process(pid)
            if suspend:
                proc.suspend()
                stdout.write(f"Suspended process '{proc.name()}' (PID: {pid})\n")
            else:
                proc.resume()
                stdout.write(f"Resumed process '{proc.name()}' (PID: {pid})\n")
            return 0
        except Exception as e:
            stdout.write(f"Failed to change state of PID {pid}: {e}\n")
            return 1

    def _task_tree(self, stdout: TextIO) -> int:
        console = Console(file=stdout)
        root_tree = Tree("🪟 [bold cyan]Windows Process Hierarchy[/bold cyan]")
        
        # Build process map
        procs = {}
        for proc in psutil.process_iter(['pid', 'ppid', 'name']):
            try:
                procs[proc.info['pid']] = proc.info
            except Exception:
                pass

        # Find top level processes (ppid not in procs or ppid == 0)
        added_pids = set()
        for pid, info in list(procs.items())[:30]:
            if pid not in added_pids:
                node = root_tree.add(f"[green]{info['name']}[/green] (PID: {pid})")
                added_pids.add(pid)

        console.print(root_tree)
        return 0

builtin_registry.register(TaskCommand())
