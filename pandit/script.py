"""F1 script: Gemma writes from facts only; grounding check + spoiler guard; template fallback."""
import json
import re

from . import check, llm, spoiler

PROMPT = """You are Pocket Pandit, a warm, witty football expert hosting a 2-minute personal briefing for one fan (local time zone {timezone}; don't name a city).
Write a spoken script of about {words} words using ONLY the facts in the JSON below.
Rules:
- Never invent scores, scorers, injuries, transfers, numbers or quotes.
- For results marked "protected", NEVER mention the score, the winner, or any outcome.
  Only say the drama score out of 10 and whether it's worth the full replay.
- Say today's date exactly as date_spoken. Say kickoff times and days exactly as given.
- Say probabilities as whole percentages and call them "my model's estimate".
- Never name a person unless the facts name them.
- Friendly, warm, a little playful. No lists, no headings: it will be read aloud.
- Output only the words to be spoken: no stage directions, music cues or brackets.
FACTS:
{facts_json}"""

SUMMARY_PROMPT = """Summarise this headline and its short description in one spoken sentence of at most
20 words, in your own words. Do not quote it.
{headline} — {description}"""


def summarise_headlines(facts):
    for h in facts["headlines"]:
        s = llm.ask(SUMMARY_PROMPT.format(headline=h["title"], description=h["description"][:500]))
        h["summary"] = s if s and not check.names_not_in(s, h["title"] + " " + h["description"]) else None


def for_model(facts):
    """What the writer sees: no URLs, raw titles or descriptions (summaries only)."""
    f = {k: v for k, v in facts.items() if k not in ("headlines", "timezone", "date")}
    f["fixtures"] = [{k: v for k, v in fx.items() if k not in ("kickoff_utc", "comp_code")} for fx in facts["fixtures"]]
    f["headlines"] = [{"team": h["team"], "summary": h["summary"], "source": h["source"]}
                      for h in facts["headlines"] if h.get("summary")]
    return f


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def pct(p):
    return f"{round(p * 100)}%"


def template(facts):
    """Deterministic briefing. Always works, never needs a model."""
    out = [f"Good morning, this is Pocket Pandit for {facts['date_spoken']}."]
    for r in facts["results"]:
        if r["protected"]:
            out.append(spoiler.safe_line(r))
        else:
            res = "they drew" if r["winner"] == "draw" else f"{r['winner']} took it"
            out.append(f"In the {r['comp']}, {r['home']} against {r['away']} finished {r['score']}, {res}. "
                       f"Drama rating {r['drama']['score']} out of 10.")
    if not facts["results"]:
        out.append("None of your teams played since the last briefing.")
    for fx in facts["fixtures"]:
        s = f"Coming up: {fx['home']} host {fx['away']} in the {fx['comp']}, {fx['kickoff_day']} at {fx['kickoff_local']} your time."
        if "probs" in fx:
            p = fx["probs"]
            fav, side = max((p["home"], fx["home"]), (p["away"], fx["away"]))
            s += f" My model's estimate: {side} {pct(fav)}, the draw {pct(p['draw'])}."
            if fx.get("upset_alert"):
                s += " Upset alert: my model disagrees with the ratings on this one."
            if fx.get("stay_up"):
                s += f" Worth staying up? My call: {fx['stay_up']}."
        out.append(s)
    for t in facts["tables"]:
        move = ("up " + str(t["change"])) if t["change"] > 0 else ("down " + str(-t["change"])) if t["change"] < 0 else "no change"
        out.append(f"{t['team']} sit {ordinal(t['position'])} in the {t['comp']} table, {move}, on {t['points']} points.")
    for h in facts["headlines"]:
        out.append(h["summary"] if h.get("summary") else f"There's a {h['team']} story from {h['source']}; the link is in the show notes.")
    out.append("That's your lot. Have a lovely day, and I'll see you tomorrow morning.")
    return " ".join(out)


def write(facts, cfg, known_teams):
    """Returns (script, stats) where stats records which path produced it (for the post's numbers)."""
    summarise_headlines(facts)
    prompt = PROMPT.format(timezone=cfg["timezone"], words=int(cfg["briefing"]["max_seconds"] * 2.3),
                           facts_json=json.dumps(for_model(facts), indent=1))
    stats = {"attempts": 0, "grounding_failures": [], "guard_hits": 0, "source": "template"}
    for _ in range(2):  # generate, regenerate once, then template
        text = llm.ask(prompt, temperature=0.7)
        if not text:
            break
        stats["attempts"] += 1
        bad = check.problems(text, facts, known_teams)
        text, hits = spoiler.guard(text, facts)
        stats["guard_hits"] += hits
        if not bad:
            stats["source"] = "gemma"
            return re.sub(r"\([^)]*\)|\*", "", text).strip(), stats
        stats["grounding_failures"].append(bad)
    text, hits = spoiler.guard(template(facts), facts)
    stats["guard_hits"] += hits
    return text, stats
