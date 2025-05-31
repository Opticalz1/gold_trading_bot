import requests
import os
from dotenv import load_dotenv

load_dotenv("config.env")

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload)
        print("📨 Telegram alert sent.")
    except:
        print("❌ Failed to send Telegram alert.")
