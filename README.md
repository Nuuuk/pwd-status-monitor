# PWD Status Monitor | PWD 处理进度监控机器人

An automated monitoring tool powered by Google Gemini API and GitHub Actions. It tracks the latest Prevailing Wage Determination (PWD) processing times on the US Department of Labor (DOL) FLAG website and sends email notifications whenever updates or progress occur.

基于 Google Gemini API 与 GitHub Actions 的自动化监控工具。每日自动抓取美国劳工部（DOL）FLAG 官网的 Prevailing Wage Determination (PWD) 处理进度，并在排期有推进或状态更新时发送邮件通知。

---

## Features | 功能特性

* **Automated Web Scraping / 自动抓取**：Daily scheduled HTML parsing via GitHub Actions (completely free). / 通过 GitHub Actions 每日定时运行，无需个人服务器。
* **Intelligent Analysis / 智能比对**：Uses Google Gemini 2.5 Flash to accurately extract structured wage data (OEWS, Non-OEWS, Redeterminations, etc.) and detect changes against previous records. / 利用 Gemini 2.5 Flash 解析网页非结构化文本，对比历史记录并生成变动摘要。
* **Email Alerts / 邮件通知**：Instant SMTP email notifications upon status changes or initial runs. / 检测到排期推进时，自动触发 SMTP 邮件推送。
* **State Persistence / 状态存储**：Automatically commits and maintains `last_pwd_status.txt` in the repository. / 自动将最新状态写回 Git 仓库，实现无缝的历史比对。

---

## Setup & Configuration | 配置与部署

### 1. Repository Secrets | 环境变量配置

Navigate to **Settings > Secrets and variables > Actions** in your GitHub repository and add the following secrets:
在 GitHub 仓库的 **Settings > Secrets and variables > Actions** 中添加以下密钥：

| Secret Name | Description | 说明 |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google AI Studio API Key | Google AI Studio 免费生成的 API Key |
| `SENDER_EMAIL` | Sender email address (e.g., Gmail) | 发件人邮箱（如 Gmail） |
| `EMAIL_PASSWORD` | 16-character App Password for SMTP | 发件邮箱生成的 16 位应用专用密码 |
| `RECEIVER_EMAIL` | Notification recipient email | 接收通知的个人邮箱 |

### 2. Workflow Permissions | 权限设置

Ensure GitHub Actions has write access to save the state file:
确保 GitHub Actions 拥有仓库的写权限以持久化存储状态文件：
* Go to **Settings > Actions > General > Workflow permissions**.
* Select **Read and write permissions** and save.

---

## How It Works | 工作流程

```text
[Cron / Manual Trigger]
         │
         ▼
[Fetch DOL Processing Times Page]
         │
         ▼
[Gemini API: Extract & Compare with last_pwd_status.txt]
         │
    ┌────┴────────────────────────┐
    ▼                             ▼
[Changes Detected]           [No Changes]
    │                             │
    ├─> Send Email Alert          └─> Exit silently
    └─> Commit updated status
