import json
import time
import urllib.error
import urllib.request

from notifier.logger import debug_log

RESPONSE_BODY_LOG_LIMIT = 1000


def _preview_response_body(body: bytes) -> str:
    text = body.decode("utf-8", errors="replace")
    if len(text) > RESPONSE_BODY_LOG_LIMIT:
        text = text[:RESPONSE_BODY_LOG_LIMIT] + "...<truncated>"
    return repr(text)


def post_json(url: str, payload: dict, timeout: int = 10) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    start = time.perf_counter()
    debug_log(
        f"http post start url={url} timeout_s={timeout} payload_bytes={len(body)}"
    )
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            response_body = response.read()
            debug_log(
                f"http post done url={url} status={getattr(response, 'status', 'unknown')} response_bytes={len(response_body)} response_body={_preview_response_body(response_body)} elapsed_ms={int((time.perf_counter() - start) * 1000)}"
            )
    except urllib.error.HTTPError as exc:
        response_body = exc.read()
        debug_log(
            f"http post failed url={url} status={getattr(exc, 'code', 'unknown')} response_bytes={len(response_body)} response_body={_preview_response_body(response_body)} elapsed_ms={int((time.perf_counter() - start) * 1000)}"
        )
        raise
