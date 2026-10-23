"""F4 spoiler safety: headline filter (rules + Gemma) and the final script guard."""
import re

from . import llm

SCORE = re.compile(r"\b\d{1,2}\s*[-–—]\s*\d{1,2}\b")  # no ":", that's a kickoff time
RESULT_WORDS = re.compile(r"\b(" + "|".join([
    r"beat(s|en)?", r"won", r"wins?", r"winning", r"winner", r"victory", r"victorious",
    r"los(e|es|t|ing)", r"loss", r"defeat(s|ed)?", r"dr(ew|aw|aws)", r"drawn", r"tie[ds]?",
    r"stun(s|ned)?", r"thrash(es|ed)?", r"hammer(s|ed)?", r"crush(es|ed)?", r"rout(s|ed)?",
    r"edge[sd]?", r"sink(s)?", r"sank", r"held", r"hold on", r"comeback", r"come back",
    r"equali[sz](er|es|ed)", r"scor(e|ed|es|er|ers)", r"hat-?trick", r"clean sheet",
    r"pays? off", r"through to", r"knocked out", r"eliminated", r"advance[sd]?", r"top(s|ped)?",
    r"goals?", r"points?", r"unbeaten", r"humiliat\w*", r"heartbreak", r"triumph\w*", r"collapse\w*",
]) + r")\b", re.I)

HEADLINE_PROMPT = """A fan does not want to know the result of {match}. Would reading this headline
reveal or strongly hint at the result? Answer only "yes" or "no".
Headline: "{headline}\""""


def protected_matches(facts):
    return [r for r in facts["results"] if r["protected"]]


def leaks(text, match):
    """Rule check: does this text mention the match's teams together with a score or result word?"""
    names = {match["home"].lower(), match["away"].lower()}
    low = text.lower()
    return any(n in low for n in names) and bool(SCORE.search(text) or RESULT_WORDS.search(text))


def filter_headlines(facts, limit):
    """Drop anything that could spoil a protected match. Uncertain (no model) = drop."""
    hidden = protected_matches(facts)
    kept = []
    for h in facts["headlines"]:
        text = h["title"] + " " + h["description"]
        risky = [m for m in hidden if any(n.lower() in text.lower() for n in (m["home"], m["away"]))]
        if any(leaks(text, m) for m in risky):
            continue
        if any((llm.ask(HEADLINE_PROMPT.format(match=f"{m['home']} vs {m['away']}", headline=h["title"]))
                or "yes").strip().lower().startswith("y") for m in risky):
            continue
        kept.append(h)
        if len(kept) == limit:
            break
    facts["headlines"] = kept
    return facts


def safe_line(m):
    d = m["drama"]
    twist = f", with {d['tags'][0]}" if d["tags"] and d["tags"][0] != "one-sided" else ""
    return (f"{m['home']} against {m['away']}: you're watching that one later, so no result from me. "
            f"It's a {d['score']} out of 10 for drama{twist}. My call: {d['verdict']}.")


def guard(script, facts):
    """Final check on the finished script. Any sentence (or the one after it) that pairs a protected
    team with a score or result word is replaced by the safe verdict, once per match.
    ponytail: sentence-level heuristic; pronoun leaks two sentences later slip through, the
    facts file never holding the score is the real protection."""
    hidden = protected_matches(facts)
    if not hidden:
        return script, 0
    sentences = re.split(r"(?<=[.!?])\s+", script.strip())
    out, hits, carry = [], 0, None
    said = {m["id"] for m in hidden if safe_line(m) in script}
    for s in sentences:
        bad = next((m for m in hidden if leaks(s, m)), None)
        if not bad and carry and (SCORE.search(s) or RESULT_WORDS.search(s)):
            bad = carry  # "Real Madrid played Inter. They won 2-1." style follow-ups
        carry = next((m for m in hidden if any(n.lower() in s.lower() for n in (m["home"], m["away"]))), None)
        if bad:
            hits += 1
            if bad["id"] not in said:
                out.append(safe_line(bad))
                said.add(bad["id"])
            continue
        out.append(s)
    return " ".join(out), hits
