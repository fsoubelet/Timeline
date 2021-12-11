import sys

from loguru import logger

LOGURU_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


def assert_input_validity(in_json: dict) -> None:
    if "width" not in in_json:
        logger.error("Required 'width' key not found in input json")
    if "start" not in in_json:
        logger.error("Required 'start' key not found in input json")
    if "end" not in in_json:
        logger.error("Required 'end' key not found in input json")


def config_logger(level: str = "INFO", **kwargs) -> None:
    """
    Resets the logger object from loguru, with `sys.stdout` as a sink and the aforedefined format.
    This comes down to personnal preference.
    Any additional keyword argument used is transmitted to the `logger.add` call.
    """
    logger.remove()
    logger.add(sys.stdout, format=LOGURU_FORMAT, level=level.upper(), **kwargs)
