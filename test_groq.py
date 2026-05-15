import os
from milestone1.phase4_llm.client import recommend_with_groq
from milestone1.phase3_integration.prompt_builder import build_prompt_payload
from milestone1.phase2_preferences.models import UserPreferences
from milestone1.phase1_ingestion.models import Restaurant
from rich.console import Console

console = Console()

prefs = UserPreferences(
    location="Bellandur",
    budget="high",
    cuisines=[],
    min_rating=4.0
)

# Mock some candidates since HuggingFace network stream hangs on this environment
candidates = [
    Restaurant(name="The Boozy Griffin", location="Bellandur, Bangalore", cuisines=["Continental", "Italian"], cost_band="high", rating=4.2),
    Restaurant(name="AB's - Absolute Barbecues", location="Bellandur", cuisines=["North Indian", "BBQ"], cost_band="high", rating=4.8),
    Restaurant(name="Flechazo", location="Bellandur", cuisines=["Asian", "Mediterranean"], cost_band="high", rating=4.6),
    Restaurant(name="Biergarten", location="Bellandur, Outer Ring Road", cuisines=["Continental", "European"], cost_band="high", rating=4.5),
    Restaurant(name="Rural Blues", location="Bellandur", cuisines=["Italian", "European", "Mediterranean"], cost_band="high", rating=4.1),
    Restaurant(name="Moi", location="Bellandur", cuisines=["Desserts"], cost_band="low", rating=3.5), # Should be ignored by LLM conceptually or ranked lower
]

console.print("[yellow]Building Prompt Payload...[/yellow]")
prompt = build_prompt_payload(prefs, candidates)

console.print("[yellow]Querying Groq...[/yellow]")
try:
    recs = recommend_with_groq(prompt, top_k=5)
    console.print("\n[bold green]--- TOP 5 RECOMMENDATIONS FROM GROQ ---[/bold green]")
    for r in recs:
        console.print(f"- [bold]{r.restaurant_name}[/bold]: {r.explanation}")
except Exception as e:
    console.print(f"[bold red]Failed:[/bold red] {e}")
