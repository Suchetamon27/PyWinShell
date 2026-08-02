import unittest
from pywinshell.parser import parse_line, ParseError

class TestParser(unittest.TestCase):

    def test_single_command(self):
        pipeline = parse_line("sysinfo")
        self.assertIsNotNone(pipeline)
        self.assertEqual(len(pipeline.commands), 1)
        self.assertEqual(pipeline.commands[0].args, ["sysinfo"])
        self.assertFalse(pipeline.background)

    def test_pipeline_parsing(self):
        pipeline = parse_line("dir | findstr py")
        self.assertEqual(len(pipeline.commands), 2)
        self.assertEqual(pipeline.commands[0].args, ["dir"])
        self.assertEqual(pipeline.commands[1].args, ["findstr", "py"])

    def test_redirection_parsing(self):
        pipeline = parse_line("echo hello > out.txt")
        cmd = pipeline.commands[0]
        self.assertEqual(cmd.args, ["echo", "hello"])
        self.assertEqual(cmd.stdout_file, "out.txt")
        self.assertFalse(cmd.append_stdout)

    def test_background_parsing(self):
        pipeline = parse_line("notepad &")
        self.assertTrue(pipeline.background)

    def test_syntax_error(self):
        with self.assertRaises(ParseError):
            parse_line("echo >")

if __name__ == "__main__":
    unittest.main()
