from loguru import logger


def assert_input_validity(in_json: dict) -> None:
    if "width" not in in_json:
        logger.error("Required 'width' key not found in input json")
    if "start" not in in_json:
        logger.error("Required 'start' key not found in input json")
    if "end" not in in_json:
        logger.error("Required 'end' key not found in input json")
