# History

Newest first. Each entry ≤5 lines using the format defined in `AGENTS.md`.

---

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
