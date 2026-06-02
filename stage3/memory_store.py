import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(__file__).with_name("memories.db")
VALID_MEMORY_TYPES = {
    "user_fact",
    "user_preference",
    "project_context",
    "experience",
    "task_state",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence REAL NOT NULL DEFAULT 1.0,
                source TEXT NOT NULL DEFAULT 'chat_extraction',
                is_deleted INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_used_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_memories_user_active
            ON memories(user_id, is_deleted, memory_type, updated_at)
            """
        )


def add_memory(user_id, memory_type, content, confidence=1.0, source="manual", db_path=DB_PATH):
    memory_type = memory_type.strip()
    content = content.strip()
    if memory_type not in VALID_MEMORY_TYPES:
        raise ValueError(f"Invalid memory_type: {memory_type}")
    if not content:
        raise ValueError("Memory content cannot be empty")

    timestamp = now_iso()
    with get_connection(db_path) as conn:
        existing = conn.execute(
            """
            SELECT id FROM memories
            WHERE user_id = ? AND is_deleted = 0 AND memory_type = ? AND content = ?
            LIMIT 1
            """,
            (user_id, memory_type, content),
        ).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE memories
                SET confidence = MAX(confidence, ?), updated_at = ?
                WHERE id = ?
                """,
                (confidence, timestamp, existing["id"]),
            )
            return existing["id"]

        cursor = conn.execute(
            """
            INSERT INTO memories (
                user_id, memory_type, content, confidence, source,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, memory_type, content, confidence, source, timestamp, timestamp),
        )
        return cursor.lastrowid


def list_memories(user_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        return conn.execute(
            """
            SELECT id, memory_type, content, confidence, source, created_at, updated_at, last_used_at
            FROM memories
            WHERE user_id = ? AND is_deleted = 0
            ORDER BY updated_at DESC, id DESC
            """,
            (user_id,),
        ).fetchall()


def delete_memory(user_id, memory_id, db_path=DB_PATH):
    timestamp = now_iso()
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            UPDATE memories
            SET is_deleted = 1, updated_at = ?
            WHERE user_id = ? AND id = ? AND is_deleted = 0
            """,
            (timestamp, user_id, memory_id),
        )
        return cursor.rowcount > 0


def search_memories(user_id, query, limit=8, db_path=DB_PATH):
    keywords = [word for word in query.strip().split() if word]
    rows = []

    with get_connection(db_path) as conn:
        preference_rows = conn.execute(
            """
            SELECT id, memory_type, content, confidence, updated_at, last_used_at
            FROM memories
            WHERE user_id = ?
              AND is_deleted = 0
              AND memory_type IN ('user_preference', 'task_state', 'project_context')
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        rows.extend(preference_rows)

        for keyword in keywords[:5]:
            matched_rows = conn.execute(
                """
                SELECT id, memory_type, content, confidence, updated_at, last_used_at
                FROM memories
                WHERE user_id = ?
                  AND is_deleted = 0
                  AND content LIKE ?
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (user_id, f"%{keyword}%", limit),
            ).fetchall()
            rows.extend(matched_rows)

    unique_rows = []
    seen_ids = set()
    for row in rows:
        if row["id"] in seen_ids:
            continue
        seen_ids.add(row["id"])
        unique_rows.append(row)
        if len(unique_rows) >= limit:
            break
    return unique_rows


def mark_memories_used(user_id, memory_ids, db_path=DB_PATH):
    if not memory_ids:
        return
    timestamp = now_iso()
    placeholders = ",".join("?" for _ in memory_ids)
    with get_connection(db_path) as conn:
        conn.execute(
            f"""
            UPDATE memories
            SET last_used_at = ?
            WHERE user_id = ? AND id IN ({placeholders})
            """,
            (timestamp, user_id, *memory_ids),
        )
