import requests
from typing import List, Dict
import os

def search_reddit(keyword: str) -> List[Dict]:
    """Search Reddit for discussions."""
    results = []
    
    # Try with credentials, fallback to public search
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    
    if client_id and client_secret:
        try:
            import praw
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=os.getenv('REDDIT_USER_AGENT', 'customer-finder/0.1')
            )
            
            for submission in reddit.subreddit('all').search(keyword, limit=20):
                results.append({
                    'platform': 'reddit',
                    'channel': f"r/{submission.subreddit.display_name}",
                    'title': submission.title,
                    'url': f"https://reddit.com{submission.permalink}",
                    'engagement': submission.score + submission.num_comments,
                    'content': submission.selftext[:500]
                })
        except Exception:
            pass
    
    # Fallback to public API
    if not results:
        try:
            url = f"https://www.reddit.com/search.json?q={keyword}&limit=20"
            headers = {'User-Agent': 'customer-finder/0.1'}
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            
            for post in data.get('data', {}).get('children', []):
                p = post['data']
                results.append({
                    'platform': 'reddit',
                    'channel': f"r/{p['subreddit']}",
                    'title': p['title'],
                    'url': f"https://reddit.com{p['permalink']}",
                    'engagement': p['score'] + p['num_comments'],
                    'content': p.get('selftext', '')[:500]
                })
        except Exception:
            pass
    
    return results

def search_hackernews(keyword: str) -> List[Dict]:
    """Search HackerNews via Algolia API."""
    results = []
    
    try:
        url = f"https://hn.algolia.com/api/v1/search?query={keyword}&tags=story&hitsPerPage=20"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        for hit in data.get('hits', []):
            results.append({
                'platform': 'hackernews',
                'channel': 'HackerNews',
                'title': hit.get('title', ''),
                'url': hit.get('url') or f"https://news.ycombinator.com/item?id={hit['objectID']}",
                'engagement': hit.get('points', 0) + hit.get('num_comments', 0),
                'content': hit.get('story_text', '')[:500]
            })
    except Exception:
        pass
    
    return results

def search_producthunt(keyword: str) -> List[Dict]:
    """Search ProductHunt via public search."""
    results = []
    
    try:
        # Using PH's public search page
        url = f"https://www.producthunt.com/search?q={keyword}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Note: This is a simplified version. Real implementation would parse HTML
        # For MVP, we'll return placeholder data
        results.append({
            'platform': 'producthunt',
            'channel': 'ProductHunt',
            'title': f"Search results for '{keyword}'",
            'url': url,
            'engagement': 0,
            'content': f"Check ProductHunt for '{keyword}' discussions"
        })
    except Exception:
        pass
    
    return results

def search_all_platforms(keyword: str, platforms: List[str]) -> List[Dict]:
    """Search all specified platforms."""
    all_results = []
    
    if 'reddit' in platforms:
        all_results.extend(search_reddit(keyword))
    
    if 'hn' in platforms:
        all_results.extend(search_hackernews(keyword))
    
    if 'ph' in platforms:
        all_results.extend(search_producthunt(keyword))
    
    return all_results