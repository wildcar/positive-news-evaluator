# State

Current snapshot. Overwrite this file each iteration. Aim for ≤50 lines: keep pointers and
the live picture here; push detail into `AGENTS/SPEC.md` (the contract) and `AGENTS/HISTORY.md`
(the log).

## Goal

A service that scores every news item collected by Positive News Crawler on the fixed
v1 characteristic set (20 axes, integer 0–10) and lets configurable per-axis thresholds
decide which items pass on.

## Now

- Service v0 works: `evaluator.py` (Python 3.12, stdlib only) reads the queue, asks a
  model through model-router-mcp (`chat` tool, deepseek/deepseek-chat for tests) and
  writes a `skipped` event plus 20 scores per news in one transaction.
- Live runs: 103 news scored into the prod crawler DB as of 2026-07-15 (selector
  `news-evaluator`, version `0.1.0+deepseek-chat`); the 100-item batch took ~4 min,
  cost $0.07, 0 failures, 0 validation retries. Naive cut positivity>=6 &
  negativity<=3 passes 23 of 103 — feed averages: positivity 2.9, negativity 5.5.
- Reply validation per SPEC («Проверка ответа модели»): fence/prose-tolerant JSON
  extraction, key/type/range checks, up to 3 attempts with error feedback to the model.
  27 unit tests green (`python3 -m unittest discover -s tests`).
- `decision` is always `skipped` until the threshold model exists.
- v0.2.0: the model is not hard-coded — `EVALUATOR_MODEL`/`EVALUATOR_PROVIDER`/
  `EVALUATOR_TIER` come from `/etc/news-evaluator/news-evaluator.env`; empty model
  delegates the choice to the router; each event's `selector_version` records the
  model that actually answered. Verified live (dry run, news 113).
- Permanent deploy is fully prepared in `deploy/` (oneshot service + 10-min timer +
  idempotent `install.sh` that creates the `newsevaluator` user and auto-fills the
  router token) — **waiting for the owner to run** `sudo bash deploy/install.sh`;
  the permission policy blocks agents from creating system users even with chat
  approval. Until then manual batches run under `newscrawler`.

## Next

1. Owner runs `sudo bash deploy/install.sh`; then verify the first timer runs
   (`journalctl -u news-evaluator.service`) and events under `0.2.0+…`.
2. Threshold model: which threshold combinations pass a news item (min on selection
   axes, max on service axes; likely «Россия» / «Международное» profiles, hermes-style).
3. Prompt calibration: reference examples with expected scores, cross-model comparison
   on one sample.

## Open questions

- Threshold profiles: exact shape and where they are configured.
- Long-term model choice; deepseek-chat is only the test model (swap via env file).

## Deferred

- —
