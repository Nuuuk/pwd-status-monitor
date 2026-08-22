import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

HISTORY_FILE = "last_pwd_status.txt"
URL = "https://flag.dol.gov/processingtimes"

def fetch_webpage_content():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup.get_text(separator="\n", strip=True)

def analyze_and_diff(current_text, last_status):
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
    你是一个数据提取助手。请从以下 DOL Processing Times 网页文本中，找到关于 'Prevailing Wage Determination' (PWD) 的最新处理进度（如 OES, Non-OES, PERM 等对应的处理月份/日期）。

    【上次记录的状态】：
    {last_status if last_status else "暂无历史记录"}

    【当前网页最新文本】：
    {current_text[:8000]}

    请完成两个任务：
    1. 提取当前最新的 PWD 处理状态关键信息（简明结构化）。
    2. 判断相较于【上次记录的状态】是否有进展/更新。

    回复格式要求：
    HAS_CHANGED: [TRUE / FALSE]
    ---CURRENT_DATA---
    [在此处列出当前提取的 PWD 状态摘要，用于下次对比]
    ---EMAIL_BODY---
    [如果 HAS_CHANGED 为 TRUE，请用中文写一段简洁的邮件正文，说明哪些项目的排期推进了。如果为 FALSE，此处留空。]
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, EMAIL_APP_PASSWORD)
        server.send_message(msg)
    print("通知邮件已成功发送！")

def main():
    last_status = ""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            last_status = f.read()

    print("正在抓取 DOL 官网页面...")
    page_text = fetch_webpage_content()

    print("正在调用 Gemini 分析状态差异...")
    llm_output = analyze_and_diff(page_text, last_status)

    has_changed = "HAS_CHANGED: TRUE" in llm_output
    current_data = ""

    if "---CURRENT_DATA---" in llm_output:
        current_data = llm_output.split("---CURRENT_DATA---")[1].split("---EMAIL_BODY---")[0].strip()
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write(current_data)

    if has_changed or not last_status:
        email_body = llm_output.split("---EMAIL_BODY---")[-1].strip()
        if not email_body:
            email_body = f"DOL PWD 状态初始化记录完成，当前状态如下：\n\n{current_data}"
        send_email("【FLAG DOL】PWD 处理进度有更新！", email_body)
    else:
        print("PWD 状态无更新，无需发送邮件。")

if __name__ == "__main__":
    main()
