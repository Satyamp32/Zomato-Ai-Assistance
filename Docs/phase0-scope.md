# Phase 0 Scope: Zomato AI Recommendation System

## Product Slice for Milestone 1
The primary user-facing surface for Milestone 1 will be a **basic Web UI**. 
The Web UI acts as the source of user input (capturing location, budget, cuisines, and minimum rating) and serves as the primary presentation layer for the AI-generated restaurant recommendations and reasoning.

The CLI (`milestone1`) will remain available as a secondary tool primarily intended for development, diagnostics, and testing the backend pipelines (Phase 1-4) in isolation.

## Technical Stack
- **Language**: Python 3.11+
- **Dependency Manager**: pip (`pyproject.toml` based install)
- **Secrets Management**: Local `.env` file (never committed to version control).

## Non-goals
To avoid scope creep, the following are explicitly deferred:
- User accounts and authentication.
- Live Zomato API integration (we rely entirely on the static Hugging Face dataset).
- Embedded Maps or complex geolocation features.
