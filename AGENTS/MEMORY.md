# Memory

Durable agent memory for this repository: working agreements and facts that are NOT
derivable from the code, git history, or SPEC/STATE/HISTORY.

This is the ONLY agent memory store in the project. Do not use external or per-tool memory
stores — memory must travel with the repo (see AGENTS.md -> Memory). Read at the start of
every session; when you learn something durable, append a short bullet here and commit it
together with the related change.

MEMORY.md = durable facts/agreements; current state -> STATE.md; iteration log -> HISTORY.md.

## Working agreements (feedback)

- Agents must not create system principals (users/groups): `useradd newsevaluator` was
  denied by permission policy on 2026-07-14. Why: granting access to prod data is the
  server owner's decision — ask instead.

## Project facts

- The v0 test selector writes `decision='skipped'` on purpose: scores without a verdict
  until the threshold model lands (see SPEC «Сервис v0»).
