from loguru import logger as _logger
import os

# Configure loguru with sane defaults for containers
level = os.getenv("LOG_LEVEL", "INFO")
_logger.remove()
_logger.add(
    sink=lambda msg: print(msg, end=""),
    level=level,
    backtrace=False,
    diagnose=False,
    enqueue=True,
    serialize=False,
)

logger = _logger
