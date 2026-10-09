import logging
import logging.handlers
import sys
from pathlib import Path
from typing import TextIO

import structlog
from platformdirs import user_log_path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class _AppFileHandler(logging.handlers.RotatingFileHandler):
    """File handler owned by this application."""


class _AppConsoleHandler(logging.StreamHandler[TextIO]):
    """Console handler owned by this application."""


class LogConfig(BaseSettings):
    """Pydantic settings for logging, configurable via CLI_APP_LOG_* env vars."""

    level: int = logging.INFO
    console_level: int = logging.DEBUG
    file_level: int = logging.INFO
    dir: Path = user_log_path("cli-app")
    file_name: str = "cli-app.log"
    file_max_bytes: int = 4 * 1024 * 1024
    file_backup_count: int = 5
    use_json_formatter: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CLI_APP_LOG_",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("level", "console_level", "file_level", mode="before")
    @classmethod
    def _validate_log_level(cls, value: str | int) -> int:
        """Accept log level as a string name (e.g. 'DEBUG') or an integer."""
        if isinstance(value, str):
            level_name = value.upper()
            level = logging.getLevelName(level_name)
            if isinstance(level, int):
                return level
            raise ValueError(f"Invalid log level: {value}")
        if isinstance(value, int):
            return value
        raise TypeError(f"Log level must be a string or int, not {type(value)}")


def setup_logging(config: LogConfig | None = None) -> None:
    """Configure structlog and stdlib logging.

    Structlog is wired through stdlib so that both first-party loggers
    (``structlog.get_logger()``) and third-party stdlib loggers share the
    same handler chain.  The file handler always emits JSON; the console
    handler emits colourised output by default or JSON when
    ``use_json_formatter`` is ``True``.
    """
    if config is None:
        config = LogConfig()

    logs_dir_path = config.dir.resolve()
    logs_dir_path.mkdir(parents=True, exist_ok=True)
    log_file_path = logs_dir_path / config.file_name

    # Processors applied to every log record (structlog and foreign stdlib).
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    console_renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer()
        if config.use_json_formatter
        else structlog.dev.ConsoleRenderer()
    )

    # File handler always writes JSON for structured log analysis.
    file_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
        foreign_pre_chain=shared_processors,
    )
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            console_renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(config.level)

    fh = _AppFileHandler(
        filename=log_file_path,
        maxBytes=config.file_max_bytes,
        backupCount=config.file_backup_count,
    )
    fh.setLevel(config.file_level)
    fh.setFormatter(file_formatter)

    sh = _AppConsoleHandler(sys.stderr)
    sh.setLevel(config.console_level)
    sh.setFormatter(console_formatter)

    for handler in root_logger.handlers[:]:
        if isinstance(handler, (_AppFileHandler, _AppConsoleHandler)):
            root_logger.removeHandler(handler)
            handler.close()

    root_logger.addHandler(fh)
    root_logger.addHandler(sh)

    structlog.configure(
        processors=[*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# Ensure structlog never writes to stdout before setup_logging() is called.
# setup_logging() will fully reconfigure this with stdlib integration.
structlog.configure(
    logger_factory=structlog.PrintLoggerFactory(sys.stderr),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=False,
)
