"""F3 delivery: podcast RSS feed in docs/ (GitHub Pages) + optional Telegram voice message."""
import os
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape

import requests

from .config import ROOT

DOCS = ROOT / "docs"
KEEP = 14


def title(day):
    """Spoiler-safe by construction: only the date."""
    d = date.fromisoformat(day)
    return f"{d.strftime('%A')} {d.day} {d.strftime('%b')}: your teams in 2 minutes"


def notes(facts):
    """Show notes: credits and links only, never results."""
    links = "".join(f'<li><a href="{escape(h["url"] or "")}">{escape(h["team"])}: {escape(h["source"])}</a></li>'
                    for h in facts["headlines"])
    model = "TabPFN" if any(fx.get("model") == "tabpfn" for fx in facts["fixtures"]) else "Elo baseline"
    return (f"<p>Your morning football briefing. Sources:</p><ul>{links}</ul>"
            "<p>Data: football-data.org, football-data.co.uk. Voice: Kokoro-82M. Script: Gemma. "
            f"Predictions: {model}, for fun, not betting advice.</p>")


def feed(episodes, cfg):
    base = cfg["feed"]["base_url"].rstrip("/")
    items = "".join(f"""
  <item>
   <title>{escape(e["title"])}</title>
   <description><![CDATA[{e["notes"]}]]></description>
   <enclosure url="{base}/episodes/{e["file"]}" type="audio/mpeg" length="{e["bytes"]}"/>
   <guid isPermaLink="false">{e["file"]}</guid>
   <pubDate>{e["pub"]}</pubDate>
   <itunes:duration>{e["seconds"]}</itunes:duration>
  </item>""" for e in episodes)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
 <channel>
  <title>{escape(cfg["feed"]["title"])}</title>
  <link>{base}/</link>
  <description>Your personal football expert, in your pocket. Open models, zero cost.</description>
  <language>en</language>
  <itunes:image href="{base}/cover.png"/>
  <itunes:explicit>false</itunes:explicit>{items}
 </channel>
</rss>
"""


def publish(facts, mp3, seconds, state, cfg):
    ep = {"title": title(facts["date"]), "file": mp3.name, "bytes": mp3.stat().st_size, "seconds": seconds,
          "pub": format_datetime(datetime.now(timezone.utc)), "notes": notes(facts)}
    eps = [ep] + [e for e in state.get("episodes", []) if e["file"] != ep["file"]]
    for old in eps[KEEP:]:
        (DOCS / "episodes" / old["file"]).unlink(missing_ok=True)
    state["episodes"] = eps[:KEEP]
    (DOCS / "feed.xml").write_text(feed(state["episodes"], cfg), encoding="utf-8")
    if cfg["delivery"].get("telegram") and os.environ.get("TELEGRAM_BOT_TOKEN"):
        with open(mp3, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendVoice",
                          data={"chat_id": os.environ["TELEGRAM_CHAT_ID"], "caption": ep["title"]},
                          files={"voice": f}, timeout=60).raise_for_status()
