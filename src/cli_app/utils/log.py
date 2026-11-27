import logging
import logging.handlers
import sys
from types import MappingProxyType
from typing import TextIO, cast

import structlog

from cli_app.config import LogSettings

# Pass as ``extra`` to keep a record out of the console when the application reports it itself.
FILE_ONLY = MappingProxyType({"console": False})


class _AppFileHandler(logging.handlers.RotatingFileHandler):
    """Mark file handlers for replacement when logging is reconfigured."""


class _AppConsoleHandler(logging.StreamHandler[TextIO]):
    """Mark console handlers for replacement when logging is reconfigured."""


class _AppNullHandler(logging.NullHandler):
    """Keep logging.lastResort from printing to stderr when the console is disabled."""


def _console_record(record: logging.LogRecord) -> bool:
    return getattr(record, "console", True) is not False


def _prepare_handlers(
    config: LogSettings,
    console: bool,
    console_formatter: logging.Formatter,
    file_formatter: logging.Formatter,
) -> list[logging.Handler]:
    """Create all handlers before touching the root logger, closing them if one fails."""
    handlers: list[logging.Handler] = []
    try:
        if console:
            sh = _AppConsoleHandler(sys.stderr)
            sh.setLevel(config.console_level)
            sh.setFormatter(console_formatter)
            sh.addFilter(_console_record)
            handlers.append(sh)
        else:
            handlers.append(_AppNullHandler())

        logs_dir_path = config.resolved_dir.resolve()
        logs_dir_path.mkdir(parents=True, exist_ok=True)
        fh = _AppFileHandler(
            filename=logs_dir_path / config.file_name,
            maxBytes=config.file_max_bytes,
            backupCount=config.file_backup_count,
        )
        fh.setLevel(config.file_level)
        fh.setFormatter(file_formatter)
        handlers.append(fh)
    except Exception:
        for handler in handlers:
            handler.close()
        raise
    return handlers


def setup_logging(config: LogSettings | None = None, *, console: bool = True) -> None:
    """Configure shared structlog and stdlib handlers; without a config use the defaults."""
    if config is None:
        config = LogSettings()

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    # Only JSON output formats exceptions as text; ConsoleRenderer renders exc_info itself.
    json_processors: list[structlog.types.Processor] = [
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
    console_processors: list[structlog.types.Processor] = [
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.dev.ConsoleRenderer(),
    ]

    file_formatter = structlog.stdlib.ProcessorFormatter(
        processors=json_processors, foreign_pre_chain=shared_processors
    )
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processors=json_processors if config.format == "json" else console_processors,
        foreign_pre_chain=shared_processors,
    )

    handlers = _prepare_handlers(config, console, console_formatter, file_formatter)

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if isinstance(handler, (_AppFileHandler, _AppConsoleHandler, _AppNullHandler)):
            root_logger.removeHandler(handler)
            handler.close()

    for handler in handlers:
        root_logger.addHandler(handler)
    root_logger.setLevel(config.level)

    structlog.configure(
        processors=[*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger() -> structlog.typing.FilteringBoundLogger:
    """Return a logger that writes to stderr before logging is configured."""
    return cast(structlog.typing.FilteringBoundLogger, structlog.get_logger())


# Keep early logs off stdout so JSON command output remains valid.
structlog.configure(
    logger_factory=structlog.PrintLoggerFactory(sys.stderr),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=False,
)
