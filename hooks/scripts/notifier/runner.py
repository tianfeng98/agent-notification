import sys

from notifier.config import load_channels, load_global_templates
from notifier.event_parser import parse_event
from notifier.renderer import (
    DEFAULT_FAILED_TEMPLATE,
    DEFAULT_SUCCESS_TEMPLATE,
    choose_template,
    render_message,
    truncate_summary,
)
from notifier.strategies.custom import CustomStrategy
from notifier.strategies.dingtalk import DingTalkStrategy
from notifier.strategies.feishu import FeishuStrategy


def build_strategies() -> dict[str, object]:
    return {
        "dingtalk": DingTalkStrategy(),
        "feishu": FeishuStrategy(),
        "custom": CustomStrategy(),
    }


def main() -> None:
    raw = sys.stdin.read()
    reason, summary = parse_event(raw)
    summary = truncate_summary(summary)
    status = "success" if not reason or reason == "done" else "failed"

    channels = load_channels()
    if not channels:
        print("警告：未配置任何 webhook 渠道，跳过通知", file=sys.stderr)
        raise SystemExit(0)

    global_success_template, global_failed_template = load_global_templates()
    strategies = build_strategies()
    has_error = False

    for channel in channels:
        template = choose_template(
            channel.success_template if status == "success" else channel.failed_template,
            global_success_template if status == "success" else global_failed_template,
            DEFAULT_SUCCESS_TEMPLATE if status == "success" else DEFAULT_FAILED_TEMPLATE,
        )
        message = render_message(
            template,
            summary=summary,
            reason=reason,
            status=status,
        )
        try:
            strategies[channel.name].send(
                message=message,
                webhook_url=channel.webhook_url,
                reason=reason,
                summary=summary,
                status=status,
                secret=channel.secret,
            )
        except Exception as exc:
            has_error = True
            print(f"渠道 {channel.name} 发送失败：{exc}", file=sys.stderr)

    raise SystemExit(1 if has_error else 0)
