import io
import os
import subprocess
import sys
from typing import List, Optional, TextIO, Tuple
from .parser import CommandNode, PipelineNode
from .builtins import builtin_registry
from .builtins.alias import alias_map

class Executor:
    """Executes PipelineNode AST structures, managing pipes, redirection, and processes."""

    @staticmethod
    def execute_pipeline(pipeline: PipelineNode) -> int:
        if not pipeline or not pipeline.commands:
            return 0

        # Expand aliases for all commands in pipeline
        for cmd in pipeline.commands:
            if cmd.args and cmd.args[0] in alias_map:
                alias_expansion = alias_map[cmd.args[0]].split()
                cmd.args = alias_expansion + cmd.args[1:]

        # Handle single built-in command without pipes or background
        if len(pipeline.commands) == 1:
            cmd_node = pipeline.commands[0]
            if cmd_node.args and builtin_registry.has(cmd_node.args[0]):
                return Executor._execute_builtin_single(cmd_node, pipeline.background)

        # Handle complex pipeline or external processes
        return Executor._execute_pipeline_process_chain(pipeline)

    @staticmethod
    def _execute_builtin_single(cmd_node: CommandNode, background: bool) -> int:
        builtin_cmd = builtin_registry.get(cmd_node.args[0])
        if not builtin_cmd:
            return 1

        stdin_stream: TextIO = sys.stdin
        stdout_stream: TextIO = sys.stdout
        file_in = None
        file_out = None

        try:
            if cmd_node.stdin_file:
                file_in = open(cmd_node.stdin_file, "r")
                stdin_stream = file_in

            if cmd_node.stdout_file:
                mode = "a" if cmd_node.append_stdout else "w"
                file_out = open(cmd_node.stdout_file, mode, encoding="utf-8")
                stdout_stream = file_out

            code = builtin_cmd.execute(cmd_node.args[1:], stdin=stdin_stream, stdout=stdout_stream)
            return code
        finally:
            if file_in:
                file_in.close()
            if file_out:
                file_out.close()

    @staticmethod
    def _execute_pipeline_process_chain(pipeline: PipelineNode) -> int:
        procs: List[subprocess.Popen] = []
        prev_pipe = None
        last_returncode = 0

        num_cmds = len(pipeline.commands)

        for i, cmd_node in enumerate(pipeline.commands):
            is_first = (i == 0)
            is_last = (i == num_cmds - 1)

            # Determine stdin
            if is_first:
                if cmd_node.stdin_file:
                    stdin_fd = open(cmd_node.stdin_file, "rb")
                else:
                    stdin_fd = None
            else:
                stdin_fd = prev_pipe

            # Determine stdout
            if is_last:
                if cmd_node.stdout_file:
                    mode = "ab" if cmd_node.append_stdout else "wb"
                    stdout_fd = open(cmd_node.stdout_file, mode)
                else:
                    stdout_fd = None
            else:
                stdout_fd = subprocess.PIPE

            # Execute command (builtin wrapper or external executable)
            if cmd_node.args and builtin_registry.has(cmd_node.args[0]):
                # Builtin inside pipe chain: capture output into pipe stream
                builtin_cmd = builtin_registry.get(cmd_node.args[0])
                capture_out = io.StringIO()
                ret = builtin_cmd.execute(cmd_node.args[1:], stdout=capture_out)
                out_bytes = capture_out.getvalue().encode("utf-8")

                if not is_last:
                    # Feed output to next subprocess via Popen echo/python wrapper
                    proc = subprocess.Popen(
                        [sys.executable, "-c", "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())"],
                        stdin=subprocess.PIPE,
                        stdout=stdout_fd
                    )
                    if proc.stdin:
                        proc.stdin.write(out_bytes)
                        proc.stdin.close()
                    procs.append(proc)
                    prev_pipe = proc.stdout
                else:
                    if stdout_fd:
                        stdout_fd.write(out_bytes)
                        stdout_fd.close()
                    else:
                        sys.stdout.write(capture_out.getvalue())
                    last_returncode = ret
            else:
                # External process (CMD, PowerShell, or Windows executable)
                try:
                    creation_flags = 0
                    if pipeline.background:
                        creation_flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

                    # On Windows, try cmd.exe /c if executable not found directly
                    cmd_args = cmd_node.args
                    proc = subprocess.Popen(
                        cmd_args,
                        stdin=stdin_fd,
                        stdout=stdout_fd,
                        stderr=None,
                        shell=(sys.platform == "win32"),
                        creationflags=creation_flags
                    )
                    procs.append(proc)
                    if not is_last:
                        prev_pipe = proc.stdout
                except Exception as e:
                    sys.stderr.write(f"PyWinShell: command not found or failed to execute: '{cmd_node.args[0]}'\n")
                    return 127

        if pipeline.background:
            sys.stdout.write(f"[Background process launched with {len(procs)} job(s)]\n")
            return 0

        # Wait for processes to finish
        for p in procs:
            p.wait()
            if p.returncode is not None:
                last_returncode = p.returncode

        return last_returncode
