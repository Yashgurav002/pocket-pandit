# Decisions

- **Own Elo instead of ClubElo.** api.clubelo.com returned 502 on Oct 23 2026. Elo is computed from the same football-data.co.uk results (K=20, home advantage 60). Cross-league strength for Champions League games is only roughly comparable; the facts say so.
- **TabPFN optional at runtime.** Weights need a licence token (`TABPFN_TOKEN`). Without it, predictions come from the Elo logistic baseline and are labelled `"model": "elo"`.
- **`is_european` feature dropped.** It's constant in domestic training data, so it carries no signal.
- **Kickoffs as "12:30 AM".** "00:30" reads badly aloud.
- **Score regex ignores `:`.** `12:30` was flagged as a score next to protected teams.
- **Grounding also checks proper nouns.** Gemma said "Arsène Wenger" when the headline was about Arteta. Capitalised words not in the facts (apart from a small everyday allow-list) now fail the check.
- **Pages from `/docs` on main**, not a gh-pages branch. One branch is simpler; old MP3s are pruned to 14, but git history still grows by about 1 MB a day.
- **No Piper fallback yet.** Kokoro ran fine on CPU.
- **Stdlib XML for RSS**, not feedparser.
