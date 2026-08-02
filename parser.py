from typing import List, Optional
from .lexer import Token, TokenType, tokenize

class CommandNode:
    """Represents a single command with arguments and file redirections."""
    def __init__(self, args: List[str]):
        self.args = args
        self.stdin_file: Optional[str] = None
        self.stdout_file: Optional[str] = None
        self.append_stdout: bool = False

    def __repr__(self):
        return (f"CommandNode(args={self.args}, stdin={repr(self.stdin_file)}, "
                f"stdout={repr(self.stdout_file)}, append={self.append_stdout})")

class PipelineNode:
    """Represents a sequence of commands connected by pipes (|)."""
    def __init__(self, commands: List[CommandNode], background: bool = False):
        self.commands = commands
        self.background = background

    def __repr__(self):
        return f"PipelineNode(commands={self.commands}, background={self.background})"

class ParseError(Exception):
    pass

def parse_line(line: str) -> Optional[PipelineNode]:
    """Parse a raw command line string into a PipelineNode AST."""
    tokens = tokenize(line)
    if not tokens:
        return None

    commands: List[CommandNode] = []
    current_args: List[str] = []
    current_cmd = CommandNode([])
    background = False

    i = 0
    num_tokens = len(tokens)

    while i < num_tokens:
        tok = tokens[i]

        if tok.type == TokenType.WORD:
            current_args.append(tok.value)
            i += 1

        elif tok.type == TokenType.REDIRECT_OUT:
            if i + 1 >= num_tokens or tokens[i + 1].type != TokenType.WORD:
                raise ParseError("Syntax error: expected filename after '>'")
            current_cmd.stdout_file = tokens[i + 1].value
            current_cmd.append_stdout = False
            i += 2

        elif tok.type == TokenType.REDIRECT_APPEND:
            if i + 1 >= num_tokens or tokens[i + 1].type != TokenType.WORD:
                raise ParseError("Syntax error: expected filename after '>>'")
            current_cmd.stdout_file = tokens[i + 1].value
            current_cmd.append_stdout = True
            i += 2

        elif tok.type == TokenType.REDIRECT_IN:
            if i + 1 >= num_tokens or tokens[i + 1].type != TokenType.WORD:
                raise ParseError("Syntax error: expected filename after '<'")
            current_cmd.stdin_file = tokens[i + 1].value
            i += 2

        elif tok.type == TokenType.PIPE:
            if not current_args:
                raise ParseError("Syntax error: empty command before '|'")
            current_cmd.args = current_args
            commands.append(current_cmd)

            # Reset for next command in pipe chain
            current_args = []
            current_cmd = CommandNode([])
            i += 1

        elif tok.type == TokenType.BACKGROUND:
            if i != num_tokens - 1:
                raise ParseError("Syntax error: '&' must be at the end of the line")
            background = True
            i += 1

        else:
            raise ParseError(f"Syntax error: unexpected token {tok.value}")

    if current_args:
        current_cmd.args = current_args
        commands.append(current_cmd)
    elif not commands:
        raise ParseError("Syntax error: empty command")

    return PipelineNode(commands, background)
