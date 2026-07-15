# positive-news-evaluator

AI news evaluator. Reads every news item collected by Positive News Crawler (sibling
repo `positive-news-crawler`, exchange via its `exchange_*` SQLite contract), scores it
on a fixed set of 20 characteristics (integer 0–10 each, independent axes), and
configurable per-axis thresholds decide which items pass on.

Status: service v0 is running. `evaluator.py` (Python 3.12, stdlib only) takes a batch
from the crawler queue, asks a chat model through model-router-mcp, validates the
reply, and writes a review event plus 20 per-axis scores in one transaction. The model
is configured in `/etc/news-evaluator/news-evaluator.env` (never hard-coded; each event
records the model that actually answered). Verdicts stay `skipped` until the threshold
model is designed.

```bash
python3 -m unittest discover -s tests   # unit tests (no network, no DB)
sudo bash deploy/install.sh             # host install: user, config, systemd timer
```

Host run commands live in `AGENTS/ENV.md`.

- Product spec: `AGENTS/SPEC.md` (in Russian)
- Agent workflow & repo map: `AGENTS.md`
