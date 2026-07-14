# Environment

Host facts, tools, credentials, and command cheat-sheet for this project.
Update whenever a new tool, credential, or host-specific quirk is learned.

## Host

- **Dev**: Linux (kernel 6.8) / bash / user `keeper` / repo at `/home/keeper/repo/positive-news-evaluator`
- **Prod**: not deployed yet. Per the crawler's exchange contract, direct SQLite clients must run on the same Ubuntu host as the crawler, under a dedicated system user in the `newscrawler` group (see `~/repo/positive-news-crawler/docs/database-contract.md`).

## Tools

- git; commit identity `wildcar <wildcar@mail.ru>`.
- Sibling repo: `~/repo/positive-news-crawler` — the upstream crawler; its `docs/database-contract.md` defines the `exchange_*` SQLite contract this service consumes.

## Credentials & secrets

- None yet. When prod access appears, keep pointers only — never store values here.
- Local env files (`.env*`) are gitignored and must not be committed.

## Environments

| Env | Host | Identifier | Role / account | Where used |
|-----|------|------------|----------------|------------|
| dev  | local Linux | `/home/keeper/repo/positive-news-evaluator` | `keeper` | spec work, future development |
| prod | — | `/var/lib/newscrawler/newscrawler.sqlite3` (crawler's Ubuntu host) | dedicated user in `newscrawler` group | future: read queue, write verdicts |

## Commands cheat-sheet

### Dev

```
# no code yet — nothing to run
```

### Prod

```
# not deployed yet
```

## Host-specific quirks

### Dev

- —

### Prod

- SQLite sidecar files (`-wal`, `-shm`) must stay group-accessible: clients run with `umask 0007` (see the crawler's `docs/database-contract.md`).
