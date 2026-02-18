#!/usr/bin/env python3
import os
import json
from typing import List, Dict
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import praw
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer(help="自动发现和验证目标客户的 CLI 工具")
console = Console()

class CustomerFinder:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )
    
    def generate_persona(self, product_desc: str) -> Dict:
        """根据产品描述生成目标客户画像"""
        prompt = f"""
        产品描述: {product_desc}
        
        请生成目标客户画像，包含:
        1. 客户类型（技术创始人/独立开发者/产品经理等）
        2. 主要痛点（3-5个）
        3. 搜索关键词（用于在社交媒体搜索，5-10个）
        4. 典型使用场景
        
        以JSON格式返回，格式如下:
        {{
            "customer_type": "...",
            "pain_points": ["...", "..."],
            "search_keywords": ["...", "..."],
            "use_cases": ["...", "..."]
        }}
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def search_reddit(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """从 Reddit 搜索相关讨论"""
        results = []
        subreddits = ["SaaS", "startups", "Entrepreneur", "indiehackers", "buildinpublic"]
        
        for keyword in keywords[:3]:  # 限制关键词数量
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    for post in subreddit.search(keyword, limit=limit//len(keywords)//len(subreddits)):
                        results.append({
                            "platform": "Reddit",
                            "title": post.title,
                            "content": post.selftext[:500],
                            "author": str(post.author),
                            "url": f"https://reddit.com{post.permalink}",
                            "score": post.score
                        })
                except Exception as e:
                    console.print(f"[yellow]Reddit 搜索警告: {e}[/yellow]")
        
        return results
    
    def search_hackernews(self, keywords: List[str], limit: int = 30) -> List[Dict]:
        """从 HackerNews 搜索相关讨论"""
        results = []
        
        for keyword in keywords[:3]:
            try:
                url = f"https://hn.algolia.com/api/v1/search?query={keyword}&tags=story&hitsPerPage={limit//len(keywords)}"
                response = requests.get(url, timeout=10)
                data = response.json()
                
                for hit in data.get("hits", []):
                    results.append({
                        "platform": "HackerNews",
                        "title": hit.get("title", ""),
                        "content": hit.get("story_text", "")[:500],
                        "author": hit.get("author", ""),
                        "url": hit.get("url", ""),
                        "score": hit.get("points", 0)
                    })
            except Exception as e:
                console.print(f"[yellow]HackerNews 搜索警告: {e}[/yellow]")
        
        return results
    
    def analyze_leads(self, discussions: List[Dict], persona: Dict) -> List[Dict]:
        """分析讨论内容，提取潜在客户"""
        if not discussions:
            return []
        
        # 合并讨论内容
        content_sample = "\n\n".join([
            f"标题: {d['title']}\n内容: {d['content']}\n作者: {d['author']}"
            for d in discussions[:10]  # 只分析前10条
        ])
        
        prompt = f"""
        目标客户画像:
        {json.dumps(persona, ensure_ascii=False, indent=2)}
        
        讨论内容样本:
        {content_sample}
        
        请分析这些讨论，提取潜在客户信息，包含:
        1. 用户名
        2. 痛点匹配度 (0-100)
        3. 具体痛点描述
        4. 推荐接触理由
        
        返回JSON数组，格式:
        [{{
            "username": "...",
            "match_score": 85,
            "pain_points": "...",
            "contact_reason": "..."
        }}]
        
        最多返回10个最匹配的潜在客户。
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            leads = result if isinstance(result, list) else result.get("leads", [])
            
            # 添加原始讨论链接
            for lead in leads:
                matching_discussions = [d for d in discussions if d["author"] == lead["username"]]
                if matching_discussions:
                    lead["profile_url"] = matching_discussions[0]["url"]
            
            return leads
        except Exception as e:
            console.print(f"[red]分析失败: {e}[/red]")
            return []
    
    def generate_email_template(self, persona: Dict, lead: Dict) -> str:
        """生成个性化冷邮件模板"""
        prompt = f"""
        目标客户画像: {json.dumps(persona, ensure_ascii=False)}
        潜在客户信息: {json.dumps(lead, ensure_ascii=False)}
        
        生成一封个性化的冷邮件模板（英文），要求:
        1. 简短（100-150词）
        2. 直接提到对方的具体痛点
        3. 清晰的价值主张
        4. 软性的 CTA（不要太推销）
        5. 专业但友好的语气
        
        只返回邮件正文，不要主题行。
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

@app.command()
def find(
    product: str = typer.Option(..., "--product", "-p", help="产品描述"),
    output: str = typer.Option("leads.json", "--output", "-o", help="输出文件路径"),
    limit: int = typer.Option(50, "--limit", "-l", help="搜索结果数量限制")
):
    """根据产品描述查找潜在客户"""
    
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]错误: 未设置 OPENAI_API_KEY[/red]")
        raise typer.Exit(1)
    
    finder = CustomerFinder()
    
    with Progress() as progress:
        task = progress.add_task("[cyan]处理中...", total=5)
        
        # 1. 生成客户画像
        console.print("\n[bold]步骤 1/5:[/bold] 生成目标客户画像...")
        persona = finder.generate_persona(product)
        console.print(f"[green]✓[/green] 客户类型: {persona['customer_type']}")
        console.print(f"[green]✓[/green] 搜索关键词: {', '.join(persona['search_keywords'][:5])}")
        progress.update(task, advance=1)
        
        # 2. 搜索 Reddit
        console.print("\n[bold]步骤 2/5:[/bold] 搜索 Reddit 讨论...")
        reddit_results = finder.search_reddit(persona['search_keywords'], limit)
        console.print(f"[green]✓[/green] 找到 {len(reddit_results)} 条 Reddit 讨论")
        progress.update(task, advance=1)
        
        # 3. 搜索 HackerNews
        console.print("\n[bold]步骤 3/5:[/bold] 搜索 HackerNews 讨论...")
        hn_results = finder.search_hackernews(persona['search_keywords'], limit)
        console.print(f"[green]✓[/green] 找到 {len(hn_results)} 条 HackerNews 讨论")
        progress.update(task, advance=1)
        
        # 4. 分析潜在客户
        console.print("\n[bold]步骤 4/5:[/bold] 分析潜在客户...")
        all_discussions = reddit_results + hn_results
        leads = finder.analyze_leads(all_discussions, persona)
        console.print(f"[green]✓[/green] 识别出 {len(leads)} 个潜在客户")
        progress.update(task, advance=1)
        
        # 5. 生成邮件模板
        console.print("\n[bold]步骤 5/5:[/bold] 生成邮件模板...")
        for lead in leads[:3]:  # 只为前3个生成邮件
            lead["email_template"] = finder.generate_email_template(persona, lead)
        progress.update(task, advance=1)
    
    # 保存结果
    result = {
        "persona": persona,
        "leads": leads,
        "total_discussions": len(all_discussions)
    }
    
    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 显示结果表格
    console.print(f"\n[bold green]✓ 完成！结果已保存到 {output}[/bold green]\n")
    
    if leads:
        table = Table(title="潜在客户列表（Top 10）")
        table.add_column("用户名", style="cyan")
        table.add_column("匹配度", style="magenta")
        table.add_column("痛点", style="yellow")
        table.add_column("链接", style="blue")
        
        for lead in leads[:10]:
            table.add_row(
                lead.get("username", "N/A"),
                f"{lead.get('match_score', 0)}%",
                lead.get("pain_points", "")[:50] + "...",
                lead.get("profile_url", "N/A")[:40]
            )
        
        console.print(table)

@app.command()
def show(
    file: str = typer.Argument("leads.json", help="结果文件路径")
):
    """显示已保存的潜在客户列表"""
    
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        console.print(f"\n[bold]客户画像:[/bold]")
        console.print(f"类型: {data['persona']['customer_type']}")
        console.print(f"痛点: {', '.join(data['persona']['pain_points'])}")
        
        console.print(f"\n[bold]找到 {len(data['leads'])} 个潜在客户[/bold]\n")
        
        for i, lead in enumerate(data['leads'], 1):
            console.print(f"[bold cyan]{i}. {lead['username']}[/bold cyan] (匹配度: {lead['match_score']}%)")
            console.print(f"   痛点: {lead['pain_points']}")
            console.print(f"   链接: {lead.get('profile_url', 'N/A')}")
            
            if "email_template" in lead:
                console.print(f"\n   [bold]邮件模板:[/bold]")
                console.print(f"   {lead['email_template']}\n")
            console.print()
    
    except FileNotFoundError:
        console.print(f"[red]错误: 文件 {file} 不存在[/red]")
        raise typer.Exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]错误: 文件 {file} 格式无效[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()