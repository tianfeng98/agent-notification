import os

from notifier.models import ChannelConfig

GLOBAL_SUCCESS_TEMPLATE_ENV = "AGENT_NOTIFICATION_SUCCESS_TEMPLATE"
GLOBAL_FAILED_TEMPLATE_ENV = "AGENT_NOTIFICATION_FAILED_TEMPLATE"

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


def load_global_templates() -> tuple[str, str]:
    return (
        os.environ.get(GLOBAL_SUCCESS_TEMPLATE_ENV, "").strip(),
        os.environ.get(GLOBAL_FAILED_TEMPLATE_ENV, "").strip(),
    )


def load_channels() -> list[ChannelConfig]:
    channels = []
    for name in ("dingtalk", "feishu", "custom"):
        envs = CHANNEL_ENVS[name]
        webhook_url = os.environ.get(envs["webhook"], "").strip()
        if not webhook_url:
            continue
        secret = os.environ.get(envs["secret"], "").strip() if envs["secret"] else ""
        channels.append(
            ChannelConfig(
                name=name,
                webhook_url=webhook_url,
                secret=secret,
                success_template=os.environ.get(envs["success"], "").strip() or None,
                failed_template=os.environ.get(envs["failed"], "").strip() or None,
            )
        )
    return channels
