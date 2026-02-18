import typer
from rich.console import Console
from rich.table import Table
from typing import Optional, List
import json
from pathlib import Path

from .searcher import search_all_platforms
from .analyzer import analyze_and_rank
from .generator import generate_outreach_templates

app = typer.Typer(help="Find target customers for your product")
console = Console()

@app.command()
def search(
    keyword: str = typer.Argument(..., help="Product keyword to search"),
    platforms: Optional[List[str]] = typer.Option(
        None, "--platforms", "-p", help="Platforms to search (reddit, hn, ph)"
    ),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of results to show"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Export results to JSON"),
):
    """Search for potential customer channels."""
    
    platforms = platforms or ["reddit", "hn", "ph"]
    
    with console.status(f"[bold green]Searching {', '.join(platforms)}..."):
        results = search_all_platforms(keyword, platforms)
    
    console.print(f"\n[bold]Found {len(results)} discussions[/bold]\n")
    
    with console.status("[bold green]Analyzing discussions..."):
        ranked = analyze_and_rank(results, keyword, limit)
    
    with console.status("[bold green]Generating outreach templates..."):
        for item in ranked:
            item['template'] = generate_outreach_templates(item, keyword)
    
    # Display results
    console.print("[bold cyan]🎯 Top Potential Channels[/bold]\n")
    
    for idx, item in enumerate(ranked, 1):
        console.print(f"[bold yellow]{idx}. {item['channel']}[/bold] (Score: {item['score']}/100)")
        console.print(f"   Platform: {item['platform']}")
        console.print(f"   Title: {item['title'][:80]}...")
        console.print(f"   Engagement: {item['engagement']} interactions")
        console.print(f"   Match: {item['match_level']}")
        console.print(f"   URL: {item['url']}")
        console.print(f"\n   [bold]Outreach Template:[/bold]")
        console.print(f"   {item['template'][:200]}...\n")
    
    # Export if requested
    if output:
        with open(output, 'w') as f:
            json.dump(ranked, f, indent=2)
        console.print(f"[green]✓ Results exported to {output}[/green]")

if __name__ == "__main__":
    app()