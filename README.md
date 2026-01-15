# 🚀 GeminiForge (原 gtgm)

基于 GitHub Actions 的 Gemini Business 账号自动注册工具，支持 VLESS 代理和定时任务。

## ✨ 功能特点

- 🔄 **自动注册** - 每6小时自动注册新账号
- 🌐 **代理支持** - 支持 HTTP/SOCKS5/VLESS 代理
- 📦 **自动同步** - 注册后自动同步凭证到远程 API
- 🎭 **无头浏览器** - 使用 Playwright 模拟真实浏览器
- ⚡ **并发注册** - 支持多账号并发注册

---

## 📋 快速开始

### 第一步：Fork 仓库

点击右上角 `Fork` 按钮，将此仓库复制到你的 GitHub 账户。

### 第二步：配置 Secrets

进入仓库 **Settings** → **Secrets and variables** → **Actions**，添加以下密钥：

#### 必填配置

| Secret | 说明 | 示例 |
|--------|------|------|
| `WORKER_DOMAIN` | 邮箱 Worker 域名 | `email.example.com` |
| `EMAIL_DOMAIN` | 邮箱域名 | `mail.example.com` |
| `ADMIN_PASSWORD` | 邮箱管理密码 | `your_password` |
| `SYNC_URL` | 同步 API 地址 | `https://xxx.hf.space` |
| `SYNC_KEY` | 同步 API 密钥 | `your_api_key` |

#### 代理配置（可选）

| Secret | 说明 | 示例 |
|--------|------|------|
| `PROXY` | HTTP/SOCKS5 代理 | `http://host:port` |
| `VLESS_CONFIG` | VLESS 代理配置 | 见下方说明 |

### 第三步：运行

- **手动运行**：Actions → `Gemini Business Account Registration` → `Run workflow`
- **定时运行**：每6小时自动运行（北京时间 08:00, 14:00, 20:00, 02:00）

---

## ⚙️ 运行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `count` | 注册账号数量 | 手动: 1, 定时: 2 |
| `concurrent` | 并发数 (1-5) | 1 |

---

## 🔒 代理配置详解

### HTTP/SOCKS5 代理

设置 `PROXY` Secret：

```
http://host:port
http://user:pass@host:port
socks5://host:port
```

### VLESS 代理

设置 `VLESS_CONFIG` Secret，支持两种格式：

**格式一：VLESS URL（推荐）**

```
vless://uuid@server:port?type=tcp&security=reality&sni=example.com&fp=chrome&pbk=xxx
```

**格式二：YAML 配置**

```yaml
{ server: example.com, port: 443, uuid: xxx-xxx, flow: xtls-rprx-vision, ... }
```

> ⚠️ **注意**：使用 VLESS 代理时会自动安装 sing-box

---

## 📁 项目结构

```
gtgm/
├── register.py          # 主注册脚本
├── proxy_helper.py      # VLESS 代理启动器
├── requirements.txt     # Python 依赖
├── README.md            # 说明文档
└── .github/
    └── workflows/
        └── register.yml # GitHub Actions 工作流
```

---

## 🔧 技术实现

| 组件 | 技术 | 说明 |
|------|------|------|
| 浏览器 | Playwright | 无头 Chromium 浏览器 |
| 代理 | sing-box | VLESS/Reality 代理客户端 |
| 并发 | asyncio | Python 异步并发 |
| HTTP | requests | 带连接池的 HTTP 客户端 |

---

## ❓ 常见问题

### Q: 注册失败，提示连接重置？

A: 检查代理是否可用。可以尝试更换代理节点。

### Q: 凭证有效期显示不正确？

A: 已自动处理时区问题，凭证有效期为12小时（北京时间）。

### Q: 如何修改定时运行频率？

A: 编辑 `.github/workflows/register.yml` 中的 `cron` 表达式。

---

## 📜 许可证

MIT License

---

## 🙏 感谢

本项目的实现参考了以下资源，特此感谢：

### 注册机逻辑
- GitHub: [xLmiler/test_band](https://github.com/xLmiler/test_band)
- Linux.do: [相关讨论帖](https://linux.do/t/topic/1234455?u=starsdream)

### API 反代
- Linux.do: [2API 反代教程](https://linux.do/t/topic/1225645?u=starsdream)

### Hugging Face 镜像
- Linux.do: [HF 镜像部署](https://linux.do/t/topic/1226413?u=starsdream)

### 域名邮箱搭建
- Linux.do: [域名邮箱教程](https://linux.do/t/topic/316819?u=starsdream)
- 官方文档: [Temp Mail Docs](https://temp-mail-docs.awsl.uk)
