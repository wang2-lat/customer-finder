import requests
from typing import List, Dict
from bs4 import BeautifulSoup
import time

class PlatformScraper:
    def __init__(self, config: Dict):
        self.config = config
        self.reddit_enabled = bool(config.get("reddit_client_id"))
    
    def scrape_all_platforms(self, keywords: List[str], limit: int = 10) -> List[Dict]:
        """爬取所有平台数据"""
        channels = []
        
        # Reddit
        if self.reddit_enabled:
            channels.extend(self._scrape_reddit(keywords, limit))
        
        # ProductHunt (公开数据)
        channels.extend(self._scrape_producthunt(keywords, limit))
        
        # IndieHackers (公开数据)
        channels.extend(self._scrape_indiehackers(keywords, limit))
        
        # 按优先级排序
        return sorted(channels, key=lambda x: {"高": 0, "中": 1, "低": 2}[x["priority"]])
    
    def _scrape_reddit(self, keywords: List[str], limit: int) -> List[Dict]:
        """爬取 Reddit 数据"""
        try:
            import praw
            
            reddit = praw.Reddit(
                client_id=self.config["reddit_client_id"],
                client_secret=self.config["reddit_client_secret"],
                user_agent=self.config["reddit_user_agent"]
            )
            
            subreddits = ["SaaS", "startups", "Entrepreneur", "webdev", "programming"]
            channels = []
            
            for subreddit_name in subreddits:
                subreddit = reddit.subreddit(subreddit_name)
                posts = []
                matched_keywords = set()
                
                for keyword in keywords[:3]:  # 限制关键词数量
                    try:
                        for post in subreddit.search(keyword, limit=5):
                            posts.append({
                                "title": post.title,
                                "url": f"https://reddit.com{post.permalink}",
                                "score": post.score
                            })
                            matched_keywords.add(keyword)
                        time.sleep(0.5)  # 避免限流
                    except Exception:
                        continue
                
                if posts:
                    channels.append({
                        "platform": "Reddit",
                        "community": f"r/{subreddit_name}",
                        "discussion_count": len(posts),
                        "matched_keywords": list(matched_keywords),
                        "priority": "高" if len(posts) > 3 else "中",
                        "top_posts": sorted(posts, key=lambda x: x["score"], reverse=True)[:3]
                    })
            
            return channels
        except Exception as e:
            print(f"Reddit 爬取失败: {e}")
            return []
    
    def _scrape_producthunt(self, keywords: List[str], limit: int) -> List[Dict]:
        """爬取 ProductHunt 数据（模拟数据）"""
        # ProductHunt API 需要认证，这里返回模拟数据
        return [{
            "platform": "ProductHunt",
            "community": "Launch Feed",
            "discussion_count": 12,
            "matched_keywords": keywords[:2],
            "priority": "中",
            "top_posts": [{
                "title": "相关产品讨论",
                "url": "https://www.producthunt.com",
                "score": 0
            }]
        }]
    
    def _scrape_indiehackers(self, keywords: List[str], limit: int) -> List[Dict]:
        """爬取 IndieHackers 数据（模拟数据）"""
        return [{
            "platform": "IndieHackers",
            "community": "Growth & Marketing",
            "discussion_count": 8,
            "matched_keywords": keywords[:2],
            "priority": "中",
            "top_posts": [{
                "title": "相关创业讨论",
                "url": "https://www.indiehackers.com",
                "score": 0
            }]
        }]