"""
timer_widget.py
Large circular Pomodoro timer with Start/Pause/Resume/Reset/Skip controls.
Draws the progress ring on a Canvas (kept in sync with the theme palette)
and receives tick updates from PomodoroEngine via the dashboard's callbacks
-- this widget never touches the engine's thread directly.
"""

from __future__ import annotations

import math
import tkinter as tk
from typing import Callable, Optional

import customtkinter as ctk

from core.pomodoro import SessionType, TimerState
from ui.theme import Palette, ThemeManager

SESSION_LABELS = {
    SessionType.FOCUS: "🍅  Focus Session",
    SessionType.SHORT_BREAK: "☕  Short Break",
    SessionType.LONG_BREAK: "🌙  Long Break",
}

RING_SIZE = 320
RING_THICKNESS = 14


class TimerWidget(ctk.CTkFrame):
    def __init__(
        self,
        master,
        theme: ThemeManager,
        on_start: Callable[[], None],
        on_pause: Callable[[], None],
        on_resume: Callable[[], None],
        on_reset: Callable[[], None],
        on_skip: Callable[[], None],
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme = theme
        self._on_start = on_start
        self._on_pause = on_pause
        self._on_resume = on_resume
        self._on_reset = on_reset
        self._on_skip = on_skip

        self._state: TimerState = TimerState.IDLE
        self._session_type: SessionType = SessionType.FOCUS
        self._progress_fraction: float = 0.0  # 0..1, elapsed portion

        self._build_ui()
        self.theme.subscribe(self._on_theme_changed)

    # ------------------------------------------------------------------ #
    # Layout
    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        colors = self.theme.colors

        self.session_label = ctk.CTkLabel(
            self,
            text=SESSION_LABELS[self._session_type],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=colors.text_secondary,
        )
        self.session_label.pack(pady=(0, 12))

        self.canvas = tk.Canvas(
            self,
            width=RING_SIZE,
            height=RING_SIZE,
            highlightthickness=0,
            bg=colors.background,
        )
        self.canvas.pack()

        self.time_text_id = None
        self._draw_ring()

        button_row = ctk.CTkFrame(self, fg_color="transparent")
        button_row.pack(pady=(20, 0))

        self.start_btn = ctk.CTkButton(
            button_row,
            text="▶  Start",
            width=110,
            height=42,
            corner_radius=21,
            fg_color=colors.primary,
            hover_color=self._darken(colors.primary),
            command=self._handle_primary_button,
        )
        self.start_btn.grid(row=0, column=0, padx=6)

        self.reset_btn = ctk.CTkButton(
            button_row,
            text="↺  Reset",
            width=110,
            height=42,
            corner_radius=21,
            fg_color=colors.surface_alt,
            hover_color=colors.border,
            text_color=colors.text,
            command=self._on_reset,
        )
        self.reset_btn.grid(row=0, column=1, padx=6)

        self.skip_btn = ctk.CTkButton(
            button_row,
            text="⏭  Skip",
            width=110,
            height=42,
            corner_radius=21,
            fg_color=colors.surface_alt,
            hover_color=colors.border,
            text_color=colors.text,
            command=self._on_skip,
        )
        self.skip_btn.grid(row=0, column=2, padx=6)

    # ------------------------------------------------------------------ #
    # Public API (called by dashboard)
    # ------------------------------------------------------------------ #
    def update_tick(self, remaining_seconds: int, total_seconds: int) -> None:
        self._progress_fraction = 0.0 if total_seconds == 0 else 1 - (remaining_seconds / total_seconds)
        self._draw_ring(remaining_seconds)

    def set_state(self, state: TimerState) -> None:
        self._state = state
        label_map = {
            TimerState.IDLE: "▶  Start",
            TimerState.RUNNING: "⏸  Pause",
            TimerState.PAUSED: "▶  Resume",
        }
        self.start_btn.configure(text=label_map[state])

    def set_session_type(self, session_type: SessionType) -> None:
        self._session_type = session_type
        self.session_label.configure(text=SESSION_LABELS[session_type])
        self._draw_ring()

    # ------------------------------------------------------------------ #
    # Internal
    # ------------------------------------------------------------------ #
    def _handle_primary_button(self) -> None:
        if self._state == TimerState.IDLE:
            self._on_start()
        elif self._state == TimerState.RUNNING:
            self._on_pause()
        elif self._state == TimerState.PAUSED:
            self._on_resume()

    def _draw_ring(self, remaining_seconds: Optional[int] = None) -> None:
        colors = self.theme.colors
        self.canvas.configure(bg=colors.background)
        self.canvas.delete("all")

        pad = RING_THICKNESS
        x0, y0 = pad, pad
        x1, y1 = RING_SIZE - pad, RING_SIZE - pad

        # Track (background ring)
        self.canvas.create_oval(
            x0, y0, x1, y1,
            outline=colors.surface_alt,
            width=RING_THICKNESS,
        )

        # Progress arc: starts at 12 o'clock, sweeps clockwise
        extent = -360 * self._progress_fraction
        ring_color = colors.secondary if self._session_type == SessionType.FOCUS else colors.success
        if self._progress_fraction > 0:
            self.canvas.create_arc(
                x0, y0, x1, y1,
                start=90,
                extent=extent,
                style=tk.ARC,
                outline=ring_color,
                width=RING_THICKNESS,
            )

        display_seconds = remaining_seconds if remaining_seconds is not None else 0
        from core.pomodoro import PomodoroEngine  # local import avoids UI<->core cycle at module load

        self.canvas.create_text(
            RING_SIZE / 2,
            RING_SIZE / 2,
            text=PomodoroEngine.format_time(display_seconds),
            font=(self._font_family(), 52, "bold"),
            fill=colors.text,
        )

    @staticmethod
    def _font_family() -> str:
        return "Segoe UI"

    @staticmethod
    def _darken(hex_color: str, factor: float = 0.85) -> str:
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        r, g, b = (max(0, int(c * factor)) for c in (r, g, b))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _on_theme_changed(self, colors: Palette) -> None:
        self.session_label.configure(text_color=colors.text_secondary)
        self.reset_btn.configure(fg_color=colors.surface_alt, hover_color=colors.border, text_color=colors.text)
        self.skip_btn.configure(fg_color=colors.surface_alt, hover_color=colors.border, text_color=colors.text)
        self.start_btn.configure(fg_color=colors.primary, hover_color=self._darken(colors.primary))
        self._draw_ring()
