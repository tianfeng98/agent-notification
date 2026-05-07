from notifier.http_client import post_json
from notifier.strategies.base import BaseStrategy


class CustomStrategy(BaseStrategy):
    name = "custom"

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
        post_json(
            webhook_url,
            {
                "text": message,
                "reason": reason,
                "summary": summary,
                "status": status,
            },
        )
