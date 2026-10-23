# TabPFN vs baselines

Train: seasons 1819–2425 (12533 matches, top 5 leagues). Test: season 2526 (1752 matches). Features known before kickoff only.

| Model | Log loss ↓ | Brier ↓ | Accuracy ↑ |
| --- | --- | --- | --- |
| Always home win (base rates) | 1.0720 | 0.6484 | 0.440 |
| Elo only (logistic on elo_diff) | 0.9967 | 0.5944 | 0.505 |
| Gradient boosting (defaults) | 1.0042 | 0.5990 | 0.509 |
| **TabPFN** (3000 context rows, no tuning) | 0.9962 | 0.5935 | 0.514 |
| Bookmaker implied (B365, reality check) | 0.9790 | 0.5827 | 0.533 |

TabPFN fit+predict on CPU: 150s.

Calibration of home-win probability, **TabPFN** (3000 context rows, no tuning):

| Bin | Matches | Predicted | Actual |
| --- | --- | --- | --- |
| 0.0–0.2 | 180 | 0.14 | 0.16 |
| 0.2–0.4 | 614 | 0.31 | 0.33 |
| 0.4–0.6 | 604 | 0.49 | 0.48 |
| 0.6–0.8 | 317 | 0.68 | 0.68 |
| 0.8–1.0 | 37 | 0.82 | 0.84 |
