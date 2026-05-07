import json
import os
import subprocess
from pathlib import Path

try:
    import pwd
except ImportError:  # pragma: no cover - unavailable on Windows
    pwd = None

from notifier.logger import debug_log
from notifier.models import ChannelConfig

GLOBAL_SUCCESS_TEMPLATE_ENV = "AGENT_NOTIFICATION_SUCCESS_TEMPLATE"
GLOBAL_FAILED_TEMPLATE_ENV = "AGENT_NOTIFICATION_FAILED_TEMPLATE"
ALLOWED_POSIX_SHELL_NAMES = {"zsh", "bash", "sh", "dash", "ksh"}

CHANNEL_ENVS = {
    "dingtalk": {
        "webhook": "AGENT_NOTIFICATION_DINGTALK_WEBHOOK_URL",
        "secret": "AGENT_NOTIFICATION_DINGTALK_SECRET",
        "success": "AGENT_NOTIFICATION_DINGTALK_SUCCESS_TEMPLATE",
        "failed": "AGENT_NOTIFICATION_DINGTALK_FAILED_TEMPLATE",
    },
    "feishu": {
        "webhook": "AGENT_NOTIFICATION_FEISHU_WEBHOOK_URL",
        "secret": "AGENT_NOTIFICATION_FEISHU_SECRET",
        "success": "AGENT_NOTIFICATION_FEISHU_SUCCESS_TEMPLATE",
        "failed": "AGENT_NOTIFICATION_FEISHU_FAILED_TEMPLATE",
    },
    "custom": {
        "webhook": "AGENT_NOTIFICATION_CUSTOM_WEBHOOK_URL",
        "secret": "",
        "success": "AGENT_NOTIFICATION_CUSTOM_SUCCESS_TEMPLATE",
        "failed": "AGENT_NOTIFICATION_CUSTOM_FAILED_TEMPLATE",
    },
}

CHANNEL_WEBHOOK_ENV_KEYS = tuple(
    CHANNEL_ENVS[name]["webhook"] for name in ("dingtalk", "feishu", "custom")
)


def _notification_env_keys() -> set[str]:
    keys = {GLOBAL_SUCCESS_TEMPLATE_ENV, GLOBAL_FAILED_TEMPLATE_ENV, "AGENT_NOTIFICATION_DEBUG"}
    for envs in CHANNEL_ENVS.values():
        keys.update(value for value in envs.values() if value)
    return keys


def _login_shell_path() -> str:
    # This function is POSIX-only; Windows uses COMSPEC and `set` directly.
    if os.name == "nt":
        return ""

    shell = os.environ.get("SHELL", "").strip()
    if not shell:
        if pwd is not None:
            shell = pwd.getpwuid(os.getuid()).pw_shell or "/bin/sh"
        else:
            shell = "/bin/sh"

    shell_name = Path(shell).name.lower()
    if shell_name not in ALLOWED_POSIX_SHELL_NAMES:
        debug_log(f"config shell not allowed shell={shell}, fallback=/bin/sh")
        return "/bin/sh"
    return shell


def _login_shell_env_command() -> tuple[list[str], str]:
    if os.name == "nt":
        comspec = os.environ.get("COMSPEC", "").strip() or "cmd.exe"
        return [comspec, "/d", "/c", "set"], comspec

    shell = _login_shell_path()
    return [shell, "-ilc", "env"], shell


def _read_login_shell_env() -> dict[str, str]:
    command, source = _login_shell_env_command()
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
    except Exception as exc:
        debug_log(f"config login shell env read failed source={source} error={exc}")
        return {}

    keys = _notification_env_keys()
    env_map: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in keys:
            env_map[key] = value
    debug_log(
        f"config login shell env loaded source={source} keys={sorted(env_map.keys())}"
    )
    return env_map


def _has_any_channel_webhook(values: dict[str, str]) -> bool:
    for key in CHANNEL_WEBHOOK_ENV_KEYS:
        if values.get(key, "").strip():
            return True
    return False

def _plugin_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_hook_env_file(path: Path) -> dict[str, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    hooks = payload.get("hooks")
    if not isinstance(hooks, dict):
        return {}

    stop_items = hooks.get("Stop")
    if not isinstance(stop_items, list):
        return {}

    for item in stop_items:
        if not isinstance(item, dict):
            continue

        # Flat hook format: { type, command, env }
        env_map = item.get("env")
        if isinstance(env_map, dict):
            return {
                str(k): str(v)
                for k, v in env_map.items()
                if isinstance(k, str) and isinstance(v, (str, int, float, bool))
            }

        # Matcher compatibility format: { matcher, hooks: [ { type, command, env } ] }
        nested_hooks = item.get("hooks")
        if isinstance(nested_hooks, list):
            for nested in nested_hooks:
                if not isinstance(nested, dict):
                    continue
                nested_env = nested.get("env")
                if isinstance(nested_env, dict):
                    return {
                        str(k): str(v)
                        for k, v in nested_env.items()
                        if isinstance(k, str)
                        and isinstance(v, (str, int, float, bool))
                    }

    return {}


def _read_hook_env_fallback() -> dict[str, str]:
    root = _plugin_root()
    candidates = [root / "hooks.json", root / "hooks" / "hooks.json"]
    for path in candidates:
        if not path.exists():
            debug_log(f"config fallback not found path={path}")
            continue
        env_map = _read_hook_env_file(path)
        if env_map:
            debug_log(f"config fallback loaded path={path} keys={sorted(env_map.keys())}")
            return env_map
        debug_log(f"config fallback exists but no env map path={path}")
    return {}


def _get_config_values() -> dict[str, str]:
    values = dict(os.environ)
    debug_log(f"config os env loaded count={len(os.environ)}")

    hook_env = _read_hook_env_fallback()
    if hook_env:
        # hooks.json env has higher priority than process environment variables.
        values.update(hook_env)

    shell_env_count = 0
    if not _has_any_channel_webhook(values):
        shell_env = _read_login_shell_env()
        shell_env_count = len(shell_env)
        for key, value in shell_env.items():
            values.setdefault(key, value)
    else:
        debug_log("config shell fallback skipped reason=channel_webhook_present")

    debug_log(
        f"config merged count={len(values)} hook_env_count={len(hook_env)} shell_env_count={shell_env_count}"
    )
    return values


def load_global_templates() -> tuple[str, str]:
    values = _get_config_values()
    return (
        values.get(GLOBAL_SUCCESS_TEMPLATE_ENV, "").strip(),
        values.get(GLOBAL_FAILED_TEMPLATE_ENV, "").strip(),
    )


def load_channels() -> list[ChannelConfig]:
    values = _get_config_values()
    channels = []
    for name in ("dingtalk", "feishu", "custom"):
        envs = CHANNEL_ENVS[name]
        webhook_url = values.get(envs["webhook"], "").strip()
        if not webhook_url:
            continue
        secret = values.get(envs["secret"], "").strip() if envs["secret"] else ""
        channels.append(
            ChannelConfig(
                name=name,
                webhook_url=webhook_url,
                secret=secret,
                success_template=values.get(envs["success"], "").strip() or None,
                failed_template=values.get(envs["failed"], "").strip() or None,
            )
        )
    debug_log(f"config channels discovered names={[channel.name for channel in channels]}")
    return channels
