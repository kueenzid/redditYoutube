import json
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

WICHTIGSTE_ARTIKEL_URL = "https://www.20min.ch/wichtige-news"

BASE_URL = "https://www.20min.ch"

# Die Startseite hat alle aktuellen Artikel, "Wichtige News" auch mehrere Tage alte
HOMEPAGE_URL = f"{BASE_URL}/"

# Google-News-Sitemap mit dem Veröffentlichungsdatum der Artikel der letzten Tage
NEWS_SITEMAP_URL = f"{BASE_URL}/sitemaps/de/news.xml"

# Nur Artikel, die in den letzten so vielen Stunden erschienen sind
MAX_AGE_HOURS = 24

COMMENTS_API = "https://api.20min.ch/comment/v1/comments"

HEADERS = {"User-Agent": "Mozilla/5.0"}

# Gewicht jeder Reaktion beim Sortieren der Kommentare, "So nicht" zählt doppelt
REACTION_WEIGHTS = {
    "exact": 1,        # Genau
    "awesome": 1,      # Love it
    "smart": 1,        # Smart
    "unnecessary": 1,  # Unnötig
    "nonsense": 1,     # Quatsch
    "bad": 2,          # So nicht
}

def fetch_articles(url=HOMEPAGE_URL):
    """Holt alle Artikel aus dem __NEXT_DATA__ JSON im HTML."""
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', resp.text, re.S)
    if not match:
        raise ValueError("__NEXT_DATA__ not found")
    data = json.loads(match.group(1))

    # Rekursiv nach Artikel-Teasern suchen, statt einen fixen Pfad zu erwarten
    articles = {}
    def walk(node):
        if isinstance(node, dict):
            if node.get('type') == 'teaser' and node.get('contentType') == 'article':
                articles.setdefault(node['id'], node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(data['props']['pageProps'])

    if not articles:
        raise ValueError("no articles found in __NEXT_DATA__")
    return list(articles.values())

def fetch_publication_dates():
    """Gibt {Artikel-ID: Veröffentlichungszeit} aus der News-Sitemap zurück."""
    resp = requests.get(NEWS_SITEMAP_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "news": "http://www.google.com/schemas/sitemap-news/0.9"}

    dates = {}
    for url in ET.fromstring(resp.content).findall("s:url", ns):
        match = re.search(r"-(\d+)$", url.findtext("s:loc", "", ns))
        published = url.findtext("news:news/news:publication_date", None, ns)
        if match and published:
            dates[match.group(1)] = datetime.fromisoformat(published)
    return dates

def fetch_comments(article_id, limit=100):
    """Holt die Kommentare eines Artikels über die Kommentar-API."""
    params = {"tenantId": 6, "contentId": article_id, "limit": limit, "sortBy": "reactions", "sortOrder": "desc"}
    resp = requests.get(COMMENTS_API, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json().get('comments', [])

def comment_score(comment):
    """Alle Reaktionen zählen, gewichtet mit REACTION_WEIGHTS: umstrittene Kommentare kommen nach oben."""
    return sum(REACTION_WEIGHTS.get(key, 1) * count for key, count in comment.get('reactions', {}).items())

def censor_nickname(nickname):
    """Zeigt nur den ersten Buchstaben, die Länge des Nicknames bleibt verborgen."""
    return f"{nickname[:1]}****" if nickname else "Anonym"

def top_articles_of_day(n=10):
    """Gibt die Top-n Artikel der letzten 24 Stunden nach Kommentaranzahl zurück."""
    dates = fetch_publication_dates()
    since = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)
    recent = [a for a in fetch_articles() if str(a['id']) in dates]
    articles = [a for a in recent if dates[str(a['id'])] >= since]

    if not articles:
        print(f"Keine Artikel der letzten {MAX_AGE_HOURS} Stunden gefunden, nehme die der letzten Tage")
        articles = recent

    for a in articles:
        a['commentCount'] = a.get('community', {}).get('comments', 0)

    articles_sorted = sorted(articles, key=lambda x: x['commentCount'], reverse=True)

    return articles_sorted[:n]

def get_top_articles(limit, comment_count, max_comment_length=400):
    """Gibt Artikel im selben Format wie reddit.get_hottest_posts() zurück."""
    posts_data = []
    for article in top_articles_of_day(limit):
        comments = [c for c in fetch_comments(article['id']) if len(c['body']) <= max_comment_length]
        comments.sort(key=comment_score, reverse=True)

        posts_data.append({
            "Id": str(article['id']),
            "Title": article.get('title'),
            "URL": f"{BASE_URL}{article.get('url')}",
            "Comments": article['commentCount'],
            "Top_Comments": [{
                "Author": censor_nickname(c.get('authorNickname')),
                "Body": c['body'],
                "Score": comment_score(c),
                "Reactions": c.get('reactions', {})
            } for c in comments[:comment_count]]
        })

    return posts_data

if __name__ == "__main__":
    for i, post in enumerate(get_top_articles(5, 3), 1):
        print(f"{i}. {post['Title']} ({post['Comments']} Kommentare) - {post['URL']}")
        for comment in post['Top_Comments']:
            print(f"   [{comment['Score']}] {comment['Author']}: {comment['Body'][:80]!r}")
