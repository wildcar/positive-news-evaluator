# State

Current snapshot. Overwrite this file each iteration. Aim for ≤50 lines: keep pointers and
the live picture here; push detail into `AGENTS/SPEC.md` (the contract) and `AGENTS/HISTORY.md`
(the log).

## Goal

A service that scores every news item collected by Positive News Crawler on the fixed
v1 characteristic set (20 axes, integer 0–10), selects the strong ones, prepares them into
publish-ready pages, and posts them to the platforms.

## Now

- `evaluator.py` scores news on 20 axes via model-router-mcp and, with the `default`
  profile, writes `positive`/`not_positive` plus scores in one transaction. LIVE on prod
  (every 10 min); backfill done. ~120 positive of ~6200.
- `preparer.py` turns selected news into a self-contained HTML page: illustrations +
  captions, fresh Russian retelling, evaluator-owned SQLite + media/pages. LIVE on prod
  (every 15 min); first batches produced good pages.
- NEW `publisher.py` (stdlib, ported from the proven hermes flows): posts prepared news,
  fully automatically by timer, to three platforms, each enabled only when its secret is
  set in the env file:
  - Telegram @posinus — `sendPhoto` + HTML caption (bot `buyvbot`, chat `-1003795927410`).
  - Site wildcar.ru (Эгея) — login, image upload, `note-process`, `note-publish`, verify.
  - VK community wall — photo upload + `wall.post` (needs a USER token, group admin).
  Idempotent per `(news_id, platform)`; marks «Опубликовано» when all enabled platforms
  succeed. 67 unit tests green. Transport verified live without posting: Telegram `getMe`
  ok, Эгея login + CSRF scrape ok. NOT yet deployed (needs `install.sh` + secrets).

## Next

1. Owner: deploy the publisher (`sudo bash deploy/install.sh`) — copies `publisher.py`,
   installs `news-publisher.timer` (every 30 min, `PUB_BATCH=1`).
2. Owner: fill platform secrets in `/etc/news-evaluator/news-evaluator.env`
   (`TELEGRAM_BOT_TOKEN`, `EGEYA_PASSWORD`, and — once obtained — a VK user token +
   `VK_GROUP_ID`). Nothing posts until at least one is set.
3. Prompt calibration and soft profiles («Россия» / «Международное»).

## Open questions

- Which VK community to post to, and its numeric `VK_GROUP_ID` (owner picks; env-driven).
- Long-term model choice; deepseek-chat is only the test model (swap via env file).

## Resolved

- Publishing is full-auto (no approval gate), owner's call (2026-07-23).
- Platforms: Telegram + wildcar.ru + VK; MAX dropped — owner cannot create a MAX bot
  (needs a verified org profile), chose VK instead (2026-07-23).
- Strict `default` rule is intended; retelling generated fresh (owner, 2026-07-23).

## Deferred

- —
