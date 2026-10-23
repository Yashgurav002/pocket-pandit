"""PRD §15 checks. Offline: no model, no API key."""
import copy
import itertools
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import pandas as pd

from ml.build_training import Tracker
from pandit import check, config, drama, facts, fetch, publish, script, spoiler
from pandit.__main__ import known_teams

# After the imports: config.py loads .env, and tests must stay offline whatever is in it.
os.environ["PANDIT_NO_LLM"] = "1"
for key in ("FOOTBALL_DATA_TOKEN", "TABPFN_TOKEN", "TELEGRAM_BOT_TOKEN"):
    os.environ.pop(key, None)

CFG = config.load()


def sample_facts():
    raw = fetch.raw(CFG)
    f = facts.build(raw, CFG, {}, datetime.fromisoformat(raw["now"]))
    return raw, f


def test_ist_times():
    k = lambda s: facts.kickoff(datetime.fromisoformat(s), "Asia/Kolkata")
    assert k("2026-10-21T19:00:00+00:00") == ("12:30 AM", "Wednesday night")  # crosses midnight
    assert k("2026-10-21T18:29:00+00:00") == ("11:59 PM", "Wednesday")
    assert k("2026-10-21T14:00:00+00:00") == ("7:30 PM", "Wednesday")
    assert k("2026-10-21T23:30:00+00:00") == ("5:00 AM", "Thursday")
    assert k("2026-12-31T19:00:00+00:00") == ("12:30 AM", "Thursday night")  # year boundary


def test_protected_facts():
    _, f = sample_facts()
    prot = [r for r in f["results"] if r["protected"]]
    assert prot and all("score" not in r and "winner" not in r for r in prot)
    assert "3-2" not in json.dumps(f)  # the hidden Real Madrid score
    assert all(r["drama"]["score"] for r in prot)
    assert not any(t["team"] == "Real Madrid" for t in f["tables"])
    assert not any("stun" in h["title"] or "match report" in h["title"] for h in
                   spoiler.filter_headlines(copy.deepcopy(f), 3)["headlines"])


LEAKS = ["Real Madrid beat Inter 3-2 last night.", "Real Madrid won it late.", "Inter were stunned by Real Madrid.",
         "Real Madrid drew with Inter.", "It finished 3-2 to Real Madrid.", "Real Madrid lost to Inter.",
         "Real Madrid came from behind and scored twice.", "Inter's defeat at Real Madrid hurts.",
         "Real Madrid sealed a famous victory over Inter.", "A Real Madrid comeback against Inter!"]
FOLLOW = ["Real Madrid played Inter last night. They won 3-2.", "What a night for Real Madrid. Two goals late on."]


def test_spoiler_guard():
    _, f = sample_facts()
    m = next(r for r in f["results"] if r["protected"])
    pre = ["Good morning.", "Arsenal play tonight at 12:30 AM.", "Barcelona are top of La Liga."]
    post = ["", "Have a lovely day.", "Sleep well."]
    cases = [" ".join(filter(None, [a, b, c])) for a, b, c in itertools.product(pre, LEAKS + FOLLOW, post)]
    assert len(cases) >= 50
    for text in cases:
        out, hits = spoiler.guard(text, f)
        assert hits >= 1, text
        assert "3-2" not in out and spoiler.safe_line(m) in out
        body = out.replace(spoiler.safe_line(m), "")
        assert not any(spoiler.leaks(s, m) for s in body.split(". ")), out
    clean = "Good morning. Arsenal play tonight. Have a lovely day."
    assert spoiler.guard(clean, f) == (clean, 0)


def test_safe_line_has_no_result_words():
    for feats in itertools.product(["0-1", "2-3", "4+"], [0, 1, 2], *[[True, False]] * 4):
        d = drama.score(dict(zip(["total_goals_band", "lead_changes", "late_decisive_goal", "red_card",
                                  "comeback", "one_sided"], feats)))
        assert not spoiler.RESULT_WORDS.search(" ".join(d["tags"]) + " " + d["verdict"]), d


def test_grounding():
    raw, f = sample_facts()
    teams = known_teams(raw)
    assert check.problems(script.template(f), f, teams) == []
    assert "Liverpool" in check.problems("Arsenal face Liverpool tonight.", f, teams)
    assert "Wenger" in check.problems("Good morning. Arsène Wenger says Arsenal are ready.", f, teams)
    assert check.problems("Good morning. I’d stay up for Arsenal.", f, teams) == []
    assert "87" in check.problems("Good morning. My model gives Arsenal 87 percent.", f, teams)


def test_drama_rule():
    base = dict(total_goals_band="2-3", lead_changes=0, late_decisive_goal=False, red_card=False,
                comeback=False, one_sided=False)
    assert drama.score(base)["score"] == 5
    assert drama.score({**base, "comeback": True, "late_decisive_goal": True, "lead_changes": 2})["score"] == 10
    assert drama.score({**base, "total_goals_band": "0-1", "one_sided": True})["score"] == 1
    assert drama.score({**base, "comeback": True})["verdict"] == "worth the full replay"
    ft, ht = {"home": 3, "away": 2}, {"home": 0, "away": 1}
    assert drama.from_score(ft, ht)["comeback"] and drama.from_score(ft, ht)["total_goals_band"] == "4+"


def test_no_leakage_features():
    tr = Tracker()
    d = lambda s: pd.Timestamp(s)
    first = tr.features("A", "B", d("2025-08-10"), 0, 0.0)
    assert first["elo_diff"] == 60 and first["home_pts_last5"] == 0  # knows nothing before the first match
    tr.update("A", "B", 5, 0, d("2025-08-10"))
    after = tr.features("A", "B", d("2025-08-17"), 0, 0.1)
    assert after["home_pts_last5"] == 3 and after["elo_home"] > 1500 and after["rest_days_home"] == 7
    assert first["home_pts_last5"] == 0  # earlier row unchanged by the later result


def test_fallback():
    raw, f = sample_facts()
    text, stats = script.write(f, CFG, known_teams(raw))
    assert stats["source"] == "template" and "Good morning" in text and "3-2" not in text
    assert stats["guard_hits"] == 0 and text.count("no result from me") == 1


def test_feed():
    _, f = sample_facts()
    eps = [{"title": publish.title(f"2026-10-{d:02d}"), "file": f"2026-10-{d:02d}.mp3", "bytes": 1, "seconds": 120,
            "pub": "Wed, 21 Oct 2026 01:15:00 +0000", "notes": publish.notes(f)} for d in range(20, 0, -1)]
    root = ET.fromstring(publish.feed(eps[:publish.KEEP], CFG))
    items = root.findall("channel/item")
    assert len(items) == 14 and items[0].findtext("guid") == "2026-10-20.mp3"
    assert items[0].find("enclosure").get("type") == "audio/mpeg"
    assert "3-2" not in publish.notes(f) and publish.title("2026-10-24") == "Saturday 24 Oct: your teams in 2 minutes"


def test_summary_with_invented_name_is_dropped(monkeypatch):
    f = spoiler.filter_headlines(sample_facts()[1], 3)
    replies = iter(["Ars\u00e8ne Wenger says Arsenal are ready.", "Barcelona are adding more seats at Camp Nou."])
    monkeypatch.setattr(script.llm, "ask", lambda *a, **k: next(replies))
    script.summarise_headlines(f)
    assert [h["summary"] for h in f["headlines"]] == [None, "Barcelona are adding more seats at Camp Nou."]


def test_team_matching_is_exact():
    follows = ["Real Madrid", "Arsenal", "Barcelona"]
    n = lambda name, short: facts.name_for({"name": name, "shortName": short}, follows)
    assert n("FC Barcelona", "Barça") == "Barcelona"
    assert n("Real Madrid CF", "Real Madrid") == "Real Madrid"
    assert n("Arsenal FC", "Arsenal") == "Arsenal"
    assert n("RCD Espanyol de Barcelona", "Espanyol") == "Espanyol"
    assert facts.name_for({"name": "FC Barcelona"}, follows) == "Barcelona"  # standings rows have no shortName


def test_wrong_weekday_is_caught():
    raw, f = sample_facts()  # sample date: Wednesday 21 October 2026
    teams = known_teams(raw)
    assert check.problems("Good morning, it's Wednesday, October 21st.", f, teams) == []
    assert check.problems("Good morning, it's Wednesday 21 October.", f, teams) == []
    assert "Saturday, October 21" in " ".join(check.problems("Good morning. It's Saturday, October 21st.", f, teams))
    assert "Sunday" in check.problems("Good morning. See you Sunday.", f, teams)  # weekday not in facts
