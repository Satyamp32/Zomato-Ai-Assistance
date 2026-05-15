import os
from typing import List, Iterator
from datasets import load_dataset
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from milestone1.phase1_ingestion.models import Restaurant

# Load env to optionally get HF_TOKEN
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
console = Console()

def iter_restaurants() -> Iterator[Restaurant]:
    """
    Stream restaurants from Hugging Face and yield validated Canonical models.
    Streaming is used to avoid downloading the entire dataset into memory at once if it's large.
    """
    try:
        # We load the dataset in streaming mode
        dataset = load_dataset(DATASET_ID, split="train", streaming=True, token=HF_TOKEN)
        
        for row in dataset:
            # Map dataset columns to our Pydantic model
            # Based on dataset contract:
            # name -> name, location -> location, cuisines -> cuisines, cost -> cost_band, rating -> rating
            # The actual column names might be slightly different depending on the dataset structure.
            # We will try to dynamically extract them.
            
            # The exact columns from ManikaSaini/zomato-restaurant-recommendation usually include:
            # 'Restaurant Name', 'Location', 'Cuisines', 'Cost', 'Rating' etc. Let's do a case-insensitive map.
            row_lower = {k.lower().strip(): v for k, v in row.items()}
            
            name = row_lower.get("restaurant name") or row_lower.get("name") or "Unknown"
            location = row_lower.get("location") or row_lower.get("city") or "Unknown"
            cuisines = row_lower.get("cuisines", "")
            cost = str(row_lower.get("cost") or row_lower.get("average cost for two") or "medium")
            rating = row_lower.get("rating") or row_lower.get("aggregate rating") or row_lower.get("rate") or 0.0

            try:
                restaurant = Restaurant(
                    name=name,
                    location=location,
                    cuisines=cuisines,
                    cost_band=cost,
                    rating=rating
                )
                yield restaurant
            except Exception:
                # Skip rows that completely fail validation
                continue
                
    except Exception as e:
        console.print(f"[bold red]Error loading dataset:[/bold red] {str(e)}")
        raise

def load_restaurants(limit: int = 100) -> List[Restaurant]:
    """Load a specific number of restaurants into memory."""
    restaurants = []
    for idx, r in enumerate(iter_restaurants()):
        if idx >= limit:
            break
        restaurants.append(r)
    return restaurants

def ingest_smoke_test(limit: int = 10):
    """CLI handler to smoke test ingestion."""
    console.print(f"[bold blue]Downloading top {limit} records from {DATASET_ID}...[/bold blue]")
    
    restaurants = load_restaurants(limit=limit)
    
    table = Table(title=f"Sample Restaurants ({len(restaurants)} loaded)")
    table.add_column("Name", style="cyan")
    table.add_column("Location", style="magenta")
    table.add_column("Rating", style="yellow")
    table.add_column("Cuisines")
    table.add_column("Cost Band")
    
    for r in restaurants:
        table.add_row(
            r.name,
            r.location,
            str(r.rating),
            ", ".join(r.cuisines)[:30] + "..." if len(", ".join(r.cuisines)) > 30 else ", ".join(r.cuisines),
            r.cost_band
        )
        
    console.print(table)
