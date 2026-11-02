import json
import re
import requests

WICHTIGSTE_ARTIKEL_URL = "https://www.20min.ch/wichtige-news"

BASE_URL = "https://www.20min.ch"

COMMENTS_API = "https://api.20min.ch/comment/v1/comments"

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_articles():
    """Holt alle Artikel aus dem __NEXT_DATA__ JSON im HTML."""
    resp = requests.get(WICHTIGSTE_ARTIKEL_URL, headers=HEADERS, timeout=15)
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

def fetch_comments(article_id, limit=30):
    """Holt die Kommentare eines Artikels über die Kommentar-API."""
    params = {"tenantId": 6, "contentId": article_id, "limit": limit, "sortBy": "reactions", "sortOrder": "desc"}
    resp = requests.get(COMMENTS_API, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return [c for c in resp.json().get('comments', []) if c.get('status') == 'ACCEPTED']

def comment_score(comment):
    """"Genau" und "Smart" zählen als Zustimmung, "Unnötig" oder "Quatsch" nicht."""
    reactions = comment.get('reactions', {})
    return reactions.get('exact', 0) + reactions.get('smart', 0) + reactions.get('awesome', 0)

def top_articles_of_day(n=10):
    """Gibt die Top-n Artikel nach Kommentaranzahl zurück."""
    articles = fetch_articles()

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
                "Author": c.get('authorNickname', 'N/A'),
                "Body": c['body'],
                "Score": comment_score(c)
            } for c in comments[:comment_count]]
        })

    return posts_data

if __name__ == "__main__":
    for i, post in enumerate(get_top_articles(5, 3), 1):
        print(f"{i}. {post['Title']} ({post['Comments']} Kommentare) - {post['URL']}")
        for comment in post['Top_Comments']:
            print(f"   [{comment['Score']}] {comment['Author']}: {comment['Body'][:80]!r}")
