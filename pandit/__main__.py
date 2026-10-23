"""python -m pandit facts | run [--local]"""
import argparse
import json
import os
import time
from datetime import datetime, timezone

from . import config, facts, fetch, predict, publish, script, spoiler, tts
from .config import DATA


def known_teams(raw):
    names = {m[side].get(k) for m in raw["matches"] for side in ("homeTeam", "awayTeam") for k in ("name", "shortName")}
    names |= {r["team"] for t in raw["standings"].values() for r in t}
    return sorted(n for n in names if n)


def build_facts(cfg, state, now):
    raw = fetch.raw(cfg)
    if not os.environ.get("FOOTBALL_DATA_TOKEN"):
        now = datetime.fromisoformat(raw["now"])  # the bundled sample is a frozen morning
    f = facts.build(raw, cfg, state, now)
    predict.add(f, cfg)
    spoiler.filter_headlines(f, cfg["briefing"]["headlines"])
    return raw, f


def main():
    ap = argparse.ArgumentParser(prog="pandit")
    ap.add_argument("command", choices=["facts", "run"])
    ap.add_argument("--local", action="store_true", help="don't publish; play the MP3")
    args = ap.parse_args()

    cfg = config.load()
    state_path = DATA / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    t0 = time.time()
    raw, f = build_facts(cfg, state, datetime.now(timezone.utc))
    out = DATA / "facts" / f"{f['date']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(f, indent=1, ensure_ascii=False), encoding="utf-8")
    if args.command == "facts":
        print(json.dumps(f, indent=1, ensure_ascii=False))
        return

    text, stats = script.write(f, cfg, known_teams(raw))
    out.with_suffix(".txt").write_text(text, encoding="utf-8")
    mp3 = publish.DOCS / "episodes" / f"{f['date']}.mp3"
    mp3.parent.mkdir(parents=True, exist_ok=True)
    seconds = tts.speak(text, mp3)
    stats.update(seconds=seconds, pipeline_seconds=round(time.time() - t0))
    print(text, "\n", stats)
    if args.local:
        os.startfile(mp3) if os.name == "nt" else None
        return
    publish.publish(f, mp3, seconds, state, cfg)
    state.setdefault("runs", []).append({"date": f["date"], **stats})
    state_path.write_text(json.dumps(state, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
