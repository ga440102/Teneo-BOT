# Teneo Community Node BOT (Python)

基于 Teneo WebSocket 的社区节点自动保活脚本（Python 异步版）。自动与 `secure.ws.teneo.pro` 建立长连接、定时发送心跳（PING）并接收服务器脉冲（Pulse），持续累积节点积分。

> 本仓库为 Python 实现：单文件 `bot.py` 负责保活，`setup.py` 负责用账号登录换取 `accessToken`。

## ✨ 功能特性

- **WebSocket 长连接保活**：连接 `wss://secure.ws.teneo.pro/websocket?accessToken=...&version=v0.2`，自动连接 / 断线重连。
- **心跳与积分**：每 10 秒发送 `PING`，解析服务端 `Connected successfully` / `Pulse from server` 消息，实时显示当日积分（pointsToday）、总积分（pointsTotal）与心跳数（heartbeats）。
- **多账号并发**：从 `tokens.json` 读取多个账号，每个账号独立 WebSocket 协程并行运行。
- **代理支持**：三种模式可选
  - `1` 使用 [Free Proxyscrape](https://proxyscrape.com/free-proxy-list) 公共代理（自动拉取）
  - `2` 使用 `proxy.txt` 中的私有代理
  - `3` 不使用代理直连
  - 可选代理失效自动轮换（`y` / `n`）
- **Token 自动获取**：`setup.py` 用 `accounts.json` 中的邮箱 / 密码登录 Teneo，自动过 Turnstile 验证（2captcha 或本地 solver），把 `accessToken` 写入 `tokens.json`。
- **私有 Turnstile-Solver**：若自建了私有 solver，使用 `setup2.py` 取 token。

## 📦 环境要求

- Python 3.9+
- 能访问 `secure.ws.teneo.pro` 与 `auth.teneo.pro` 的网络环境
- （可选）2captcha API Key，用于自动过人机验证

## 🔧 安装

```bash
pip install -r requirements.txt
```

依赖：`aiohttp`、`aiohttp-socks`、`fake-useragent`、`colorama`、`pytz`

## ⚙️ 配置

### 1. accounts.json（供 setup.py 登录取 token）

```json
[
    { "Email": "your_email_address_1", "Password": "your_password_1" },
    { "Email": "your_email_address_2", "Password": "your_password_2" }
]
```

### 2. 2captcha_key.txt（可选）

填入你的 2captcha API Key，用于自动过 Turnstile：

```
your_2captcha_key
```

没有 key 也可手动获取 token 后直接写入 `tokens.json`。

### 3. tokens.json（供 bot.py 运行）

由 `setup.py` 自动生成，格式：

```json
[
    { "Email": "your_email_address_1", "accessToken": "your_access_token_1" },
    { "Email": "your_email_address_2", "accessToken": "your_access_token_2" }
]
```

若已手动拿到 token，也可直接按此格式填写。

### 4. proxy.txt（可选）

仅在「使用代理」模式下生效，每行一个：

```
ip:port                      # 默认 http
protocol://ip:port           # 例如 http://1.2.3.4:8080
protocol://user:pass@ip:port # 带鉴权，例如 socks5://user:pass@1.2.3.4:1080
```

## 🚀 运行

### 第一步：获取 token（setup.py）

```bash
python setup.py
```

按提示选择代理模式，脚本会用 `accounts.json` 登录并把 `accessToken` 写入 `tokens.json`。若使用私有 Turnstile-Solver，改用 `python setup2.py`。

### 第二步：启动保活（bot.py）

```bash
python bot.py
```

启动后交互式选择代理模式（`1` / `2` / `3`）及是否轮换失效代理（`y` / `n`），随后进入长期运行。按 `Ctrl+C` 退出。

## 📁 文件结构

```
.
├── bot.py              # 主程序：WebSocket 保活 + 心跳积分
├── setup.py            # 用 accounts.json 登录取 accessToken
├── setup2.py           # 私有 Turnstile-Solver 取 token 版本
├── requirements.txt    # Python 依赖
├── accounts.json       # 你的账号邮箱 / 密码（被 .gitignore 忽略，勿提交）
├── tokens.json         # 生成的 accessToken（被 .gitignore 忽略，勿提交）
├── 2captcha_key.txt    # 你的 2captcha key（被 .gitignore 忽略，勿提交）
└── proxy.txt           # 你的代理列表（被 .gitignore 忽略，勿提交）
```

## ⚠️ 说明

- `accounts.json` / `tokens.json` / `2captcha_key.txt` / `proxy.txt` 含有你的私密凭证，已在 `.gitignore` 中忽略，**切勿提交到公开仓库**。
- 本脚本仅用于自动化你自己的 Teneo 节点运维，请遵守 Teneo 服务条款与当地法律法规。
