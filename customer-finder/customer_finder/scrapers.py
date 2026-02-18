import os
import time
from datetime import datetime, timedelta
from typing import List, Dict
import praw
import requests

class RedditScraper:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "customer-finder/0.1")
        )
    
    def search(self, keywords: str, days: int = 30, limit: int = 50) -> List[Dict]:
        results = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 搜索相关 subreddits
        subreddits = ["SaaS", "Entrepreneur", "startups", "smallbusiness", "indiehackers"]
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                for submission in subreddit.search(keywords, limit=limit, time_filter="month"):
                    created = datetime.fromtimestamp(submission.created_utc)
                    if created < cutoff_date:
                        continue
                    
                    results.append({
                        "platform": "reddit",
                        "author": str(submission.author),
                        "title": submission.title,
                        "content": submission.selftext[:500],
                        "url": f"https://reddit.com{submission.permalink}",
                        "score": submission.score,
                        "created_at": created.isoformat(),
                        "contact": f"https://reddit.com/user/{submission.author}"
                    })
                time.sleep(1)  # 避免限流
            except Exception as e:
                print(f"Reddit subreddit {subreddit_name} 错误: {e}")
                continue
        
        return results

class HackerNewsScraper:
    BASE_URL = "https://hn.algolia.com/api/v1"
    
    def search(self, keywords: str, days: int = 30, limit: int = 50) -> List[Dict]:
        results = []
        cutoff_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/search",
                params={
                    "query": keywords,
                    "tags": "(story,comment)",
                    "numericFilters": f"created_at_i>{cutoff_timestamp}",
                    "hitsPerPage": limit
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            for hit in data.get("hits", []):
                results.append({
                    "platform": "hackernews",
                    "author": hit.get("author", "unknown"),
                    "title": hit.get("title") or hit.get("story_title", ""),
                    "content": hit.get("comment_text", "")[:500],
                    "url": f"https://news.ycombinator.com/item?id={hit['objectID']}",
                    "score": hit.get("points", 0),
                    "created_at": hit.get("created_at", ""),
                    "contact": f"https://news.ycombinator.com/user?id={hit.get('author')}"
                })
        except Exception as e:
            print(f"HackerNews 错误: {e}")
        
        return results

class ProductHuntScraper:
    BASE_URL = "https://api.producthunt.com/v2/api/graphql"
    
    def __init__(self):
        self.token = os.getenv("PRODUCTHUNT_API_TOKEN")
    
    def search(self, keywords: str, days: int = 30, limit: int = 50) -> List[Dict]:
        if not self.token:
            print("ProductHunt API token 未配置，跳过")
            return []
        
        results = []
        # ProductHunt API 需要 GraphQL 查询，这里简化处理
        # 实际使用时需要完整实现 GraphQL 查询
        return results