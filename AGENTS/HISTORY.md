# History

Newest first. Each entry ≤5 lines using the format defined in `AGENTS.md`.

---

## 2026-07-23 · Preparer: selected news to HTML pages
- What: New `preparer.py` (stdlib, reuses evaluator's MCP client) prepares selected news: article re-fetch + illustration/caption extraction (og:image, figure/figcaption, lazy img, robots-aware), fresh Russian retelling (JSON title/body, humanizer-ru + deterministic long-dash→hyphen), self-contained HTML page, evaluator-owned SQLite + media/pages dirs, «Подготовлено» label. Deploy: install.sh + news-preparer.timer (15 min). +12 tests (48 total).
- Why: Step 4 of the pipeline — turn «Отобрано» news into publish-ready pages.
- Files: preparer.py, tests/test_preparer.py, deploy/{install.sh,news-preparer.service,news-preparer.timer,news-evaluator.env.example}, AGENTS/{SPEC,STATE,AGENTS}.md, README.md
- Next: Owner deploys; then publication stage («Опубликовано»).

## 2026-07-23 · Default selection profile implemented
- What: `SelectionProfile` + `DEFAULT_PROFILE` in `evaluator.py`; scoring now writes positive/not_positive; new `--backfill` re-verdicts old `skipped` news from stored scores (no model calls). `write_review` takes a `decision`. +9 unit tests (36 total).
- Why: Owner confirmed the strict rule and said proceed; turns the always-`skipped` v0 into real selection.
- Files: evaluator.py, tests/test_evaluator.py, AGENTS/SPEC.md, AGENTS/STATE.md
- Next: Owner deploys and runs `--backfill` once (dry-run on prod: 6228 processed, 120 selected).

## 2026-07-23 · Selection rule and post-selection pipeline specced
- What: Fixed the `default` selection profile (positivity≥8, heroism/clickbait/promo≤4, one bright axis ≥9 → «Отобрано»), the label lifecycle, the «Подготовлено» preparation stage (illustrations+captions, RU retelling, HTML) in an evaluator-owned DB, and the publication placeholder.
- Why: User request to define selection thresholds and the downstream prepare/publish flow.
- Files: AGENTS/SPEC.md, AGENTS/STATE.md
- Next: Implement the profile in code plus a backfill pass over `skipped` events.
- Fixes-on-the-fly: removed a stray duplicate `news-evaluator` repo I had created before finding this one.

## 2026-07-15 · Permanent mode live
- What: Owner ran `deploy/install.sh`: `newsevaluator` user created, timer active (25 news / 10 min), first batch 25/25 with 0 failures, events recorded as `0.2.0+deepseek-chat`.
- Why: Ships the deferred deploy step; the evaluator now runs unattended.
- Files: AGENTS/STATE.md (snapshot refresh only)
- Next: Threshold model; prompt calibration.

## 2026-07-15 · Permanent deploy prepared, model un-hardcoded (v0.2.0)
- What: `selector_version` now records the model that actually answered; empty `EVALUATOR_MODEL` delegates choice to the router (provider/tier hints); added `deploy/` — oneshot service + 10-min timer + env template + idempotent `install.sh` (creates the dedicated user, auto-fills the router token, registers in update-services).
- Why: Owner asked to make the service permanent with the model swappable without code edits.
- Files: evaluator.py, tests/test_evaluator.py, deploy/*, AGENTS/SPEC.md, AGENTS.md, AGENTS/{ENV,STATE,MEMORY}.md, README.md
- Next: Owner runs `sudo bash deploy/install.sh` (permission policy: agents must not create system users); verify first timer runs.

## 2026-07-14 · Evaluator service v0, first live scores
- What: Built stdlib-only `evaluator.py` (MCP chat via model-router-mcp, tolerant JSON validation with up to 3 attempts, transactional event+scores write) plus 27 unit tests; scored news 10–12 into the prod crawler DB with deepseek-chat.
- Why: First working version of the evaluator; validation guards against models that ignore strict JSON rules.
- Files: evaluator.py, tests/test_evaluator.py, AGENTS/SPEC.md, AGENTS.md, AGENTS/{ENV,STATE,MEMORY}.md, README.md
- Next: Threshold model; prompt calibration; dedicated user + systemd timer for deploy.

## 2026-07-14 · Storage contract landed in the crawler
- What: SPEC/STATE now point to the real storage — axis set in `exchange_evaluation_characteristics`, per-axis 0–10 scores in append-only `exchange_evaluation_scores` tied to review events, latest via `exchange_latest_evaluation_scores` — replacing the draft "scores in event metadata" plan.
- Why: The crawler implemented the evaluation side of the exchange contract (crawler commit 9697c9e); specs must match it.
- Files: AGENTS/SPEC.md, AGENTS/STATE.md
- Next: Threshold model, evaluator prompt, then the service skeleton against the real contract.

## 2026-07-14 · Mandatory humanizer-ru skill
- What: Vendored smixs/humanizer-ru v1.2.0 into `.claude/skills/` (un-ignored in .gitignore) and made it mandatory for all Russian prose; set up `origin` and pushed to github.com/wildcar/positive-news-evaluator.
- Why: User requirement — Russian text produced in this repo must not read as AI-generated.
- Files: .claude/skills/humanizer-ru/{SKILL.md,LICENSE}, AGENTS.md, .gitignore, AGENTS/STATE.md
- Next: Threshold model design (see AGENTS/STATE.md → Next).

## 2026-07-14 · Adopt agent-template harness
- What: Migrated repo to the wildcar/agent-template layout; moved SPEC.md → AGENTS/SPEC.md (content unchanged).
- Why: Standardize the agent workflow across repos, matching positive-news-crawler.
- Files: AGENTS.md, CLAUDE.md, README.md, AGENTS/{SPEC,STATE,HISTORY,MEMORY,ENV}.md, docs/adr/TEMPLATE.md, .gitignore, .gitattributes
- Next: Threshold model design (see AGENTS/STATE.md → Next).

## 2026-07-14 · Characteristic set v1
- What: Fixed the v1 characteristic set — 20 independent axes scored 0–10 — plus scale rules and a draft model response format.
- Why: The axes are the foundation for thresholds, the evaluator prompt, and the service.
- Files: SPEC.md (now AGENTS/SPEC.md)
- Next: Threshold model, evaluator prompt, service skeleton.
