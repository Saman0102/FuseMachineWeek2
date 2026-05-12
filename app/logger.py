import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logger():
    log_format = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(module)s| %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logger = logging.getLogger()
    if getattr(logger, "_is_configured", False):
        return logger
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler("app.log", maxBytes=10**6, backupCount=5)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    logger._is_configured = True
    return logger


def get_logger(name: str) -> logging.Logger:
    setup_logger()
    return logging.getLogger(name)