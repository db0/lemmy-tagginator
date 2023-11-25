import time
from tagginator import tagginator
from loguru import logger

if __name__ == "__main__":
    while True:
        logger.info("Running main loop...")
        tagginator()
        logger.info("Retrieving Reports...")
        tagginator.resolve_reports()
        time.sleep(60)
