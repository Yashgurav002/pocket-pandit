# Pocket Pandit

Your personal football expert, in your pocket. Every morning you get a two-minute audio briefing on your teams in your podcast app. It's built only from open models and runs free on GitHub Actions.

- **Spoiler-safe:** for teams you're saving to watch later, the score never reaches the model. You get a drama rating out of 10 and a "worth the replay?" verdict.
- **Predictions:** win/draw/loss chances from TabPFN (or an Elo baseline), with an upset alert.
- **Worth staying up?** A call on late kickoffs in your timezone.
- **Facts only:** every number, team and name in the script is checked against the day's facts. If the check fails, it falls back to a template.

## Run it locally

```bash
pip install -r requirements.txt
ollama pull gemma3:4b
python -m ml.build_training          # ~2 min first time: 10 seasons of top-5 league results
python -m pandit facts               # print today's facts.json
python -m pandit run --local         # write the script, speak it, play the MP3
python -m ml.evaluate                # TabPFN vs baselines -> evaluation/tabpfn.md
python -m pytest -q tests
```

With no `FOOTBALL_DATA_TOKEN` set, it uses `data/sample/raw.json`. That file is **fictional** sample data, so it runs offline.

## Make it yours

1. Fork, then edit `config.yaml` (teams, spoiler-safe teams, wake-up time, `feed.base_url`).
2. Add repository secrets: `FOOTBALL_DATA_TOKEN` (free at football-data.org), optionally `TABPFN_TOKEN` (free non-commercial licence at platform.priorlabs.ai), plus `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
3. Settings → Pages → deploy from branch `main`, folder `/docs`.
4. Run the **morning-briefing** workflow once by hand, then subscribe to `<your pages url>/feed.xml`.

## Environment switches

| Var | Default | |
| --- | --- | --- |
| `GEMMA_MODEL` | `gemma3:4b` | any Ollama model |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | any OpenAI-compatible server (e.g. hosted free Gemma) |
| `GEMMA_API_KEY` | – | for a hosted endpoint |
| `PANDIT_VOICE` | `bm_george` | any Kokoro voice |
| `PANDIT_NO_LLM` | – | force the template path |

## Licences and credits

Code: MIT. Models: Gemma (Gemma Terms of Use), TabPFN (non-commercial licence, Prior Labs), Kokoro-82M (Apache-2.0). Data: [football-data.org](https://www.football-data.org), [football-data.co.uk](https://www.football-data.co.uk). News is summarised in one sentence of our own words, with the source credited and linked in the show notes. Predictions are estimates for fun, not betting advice.
