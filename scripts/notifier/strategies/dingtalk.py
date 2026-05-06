import base64
import hashlib
import hmac
import time
import urllib.parse

from scripts.notifier.http_client import post_json
from scripts.notifier.strategies.base import BaseStrategy


class DingTalkStrategy(BaseStrategy):
    name = "dingtalk"

    def _sign(self, secret: str) -> tuple[str, str]:
        timestamp = str(round(time.time() * 1000))
        string_to_sign = f"{timestamp}\\n{secret}".encode("utf-8")
        digest = hmac.new(
            secret.encode("utf-8"), string_to_sign, digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(digest))
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
        url = webhook_url
        if secret:
            timestamp, sign = self._sign(secret)
            separator = "&" if "?" in webhook_url else "?"
            url = f"{webhook_url}{separator}timestamp={timestamp}&sign={sign}"
        post_json(url, {"msgtype": "text", "text": {"content": message}})
