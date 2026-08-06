# databricks-lakebase-ticketing

An internal support ticketing system built as a **Databricks App**, backed by
**Lakebase** (Databricks-managed Postgres). Users can create support tickets,
hold a threaded conversation on each one, change ticket status, and view
aggregate statistics — all reading from and writing to Lakebase.

## Features

- **Tickets & conversations** — create tickets and append messages in
  conversation order.
- **Status workflow** — `open → in_progress → waiting → resolved / closed / canceled`.
- **Priorities** — `low`, `normal`, `high`, `urgent`.
- **Filtering** — filter the ticket list by status.
- **Statistics dashboard** — totals, open backlog, count by status/priority,
  message count, and tickets awaiting a first reply, shown in the app's home view.
- **Input validation** — ticket titles require ≥ 15 characters, replies ≥ 3
  characters; enforced server-side and mirrored in the UI.
- **Identity-aware** — the logged-in user is resolved from the Databricks
  `X-Forwarded-Email` header (falling back to the SDK's current user locally).

## Architecture

| File | Role |
|------|------|
| [`app.py`](app.py) | Flask app: JSON API over the tickets schema + serves the single-page UI. |
| [`lakebase.py`](lakebase.py) | Lakebase (Postgres) connection helper — reads the connection URL from a Databricks secret. |
| [`templates/index.html`](templates/index.html) | Single-page, fetch-based UI (create/list/detail/reply/status/stats). |
| [`app.yaml`](app.yaml) | Databricks Apps run configuration. |
| [`requirements.txt`](requirements.txt) | Python dependencies. |

## Data model

Two related tables in Lakebase. The app assumes `CHECK` constraints on
`status`/`priority` that match the values above. Illustrative DDL:

```sql
CREATE TABLE tickets (
    ticket_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title       TEXT NOT NULL,
    priority    TEXT NOT NULL DEFAULT 'normal'
                CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    status      TEXT NOT NULL DEFAULT 'open'
                CHECK (status IN ('open', 'in_progress', 'waiting',
                                  'resolved', 'closed', 'canceled')),
    created_by  TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ticket_messages (
    message_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticket_id    BIGINT NOT NULL REFERENCES tickets(ticket_id),
    message_text TEXT NOT NULL,
    author       TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Configuration

The app connects to Lakebase through a single Postgres connection URL stored in
a Databricks **secret** (base64-encoded). It is never committed or passed as a
plaintext env var. The scope/key are configurable:

| Env var | Default | Description |
|---------|---------|-------------|
| `LAKEBASE_SECRET_SCOPE` | `database-ticketing` | Databricks secret scope holding the connection URL. |
| `LAKEBASE_SECRET_KEY` | `lakebase-url` | Secret key within that scope. |

The decoded secret is a standard Postgres URL, e.g.:

```
postgresql://role:password@host:5432/databricks_postgres?sslmode=require
```

Store it (base64-encoded) as a Databricks secret rather than in the repo:

```bash
printf '%s' "$LAKEBASE_URL" | base64 | \
  databricks secrets put-secret database-ticketing lakebase-url
```

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

The server listens on `http://0.0.0.0:8000` by default. Override with
`FLASK_RUN_HOST` / `FLASK_RUN_PORT` (or `DATABRICKS_APP_PORT`). Local runs still
read the Lakebase URL from the configured Databricks secret, so a valid
Databricks CLI/SDK auth context is required.

## Deploying to Databricks Apps

Deployment is driven by [`app.yaml`](app.yaml), which runs `python app.py` and
sets the secret scope/key. Deploy the app through Databricks Apps; the platform
injects the authenticated user via the `X-Forwarded-Email` header at runtime.

## API reference

All endpoints return JSON.

| Method | Path | Body | Description |
|--------|------|------|-------------|
| `GET` | `/healthz` | — | Health check. |
| `GET` | `/` | — | Single-page UI. |
| `GET` | `/tickets` | — | List tickets, newest first. Query: `status`, `limit` (default 200). |
| `POST` | `/tickets` | `{title, priority?, created_by?}` | Create a ticket. Title ≥ 15 chars. |
| `GET` | `/tickets/{id}` | — | A ticket and its messages. |
| `POST` | `/tickets/{id}/messages` | `{message_text, author?}` | Append a message. Text ≥ 3 chars. |
| `POST` | `/tickets/{id}/status` | `{status}` | Change a ticket's status. |
| `GET` | `/meta` | — | Allowed statuses and priorities. |
| `GET` | `/stats` | — | Aggregate counts for the dashboard. |

There is no delete route by design.
