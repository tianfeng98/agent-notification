import io
import unittest
import urllib.error
from contextlib import redirect_stdout
from unittest.mock import patch

from notifier.http_client import post_json
from notifier.logger import configure_debug


class _FakeResponse:
    def __init__(self, body: bytes, status: int = 200) -> None:
        self._body = body
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self._body


class HttpClientTests(unittest.TestCase):
    def test_post_json_logs_response_body_when_debug_enabled(self) -> None:
        stdout_buffer = io.StringIO()
        configure_debug({"AGENT_NOTIFICATION_DEBUG": "1"})

        with patch("urllib.request.urlopen", return_value=_FakeResponse(b'{"ok":true}')):
            with redirect_stdout(stdout_buffer):
                post_json("https://example.com/webhook", {"text": "hello"})

        output = stdout_buffer.getvalue()
        self.assertIn("http post done", output)
        self.assertIn("response_body='{\"ok\":true}'", output)

    def test_post_json_logs_response_body_for_http_error(self) -> None:
        stdout_buffer = io.StringIO()
        configure_debug({"AGENT_NOTIFICATION_DEBUG": "1"})
        error = urllib.error.HTTPError(
            url="https://example.com/webhook",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"bad request"}'),
        )

        with patch("urllib.request.urlopen", side_effect=error):
            with redirect_stdout(stdout_buffer):
                with self.assertRaises(urllib.error.HTTPError):
                    post_json("https://example.com/webhook", {"text": "hello"})

        output = stdout_buffer.getvalue()
        self.assertIn("http post failed", output)
        self.assertIn("response_body='{\"error\":\"bad request\"}'", output)


if __name__ == "__main__":
    unittest.main()