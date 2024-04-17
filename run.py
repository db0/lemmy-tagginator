import time
from tagginator import tagginator
from loguru import logger

if __name__ == "__main__":
    iterations = 0
    while True:
        if iterations >= 60:
            logger.info("Refreshing lemmy auth token...")
            tagginator.lemmy.relog_in()
            iterations = 0
        iterations += 1
        logger.info("Running main loop...")
        tagginator()
        logger.info("Retrieving Reports...")
        tagginator.resolve_reports()
        time.sleep(60)
