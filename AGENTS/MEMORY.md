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
  denied by permission policy on 2026-07-14 and again on 2026-07-15 even after the
  owner approved the permanent deploy in chat. Why: granting access to prod data must
  be executed by the owner personally — prepare an installer and hand it over instead.

## Project facts

- The v0 test selector writes `decision='skipped'` on purpose: scores without a verdict
  until the threshold model lands (see SPEC «Сервис v0»).
- The `default` selection rule (owner's spec, 2026-07-23): positivity≥8 AND heroism≤4
  AND clickbait≤4 AND promo≤4 AND at least one of pride_humanity/pride_russia/inspiration/
  beauty/interestingness/surprise/uniqueness ≥9. Note heroism is used as an UPPER gate
  here even though its reference `threshold_direction` is `lower_bound`.
- Post-selection artifacts (prepared HTML, downloaded illustrations, retelling) and the
  «Подготовлено»/«Опубликовано» labels live in an evaluator-owned DB, NOT the crawler DB:
  the exchange contract forbids clients from writing any table but the two exchange ones.
- Deleting rejected news is the crawler's job (its maintenance), not the evaluator's —
  same contract limit. The evaluator only supplies the `not_positive` verdict.
