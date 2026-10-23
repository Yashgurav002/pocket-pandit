"""Raw data: football-data.org (matches, standings) and RSS headlines.

Without FOOTBALL_DATA_TOKEN the bundled sample in data/sample/raw.json is used,
so the whole pipeline runs offline.
"""
import json
import os
import time
import xml.etree.ElementTree as ET
from datetime import date, timedelta

import requests

from .config import DATA

API = "https://api.football-data.org/v4"


def _get(path, params=None):
    headers = {"X-Auth-Token": os.environ["FOOTBALL_DATA_TOKEN"]}
    for _ in range(3):
        r = requests.get(API + path, params=params, headers=headers, timeout=30)
        if r.status_code == 429:  # free plan: 10 calls/minute
            time.sleep(int(r.headers.get("X-RequestCounter-Reset", 60)) + 1)
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()


def matches(competitions, today):
    data = _get("/matches", {
        "competitions": ",".join(competitions),
        "dateFrom": (today - timedelta(days=2)).isoformat(),
        "dateTo": (today + timedelta(days=2)).isoformat(),
    })
    return data["matches"]


def standings(code):
    data = _get(f"/competitions/{code}/standings")
    total = next(s for s in data["standings"] if s["type"] == "TOTAL")
    return [{"position": r["position"], "team": r["team"]["name"], "points": r["points"]}
            for r in total["table"]]


def headlines(urls):
    items = []
    for url in urls:
        try:
            root = ET.fromstring(requests.get(url, timeout=20).content)
        except (requests.RequestException, ET.ParseError):
            continue  # one dead feed shouldn't kill the briefing
        source = root.findtext("channel/title", url)
        for it in root.iter("item"):
            items.append({"title": (it.findtext("title") or "").strip(),
                          "description": (it.findtext("description") or "").strip(),
                          "url": it.findtext("link"), "source": source})
    return items


def raw(cfg, today=None):
    """Everything fetched for one day, cached to data/raw/<date>.json."""
    today = today or date.today()
    if not os.environ.get("FOOTBALL_DATA_TOKEN"):
        return json.loads((DATA / "sample" / "raw.json").read_text(encoding="utf-8"))
    ms = matches(cfg["competitions"], today)
    comps = sorted({m["competition"]["code"] for m in ms} & set(cfg["competitions"]) - {"CL"})
    out = {"date": today.isoformat(), "matches": ms,
           "standings": {c: standings(c) for c in comps},
           "headlines": headlines(cfg.get("rss_feeds", []))}
    path = DATA / "raw" / f"{today}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out
