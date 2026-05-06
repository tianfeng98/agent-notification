import json


def read_last_assistant_message(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError:
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
    except Exception:
        return "done", ""

    reason = str(
        payload.get("stopReason")
        or payload.get("reason")
        or payload.get("stop_reason")
        or "done"
    ).strip() or "done"
    transcript_path = str(payload.get("transcript_path") or "").strip()
    summary = read_last_assistant_message(transcript_path) if transcript_path else ""
    return reason, summary
