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


def parse_event(raw: str) -> tuple[str, str]:
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception as exc:
        debug_log(f"event json parse failed error={exc}")
        return "done", ""

    reason = str(
        payload.get("stopReason")
        or payload.get("reason")
        or payload.get("stop_reason")
        or "done"
    ).strip() or "done"
    transcript_path = str(payload.get("transcript_path") or "").strip()
    debug_log(f"event fields extracted reason={reason!r} transcript_path={transcript_path!r}")
    summary = read_last_assistant_message(transcript_path) if transcript_path else ""
    return reason, summary
