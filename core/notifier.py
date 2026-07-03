"""
notifier.py
Desktop notification + alarm sound playback, isolated behind a small
interface so the UI never has to deal with plyer/pygame quirks or
platform-specific failures directly.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("focusflow.notifier")

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


class Notifier:
    """Wraps plyer (desktop toast notifications) and pygame (alarm sound)."""

    def __init__(self) -> None:
        self._mixer_ready = False
        try:
            import pygame

            pygame.mixer.init()
            self._mixer_ready = True
        except Exception as exc:  # pragma: no cover - depends on audio hardware
            logger.warning("Audio mixer unavailable, sounds will be skipped: %s", exc)

    def notify(self, title: str, message: str, enabled: bool = True) -> None:
        if not enabled:
            return
        try:
            from plyer import notification

            notification.notify(
                title=title,
                message=message,
                app_name="FocusFlow",
                timeout=6,
            )
        except Exception as exc:  # pragma: no cover - depends on OS notification backend
            logger.warning("Desktop notification failed: %s", exc)

    def play_alarm(self, filename: str, volume: float = 0.8, enabled: bool = True) -> None:
        if not enabled or not self._mixer_ready:
            return
        path = self._resolve_sound_path(filename)
        if path is None:
            logger.warning("Alarm sound file not found: %s", filename)
            return
        try:
            import pygame

            sound = pygame.mixer.Sound(str(path))
            sound.set_volume(max(0.0, min(1.0, volume)))
            sound.play()
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to play alarm sound: %s", exc)

    @staticmethod
    def _resolve_sound_path(filename: str) -> Optional[Path]:
        candidate = ASSETS_DIR / filename
        if candidate.exists():
            return candidate
        default = ASSETS_DIR / "notification.wav"
        return default if default.exists() else None
