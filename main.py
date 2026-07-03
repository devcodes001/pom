"""
main.py
FocusFlow entry point. Sets up logging, initializes the database, and
launches the CustomTkinter dashboard window.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from core.database import Database, DEFAULT_DB_PATH
from ui.dashboard import Dashboard

LOG_DIR = Path(__file__).resolve().parent / "logs"


def configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "focusflow.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)

    root_logger = logging.getLogger("focusflow")
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def main() -> None:
    configure_logging()
    logger = logging.getLogger("focusflow.main")
    logger.info("Starting FocusFlow")

    try:
        db = Database(DEFAULT_DB_PATH)
    except Exception:
        logger.exception("Failed to initialize database")
        raise

    try:
        app = Dashboard(db)
        app.mainloop()
    except Exception:
        logger.exception("Unhandled exception in main loop")
        raise
    finally:
        logger.info("FocusFlow shut down")


if __name__ == "__main__":
    main()
