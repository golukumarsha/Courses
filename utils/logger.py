"""
utils/logger.py
CourseVault — Centralized Logging Setup
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime

# ─── Logs folder banao ────────────────────────────────
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ─── Log file paths ───────────────────────────────────
LOG_FILE_ALL = os.path.join(LOG_DIR, "app.log")        # Saare logs
LOG_FILE_ERROR = os.path.join(LOG_DIR, "error.log")      # Sirf errors
LOG_FILE_ACCESS = os.path.join(LOG_DIR, "access.log")     # Request logs

# ─── Custom Formatter ─────────────────────────────────


class CustomFormatter(logging.Formatter):
    """Color + structured format"""

    COLORS = {
        logging.DEBUG:    "\033[36m",   # Cyan
        logging.INFO:     "\033[32m",   # Green
        logging.WARNING:  "\033[33m",   # Yellow
        logging.ERROR:    "\033[31m",   # Red
        logging.CRITICAL: "\033[35m",   # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        record.levelname = f"{color}{record.levelname:<8}{self.RESET}"
        return super().format(record)


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """
    Har module ke liye logger banao.
    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Kuch hua")
        logger.error("Kuch galat hua")
    """
    logger = logging.getLogger(name)

    # Already configured hai toh dobara mat karo
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ── 1. Console Handler (colored) ──────────────────
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)
    console.setFormatter(CustomFormatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
    logger.addHandler(console)

    # ── 2. app.log — rotating file (saare logs) ───────
    file_all = logging.handlers.RotatingFileHandler(
        LOG_FILE_ALL,
        maxBytes=5 * 1024 * 1024,   # 5 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_all.setLevel(logging.DEBUG)
    file_all.setFormatter(logging.Formatter(
        LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
    logger.addHandler(file_all)

    # ── 3. error.log — sirf WARNING aur upar ─────────
    file_err = logging.handlers.RotatingFileHandler(
        LOG_FILE_ERROR,
        maxBytes=2 * 1024 * 1024,   # 2 MB
        backupCount=3,
        encoding="utf-8"
    )
    file_err.setLevel(logging.WARNING)
    file_err.setFormatter(logging.Formatter(
        LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
    logger.addHandler(file_err)

    return logger


# ─── Access Logger (request logs) ────────────────────
def get_access_logger() -> logging.Logger:
    """Sirf HTTP request/response logs ke liye"""
    logger = logging.getLogger("access")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    file_access = logging.handlers.RotatingFileHandler(
        LOG_FILE_ACCESS,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=7,
        encoding="utf-8"
    )
    fmt = "%(asctime)s | %(message)s"
    file_access.setFormatter(logging.Formatter(fmt, datefmt=LOG_DATE_FORMAT))
    logger.addHandler(file_access)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(fmt, datefmt=LOG_DATE_FORMAT))
    logger.addHandler(console)

    return logger
