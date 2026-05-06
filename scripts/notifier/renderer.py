from collections import UserDict
from typing import Optional

MAX_SUMMARY_LEN = 4000
DEFAULT_SUCCESS_TEMPLATE = "「Agent执行成功」\n\n---\n{summary}"
DEFAULT_FAILED_TEMPLATE = "「Agent执行失败」{reason}"


class SafeFormatDict(UserDict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def choose_template(
    channel_template: Optional[str], global_template: str, fallback: str
) -> str:
    if channel_template:
        return channel_template
    if global_template:
        return global_template
    return fallback


def truncate_summary(summary: str) -> str:
    if len(summary) <= MAX_SUMMARY_LEN:
        return summary
    return summary[:MAX_SUMMARY_LEN] + "..."


def render_message(template: str, *, summary: str, reason: str, status: str) -> str:
    return template.format_map(
        SafeFormatDict(summary=summary, reason=reason, status=status)
    )
