import os
import unittest
from unittest.mock import patch

from notifier import config as config_module


class ConfigTests(unittest.TestCase):
    def test_hooks_env_overrides_os_env(self) -> None:
        with patch.dict(
            os.environ,
            {"AGENT_NOTIFICATION_DINGTALK_WEBHOOK_URL": "https://os.example.com"},
            clear=True,
        ):
            with patch.object(
                config_module,
                "_read_hook_env_fallback",
                return_value={
                    "AGENT_NOTIFICATION_DINGTALK_WEBHOOK_URL": "https://hooks.example.com"
                },
            ):
                values = config_module._get_config_values()

        self.assertEqual(
            "https://hooks.example.com",
            values["AGENT_NOTIFICATION_DINGTALK_WEBHOOK_URL"],
        )

    def test_os_env_used_when_hooks_env_missing(self) -> None:
        with patch.dict(
            os.environ,
            {"AGENT_NOTIFICATION_FEISHU_WEBHOOK_URL": "https://os.feishu.example.com"},
            clear=True,
        ):
            with patch.object(
                config_module,
                "_read_hook_env_fallback",
                return_value={},
            ):
                values = config_module._get_config_values()

        self.assertEqual(
            "https://os.feishu.example.com",
            values["AGENT_NOTIFICATION_FEISHU_WEBHOOK_URL"],
        )


if __name__ == "__main__":
    unittest.main()