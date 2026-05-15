# Dataset Contract

## Source
**Hugging Face**: `ManikaSaini/zomato-restaurant-recommendation`

## Field Mapping
This document defines how the columns from the Hugging Face dataset map to our internal `Restaurant` canonical model used throughout the application (Phase 1+).

| Source Dataset Column | Internal Field (`Restaurant` Model) | Expected Type | Normalization Rules |
| :--- | :--- | :--- | :--- |
| `name` | `name` | String | Trim whitespace. |
| `location` | `location` | String | Capitalize first letter. |
| `cuisines` | `cuisines` | List[String] | Split by comma, trim whitespace. |
| `cost` | `cost_band` | String/Enum | Convert exact numeric values to budget bands (e.g., low, medium, high) if applicable, or keep as string/numeric based on Phase 2 needs. Defaulting to String for v1. |
| `rating` | `rating` | Float | Convert string representation to float. Coerce out of bounds (<0 or >5) or invalid strings to 0.0. |

Extra columns from the dataset will be ignored to keep the LLM context window minimal, unless specific columns (like 'type' or 'address') are required for advanced prompts later.
