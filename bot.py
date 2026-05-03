import requests
from bs4 import BeautifulSoup
import os
import json

# उन वेबसाइट्स की लिस्ट जिन्हें चेक करना है
URLS = [
    "https://rpsc.rajasthan.gov.in/news",
    "https://rssb.rajasthan.gov.in/news",
    "https://rpsc.rajasthan.gov.in/results",
    "https://rssb.rajasthan.gov.in/results"
]

TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
DATA_FILE = "last_updates.json"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    return requests.post(url, data=payload)

def get_updates(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        # ताज़ा लिंक ढूंढना
        first_link = soup.find('a', href=True)
        if first_link:
            return {"text": first_link.get_text(strip=True), "link": first_link['href']}
    except: return None
    return None

def main():
    # पुरानी याददाश्त लोड करना
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: history = json.load(f)
    else: history = {}

    for url in URLS:
        data = get_updates(url)
        if data and data['link'] != history.get(url):
            # नया मैसेज भेजना
            site = "RPSC" if "rpsc" in url else "RSSB"
            msg = f"<b>🔔 {site} नयी अपडेट</b>\n\n📝 {data['text']}\n\n📢 @raj_education_news"
            res = send_msg(msg)
            
            # अगर मैसेज चला गया, तो रिकॉर्ड अपडेट करें
            if res.status_code == 200:
                history[url] = data['link']
    
    # नया रिकॉर्ड सेव करना
    with open(DATA_FILE, "w") as f: json.dump(history, f)

if __name__ == "__main__":
    main()
    
