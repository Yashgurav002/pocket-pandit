# Pocket Pandit — Tasks

Tracked from `POCKET_PANDIT_PRD.md`. Tick `[x]` when done. IDs match PRD features (F*) where possible.

## Phase 1 — Data & facts (Fri)
- [x] T01 Repo skeleton (§13), `config.yaml` (§7.1), `requirements.txt`
- [x] T02 `config.py` — load YAML
- [x] T03 `fetch.py` — football-data.org matches + standings (cached, rate-limited, token from env)
- [x] T04 `fetch.py` — RSS headlines (stdlib XML)
- [x] T05 `facts.py` — facts.json (§8): IST kickoffs, protected results stripped of scores
- [x] T06 Offline sample data so the pipeline runs without a token
- [x] T07 Tests: `test_ist_times`, `test_protected_facts`

## Phase 2 — AI parts (Sat)
- [x] T08 `llm.py` — Ollama client (OpenAI-compatible switch via env)
- [x] T09 `drama.py` — Gemma feature extraction + transparent 1–10 rule; score-only fallback (F5)
- [x] T10 `spoiler.py` — rule filter + Gemma headline check + final script guard (F4)
- [x] T11 `script.py` — Gemma script from facts only + deterministic template fallback (F1)
- [x] T12 `check.py` — grounding check → regenerate once → template
- [x] T13 `ml/build_training.py` — football-data.co.uk CSVs → features (own Elo; ClubElo was 502 on Oct 23)
- [x] T14 `ml/evaluate.py` — TabPFN vs home/Elo/GBM/bookmaker → `evaluation/tabpfn.md`
- [x] T15 `predict.py` — probabilities, upset alert, stay-up rule (F6, F7)
- [x] T16 `tts.py` — Kokoro → MP3 via ffmpeg (F2)
- [x] T17 Tests: spoiler guard, grounding, drama rule, no-leakage, fallback

## Phase 3 — Automation (Sun)
- [x] T18 `publish.py` — feed.xml (RSS 2.0 + iTunes), keep last 14, Telegram sendVoice (F3)
- [x] T19 `docs/index.html` — landing page on GitHub Pages
- [x] T20 `.github/workflows/briefing.yml` + `ci.yml`
- [x] T21 Test: `test_feed`
- [x] T22 README (licences, attribution), DECISIONS.md

## Phase 4 — Proof (Mon)
- [x] T23 Real keys: football-data.org token, TabPFN licence, Telegram bot (in .env; still to add as GitHub secrets)
- [ ] T24 Listen to an automatic episode; record demo; DEV post

## Optional (cut list order)
- [ ] Tinker spoiler classifier (F11) · Sentry spans · Hindi (F9) · Telegram follow-ups (F10) · .tech domain
