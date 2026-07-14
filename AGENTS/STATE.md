# State

Current snapshot. Overwrite this file each iteration. Aim for ≤50 lines: keep pointers and
the live picture here; push detail into `AGENTS/SPEC.md` (the contract) and `AGENTS/HISTORY.md`
(the log).

## Goal

A service that scores every news item collected by Positive News Crawler on the fixed
v1 characteristic set (20 axes, integer 0–10) and lets configurable per-axis thresholds
decide which items pass on.

## Now

- Characteristic set v1 is fixed in `AGENTS/SPEC.md`: 20 axes, scale rules, draft model response format.
- Repo follows the agent-template harness (AGENTS.md + AGENTS/ + docs/adr).
- humanizer-ru skill is vendored at `.claude/skills/humanizer-ru/` and mandatory for Russian prose (AGENTS.md → Language Rules).
- No code yet; stack not chosen.

## Next

1. Threshold model: which threshold combinations pass a news item (min on selection axes,
   max on service axes; likely «Россия» / «Международное» profiles, hermes-style).
2. Evaluator prompt with scale anchors and calibration examples.
3. Service skeleton: read `exchange_news_for_selection`, score, write verdict to
   `exchange_review_events` (scores in event metadata), idempotency per the crawler contract.

## Open questions

- Stack for the service (language / runtime / LLM client) — not chosen.
- Exact shape of threshold profiles and where they are configured.

## Deferred

- —
