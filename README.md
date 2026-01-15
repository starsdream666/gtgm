# Gemini Business 注册机 (GitHub Actions版)

自动注册 Gemini Business 账号并同步到远程API，专为GitHub Actions设计。

## 快速开始

### 1. Fork 此仓库

### 2. 配置 Secrets

在仓库 Settings → Secrets and variables → Actions 中添加：

| Secret | 说明 |
|--------|------|
| `WORKER_DOMAIN` | 邮箱Worker域名 |
| `EMAIL_DOMAIN` | 邮箱域名 |
| `ADMIN_PASSWORD` | 邮箱管理密码 |
| `SYNC_URL` | 同步API地址 |
| `SYNC_KEY` | 同步API密钥 |

### 3. 运行

**手动运行**：Actions → Gemini Business Account Registration → Run workflow

**定时运行**：默认每天 UTC 00:00 运行

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| count | 注册账号数量 | 1 |
| concurrent | 并发数 | 1 |

## 技术细节

- 使用 **Playwright** 无头浏览器
- 使用 **asyncio** 实现并发注册
- 自动同步到远程API
- 支持网络请求重试

## 目录结构

```
gtgm/
├── register.py           # 主脚本
├── requirements.txt      # 依赖
├── README.md            # 说明
└── .github/
    └── workflows/
        └── register.yml  # GitHub Actions
```
