from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
  version INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  file_path TEXT NOT NULL,
  file_name TEXT NOT NULL,
  page_count INTEGER NOT NULL,
  encrypted INTEGER NOT NULL DEFAULT 0,
  opened_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  task_type TEXT NOT NULL,
  status TEXT NOT NULL,
  priority INTEGER NOT NULL DEFAULT 5,
  progress REAL NOT NULL DEFAULT 0,
  payload_json TEXT NOT NULL,
  logs_json TEXT NOT NULL DEFAULT '[]',
  result_ref TEXT,
  error_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  started_at TEXT,
  finished_at TEXT
);
"""


class ProjectStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def init(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA_SQL)
            self._ensure_tasks_columns(conn)
            conn.commit()

    def save_document(self, payload: dict) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO documents (id, file_path, file_name, page_count, encrypted, opened_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  file_path = excluded.file_path,
                  file_name = excluded.file_name,
                  page_count = excluded.page_count,
                  encrypted = excluded.encrypted,
                  updated_at = excluded.updated_at
                """,
                (
                    payload["id"],
                    payload["file_path"],
                    payload["file_name"],
                    payload["page_count"],
                    int(payload.get("encrypted", False)),
                    payload.get("opened_at", now),
                    now,
                ),
            )
            conn.commit()

    def get_document(self, document_id: str) -> dict | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT id, file_path, file_name, page_count, encrypted, opened_at, updated_at FROM documents WHERE id = ?",
                (document_id,),
            ).fetchone()
            return dict(row) if row else None

    def save_task(self, payload: dict) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                  id, task_type, status, priority, progress, payload_json,
                  logs_json, result_ref, error_json, created_at, updated_at, started_at, finished_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  status = excluded.status,
                  priority = excluded.priority,
                  progress = excluded.progress,
                  payload_json = excluded.payload_json,
                  logs_json = excluded.logs_json,
                  result_ref = excluded.result_ref,
                  error_json = excluded.error_json,
                  updated_at = excluded.updated_at,
                  started_at = excluded.started_at,
                  finished_at = excluded.finished_at
                """,
                (
                    payload["id"],
                    payload["task_type"],
                    payload["status"],
                    int(payload.get("priority", 5)),
                    float(payload.get("progress", 0.0)),
                    json.dumps(payload.get("payload", {}), ensure_ascii=False),
                    json.dumps(payload.get("logs", []), ensure_ascii=False),
                    payload.get("result_ref"),
                    json.dumps(payload.get("error"), ensure_ascii=False)
                    if payload.get("error") is not None
                    else None,
                    payload.get("created_at", now),
                    now,
                    payload.get("started_at"),
                    payload.get("finished_at"),
                ),
            )
            conn.commit()

    def get_task(self, task_id: str) -> dict | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if not row:
                return None
            data = dict(row)
            data["payload"] = json.loads(data.get("payload_json") or "{}")
            data["logs"] = json.loads(data.get("logs_json") or "[]")
            data["error"] = json.loads(data["error_json"]) if data.get("error_json") else None
            return data

    @staticmethod
    def _ensure_tasks_columns(conn: sqlite3.Connection) -> None:
        rows = conn.execute("PRAGMA table_info(tasks)").fetchall()
        existing = {row[1] for row in rows}
        wanted = {
            "priority": "INTEGER NOT NULL DEFAULT 5",
            "logs_json": "TEXT NOT NULL DEFAULT '[]'",
            "result_ref": "TEXT",
            "error_json": "TEXT",
            "updated_at": "TEXT",
        }
        for name, ddl in wanted.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE tasks ADD COLUMN {name} {ddl}")
