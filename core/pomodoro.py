"""
pomodoro.py
Session-state machine and background timer thread for the Pomodoro technique.

Design notes:
- The timer runs on a daemon thread and ticks once per second, but computes
  remaining time from a wall-clock deadline (time.monotonic) rather than by
  counting down an integer. This means the displayed time stays accurate
  even if the system briefly stalls or a tick is delayed -- it never drifts.
- All communication back to the UI happens through callbacks. The engine
  itself has zero Tkinter/CustomTkinter imports, so it is independently
  testable and reusable.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger("focusflow.pomodoro")


class SessionType(str, Enum):
    FOCUS = "focus"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class TimerState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"


@dataclass
class PomodoroConfig:
    focus_minutes: int = 25
    short_break_minutes: int = 5
    long_break_minutes: int = 15
    sessions_before_long_break: int = 4

    def minutes_for(self, session_type: SessionType) -> int:
        return {
            SessionType.FOCUS: self.focus_minutes,
            SessionType.SHORT_BREAK: self.short_break_minutes,
            SessionType.LONG_BREAK: self.long_break_minutes,
        }[session_type]


# Callback signatures -------------------------------------------------------
TickCallback = Callable[[int, int], None]                 # (remaining_seconds, total_seconds)
SessionEndCallback = Callable[[SessionType, bool], None]   # (finished_type, completed_naturally)
SessionStartCallback = Callable[[SessionType], None]


class PomodoroEngine:
    """Drives one Pomodoro session at a time on a background thread."""

    def __init__(self, config: PomodoroConfig) -> None:
        self.config = config
        self.state: TimerState = TimerState.IDLE
        self.current_session_type: SessionType = SessionType.FOCUS
        self.completed_focus_sessions: int = 0
        self.active_task_id: Optional[int] = None

        self._total_seconds: int = self.config.minutes_for(self.current_session_type) * 60
        self._remaining_seconds: int = self._total_seconds
        self._deadline: Optional[float] = None       # time.monotonic() when timer hits 0
        self._session_started_at: Optional[datetime] = None

        self._thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        self._lock = threading.RLock()

        self.on_tick: Optional[TickCallback] = None
        self.on_session_start: Optional[SessionStartCallback] = None
        self.on_session_end: Optional[SessionEndCallback] = None

    # ------------------------------------------------------------------ #
    # Public controls
    # ------------------------------------------------------------------ #
    def start(self, task_id: Optional[int] = None) -> None:
        with self._lock:
            if self.state == TimerState.RUNNING:
                return
            self.active_task_id = task_id
            self._total_seconds = self.config.minutes_for(self.current_session_type) * 60
            if self.state == TimerState.IDLE:
                self._remaining_seconds = self._total_seconds
                self._session_started_at = datetime.now()
                if self.on_session_start:
                    self.on_session_start(self.current_session_type)
            self._deadline = time.monotonic() + self._remaining_seconds
            self.state = TimerState.RUNNING
            self._launch_thread()
            logger.info("Timer started: %s (%ss)", self.current_session_type, self._remaining_seconds)

    def pause(self) -> None:
        with self._lock:
            if self.state != TimerState.RUNNING:
                return
            self._remaining_seconds = max(0, round(self._deadline - time.monotonic()))
            self.state = TimerState.PAUSED
            self._stop_flag.set()
            logger.info("Timer paused at %ss remaining", self._remaining_seconds)

    def resume(self) -> None:
        with self._lock:
            if self.state != TimerState.PAUSED:
                return
            self._deadline = time.monotonic() + self._remaining_seconds
            self.state = TimerState.RUNNING
            self._launch_thread()
            logger.info("Timer resumed with %ss remaining", self._remaining_seconds)

    def reset(self) -> None:
        with self._lock:
            self._stop_flag.set()
            self.state = TimerState.IDLE
            self._total_seconds = self.config.minutes_for(self.current_session_type) * 60
            self._remaining_seconds = self._total_seconds
            self._deadline = None
            if self.on_tick:
                self.on_tick(self._remaining_seconds, self._total_seconds)
            logger.info("Timer reset")

    def skip(self) -> None:
        """Immediately end the current session as if it finished naturally=False."""
        with self._lock:
            self._stop_flag.set()
            self._finish_session(completed_naturally=False)
            logger.info("Session skipped: %s", self.current_session_type)

    def shutdown(self) -> None:
        """Call on app exit to cleanly stop the background thread."""
        self._stop_flag.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    # ------------------------------------------------------------------ #
    # Internal thread loop
    # ------------------------------------------------------------------ #
    def _launch_thread(self) -> None:
        self._stop_flag.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self) -> None:
        while not self._stop_flag.is_set():
            with self._lock:
                if self.state != TimerState.RUNNING or self._deadline is None:
                    return
                remaining = max(0, round(self._deadline - time.monotonic()))
                self._remaining_seconds = remaining
                total = self._total_seconds
            if self.on_tick:
                self.on_tick(remaining, total)
            if remaining <= 0:
                self._finish_session(completed_naturally=True)
                return
            time.sleep(1.0)

    # ------------------------------------------------------------------ #
    # Session transitions
    # ------------------------------------------------------------------ #
    def _finish_session(self, completed_naturally: bool) -> None:
        finished_type = self.current_session_type
        self.state = TimerState.IDLE

        if finished_type == SessionType.FOCUS and completed_naturally:
            self.completed_focus_sessions += 1

        if self.on_session_end:
            self.on_session_end(finished_type, completed_naturally)

        self.current_session_type = self._next_session_type(finished_type, completed_naturally)
        self._total_seconds = self.config.minutes_for(self.current_session_type) * 60
        self._remaining_seconds = self._total_seconds
        self._deadline = None
        if self.on_tick:
            self.on_tick(self._remaining_seconds, self._total_seconds)

    def _next_session_type(self, finished: SessionType, completed_naturally: bool) -> SessionType:
        if finished == SessionType.FOCUS:
            if not completed_naturally:
                return SessionType.SHORT_BREAK
            if self.completed_focus_sessions % self.config.sessions_before_long_break == 0:
                return SessionType.LONG_BREAK
            return SessionType.SHORT_BREAK
        return SessionType.FOCUS

    # ------------------------------------------------------------------ #
    # Introspection helpers (used by UI to render mm:ss)
    # ------------------------------------------------------------------ #
    @property
    def remaining_seconds(self) -> int:
        with self._lock:
            if self.state == TimerState.RUNNING and self._deadline is not None:
                return max(0, round(self._deadline - time.monotonic()))
            return self._remaining_seconds

    @property
    def total_seconds(self) -> int:
        return self._total_seconds

    @property
    def session_started_at(self) -> Optional[datetime]:
        return self._session_started_at

    @staticmethod
    def format_time(seconds: int) -> str:
        minutes, secs = divmod(max(0, seconds), 60)
        return f"{minutes:02d}:{secs:02d}"
