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
- First live run 2026-07-14: news 10–12 scored into the prod crawler DB
  (selector `news-evaluator`, version `0.1.0+deepseek-chat`, cost ~$0.002, 0 failures).
- Reply validation per SPEC («Проверка ответа модели»): fence/prose-tolerant JSON
  extraction, key/type/range checks, up to 3 attempts with error feedback to the model.
  27 unit tests green (`python3 -m unittest discover -s tests`).
- `decision` is always `skipped` until the threshold model exists.
- Runs on the host go under the `newscrawler` user from `/opt/news-evaluator`
  (see `AGENTS/ENV.md`); a dedicated system user is pending the owner's approval.

## Next

1. Threshold model: which threshold combinations pass a news item (min on selection
   axes, max on service axes; likely «Россия» / «Международное» profiles, hermes-style).
2. Prompt calibration: reference examples with expected scores, cross-model comparison
   on one sample.
3. Deploy hardening: dedicated system user in the `newscrawler` group, systemd timer,
   unit registered in `/etc/newscrawler/update-services`.

## Open questions

- Dedicated system user for the evaluator — needs the server owner (agent may not
  create principals; see `AGENTS/MEMORY.md`).
- Threshold profiles: exact shape and where they are configured.
- Long-term model choice; deepseek-chat is only the test model.

## Deferred

- —
