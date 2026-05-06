# agent-notification

通过 Copilot Agent 的 Stop hook，将会话结束通知发送到钉钉、飞书或自定义 webhook。

## Supported channels

- dingtalk
- feishu
- custom

## Quick start

使用 [hooks/webhook-notify.json](hooks/webhook-notify.json) 作为示例，只保留 hook 命令。
所有变量都从操作系统环境变量读取，不要写在 hook 配置文件里。

例如在 macOS/Linux shell 中先导出：

```bash
export AGENT_NOTIFICATION_DINGTALK_WEBHOOK_URL="https://oapi.dingtalk.com/robot/send?access_token=your_token"
export AGENT_NOTIFICATION_DINGTALK_SECRET="SECxxxxxxxx"
export AGENT_NOTIFICATION_FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/your_token"
export AGENT_NOTIFICATION_CUSTOM_WEBHOOK_URL="https://example.com/webhook"
export AGENT_NOTIFICATION_SUCCESS_TEMPLATE="「Agent执行成功」\n\n---\n{summary}"
export AGENT_NOTIFICATION_FAILED_TEMPLATE="「Agent执行失败」{reason}"
```

## Environment variables

### Global templates

- `AGENT_NOTIFICATION_SUCCESS_TEMPLATE`
- `AGENT_NOTIFICATION_FAILED_TEMPLATE`

### DingTalk

- `AGENT_NOTIFICATION_DINGTALK_WEBHOOK_URL`
- `AGENT_NOTIFICATION_DINGTALK_SECRET`
- `AGENT_NOTIFICATION_DINGTALK_SUCCESS_TEMPLATE`
- `AGENT_NOTIFICATION_DINGTALK_FAILED_TEMPLATE`

### Feishu

- `AGENT_NOTIFICATION_FEISHU_WEBHOOK_URL`
- `AGENT_NOTIFICATION_FEISHU_SECRET`
- `AGENT_NOTIFICATION_FEISHU_SUCCESS_TEMPLATE`
- `AGENT_NOTIFICATION_FEISHU_FAILED_TEMPLATE`

### Custom

- `AGENT_NOTIFICATION_CUSTOM_WEBHOOK_URL`
- `AGENT_NOTIFICATION_CUSTOM_SUCCESS_TEMPLATE`
- `AGENT_NOTIFICATION_CUSTOM_FAILED_TEMPLATE`

## Behavior

- 配置了哪个渠道的 webhook URL，就启用哪个渠道。
- 发送顺序固定为 dingtalk -> feishu -> custom。
- 单个渠道失败不会阻断后续渠道，但最终进程会返回退出码 1。
- 没有配置任何渠道时，程序输出警告并退出 0。

## Template variables

- `{summary}`
- `{reason}`
- `{status}`

## Migration

- `DINGTALK_WEBHOOK_URL` -> `AGENT_NOTIFICATION_DINGTALK_WEBHOOK_URL`
- `DINGTALK_SECRET` -> `AGENT_NOTIFICATION_DINGTALK_SECRET`
- `hooks/scripts/notify_dingtalk.py` 已由通用入口 `hooks/scripts/notify_webhook.py` 取代，旧脚本目前保留兼容转发。
