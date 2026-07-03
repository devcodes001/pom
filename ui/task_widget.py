"""
task_widget.py
Task list UI: add/edit/delete, mark complete, search, filter, and
drag-to-reorder. Talks only to TaskManager (never Database directly).
"""

from __future__ import annotations

import logging
from typing import Callable, Optional

import customtkinter as ctk

from core.database import Task
from core.task_manager import TaskFilter, TaskManager
from ui.theme import Palette, ThemeManager

logger = logging.getLogger("focusflow.ui.tasks")


class TaskRow(ctk.CTkFrame):
    """A single draggable task row."""

    def __init__(
        self,
        master,
        task: Task,
        theme: ThemeManager,
        on_toggle: Callable[[int], None],
        on_edit: Callable[[Task], None],
        on_delete: Callable[[int], None],
        on_drag_reorder: Callable[["TaskRow", int], None],
        **kwargs,
    ) -> None:
        super().__init__(master, corner_radius=14, **kwargs)
        self.task = task
        self.theme = theme
        self._on_toggle = on_toggle
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._on_drag_reorder = on_drag_reorder
        self._drag_start_y = 0

        self._build_ui()
        self.theme.subscribe(self._on_theme_changed)

    def _build_ui(self) -> None:
        colors = self.theme.colors
        self.configure(fg_color=colors.surface)

        self.grid_columnconfigure(1, weight=1)

        self.check_var = ctk.BooleanVar(value=self.task.completed)
        self.checkbox = ctk.CTkCheckBox(
            self,
            text="",
            variable=self.check_var,
            width=24,
            command=lambda: self._on_toggle(self.task.id),
            fg_color=colors.primary,
            hover_color=colors.primary,
        )
        self.checkbox.grid(row=0, column=0, rowspan=2, padx=(14, 10), pady=14)

        title_text = self.task.title
        self.title_label = ctk.CTkLabel(
            self,
            text=title_text,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=colors.text_secondary if self.task.completed else colors.text,
            anchor="w",
        )
        self.title_label.grid(row=0, column=1, sticky="ew", pady=(12, 0))

        meta_parts = [f"🍅 {self.task.completed_pomodoros}/{self.task.estimated_pomodoros}"]
        if self.task.deadline:
            meta_parts.append(f"📅 {self.task.deadline}")
        self.meta_label = ctk.CTkLabel(
            self,
            text="   •   ".join(meta_parts),
            font=ctk.CTkFont(size=12),
            text_color=colors.text_secondary,
            anchor="w",
        )
        self.meta_label.grid(row=1, column=1, sticky="ew", pady=(0, 12))

        self.priority_badge = ctk.CTkLabel(
            self,
            text=self.task.priority,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#FFFFFF",
            fg_color=self.theme.priority_color(self.task.priority),
            corner_radius=10,
            width=64,
            height=24,
        )
        self.priority_badge.grid(row=0, column=2, rowspan=2, padx=8)

        self.progress_bar = ctk.CTkProgressBar(
            self, width=90, height=8, progress_color=colors.primary
        )
        self.progress_bar.set(self.task.progress)
        self.progress_bar.grid(row=0, column=3, rowspan=2, padx=8)

        edit_btn = ctk.CTkButton(
            self, text="✎", width=32, height=32, fg_color="transparent",
            hover_color=colors.surface_alt, text_color=colors.text_secondary,
            command=lambda: self._on_edit(self.task),
        )
        edit_btn.grid(row=0, column=4, rowspan=2, padx=(4, 2))

        delete_btn = ctk.CTkButton(
            self, text="🗑", width=32, height=32, fg_color="transparent",
            hover_color=colors.surface_alt, text_color=colors.secondary,
            command=lambda: self._on_delete(self.task.id),
        )
        delete_btn.grid(row=0, column=5, rowspan=2, padx=(2, 14))

        # Drag-to-reorder: bind on the row itself and its non-interactive children
        for widget in (self, self.title_label, self.meta_label):
            widget.bind("<ButtonPress-1>", self._on_drag_start)
            widget.bind("<B1-Motion>", self._on_drag_motion)
            widget.bind("<ButtonRelease-1>", self._on_drag_release)

    def _on_drag_start(self, event) -> None:
        self._drag_start_y = event.y_root
        self.lift()

    def _on_drag_motion(self, event) -> None:
        delta = event.y_root - self._drag_start_y
        if abs(delta) > 28:
            direction = 1 if delta > 0 else -1
            self._on_drag_reorder(self, direction)
            self._drag_start_y = event.y_root

    def _on_drag_release(self, _event) -> None:
        pass

    def refresh(self, task: Task) -> None:
        self.task = task
        colors = self.theme.colors
        self.check_var.set(task.completed)
        self.title_label.configure(
            text=task.title,
            text_color=colors.text_secondary if task.completed else colors.text,
        )
        meta_parts = [f"🍅 {task.completed_pomodoros}/{task.estimated_pomodoros}"]
        if task.deadline:
            meta_parts.append(f"📅 {task.deadline}")
        self.meta_label.configure(text="   •   ".join(meta_parts))
        self.priority_badge.configure(
            text=task.priority, fg_color=self.theme.priority_color(task.priority)
        )
        self.progress_bar.set(task.progress)

    def _on_theme_changed(self, colors: Palette) -> None:
        self.configure(fg_color=colors.surface)
        self.title_label.configure(
            text_color=colors.text_secondary if self.task.completed else colors.text
        )
        self.meta_label.configure(text_color=colors.text_secondary)
        self.progress_bar.configure(progress_color=colors.primary)
        self.priority_badge.configure(fg_color=self.theme.priority_color(self.task.priority))


class TaskFormDialog(ctk.CTkToplevel):
    """Modal dialog for adding or editing a task."""

    def __init__(self, master, theme: ThemeManager, on_submit: Callable[[dict], None], task: Optional[Task] = None):
        super().__init__(master)
        self.theme = theme
        self._on_submit = on_submit
        self._task = task

        colors = theme.colors
        self.title("Edit Task" if task else "New Task")
        self.geometry("420x480")
        self.configure(fg_color=colors.background)
        self.grab_set()
        self.resizable(False, False)

        pad = {"padx": 24, "pady": (14, 4)}

        ctk.CTkLabel(self, text="Title", text_color=colors.text_secondary, anchor="w").pack(fill="x", **pad)
        self.title_entry = ctk.CTkEntry(self, height=38)
        self.title_entry.pack(fill="x", padx=24)
        if task:
            self.title_entry.insert(0, task.title)

        ctk.CTkLabel(self, text="Description", text_color=colors.text_secondary, anchor="w").pack(fill="x", **pad)
        self.desc_entry = ctk.CTkTextbox(self, height=70)
        self.desc_entry.pack(fill="x", padx=24)
        if task:
            self.desc_entry.insert("1.0", task.description)

        ctk.CTkLabel(self, text="Priority", text_color=colors.text_secondary, anchor="w").pack(fill="x", **pad)
        self.priority_menu = ctk.CTkOptionMenu(self, values=["High", "Medium", "Low"])
        self.priority_menu.set(task.priority if task else "Medium")
        self.priority_menu.pack(fill="x", padx=24)

        ctk.CTkLabel(self, text="Deadline (YYYY-MM-DD, optional)", text_color=colors.text_secondary, anchor="w").pack(fill="x", **pad)
        self.deadline_entry = ctk.CTkEntry(self, height=38)
        self.deadline_entry.pack(fill="x", padx=24)
        if task and task.deadline:
            self.deadline_entry.insert(0, task.deadline)

        ctk.CTkLabel(self, text="Estimated Pomodoros", text_color=colors.text_secondary, anchor="w").pack(fill="x", **pad)
        self.estimate_entry = ctk.CTkEntry(self, height=38)
        self.estimate_entry.insert(0, str(task.estimated_pomodoros if task else 1))
        self.estimate_entry.pack(fill="x", padx=24)

        self.error_label = ctk.CTkLabel(self, text="", text_color=colors.secondary)
        self.error_label.pack(fill="x", padx=24, pady=(6, 0))

        submit_btn = ctk.CTkButton(
            self, text="Save Task", height=42, fg_color=colors.primary, command=self._submit
        )
        submit_btn.pack(fill="x", padx=24, pady=20)

    def _submit(self) -> None:
        title = self.title_entry.get().strip()
        if not title:
            self.error_label.configure(text="Title is required.")
            return
        try:
            estimate = int(self.estimate_entry.get().strip() or "1")
            if estimate < 1:
                raise ValueError
        except ValueError:
            self.error_label.configure(text="Estimated Pomodoros must be a positive integer.")
            return

        self._on_submit(
            {
                "title": title,
                "description": self.desc_entry.get("1.0", "end").strip(),
                "priority": self.priority_menu.get(),
                "deadline": self.deadline_entry.get().strip() or None,
                "estimated_pomodoros": estimate,
            }
        )
        self.destroy()


class TaskWidget(ctk.CTkFrame):
    def __init__(self, master, theme: ThemeManager, task_manager: TaskManager, on_change: Callable[[], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme = theme
        self.task_manager = task_manager
        self._on_change = on_change
        self._current_filter = TaskFilter.ALL
        self._search_query = ""
        self._rows: list[TaskRow] = []

        self._build_ui()
        self.theme.subscribe(self._on_theme_changed)
        self.refresh()

    def _build_ui(self) -> None:
        colors = self.theme.colors

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        self.search_entry = ctk.CTkEntry(header, placeholder_text="Search tasks…", height=36, width=220)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        self.filter_menu = ctk.CTkOptionMenu(
            header, values=[f.value for f in TaskFilter], command=self._on_filter_changed, width=130
        )
        self.filter_menu.set(TaskFilter.ALL.value)
        self.filter_menu.pack(side="left", padx=10)

        self.add_btn = ctk.CTkButton(
            header, text="+ Add Task", height=36, fg_color=colors.primary, command=self._open_add_dialog
        )
        self.add_btn.pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

        self.empty_label = ctk.CTkLabel(
            self.list_frame, text="No tasks yet — add your first one!", text_color=colors.text_secondary
        )

    # ------------------------------------------------------------------ #
    # Rendering
    # ------------------------------------------------------------------ #
    def refresh(self) -> None:
        for row in self._rows:
            row.destroy()
        self._rows.clear()
        self.empty_label.pack_forget()

        tasks = self.task_manager.get_tasks(self._current_filter, self._search_query)
        if not tasks:
            self.empty_label.pack(pady=40)
            return

        for task in tasks:
            row = TaskRow(
                self.list_frame,
                task,
                self.theme,
                on_toggle=self._toggle_task,
                on_edit=self._open_edit_dialog,
                on_delete=self._delete_task,
                on_drag_reorder=self._handle_drag_reorder,
            )
            row.pack(fill="x", pady=5, padx=2)
            self._rows.append(row)

    # ------------------------------------------------------------------ #
    # Event handlers
    # ------------------------------------------------------------------ #
    def _on_search_changed(self, _event) -> None:
        self._search_query = self.search_entry.get()
        self.refresh()

    def _on_filter_changed(self, value: str) -> None:
        self._current_filter = TaskFilter(value)
        self.refresh()

    def _open_add_dialog(self) -> None:
        TaskFormDialog(self, self.theme, on_submit=self._handle_add_submit)

    def _handle_add_submit(self, data: dict) -> None:
        self.task_manager.add_task(**data)
        self.refresh()
        self._on_change()

    def _open_edit_dialog(self, task: Task) -> None:
        TaskFormDialog(self, self.theme, on_submit=lambda data: self._handle_edit_submit(task.id, data), task=task)

    def _handle_edit_submit(self, task_id: int, data: dict) -> None:
        self.task_manager.edit_task(task_id, **data)
        self.refresh()
        self._on_change()

    def _toggle_task(self, task_id: int) -> None:
        self.task_manager.toggle_complete(task_id)
        self.refresh()
        self._on_change()

    def _delete_task(self, task_id: int) -> None:
        self.task_manager.delete_task(task_id)
        self.refresh()
        self._on_change()

    def _handle_drag_reorder(self, row: TaskRow, direction: int) -> None:
        try:
            idx = self._rows.index(row)
        except ValueError:
            return
        new_idx = idx + direction
        if not (0 <= new_idx < len(self._rows)):
            return
        self._rows[idx], self._rows[new_idx] = self._rows[new_idx], self._rows[idx]
        for r in self._rows:
            r.pack_forget()
        for r in self._rows:
            r.pack(fill="x", pady=5, padx=2)
        ordered_ids = [r.task.id for r in self._rows]
        self.task_manager.reorder(ordered_ids)

    def _on_theme_changed(self, colors: Palette) -> None:
        self.add_btn.configure(fg_color=colors.primary)
        self.empty_label.configure(text_color=colors.text_secondary)

    def add_task_shortcut(self) -> None:
        """Invoked by the global Ctrl+N shortcut."""
        self._open_add_dialog()
