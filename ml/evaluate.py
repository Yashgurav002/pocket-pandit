"""TabPFN vs baselines on a time-ordered split -> evaluation/tabpfn.md.

Train: older seasons (first season skipped: Elo warm-up). Test: the most recent completed season.
"""
import os
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, log_loss

from ml.build_training import FEATURES, OUT
from pandit.config import ROOT
from pandit.predict import CONTEXT_ROWS, LABELS, fit, tabpfn_model


def brier(y, p):
    onehot = np.eye(3)[y]
    return float(np.mean(np.sum((p - onehot) ** 2, axis=1)))


def calibration(y, p, bins=5):
    """Home-win probability: predicted vs actual, per bin."""
    edges = np.linspace(0, 1, bins + 1)
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p[:, 0] >= lo) & (p[:, 0] < hi)
        if m.sum():
            rows.append(f"| {lo:.1f}–{hi:.1f} | {m.sum()} | {p[m, 0].mean():.2f} | {(y[m] == 0).mean():.2f} |")
    return rows


def main():
    df = pd.read_csv(OUT / "matches.csv").dropna(subset=FEATURES + ["result"])
    seasons = sorted(df["season"].unique())
    test_season = seasons[-2]  # last one is in progress
    train = df[(df["season"] > seasons[0]) & (df["season"] < test_season)]
    test = df[df["season"] == test_season]
    y_tr, y = train["result"].map(LABELS.index).values, test["result"].map(LABELS.index).values

    preds, secs = {}, {}
    prior = np.bincount(y_tr, minlength=3) / len(y_tr)
    preds["Always home win (base rates)"] = np.tile(prior, (len(test), 1))
    elo, _, _ = fit(train, use_tabpfn=False)
    preds["Elo only (logistic on elo_diff)"] = elo.predict_proba(test[["elo_diff"]])
    preds["Gradient boosting (defaults)"] = HistGradientBoostingClassifier().fit(
        train[FEATURES], y_tr).predict_proba(test[FEATURES])
    if os.environ.get("TABPFN_TOKEN"):
        t = time.time()
        ctx = train.tail(CONTEXT_ROWS)
        preds[f"**TabPFN** ({CONTEXT_ROWS} context rows, no tuning)"] = tabpfn_model().fit(
            ctx[FEATURES], ctx["result"].map(LABELS.index)).predict_proba(test[FEATURES])
        secs["tabpfn"] = time.time() - t
    odds = test[["odds_h", "odds_d", "odds_a"]].values
    ok = ~np.isnan(odds).any(axis=1)
    book = 1 / odds[ok]
    book /= book.sum(axis=1, keepdims=True)

    lines = [f"# TabPFN vs baselines\n",
             f"Train: seasons {train['season'].min()}–{train['season'].max()} ({len(train)} matches, top 5 leagues). "
             f"Test: season {test_season} ({len(test)} matches). Features known before kickoff only.\n",
             "| Model | Log loss ↓ | Brier ↓ | Accuracy ↑ |", "| --- | --- | --- | --- |"]
    for name, p in preds.items():
        acc = accuracy_score(y, np.zeros_like(y)) if name.startswith("Always") else accuracy_score(y, p.argmax(1))
        lines.append(f"| {name} | {log_loss(y, p, labels=[0, 1, 2]):.4f} | {brier(y, p):.4f} | {acc:.3f} |")
    lines.append(f"| Bookmaker implied (B365, reality check) | {log_loss(y[ok], book, labels=[0, 1, 2]):.4f} | "
                 f"{brier(y[ok], book):.4f} | {accuracy_score(y[ok], book.argmax(1)):.3f} |")
    if "tabpfn" not in secs:
        lines.append("\n_TabPFN not run: set `TABPFN_TOKEN` (free licence at platform.priorlabs.ai)._")
    else:
        lines.append(f"\nTabPFN fit+predict on CPU: {secs['tabpfn']:.0f}s.")
    best = min(preds, key=lambda k: log_loss(y, preds[k], labels=[0, 1, 2]))
    lines += [f"\nCalibration of home-win probability, {best}:\n",
              "| Bin | Matches | Predicted | Actual |", "| --- | --- | --- | --- |", *calibration(y, preds[best])]
    out = ROOT / "evaluation" / "tabpfn.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")  # the table has ↓/↑, which a Windows console can't print


if __name__ == "__main__":
    main()
