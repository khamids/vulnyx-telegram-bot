import requests
import xml.etree.ElementTree as ET
import json
import os

RSS_URL = "https://vulnyx.com/feed/rss.xml"
BOT_TOKEN = os.getenv("7843128995:AAHyAgO91PRYpnRsgjHkMdic9hp-kkvNGts")
CHAT_ID = os.getenv("165689956")
STATE_FILE = "last_vm.json"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def get_latest_vm():
    resp = requests.get(RSS_URL)
    root = ET.fromstring(resp.content)
    channel = root.find("channel")
    latest_item = channel.find("item")
    title = latest_item.find("title").text
    link = latest_item.find("link").text
    date = latest_item.find("pubDate").text
    return {"title": title, "link": link, "date": date}

def load_last_vm():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return None

def save_last_vm(vm):
    with open(STATE_FILE, "w") as f:
        json.dump(vm, f)

if __name__ == "__main__":
    latest_vm = get_latest_vm()
    last_vm = load_last_vm()

    if not last_vm or latest_vm["title"] != last_vm["title"]:
        message = f"🆕 New VulNyx VM Released!\n\n*{latest_vm['title']}*\n{latest_vm['link']}\nDate: {latest_vm['date']}"
        send_telegram_message(message)
        save_last_vm(latest_vm)
