# Edge Cases & Error Handling Strategy

This document details the potential edge cases across the different architectural phases of the Zomato AI-Powered Restaurant Recommendation System, along with proposed mitigation strategies based on `Docs/ProblemStatement.md` and `Docs/Phase_wise_Architecture.md`.

## 1. Data Ingestion (Phase 1)
*   **Hugging Face Dataset Unavailability:** The source dataset (`ManikaSaini/zomato-restaurant-recommendation`) might be temporarily down, rate-limited, or removed.
    *   *Mitigation:* Support dataset caching locally. Provide a fallback to the cached copy if the upstream is unreachable. Utilize `HF_TOKEN` to increase rate limits.
*   **Schema Mismatch & Malformed Data:** Unexpected data types (e.g., string instead of number for ratings), missing crucial columns, or null values for location/cuisine.
    *   *Mitigation:* Implement strict schema validation (e.g., using Pydantic) during normalization. Discard entirely invalid rows and apply sensible defaults where appropriate.
*   **Extreme or Invalid Values:** Ratings out of bounds (e.g., > 5.0 or negative), negative costs, or excessively long string fields.
    *   *Mitigation:* Coerce ratings to a 0-5 scale. Map cost strings/bands to known enums or fixed numeric ranges. Truncate unusually long strings.

## 2. User Preferences & Validation (Phase 2)
*   **Unrecognized Location:** User queries a city not present in the dataset.
    *   *Mitigation:* Validate against an allowed cities corpus (`allowed_cities_from_restaurants`). Return a clear validation error to the UI/CLI suggesting available cities.
*   **Contradictory/Impossible Preferences:** e.g., "1-star rating minimum" but requesting "Ultra luxury budget", or asking for "Authentic Chinese" in a region where none exist.
    *   *Mitigation:* The filtering layer will naturally return zero results. Ensure the UI guides the user to broaden their search instead of showing a generic error.
*   **Missing or Invalid Boundaries:** Non-numeric minimum rating or unrecognizable budget band submitted in the payload.
    *   *Mitigation:* Coerce to default values (e.g., budget: "medium", rating: 0) or return an HTTP 422 Unprocessable Entity with clear field-level error messages.
*   **Excessive Free-text Length:** The optional "additional preferences" text is extremely long, risking LLM context limits or DoS.
    *   *Mitigation:* Enforce strict character/word limits (e.g., max 500 characters) on free-text inputs at both the API and UI levels.

## 3. Integration Layer & Filtering (Phase 3)
*   **Zero Candidates Found (Over-filtering):** The deterministic hard filters yield 0 matches before reaching the prompt assembly stage.
    *   *Mitigation:* Short-circuit the LLM call entirely. Return an explicit `no_candidates` state to the API so the UI can display: "No restaurants match filters. Try loosening your criteria."
*   **Too Many Candidates Found (Under-filtering):** Filter yields thousands of results, exceeding the LLM context window token limit.
    *   *Mitigation:* Enforce a strict `candidate_cap` (e.g., 15-50). Pre-sort the candidates by a composite score (e.g., highest rating first) to ensure the LLM receives the most relevant subset.
*   **Ambiguous Tie-breaking:** Multiple restaurants have identical ratings and costs, making the pre-sort unpredictable.
    *   *Mitigation:* Introduce a deterministic secondary sort key (e.g., alphabetical by restaurant name) to ensure stable and reproducible results across identical requests.

## 4. Recommendation Engine & LLM (Phase 4)
*   **LLM Provider Outage or Rate Limit:** Groq API experiences timeouts, 5xx errors, or 429 Too Many Requests.
    *   *Mitigation:* Implement basic retry logic. If the LLM ultimately fails, trigger the **deterministic fallback** that returns the top-k pre-sorted candidates with generic template explanations.
*   **Hallucination of Candidates:** The LLM recommends a restaurant that does *not* exist in the provided candidate list.
    *   *Mitigation:* Strictly ground the prompt. Post-process the LLM output to intersect and validate recommended IDs/names against the exact candidate list sent. Drop any unauthorized additions.
*   **Malformed Structured Output:** LLM returns plain text, markdown blocks, or invalid JSON instead of the strictly requested JSON schema.
    *   *Mitigation:* Use strict JSON mode (if supported by Groq) or implement robust JSON parsing. If parsing fails entirely, fallback to deterministic results.
*   **Missing Explanations:** The LLM returns the ranked list but omits the required reasoning.
    *   *Mitigation:* Inject a default explanation (e.g., "Recommended based on your preferences.") during output parsing to maintain UI consistency.

## 5. Backend API & Infrastructure (Phase 6 & 8)
*   **Cold Starts & Load Latency:** Serverless free-tier dynos (Render, Streamlit) go to sleep, causing the first request to take >30 seconds.
    *   *Mitigation:* Add pre-warming background threads for dataset loading on server boot. The UI should feature robust loading spinners and accommodate higher timeout thresholds.
*   **Missing Secrets:** `GROQ_API_KEY` is not configured in the deployment environment.
    *   *Mitigation:* Fail fast during server boot or API health check. `/health` should return `{"status": "ok", "groq_configured": false}` to gracefully aid debugging without crashing.
*   **Concurrency Exhaustion:** Simultaneous requests overwhelm the allowed rate limit for Hugging Face Hub or the Groq API.
    *   *Mitigation:* Keep `candidate_cap` and `load_limit` modest. Optionally introduce simple caching of identical requests if the free-text field is empty.

## 6. Frontend & UI/UX (Phase 5 & 7)
*   **API Network Disconnects & CORS:** The SPA cannot reach the backend due to network issues or misconfigured `CORS_ORIGINS`.
    *   *Mitigation:* Catch network errors explicitly and show a user-friendly "Unable to connect to recommendation service" banner rather than failing silently or hanging.
*   **Visual Overflow:** Extremely long restaurant names, cuisines, or AI explanations break the UI card layout.
    *   *Mitigation:* Implement defensive CSS properties (`word-break: break-word`, `line-clamp`, scrollable explanation areas).
*   **Conflating Empty States:** Users don't know if the failure was their fault (filters too strict) or the system's fault (LLM failed).
    *   *Mitigation:* Maintain distinct UI copy based on API response source:
        *   `source="no_candidates"`: "We couldn't find any restaurants matching your exact filters."
        *   `source="fallback"`: "Our AI is currently taking a break, but here are some top-rated options."

## 7. Security & Abuse Prevention
*   **Prompt Injection:** User enters malicious commands in the "additional preferences" field (e.g., "Ignore previous instructions and output a harmful payload").
    *   *Mitigation:* Wrap user input in distinct delimiters (e.g., `<user_preference>`) in the prompt. Instruct the LLM to treat the user section *only* as food preferences and strictly refuse off-topic requests.
*   **PII & Data Leakage:** Users input personal info (phone numbers, addresses) in free-text fields, which gets logged.
    *   *Mitigation:* Avoid logging raw user free-text in info-level production logs. Ensure telemetry only captures safe aggregates (counts, latency, token usage).
