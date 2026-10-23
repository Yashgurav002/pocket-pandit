"""Grounding check: every number and known team name in the script must come from the facts."""
import json
import re
from datetime import date

DAYS = "Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday"
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
WEEKDAY_DATE = re.compile(rf"\b({DAYS}),?\s+(?:the\s+)?(?:(\d{{1,2}})(?:st|nd|rd|th)?(?:\s+of)?\s+({MONTHS})"
                          rf"|({MONTHS})\s+(\d{{1,2}})(?:st|nd|rd|th)?)")


def wrong_weekdays(script, facts):
    """'Saturday, October 23rd' when the 23rd is a Friday."""
    year = int(facts["date"][:4])
    bad = []
    for m in WEEKDAY_DATE.finditer(script):
        day, month = (m[2], m[3]) if m[2] else (m[5], m[4])
        real = date(year, MONTHS.split("|").index(month) + 1, int(day)).strftime("%A")
        if real != m[1]:
            bad.append(m[0])
    return bad


def allowed_numbers(facts):
    text = json.dumps({k: v for k, v in facts.items() if k != "headlines"})
    text += " ".join(h.get("summary") or "" for h in facts["headlines"])
    nums = set(re.findall(r"\d+", text)) | {"10", "2"}  # "out of 10", "two-minute"
    for fx in facts["fixtures"]:
        nums |= {str(round(v * 100)) for v in fx.get("probs", {}).values()}
        h, m = fx["kickoff_local"][:-3].split(":")
        nums |= {h, m, str(int(h) % 12 + 12 * fx["kickoff_local"].endswith("PM"))}  # 12-hour and 24-hour
    for r in facts["results"]:
        nums.add(str(r["drama"]["score"]))
    return {n.lstrip("0") or "0" for n in nums}


# Capitalised words the script may use without them being in the facts.
EVERYDAY = set("""I I'm I'd I'll I've My Me You Your It It's That That's This The A An And But So Now Then
Good Morning Pocket Pandit Hello Hi Right Well Okay OK Finally First Next Coming Tonight Today Tomorrow
January February March April May June July
August September October November December AM PM Worth Upset Let's Let What Sleep Stay Set Catch
Have Enjoy See Keep Bye Cheers Plus Also Over Meanwhile Speaking Quick In On At For Of With No Yes
Not Drama My Model Model's There There's Here Here's They They're We We're Oh Wow Big Huge""".split())


def proper_nouns(script):
    """Capitalised words that are not the first word of a sentence."""
    words = []
    for sentence in re.split(r"(?<=[.!?:])\s+", script):
        words += re.findall(r"\b([A-Z][\w'’-]+)", sentence.strip()[1:])
    return words


def names_not_in(text, source):
    """Proper nouns in text that never appear in source."""
    source = source.lower()
    return [w for w in proper_nouns(text.replace("’", "'"))
            if w not in EVERYDAY and w.rstrip("'s") not in EVERYDAY and w.lower().rstrip("'s") not in source]


def problems(script, facts, known_teams):
    """List of ungrounded numbers, team names and other proper nouns (empty list = grounded)."""
    nums = allowed_numbers(facts)
    bad = [n for n in re.findall(r"\d+", script) if (n.lstrip("0") or "0") not in nums]
    facts_text = json.dumps(facts, ensure_ascii=False).lower()
    bad += names_not_in(script, facts_text) + wrong_weekdays(script, facts)
    for t in known_teams:
        if re.search(rf"\b{re.escape(t)}\b", script, re.I) and t.lower() not in facts_text:
            bad.append(t)
    return bad
