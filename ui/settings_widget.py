"""
settings_widget.py
Settings panel: theme mode, accent color, Pomodoro/break durations,
alarm sound, auto-start behavior, notifications, and startup toggle.
"""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk
from tkinter import colorchooser

from core.settings import SettingsManager
from ui.theme import Palette, ThemeManager

ACCENT_PRESETS = ["#7C3AED", "#EF4444", "#3B82F6", "#22C55E", "#F59E0B", "#EC4899"]


class LabeledRow(ctk.CTkFrame):
    """A settings row: label on the left, control on the right."""

    def __init__(self, master, theme: ThemeManager, label: str, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme = theme
        colors = theme.colors
        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text=label, text_color=colors.text, anchor="w", font=ctk.CTkFont(size=13))
        self.label.grid(row=0, column=0, sticky="w", pady=10)

        self.theme.subscribe(self._on_theme_changed)

    def _on_theme_changed(self, colors: Palette) -> None:
        self.label.configure(text_color=colors.text)


class SettingsWidget(ctk.CTkScrollableFrame):
    def __init__(
        self,
        master,
        theme: ThemeManager,
        settings_manager: SettingsManager,
        on_theme_toggle: Callable[[str], None],
        on_durations_changed: Callable[[], None],
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme = theme
        self.sm = settings_manager
        self._on_theme_toggle = on_theme_toggle
        self._on_durations_changed = on_durations_changed

        self._build_ui()
        self.theme.subscribe(self._on_theme_changed)

    def _section(self, title: str) -> ctk.CTkFrame:
        colors = self.theme.colors
        card = ctk.CTkFrame(self, corner_radius=16, fg_color=colors.surface)
        card.pack(fill="x", pady=10, padx=2)
        ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(size=15, weight="bold"), text_color=colors.text, anchor="w"
        ).pack(fill="x", padx=20, pady=(16, 4))
        return card

    def _build_ui(self) -> None:
        colors = self.theme.colors
        s = self.sm.settings

        # --- Appearance ---
        appearance_card = self._section("Appearance")

        row = LabeledRow(appearance_card, self.theme, "Theme")
        row.pack(fill="x", padx=20, pady=(0, 4))
        self.theme_switch = ctk.CTkSegmentedButton(
            row, values=["Dark", "Light"], command=self._handle_theme_change
        )
        self.theme_switch.set(s.theme_mode)
        self.theme_switch.grid(row=0, column=1, sticky="e")

        accent_row = LabeledRow(appearance_card, self.theme, "Accent Color")
        accent_row.pack(fill="x", padx=20, pady=(0, 16))
        swatches = ctk.CTkFrame(accent_row, fg_color="transparent")
        swatches.grid(row=0, column=1, sticky="e")
        for i, hex_color in enumerate(ACCENT_PRESETS):
            btn = ctk.CTkButton(
                swatches, text="", width=26, height=26, corner_radius=13,
                fg_color=hex_color, hover_color=hex_color,
                command=lambda c=hex_color: self._handle_accent_change(c),
            )
            btn.grid(row=0, column=i, padx=3)
        custom_btn = ctk.CTkButton(
            swatches, text="＋", width=26, height=26, corner_radius=13,
            fg_color=colors.surface_alt, command=self._pick_custom_color,
        )
        custom_btn.grid(row=0, column=len(ACCENT_PRESETS), padx=3)

        # --- Pomodoro durations ---
        durations_card = self._section("Pomodoro Durations (minutes)")

        self.focus_entry = self._duration_row(durations_card, "Focus", s.focus_minutes)
        self.short_break_entry = self._duration_row(durations_card, "Short Break", s.short_break_minutes)
        self.long_break_entry = self._duration_row(durations_card, "Long Break", s.long_break_minutes)
        self.sessions_entry = self._duration_row(
            durations_card, "Sessions Before Long Break", s.sessions_before_long_break, last=True
        )

        save_btn = ctk.CTkButton(
            durations_card, text="Save Durations", height=36, fg_color=colors.primary,
            command=self._save_durations,
        )
        save_btn.pack(anchor="e", padx=20, pady=(4, 16))

        # --- Behavior ---
        behavior_card = self._section("Behavior")

        self.auto_break_var = ctk.BooleanVar(value=s.auto_start_breaks)
        self._switch_row(behavior_card, "Auto-start Breaks", self.auto_break_var, "auto_start_breaks")

        self.auto_work_var = ctk.BooleanVar(value=s.auto_start_work)
        self._switch_row(behavior_card, "Auto-start Work", self.auto_work_var, "auto_start_work")

        self.notifications_var = ctk.BooleanVar(value=s.notifications_enabled)
        self._switch_row(behavior_card, "Desktop Notifications", self.notifications_var, "notifications_enabled")

        self.startup_var = ctk.BooleanVar(value=s.launch_at_startup)
        self._switch_row(
            behavior_card, "Launch at Startup", self.startup_var, "launch_at_startup", last=True
        )

        # --- Goal ---
        goal_card = self._section("Daily Goal")
        goal_row = LabeledRow(goal_card, self.theme, "Target Pomodoros per Day")
        goal_row.pack(fill="x", padx=20, pady=(0, 16))
        self.goal_entry = ctk.CTkEntry(goal_row, width=80)
        self.goal_entry.insert(0, str(s.daily_goal_pomodoros))
        self.goal_entry.grid(row=0, column=1, sticky="e")
        self.goal_entry.bind("<FocusOut>", self._save_goal)

    def _duration_row(self, parent, label: str, value: int, last: bool = False) -> ctk.CTkEntry:
        row = LabeledRow(parent, self.theme, label)
        row.pack(fill="x", padx=20, pady=(0, 16 if last else 4))
        entry = ctk.CTkEntry(row, width=80)
        entry.insert(0, str(value))
        entry.grid(row=0, column=1, sticky="e")
        return entry

    def _switch_row(self, parent, label: str, var: ctk.BooleanVar, key: str, last: bool = False) -> None:
        row = LabeledRow(parent, self.theme, label)
        row.pack(fill="x", padx=20, pady=(0, 16 if last else 4))
        switch = ctk.CTkSwitch(
            row, text="", variable=var, command=lambda: self.sm.update(**{key: var.get()})
        )
        switch.grid(row=0, column=1, sticky="e")

    # ------------------------------------------------------------------ #
    def _handle_theme_change(self, value: str) -> None:
        self.sm.update(theme_mode=value)
        self._on_theme_toggle(value)

    def _handle_accent_change(self, hex_color: str) -> None:
        self.sm.update(accent_color=hex_color)
        self.theme.set_accent(hex_color)

    def _pick_custom_color(self) -> None:
        color = colorchooser.askcolor(title="Choose accent color")
        if color and color[1]:
            self._handle_accent_change(color[1])

    def _save_durations(self) -> None:
        try:
            focus = int(self.focus_entry.get())
            short_break = int(self.short_break_entry.get())
            long_break = int(self.long_break_entry.get())
            sessions = int(self.sessions_entry.get())
            if min(focus, short_break, long_break, sessions) < 1:
                raise ValueError
        except ValueError:
            return
        self.sm.update(
            focus_minutes=focus,
            short_break_minutes=short_break,
            long_break_minutes=long_break,
            sessions_before_long_break=sessions,
        )
        self._on_durations_changed()

    def _save_goal(self, _event=None) -> None:
        try:
            goal = int(self.goal_entry.get())
            if goal < 1:
                raise ValueError
        except ValueError:
            return
        self.sm.update(daily_goal_pomodoros=goal)

    def _on_theme_changed(self, colors: Palette) -> None:
        for child in self.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                child.configure(fg_color=colors.surface)
