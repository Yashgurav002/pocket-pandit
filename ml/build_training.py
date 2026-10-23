"""football-data.co.uk CSVs -> data/training/matches.csv (+ team_state.json for live prediction).

Features are computed walking matches in date order, so each row only sees the past (no leakage).
Elo is our own, from these results. ClubElo was down (502) on Oct 23 2026.
ponytail: one Elo pool for the top five leagues; leagues never meet here, so cross-league strength
(Champions League) is only roughly comparable. Swap in ClubElo ratings when its API is back.
"""
import io
import json
from collections import defaultdict, deque
from datetime import date

import pandas as pd
import requests

from pandit.config import DATA

LEAGUES = {"E0": 0, "SP1": 1, "D1": 2, "I1": 3, "F1": 4}  # PL, La Liga, Bundesliga, Serie A, Ligue 1
FEATURES = ["elo_home", "elo_away", "elo_diff", "home_pts_last5", "away_pts_last5", "home_gd_last5",
            "away_gd_last5", "home_home_pts_last5", "away_away_pts_last5", "rest_days_home",
            "rest_days_away", "league", "season_progress"]
K, HOME_ADV = 20, 60
OUT = DATA / "training"


def seasons(n=10):
    y = date.today().year % 100 - (date.today().month < 8)
    return [f"{s:02d}{s + 1:02d}" for s in range(y - n + 1, y + 1)]


def download(season, div, current):
    path = OUT / "raw" / f"{season}_{div}.csv"
    if not path.exists() or season == current:  # finished seasons never change
        r = requests.get(f"https://www.football-data.co.uk/mmz4281/{season}/{div}.csv", timeout=30)
        r.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(r.content)
    df = pd.read_csv(io.BytesIO(path.read_bytes()), encoding="latin-1", on_bad_lines="skip")
    df.columns = [c.lstrip("﻿ï»¿") for c in df.columns]
    df = df.dropna(subset=["HomeTeam", "AwayTeam", "FTR"])
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, format="mixed")
    df["season"], df["div"] = season, div
    n_teams = df["HomeTeam"].nunique()
    df["season_len"] = n_teams * (n_teams - 1)
    return df[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "B365H", "B365D", "B365A",
               "season", "div", "season_len"]]


class Tracker:
    """Running team state: Elo, last 5 results (all / home / away), last match date."""

    def __init__(self):
        self.elo = defaultdict(lambda: 1500.0)
        self.form = defaultdict(lambda: deque(maxlen=5))       # (pts, gd)
        self.home_form = defaultdict(lambda: deque(maxlen=5))  # pts at home
        self.away_form = defaultdict(lambda: deque(maxlen=5))  # pts away
        self.last = {}

    def features(self, home, away, when, league, progress):
        rest = lambda t: min((when - self.last[t]).days, 30) if t in self.last else 7
        eh, ea = self.elo[home], self.elo[away]
        return {"elo_home": eh, "elo_away": ea, "elo_diff": eh + HOME_ADV - ea,
                "home_pts_last5": sum(p for p, _ in self.form[home]),
                "away_pts_last5": sum(p for p, _ in self.form[away]),
                "home_gd_last5": sum(g for _, g in self.form[home]),
                "away_gd_last5": sum(g for _, g in self.form[away]),
                "home_home_pts_last5": sum(self.home_form[home]),
                "away_away_pts_last5": sum(self.away_form[away]),
                "rest_days_home": rest(home), "rest_days_away": rest(away),
                "league": league, "season_progress": progress}

    def update(self, home, away, hg, ag, when):
        exp = 1 / (1 + 10 ** ((self.elo[away] - self.elo[home] - HOME_ADV) / 400))
        res = 1.0 if hg > ag else 0.5 if hg == ag else 0.0
        delta = K * (res - exp)
        self.elo[home] += delta
        self.elo[away] -= delta
        hp, ap = (3, 0) if hg > ag else (1, 1) if hg == ag else (0, 3)
        self.form[home].append((hp, hg - ag))
        self.form[away].append((ap, ag - hg))
        self.home_form[home].append(hp)
        self.away_form[away].append(ap)
        self.last[home] = self.last[away] = when

    def state(self):
        return {t: {"elo": self.elo[t], "form": list(self.form[t]), "home_form": list(self.home_form[t]),
                    "away_form": list(self.away_form[t]), "last": self.last[t].isoformat()}
                for t in self.last}

    @classmethod
    def from_state(cls, state):
        tr = cls()
        for t, s in state.items():
            tr.elo[t] = s["elo"]
            tr.form[t].extend(map(tuple, s["form"]))
            tr.home_form[t].extend(s["home_form"])
            tr.away_form[t].extend(s["away_form"])
            tr.last[t] = pd.Timestamp(s["last"])
        return tr


def build():
    ss = seasons()
    df = pd.concat([download(s, d, ss[-1]) for s in ss for d in LEAGUES]).sort_values("Date")
    df["n_in_season"] = df.groupby(["season", "div"]).cumcount()
    tr, rows = Tracker(), []
    for r in df.itertuples():
        feats = tr.features(r.HomeTeam, r.AwayTeam, r.Date, LEAGUES[r.div], r.n_in_season / r.season_len)
        rows.append({"date": r.Date.date().isoformat(), "season": r.season, "home": r.HomeTeam,
                     "away": r.AwayTeam, **feats, "result": r.FTR,
                     "odds_h": r.B365H, "odds_d": r.B365D, "odds_a": r.B365A})
        tr.update(r.HomeTeam, r.AwayTeam, r.FTHG, r.FTAG, r.Date)
    pd.DataFrame(rows).to_csv(OUT / "matches.csv", index=False)
    (OUT / "team_state.json").write_text(json.dumps(tr.state()), encoding="utf-8")
    print(f"{len(rows)} matches, {len(tr.last)} teams, seasons {ss[0]}..{ss[-1]}")


if __name__ == "__main__":
    build()
