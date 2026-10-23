"""Build facts.json (PRD §8): the ONLY thing the script writer may use.

Protected results never carry a score, winner or table line, so nothing downstream can leak them.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from . import drama

RESULTS_HOURS = 30   # results since roughly the last morning briefing
FIXTURES_HOURS = 30  # today and tonight
COMPS = {"CL": "Champions League", "PL": "Premier League", "PD": "La Liga", "BL1": "Bundesliga",
         "SA": "Serie A", "FL1": "Ligue 1"}  # spoken names


def utc(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


CLUB_TOKENS = {"fc", "cf", "afc", "rcd", "sc", "sv", "ac", "as", "ss", "ssc", "us", "ogc", "rc", "cd", "ud",
               "sd", "bv", "vfb", "vfl", "tsg", "1.", "kv"}


def bare(name):
    """'FC Barcelona' -> 'barcelona', 'Real Madrid CF' -> 'real madrid'."""
    return " ".join(w for w in (name or "").lower().split() if w not in CLUB_TOKENS)


def name_for(team, follows):
    """Config name if we follow this team ("Barcelona" for "FC Barcelona"), else shortName.
    Exact match only: "Barcelona" must not pick up "RCD Espanyol de Barcelona"."""
    for f in follows:
        if f.lower() == (team.get("shortName") or "").lower() or f.lower() == bare(team.get("name")):
            return f
    return team.get("shortName") or team["name"]


def kickoff(utc_dt, tz):
    """'12:30 AM' and 'Wednesday night' for a kickoff just after midnight local time."""
    local = utc_dt.astimezone(ZoneInfo(tz))
    day = (local - timedelta(days=1)).strftime("%A") + " night" if local.hour < 5 else local.strftime("%A")
    return local.strftime("%I:%M %p").lstrip("0"), day


def find_report(headlines, home, away):
    for h in headlines:
        text = (h["title"] + " " + h["description"]).lower()
        if home.lower() in text and away.lower() in text:
            return h["title"] + ". " + h["description"]
    return None


def build(raw, cfg, state, now):
    tz, follows = cfg["timezone"], cfg["teams"]
    safe = {t.lower() for t in cfg["spoiler_safe"]["teams"]}
    window = timedelta(hours=cfg["spoiler_safe"]["window_hours"])
    results, fixtures, protected_comps = [], [], set()

    for m in sorted(raw["matches"], key=lambda m: m["utcDate"]):
        home, away = name_for(m["homeTeam"], follows), name_for(m["awayTeam"], follows)
        if home not in follows and away not in follows:
            continue
        when = utc(m["utcDate"])
        base = {"id": str(m["id"]), "comp": COMPS.get(m["competition"]["code"], m["competition"]["name"]), "home": home, "away": away}

        if m["status"] == "FINISHED" and now - when <= timedelta(hours=RESULTS_HOURS):
            protected = bool({home.lower(), away.lower()} & safe) and now - when <= window
            d = drama.rate(m, find_report(raw["headlines"], home, away))
            if protected:
                protected_comps.add(m["competition"]["code"])
                results.append({**base, "protected": True, "drama": d})
            else:
                ft = m["score"]["fullTime"]
                winner = {"HOME_TEAM": home, "AWAY_TEAM": away}.get(m["score"]["winner"], "draw")
                results.append({**base, "protected": False, "score": f"{ft['home']}-{ft['away']}",
                                "winner": winner, "drama": d})

        elif m["status"] in ("SCHEDULED", "TIMED") and timedelta(0) <= when - now <= timedelta(hours=FIXTURES_HOURS):
            local, day = kickoff(when, tz)
            fixtures.append({**base, "comp_code": m["competition"]["code"], "stage": m.get("stage"), "matchday": m.get("matchday"),
                             "kickoff_utc": m["utcDate"], "kickoff_local": local, "kickoff_day": day})

    tables, positions = [], {}
    for code, table in raw["standings"].items():
        for row in table:
            team = name_for({"name": row["team"]}, follows)
            if team not in follows:
                continue
            key = f"{code}:{team}"
            positions[key] = row["position"]
            if code in protected_comps or team.lower() in safe:
                continue  # a hidden result moves this table, so say nothing about it
            prev = state.get("positions", {}).get(key, row["position"])
            tables.append({"comp": COMPS.get(code, code), "team": team, "position": row["position"],
                           "points": row["points"], "change": prev - row["position"]})
    state["positions"] = positions

    headlines = [{**h, "team": t} for h in raw["headlines"]
                 for t in [next((t for t in follows if t.lower() in (h["title"] + h["description"]).lower()), None)]
                 if t]

    today = now.astimezone(ZoneInfo(tz)).date()
    return {"date": today.isoformat(), "date_spoken": f"{today:%A} {today.day} {today:%B}", "timezone": tz,
            "results": results, "fixtures": fixtures, "tables": tables, "headlines": headlines}
