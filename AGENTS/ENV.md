# Environment

Host facts, tools, credentials, and command cheat-sheet for this project.
Update whenever a new tool, credential, or host-specific quirk is learned.

## Host

- **Dev**: Linux (kernel 6.8) / bash / user `keeper` / repo at `/home/keeper/repo/positive-news-evaluator`
- **Prod**: same host. The script is copied to `/opt/news-evaluator/evaluator.py` (`/home/keeper` is 750, other users cannot read the repo). Per the crawler's exchange contract, direct SQLite clients run on this host under a user in the `newscrawler` group; test runs use the `newscrawler` user itself — a dedicated system user needs the server owner (see `AGENTS/MEMORY.md`).

## Tools

- git; commit identity `wildcar <wildcar@mail.ru>`; GitHub push via `gh` auth (account `wildcar`).
- Sibling repo: `~/repo/positive-news-crawler` — the upstream crawler; its `docs/database-contract.md` defines the `exchange_*` SQLite contract this service consumes.
- model-router-mcp: MCP server for model access, systemd unit `model-router-mcp.service`, Streamable HTTP endpoint `http://127.0.0.1:8088/mcp`, deployed at `/opt/model-router-mcp`, sources at `~/repo/model-router-mcp`. Registered deepseek chat models: `deepseek-chat`, `deepseek-reasoner`.

## Credentials & secrets

- Router Bearer token: `AUTH_TOKEN` in `/opt/model-router-mcp/.env` (root-readable via sudo). Pass to the evaluator as `ROUTER_AUTH_TOKEN`; never commit it.
- Local env files (`.env*`) are gitignored and must not be committed.

## Environments

| Env | Host | Identifier | Role / account | Where used |
|-----|------|------------|----------------|------------|
| dev  | local Linux | `/home/keeper/repo/positive-news-evaluator` | `keeper` | development, unit tests |
| prod | same host | `/var/lib/newscrawler/newscrawler.sqlite3`, `/opt/news-evaluator` | `newscrawler` (test runs); dedicated user pending | read queue, write events + scores |

## Commands cheat-sheet

### Dev

```
python3 -m unittest discover -s tests          # unit tests, no network
```

### Prod

```
# deploy (after changing evaluator.py)
sudo install -m 0644 evaluator.py /opt/news-evaluator/evaluator.py

# run a batch (token read via sudo, never echo it)
TOKEN=$(sudo grep '^AUTH_TOKEN=' /opt/model-router-mcp/.env | cut -d= -f2-)
sudo -u newscrawler env ROUTER_AUTH_TOKEN="$TOKEN" \
  bash -c 'umask 0007; python3 /opt/news-evaluator/evaluator.py --limit 3'
# add --dry-run to print scores without writing
```

## Host-specific quirks

### Dev

- `127.0.0.1:8000` is the crawler web UI (waitress, redirects to https) — the model router is on `8088`.

### Prod

- SQLite sidecar files (`-wal`, `-shm`) must stay group-accessible: clients run with `umask 0007` (see the crawler's `docs/database-contract.md`).
- FastMCP redirects `/mcp` to `/mcp/` with 307; urllib does not re-POST on redirects — the evaluator's client follows 307/308 manually.
- The router's deepseek adapter forwards only `temperature`, `max_tokens`, `top_p` from params; `response_format` (JSON mode) does not reach the provider, so strict JSON relies on the prompt plus validation.
