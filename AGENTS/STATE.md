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
- `publisher.py` posts prepared news, fully automatically by timer, to three platforms,
  each enabled only when its secret is set: Telegram @posinus (`sendPhoto` + HTML caption),
  wildcar.ru (Эгея login → upload → note-process → note-publish → verify), VK community
  wall (photo upload + `wall.post`, needs a USER token of a group admin). Renders each
  format from the stored markdown; idempotent per `(news_id, platform)`; marks
  «Опубликовано» when all enabled platforms succeed. DEPLOYED and live on prod (owner ran
  install.sh and filled secrets).

## Next

1. Owner: **redeploy** for the markdown change (`sudo bash deploy/install.sh`) — new
   `preparer.py`/`publisher.py`. The own DB auto-migrates on first open: it adds
   `retold_body_md` and backfills it from the old HTML, no model calls, no manual step.
2. Watch the first live posts; tune `PUB_BATCH` / cadence if needed.
3. Prompt calibration and soft profiles («Россия» / «Международное»).

## Open questions

- Which VK community + numeric `VK_GROUP_ID` (owner picks; env-driven).
- Long-term model choice; deepseek-chat is only the test model (swap via env file).

## Resolved

- Prepared retelling is stored as markdown, not HTML: no platform consumes HTML, and it
  kills the HTML→paragraph round-trip in the publisher (owner, 2026-07-23).
- Publishing is full-auto (no approval gate); platforms Telegram + wildcar.ru + VK; MAX
  dropped (owner cannot create a MAX bot) (owner, 2026-07-23).
- Strict `default` rule is intended; retelling generated fresh (owner, 2026-07-23).

## Deferred

- —
