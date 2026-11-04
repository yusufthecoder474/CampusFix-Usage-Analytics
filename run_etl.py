import argparse
import logging
import sys
import time
from pathlib import Path

from src.etl import load

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "etl.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("campusfix_etl")


def run_with_retries(max_attempts=3, delay_seconds=2):
    for attempt in range(1, max_attempts + 1):
        try:
            logger.info("ETL attempt %s/%s started", attempt, max_attempts)
            result = load()
            logger.info(
                "ETL completed: inserted=%s duplicate=%s quarantined=%s",
                result["inserted"],
                result["duplicate"],
                result["quarantined"],
            )
            return True
        except Exception:
            logger.exception("ETL attempt %s failed", attempt)
            if attempt < max_attempts:
                time.sleep(delay_seconds * attempt)

    logger.error("ETL failed after %s attempts", max_attempts)
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args()

    if args.attempts < 1:
        parser.error("--attempts must be at least 1")

    sys.exit(0 if run_with_retries(args.attempts) else 1)
