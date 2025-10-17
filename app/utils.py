import sys
import logging

def split_fields(datapoint: dict):
    data = {}
    tags = {}
    for field_key in datapoint:
        if field_key in ["date"]:
            continue

        v = datapoint[field_key]
        if type(v) in [int, float]:
            data[field_key] = float(v)
        else:
            tags[field_key] = str(v)

    return data, tags


def setup_logger(name: str = "apple-health", level: int = logging.INFO):
    """Setup and return a configured logger"""
    handler = logging.StreamHandler(sys.stdout)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # Avoid adding multiple handlers if logger already exists
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
