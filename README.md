# Creator Advice Agent — Demo

A simple demo web app: type a creator goal in plain language, get back
**structured, actionable video advice** — not a generic chatbot reply.

> Example input: *"I want to get popular in the gaming niche on YouTube"*
>
> Output: niche identified → trend summary → 3–5 video ideas (each with an
> angle and reasoning) → concrete next steps, rendered as clean cards.

Stateless demo: no database, no accounts, no auth. Trend advice comes from
the LLM's general knowledge for now — see **Phase 2** below.

## Project structure

```
creator-advice-agent/
├── app.py                  # Flask backend: routes, LLM prompt, JSON validation
├── requirements.txt
├── .env.example            # copy to .env and add your key
├── templates/
│   └── index.html          # single input page + results layout
└── static/
    ├── style.css
    └── app.js              # calls /api/advice, renders cards, shows errors
```

## Setup

Requires Python 3.10+.

```bash
cd creator-advice-agent

# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your API key (never hardcode it, never commit .env)
cp .env.example .env
# then edit .env and set LLM_API_KEY=sk-...
```

Any OpenAI-compatible provider works. To use a different one, set
`LLM_BASE_URL` and `LLM_MODEL` in `.env` (see `.env.example`).

### No API key? Demo mode

If no key is set (or `MOCK_LLM=true`), the app still runs and returns
clearly-labelled **sample output**, so you can demo the full flow
(input → structured cards) without a key. Add a key for real AI advice.

## Run it

```bash
python app.py
```

Open http://127.0.0.1:5000, type a goal, and click **Get video ideas**.

Health check: http://127.0.0.1:5000/health

## API

### `POST /api/advice`

Request:

```json
{ "goal": "I want to get popular in the gaming niche on YouTube" }
```

Response (`200`):

```json
{
  "niche_identified": "Gaming",
  "trend_summary": "2–3 sentences on what's likely working in this niche now…",
  "video_ideas": [
    {
      "title": "Suggested video title",
      "angle": "Why this angle/format could work",
      "reasoning": "What signal or pattern this idea is based on"
    }
  ],
  "next_steps": ["Concrete action item", "Another action item"],
  "demo_mode": false
}
```

Errors are friendly JSON, never a stack trace:

| Case | Status | Body |
|---|---|---|
| Empty goal | `400` | `{"error": "Please describe your goal first…"}` |
| Goal over 500 chars | `400` | `{"error": "That goal is a bit long…"}` |
| LLM unreachable / bad key | `502` | `{"error": "We couldn't reach the AI service…"}` |
| LLM returns malformed/incomplete JSON | `502` | `{"error": "The AI returned a response we couldn't read…"}` |

Try it from the terminal:

```bash
curl -s -X POST http://127.0.0.1:5000/api/advice \
  -H "Content-Type: application/json" \
  -d '{"goal": "I want to get popular in the gaming niche on YouTube"}'
```

## How it works

1. The frontend sends the goal to `POST /api/advice`.
2. `app.py` builds a system prompt that requires **JSON only**, in the exact
   schema above (with `response_format: json_object` where supported).
3. The response is parsed defensively in `parse_llm_json()` — code fences
   are stripped and every required field is validated.
4. The frontend renders the JSON as cards, using `textContent` (not
   `innerHTML`) so LLM output can't inject markup.

## Phase 2 (not in this demo)

Real trend data — YouTube Data API / Google Trends — is intentionally
**not** integrated yet. The integration point is marked in `app.py`:

```python
# PHASE 2 — REAL TREND DATA INTEGRATION POINT
def get_trend_context(niche_hint: str):
    return None
```

Implementing that function and passing its result into `build_prompt()`
is the whole Phase 2 change — no other code needs to move.

## Notes for presenting this demo

- Show the raw JSON (curl command above) next to the card UI — that's the
  point of the project: an LLM constrained to a useful structure.
- Try a second niche live (cooking, fitness) to show it's not hardcoded.
- Be upfront: trend summaries are the model's general knowledge, not live
  data. That's exactly what Phase 2 fixes.
