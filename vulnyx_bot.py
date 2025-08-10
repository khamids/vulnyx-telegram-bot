import requests
import xml.etree.ElementTree as ET
import os

RSS_URL = "https://vulnyx.com/feed/rss.xml"
BOT_TOKEN = os.getenv("7843128995:AAHyAgO91PRYpnRsgjHkMdic9hp-kkvNGts")
CHAT_ID = os.getenv("165689956")
LAST_VM_FILE = "last_vm.txt"

def get_latest_vm():
    resp = requests.get(RSS_URL, timeout=10)

    # Step 1 — Check HTTP status
    if resp.status_code != 200:
        print(f"Failed to fetch RSS feed, status {resp.status_code}")
        return None

    content = resp.content.strip()

    # Step 2 — Check if looks like XML
    if not content.startswith(b"<?xml") and b"<rss" not in content:
        print("Feed does not look like valid RSS XML.")
        return None

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        print(f"Failed to parse XML: {e}")
        return None

    # Step 3 — Find latest item
    channel = root.find("channel")
    if channel is None:
        print("No channel element found in RSS.")
        return None

    latest_item = channel.find("item")
    if latest_item is None:
        print("No items found in RSS feed.")
        return None

    title = latest_item.find("title").text
    link = latest_item.find("link").text
    date = latest_item.find("pubDate").text
    return {"title": title, "link": link, "date": date}

def read_last_vm():
    if os.path.exists(LAST_VM_FILE):
        with open(LAST_VM_FILE, "r") as f:
            return f.read().strip()
    return None

def write_last_vm(title):
    with open(LAST_VM_FILE, "w") as f:
        f.write(title.strip())

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": False}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code != 200:
            print(f"Failed to send message: {resp.text}")
    except requests.RequestException as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    latest_vm = get_latest_vm()
    if latest_vm is None:
        print("Skipping — feed not valid this run.")
        exit(0)

    last_sent = read_last_vm()
    if last_sent == latest_vm["title"]:
        print(f"No new VM. Last sent: {last_sent}")
        exit(0)

    message = f"🖥 New VulNyx VM Released!\n\nTitle: {latest_vm['title']}\nDate: {latest_vm['date']}\nLink: {latest_vm['link']}"
    send_telegram_message(message)
    write_last_vm(latest_vm["title"])
    print(f"Sent alert for: {latest_vm['title']}")
