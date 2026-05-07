# agent-notification

通过 Copilot Agent 的 Stop hook，将会话结束通知发送到钉钉、飞书或自定义 webhook。

本仓库同时提供 Copilot format 与 Claude format 的插件清单，避免不同加载路径带来的兼容问题。

Copilot format（推荐给 VS Code）：

- `plugin.json`
- `hooks.json`
- `scripts/notify_webhook.py`

Claude format（兼容）：

- `.claude-plugin/plugin.json`
- `hooks/hooks.json`

## Supported channels

- dingtalk
- feishu
- custom

## Quick start

### 1) 设置环境变量（支持两种来源）

支持以下两种来源：

- `hooks.json`（或 `hooks/hooks.json`）里 Stop hook 的 `env` 字段
- 操作系统环境变量

优先级：hooks 配置里的 `env` > 进程环境变量 > 登录 shell 环境变量回退。

说明：

- 默认先读取 Python 进程内的环境变量（`os.environ`）。
- 当未检测到任何渠道 webhook 变量时，才会触发一次 shell 环境回退读取。
- 回退读取仅用于兼容 VS Code 或 Hook 进程未继承 shell 变量的场景。

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

- 方式 A：命令面板运行 `Chat: Install Plugin From Source`，输入本仓库 Git 地址（例如 `https://github.com/tianfeng98/agent-notification.git`）。
- 方式 B：在 `settings.json` 配置本地插件路径：

```json
{
  "chat.pluginLocations": {
    "/absolute/path/to/agent-notification": true
  }
}
```

安装后，VS Code 会读取根目录 [plugin.json](plugin.json) 和 [hooks.json](hooks.json)。

`hooks.json` 也可以直接配置 `env`，例如：

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "python3 scripts/notify_webhook.py",
        "timeout": 10,
        "env": {
          "AGENT_NOTIFICATION_DINGTALK_WEBHOOK_URL": "https://oapi.dingtalk.com/robot/send?access_token=your_token",
          "AGENT_NOTIFICATION_DINGTALK_SECRET": "SECxxxxxxxx"
        }
      }
    ]
  }
}
```

注意：

- 如果你在“插件市场（marketplaces）”入口里填插件仓库地址，会报“不是有效的插件市场”。
- 该地址应当填在“Install Plugin From Source”入口，或配置 `chat.pluginLocations`。

### 3) Workspace Hook 示例（可选）

如果你不通过插件机制安装，只想在工作区直接使用，也可以参考 [hooks/webhook-notify.json](hooks/webhook-notify.json)。

## Cross-platform behavior

- macOS/Linux：回退读取会调用允许列表内的 shell（zsh/bash/sh/dash/ksh）并读取环境变量。
- Windows：回退读取使用 `COMSPEC`（默认 `cmd.exe`）执行 `set`。
- Hook command 默认使用 `python scripts/notify_webhook.py` 风格，避免绑定单一 shell 路径。

## 安装后自检

1. 确认插件入口文件存在

- [plugin.json](plugin.json)
- [hooks.json](hooks.json)
- [scripts/notify_webhook.py](scripts/notify_webhook.py)

1. 确认脚本语法可执行

在仓库根目录运行：

python3 -m py_compile scripts/notify_webhook.py scripts/notifier/runner.py scripts/notifier/config.py scripts/notifier/event_parser.py scripts/notifier/renderer.py scripts/notifier/http_client.py scripts/notifier/models.py scripts/notifier/strategies/base.py scripts/notifier/strategies/dingtalk.py scripts/notifier/strategies/feishu.py scripts/notifier/strategies/custom.py

1. 确认安装入口用对

- 正确入口：Chat: Install Plugin From Source
- 或者使用 settings.json 的 chat.pluginLocations
- 错误入口：把插件仓库地址填到插件市场配置 chat.plugins.marketplaces

1. 在 VS Code 确认插件已启用

- 打开 Extensions 视图并筛选 Agent Plugins - Installed
- 确认 agent-notification 已启用（workspace 或 global）

1. 触发一次 Stop 事件验证

- 先在操作系统导出至少一个渠道的 webhook 变量
- 发起一次正常对话并结束，让 Stop hook 被触发
- 预期行为：渠道收到消息；若部分渠道失败，日志会提示失败渠道且进程返回 1

## 常见问题

1. 报错“不是有效的插件市场”

原因：把插件仓库当成了插件市场仓库。
处理：使用 Install Plugin From Source 或 chat.pluginLocations，不要写进 chat.plugins.marketplaces。

1. 配了系统环境变量但 hooks 读不到

官方 hooks 支持 `env` 字段，且 hook 进程会使用 VS Code 进程环境。常见问题是 VS Code 从图标启动时拿不到 shell 里临时 `export` 的变量。
处理建议：

- 优先把变量写在 [hooks.json](hooks.json) 或 [hooks/hooks.json](hooks/hooks.json) 的 `env` 中（优先级最高）。
- 如果必须用系统环境变量，确保变量在启动 VS Code 的同一进程环境中可见（例如从已 export 的终端启动 VS Code）。
- 若进程环境中没有渠道变量，程序会自动尝试读取登录 shell 环境变量；若你的 shell 初始化文件较复杂，可优先改为 hooks 的 `env` 显式配置。

1. 插件安装后看不到效果

- 检查 [plugin.json](plugin.json) 的 name 是否为小写 kebab-case
- 检查 [hooks.json](hooks.json) 命令路径与脚本是否存在
- 检查系统环境变量是否已在 VS Code 进程可见

1. hooks 没有触发

- 确认插件处于启用状态
- 确认触发的是 Stop 生命周期事件
- 在脚本中增加临时日志到 /tmp 目录排查输入事件

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
