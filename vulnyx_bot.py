import os
import requests
import xml.etree.ElementTree as ET

RSS_URL = "https://vulnyx.com/feed/rss.xml"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LAST_VM_FILE = "last_vm.txt"

def get_latest_vm():
    resp = requests.get(RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        print(f"Failed to fetch RSS feed, status {resp.status_code}")
        return None
    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None

    latest_item = root.find(".//item")
    if latest_item is None:
        return None

    title = latest_item.find("title").text.strip()
    link = latest_item.find("link").text.strip()
    return title, link

def read_last_vm():
    if os.path.exists(LAST_VM_FILE):
        with open(LAST_VM_FILE, "r") as f:
            return f.read().strip()
    return None

def write_last_vm(vm_title):
    with open(LAST_VM_FILE, "w") as f:
        f.write(vm_title)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    resp = requests.post(url, data=payload)
    if resp.status_code != 200:
        print(f"Failed to send Telegram message: {resp.text}")

if __name__ == "__main__":
    latest_vm = get_latest_vm()
    if latest_vm is None:
        print("Skipping — feed not valid this run.")
        exit(0)

    title, link = latest_vm
    last_vm = read_last_vm()

    # Warm start: first run, just store current VM without sending
    if last_vm is None:
        print(f"[INFO] First run — storing latest VM without sending: {title}")
        write_last_vm(title)
        exit(0)

    if title != last_vm:
        send_telegram_message(f"🆕 New VulNyx VM: {title}\n{link}")
        write_last_vm(title)
    else:
        print("[INFO] No new VM detected.")
