import typer
from pathlib import Path
from typing import Optional
from .scraper import RedditScraper, ProductHuntScraper
from .analyzer import CustomerProfileAnalyzer
from .exporter import CSVExporter

app = typer.Typer(help="帮技术创始人找到产品的真实付费客户渠道")


@app.command()
def find(
    product_description: str = typer.Argument(..., help="产品描述，例如：'AI代码审查工具'"),
    output: Path = typer.Option("customers.csv", "--output", "-o", help="输出CSV文件路径"),
    reddit_limit: int = typer.Option(50, "--reddit-limit", help="Reddit搜索结果数量"),
    ph_limit: int = typer.Option(20, "--ph-limit", help="ProductHunt搜索结果数量"),
):
    """根据产品描述查找潜在付费客户"""
    
    typer.echo(f"🔍 分析产品: {product_description}")
    
    # 1. 生成客户画像和搜索关键词
    analyzer = CustomerProfileAnalyzer()
    profile = analyzer.generate_profile(product_description)
    typer.echo(f"✅ 客户画像: {profile['persona']}")
    typer.echo(f"🔑 搜索关键词: {', '.join(profile['keywords'])}")
    
    # 2. 爬取Reddit讨论
    typer.echo("\n📡 正在爬取 Reddit...")
    reddit_scraper = RedditScraper()
    reddit_leads = reddit_scraper.search(profile['keywords'], limit=reddit_limit)
    typer.echo(f"✅ 找到 {len(reddit_leads)} 条 Reddit 线索")
    
    # 3. 爬取ProductHunt
    typer.echo("\n📡 正在爬取 ProductHunt...")
    ph_scraper = ProductHuntScraper()
    ph_leads = ph_scraper.search(profile['keywords'], limit=ph_limit)
    typer.echo(f"✅ 找到 {len(ph_leads)} 条 ProductHunt 线索")
    
    # 4. 合并并导出
    all_leads = reddit_leads + ph_leads
    if not all_leads:
        typer.echo("❌ 未找到任何潜在客户，请尝试调整产品描述", err=True)
        raise typer.Exit(1)
    
    exporter = CSVExporter()
    exporter.export(all_leads, output)
    typer.echo(f"\n✅ 已导出 {len(all_leads)} 条线索到: {output}")
    typer.echo(f"💡 下一步: 打开CSV文件，筛选高质量线索后发送个性化邮件")


@app.command()
def setup():
    """配置Reddit API密钥"""
    typer.echo("🔧 Reddit API 配置向导")
    typer.echo("\n请访问: https://www.reddit.com/prefs/apps")
    typer.echo("1. 点击 'create another app'")
    typer.echo("2. 选择 'script' 类型")
    typer.echo("3. 复制 client_id 和 client_secret\n")
    
    client_id = typer.prompt("Reddit Client ID")
    client_secret = typer.prompt("Reddit Client Secret", hide_input=True)
    
    env_content = f"""REDDIT_CLIENT_ID={client_id}
REDDIT_CLIENT_SECRET={client_secret}
REDDIT_USER_AGENT=customer-finder/0.1.0
"""
    
    Path(".env").write_text(env_content)
    typer.echo("✅ 配置已保存到 .env 文件")


if __name__ == "__main__":
    app()