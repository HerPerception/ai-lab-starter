import logging
import os


def configure_logging(level: str | None = None) -> logging.Logger:
    """Configure and return the package logger using AILAB_LOG_LEVEL (default: WARNING)."""
    chosen_level = (level or os.environ.get("AILAB_LOG_LEVEL", "WARNING")).upper()
    numeric_level = getattr(logging, chosen_level, logging.WARNING)

    logger = logging.getLogger("ailab")
    logger.setLevel(numeric_level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
