"""
Ticketing Databricks App.

- Serves a small Flask JSON API over the Lakebase tickets schema
- Renders a single-page UI from templates/index.html (fetch-based)
- Reads/writes to Lakebase (Databricks-managed Postgres) via lakebase.py

Tables:
    tickets(ticket_id, title, priority, status, created_by, created_at)
    ticket_messages(message_id, ticket_id, message_text, author, created_at)

Run locally:
    python app.py
Deploy as a Databricks App using app.yaml.
"""

import logging
import os
from datetime import datetime

from databricks.sdk import WorkspaceClient
from flask import Flask, jsonify, render_template, request

import lakebase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ticketing-app")

app = Flask(__name__)
_w = WorkspaceClient()

# Must match the CHECK constraints on the tables exactly.
STATUSES = ["open", "in_progress", "waiting", "resolved", "closed", "canceled"]
PRIORITIES = ["low", "normal", "high", "urgent"]


def _current_user_email() -> str:
    """
    Resolve the current user's email so tickets/messages can be attributed.

    Databricks Apps inject the logged-in user's identity via the
    X-Forwarded-Email header on every request. Fall back to the Databricks
    SDK's current_user API for local development where that header isn't set.
    """
    header_email = request.headers.get("X-Forwarded-Email")
    if header_email:
        return header_email
    return _w.current_user.me().user_name


def _serialize(row: dict) -> dict:
    """Convert non-JSON-native values (datetimes) to ISO strings for the API."""
    out = {}
    for key, value in row.items():
        out[key] = value.isoformat() if isinstance(value, datetime) else value
    return out


# --------------------------------------------------------------------------- #
# Infra routes
# --------------------------------------------------------------------------- #
@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.errorhandler(Exception)
def handle_exception(err):
    """Ensure all unhandled errors return JSON (not an HTML error page),
    so the frontend's resp.json() call never chokes on HTML."""
    logger.exception("Unhandled exception while processing request")
    status_code = getattr(err, "code", 500)
    if not isinstance(status_code, int):
        status_code = 500
    return jsonify({"error": str(err)}), status_code


@app.route("/")
def index():
    """Single-page ticketing UI."""
    return render_template("index.html", email=_current_user_email())


# --------------------------------------------------------------------------- #
# Ticket API
# --------------------------------------------------------------------------- #
@app.route("/tickets", methods=["GET"])
def list_tickets():
    """List tickets, newest first, optionally filtered by ?status=."""
    status_filter = request.args.get("status")
    limit = int(request.args.get("limit", 200))

    if status_filter in STATUSES:
        rows = lakebase.run_query(
            """
            SELECT ticket_id, title, priority, status, created_by, created_at
            FROM tickets
            WHERE status = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (status_filter, limit),
        )
    else:
        rows = lakebase.run_query(
            """
            SELECT ticket_id, title, priority, status, created_by, created_at
            FROM tickets
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
    return jsonify([_serialize(r) for r in rows])


@app.route("/tickets", methods=["POST"])
def create_ticket():
    """Create a ticket. Body: {title, priority?, created_by?}.

    Uses get_connection directly for INSERT ... RETURNING, because
    run_write only reports a rowcount and we want the generated id.
    """
    body = request.get_json(silent=True) or {}

    title = (body.get("title") or "").strip()
    priority = (body.get("priority") or "normal").strip()
    created_by = (body.get("created_by") or "").strip() or _current_user_email()

    if not title:
        return jsonify({"error": "title is required"}), 400
    if priority not in PRIORITIES:
        return jsonify({"error": f"invalid priority: {priority!r}"}), 400

    with lakebase.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tickets (title, priority, created_by)
                VALUES (%s, %s, %s)
                RETURNING ticket_id, title, priority, status, created_by, created_at
                """,
                (title, priority, created_by),
            )
            row = cur.fetchone()
            conn.commit()

    return jsonify(_serialize(row)), 201


@app.route("/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    """Return a single ticket together with its messages (conversation order)."""
    ticket_rows = lakebase.run_query(
        """
        SELECT ticket_id, title, priority, status, created_by, created_at
        FROM tickets
        WHERE ticket_id = %s
        """,
        (ticket_id,),
    )
    if not ticket_rows:
        return jsonify({"error": f"ticket {ticket_id} not found"}), 404

    messages = lakebase.run_query(
        """
        SELECT message_id, ticket_id, message_text, author, created_at
        FROM ticket_messages
        WHERE ticket_id = %s
        ORDER BY created_at ASC, message_id ASC
        """,
        (ticket_id,),
    )
    return jsonify(
        {
            "ticket": _serialize(ticket_rows[0]),
            "messages": [_serialize(m) for m in messages],
        }
    )


@app.route("/tickets/<int:ticket_id>/messages", methods=["POST"])
def add_message(ticket_id):
    """Append a message to a ticket. Body: {message_text, author?}."""
    if not _ticket_exists(ticket_id):
        return jsonify({"error": f"ticket {ticket_id} not found"}), 404

    body = request.get_json(silent=True) or {}
    text = (body.get("message_text") or "").strip()
    author = (body.get("author") or "").strip() or _current_user_email()

    if not text:
        return jsonify({"error": "message_text is required"}), 400

    lakebase.run_write(
        """
        INSERT INTO ticket_messages (ticket_id, message_text, author)
        VALUES (%s, %s, %s)
        """,
        (ticket_id, text, author),
    )
    return jsonify({"ticket_id": ticket_id, "author": author}), 201


@app.route("/tickets/<int:ticket_id>/status", methods=["POST"])
def update_status(ticket_id):
    """Change a ticket's status. Body: {status}. No delete route by design."""
    if not _ticket_exists(ticket_id):
        return jsonify({"error": f"ticket {ticket_id} not found"}), 404

    body = request.get_json(silent=True) or {}
    status = (body.get("status") or "").strip()
    if status not in STATUSES:
        return jsonify({"error": f"invalid status: {status!r}"}), 400

    lakebase.run_write(
        "UPDATE tickets SET status = %s WHERE ticket_id = %s",
        (status, ticket_id),
    )
    return jsonify({"ticket_id": ticket_id, "status": status})


@app.route("/meta", methods=["GET"])
def meta():
    """Expose the allowed statuses/priorities so the UI stays in sync."""
    return jsonify({"statuses": STATUSES, "priorities": PRIORITIES})


def _ticket_exists(ticket_id: int) -> bool:
    rows = lakebase.run_query(
        "SELECT 1 FROM tickets WHERE ticket_id = %s", (ticket_id,)
    )
    return bool(rows)


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("DATABRICKS_APP_PORT", os.getenv("FLASK_RUN_PORT", 8000)))
    app.run(debug=True, host=host, port=port)
    print(f"Flask app running on http://{host}:{port}")
