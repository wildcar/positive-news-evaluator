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
- Permanent mode is LIVE since 2026-07-15: the owner ran `deploy/install.sh`,
  `news-evaluator.timer` fires every 10 min under the dedicated `newsevaluator` user
  (25 news per batch, ~3600/day capacity vs ~500/day inflow). First timer batch:
  25/25, 0 failures, sidecar group perms intact. DB now holds 103 events under
  `0.1.0+deepseek-chat` and the permanent stream under `0.2.0+deepseek-chat`.

## Next

1. Implement the `default` selection profile (SPEC «Пороговая модель»): apply it at
   scoring time and add a backfill pass over already-`skipped` news that writes a
   correcting `positive`/`not_positive` event. Rule: positivity≥8, heroism≤4,
   clickbait≤4, promo≤4, and at least one of pride_humanity/pride_russia/inspiration/
   beauty/interestingness/surprise/uniqueness ≥9.
2. Crawler-side change (separate repo): delete rejected news older than 3 days.
3. Preparation stage (label «Подготовлено»): download illustrations with captions,
   Russian retelling, HTML page, in a new evaluator-owned SQLite + media dir.
4. Publication stage (label «Опубликовано») — next project step, platforms TBD.
5. Prompt calibration and soft profiles («Россия» / «Международное»).

## Open questions

- Selection rule is strict: feed positivity averages ~3, so `default` will pass very
  few items. Confirm this is intended vs adding a softer profile alongside it.
- Retelling: generate fresh vs seed from the crawler's existing `news_translations`.
- Publication platforms, formats, and credentials (deferred to the publication step).
- Long-term model choice; deepseek-chat is only the test model (swap via env file).

## Deferred

- —
