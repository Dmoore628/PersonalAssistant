import os
import sys

from loguru import logger as _logger

# Configure loguru with sane defaults for containers
level = os.getenv("LOG_LEVEL", "INFO")
_logger.remove()

_logger.add(
    sink=sys.stdout,
    level=level,
    backtrace=False,
    diagnose=False,
    enqueue=True,
    serialize=False,
)

logger = _logger
