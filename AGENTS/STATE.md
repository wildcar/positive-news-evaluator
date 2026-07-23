# State

Current snapshot. Overwrite this file each iteration. Aim for ≤50 lines: keep pointers and
the live picture here; push detail into `AGENTS/SPEC.md` (the contract) and `AGENTS/HISTORY.md`
(the log).

## Goal

A service that scores every news item collected by Positive News Crawler on the fixed
v1 characteristic set (20 axes, integer 0–10), selects the strong ones, prepares them into
a publish-ready retelling, and posts them to the platforms.

## Now

- `evaluator.py` scores news on 20 axes via model-router-mcp and, with the `default`
  profile, writes `positive`/`not_positive` plus scores in one transaction. LIVE on prod
  (every 10 min); backfill done. ~120 positive of ~6200.
- `preparer.py` turns selected news into a **markdown** retelling (H1 title, paragraphs,
  `Источник: [имя](url)`) plus downloaded illustrations, in the evaluator-owned SQLite +
  media dir. Canonical form is `prepared_item.retold_body_md`; no HTML page anymore. LIVE
  on prod (every 15 min).
- `publisher.py` posts prepared news, fully automatically by timer, to Telegram @posinus,
  wildcar.ru (Эгея) and a VK community wall; each platform enables only when its secret is
  set. Renders each format from the stored markdown; idempotent per `(news_id, platform)`.
  Paces NEW posts to at most one per `PUB_MIN_INTERVAL_MINUTES` (default 120); a platform
  that keeps failing is retried up to `PUB_MAX_ATTEMPTS` (8), then given up on so it can't
  block the queue (item finalized «Опубликовано» best-effort). DEPLOYED and live on prod.
  LIVE STATUS: Telegram + wildcar.ru work (news 6775 posted); VK fails — the configured
  token is a COMMUNITY token, a USER token of a group admin is required (error 27).

## Next

1. Owner: **redeploy** (`sudo bash deploy/install.sh`) to pick up the 2h pacing +
   give-up-on-failing-platform fix (and the markdown change). The own DB auto-migrates
   on first open (adds `retold_body_md`, no model calls).
2. Owner: fix VK — get a USER access token of a group admin (scope photos,wall,groups)
   and put it + `VK_GROUP_ID` in the env file; the current token is a community token
   (error 27). Or blank `VK_ACCESS_TOKEN` to disable VK cleanly.
3. Prompt calibration and soft profiles («Россия» / «Международное»).

## Open questions

- Which VK community + numeric `VK_GROUP_ID` (owner picks; env-driven).
- Long-term model choice; deepseek-chat is only the test model (swap via env file).

## Resolved

- Publish at most one NEW news per 2h (`PUB_MIN_INTERVAL_MINUTES=120`); a failing platform
  is given up after `PUB_MAX_ATTEMPTS` so it can't block the queue (owner, 2026-07-23).
- Prepared retelling is stored as markdown, not HTML: no platform consumes HTML, and it
  kills the HTML→paragraph round-trip in the publisher (owner, 2026-07-23).
- Publishing is full-auto (no approval gate); platforms Telegram + wildcar.ru + VK; MAX
  dropped (owner cannot create a MAX bot) (owner, 2026-07-23).
- Strict `default` rule is intended; retelling generated fresh (owner, 2026-07-23).

## Deferred

- —
