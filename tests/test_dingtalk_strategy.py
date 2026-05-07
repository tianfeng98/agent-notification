import base64
import hashlib
import hmac
import unittest
import urllib.parse
from unittest.mock import patch

from notifier.strategies.dingtalk import DingTalkStrategy


class DingTalkStrategyTests(unittest.TestCase):
    def test_sign_uses_real_newline_separator(self) -> None:
        strategy = DingTalkStrategy()
        secret = "SEC_test_secret"

        with patch("notifier.strategies.dingtalk.time.time", return_value=1700000000.123):
            timestamp, sign = strategy._sign(secret)

        expected_timestamp = "1700000000123"
        payload = f"{expected_timestamp}\n{secret}".encode("utf-8")
        expected_digest = hmac.new(
            secret.encode("utf-8"), payload, digestmod=hashlib.sha256
        ).digest()
        expected_sign = urllib.parse.quote_plus(
            base64.b64encode(expected_digest).decode("utf-8")
        )

        self.assertEqual(expected_timestamp, timestamp)
        self.assertEqual(expected_sign, sign)

    def test_send_appends_timestamp_and_sign_to_webhook_url(self) -> None:
        strategy = DingTalkStrategy()
        with patch.object(strategy, "_sign", return_value=("1700000000123", "abc123%2B")):
            with patch("notifier.strategies.dingtalk.post_json") as mock_post:
                strategy.send(
                    message="hello",
                    webhook_url="https://oapi.dingtalk.com/robot/send?access_token=token",
                    reason="done",
                    summary="",
                    status="success",
                    secret="SEC_test_secret",
                )

        mock_post.assert_called_once_with(
            "https://oapi.dingtalk.com/robot/send?access_token=token&timestamp=1700000000123&sign=abc123%2B",
            {"msgtype": "text", "text": {"content": "hello"}},
        )


if __name__ == "__main__":
    unittest.main()