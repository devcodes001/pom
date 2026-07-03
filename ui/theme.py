"""
theme.py
Single source of truth for color palettes. Every widget in ui/ pulls its
colors from ThemeManager.colors so that toggling Dark/Light repaints the
whole app consistently without restarting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

import customtkinter as ctk

ThemeMode = Literal["Dark", "Light"]


@dataclass(frozen=True)
class Palette:
    background: str
    surface: str            # card background
    surface_alt: str        # slightly raised/alternate card
    primary: str             # accent (customizable)
    secondary: str           # secondary accent (red)
    text: str
    text_secondary: str
    border: str
    success: str
    warning: str
    high_priority: str
    medium_priority: str
    low_priority: str


DARK_PALETTE = Palette(
    background="#18181B",
    surface="#27272A",
    surface_alt="#303035",
    primary="#7C3AED",
    secondary="#EF4444",
    text="#FFFFFF",
    text_secondary="#A1A1AA",
    border="#3F3F46",
    success="#22C55E",
    warning="#F59E0B",
    high_priority="#EF4444",
    medium_priority="#F59E0B",
    low_priority="#22C55E",
)

LIGHT_PALETTE = Palette(
    background="#FAFAFA",
    surface="#FFFFFF",
    surface_alt="#F4F4F5",
    primary="#7C3AED",
    secondary="#EF4444",
    text="#18181B",
    text_secondary="#52525B",
    border="#E4E4E7",
    success="#16A34A",
    warning="#D97706",
    high_priority="#DC2626",
    medium_priority="#D97706",
    low_priority="#16A34A",
)

FONT_FAMILY = "Segoe UI"


class ThemeManager:
    """Holds the active palette and notifies subscribed widgets when it changes."""

    def __init__(self, mode: ThemeMode = "Dark", accent_color: str | None = None) -> None:
        self._mode: ThemeMode = mode
        self._accent_override = accent_color
        self._subscribers: list[Callable[[Palette], None]] = []
        self._apply_ctk_mode()

    @property
    def mode(self) -> ThemeMode:
        return self._mode

    @property
    def colors(self) -> Palette:
        base = DARK_PALETTE if self._mode == "Dark" else LIGHT_PALETTE
        if self._accent_override:
            base = Palette(**{**base.__dict__, "primary": self._accent_override})
        return base

    def _apply_ctk_mode(self) -> None:
        ctk.set_appearance_mode("dark" if self._mode == "Dark" else "light")

    def set_mode(self, mode: ThemeMode) -> None:
        if mode == self._mode:
            return
        self._mode = mode
        self._apply_ctk_mode()
        self._notify()

    def toggle(self) -> ThemeMode:
        self.set_mode("Light" if self._mode == "Dark" else "Dark")
        return self._mode

    def set_accent(self, hex_color: str) -> None:
        self._accent_override = hex_color
        self._notify()

    def subscribe(self, callback: Callable[[Palette], None]) -> None:
        """Widgets register a redraw callback so they repaint on theme change."""
        self._subscribers.append(callback)

    def _notify(self) -> None:
        colors = self.colors
        for callback in list(self._subscribers):
            try:
                callback(colors)
            except Exception:
                # A single misbehaving widget shouldn't break the whole app's
                # theme switch; log and continue notifying the rest.
                import logging

                logging.getLogger("focusflow.theme").exception(
                    "Theme subscriber raised an exception"
                )

    def priority_color(self, priority: str) -> str:
        c = self.colors
        return {
            "High": c.high_priority,
            "Medium": c.medium_priority,
            "Low": c.low_priority,
        }.get(priority, c.text_secondary)
