import os
import requests
import datetime

API_KEY       = os.getenv('NEWSAPI_KEY')
WEBHOOK_URL   = os.getenv('DISCORD_WEBHOOK_URL')
SOURCES       = 'hacker-news,techcrunch,wired'
KEYWORDS      = [
    "zero-day", "vulnerability", "exploit", "ransomware",
    "government breach", "data breach", "cyberattack",
    "critical infrastructure", "nation state", "hackers", "palo alto networks"
]

def post_to_discord(article):
    content = f"**{article['title']}**\n" \
              f"Source: {article['source']['name']}\n" \
              f"Published: {article['publishedAt']}\n" \
              f"<{article['url']}>"
    resp = requests.post(WEBHOOK_URL, json={'content': content})
    if resp.status_code != 204:
        print(f"❌ Discord error {resp.status_code}: {resp.text}")

def fetch_and_post():
    now   = datetime.datetime.now(datetime.timezone.utc)
    start = now - datetime.timedelta(minutes=45)  # safe buffer
    from_date = start.isoformat()
    to_date   = now.isoformat()

    url = 'https://newsapi.org/v2/everything'
    found = []

    params = {
        'apiKey': API_KEY,
        'sources': SOURCES,
        'from': from_date,
        'to': to_date,
        'sortBy': 'publishedAt',
        'language': 'en',
        'pageSize': 100  # get more articles to filter manually
    }

    r = requests.get(url, params=params)
    r.raise_for_status()

    articles = r.json().get('articles', [])
    for art in articles:
        title_lower = art['title'].lower()
        for kw in KEYWORDS:
            if kw.lower() in title_lower:
                found.append(art)
                break  # stop checking other keywords for this article

    # dedupe by URL
    seen = set()
    for art in found:
        if art['url'] not in seen:
            seen.add(art['url'])
            post_to_discord(art)

if __name__ == "__main__":
    fetch_and_post()
