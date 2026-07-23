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
- Selection profile `default` is implemented in `evaluator.py` (SPEC «Пороговая
  модель»): scoring now writes `positive`/`not_positive`, and `--backfill`
  re-verdicts already-scored news from stored scores with no model calls. 36 unit
  tests green. Backfill dry-run on prod: 6228 processed, 120 selected (~1.9%), 0
  incomplete. Backfill has since run for real on prod (events tagged
  `0.2.0+backfill:default`): latest reviews now hold 120 positive and 6108
  not_positive by `news-evaluator`.
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

1. ✅ Deployed and backfilled on prod (120 positive / 6108 not_positive).
2. ✅ Crawler-side retention for rejected news committed (`positive-news-crawler`,
   `purge_rejected_content`, 3 days); awaits crawler deploy.
3. Preparation stage (label «Подготовлено»): download illustrations with captions,
   Russian retelling (generate fresh), HTML page, in a new evaluator-owned SQLite +
   media dir.
4. Publication stage (label «Опубликовано») — next project step, platforms TBD.
5. Prompt calibration and soft profiles («Россия» / «Международное»).

## Open questions

- Publication platforms, formats, and credentials (deferred to the publication step).
- Long-term model choice; deepseek-chat is only the test model (swap via env file).

## Resolved

- Strict `default` rule is intended: owner confirmed few items is fine (2026-07-23).
- Retelling: generate fresh, do not reuse `news_translations` (owner, 2026-07-23).

## Deferred

- —
