"""
settings.py
Typed convenience wrapper around Database settings so the rest of the
app never has to think about string<->type conversion or key names.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from core.database import Database, DEFAULT_SETTINGS

logger = logging.getLogger("focusflow.settings")


@dataclass
class AppSettings:
    """In-memory snapshot of user settings, backed by the database."""

    theme_mode: str = "Dark"
    accent_color: str = "#7C3AED"
    focus_minutes: int = 25
    short_break_minutes: int = 5
    long_break_minutes: int = 15
    sessions_before_long_break: int = 4
    auto_start_breaks: bool = True
    auto_start_work: bool = False
    notifications_enabled: bool = True
    alarm_sound: str = "notification.wav"
    alarm_volume: float = 0.8
    launch_at_startup: bool = False
    daily_goal_pomodoros: int = 8
    user_name: str = "there"


class SettingsManager:
    """Loads settings from the database and persists changes back to it."""

    def __init__(self, db: Database) -> None:
        self._db = db
        self.settings = self._load()

    def _load(self) -> AppSettings:
        raw = {**DEFAULT_SETTINGS, **self._db.get_all_settings()}
        try:
            return AppSettings(
                theme_mode=raw["theme_mode"],
                accent_color=raw["accent_color"],
                focus_minutes=int(raw["focus_minutes"]),
                short_break_minutes=int(raw["short_break_minutes"]),
                long_break_minutes=int(raw["long_break_minutes"]),
                sessions_before_long_break=int(raw["sessions_before_long_break"]),
                auto_start_breaks=raw["auto_start_breaks"] == "1",
                auto_start_work=raw["auto_start_work"] == "1",
                notifications_enabled=raw["notifications_enabled"] == "1",
                alarm_sound=raw["alarm_sound"],
                alarm_volume=float(raw["alarm_volume"]),
                launch_at_startup=raw["launch_at_startup"] == "1",
                daily_goal_pomodoros=int(raw["daily_goal_pomodoros"]),
                user_name=raw["user_name"],
            )
        except (KeyError, ValueError) as exc:
            logger.warning("Corrupt settings detected (%s); falling back to defaults", exc)
            return AppSettings()

    def update(self, **kwargs) -> None:
        """Update one or more settings in memory and persist them."""
        for key, value in kwargs.items():
            if not hasattr(self.settings, key):
                raise AttributeError(f"Unknown setting: {key}")
            setattr(self.settings, key, value)
            db_value = "1" if isinstance(value, bool) and value else (
                "0" if isinstance(value, bool) else value
            )
            self._db.set_setting(key, db_value)
        logger.debug("Settings updated: %s", kwargs)

    def reload(self) -> AppSettings:
        self.settings = self._load()
        return self.settings
