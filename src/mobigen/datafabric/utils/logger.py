import logging
from enum import Enum
from functools import singledispatch
from types import DynamicClassAttribute
from typing import Optional, Union

GLOSSARY_LOGGER = "glossary"
BASE_LOGGING_FORMAT = (
    "[%(asctime)s] %(levelname)-8s {%(name)s:%(module)s:%(lineno)d} - %(message)s"
)
logging.basicConfig(format=BASE_LOGGING_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")


class Loggers(Enum):
    """
    Enum for loggers
    """
    CLI = "CLI"
    REST = "REST"
    UTILS = "UTILS"

    @DynamicClassAttribute
    def value(self):
        """Centralize the logger under `glossary.NAME`"""
        # Disabling linting, false positive as it does not find _value_
        return GLOSSARY_LOGGER + "." + self._value_  # pylint: disable=no-member


class ANSI(Enum):
    BRIGHT_RED = "\u001b[31;1m"
    BOLD = "\u001b[1m"
    BRIGHT_CYAN = "\u001b[36;1m"
    YELLOW = "\u001b[33;1m"
    GREEN = "\u001b[32;1m"
    ENDC = "\033[0m"
    BLUE = "\u001b[34;1m"
    MAGENTA = "\u001b[35;1m"


def cli_logger(lv: Union[int, str] = logging.DEBUG):
    """
    Method to get the CLI logger
    """
    logger = logging.getLogger(Loggers.CLI.value)
    logger.setLevel(lv)
    return logger


def rest_logger(lv: Union[int, str] = logging.DEBUG):
    """
    Method to get the REST logger
    """
    logger = logging.getLogger(Loggers.REST.value)
    logger.setLevel(lv)
    return logger


def utils_logger(lv: Union[int, str] = logging.DEBUG):
    """
    Method to get the UTILS logger
    """
    logger = logging.getLogger(Loggers.UTILS.value)
    logger.setLevel(lv)
    return logger


def set_loggers_level(name: str, lv: Union[int, str] = logging.INFO):
    """
    Set all loggers levels
    :param name: logger name
    :param lv: logging level
    """
    logging.getLogger(name).setLevel(lv)


def log_ansi_encoded_string(
    color: Optional[ANSI] = None, bold: bool = False, message: str = ""
):
    utils_logger().info(
        f"{ANSI.BOLD.value if bold else ''}{color.value if color else ''}{message}{ANSI.ENDC.value}"
    )