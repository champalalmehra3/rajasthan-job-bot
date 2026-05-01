import requests
from bs4 import BeautifulSoup
import os
import json

URLS = [
    "https://rpsc.rajasthan.gov.in/syllabus",
    "https://rpsc.rajasthan.gov.in/results",
    "https://rpsc.rajasthan.gov.in/advertisements",
    "https://rpsc.rajasthan.gov.in/news",
    "https://rssb.rajasthan.gov.in/news",
    "https://rssb.rajasthan.gov.in/results",
    "https://rssb.rajasthan.gov.in/answerkeys",
    "https://rssb.rajasthan.gov.in/advertisements",
    "https://rssb.rajasthan.gov.in/oldpapers",
    "https://rssb.rajasthan.gov.in/examscheme"
]

TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
DATA_FILE = "last_updates.json"

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=payload)

def get_latest_info(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            text = link.get_text(strip=True)
            if len(text) > 10 and ('.pdf' in href.lower() or 'javascript:void' not in href.lower()):
                full_url = href if href.startswith('http') else f"{url.split('.in')[0]}.in{href}"
                return {"text": text, "url": full_url}
    except: return None
    return None

def main():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: history = json.load(f)
    else: history = {}
    new_history = {}
    for url in URLS:
        info = get_latest_info(url)
        if info:
            current_link = info['url']
            if history.get(url) != current_link:
                page_name = url.split('/')[-1].capitalize()
                site_name = "RPSC" if "rpsc" in url else "RSSB"
                msg = f"<b>🔔 {site_name} नयी अपडेट ({page_name})</b>\n\n📝 {info['text']}\n\n🔗 <a href='{current_link}'>यहाँ क्लिक करें</a>\n\n📢 @raj_education_news"
                send_telegram_msg(msg)
            new_history[url] = current_link
    with open(DATA_FILE, "w") as f: json.dump(new_history, f)

if __name__ == "__main__":
    main()
  
