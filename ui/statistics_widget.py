"""
statistics_widget.py
Statistics dashboard: today/weekly/monthly focus time, completed tasks
and pomodoros, streaks, and three Matplotlib charts (daily/weekly/monthly
productivity) that repaint to match the active theme.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Optional

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from core.database import Database, Session, Task
from ui.theme import Palette, ThemeManager


class StatCard(ctk.CTkFrame):
    def __init__(self, master, theme: ThemeManager, label: str, value: str, **kwargs):
        super().__init__(master, corner_radius=16, **kwargs)
        self.theme = theme
        colors = theme.colors
        self.configure(fg_color=colors.surface)

        self.value_label = ctk.CTkLabel(
            self, text=value, font=ctk.CTkFont(size=26, weight="bold"), text_color=colors.text
        )
        self.value_label.pack(anchor="w", padx=18, pady=(16, 0))

        self.caption_label = ctk.CTkLabel(
            self, text=label, font=ctk.CTkFont(size=12), text_color=colors.text_secondary
        )
        self.caption_label.pack(anchor="w", padx=18, pady=(0, 16))

        self.theme.subscribe(self._on_theme_changed)

    def set_value(self, value: str) -> None:
        self.value_label.configure(text=value)

    def _on_theme_changed(self, colors: Palette) -> None:
        self.configure(fg_color=colors.surface)
        self.value_label.configure(text_color=colors.text)
        self.caption_label.configure(text_color=colors.text_secondary)


class StatisticsWidget(ctk.CTkScrollableFrame):
    def __init__(self, master, theme: ThemeManager, db: Database, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme = theme
        self.db = db
        self._figures: list[tuple[Figure, FigureCanvasTkAgg]] = []

        self._build_ui()
        self.theme.subscribe(self._on_theme_changed)
        self.refresh()

    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)

        self.card_today = StatCard(cards_frame, self.theme, "Today's Focus Time", "0m")
        self.card_today.grid(row=0, column=0, padx=6, sticky="ew")

        self.card_week = StatCard(cards_frame, self.theme, "Weekly Focus Time", "0m")
        self.card_week.grid(row=0, column=1, padx=6, sticky="ew")

        self.card_month = StatCard(cards_frame, self.theme, "Monthly Focus Time", "0m")
        self.card_month.grid(row=0, column=2, padx=6, sticky="ew")

        self.card_streak = StatCard(cards_frame, self.theme, "Current Streak", "0 days")
        self.card_streak.grid(row=0, column=3, padx=6, sticky="ew")

        cards_frame2 = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame2.pack(fill="x", pady=(0, 24))
        for i in range(3):
            cards_frame2.grid_columnconfigure(i, weight=1)

        self.card_tasks = StatCard(cards_frame2, self.theme, "Completed Tasks", "0")
        self.card_tasks.grid(row=0, column=0, padx=6, sticky="ew")

        self.card_pomodoros = StatCard(cards_frame2, self.theme, "Completed Pomodoros", "0")
        self.card_pomodoros.grid(row=0, column=1, padx=6, sticky="ew")

        self.card_longest_streak = StatCard(cards_frame2, self.theme, "Longest Streak", "0 days")
        self.card_longest_streak.grid(row=0, column=2, padx=6, sticky="ew")

        self.charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.charts_frame.pack(fill="both", expand=True)

    # ------------------------------------------------------------------ #
    def refresh(self) -> None:
        sessions = [s for s in self.db.get_all_sessions() if s.session_type == "focus" and s.completed]
        tasks = self.db.get_tasks()

        today = date.today()
        today_minutes = self._minutes_on(sessions, today)
        week_minutes = sum(
            self._minutes_on(sessions, today - timedelta(days=i)) for i in range(7)
        )
        month_minutes = sum(
            self._minutes_on(sessions, today - timedelta(days=i)) for i in range(30)
        )

        self.card_today.set_value(self._fmt_minutes(today_minutes))
        self.card_week.set_value(self._fmt_minutes(week_minutes))
        self.card_month.set_value(self._fmt_minutes(month_minutes))

        completed_tasks = sum(1 for t in tasks if t.completed)
        self.card_tasks.set_value(str(completed_tasks))
        self.card_pomodoros.set_value(str(len(sessions)))

        current_streak, longest_streak = self._compute_streaks(sessions)
        self.card_streak.set_value(f"{current_streak} day{'s' if current_streak != 1 else ''}")
        self.card_longest_streak.set_value(f"{longest_streak} day{'s' if longest_streak != 1 else ''}")

        self._render_charts(sessions)

    @staticmethod
    def _minutes_on(sessions: list[Session], day: date) -> int:
        total = 0
        for s in sessions:
            started = datetime.fromisoformat(s.started_at).date()
            if started == day:
                total += s.duration_minutes
        return total

    @staticmethod
    def _fmt_minutes(total_minutes: int) -> str:
        hours, minutes = divmod(total_minutes, 60)
        if hours:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    @staticmethod
    def _compute_streaks(sessions: list[Session]) -> tuple[int, int]:
        days_with_focus = sorted({datetime.fromisoformat(s.started_at).date() for s in sessions})
        if not days_with_focus:
            return 0, 0

        longest = current = 1
        streaks = [1]
        for prev, curr in zip(days_with_focus, days_with_focus[1:]):
            if (curr - prev).days == 1:
                streaks[-1] += 1
            else:
                streaks.append(1)
        longest = max(streaks)

        today = date.today()
        current = 0
        cursor = today
        day_set = set(days_with_focus)
        # Current streak counts back from today (or yesterday if nothing done yet today)
        if today not in day_set:
            cursor = today - timedelta(days=1)
        while cursor in day_set:
            current += 1
            cursor -= timedelta(days=1)

        return current, longest

    # ------------------------------------------------------------------ #
    # Charts
    # ------------------------------------------------------------------ #
    def _render_charts(self, sessions: list[Session]) -> None:
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        self._figures.clear()

        self._add_chart("Daily Productivity (last 7 days)", *self._daily_series(sessions))
        self._add_chart("Weekly Productivity (last 8 weeks)", *self._weekly_series(sessions))
        self._add_chart("Monthly Productivity (last 12 months)", *self._monthly_series(sessions))

    def _daily_series(self, sessions: list[Session]) -> tuple[list[str], list[int]]:
        today = date.today()
        days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        labels = [d.strftime("%a") for d in days]
        values = [self._minutes_on(sessions, d) for d in days]
        return labels, values

    def _weekly_series(self, sessions: list[Session]) -> tuple[list[str], list[int]]:
        today = date.today()
        buckets: list[int] = []
        labels: list[str] = []
        for w in range(7, -1, -1):
            week_start = today - timedelta(days=today.weekday() + 7 * w)
            total = sum(self._minutes_on(sessions, week_start + timedelta(days=d)) for d in range(7))
            buckets.append(total)
            labels.append(week_start.strftime("%b %d"))
        return labels, buckets

    def _monthly_series(self, sessions: list[Session]) -> tuple[list[str], list[int]]:
        by_month: dict[tuple[int, int], int] = defaultdict(int)
        for s in sessions:
            d = datetime.fromisoformat(s.started_at).date()
            by_month[(d.year, d.month)] += s.duration_minutes

        today = date.today()
        months: list[tuple[int, int]] = []
        y, m = today.year, today.month
        for _ in range(12):
            months.append((y, m))
            m -= 1
            if m == 0:
                m = 12
                y -= 1
        months.reverse()
        labels = [datetime(y, m, 1).strftime("%b") for (y, m) in months]
        values = [by_month.get((y, m), 0) for (y, m) in months]
        return labels, values

    def _add_chart(self, title: str, labels: list[str], values: list[int]) -> None:
        colors = self.theme.colors
        fig = Figure(figsize=(9.5, 2.6), dpi=100)
        fig.patch.set_facecolor(colors.background)
        ax = fig.add_subplot(111)
        ax.set_facecolor(colors.background)

        bar_color = colors.primary
        ax.bar(labels, [v / 60 for v in values], color=bar_color, width=0.55, zorder=3)
        ax.set_title(title, color=colors.text, fontsize=11, loc="left", fontweight="bold")
        ax.set_ylabel("Hours", color=colors.text_secondary, fontsize=9)
        ax.tick_params(colors=colors.text_secondary, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(colors.border)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", color=colors.border, linewidth=0.5, zorder=0)
        fig.tight_layout()

        card = ctk.CTkFrame(self.charts_frame, corner_radius=16, fg_color=colors.surface)
        card.pack(fill="x", pady=8)

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self._figures.append((fig, canvas))

    def _on_theme_changed(self, _colors: Palette) -> None:
        self.refresh()
