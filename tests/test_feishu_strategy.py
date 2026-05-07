import base64
import hashlib
import hmac
import unittest
from unittest.mock import patch

from notifier.strategies.feishu import FeishuStrategy


class FeishuStrategyTests(unittest.TestCase):
    def test_sign_uses_real_newline_separator(self) -> None:
        strategy = FeishuStrategy()
        secret = "test_secret"

        with patch("notifier.strategies.feishu.time.time", return_value=1700000000.123):
            timestamp, sign = strategy._sign(secret)

        expected_timestamp = "1700000000"
        payload = f"{expected_timestamp}\n{secret}".encode("utf-8")
        expected_digest = hmac.new(payload, b"", digestmod=hashlib.sha256).digest()
        expected_sign = base64.b64encode(expected_digest).decode("utf-8")

        self.assertEqual(expected_timestamp, timestamp)
        self.assertEqual(expected_sign, sign)

    def test_send_puts_timestamp_and_sign_into_payload(self) -> None:
        strategy = FeishuStrategy()
        with patch.object(strategy, "_sign", return_value=("1700000000", "abc123=")):
            with patch("notifier.strategies.feishu.post_json") as mock_post:
                strategy.send(
                    message="hello",
                    webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/token",
                    reason="done",
                    summary="",
                    status="success",
                    secret="test_secret",
                )

        mock_post.assert_called_once_with(
            "https://open.feishu.cn/open-apis/bot/v2/hook/token",
            {
                "msg_type": "text",
                "content": {"text": "hello"},
                "timestamp": "1700000000",
                "sign": "abc123=",
            },
        )


if __name__ == "__main__":
    unittest.main()