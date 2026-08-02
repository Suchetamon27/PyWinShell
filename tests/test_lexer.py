import unittest
from pywinshell.lexer import tokenize, TokenType, Token

class TestLexer(unittest.TestCase):

    def test_simple_words(self):
        tokens = tokenize("echo hello world")
        expected = [
            Token(TokenType.WORD, "echo"),
            Token(TokenType.WORD, "hello"),
            Token(TokenType.WORD, "world")
        ]
        self.assertEqual(tokens, expected)

    def test_quoted_arguments(self):
        tokens = tokenize('echo "hello world" \'foo bar\'')
        expected = [
            Token(TokenType.WORD, "echo"),
            Token(TokenType.WORD, "hello world"),
            Token(TokenType.WORD, "foo bar")
        ]
        self.assertEqual(tokens, expected)

    def test_pipe_and_redirection(self):
        tokens = tokenize("dir | findstr py > out.txt >> append.txt < in.txt &")
        expected = [
            Token(TokenType.WORD, "dir"),
            Token(TokenType.PIPE, "|"),
            Token(TokenType.WORD, "findstr"),
            Token(TokenType.WORD, "py"),
            Token(TokenType.REDIRECT_OUT, ">"),
            Token(TokenType.WORD, "out.txt"),
            Token(TokenType.REDIRECT_APPEND, ">>"),
            Token(TokenType.WORD, "append.txt"),
            Token(TokenType.REDIRECT_IN, "<"),
            Token(TokenType.WORD, "in.txt"),
            Token(TokenType.BACKGROUND, "&")
        ]
        self.assertEqual(tokens, expected)

if __name__ == "__main__":
    unittest.main()
