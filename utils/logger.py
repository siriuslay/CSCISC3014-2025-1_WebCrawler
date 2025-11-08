import sys
from pathlib import Path
from loguru import logger

def setup_logger():
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", level="INFO", colorize=True)
    logger.add("logs/scraper.log", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}", level="INFO", rotation="500 MB", retention="10 days", compression="zip", encoding="utf-8")
    return logger

log = setup_logger()
