"""F6 predictions (TabPFN), upset alert, and F7 "worth staying up?".

TabPFN needs TABPFN_TOKEN (free non-commercial licence at platform.priorlabs.ai). Without it we
fall back to the Elo-only logistic baseline and say so in the facts ("model": "elo").
"""
import difflib
import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from ml.build_training import FEATURES, OUT, Tracker

LABELS = ["H", "D", "A"]
CONTEXT_ROWS = 3000  # ponytail: TabPFN context sample sized for a CPU runner; raise on a GPU
LEAGUE = {"PL": 0, "PD": 1, "BL1": 2, "SA": 3, "FL1": 4}
SEASON_GAMES = {"PL": 38, "PD": 38, "BL1": 34, "SA": 38, "FL1": 34}
ALIASES = {"Barça": "Barcelona", "Atleti": "Ath Madrid", "Athletic": "Ath Bilbao", "PSG": "Paris SG",
           "Man United": "Man United", "Nottingham": "Nott'm Forest", "Leverkusen": "Leverkusen",
           "Bayern": "Bayern Munich", "M'gladbach": "M'gladbach", "Spurs": "Tottenham"}
KNOCKOUT = {"PLAYOFFS", "LAST_16", "QUARTER_FINALS", "SEMI_FINALS", "FINAL"}


def tabpfn_model():
    from tabpfn import TabPFNClassifier
    return TabPFNClassifier(device="cpu", categorical_features_indices=[FEATURES.index("league")])


def fit(train, use_tabpfn=None):
    """Returns (elo_model, main_model, main_name)."""
    y = train["result"].map(LABELS.index)
    elo = LogisticRegression().fit(train[["elo_diff"]], y)
    if use_tabpfn is None:
        use_tabpfn = bool(os.environ.get("TABPFN_TOKEN"))
    if not use_tabpfn:
        return elo, None, "elo"
    ctx = train.tail(CONTEXT_ROWS)
    return elo, tabpfn_model().fit(ctx[FEATURES], ctx["result"].map(LABELS.index)), "tabpfn"


def match_team(name, known):
    name = ALIASES.get(name, name)
    if name in known:
        return name
    sub = [k for k in known if name.lower() in k.lower() or k.lower() in name.lower()]
    return sub[0] if sub else next(iter(difflib.get_close_matches(name, known, n=1, cutoff=0.8)), None)


def stay_up(fx, probs, wake_up, tz, follows):
    """Only for kickoffs 23:00-05:00 local. Transparent points rule."""
    local = datetime.fromisoformat(fx["kickoff_utc"].replace("Z", "+00:00")).astimezone(ZoneInfo(tz))
    if not (local.hour >= 23 or local.hour < 5):
        return None
    p = sorted(probs.values(), reverse=True)
    points = 2 * (1 - (p[0] - p[1]))                          # closeness: 0..2
    points += 2 if fx.get("stage") in KNOCKOUT else 0          # knockout football
    points += 1 if fx["home"] in follows and fx["away"] in follows else 0  # two of your teams
    wake = local.replace(hour=int(wake_up[:2]), minute=int(wake_up[3:]))
    if wake <= local:
        wake += timedelta(days=1)
    if (wake - (local + timedelta(hours=2))).total_seconds() < 4 * 3600:
        points -= 1                                            # under 4 hours of sleep after
    return "stay up" if points >= 3 else "set an alarm for the second half" if points >= 2 else \
        "sleep and catch the highlights"


def add(facts, cfg):
    path = OUT / "matches.csv"
    if not path.exists() or not facts["fixtures"]:
        return facts
    hist = pd.read_csv(path)
    tracker = Tracker.from_state(json.loads((OUT / "team_state.json").read_text(encoding="utf-8")))
    known = list(tracker.last)
    try:
        elo, main, name = fit(hist)
    except Exception as e:  # licence/download problems must not kill the morning briefing
        print(f"[predict] TabPFN unavailable ({e}); using Elo baseline")
        elo, main, name = fit(hist, use_tabpfn=False)

    for fx in facts["fixtures"]:
        home, away = match_team(fx["home"], known), match_team(fx["away"], known)
        if not home or not away:
            print(f"[predict] no history for {fx['home']} or {fx['away']}; skipping")
            continue
        code = fx["comp_code"]
        league = LEAGUE.get(code, int(hist.loc[hist["home"] == home, "league"].iloc[-1]))
        progress = min(fx.get("matchday") or 19, SEASON_GAMES.get(code, 38)) / SEASON_GAMES.get(code, 38)
        when = pd.Timestamp(fx["kickoff_utc"][:10])
        X = pd.DataFrame([tracker.features(home, away, when, league, progress)])[FEATURES]
        p_elo = elo.predict_proba(X[["elo_diff"]])[0]
        p = main.predict_proba(X)[0] if main is not None else p_elo
        fx["probs"] = {"home": round(float(p[0]), 2), "draw": round(float(p[1]), 2), "away": round(float(p[2]), 2)}
        fx["model"] = name
        fav, elo_fav = int(np.argmax(p)), int(np.argmax(p_elo))
        fx["upset_alert"] = fav != elo_fav and abs(p[elo_fav] - p_elo[elo_fav]) >= 0.15
        fx["stay_up"] = stay_up(fx, fx["probs"], cfg["wake_up"], cfg["timezone"], cfg["teams"])
        if code == "CL":
            fx["note"] = "cross-league estimate, less reliable"
    return facts
