"""
Creator Advice Agent — demo Flask app
======================================
User types a goal in plain language (e.g. "I want to get popular in the
gaming niche on YouTube") and gets back structured, actionable advice:
niche, trend summary, 3-5 explained video ideas, and next steps.

Stateless demo: no database, no accounts, no auth.
"""

import json
import os
import re

from flask import Flask, jsonify, render_template, request

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional at runtime
    pass

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Config — API key comes from the environment, never hardcode it.
#   LLM_API_KEY   (preferred)  or  OPENAI_API_KEY
#   LLM_MODEL     (optional, default: gpt-4o-mini)
#   LLM_BASE_URL  (optional, for any OpenAI-compatible provider)
#   MOCK_LLM      (optional, "true" forces the built-in demo fallback)
# ---------------------------------------------------------------------------
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")


def get_api_key():
    return os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")


def mock_mode_enabled():
    if os.environ.get("MOCK_LLM", "").lower() == "true":
        return True
    # No key configured -> fall back to mock so the demo still runs in class.
    # Set a real key and this path is not used.
    return not get_api_key()


# ---------------------------------------------------------------------------
# PHASE 2 — REAL TREND DATA INTEGRATION POINT
# ---------------------------------------------------------------------------
# TODO (Phase 2): Plug real trend data in here.
#   * YouTube Data API v3  -> trending / most-popular videos in the niche,
#                             search results, view counts, publish cadence
#   * Google Trends (pytrends) -> rising queries for the niche keyword
# Return that data as a dict, then pass it into build_prompt() so the LLM
# reasons over *live* signals instead of only its general knowledge.
# For this demo it intentionally returns None (LLM knowledge only).
# ---------------------------------------------------------------------------
def get_trend_context(niche_hint: str):
    return None


SYSTEM_PROMPT = """You are a content strategy agent for video creators.
You return ONLY valid JSON — no markdown, no code fences, no commentary.

The JSON must have exactly this shape:
{
  "niche_identified": "string — the niche/topic detected from the user's goal",
  "trend_summary": "string — 2-3 sentences on what is likely working in this niche right now",
  "video_ideas": [
    {
      "title": "string — a suggested, clickable video title",
      "angle": "string — why this angle/format could work",
      "reasoning": "string — what signal or pattern this idea is based on"
    }
  ],
  "next_steps": ["string — a concrete action item"]
}

Rules:
- video_ideas: 3 to 5 items, each meaningfully different (format, angle, or audience).
- next_steps: 2 to 3 items, concrete enough to do this week (not "be consistent").
- Be specific to the niche and platform named by the user. Avoid generic advice.
"""


def build_prompt(goal: str, trend_context=None) -> str:
    prompt = f"Creator goal: {goal}\n\nReturn the structured advice JSON described in the system prompt."
    if trend_context:  # Phase 2: live data will land here when implemented
        prompt += f"\n\nLive trend data to reason over:\n{json.dumps(trend_context, indent=2)}"
    return prompt


def call_llm(goal: str) -> dict:
    """Call an OpenAI-compatible chat API and return the parsed dict."""
    from openai import OpenAI  # imported lazily so mock mode needs no key/client

    client_kwargs = {"api_key": get_api_key()}
    base_url = os.environ.get("LLM_BASE_URL")
    if base_url:
        client_kwargs["base_url"] = base_url

    client = OpenAI(**client_kwargs)
    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.7,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(goal, get_trend_context(goal))},
        ],
    )
    raw = response.choices[0].message.content or ""
    return parse_llm_json(raw)


def parse_llm_json(raw: str) -> dict:
    """Parse LLM output defensively: strip code fences, validate the shape."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE).strip()
    data = json.loads(cleaned)  # raises ValueError on malformed JSON -> handled by caller

    if not isinstance(data, dict):
        raise ValueError("LLM did not return a JSON object")
    for field in ("niche_identified", "trend_summary", "video_ideas", "next_steps"):
        if field not in data:
            raise ValueError(f"LLM response is missing '{field}'")
    if not isinstance(data["video_ideas"], list) or not data["video_ideas"]:
        raise ValueError("'video_ideas' must be a non-empty list")
    for idea in data["video_ideas"]:
        if not all(k in idea for k in ("title", "angle", "reasoning")):
            raise ValueError("Each video idea needs title, angle, and reasoning")
    if not isinstance(data["next_steps"], list) or not data["next_steps"]:
        raise ValueError("'next_steps' must be a non-empty list")
    return data


def mock_advice(goal: str) -> dict:
    """Built-in fallback so the demo runs with no API key (clearly labelled).

    It does simple keyword detection — it is NOT a real LLM call.
    """
    text = goal.lower()
    niche = "Gaming"
    if "cook" in text or "food" in text:
        niche = "Cooking / Food"
    elif "fitness" in text or "gym" in text or "workout" in text:
        niche = "Fitness"
    elif "beauty" in text or "makeup" in text:
        niche = "Beauty"
    elif "tech" in text or "coding" in text or "programming" in text:
        niche = "Tech / Coding"
    elif "travel" in text or "vlog" in text:
        niche = "Travel / Vlogging"
    elif "study" in text or "education" in text:
        niche = "Study / Education"

    return {
        "niche_identified": niche,
        "trend_summary": (
            f"[Demo mode — no API key set, showing sample output] In {niche}, "
            "short, challenge-based and 'I tried X for 30 days' formats tend to travel well, "
            "and viewers respond to clear stakes, fast hooks in the first 10 seconds, and series they can binge."
        ),
        "video_ideas": [
            {
                "title": f"I Tried the Hardest Challenge in {niche} for 7 Days",
                "angle": "A time-boxed challenge with a clear win/lose outcome and daily progress.",
                "reasoning": "Challenge + deadline formats create built-in suspense and strong click-through.",
            },
            {
                "title": f"Beginner Mistakes Everyone Makes in {niche} (And How to Fix Them)",
                "angle": "Search-friendly, evergreen list video aimed at newcomers.",
                "reasoning": "Beginner pain-point titles capture steady search traffic, not just browse traffic.",
            },
            {
                "title": f"$10 vs $1,000: Does Money Actually Help in {niche}?",
                "angle": "Side-by-side comparison with a surprising verdict.",
                "reasoning": "Extreme price comparisons are a proven curiosity-gap format across niches.",
            },
            {
                "title": f"I Copied a Top Creator's {niche} Routine for 30 Days",
                "angle": "Documented experiment referencing a creator the audience already knows.",
                "reasoning": "Borrowed relevance + a transformation arc drives comments and shares.",
            },
        ],
        "next_steps": [
            "Pick the first idea above and write 5 title/thumbnail variants before filming anything.",
            "Film it this week, keeping the hook in the first 10 seconds — don't save the payoff for the end.",
            "Post, then reply to every comment in the first 2 hours to seed engagement.",
        ],
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/advice", methods=["POST"])
def advice():
    payload = request.get_json(silent=True) or {}
    goal = str(payload.get("goal", "")).strip()

    if not goal:
        return jsonify({"error": "Please describe your goal first — e.g. 'I want to grow in the gaming niche on YouTube'."}), 400
    if len(goal) > 500:
        return jsonify({"error": "That goal is a bit long — please keep it under 500 characters."}), 400

    if mock_mode_enabled():
        return jsonify({**mock_advice(goal), "demo_mode": True})

    try:
        result = call_llm(goal)
    except json.JSONDecodeError:
        app.logger.exception("LLM returned malformed JSON")
        return jsonify({"error": "The AI returned a response we couldn't read. Please try again."}), 502
    except ValueError as exc:
        app.logger.exception("LLM response failed validation")
        return jsonify({"error": f"The AI response was incomplete ({exc}). Please try again."}), 502
    except Exception:
        app.logger.exception("LLM call failed")
        return jsonify({"error": "We couldn't reach the AI service right now. Check your API key and connection, then try again."}), 502

    return jsonify({**result, "demo_mode": False})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "mock_mode": mock_mode_enabled(), "model": LLM_MODEL})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
