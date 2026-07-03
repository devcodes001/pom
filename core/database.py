"""
database.py
Centralized SQLite persistence layer for FocusFlow.

All other core/ui modules talk to the database exclusively through the
Database class below -- no other module should open a sqlite3 connection
directly. This keeps schema changes and query logic in one place.
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path
from typing import Any, Iterator, Optional

logger = logging.getLogger("focusflow.database")


DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "database" / "focusflow.db"

DEFAULT_SETTINGS: dict[str, str] = {
    "theme_mode": "Dark",              # Dark | Light | System
    "accent_color": "#7C3AED",
    "focus_minutes": "25",
    "short_break_minutes": "5",
    "long_break_minutes": "15",
    "sessions_before_long_break": "4",
    "auto_start_breaks": "1",
    "auto_start_work": "0",
    "notifications_enabled": "1",
    "alarm_sound": "notification.wav",
    "alarm_volume": "0.8",
    "launch_at_startup": "0",
    "daily_goal_pomodoros": "8",
    "user_name": "there",
}


@dataclass
class Task:
    """Represents a single task row."""

    id: Optional[int]
    title: str
    description: str = ""
    priority: str = "Medium"          # High | Medium | Low
    deadline: Optional[str] = None    # ISO date string, may be None
    estimated_pomodoros: int = 1
    completed_pomodoros: int = 0
    completed: bool = False
    position: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    @property
    def progress(self) -> float:
        """Return completion progress in the range [0.0, 1.0]."""
        if self.estimated_pomodoros <= 0:
            return 1.0 if self.completed else 0.0
        return min(1.0, self.completed_pomodoros / self.estimated_pomodoros)


@dataclass
class Session:
    """Represents a single completed/aborted Pomodoro session row."""

    id: Optional[int]
    session_type: str          # focus | short_break | long_break
    duration_minutes: int
    completed: bool
    task_id: Optional[int]
    started_at: str
    ended_at: str


class Database:
    """Thin, thread-safe-enough wrapper around a single SQLite file.

    CustomTkinter callbacks all run on the main thread, and the Pomodoro
    engine only touches the DB via callbacks marshalled back onto the main
    thread, so a single connection with `check_same_thread=False` plus a
    module-level lock is sufficient here.
    """

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()
        self._init_default_settings()
        logger.info("Database ready at %s", self.db_path)

    # ------------------------------------------------------------------ #
    # Schema
    # ------------------------------------------------------------------ #
    def _init_schema(self) -> None:
        with self._cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    priority TEXT DEFAULT 'Medium',
                    deadline TEXT,
                    estimated_pomodoros INTEGER DEFAULT 1,
                    completed_pomodoros INTEGER DEFAULT 0,
                    completed INTEGER DEFAULT 0,
                    position INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_type TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    completed INTEGER NOT NULL,
                    task_id INTEGER,
                    started_at TEXT NOT NULL,
                    ended_at TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE SET NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )

    def _init_default_settings(self) -> None:
        with self._cursor() as cur:
            for key, value in DEFAULT_SETTINGS.items():
                cur.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                    (key, value),
                )

    @contextmanager
    def _cursor(self) -> Iterator[sqlite3.Cursor]:
        cur = self._conn.cursor()
        try:
            yield cur
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            logger.exception("Database operation failed, rolled back")
            raise
        finally:
            cur.close()

    def close(self) -> None:
        self._conn.close()

    # ------------------------------------------------------------------ #
    # Settings
    # ------------------------------------------------------------------ #
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self._cursor() as cur:
            cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cur.fetchone()
            return row["value"] if row else default

    def get_all_settings(self) -> dict[str, str]:
        with self._cursor() as cur:
            cur.execute("SELECT key, value FROM settings")
            return {row["key"]: row["value"] for row in cur.fetchall()}

    def set_setting(self, key: str, value: Any) -> None:
        with self._cursor() as cur:
            cur.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, str(value)),
            )

    # ------------------------------------------------------------------ #
    # Tasks
    # ------------------------------------------------------------------ #
    def add_task(self, task: Task) -> int:
        with self._cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(position), -1) + 1 AS next_pos FROM tasks")
            next_pos = cur.fetchone()["next_pos"]
            task.position = next_pos
            cur.execute(
                """
                INSERT INTO tasks
                    (title, description, priority, deadline, estimated_pomodoros,
                     completed_pomodoros, completed, position, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.title,
                    task.description,
                    task.priority,
                    task.deadline,
                    task.estimated_pomodoros,
                    task.completed_pomodoros,
                    int(task.completed),
                    next_pos,
                    task.created_at,
                ),
            )
            return cur.lastrowid

    def update_task(self, task: Task) -> None:
        if task.id is None:
            raise ValueError("Cannot update a task without an id")
        with self._cursor() as cur:
            cur.execute(
                """
                UPDATE tasks SET
                    title = ?, description = ?, priority = ?, deadline = ?,
                    estimated_pomodoros = ?, completed_pomodoros = ?,
                    completed = ?, position = ?
                WHERE id = ?
                """,
                (
                    task.title,
                    task.description,
                    task.priority,
                    task.deadline,
                    task.estimated_pomodoros,
                    task.completed_pomodoros,
                    int(task.completed),
                    task.position,
                    task.id,
                ),
            )

    def delete_task(self, task_id: int) -> None:
        with self._cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def increment_task_pomodoro(self, task_id: int) -> None:
        with self._cursor() as cur:
            cur.execute(
                "UPDATE tasks SET completed_pomodoros = completed_pomodoros + 1 WHERE id = ?",
                (task_id,),
            )

    def reorder_tasks(self, ordered_ids: list[int]) -> None:
        with self._cursor() as cur:
            for position, task_id in enumerate(ordered_ids):
                cur.execute(
                    "UPDATE tasks SET position = ? WHERE id = ?", (position, task_id)
                )

    def get_tasks(self) -> list[Task]:
        with self._cursor() as cur:
            cur.execute("SELECT * FROM tasks ORDER BY position ASC, id ASC")
            return [self._row_to_task(row) for row in cur.fetchall()]

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            priority=row["priority"],
            deadline=row["deadline"],
            estimated_pomodoros=row["estimated_pomodoros"],
            completed_pomodoros=row["completed_pomodoros"],
            completed=bool(row["completed"]),
            position=row["position"],
            created_at=row["created_at"],
        )

    # ------------------------------------------------------------------ #
    # Sessions
    # ------------------------------------------------------------------ #
    def log_session(self, session: Session) -> int:
        with self._cursor() as cur:
            cur.execute(
                """
                INSERT INTO sessions
                    (session_type, duration_minutes, completed, task_id, started_at, ended_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_type,
                    session.duration_minutes,
                    int(session.completed),
                    session.task_id,
                    session.started_at,
                    session.ended_at,
                ),
            )
            return cur.lastrowid

    def get_sessions_since(self, since_iso_date: str) -> list[Session]:
        with self._cursor() as cur:
            cur.execute(
                "SELECT * FROM sessions WHERE started_at >= ? ORDER BY started_at ASC",
                (since_iso_date,),
            )
            return [self._row_to_session(row) for row in cur.fetchall()]

    def get_all_sessions(self) -> list[Session]:
        with self._cursor() as cur:
            cur.execute("SELECT * FROM sessions ORDER BY started_at ASC")
            return [self._row_to_session(row) for row in cur.fetchall()]

    @staticmethod
    def _row_to_session(row: sqlite3.Row) -> Session:
        return Session(
            id=row["id"],
            session_type=row["session_type"],
            duration_minutes=row["duration_minutes"],
            completed=bool(row["completed"]),
            task_id=row["task_id"],
            started_at=row["started_at"],
            ended_at=row["ended_at"],
        )
