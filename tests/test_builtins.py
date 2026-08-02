import io
import unittest
from pywinshell.builtins import builtin_registry
import pywinshell.builtins.filesystem
import pywinshell.builtins.history
import pywinshell.builtins.env

class TestBuiltins(unittest.TestCase):

    def test_registry(self):
        self.assertTrue(builtin_registry.has("cd"))
        self.assertTrue(builtin_registry.has("pwd"))
        self.assertTrue(builtin_registry.has("sysinfo"))
        self.assertTrue(builtin_registry.has("task"))
        self.assertTrue(builtin_registry.has("winenv"))

    def test_pwd(self):
        cmd = builtin_registry.get("pwd")
        out = io.StringIO()
        res = cmd.execute([], stdout=out)
        self.assertEqual(res, 0)
        self.assertIn("Downloads", out.getvalue())

    def test_winenv(self):
        cmd = builtin_registry.get("winenv")
        out = io.StringIO()
        res = cmd.execute(["set", "TEST_VAR", "12345"], stdout=out)
        self.assertEqual(res, 0)

        out2 = io.StringIO()
        res2 = cmd.execute(["get", "TEST_VAR"], stdout=out2)
        self.assertEqual(res2, 0)
        self.assertIn("12345", out2.getvalue())

if __name__ == "__main__":
    unittest.main()
