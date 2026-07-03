# 🍅 FocusFlow

A modern desktop Pomodoro timer and task manager, built with Python and CustomTkinter.
Features a Notion/Linear/Spotify-inspired UI with full **light and dark theme** support.

![Python](https://img.shields.io/badge/python-3.12+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- **Pomodoro Timer** — animated circular progress ring, accurate wall-clock timing on a
  background thread (never freezes the UI), auto long-break every 4th session, fully
  configurable durations.
- **Task Manager** — add/edit/delete, priority levels, deadlines, estimated vs. completed
  Pomodoros, drag-to-reorder, search, and filtering (All / Pending / Completed).
- **Light & Dark Theme** — one-click toggle in the top bar (or `Ctrl+T`), persisted between
  launches, with a customizable accent color. Every screen — including the Matplotlib
  charts — repaints instantly to match.
- **Statistics** — today/weekly/monthly focus time, completed tasks & Pomodoros, current and
  longest streaks, plus daily/weekly/monthly productivity charts.
- **Desktop Notifications & Alarm Sound** — via `plyer` and `pygame`.
- **Daily Goal Tracker** — visual Pomodoro progress in the sidebar (e.g. `🍅🍅🍅🍅○○○○`).
- **SQLite Persistence** — tasks, sessions, and settings are saved automatically and restored
  on every launch.
- **Keyboard Shortcuts** — see below.

## Project Structure

```
FocusFlow/
├── main.py                  # entry point
├── ui/
│   ├── dashboard.py          # main window, navigation, wiring
│   ├── timer_widget.py       # circular Pomodoro timer
│   ├── task_widget.py        # task list + add/edit dialog
│   ├── statistics_widget.py  # stat cards + Matplotlib charts
│   ├── settings_widget.py    # settings panel
│   └── theme.py               # light/dark palettes + ThemeManager
├── core/
│   ├── pomodoro.py            # timer state machine (thread-safe, no UI deps)
│   ├── database.py            # SQLite access layer
│   ├── task_manager.py        # task CRUD/business logic
│   ├── settings.py            # typed settings wrapper
│   └── notifier.py            # desktop notification + alarm sound
├── assets/
│   ├── icon.png
│   └── notification.wav
├── database/
│   └── focusflow.db           # created automatically on first run
├── logs/
│   └── focusflow.log          # created automatically on first run
├── requirements.txt
└── README.md
```

## Installation

1. Install Python 3.12 or newer.
2. From the `FocusFlow/` directory, install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   > **Linux users:** if `tkinter` is not already installed, run
   > `sudo apt-get install python3-tk` first (it ships with the standard Python installer
   > on Windows and macOS).

3. Run the app:

   ```bash
   python main.py
   ```

On first launch, FocusFlow creates `database/focusflow.db` and `logs/focusflow.log`
automatically — no manual setup required.

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Space` | Start / Pause / Resume timer |
| `Ctrl+N` | New task |
| `Ctrl+T` | Toggle light/dark theme |
| `Ctrl+Q` | Quit |

## Building a Windows Executable

FocusFlow is PyInstaller-compatible. From the `FocusFlow/` directory:

```bash
pyinstaller --name FocusFlow ^
  --windowed ^
  --icon assets/icon.png ^
  --add-data "assets;assets" ^
  main.py
```

*(On macOS/Linux, replace `assets;assets` with `assets:assets` and drop the `^` line
continuations — use `\` instead, or put it all on one line.)*

The executable will be created at `dist/FocusFlow/FocusFlow.exe`. The `database/` and
`logs/` folders will be created next to the executable the first time it runs.

**Note:** because the SQLite database and log files are created relative to the
application at runtime, keep `FocusFlow.exe` inside its own `dist/FocusFlow/` folder
rather than moving just the `.exe` file elsewhere.

## Customization

All defaults (theme, accent color, durations, notifications, daily goal, etc.) live in
the **Settings** tab and are persisted to SQLite — no code changes needed for day-to-day
tweaks. Advanced defaults (e.g. the starting accent presets) can be edited in
`ui/settings_widget.py` (`ACCENT_PRESETS`) and `core/database.py` (`DEFAULT_SETTINGS`).

## Architecture Notes

- **`PomodoroEngine`** (`core/pomodoro.py`) has zero UI dependencies and runs on a daemon
  thread, computing remaining time from a `time.monotonic()` deadline rather than counting
  down an integer — so it never visibly drifts even under system load. UI callbacks are
  marshalled back onto the Tk main thread via `.after(0, ...)`.
- **`ThemeManager`** (`ui/theme.py`) is the single source of truth for colors. Every widget
  subscribes to it and repaints on theme change — no widget hardcodes a color.
- **`Database`** (`core/database.py`) is the only module that opens a SQLite connection;
  all other modules go through `TaskManager` or `SettingsManager`.

## License

MIT — use it, fork it, ship it.
