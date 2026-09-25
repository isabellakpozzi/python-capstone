import logging
import sys

def setup_logging():
    logger = logging.getLogger("rag_system")
    logger.setLevel(logging.INFO)

    if not logger.handlers: 
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"event": "%(message)s"}'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

logger = setup_logging()