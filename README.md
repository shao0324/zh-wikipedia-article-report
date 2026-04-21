[![Built with Claude](https://img.shields.io/badge/Built%20with-Claude%20AI-orange?logo=anthropic&logoColor=white)](https://claude.ai/code)

# 中文維基百科羽球條目監測機器人

自動監測中文維基百科新頁面 RSS，當出現羽球相關條目時，即時發送 Email 通知並歸檔留存。

## 功能

- 每小時自動抓取中文維基百科的新增頁面（一般條目與分類頁）
- 比對關鍵字（預設：`羽球`、`羽毛球`），支援透過 GitHub Repository Variables 自訂
- 發現新條目時發送 Gmail 通知信
- 自動將結果歸檔至按月份命名的 Markdown 紀錄檔（`logs/YYYY-MM.md`）
- 以 `history.txt` 去重，避免重複通知

## 運作架構

```
GitHub Actions (每小時)
        │
        ▼
   抓取兩條 Atom Feed
   ├─ Special:NewPages (namespace=0，一般條目)
   └─ Special:NewPages (namespace=14，分類頁)
        │
        ▼
   關鍵字比對（標題 + 摘要）
        │
        ▼
   與 history.txt 去重
        │
   ┌────┴────────────┐
 有新條目            無新條目
   │                    │
   ▼                    ▼
發送 Email           直接結束
寫入 logs/YYYY-MM.md
更新 history.txt
Commit & Push 回 main
```

## 快速開始

### 本地執行

```bash
pip install feedparser

export EMAIL_FROM="your-email@gmail.com"
export EMAIL_TO="recipient@gmail.com"
export SMTP_PASSWORD="your-gmail-app-password"

python zh-wikipedia-ariticle-report.py
```

> **Dry Run 模式**：未設定 `EMAIL_FROM` 或 `SMTP_PASSWORD` 時，程式仍會正常執行並列印結果，只會靜默略過發信。

### 自訂關鍵字

透過環境變數 `KEYWORDS` 以逗號分隔傳入，例如：

```bash
export KEYWORDS="羽球,羽毛球,桌球"
python zh-wikipedia-ariticle-report.py
```

在 GitHub Actions 中，於 Repository **Variables**（非 Secrets）新增 `KEYWORDS` 即可覆蓋預設值。

## GitHub Actions 部署

### 必要 Secrets

前往 `Settings → Secrets and variables → Actions` 新增以下三個 Secret：

| 名稱 | 說明 |
|------|------|
| `EMAIL_FROM` | 寄件人 Gmail 地址 |
| `EMAIL_TO` | 收件人 Email 地址 |
| `SMTP_PASSWORD` | Gmail 應用程式密碼（App Password） |

### 排程

工作流程檔案位於 `.github/workflows/watchdog.yml`，預設每小時整點（UTC）執行一次：

```yaml
on:
  schedule:
    - cron: '0 * * * *'
  workflow_dispatch:  # 支援手動觸發
```

## 持久化檔案

| 檔案 | 用途 |
|------|------|
| `history.txt` | 已抓取過的 URL 列表（去重用，由 CI 自動 commit） |
| `logs/YYYY-MM.md` | 按月份歸檔的 Markdown 紀錄（由 CI 自動 commit） |

## 相依套件

| 套件 | 用途 |
|------|------|
| `feedparser` | 解析 Wikipedia Atom Feed |

其餘均為 Python 標準函式庫（`smtplib`、`datetime`、`os`、`email.mime.text`）。

## 取得 Gmail 應用程式密碼

1. 前往 [Google 帳戶安全性設定](https://myaccount.google.com/security)
2. 開啟「兩步驟驗證」
3. 搜尋「應用程式密碼」並建立一組新密碼
4. 將產生的 16 位密碼填入 `SMTP_PASSWORD`
