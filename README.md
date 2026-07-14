# positive-news-evaluator

AI news evaluator. Reads every news item collected by Positive News Crawler (sibling
repo `positive-news-crawler`, exchange via its `exchange_*` SQLite contract), scores it
on a fixed set of 20 characteristics (integer 0–10 each, independent axes), and
configurable per-axis thresholds decide which items pass on.

Status: specification stage — characteristic set v1 is fixed; the threshold model,
evaluator prompt, and service skeleton are next. No runnable code yet.

- Product spec: `AGENTS/SPEC.md` (in Russian)
- Agent workflow & repo map: `AGENTS.md`
