import sys
import time
import traceback

from notifier.config import load_channels, load_global_templates
from notifier.event_parser import parse_event
from notifier.logger import configure_debug, debug_log, output_log
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
    configure_debug()
    start = time.perf_counter()
    debug_log("hook started")

    raw = sys.stdin.read()
    debug_log(f"stdin loaded bytes={len(raw.encode('utf-8')) if raw else 0}")

    reason, summary = parse_event(raw)
    debug_log(f"event parsed reason={reason!r} summary_len={len(summary)}")

    summary = truncate_summary(summary)
    status = "success" if not reason or reason == "done" else "failed"
    debug_log(f"status resolved status={status}")

    channels = load_channels()
    debug_log(f"channels loaded names={[channel.name for channel in channels]}")
    if not channels:
        output_log("警告：未配置任何 webhook 渠道，跳过通知")
        raise SystemExit(0)

    global_success_template, global_failed_template = load_global_templates()
    strategies = build_strategies()
    has_error = False

    for channel in channels:
        debug_log(f"channel={channel.name} preparing template")
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
        debug_log(f"channel={channel.name} message rendered len={len(message)}")
        try:
            channel_start = time.perf_counter()
            debug_log(f"channel={channel.name} send start")
            strategies[channel.name].send(
                message=message,
                webhook_url=channel.webhook_url,
                reason=reason,
                summary=summary,
                status=status,
                secret=channel.secret,
            )
            debug_log(
                f"channel={channel.name} send done elapsed_ms={int((time.perf_counter() - channel_start) * 1000)}"
            )
        except Exception as exc:
            has_error = True
            output_log(f"渠道 {channel.name} 发送失败：{exc}")
            traceback.print_exc(file=sys.stdout)

    debug_log(
        f"hook finished has_error={has_error} elapsed_ms={int((time.perf_counter() - start) * 1000)}"
    )
    raise SystemExit(1 if has_error else 0)
