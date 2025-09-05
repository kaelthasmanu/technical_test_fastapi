import logging
import sys
from typing import Optional

from loguru import logger


class InterceptHandler(logging.Handler):
    """Redirect standard logging records to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[attr-defined]
            depth += 1

        logger.bind(name=record.name).opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(configs) -> None:
    """Configure Loguru and intercept stdlib/uvicorn loggers.

    Args:
        configs: settings object providing LOG_* fields.
    """
    logger.remove()

    # Console sink
    console_kwargs = dict(
        level=configs.LOG_LEVEL,
        backtrace=configs.ENV != "prod",
        diagnose=configs.ENV != "prod",
        enqueue=True,
    )
    if getattr(configs, "LOG_JSON", False):
        logger.add(sys.stdout, serialize=True, **console_kwargs)
    else:
        fmt = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
        logger.add(sys.stdout, format=fmt, **console_kwargs)

    # Optional file sink
    log_file: Optional[str] = getattr(configs, "LOG_FILE", None)
    if log_file:
        logger.add(
            log_file,
            rotation=getattr(configs, "LOG_ROTATION", "10 MB"),
            retention=getattr(configs, "LOG_RETENTION", "7 days"),
            level=configs.LOG_LEVEL,
            enqueue=True,
            backtrace=False,
            diagnose=False,
        )

    # Intercept stdlib logging and uvicorn loggers
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        _logger = logging.getLogger(name)
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False

    logger.info(
        "Logging configured: level={}, json={}, file={}",
        configs.LOG_LEVEL,
        getattr(configs, "LOG_JSON", False),
        bool(log_file),
    )
