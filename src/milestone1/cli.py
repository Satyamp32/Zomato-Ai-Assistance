import typer
from milestone1.phase0 import info
from milestone1.phase1_ingestion import loader
from milestone1.phase2_preferences.parser import parse_preferences
from milestone1.phase3_integration.filter import filter_and_rank
from milestone1.phase3_integration.prompt_builder import build_prompt_payload
from milestone1.phase4_llm.client import recommend_with_groq
from milestone1.phase4_llm.models import LLMRecommendation
from typing import List, Optional

app = typer.Typer(help="Zomato AI Recommendation System CLI")

@app.command()
def info_cmd():
    """Display information about the project scope and environment."""
    info.print_info()

@app.command()
def doctor():
    """Check if the environment is correctly configured."""
    info.run_doctor()

@app.command()
def ingest(limit: int = typer.Option(10, help="Number of records to display")):
    """Download and ingest data from Hugging Face."""
    loader.ingest_smoke_test(limit=limit)

@app.command()
def prefs_parse(
    location: str = typer.Option(..., help="City or location"),
    budget: str = typer.Option("medium", help="Budget band (low/medium/high)"),
    cuisines: str = typer.Option("", help="Comma separated list of cuisines"),
    min_rating: float = typer.Option(0.0, help="Minimum rating out of 5.0")
):
    """Parse and validate user preferences."""
    data = {
        "location": location,
        "budget": budget,
        "cuisines": cuisines.split(",") if cuisines else [],
        "min_rating": min_rating
    }
    try:
        prefs = parse_preferences(data)
        typer.echo("Preferences parsed successfully!")
        typer.echo(prefs.model_dump_json(indent=2))
    except Exception as e:
        typer.echo(f"Error parsing preferences: {e}", err=True)

@app.command()
def prompt_build(
    location: str = typer.Option(..., help="City or location"),
    budget: str = typer.Option("medium", help="Budget band"),
    cuisines: str = typer.Option("", help="Comma separated list of cuisines"),
    min_rating: float = typer.Option(0.0, help="Minimum rating"),
    limit: int = typer.Option(100, help="Max candidates to load from Hugging Face")
):
    """Build the LLM prompt payload using deterministic filtering."""
    data = {
        "location": location,
        "budget": budget,
        "cuisines": cuisines.split(",") if cuisines else [],
        "min_rating": min_rating
    }
    try:
        prefs = parse_preferences(data)
        typer.echo(f"Loading {limit} restaurants to filter against...")
        restaurants = loader.load_restaurants(limit=limit)
        
        filtered = filter_and_rank(prefs, restaurants)
        typer.echo(f"Filtered down to {len(filtered)} candidates.")
        
        prompt = build_prompt_payload(prefs, filtered)
        typer.echo("\n--- GENERATED PROMPT ---")
        typer.echo(prompt)
    except Exception as e:
        typer.echo(f"Error building prompt: {e}", err=True)

@app.command()
def recommend(
    location: str = typer.Option(..., help="City or location"),
    budget: str = typer.Option("medium", help="Budget band (low/medium/high)"),
    cuisines: str = typer.Option("", help="Comma separated list of cuisines"),
    min_rating: float = typer.Option(0.0, help="Minimum rating"),
    limit: int = typer.Option(100, help="Max candidates to load from Hugging Face"),
    top_k: int = typer.Option(5, help="Number of recommendations to get from LLM")
):
    """Run the full end-to-end recommendation pipeline."""
    # We map numerical budget to "high" based on user context if needed, 
    # but the parser handles string coercion gracefully.
    data = {
        "location": location,
        "budget": budget,
        "cuisines": cuisines.split(",") if cuisines else [],
        "min_rating": min_rating
    }
    
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        console = Console()
        
        console.print("[yellow]Parsing preferences...[/yellow]")
        prefs = parse_preferences(data)
        
        console.print(f"[yellow]Loading dataset (limit={limit})...[/yellow]")
        restaurants = loader.load_restaurants(limit=limit)
        
        console.print("[yellow]Filtering candidates...[/yellow]")
        filtered = filter_and_rank(prefs, restaurants)
        if not filtered:
            console.print("[bold red]No candidates match the exact criteria.[/bold red]")
            raise typer.Exit()
            
        console.print(f"[green]Found {len(filtered)} matching candidates.[/green]")
        prompt = build_prompt_payload(prefs, filtered)
        
        console.print("[yellow]Querying Groq LLM...[/yellow]")
        recs = recommend_with_groq(prompt, top_k=top_k)
        
        console.print("\n[bold blue]--- TOP RECOMMENDATIONS ---[/bold blue]\n")
        for idx, rec in enumerate(recs, 1):
            console.print(Panel(
                f"[bold green]Name:[/bold green] {rec.restaurant_name}\n\n[bold cyan]Why:[/bold cyan] {rec.explanation}",
                title=f"Recommendation #{idx}",
                expand=False
            ))
            
    except Exception as e:
        typer.echo(f"Recommendation failed: {e}", err=True)

if __name__ == "__main__":
    app()
