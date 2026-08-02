import os
from prompt_toolkit.formatted_text import HTML
from .win32_utils import is_admin, get_git_branch

class ShellPrompt:
    """Generates styled HTML prompts for prompt_toolkit REPL."""

    @staticmethod
    def get_prompt_tokens() -> HTML:
        admin = is_admin()
        cwd = os.getcwd()

        # Format cwd for display (shorten home directory if needed)
        home = os.path.expanduser("~")
        if cwd.startswith(home):
            cwd_disp = "~" + cwd[len(home):]
        else:
            cwd_disp = cwd

        # Clean path formatting
        cwd_disp = cwd_disp.replace("\\", "/")

        git_branch = get_git_branch(os.getcwd())

        # Construct prompt string
        parts = []

        # 1. Admin badge
        if admin:
            parts.append('<style bg="#d70000" fg="#ffffff"><b> ⚡ ADMIN </b></style>')
        else:
            parts.append('<style bg="#2b2b2b" fg="#808080"><b> 👤 USER </b></style>')

        # 2. Path badge
        parts.append(f'<style bg="#005f87" fg="#ffffff"> 📁 {cwd_disp} </style>')

        # 3. Git branch (if available)
        if git_branch:
            parts.append(f'<style bg="#5f8700" fg="#ffffff"> 🌿 {git_branch} </style>')

        # 4. Prompt arrow
        arrow_color = "#d70000" if admin else "#00aaff"
        parts.append(f'<style fg="{arrow_color}"><b> ❯ </b></style>')

        return HTML("".join(parts))

    @staticmethod
    def get_plain_prompt() -> str:
        """Fallback plain text prompt."""
        admin_prefix = "[ADMIN] " if is_admin() else ""
        return f"{admin_prefix}{os.getcwd()}> "
