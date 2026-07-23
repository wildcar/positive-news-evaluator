# State

Current snapshot. Overwrite this file each iteration. Aim for ≤50 lines: keep pointers and
the live picture here; push detail into `AGENTS/SPEC.md` (the contract) and `AGENTS/HISTORY.md`
(the log).

## Goal

A service that scores every news item collected by Positive News Crawler on the fixed
v1 characteristic set (20 axes, integer 0–10) and lets configurable per-axis thresholds
decide which items pass on.

## Now

- `evaluator.py` (Python 3.12, stdlib only) scores news on the 20 axes via
  model-router-mcp and, with the `default` selection profile, writes
  `positive`/`not_positive` plus 20 scores per news in one transaction. Model is
  config-driven (`/etc/news-evaluator/news-evaluator.env`); each event records the
  model that answered in `selector_version`. Runs every 10 min under `newsevaluator`.
- LIVE on prod: backfill ran (events `0.2.0+backfill:default`); latest reviews hold
  120 positive and 6108 not_positive by `news-evaluator`. Feed positivity averages ~3,
  so the strict rule passes ~2%. Crawler-side retention of rejected news (>3 days) is
  deployed by the owner.
- NEW `preparer.py` (stdlib, reuses evaluator's MCP client): takes selected, not-yet-
  prepared news; re-fetches the article for illustrations+captions (og:image, figure/
  figcaption, lazy img) respecting robots; asks the model for a fresh lively Russian
  retelling (JSON {title, body[]}, humanizer-ru rules + deterministic long-dash→hyphen);
  builds a self-contained HTML page; stores everything in an evaluator-owned SQLite
  (`/var/lib/news-evaluator/evaluator.sqlite3`) + media/pages dirs; marks «Подготовлено».
  48 unit tests green. Verified by dry-run on prod news 580 (EN→RU) and 469 (RU): good
  retelling, 4 images, no long dashes. NOT yet deployed (needs `install.sh`).

## Next

1. Owner: deploy the preparer (`sudo bash deploy/install.sh`) — copies `preparer.py`,
   creates `/var/lib/news-evaluator`, enables `news-preparer.timer` (every 15 min).
2. Publication stage (label «Опубликовано») — next project step, platforms TBD.
3. Prompt calibration and soft profiles («Россия» / «Международное»).

## Open questions

- Publication platforms, formats, and credentials (deferred to the publication step).
- Long-term model choice; deepseek-chat is only the test model (swap via env file).

## Resolved

- Strict `default` rule is intended: owner confirmed few items is fine (2026-07-23).
- Retelling: generate fresh, do not reuse `news_translations` (owner, 2026-07-23).

## Deferred

- —
