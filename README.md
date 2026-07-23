# positive-news-evaluator

AI news evaluator. Reads every news item collected by Positive News Crawler (sibling
repo `positive-news-crawler`, exchange via its `exchange_*` SQLite contract), scores it
on a fixed set of 20 characteristics (integer 0–10 each, independent axes), and a
selection profile decides which items pass on. Selected news are then turned into
publish-ready HTML pages.

Two stdlib-only scripts (Python 3.12):

- `evaluator.py` — scores a batch, applies the `default` selection profile, and writes
  a review event (positive/not_positive) plus 20 scores per news in one transaction.
  `--backfill` re-verdicts already-scored news from stored scores. The `default`
  profile is strict (few items pass) — see `AGENTS/SPEC.md`, section «Пороговая модель».
- `preparer.py` — for each selected news, extracts illustrations with captions from the
  article, asks the model for a fresh lively Russian retelling, builds a self-contained
  HTML page, and stores it in the evaluator's own SQLite + media/pages dirs.

The model is configured in `/etc/news-evaluator/news-evaluator.env` (never hard-coded;
each event records the model that actually answered).

```bash
python3 -m unittest discover -s tests        # unit tests (no network, no DB)
python3 evaluator.py --backfill --dry-run    # re-verdict old scored news, print only
python3 preparer.py --dry-run --news-id N    # prepare one selected news, print only
sudo bash deploy/install.sh                  # host install: user, config, systemd timers
```

Host run commands live in `AGENTS/ENV.md`.

- Product spec: `AGENTS/SPEC.md` (in Russian)
- Agent workflow & repo map: `AGENTS.md`
