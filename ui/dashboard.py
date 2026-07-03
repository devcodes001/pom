"""
dashboard.py
Main application window: top bar (logo/greeting/date/time/theme toggle),
left navigation, and the three main panels (Timer+Goal, Tasks, Statistics,
Settings). Wires the PomodoroEngine, TaskManager, and Notifier together and
marshals all engine callbacks back onto the Tk main thread via `.after()`.
"""

from __future__ import annotations

import logging
import random
from datetime import datetime
from typing import Optional

import customtkinter as ctk

from core.database import Database, Session
from core.notifier import Notifier
from core.pomodoro import PomodoroConfig, PomodoroEngine, SessionType, TimerState
from core.settings import SettingsManager
from core.task_manager import TaskManager
from ui.settings_widget import SettingsWidget
from ui.statistics_widget import StatisticsWidget
from ui.task_widget import TaskWidget
from ui.theme import Palette, ThemeManager
from ui.timer_widget import TimerWidget

logger = logging.getLogger("focusflow.ui.dashboard")

MOTIVATIONAL_QUOTES = [
    "Nice work — one more Pomodoro closer to done.",
    "Small steps, real progress. Keep going.",
    "Focus builds momentum. You've got this.",
    "That's how habits are built — one session at a time.",
    "Great focus! Take a real break before the next one.",
    "Consistency beats intensity. Well done.",
]

NAV_ITEMS = ["Timer", "Tasks", "Statistics", "Settings"]


class Dashboard(ctk.CTk):
    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db
        self.settings_manager = SettingsManager(db)
        s = self.settings_manager.settings

        self.theme = ThemeManager(mode=s.theme_mode, accent_color=s.accent_color)
        self.notifier = Notifier()
        self.task_manager = TaskManager(db)

        self.pomodoro = PomodoroEngine(
            PomodoroConfig(
                focus_minutes=s.focus_minutes,
                short_break_minutes=s.short_break_minutes,
                long_break_minutes=s.long_break_minutes,
                sessions_before_long_break=s.sessions_before_long_break,
            )
        )
        self.pomodoro.on_tick = self._handle_tick
        self.pomodoro.on_session_end = self._handle_session_end
        self.pomodoro.on_session_start = self._handle_session_start

        self._todays_completed_pomodoros = 0
        self._active_panel: Optional[ctk.CTkFrame] = None
        self._panels: dict[str, ctk.CTkFrame] = {}

        self._configure_window()
        self._build_layout()
        self._bind_shortcuts()
        self._show_panel("Timer")
        self._tick_clock()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ #
    # Window setup
    # ------------------------------------------------------------------ #
    def _configure_window(self) -> None:
        self.title("FocusFlow")
        self.geometry("1180x760")
        self.minsize(980, 640)
        colors = self.theme.colors
        self.configure(fg_color=colors.background)
        self._set_window_icon()

    def _set_window_icon(self) -> None:
        """Best-effort window icon load; the app must still run if this fails
        (e.g. missing Pillow/Tk photoimage support on some platforms)."""
        try:
            from pathlib import Path
            from PIL import Image, ImageTk

            icon_path = Path(__file__).resolve().parent.parent / "assets" / "icon.png"
            if icon_path.exists():
                icon_image = ImageTk.PhotoImage(Image.open(icon_path))
                self.iconphoto(False, icon_image)
                self._icon_image_ref = icon_image  # keep a reference alive
        except Exception:
            logger.warning("Could not set window icon", exc_info=True)

    def _build_layout(self) -> None:
        colors = self.theme.colors

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=210, corner_radius=0, fg_color=colors.surface)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        logo_label = ctk.CTkLabel(
            self.sidebar, text="🍅 FocusFlow", font=ctk.CTkFont(size=20, weight="bold"), text_color=colors.text
        )
        logo_label.pack(pady=(28, 30), padx=20, anchor="w")

        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        for item in NAV_ITEMS:
            btn = ctk.CTkButton(
                self.sidebar,
                text=item,
                anchor="w",
                height=42,
                corner_radius=10,
                fg_color="transparent",
                text_color=colors.text_secondary,
                hover_color=colors.surface_alt,
                command=lambda i=item: self._show_panel(i),
            )
            btn.pack(fill="x", padx=14, pady=4)
            self.nav_buttons[item] = btn

        self.goal_tracker_label = ctk.CTkLabel(
            self.sidebar, text="", font=ctk.CTkFont(size=13), text_color=colors.text_secondary, wraplength=180
        )
        self.goal_tracker_label.pack(side="bottom", padx=20, pady=24, anchor="w")

        # --- Main content area ---
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=28, pady=20)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        # Top bar
        top_bar = ctk.CTkFrame(self.main_area, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        top_bar.grid_columnconfigure(0, weight=1)

        self.greeting_label = ctk.CTkLabel(
            top_bar, text=self._greeting_text(), font=ctk.CTkFont(size=22, weight="bold"), text_color=colors.text
        )
        self.greeting_label.grid(row=0, column=0, sticky="w")

        self.datetime_label = ctk.CTkLabel(
            top_bar, text="", font=ctk.CTkFont(size=13), text_color=colors.text_secondary
        )
        self.datetime_label.grid(row=1, column=0, sticky="w")

        self.theme_toggle_btn = ctk.CTkButton(
            top_bar, text=self._theme_icon(), width=42, height=42, corner_radius=21,
            fg_color=colors.surface, hover_color=colors.surface_alt, text_color=colors.text,
            command=self._toggle_theme,
        )
        self.theme_toggle_btn.grid(row=0, column=1, rowspan=2, sticky="e")

        # Panel container
        self.panel_container = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.panel_container.grid(row=1, column=0, sticky="nsew")
        self.panel_container.grid_columnconfigure(0, weight=1)
        self.panel_container.grid_rowconfigure(0, weight=1)

        self._build_panels()
        self.theme.subscribe(self._on_theme_changed)
        self._update_goal_tracker()

    def _build_panels(self) -> None:
        # Timer panel
        timer_panel = ctk.CTkFrame(self.panel_container, fg_color="transparent")
        self.timer_widget = TimerWidget(
            timer_panel,
            self.theme,
            on_start=self._start_timer,
            on_pause=self.pomodoro.pause,
            on_resume=self._resume_timer,
            on_reset=self._reset_timer,
            on_skip=self._skip_timer,
        )
        self.timer_widget.pack(expand=True)
        self.timer_widget.set_state(self.pomodoro.state)
        self.timer_widget.update_tick(self.pomodoro.remaining_seconds, self.pomodoro.total_seconds)
        self._panels["Timer"] = timer_panel

        # Tasks panel
        tasks_panel = ctk.CTkFrame(self.panel_container, fg_color="transparent")
        self.task_widget = TaskWidget(
            tasks_panel, self.theme, self.task_manager, on_change=self._update_goal_tracker
        )
        self.task_widget.pack(fill="both", expand=True)
        self._panels["Tasks"] = tasks_panel

        # Statistics panel
        stats_panel = ctk.CTkFrame(self.panel_container, fg_color="transparent")
        self.statistics_widget = StatisticsWidget(stats_panel, self.theme, self.db)
        self.statistics_widget.pack(fill="both", expand=True)
        self._panels["Statistics"] = stats_panel

        # Settings panel
        settings_panel = ctk.CTkFrame(self.panel_container, fg_color="transparent")
        self.settings_widget = SettingsWidget(
            settings_panel,
            self.theme,
            self.settings_manager,
            on_theme_toggle=self._apply_theme_mode,
            on_durations_changed=self._apply_durations,
        )
        self.settings_widget.pack(fill="both", expand=True)
        self._panels["Settings"] = settings_panel

        for panel in self._panels.values():
            panel.grid(row=0, column=0, sticky="nsew")

    def _bind_shortcuts(self) -> None:
        self.bind("<space>", lambda e: self._handle_space())
        self.bind("<Control-n>", lambda e: self.task_widget.add_task_shortcut())
        self.bind("<Control-N>", lambda e: self.task_widget.add_task_shortcut())
        self.bind("<Control-q>", lambda e: self._on_close())
        self.bind("<Control-Q>", lambda e: self._on_close())
        self.bind("<Control-s>", lambda e: None)  # data auto-saves; reserved for future use
        self.bind("<Control-t>", lambda e: self._toggle_theme())
        self.bind("<Control-T>", lambda e: self._toggle_theme())

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def _show_panel(self, name: str) -> None:
        colors = self.theme.colors
        for item, btn in self.nav_buttons.items():
            active = item == name
            btn.configure(
                fg_color=colors.primary if active else "transparent",
                text_color="#FFFFFF" if active else colors.text_secondary,
            )
        self._panels[name].tkraise()
        if name == "Statistics":
            self.statistics_widget.refresh()
        if name == "Tasks":
            self.task_widget.refresh()

    # ------------------------------------------------------------------ #
    # Timer controls
    # ------------------------------------------------------------------ #
    def _start_timer(self) -> None:
        self.pomodoro.start()
        self.timer_widget.set_state(self.pomodoro.state)

    def _resume_timer(self) -> None:
        self.pomodoro.resume()
        self.timer_widget.set_state(self.pomodoro.state)

    def _reset_timer(self) -> None:
        self.pomodoro.reset()
        self.timer_widget.set_state(self.pomodoro.state)
        self.timer_widget.set_session_type(self.pomodoro.current_session_type)

    def _skip_timer(self) -> None:
        self.pomodoro.skip()

    def _handle_space(self) -> None:
        if self.pomodoro.state == TimerState.RUNNING:
            self.pomodoro.pause()
        elif self.pomodoro.state == TimerState.PAUSED:
            self.pomodoro.resume()
        else:
            self.pomodoro.start()
        self.timer_widget.set_state(self.pomodoro.state)

    # ------------------------------------------------------------------ #
    # Engine callbacks (fired from the background thread -> marshal to Tk)
    # ------------------------------------------------------------------ #
    def _handle_tick(self, remaining: int, total: int) -> None:
        self.after(0, lambda: self.timer_widget.update_tick(remaining, total))

    def _handle_session_start(self, session_type: SessionType) -> None:
        self.after(0, lambda: self.timer_widget.set_session_type(session_type))

    def _handle_session_end(self, finished_type: SessionType, completed_naturally: bool) -> None:
        self.after(0, lambda: self._on_session_end_main_thread(finished_type, completed_naturally))

    def _on_session_end_main_thread(self, finished_type: SessionType, completed_naturally: bool) -> None:
        s = self.settings_manager.settings

        started_at = self.pomodoro.session_started_at or datetime.now()
        self.db.log_session(
            Session(
                id=None,
                session_type=finished_type.value,
                duration_minutes=self.pomodoro.config.minutes_for(finished_type),
                completed=completed_naturally,
                task_id=self.pomodoro.active_task_id,
                started_at=started_at.isoformat(timespec="seconds"),
                ended_at=datetime.now().isoformat(timespec="seconds"),
            )
        )

        if finished_type == SessionType.FOCUS and completed_naturally:
            self._todays_completed_pomodoros += 1
            if self.pomodoro.active_task_id is not None:
                try:
                    self.task_manager.register_pomodoro_completion(self.pomodoro.active_task_id)
                    self.task_widget.refresh()
                except KeyError:
                    logger.warning("Active task no longer exists")

            title = "🍅 Focus Complete"
            message = random.choice(MOTIVATIONAL_QUOTES) + " Time for a break!"
        elif finished_type == SessionType.FOCUS:
            title = "🍅 Focus Session Skipped"
            message = "Moving on to a break."
        else:
            title = "☕ Break Finished"
            message = "Ready to focus again!"

        self.notifier.notify(title, message, enabled=s.notifications_enabled)
        self.notifier.play_alarm(s.alarm_sound, s.alarm_volume, enabled=s.notifications_enabled)

        self.timer_widget.set_state(self.pomodoro.state)
        self.timer_widget.set_session_type(self.pomodoro.current_session_type)
        self.timer_widget.update_tick(self.pomodoro.remaining_seconds, self.pomodoro.total_seconds)
        self._update_goal_tracker()

        auto_start = (
            (self.pomodoro.current_session_type != SessionType.FOCUS and s.auto_start_breaks)
            or (self.pomodoro.current_session_type == SessionType.FOCUS and s.auto_start_work)
        )
        if auto_start:
            self.pomodoro.start(task_id=self.pomodoro.active_task_id)
            self.timer_widget.set_state(self.pomodoro.state)

    # ------------------------------------------------------------------ #
    # Theme
    # ------------------------------------------------------------------ #
    def _toggle_theme(self) -> None:
        new_mode = self.theme.toggle()
        self.settings_manager.update(theme_mode=new_mode)
        self.theme_toggle_btn.configure(text=self._theme_icon())

    def _apply_theme_mode(self, mode: str) -> None:
        self.theme.set_mode(mode)
        self.theme_toggle_btn.configure(text=self._theme_icon())

    def _theme_icon(self) -> str:
        return "🌙" if self.theme.mode == "Dark" else "☀️"

    def _apply_durations(self) -> None:
        s = self.settings_manager.settings
        self.pomodoro.config.focus_minutes = s.focus_minutes
        self.pomodoro.config.short_break_minutes = s.short_break_minutes
        self.pomodoro.config.long_break_minutes = s.long_break_minutes
        self.pomodoro.config.sessions_before_long_break = s.sessions_before_long_break
        if self.pomodoro.state == TimerState.IDLE:
            self.pomodoro.reset()
            self.timer_widget.update_tick(self.pomodoro.remaining_seconds, self.pomodoro.total_seconds)

    def _on_theme_changed(self, colors: Palette) -> None:
        self.configure(fg_color=colors.background)
        self.sidebar.configure(fg_color=colors.surface)
        self.greeting_label.configure(text_color=colors.text)
        self.datetime_label.configure(text_color=colors.text_secondary)
        self.theme_toggle_btn.configure(fg_color=colors.surface, hover_color=colors.surface_alt, text_color=colors.text)
        self.goal_tracker_label.configure(text_color=colors.text_secondary)
        self._show_panel(self._current_panel_name())

    def _current_panel_name(self) -> str:
        for name, panel in self._panels.items():
            if panel.winfo_ismapped() or panel.winfo_viewable():
                return name
        return "Timer"

    # ------------------------------------------------------------------ #
    # Misc UI helpers
    # ------------------------------------------------------------------ #
    def _greeting_text(self) -> str:
        hour = datetime.now().hour
        name = self.settings_manager.settings.user_name
        if hour < 12:
            period = "morning"
        elif hour < 18:
            period = "afternoon"
        else:
            period = "evening"
        return f"Good {period}, {name}"

    def _tick_clock(self) -> None:
        now = datetime.now()
        self.datetime_label.configure(text=now.strftime("%A, %B %d, %Y   •   %I:%M:%S %p"))
        self.after(1000, self._tick_clock)

    def _update_goal_tracker(self) -> None:
        s = self.settings_manager.settings
        goal = max(1, s.daily_goal_pomodoros)
        done = min(self._todays_completed_pomodoros, goal)
        filled = "🍅" * done
        empty = "○" * (goal - done)
        self.goal_tracker_label.configure(text=f"Daily Goal: {done}/{goal}\n{filled}{empty}")

    # ------------------------------------------------------------------ #
    def _on_close(self) -> None:
        try:
            self.pomodoro.shutdown()
        finally:
            self.db.close()
            self.destroy()
