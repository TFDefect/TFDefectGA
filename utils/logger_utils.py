import logging
import sys


def setup_logger():
    """Configure le logger global du projet pour éviter les doublons."""
    logger = logging.getLogger(__name__)

    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
