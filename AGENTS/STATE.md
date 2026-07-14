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
- The crawler side of the storage contract is implemented (crawler commit 9697c9e, production migration pending): the axis set is seeded into `exchange_evaluation_characteristics`, scores go to append-only `exchange_evaluation_scores` tied to review events, latest scores come from the `exchange_latest_evaluation_scores` view; client SQL is in the crawler's `docs/database-contract.md`.
- Repo follows the agent-template harness (AGENTS.md + AGENTS/ + docs/adr).
- humanizer-ru skill is vendored at `.claude/skills/humanizer-ru/` and mandatory for Russian prose (AGENTS.md → Language Rules).
- No code yet; stack not chosen.

## Next

1. Threshold model: which threshold combinations pass a news item (min on selection axes,
   max on service axes; likely «Россия» / «Международное» profiles, hermes-style).
2. Evaluator prompt with scale anchors and calibration examples.
3. Service skeleton: read `exchange_news_for_selection` and the
   `exchange_evaluation_characteristics` reference, score, write the verdict to
   `exchange_review_events` and per-axis scores to `exchange_evaluation_scores`
   in one transaction, idempotency per the crawler contract.

## Open questions

- Stack for the service (language / runtime / LLM client) — not chosen.
- Exact shape of threshold profiles and where they are configured.

## Deferred

- —
