# Pocket Pandit — PRD & Build Spec

> **Your personal football expert, in your pocket. Two minutes a morning, zero effort.**
> Pocket Pandit is a free, open-source, self-hosted morning audio briefing for the teams and competitions you follow. It writes the script with Gemma, predicts tonight's matches with TabPFN, speaks it with an open-source voice model, and drops it into your podcast app or Telegram every morning. It can also keep results secret for matches you plan to watch later, and tell you whether a replay is worth your 90 minutes.

**Challenge:** Hacktoberfest Open-Source AI Challenge, Week 3 — "Slow and Steady": build something with open-weight models or open-source AI that rewards laziness.
**Deadline:** Sunday Oct 25, 11:59 PM PDT = **Monday Oct 26, ~12:29 PM IST**. Today is Friday Oct 23: about 2.5 days. Aim to publish by Monday 10 AM IST.
**Builder:** a football fan in Vasai (IST timezone) following European football, mainly the Champions League and top leagues.

**Ground rules**
1. **Everything open source and free.** Open-weight models only, run locally or on free compute. No paid APIs, no credits from your own pocket. Hacktoberfest promos are optional extras.
2. **Facts come from data, not from the model.** The model only phrases facts it was given.
3. **No copying news articles.** Summarise in our own words, credit the source, link it in the show notes.
4. **[verify]** marks anything written from training knowledge or a quick search, not confirmed in official docs.

---

## 0. Research: does this already exist?

Short web check done on Oct 23, 2026 (not exhaustive).

| Product | What it is | Gap Pocket Pandit fills |
| --- | --- | --- |
| **Scoutcast.ai** | AI-personalised ~2-minute daily sports audio briefings, follow-up questions, covers Premier League, Champions League, La Liga, Bundesliga, Serie A, Ligue 1 and US sports. **$4.99/month** or $39.99/year after a 7-day trial. Closed app, closed AI, US-fantasy focus | Free, open source, self-hosted; open models; no app needed; spoiler-safe mode; "worth watching?" verdict; IST-aware "worth staying up?" for late kickoffs |
| The Athletic "Daily Football Briefing" | Human-made 10-minute daily podcast | Not personalised to your teams; not spoiler-safe |
| BBC "Football Daily" and similar podcasts | General football news podcasts | Same: everyone gets the same episode |
| Open-source podcast generators (e.g. Podcastfy; self-hosted daily-briefing projects on GitHub) | Turn any text into audio; some daily-briefing projects use closed models (Claude/Polly/Google voices) | Not football-specific; no structured match data, predictions or spoiler safety; often closed models |

**Takeaway:** personalised AI sports briefings exist, but as a paid, closed product. The novelty here is: **fully open and free to run forever**, **spoiler-safe**, **"is the replay worth watching?" without telling you the score**, and **built for fans in Asian timezones** where Champions League matches start at 12:30 AM. Say this honestly in the post; judges respect knowing the landscape.

---

## 1. Summary

**Name:** Pocket Pandit · **Domain:** `pocketpandit.tech` or similar via the free .tech promo [verify availability; turn off auto-renew, it renews at $29.99/year]

**Why the name:** a *pandit* is an expert in Hindi, and the word is close to *pundit*, the TV football expert. Pocket Pandit is your own football expert that fits in your pocket and does the catching-up for you. The Indian twist also says who it's built for first: fans in Asian timezones.

**One-line pitch:** Set it up once and never check a football app again: every morning, a two-minute personal audio briefing on your teams appears in your podcast app, built entirely from open models running for free on GitHub Actions.

**The lazy payoff:**
- No more opening five apps every morning: one two-minute listen while brushing your teeth.
- No more watching a dull 0–0 replay: it tells you, without spoilers, whether a match is worth 90 minutes.
- No more deciding whether to stay up for a 12:30 AM kickoff: it gives a "worth staying up?" call.
- Zero cost, zero maintenance: it runs itself on free GitHub Actions.

**The one wow moment:** the briefing plays: *"Good morning. Real Madrid played last night, and you said you'd watch it later, so no score from me. But it's an 8 out of 10 for drama, with a late twist. Worth the full replay. Tonight, Arsenal host PSV at 12:30 AM your time. My model gives Arsenal a 61% chance, so it's not a must-stay-up. Catch the highlights instead."*

**Why it fits the theme:** it does a daily chore for you (catching up on football), saves real time (skipped replays, skipped late nights), and costs nothing to run, which is exactly the "set it up once and never pay for it again" angle the prompt describes.

---

## 2. Users and problem

**Primary user:** fans who follow a few teams across leagues and the Champions League, especially in Asian timezones where big matches start between 8:30 PM and 1:30 AM local time.

**Problems**
1. Catching up means opening several apps, scrolling past things you don't care about, and often seeing a score you didn't want to see.
2. Late kickoffs force a choice: stay up, or risk spoilers before watching the replay.
3. Full replays take 90+ minutes; most fans don't know which ones are worth it.
4. Paid personalised briefings exist, but cost money and send your listening habits to a closed service.

**First user:** you. Then 3–5 friends from your football group, each with their own teams; ask what they'd keep or drop.

---

## 3. Goals, non-goals, success metrics

**Goals (by Monday morning IST)**
- A daily briefing for your teams, generated end to end with open models, delivered to a podcast feed and Telegram.
- Spoiler-safe mode and the "worth watching?" verdict working on real recent matches.
- TabPFN match predictions with an honest comparison against simple baselines.
- Runs on a schedule in GitHub Actions, free.

**Non-goals:** live scores, betting tips (predictions are framed as "how likely", never as betting advice), video highlights, a mobile app.

**Success metrics (measure on your own week)**
| Metric | How |
| --- | --- |
| Minutes saved per day | Your usual catch-up time (estimate honestly) minus briefing length |
| Replays skipped / watched on its advice | Count; did you agree with the verdict? |
| Spoiler leaks | Must be 0 across all spoiler-safe test cases |
| Briefing length | Target 90–150 seconds |
| Fact accuracy | Every number and name in the script appears in the facts given to the model |
| Prediction quality | Log loss and accuracy vs baselines (Section 9) |
| Cost | ₹0; GitHub Actions minutes used |

---

## 4. Features

| ID | Feature | Priority |
| --- | --- | --- |
| F1 | **Daily briefing:** results, upcoming fixtures in IST, table changes, short news, for followed teams and competitions | Must |
| F2 | **Open voice:** script spoken by an open-source TTS model, published as MP3 | Must |
| F3 | **Delivery:** private podcast RSS feed (GitHub Pages) + Telegram voice message | Must (RSS) / Should (Telegram) |
| F4 | **Spoiler-safe teams:** results, scores, tables and spoiler-y headlines hidden for chosen teams for N hours | Must |
| F5 | **"Worth watching?" verdict:** drama score 1–10 without revealing the result | Must |
| F6 | **Match predictions (TabPFN):** win/draw/loss chances for upcoming matches; "upset alert" | Must |
| F7 | **"Worth staying up?"** for late kickoffs in your timezone | Should |
| F8 | **Setup page:** pick teams, competitions, spoiler-safe teams, wake-up time, language | Should (a YAML config file is enough for MVP) |
| F9 | **Hindi / Hinglish briefing option** | Nice |
| F10 | **Ask a follow-up** in Telegram ("who scored?" when you're ready for spoilers) | Nice |
| F11 | **Spoiler-headline classifier fine-tuned with Tinker** (promo credits) | Nice |

### F1 — Daily briefing structure (~2 minutes)
1. Greeting with date (IST).
2. **Your teams' results** since the last briefing (or spoiler-safe verdicts, F4/F5).
3. **Today and tonight:** fixtures for your teams with kickoff in IST, prediction (F6), and "worth staying up?" (F7).
4. **Table check:** one line per followed league (position changes for your teams); hidden for spoiler-safe teams.
5. **Three headlines** about your teams, summarised in one sentence each (spoiler-filtered).
6. Sign-off.

### F4 — Spoiler-safe mode
- Config: `spoiler_safe: ["Real Madrid"]`, `spoiler_window_hours: 36`.
- For matches involving these teams within the window: no scores, no "won/lost/drew", no scorers, no table positions affected by the match, and no headlines that reveal the result.
- Headlines are filtered twice: a rule filter (scores like `2-1`, words like "beat", "stun", "thrash", "draw", "win") plus a Gemma classifier ("would this headline reveal the result?"). Anything uncertain is dropped.
- Episode titles and show notes are spoiler-safe too.
- Final check: a **spoiler guard** scans the finished script for any score pattern or result word near a protected team name; if found, that section is replaced with the safe verdict template.

### F5 — "Worth watching?" (drama score)
- Inputs: match facts available for free (final score, goal counts from the results feed), plus a free match report or summary from a public RSS feed when available.
- Gemma reads the report and outputs **features only** (JSON): `total_goals_band` (0–1 / 2–3 / 4+), `lead_changes` (0 / 1 / 2+), `late_decisive_goal` (bool), `red_card` (bool), `comeback` (bool), `one_sided` (bool).
- A transparent rule turns features into a score of 1–10 (e.g. +3 comeback, +2 late decisive goal, +2 for 4+ goals, −3 one-sided). The rule is in code and explained in the post.
- Spoken as: *"8 out of 10, with a late twist. Worth the full replay."* Never the score or winner.
- If no report is available, fall back to score-based features only, still never spoken.

### F6 — Predictions
For each upcoming match involving your teams: home win / draw / away win probabilities from TabPFN (Section 9). Spoken as: *"My model makes Arsenal 61% favourites."* Add **"upset alert"** when the model disagrees strongly with the simple Elo favourite. Always framed as likelihood, never betting advice.

### F7 — Worth staying up?
For kickoffs between 11 PM and 5 AM in your timezone: combine predicted closeness (how close the TabPFN probabilities are), match importance (knockout stage, top-of-table clash, derby, a team you follow strongly), and your wake-up time, into "stay up", "set an alarm for the second half" or "sleep and catch the highlights". Simple, transparent rule.

---

## 5. Free data sources

| Data | Source | Cost / limits | Notes |
| --- | --- | --- | --- |
| Fixtures, results, tables (12 competitions incl. Premier League, Champions League, La Liga, Bundesliga, Serie A, Ligue 1) | **football-data.org free plan** | Free forever; **scores and schedules delayed**; 10 calls/minute; no scorers/cards on the free plan | Delayed scores are fine for a morning briefing. Check terms for non-commercial use [verify] |
| Historical results for training (domestic leagues, many seasons, with match stats) | **football-data.co.uk** free CSV files | Free | The TabPFN training "CSV" [verify terms and columns] |
| Club strength across leagues (needed for Champions League) | **ClubElo** (clubelo.com) free API/CSV | Free | Elo ratings for European clubs, comparable across leagues [verify API format] |
| News and match reports | Public **RSS feeds** from major football outlets and club sites | Free | Summarise in our own words, credit and link; never read articles verbatim |
| Kickoff times in IST | Computed from UTC times in the fixtures | — | `Asia/Kolkata` |

Optional partner extras (not required): **SerpApi** free plan for extra news, **Browserbase** if a source needs a real browser. Avoid unofficial or undocumented APIs whose terms you can't confirm.

---
## 6. Open models (everything open-weight, everything free)

| Job | Model | Where it runs | Why |
| --- | --- | --- | --- |
| Writing the script, extracting drama features, spoiler-headline check, headline summaries | **Gemma** (latest available; a ~4B-class model, quantised) via **Ollama** | GitHub Actions runner (CPU) or your laptop | Open weights, free, swappable; your preferences stay in your own repo |
| Voice | **Kokoro-82M** (open-weight TTS, Apache-2.0 [verify]); fallback **Piper** (open source [verify licence]) | Same runner, CPU | Free, open, runs fast on CPU; Hindi voices may be available [verify] |
| Match predictions | **TabPFN-3.5**, open weights, free under the non-commercial licence from platform.priorlabs.ai; run locally | Same runner or laptop | Tabular foundation model: strong predictions from a CSV without tuning |
| Spoiler-headline classifier (optional) | Small open model fine-tuned with **Tinker** (promo credits) | Exported and run via Ollama [verify export path] | Measurable before/after for the Tinker category |

**Quality fallback (still open, still free):** if Gemma on a CPU runner is too slow or weak, call the same Gemma model through the Google AI Studio free tier [verify Gemma availability and limits]. Same weights, hosted for free. Keep it as an environment switch, not the default.

**Why not ElevenLabs?** It's a closed service. The default voice is open (Kokoro). ElevenLabs could be an optional voice for the demo video only; if used, say so, but the product doesn't need it.

---

## 7. Architecture: no server at all

```
GitHub Actions (cron, every morning before your wake-up time)
  │
  ├─ 1. fetch.py     football-data.org (results, fixtures, tables) · ClubElo · RSS feeds
  ├─ 2. facts.py     build today's facts.json for YOUR teams (IST times, table changes)
  ├─ 3. predict.py   TabPFN: probabilities for upcoming matches; upset alert; stay-up call
  ├─ 4. drama.py     Gemma extracts drama features from match reports → 1–10 score (rule)
  ├─ 5. spoiler.py   hide protected results; filter headlines (rules + Gemma check)
  ├─ 6. script.py    Gemma writes a ~2-minute script from facts.json ONLY
  ├─ 7. check.py     grounding check (every name/number in facts) + spoiler guard
  │                  → regenerate once → else deterministic template script
  ├─ 8. tts.py       Kokoro speaks it → MP3 (mono, 64 kbps)
  └─ 9. publish.py   commit MP3 + feed.xml to the gh-pages branch (GitHub Pages)
                     → optional Telegram voice message via the Bot API
                     → keep only the last 14 episodes
Your phone: any podcast app subscribed to https://<you>.github.io/<repo>/feed.xml
            (or your .tech domain pointing at GitHub Pages)
```

- **Cost:** GitHub Actions is free for public repositories [verify current limits]; GitHub Pages is free; all models are open and run on the runner.
- **Privacy:** your teams and listening preferences live in your own repo config. Use a private repo + local run if you don't want them public (Section 12).
- **Cache** the Gemma, Kokoro and TabPFN model files between runs with `actions/cache` so each run doesn't re-download them [verify cache size limits].
- **Local mode:** `python -m pandit run --local` does the same on your laptop and plays the MP3.

### 7.1 Configuration (`config.yaml`)
```yaml
timezone: Asia/Kolkata
wake_up: "07:00"            # the workflow runs ~45 min before this
language: en                # en | hi | hinglish
competitions: [CL, PL, PD, BL1, SA, FL1]   # football-data.org codes [verify codes]
teams:
  - Real Madrid
  - Arsenal
  - Barcelona
spoiler_safe:
  teams: [Real Madrid]
  window_hours: 36
briefing:
  max_seconds: 150
  headlines: 3
delivery:
  rss: true
  telegram: true            # needs TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID secrets
```

### 7.2 Secrets (GitHub repository secrets)
`FOOTBALL_DATA_TOKEN` (free key) · `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (optional) · `PRIORLABS_TOKEN` or Hugging Face token if TabPFN weights need authenticated download [verify] · `SENTRY_DSN` (optional) · `GEMMA_API_KEY` only if using the hosted fallback.

### 7.3 Data files
| File | Contents |
| --- | --- |
| `data/facts/YYYY-MM-DD.json` | Everything the script is allowed to say (Section 8) |
| `data/state.json` | Last run time, episode list, feedback on verdicts |
| `data/training/matches.parquet` | Prepared TabPFN training table (built once by `ml/build_training.py`) |
| `docs/feed.xml`, `docs/episodes/*.mp3` | The podcast feed on GitHub Pages |

---

## 8. The facts file (the only thing the model may use)

```json
{
  "date": "2026-10-24",
  "timezone": "Asia/Kolkata",
  "results": [
    {"id": "m1", "comp": "Champions League", "home": "Real Madrid", "away": "Inter",
     "protected": true, "drama": {"score": 8, "tags": ["late twist", "end-to-end"]}},
    {"id": "m2", "comp": "Premier League", "home": "Arsenal", "away": "Chelsea",
     "protected": false, "score": "2-1", "summary_points": ["second-half winner"]}
  ],
  "fixtures": [
    {"id": "f1", "comp": "Champions League", "home": "Arsenal", "away": "PSV",
     "kickoff_local": "00:30", "kickoff_day": "Wednesday night",
     "probs": {"home": 0.61, "draw": 0.22, "away": 0.17},
     "upset_alert": false, "stay_up": "highlights"}
  ],
  "tables": [{"comp": "Premier League", "team": "Arsenal", "position": 2, "change": 1}],
  "headlines": [{"team": "Barcelona", "summary": "...", "source": "...", "url": "..."}]
}
```
Protected results never contain the score in the facts file at all, so the model can't leak what it never sees.

---

## 9. TabPFN: match prediction from a CSV

**Task:** predict home win / draw / away win before kickoff.

**Training data:** football-data.co.uk CSVs for the top five domestic leagues, ~8–10 seasons [verify columns], joined with ClubElo ratings on the match date.

**Features (all known before kickoff, so no leakage):**
`elo_home`, `elo_away`, `elo_diff`, `home_pts_last5`, `away_pts_last5`, `home_gd_last5`, `away_gd_last5`, `home_home_pts_last5`, `away_away_pts_last5`, `rest_days_home`, `rest_days_away`, `league` (categorical), `season_progress` (0–1), `is_european` (bool).

**Training size:** sample a few thousand recent rows as TabPFN context, so it runs on a CPU in reasonable time [verify TabPFN-3.5 row limits and CPU speed].

**Evaluation (`ml/evaluate.py`, results in `evaluation/tabpfn.md`):** time-ordered split: train on older seasons, test on the most recent completed season.
| Model | Notes |
| --- | --- |
| Always home win | Naive baseline |
| Elo only (logistic regression on `elo_diff`) | Classic football baseline |
| Gradient boosting with defaults | Standard tabular baseline |
| **TabPFN** | No tuning |
| Bookmaker implied probabilities (from the CSV odds columns) | Not a baseline to beat; a "reality check" ceiling, reported honestly |

Metrics: log loss (main), multi-class Brier score, accuracy, and a calibration plot. If TabPFN doesn't beat the Elo baseline, say so and explain; honest numbers read better than inflated ones.

**Inside the agent:** the briefing pipeline calls TabPFN as a tool for each of your upcoming matches, then uses the probabilities for the spoken line, the upset alert (TabPFN favourite differs from the Elo favourite with a 15+ point gap) and the stay-up call. Prior Labs say they favour TabPFN inside a wider prediction agent, and this is one. Optional: connect via the TabPFN MCP server [verify].

**Champions League note:** domestic training data with cross-league Elo lets the model price European matches, but say clearly it's less reliable there.

---

## 10. Prompts (Gemma)

**Script**
```
You are Pocket Pandit, a warm, witty football expert hosting a 2-minute personal briefing for one fan in {timezone}.
Write a spoken script of about {words} words using ONLY the facts in the JSON below.
Rules:
- Never invent scores, scorers, injuries, transfers, numbers or quotes.
- For results marked "protected", NEVER mention the score, the winner, or any outcome.
  Only say the drama score out of 10 and whether it's worth the full replay.
- Say kickoff times in the listener's local time exactly as given.
- Say probabilities as whole percentages and call them "my model's estimate".
- Friendly, warm, a little playful. No lists, no headings: it will be read aloud.
FACTS:
{facts_json}
```

**Drama features (from a match report)**
```
Read this match report. Output ONLY JSON with these keys:
total_goals_band ("0-1","2-3","4+"), lead_changes (0,1,2), late_decisive_goal (true/false),
red_card (true/false), comeback (true/false), one_sided (true/false).
Do not include the score or team names.
REPORT:
{report_text}
```

**Spoiler-headline check**
```
A fan does not want to know the result of {match}. Would reading this headline
reveal or strongly hint at the result? Answer only "yes" or "no".
Headline: "{headline}"
```

**Headline summary**
```
Summarise this headline and its short description in one spoken sentence of at most
20 words, in your own words. Do not quote it.
{headline} — {description}
```

---

## 11. Optional: Tinker fine-tune (spoiler-headline classifier)

**Why:** spoiler detection is subtle ("Ancelotti's gamble pays off" is a spoiler; "Ancelotti faces selection headache" isn't). A small model fine-tuned on labelled headlines should beat a general model, and run faster on a CPU.
- **Data:** ~400–600 real football headlines from RSS, each labelled spoiler / not-spoiler for the match it concerns (label them yourself; ~1.5 hours).
- **Train:** Tinker LoRA on a small supported open model with the promo credits [verify supported models and export].
- **Evaluate:** same held-out set; accuracy, recall on spoilers (most important: a missed spoiler is the bad error), latency on CPU. Compare base small model, Gemma zero-shot, fine-tuned.
- Only do this if Must features are done by Saturday night.

---
## 12. Privacy, content and licences

- **Your data:** only your team list and preferences, in your own repo. No accounts, no tracking, no third-party AI service sees your listening habits.
- **Public vs private:** GitHub Actions is free for public repos; your podcast feed URL on GitHub Pages is public but unlisted. If you want it fully private, run locally (`--local`) and send only to Telegram [verify private-repo Actions free minutes if you prefer that].
- **News content:** summarise in our own words, at most one short sentence per headline, always credit and link the source in show notes. Never read or store full articles beyond what's needed to extract drama features.
- **Data terms:** check football-data.org, football-data.co.uk and ClubElo terms for non-commercial use and attribution [verify]; add attribution in the README and show notes.
- **Model licences:** Gemma terms of use; TabPFN-3.5 non-commercial licence (fine for a free personal tool; a paid product would need a commercial licence); Kokoro/Piper licences [verify]. List them in the README.
- **Not betting advice:** predictions are labelled as estimates for fun.

---

## 13. Repository structure

```
pocket-pandit/
├── pandit/                         Python package
│   ├── __main__.py              CLI: run, run --local, backfill, evaluate
│   ├── config.py                loads config.yaml
│   ├── fetch.py                 football-data.org, ClubElo, RSS (cached, rate-limited)
│   ├── facts.py                 builds facts.json
│   ├── predict.py               TabPFN inference + upset alert + stay-up rule
│   ├── drama.py                 Gemma feature extraction + scoring rule
│   ├── spoiler.py               protection, headline filters, spoiler guard
│   ├── script.py                Gemma script writer + template fallback
│   ├── check.py                 grounding check
│   ├── tts.py                   Kokoro (Piper fallback) → MP3
│   ├── publish.py               feed.xml, gh-pages commit, Telegram sendVoice
│   └── llm.py                   Ollama / OpenAI-compatible client
├── ml/
│   ├── build_training.py        football-data.co.uk CSVs + ClubElo → matches.parquet
│   ├── evaluate.py              TabPFN vs baselines → evaluation/tabpfn.md
│   └── tinker/                  optional spoiler classifier
├── tests/
├── evaluation/
├── docs/                        GitHub Pages: feed.xml, episodes/, index.html
├── config.yaml
├── .github/workflows/briefing.yml
├── .github/workflows/ci.yml
├── requirements.txt
├── DECISIONS.md
└── README.md
```

---

## 14. GitHub Actions workflow (sketch)

```yaml
name: morning-briefing
on:
  schedule:
    - cron: "15 1 * * *"     # 01:15 UTC = 06:45 IST; set from wake_up in config
  workflow_dispatch: {}
permissions:
  contents: write
jobs:
  briefing:
    runs-on: ubuntu-latest
    timeout-minutes: 40
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11", cache: pip }
      - run: pip install -r requirements.txt
      - uses: actions/cache@v4
        with:
          path: |
            ~/.ollama
            ~/.cache/huggingface
            ~/.cache/tabpfn
          key: models-v1
      - name: Install and start Ollama
        run: |
          curl -fsSL https://ollama.com/install.sh | sh
          ollama serve &
          sleep 5
          ollama pull ${{ vars.GEMMA_MODEL }}
      - name: Build briefing
        run: python -m pandit run
        env:
          FOOTBALL_DATA_TOKEN: ${{ secrets.FOOTBALL_DATA_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          SENTRY_DSN: ${{ secrets.SENTRY_DSN }}
      - name: Publish to GitHub Pages
        run: python -m pandit publish
```
[verify: Ollama install on Actions, runner RAM/CPU for the chosen Gemma size, cache limits, GitHub Pages from the `docs/` folder or `gh-pages` branch]

**Feed:** a standard podcast RSS 2.0 feed with `<enclosure url=".../episodes/2026-10-24.mp3" type="audio/mpeg" length="...">`, iTunes tags for title, image and duration, so any podcast app can subscribe. Episode titles are spoiler-safe: *"Saturday 24 Oct: your teams in 2 minutes"*.

---

## 15. Tests and measurements

| Test | Checks |
| --- | --- |
| `test_spoiler_guard` | 50 crafted scripts and headlines with hidden results: zero leaks after the guard |
| `test_protected_facts` | Protected results never include score fields in facts.json |
| `test_grounding` | Every number and team name in a generated script exists in facts.json |
| `test_ist_times` | Kickoff conversion from UTC to IST, including midnight crossings |
| `test_drama_rule` | Feature combinations produce expected scores |
| `test_no_leakage_features` | TabPFN features use only data from before kickoff |
| `test_fallback` | With the model unavailable, a template briefing still publishes |
| `test_feed` | feed.xml validates and lists the newest episode first |

**Publish these numbers (real, measured):**
| Measure | Notes |
| --- | --- |
| TabPFN vs baselines | Log loss, Brier, accuracy, calibration (Section 9) |
| Spoiler leak rate | Before and after the guard; target 0 |
| Grounding failures | How often regeneration or the template was needed |
| Pipeline time and cost | Minutes per run on Actions; ₹0 |
| Briefing length | Seconds |
| Lazy payoff | Your minutes saved per day; replays skipped on its advice and whether you agreed |
| Tinker (optional) | Spoiler recall and accuracy, base vs tuned, CPU latency |

---

## 16. Partner categories (only what you genuinely build)

| Partner | Use | Status |
| --- | --- | --- |
| **Gemma** ($200) | Writes scripts, extracts drama, checks spoilers; runs locally on a free runner | Core |
| **TabPFN** ($200) | Match prediction from a CSV, inside the pipeline as a tool | Core |
| **GitHub Copilot / Actions** ($100) | Actions is the whole runtime ("automate your project with GitHub Actions"); Copilot for building/review | Core |
| **.tech Domain** ($100) | Feed and landing page on your free .tech domain pointed at GitHub Pages | Easy add |
| **Sentry** ($100) | Trace each pipeline step: latency, tokens, failures, a bug you found | Should |
| **Entire** ($100) | Your agent coding sessions in the post | Easy add |
| **Tinker** ($200) | Spoiler classifier fine-tune with promo credits | Nice |
| Render ($200) | Only if you add a hosted setup page (promo credits) | Optional |
| ElevenLabs, Browserbase, SerpApi, Auth0, Ultramarine, others | Not needed; ElevenLabs and Ultramarine are closed | Skip |

---

## 17. Build plan (Fri Oct 23 → Mon Oct 26 morning IST)

Keep it ruthless: the Must features and one great episode beat many half-done extras.

### Friday evening (3–4 h): data and facts
- [ ] Get free keys: football-data.org; sign the TabPFN licence at platform.priorlabs.ai; create a Telegram bot (optional).
- [ ] Check every [verify] item that blocks you today (competition codes, free-plan endpoints, ClubElo format).
> **Prompt:** "Read POCKET_PANDIT_PRD.md. Create the repo in Section 13 with config.yaml from 7.1. Implement fetch.py and facts.py for football-data.org (free plan) and RSS, producing facts.json per Section 8 with IST times and protected results stripped of scores. Add tests test_ist_times and test_protected_facts."

**Done when:** `python -m pandit facts` prints a correct facts.json for your teams.

### Saturday (8–10 h): the AI parts
- [ ] **TabPFN** (morning): `ml/build_training.py` + `ml/evaluate.py` + `predict.py`. Write results to `evaluation/tabpfn.md`.
- [ ] **Gemma** (afternoon): Ollama locally; `drama.py`, `spoiler.py`, `script.py`, `check.py` with the prompts in Section 10 and the guard; tests for spoilers and grounding.
- [ ] **Voice** (evening): `tts.py` with Kokoro; listen to a full episode; tune length and tone.
> **Prompt:** "Implement predict.py, drama.py, spoiler.py, script.py, check.py and tts.py per Sections 4, 9 and 10, with the template fallback and the tests in Section 15."

**Done when:** `python -m pandit run --local` produces a ~2-minute MP3 you'd actually listen to, with zero spoilers for protected teams.

### Sunday (6–8 h): automation and proof
- [ ] `publish.py`: feed.xml + GitHub Pages + Telegram voice message.
- [ ] `.github/workflows/briefing.yml` running on schedule; trigger manually and subscribe in your podcast app.
- [ ] Point your .tech domain at GitHub Pages (optional).
- [ ] Sentry spans around each step (optional).
- [ ] Optional Tinker spoiler classifier only if all above works by Sunday afternoon.
- [ ] Record the demo (Section 18) and take screenshots.

### Monday morning IST: listen and publish
- [ ] Listen to the automatic Monday episode (real proof it runs by itself); note what you'd skip and what it saved you.
- [ ] Publish the DEV post (Section 19) by ~10 AM IST; deadline is ~12:29 PM IST.

**Cut list if behind:** Tinker → Telegram → Sentry → stay-up rule → Hindi → drama from reports (keep score-based drama) → GitHub Actions (run locally and explain). **Never cut:** facts → spoiler guard → script → open voice → TabPFN predictions with baselines.

---

## 18. Demo video (2–3 minutes)

| Time | Show | Say |
| --- | --- | --- |
| 0:00–0:15 | Phone screen: five football apps, a notification spoiling a score | "Every morning I open five apps to catch up on football, and half the time a notification spoils a match I wanted to watch." |
| 0:15–0:30 | Podcast app: a new episode is just there | "So I built Pocket Pandit. I set it up once. Now this appears every morning." |
| 0:30–1:15 | Play the real episode (with subtitles) | Let it play: results, the spoiler-safe Real Madrid verdict, tonight's prediction and stay-up call |
| 1:15–1:35 | GitHub Actions run log, green tick, ₹0 | "It runs itself on free GitHub Actions: Gemma writes it, TabPFN predicts, Kokoro speaks. All open models." |
| 1:35–1:55 | facts.json for a protected match (no score), the spoiler guard catching a planted leak | "The model can't spoil what it never sees, and a guard double-checks." |
| 1:55–2:20 | TabPFN results table vs baselines | Read the real numbers |
| 2:20–2:40 | Your stats: minutes saved, replays skipped | "This week it saved me [X] minutes a day and [Y] dull replays." |
| 2:40–3:00 | config.yaml with your teams | "Fork Pocket Pandit, put in your teams, and never check a football app again." |

---

## 19. DEV post outline (Slow and Steady)

**Title idea:** *"Meet Pocket Pandit: a football expert in my pocket that runs on open models, costs nothing, and never spoils a match"*

1. **What I Built:** the daily chore, the spoilers, the 12:30 AM kickoffs from India; what it does; the lazy payoff in numbers.
2. **Demo:** episode audio, video, feed link / .tech site.
3. **Code:** repo, licence, "fork, edit config.yaml, done".
4. **How I Built It:** the pipeline diagram; facts-only scripting; spoiler protection in three layers (strip scores from facts, filter headlines, guard the script); drama features + transparent rule; TabPFN on a CSV vs baselines; Kokoro voice; GitHub Actions as a free runtime; one bug you hit and fixed.
5. **Why Does Open Innovation Matter?** It costs nothing to run every day forever; a paid closed equivalent exists at $4.99/month; your preferences stay in your repo; you can swap Gemma for any open model or change the voice; it runs offline on a laptop; TabPFN-3.5 runs locally once licensed.
6. **Landscape:** honest note that personalised AI sports briefings exist (closed, paid) and what's different here.
7. **My Agent Session:** DevRelay/Entire embed or link; Copilot use.
8. **Prize Categories:** only what you built (Section 16).

---

## 20. Roadmap (after the hackathon)

- **More sports through data adapters.** Keep `fetch.py` behind a small adapter interface (fixtures, results, standings, drama features). F1 is the natural next sport: free open data (OpenF1, FastF1, Jolpica-F1 [verify]), richer drama signals (overtakes, safety cars, lead changes), and event-driven briefings around race weekends instead of daily.
- **Ask a follow-up** in Telegram when you're ready for spoilers ("who scored?").
- **Hindi and Hinglish voices** if the open voice model supports them well.
- **Group mode** for a friends' WhatsApp/Telegram group following the same teams.
- **Feedback loop:** thumbs up/down on "worth watching?" verdicts tunes the drama rule for you.

---

## 21. Risks

| Risk | Handling |
| --- | --- |
| Gemma too slow or weak on a CPU runner | Smaller Gemma for features/checks, larger for the script; or the free hosted Gemma fallback; or run locally |
| Spoiler leak | Facts never contain protected scores; double headline filter; final guard; tests |
| Free data delayed or missing | Morning briefing tolerates delays; skip missing parts gracefully |
| No match reports available | Score-based drama fallback (never spoken) |
| TabPFN slow on CPU | Smaller context sample; precompute daily for only your teams' matches |
| Actions minutes/cache limits | Keep models small; cache; run locally if needed |
| Copyright of news | One-sentence own-words summaries, credited and linked |
| Not enough time | Cut list in Section 17 |

---

## 22. Verify list (Friday)

- [ ] Hacktoberfest Week 3 rules: new project, deadline in IST, template, DevRelay embed
- [ ] football-data.org free plan: competitions included (CL, PL, PD, BL1, SA, FL1 codes), endpoints, delays, terms
- [ ] football-data.co.uk CSV columns and terms; ClubElo API format and terms
- [ ] Gemma model size that runs in time on a GitHub-hosted runner via Ollama; runner CPU/RAM; cache limits
- [ ] Kokoro-82M licence, CPU speed, Hindi voice support; Piper licence
- [ ] TabPFN-3.5: licence signup, local weight download (auth?), CPU speed and row limits; MCP server
- [ ] GitHub Pages podcast feed works in your podcast app (AntennaPod / Pocket Casts / Apple Podcasts)
- [ ] Telegram Bot API `sendVoice` limits
- [ ] .tech promo availability for your chosen name; auto-renew off
- [ ] Tinker supported models and export path (only if doing the optional classifier)
