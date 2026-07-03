"""
task_manager.py
Business logic for creating, editing, filtering and reordering tasks.
The UI layer should only ever talk to TaskManager, never to Database
directly, so validation rules live in exactly one place.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Optional

from core.database import Database, Task

logger = logging.getLogger("focusflow.tasks")

VALID_PRIORITIES = ("High", "Medium", "Low")


class TaskFilter(str, Enum):
    ALL = "All"
    PENDING = "Pending"
    COMPLETED = "Completed"


class TaskManager:
    """CRUD + query layer for tasks, with an in-memory cache for fast UI reads."""

    def __init__(self, db: Database) -> None:
        self._db = db
        self._tasks: list[Task] = self._db.get_tasks()

    # ------------------------------------------------------------------ #
    # Mutations
    # ------------------------------------------------------------------ #
    def add_task(
        self,
        title: str,
        description: str = "",
        priority: str = "Medium",
        deadline: Optional[str] = None,
        estimated_pomodoros: int = 1,
    ) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty")
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of {VALID_PRIORITIES}")
        if estimated_pomodoros < 1:
            raise ValueError("Estimated Pomodoros must be at least 1")

        task = Task(
            id=None,
            title=title,
            description=description.strip(),
            priority=priority,
            deadline=deadline,
            estimated_pomodoros=estimated_pomodoros,
        )
        task.id = self._db.add_task(task)
        self._tasks.append(task)
        logger.info("Task added: %s (id=%s)", task.title, task.id)
        return task

    def edit_task(self, task_id: int, **fields) -> Task:
        task = self._find(task_id)
        if "priority" in fields and fields["priority"] not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of {VALID_PRIORITIES}")
        for key, value in fields.items():
            if not hasattr(task, key):
                raise AttributeError(f"Unknown task field: {key}")
            setattr(task, key, value)
        self._db.update_task(task)
        logger.info("Task edited: id=%s fields=%s", task_id, list(fields))
        return task

    def delete_task(self, task_id: int) -> None:
        self._db.delete_task(task_id)
        self._tasks = [t for t in self._tasks if t.id != task_id]
        logger.info("Task deleted: id=%s", task_id)

    def toggle_complete(self, task_id: int) -> Task:
        task = self._find(task_id)
        task.completed = not task.completed
        self._db.update_task(task)
        logger.info("Task %s marked completed=%s", task_id, task.completed)
        return task

    def register_pomodoro_completion(self, task_id: int) -> Task:
        """Called by the Pomodoro engine when a focus session tied to this
        task finishes successfully."""
        task = self._find(task_id)
        task.completed_pomodoros += 1
        if task.completed_pomodoros >= task.estimated_pomodoros:
            task.completed = True
        self._db.update_task(task)
        return task

    def reorder(self, ordered_ids: list[int]) -> None:
        self._db.reorder_tasks(ordered_ids)
        order_index = {tid: i for i, tid in enumerate(ordered_ids)}
        for task in self._tasks:
            if task.id in order_index:
                task.position = order_index[task.id]
        self._tasks.sort(key=lambda t: t.position)

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #
    def _find(self, task_id: int) -> Task:
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise KeyError(f"No task with id {task_id}")

    def get_tasks(
        self, filter_: TaskFilter = TaskFilter.ALL, search: str = ""
    ) -> list[Task]:
        tasks = sorted(self._tasks, key=lambda t: t.position)
        if filter_ == TaskFilter.PENDING:
            tasks = [t for t in tasks if not t.completed]
        elif filter_ == TaskFilter.COMPLETED:
            tasks = [t for t in tasks if t.completed]

        if search.strip():
            needle = search.strip().lower()
            tasks = [
                t
                for t in tasks
                if needle in t.title.lower() or needle in t.description.lower()
            ]
        return tasks

    def refresh(self) -> None:
        self._tasks = self._db.get_tasks()
