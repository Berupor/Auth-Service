import logging
import os
import sys

import psycopg2


FLASK_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, FLASK_DIR)

from src.core.config import settings
from src.tools.backoff import backoff


logger = logging.getLogger(__name__)


@backoff(logger=logger, max_attempt_count=50)
def ping_psql():
    try:
        psycopg2.connect(**settings.postgres.dict())
        logger.info("*********** Successfully connected to database")

    except psycopg2.DatabaseError:
        logger.error("************ Failed to connect to database")
        raise ConnectionError()


if __name__ == "__main__":
    ping_psql()
