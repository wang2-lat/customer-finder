import typer
import json
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table

from .scrapers import RedditScraper, HackerNewsScraper, ProductHuntScraper
from .analyzer import CustomerAnalyzer
from .outreach import OutreachGenerator

app = typer.Typer(help="自动发现和验证潜在付费客户的 CLI 工具")
console = Console()

@app.command()
def search(
    keywords: str = typer.Argument(..., help="产品关键词"),
    platforms: Optional[List[str]] = typer.Option(
        ["reddit", "hackernews", "producthunt"],
        "--platforms",
        "-p",
        help="搜索平台"
    ),
    days: int = typer.Option(30, "--days", "-d", help="搜索最近 N 天"),
    min_score: int = typer.Option(3, "--min-score", "-s", help="最低评分"),
    output: Path = typer.Option("customers.json", "--output", "-o", help="输出文件"),
    limit: int = typer.Option(50, "--limit", "-l", help="每平台最多结果数"),
):
    """搜索潜在客户"""
    console.print(f"[bold green]搜索关键词:[/bold green] {keywords}")
    console.print(f"[bold green]平台:[/bold green] {', '.join(platforms)}")
    
    all_results = []
    
    # Reddit
    if "reddit" in platforms:
        with console.status("[bold yellow]正在搜索 Reddit..."):
            try:
                scraper = RedditScraper()
                results = scraper.search(keywords, days=days, limit=limit)
                all_results.extend(results)
                console.print(f"[green]✓[/green] Reddit: 找到 {len(results)} 条结果")
            except Exception as e:
                console.print(f"[red]✗[/red] Reddit 错误: {e}")
    
    # HackerNews
    if "hackernews" in platforms:
        with console.status("[bold yellow]正在搜索 HackerNews..."):
            try:
                scraper = HackerNewsScraper()
                results = scraper.search(keywords, days=days, limit=limit)
                all_results.extend(results)
                console.print(f"[green]✓[/green] HackerNews: 找到 {len(results)} 条结果")
            except Exception as e:
                console.print(f"[red]✗[/red] HackerNews 错误: {e}")
    
    # ProductHunt
    if "producthunt" in platforms:
        with console.status("[bold yellow]正在搜索 ProductHunt..."):
            try:
                scraper = ProductHuntScraper()
                results = scraper.search(keywords, days=days, limit=limit)
                all_results.extend(results)
                console.print(f"[green]✓[/green] ProductHunt: 找到 {len(results)} 条结果")
            except Exception as e:
                console.print(f"[red]✗[/red] ProductHunt 错误: {e}")
    
    # 分析和过滤
    analyzer = CustomerAnalyzer()
    customers = analyzer.analyze(all_results, min_score=min_score)
    
    # 保存结果
    output.write_text(json.dumps(customers, indent=2, ensure_ascii=False))
    console.print(f"\n[bold green]✓ 找到 {len(customers)} 个潜在客户[/bold green]")
    console.print(f"[bold]结果已保存到:[/bold] {output}")
    
    # 显示预览
    if customers:
        table = Table(title="潜在客户预览（前 5 条）")
        table.add_column("平台", style="cyan")
        table.add_column("作者", style="magenta")
        table.add_column("标题", style="green")
        table.add_column("评分", style="yellow")
        
        for customer in customers[:5]:
            table.add_row(
                customer["platform"],
                customer["author"],
                customer["title"][:50] + "..." if len(customer["title"]) > 50 else customer["title"],
                str(customer["score"])
            )
        
        console.print(table)

@app.command()
def generate_outreach(
    input_file: Path = typer.Argument(..., help="客户列表 JSON 文件"),
    product: str = typer.Option(..., "--product", "-p", help="你的产品名称"),
    output: Path = typer.Option("outreach.txt", "--output", "-o", help="输出文件"),
):
    """生成个性化触达话术"""
    if not input_file.exists():
        console.print(f"[red]错误:[/red] 文件不存在: {input_file}")
        raise typer.Exit(1)
    
    customers = json.loads(input_file.read_text())
    generator = OutreachGenerator(product)
    
    with console.status("[bold yellow]正在生成触达话术..."):
        outreach_messages = generator.generate(customers)
    
    output.write_text(outreach_messages)
    console.print(f"[bold green]✓ 已生成 {len(customers)} 条触达话术[/bold green]")
    console.print(f"[bold]结果已保存到:[/bold] {output}")

if __name__ == "__main__":
    app()