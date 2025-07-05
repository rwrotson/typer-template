import json
import logging
import logging.handlers
from os import makedirs
from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.logging import RichHandler

from utils.misc import find_project_root


class LogConfig(BaseSettings):
    level: int = logging.INFO
    console_level: int = logging.DEBUG
    file_level: int = logging.INFO
    dir: Path = find_project_root() / "logs"
    file_name: str = "cli-app.log"
    file_max_bytes: int = 4 * 1024 * 1024
    file_backup_count: int = 5
    use_json_formatter: bool = False

    model_config = SettingsConfigDict(
        env_file="log.env",
        env_prefix="CLI_APP_LOG_",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("level", "console_level", "file_level", mode="before")
    @classmethod
    def _validate_log_level(cls, value: Any) -> int:
        if isinstance(value, str):
            level_name = value.upper()
            level = logging.getLevelName(level_name)
            if isinstance(level, int):
                return level
            raise ValueError(f"Invalid log level: {value}")
        if isinstance(value, int):
            return value
        raise TypeError(f"Log level must be a string or int, not {type(value)}")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_object = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_object)


def setup_logging(config: LogConfig | None = None) -> None:
    if config is None:
        config = LogConfig()

    root = Path(__file__).parent.parent.resolve()
    logs_dir_path = root / config.dir

    if not logs_dir_path.exists() or not logs_dir_path.is_dir():
        makedirs(config.dir)

    log_file_path = logs_dir_path / config.file_name

    logger = logging.getLogger()
    logger.setLevel(config.level)

    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_formatter = logging.Formatter(format_str)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file_path,
        maxBytes=config.file_max_bytes,
        backupCount=config.file_backup_count,
    )
    file_handler.setLevel(config.file_level or config.level)
    file_handler.setFormatter(log_formatter)

    console_handler = RichHandler(markup=False, rich_tracebacks=True)
    console_handler.setLevel(config.console_level or config.level)
    console_handler.setFormatter(log_formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
