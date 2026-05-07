import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from scripts.notifier.logger import configure_debug, debug_log


class LoggerTests(unittest.TestCase):
    def test_debug_log_writes_to_stdout_when_enabled(self) -> None:
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        configure_debug({"AGENT_NOTIFICATION_DEBUG": "1"})
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            debug_log("hello")

        self.assertIn("hello", stdout_buffer.getvalue())
        self.assertEqual("", stderr_buffer.getvalue())


if __name__ == "__main__":
    unittest.main()