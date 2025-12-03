import requests

WICHTIGSTE_ARTIKEL_BASE_URL = "https://www.20min.ch/wichstige-news"

BASE_URL = "https://www.20min.ch"

def COMMENTS_API(article_id: str) -> str:
    return f"https://api.20min.ch/comment/v1/comments?tenantId=6&contentId={article_id}&limit=10&sortBy=reactions&sortOrder=desc"

def get_build_id():
    """Extrahiere die aktuelle Next.js Build-ID aus dem HTML."""
    resp = requests.get(WICHTIGSTE_ARTIKEL_BASE_URL)
    resp.raise_for_status()
    html = resp.text

    import re
    match = re.search(r'"buildId":"([^"]+)"', html)
    if not match:
        raise ValueError("Build-ID not found")
    return match.group(1)

def fetch_articles():
    """Holt alle Artikel aus der Next.js _next/data JSON."""
    build_id = get_build_id()
    json_url = f"https://www.20min.ch/_next/data/{build_id}/wichstige-news.json"
    print({json_url})
    resp = requests.get(json_url)
    resp.raise_for_status()
    data = resp.json()

    try:
        articles = data['pageProps']['store']['pageData']['data']['items'][0]['items'][0]['items']
    except KeyError:
        raise ValueError("article-path in JSON not found")

    return articles

def top_articles_of_day(n=10):
    """Gibt die Top-n Artikel nach Kommentaranzahl zurück."""
    articles = fetch_articles()

    for a in articles:
        a['commentCount'] = a.get('community', {}).get('comments', 0)

    articles_sorted = sorted(articles, key=lambda x: x['commentCount'], reverse=True)

    return articles_sorted[:n]

if __name__ == "__main__":
    top = top_articles_of_day()
    for i, a in enumerate(top, 1):
        print(f"{i}. {a.get('title')} ({a.get('commentCount',0)} Kommentare) - {BASE_URL}{a.get('url')}")
        print(COMMENTS_API(a.get('id')))
