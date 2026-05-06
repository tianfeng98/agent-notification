# agent-notification

通过 Copilot Agent 的 Stop hook，将会话结束通知发送到钉钉、飞书或自定义 webhook。

本仓库已按 VS Code Agent Plugin（Copilot format）组织，根目录包含：

- `plugin.json`
- `hooks.json`
- `hooks/scripts/notify_webhook.py`

## Supported channels

- dingtalk
- feishu
- custom

## Quick start

### 1) 设置操作系统环境变量

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

### 2) 在 VS Code 安装插件

- 方式 A：命令面板运行 `Chat: Install Plugin From Source`，输入本仓库 Git 地址。
- 方式 B：在 `settings.json` 配置本地插件路径：

```json
{
  "chat.pluginLocations": {
    "/absolute/path/to/agent-notification": true
  }
}
```

安装后，VS Code 会读取根目录 [plugin.json](plugin.json) 和 [hooks.json](hooks.json)。

### 3) Workspace Hook 示例（可选）

如果你不通过插件机制安装，只想在工作区直接使用，也可以参考 [hooks/webhook-notify.json](hooks/webhook-notify.json)。

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
