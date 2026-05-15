from rich.console import Console
from rich.table import Table
import os
import sys

console = Console()

def print_info():
    """Print project scope and details."""
    console.print("\n[bold blue]Zomato AI Recommendation System - Phase 0[/bold blue]")
    console.print("Primary UI: [green]Basic Web UI[/green]")
    console.print("Dataset: [cyan]ManikaSaini/zomato-restaurant-recommendation[/cyan]\n")

def run_doctor():
    """Check environment configuration."""
    table = Table(title="Environment Diagnostic")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="magenta")

    # Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    status = "[green]Pass[/green]" if sys.version_info >= (3, 9) else "[red]Fail (Needs >= 3.9)[/red]"
    table.add_row(f"Python ({python_version})", status)

    # API Keys check
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv("GROQ_API_KEY")
    groq_status = "[green]Set[/green]" if groq_key and groq_key != "your_groq_api_key_here" else "[yellow]Missing/Default[/yellow]"
    table.add_row("GROQ_API_KEY", groq_status)

    console.print(table)
