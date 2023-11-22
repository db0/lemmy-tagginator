import time
from tagginator import tagginator
from loguru import logger

if __name__ == "__main__":
    while True:
        logger.info("Running loop.")
        tagginator()
        time.sleep(60)
