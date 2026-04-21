import feedparser
from datetime import datetime, timezone
import os
import smtplib
from email.mime.text import MIMEText

FEED_URLS = [
    "https://zh.wikipedia.org/w/index.php?title=Special:NewPages&feed=atom&limit=50&offset=&namespace=0&username=&tagfilter=&size-mode=min&size=0",
    "https://zh.wikipedia.org/w/index.php?title=Special:NewPages&feed=atom&limit=50&offset=&namespace=14&username=&tagfilter=&size-mode=min&size=0"
]
_kw_env = os.environ.get("KEYWORDS", "")
KEYWORDS = [k.strip() for k in _kw_env.split(",") if k.strip()] or ["羽球", "羽毛球"]
HISTORY_FILE = "history.txt"  # 用來記錄所有抓取過的 URL (程式比對用)
LOG_DIR = "logs"              # 用來存放按月分類的 Markdown 紀錄

EMAIL_TO = os.environ.get("EMAIL_TO")
EMAIL_FROM = os.environ.get("EMAIL_FROM")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def load_history():
    """讀取已經抓取過的網址紀錄"""
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_history(new_urls):
    """將新的網址追加到歷史紀錄中"""
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for url in new_urls:
            f.write(f"{url}\n")

def append_to_monthly_log(entries, dt):
    """將新條目以 Markdown 格式追加到當月紀錄檔"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
    # 產生檔名，例如：logs/2026-04.md
    filename = os.path.join(LOG_DIR, f"{dt.strftime('%Y-%m')}.md")
    
    with open(filename, "a", encoding="utf-8") as f:
        # 如果是該月第一次建立檔案，加上大標題
        if os.path.getsize(filename) == 0:
            f.write(f"# {dt.strftime('%Y年%m月')} 維基百科羽球條目紀錄\n\n")
            
        # 寫入本次抓取的紀錄
        run_time_str = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        f.write(f"### 執行時間: {run_time_str}\n")
        for title, url, desc in entries:
            f.write(f"- [{title}]({url})\n")
        f.write("\n")

def send_email(subject, body):
    if not EMAIL_FROM or not EMAIL_TO or not SMTP_PASSWORD:
        print("未設定 EMAIL_FROM、EMAIL_TO 或 SMTP_PASSWORD，略過發信。")
        return

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, SMTP_PASSWORD)
        server.send_message(msg)
        print("郵件發送成功")

def main():
    seen_urls = load_history()
    new_matches = []  # 存放本次新發現的條目 (Tuple: 標題, 網址, 摘要)
    new_urls = []     # 存放本次新發現的網址 (更新 history 用)
    
    now_utc = datetime.now(timezone.utc)
    
    for feed_url in FEED_URLS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            url = entry.link
            
            # 核心邏輯：如果這個網址已經處理過，直接跳過 (不受更新時間影響)
            if url in seen_urls:
                continue
                
            title = entry.title
            summary = entry.summary if "summary" in entry else ""
            
            if any(kw in title for kw in KEYWORDS) or any(kw in summary for kw in KEYWORDS):
                new_matches.append((title, url, summary))
                new_urls.append(url)
                seen_urls.add(url) # 避免在同一次抓取中重複
    
    if new_matches:
        print(f"找到 {len(new_matches)} 筆新條目，準備發信與存檔...")
        
        # 1. 組合 Email 內容 (確保只有本次抓取的內容)
        email_lines = [f"{title}: {url}" for title, url, _ in new_matches]
        email_content = "本次排程發現以下新條目/分類：\n\n" + "\n\n".join(email_lines)
        send_email("維基百科羽球新條目通知", email_content)
        
        # 2. 存入當月的 Markdown 檔案中
        append_to_monthly_log(new_matches, now_utc)
        
        # 3. 更新歷史紀錄檔
        save_history(new_urls)
    else:
        print("本次排程沒有發現新條目。")

if __name__ == "__main__":
    main()