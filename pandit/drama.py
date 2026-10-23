"""F5 "Worth watching?": drama features -> transparent 1-10 score. Never says the result."""
import json
import re

from . import llm

PROMPT = """Read this match report. Output ONLY JSON with these keys:
total_goals_band ("0-1","2-3","4+"), lead_changes (0,1,2), late_decisive_goal (true/false),
red_card (true/false), comeback (true/false), one_sided (true/false).
Do not include the score or team names.
REPORT:
{report}"""

KEYS = {"total_goals_band", "lead_changes", "late_decisive_goal", "red_card", "comeback", "one_sided"}


def from_score(ft, ht):
    """Features we can get from the free results feed alone: full-time and half-time scores."""
    goals = ft["home"] + ft["away"]
    sign = lambda s: (s["home"] > s["away"]) - (s["home"] < s["away"])
    comeback = sign(ht) != 0 and sign(ft) == -sign(ht)
    return {"total_goals_band": "0-1" if goals <= 1 else "2-3" if goals <= 3 else "4+",
            "lead_changes": 1 if comeback else 0, "late_decisive_goal": False,
            "red_card": False, "comeback": comeback,
            "one_sided": abs(ft["home"] - ft["away"]) >= 3}


def from_report(report):
    """Gemma reads a match report and returns features only, or None."""
    out = llm.ask(PROMPT.format(report=report[:4000]))
    m = re.search(r"\{.*\}", out or "", re.S)
    try:
        feats = json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        return None
    return feats if feats and KEYS <= feats.keys() else None


def score(f):
    """The rule, in full. Base 4, then add/subtract, clamp to 1..10."""
    s, tags = 4, []
    if f["comeback"]:
        s += 3; tags.append("a big swing in momentum")
    if f["late_decisive_goal"]:
        s += 2; tags.append("a late twist")
    if f["total_goals_band"] == "4+":
        s += 2; tags.append("end-to-end action")
    elif f["total_goals_band"] == "2-3":
        s += 1
    s += min(int(f["lead_changes"]), 2)
    if f["red_card"]:
        s += 1; tags.append("a red card")
    if f["one_sided"]:
        s -= 3; tags.append("one-sided")
    s = max(1, min(10, s))
    verdict = ("worth the full replay" if s >= 7 else
               "extended highlights will do" if s >= 5 else "skip it, the highlights are plenty")
    return {"score": s, "tags": tags, "verdict": verdict}


def rate(match, report=None):
    ft, ht = match["score"]["fullTime"], match["score"]["halfTime"]
    feats = (report and from_report(report)) or from_score(ft, ht)
    return score(feats)
