from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ChannelConfig:
    name: str
    webhook_url: str
    secret: str
    success_template: Optional[str]
    failed_template: Optional[str]
