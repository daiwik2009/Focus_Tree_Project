import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "focus_tree.db"

SCOPES = ("yearly", "monthly", "weekly", "lifetime")

SCOPE_COPY = {
    "yearly": "Long-term objectives and major milestones for the year.",
    "monthly": "Campaigns and habits you want to close this month.",
    "weekly": "Short operations you can finish in a week.",
    "lifetime": "The national spirits of your life — slow, permanent goals.",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS focuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scope TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                completion_time TEXT NOT NULL DEFAULT '',
                points INTEGER NOT NULL DEFAULT 10,
                icon TEXT NOT NULL DEFAULT '',
                parent_id INTEGER,
                completed INTEGER NOT NULL DEFAULT 0,
                completed_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (parent_id) REFERENCES focuses(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS icons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                search_text TEXT NOT NULL DEFAULT ''
            );

            CREATE INDEX IF NOT EXISTS idx_focuses_scope ON focuses(scope);
            CREATE INDEX IF NOT EXISTS idx_icons_category ON icons(category);
            CREATE INDEX IF NOT EXISTS idx_icons_search ON icons(search_text);
            """
        )


def row_to_dict(row):
    return dict(row) if row is not None else None


def list_focuses(conn, scope):
    rows = conn.execute(
        """
        SELECT * FROM focuses
        WHERE scope = ?
        ORDER BY created_at ASC, id ASC
        """,
        (scope,),
    ).fetchall()
    return [row_to_dict(r) for r in rows]


def get_focus(conn, focus_id):
    return row_to_dict(
        conn.execute("SELECT * FROM focuses WHERE id = ?", (focus_id,)).fetchone()
    )


def add_focus(conn, *, scope, name, description, completion_time, points, icon, parent_id):
    cur = conn.execute(
        """
        INSERT INTO focuses (
            scope, name, description, completion_time, points, icon,
            parent_id, completed, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
        """,
        (
            scope,
            name.strip(),
            (description or "").strip(),
            (completion_time or "").strip(),
            int(points),
            (icon or "").strip(),
            parent_id,
            utc_now(),
        ),
    )
    return cur.lastrowid


def set_completed(conn, focus_id, completed):
    conn.execute(
        """
        UPDATE focuses
        SET completed = ?, completed_at = ?
        WHERE id = ?
        """,
        (1 if completed else 0, utc_now() if completed else None, focus_id),
    )


def delete_focus(conn, focus_id):
    conn.execute("DELETE FROM focuses WHERE id = ?", (focus_id,))


def score_totals(conn):
    rows = conn.execute(
        """
        SELECT scope,
               COALESCE(SUM(CASE WHEN completed = 1 THEN points ELSE 0 END), 0) AS earned,
               COALESCE(SUM(points), 0) AS possible
        FROM focuses
        GROUP BY scope
        """
    ).fetchall()
    by_scope = {scope: {"earned": 0, "possible": 0} for scope in SCOPES}
    for row in rows:
        by_scope[row["scope"]] = {
            "earned": int(row["earned"]),
            "possible": int(row["possible"]),
        }
    overall = {
        "earned": sum(v["earned"] for v in by_scope.values()),
        "possible": sum(v["possible"] for v in by_scope.values()),
    }
    return overall, by_scope


def get_icon(conn, icon_id):
    return row_to_dict(
        conn.execute("SELECT * FROM icons WHERE id = ?", (icon_id,)).fetchone()
    )


def icon_count(conn):
    row = conn.execute("SELECT COUNT(*) AS n FROM icons").fetchone()
    return int(row["n"])


def replace_icons(conn, icons):
    conn.execute("DELETE FROM icons")
    conn.executemany(
        """
        INSERT OR IGNORE INTO icons (name, category, url, search_text)
        VALUES (?, ?, ?, ?)
        """,
        icons,
    )


def search_icons(conn, query="", category="National focuses", limit=80, offset=0):
    query = (query or "").strip()
    category = (category or "").strip()
    clauses = []
    args = []
    if category:
        clauses.append("category = ?")
        args.append(category)
    if query:
        like = f"%{query.lower()}%"
        clauses.append("(LOWER(search_text) LIKE ? OR LOWER(name) LIKE ?)")
        args.extend([like, like])
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    total = conn.execute(
        f"SELECT COUNT(*) AS n FROM icons {where}", args
    ).fetchone()["n"]
    rows = conn.execute(
        f"""
        SELECT id, name, category, url
        FROM icons
        {where}
        ORDER BY name
        LIMIT ? OFFSET ?
        """,
        [*args, limit, offset],
    ).fetchall()
    return [row_to_dict(r) for r in rows], int(total)


def icon_categories(conn):
    rows = conn.execute(
        """
        SELECT category, COUNT(*) AS n
        FROM icons
        GROUP BY category
        ORDER BY n DESC
        """
    ).fetchall()
    return [row_to_dict(r) for r in rows]
