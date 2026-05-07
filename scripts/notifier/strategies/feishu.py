import base64
import hashlib
import hmac
import time

from notifier.http_client import post_json
from notifier.strategies.base import BaseStrategy


class FeishuStrategy(BaseStrategy):
    name = "feishu"

    def _sign(self, secret: str) -> tuple[str, str]:
        timestamp = str(int(time.time()))
        string_to_sign = f"{timestamp}\n{secret}".encode("utf-8")
        digest = hmac.new(string_to_sign, b"", digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(digest).decode("utf-8")
        return timestamp, sign

    def send(
        self,
        *,
        message: str,
        webhook_url: str,
        reason: str,
        summary: str,
        status: str,
        secret: str = "",
    ) -> None:
        payload = {"msg_type": "text", "content": {"text": message}}
        if secret:
            timestamp, sign = self._sign(secret)
            payload["timestamp"] = timestamp
            payload["sign"] = sign
        post_json(webhook_url, payload)
