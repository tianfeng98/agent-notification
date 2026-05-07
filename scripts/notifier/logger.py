import os
import time
from typing import Mapping, Optional

DEBUG_ENV = "AGENT_NOTIFICATION_DEBUG"
_DEBUG_ENABLED = False


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def configure_debug(env: Optional[Mapping[str, str]] = None) -> bool:
    global _DEBUG_ENABLED
    source = env if env is not None else os.environ
    _DEBUG_ENABLED = _is_truthy(str(source.get(DEBUG_ENV, "0")))
    return _DEBUG_ENABLED


def debug_log(message: str) -> None:
    if not _DEBUG_ENABLED:
        return
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{now}] [agent-notify] {message}")


def output_log(message: str) -> None:
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{now}] [agent-notify] {message}")
