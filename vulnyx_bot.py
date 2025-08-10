import os
import requests
import xml.etree.ElementTree as ET

# === CONFIG ===
RSS_URL = "https://vulnyx.com/feed/rss.xml"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LAST_VM_FILE = "last_vm.txt"

# Headers to bypass 403 blocks
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

def get_latest_vm():
    try:
        resp = requests.get(RSS_URL, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"[ERROR] Failed to fetch RSS feed — status {resp.status_code}")
            return None
        root = ET.fromstring(resp.content)
        latest_item = root.find("./channel/item")
        if latest_item is None:
            print("[ERROR] RSS feed parsed but no <item> found.")
            return None
        title = latest_item.find("title").text
        link = latest_item.find("link").text
        return title, link
    except Exception as e:
        print(f"[ERROR] Exception while fetching RSS: {e}")
        return None

def read_last_vm():
    if os.path.exists(LAST_VM_FILE):
        with open(LAST_VM_FILE, "r") as f:
            return f.read().strip()
    return None

def write_last_vm(vm_title):
    with open(LAST_VM_FILE, "w") as f:
        f.write(vm_title.strip())

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True}
    try:
        resp = requests.post(url, json=payload)
        if resp.status_code != 200:
            print(f"[ERROR] Telegram API error {resp.status_code}: {resp.text}")
        else:
            print("[INFO] Telegram message sent successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("[ERROR] BOT_TOKEN or CHAT_ID not set. Check GitHub Secrets.")
        exit(1)

    latest_vm = get_latest_vm()
    if not latest_vm:
        print("[INFO] Skipping — no valid feed data this run.")
        exit(0)

    title, link = latest_vm
    last_vm = read_last_vm()

    if title != last_vm:
        message = f"🆕 New VulNyx VM: {title}\n{link}"
        send_telegram_message(message)
        write_last_vm(title)
        print(f"[INFO] New VM found and saved: {title}")
    else:
        print("[INFO] No new VM since last check.")
