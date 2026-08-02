import os
import sys
from typing import Iterable, Set
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from .builtins import builtin_registry
from .builtins.alias import alias_map

def get_path_executables() -> Set[str]:
    """Scan PATH environment variable for executable files on Windows."""
    executables = set()
    path_env = os.environ.get("PATH", "")
    pathext = os.environ.get("PATHEXT", ".EXE;.BAT;.CMD;.PS1").upper().split(";")

    for dir_path in path_env.split(os.path.pathsep):
        if not dir_path or not os.path.exists(dir_path):
            continue
        try:
            for entry in os.listdir(dir_path):
                base, ext = os.path.splitext(entry)
                if ext.upper() in pathext:
                    executables.add(base.lower())
                    executables.add(entry.lower())
        except Exception:
            pass
    return executables

class PyWinShellCompleter(Completer):
    """Custom autocompleter for PyWinShell REPL."""

    def __init__(self):
        self.cached_executables = get_path_executables()

    def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
        text_before_cursor = document.text_before_cursor
        words = text_before_cursor.lstrip().split()

        if not words or (len(words) == 1 and not text_before_cursor.endswith(" ")):
            # Completing command name
            word_to_complete = words[0] if words else ""
            
            # 1. Builtins
            for name in builtin_registry.list_all().keys():
                if name.startswith(word_to_complete.lower()):
                    yield Completion(name, start_position=-len(word_to_complete), display_meta="Built-in")

            # 2. Aliases
            for name in alias_map.keys():
                if name.startswith(word_to_complete.lower()):
                    yield Completion(name, start_position=-len(word_to_complete), display_meta="Alias")

            # 3. Executables in PATH
            for exe in self.cached_executables:
                if exe.startswith(word_to_complete.lower()):
                    yield Completion(exe, start_position=-len(word_to_complete), display_meta="Executable")

        else:
            # Completing path or argument
            word_to_complete = document.get_word_under_cursor(WORD=True)
            
            # Expand ~
            expanded_word = os.path.expanduser(word_to_complete)
            dirname = os.path.dirname(expanded_word)
            prefix = os.path.basename(expanded_word)

            search_dir = dirname if dirname else "."
            try:
                if os.path.exists(search_dir) and os.path.isdir(search_dir):
                    for entry in os.listdir(search_dir):
                        if entry.lower().startswith(prefix.lower()):
                            is_dir = os.path.isdir(os.path.join(search_dir, entry))
                            completion_text = entry + ("/" if is_dir else "")
                            yield Completion(
                                completion_text,
                                start_position=-len(prefix),
                                display_meta="Directory" if is_dir else "File"
                            )
            except Exception:
                pass
