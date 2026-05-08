import json

from notifier.logger import debug_log


def read_last_assistant_message(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError as exc:
        debug_log(f"transcript open failed path={path} error={exc}")
        return ""

    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except Exception:
            continue
        if entry.get("type") != "assistant.message":
            continue
        content = (entry.get("data") or {}).get("content", "")
        if isinstance(content, str) and content.strip():
            return content.strip()
    return ""


def parse_event(raw: str) -> tuple[str, str, bool]:
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception as exc:
        debug_log(f"event json parse failed error={exc}")
        return "done", "", True

    hook_event_name = str(
        payload.get("hook_event_name")
        or payload.get("hookEventName")
        or payload.get("event")
        or "Stop"
    ).strip()

    # Ignore subagent completion events; we only notify the top-level final result.
    if hook_event_name in {"SubagentStop", "subagentStop"}:
        debug_log(f"event ignored hook_event_name={hook_event_name}")
        return "done", "", False

    if hook_event_name in {"ErrorOccurred", "errorOccurred"}:
        recoverable = bool(payload.get("recoverable", False))
        error_obj = payload.get("error") or {}
        error_message = ""
        if isinstance(error_obj, dict):
            error_message = str(error_obj.get("message") or "").strip()
        error_name = ""
        if isinstance(error_obj, dict):
            error_name = str(error_obj.get("name") or "").strip()
        summary = (
            f"{error_name}: {error_message}".strip(": ")
            if (error_name or error_message)
            else str(payload.get("error") or "").strip()
        )
        notify = not recoverable
        debug_log(
            f"event errorOccurred parsed recoverable={recoverable} notify={notify} summary_len={len(summary)}"
        )
        return "error", summary, notify

    if hook_event_name in {"SessionEnd", "sessionEnd"}:
        reason = str(payload.get("reason") or payload.get("end_reason") or "complete").strip() or "complete"
        # Error sessions are handled by ErrorOccurred to avoid duplicated notifications.
        if reason == "error":
            debug_log("event sessionEnd ignored reason=error")
            return reason, "", False

        summary = str(
            payload.get("finalMessage")
            or payload.get("final_message")
            or payload.get("message")
            or ""
        ).strip()
        debug_log(
            f"event sessionEnd parsed reason={reason!r} summary_len={len(summary)} notify=True"
        )
        return reason, summary, True

    reason = str(
        payload.get("stopReason")
        or payload.get("reason")
        or payload.get("stop_reason")
        or "done"
    ).strip() or "done"
    transcript_path = str(
        payload.get("transcript_path") or payload.get("transcriptPath") or ""
    ).strip()
    debug_log(
        f"event fields extracted hook_event_name={hook_event_name!r} reason={reason!r} transcript_path={transcript_path!r}"
    )
    summary = read_last_assistant_message(transcript_path) if transcript_path else ""
    return reason, summary, True
