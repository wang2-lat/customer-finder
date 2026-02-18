import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
from typing import Optional

from .analyzer import CustomerAnalyzer
from .scraper import PlatformScraper
from .config import load_config

app = typer.Typer(help="帮技术创始人找到产品的真实付费客户渠道")
console = Console()

@app.command()
def analyze(
    product_description: str = typer.Argument(..., help="产品描述"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出文件路径 (JSON)"),
    limit: int = typer.Option(10, "--limit", "-l", help="每个平台的结果数量")
):
    """分析产品并找到潜在客户渠道"""
    
    try:
        config = load_config()
    except Exception as e:
        console.print(f"[red]配置错误: {e}[/red]")
        console.print("请创建 .env 文件并配置 API keys")
        raise typer.Exit(1)
    
    with console.status("[bold green]分析客户画像..."):
        analyzer = CustomerAnalyzer(config["openai_api_key"])
        persona = analyzer.analyze_customer_persona(product_description)
    
    console.print("\n📊 [bold]客户画像分析[/bold]")
    console.print("━" * 50)
    console.print(f"目标客户: {persona['target_customers']}")
    console.print(f"痛点: {persona['pain_points']}")
    console.print(f"关键词: {', '.join(persona['keywords'])}")
    
    with console.status("[bold green]爬取平台数据..."):
        scraper = PlatformScraper(config)
        channels = scraper.scrape_all_platforms(persona['keywords'], limit)
    
    console.print("\n🎯 [bold]优先级渠道清单[/bold]")
    console.print("━" * 50)
    
    for idx, channel in enumerate(channels, 1):
        priority_emoji = "🔥" if channel['priority'] == "高" else "⭐" if channel['priority'] == "中" else "💡"
        console.print(f"\n{idx}. {priority_emoji} {channel['platform']} - {channel['community']}")
        console.print(f"   优先级: {channel['priority']}")
        console.print(f"   相关讨论: {channel['discussion_count']} 条")
        console.print(f"   关键词匹配: {', '.join(channel['matched_keywords'][:3])}")
        
        if channel['top_posts']:
            console.print(f"   热门帖子: {channel['top_posts'][0]['title'][:60]}...")
            console.print(f"   链接: {channel['top_posts'][0]['url']}")
    
    with console.status("[bold green]生成联系模板..."):
        templates = analyzer.generate_outreach_templates(persona, channels[:3])
    
    console.print("\n📧 [bold]联系方式模板[/bold]")
    console.print("━" * 50)
    for template in templates:
        console.print(f"\n[cyan]{template['channel']}[/cyan]")
        console.print(template['template'])
    
    if output:
        result = {
            "persona": persona,
            "channels": channels,
            "templates": templates
        }
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        console.print(f"\n✅ 结果已保存到: {output}")

if __name__ == "__main__":
    app()