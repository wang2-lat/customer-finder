import os
import re
import praw
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class RedditScraper:
    """Reddit爬虫"""
    
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "customer-finder/0.1.0")
        )
    
    def search(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """搜索Reddit相关讨论"""
        leads = []
        
        # 聚焦创业和技术相关subreddit
        subreddits = ["SaaS", "startups", "Entrepreneur", "indiehackers", "programming"]
        
        for keyword in keywords[:3]:  # 限制关键词数量避免超时
            try:
                for subreddit_name in subreddits:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    for post in subreddit.search(keyword, limit=limit // len(keywords)):
                        # 提取作者信息
                        author = post.author.name if post.author else "deleted"
                        
                        # 尝试从个人资料提取联系方式
                        contact = self._extract_contact(post)
                        
                        leads.append({
                            "platform": "Reddit",
                            "source": f"r/{subreddit_name}",
                            "title": post.title[:100],
                            "url": f"https://reddit.com{post.permalink}",
                            "author": author,
                            "email": contact.get("email", ""),
                            "score": post.score,
                            "created": post.created_utc,
                        })
            except Exception as e:
                print(f"⚠️  Reddit搜索错误 ({keyword}): {str(e)}")
                continue
        
        return leads
    
    def _extract_contact(self, post) -> Dict[str, str]:
        """从帖子中提取联系方式"""
        contact = {}
        
        # 从帖子内容提取邮箱
        text = f"{post.title} {post.selftext}"
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            contact["email"] = emails[0]
        
        return contact


class ProductHuntScraper:
    """ProductHunt爬虫（公开数据）"""
    
    def search(self, keywords: List[str], limit: int = 20) -> List[Dict]:
        """搜索ProductHunt相关产品和评论"""
        leads = []
        
        try:
            # ProductHunt搜索页面（公开）
            for keyword in keywords[:2]:
                url = f"https://www.producthunt.com/search?q={keyword.replace(' ', '+')}"
                headers = {"User-Agent": "Mozilla/5.0"}
                
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 简化版：提取产品链接（实际需要更复杂的解析）
                products = soup.find_all('a', href=re.compile(r'/posts/'))[:limit]
                
                for product in products:
                    leads.append({
                        "platform": "ProductHunt",
                        "source": "Search",
                        "title": product.get_text(strip=True)[:100],
                        "url": f"https://www.producthunt.com{product['href']}",
                        "author": "",
                        "email": "",
                        "score": 0,
                        "created": "",
                    })
        except Exception as e:
            print(f"⚠️  ProductHunt爬取错误: {str(e)}")
        
        return leads