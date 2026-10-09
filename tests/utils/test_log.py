import json
import logging
import logging.handlers
from pathlib import Path

import pytest
from platformdirs import user_log_path
from pydantic import ValidationError

from cli_app.utils.log import LogConfig, _AppConsoleHandler, _AppFileHandler, setup_logging

_FILE_BACKUP_COUNT = 5
_LOG_DIR_MAX_BYTES = 4 * 1024 * 1024
_EXPECTED_HANDLER_COUNT = 2


def test_log_config_defaults() -> None:
    config = LogConfig()
    assert config.dir == user_log_path("cli-app")
    assert config.level == logging.INFO
    assert config.console_level == logging.DEBUG
    assert config.file_level == logging.INFO
    assert config.use_json_formatter is False
    assert config.file_name == "cli-app.log"
    assert config.file_max_bytes == _LOG_DIR_MAX_BYTES
    assert config.file_backup_count == _FILE_BACKUP_COUNT


def test_log_config_level_from_string() -> None:
    config = LogConfig(level="DEBUG")  # type: ignore[arg-type]
    assert config.level == logging.DEBUG


def test_log_config_level_from_int() -> None:
    config = LogConfig(level=logging.WARNING)
    assert config.level == logging.WARNING


def test_log_config_console_level_from_string() -> None:
    config = LogConfig(console_level="WARNING")  # type: ignore[arg-type]
    assert config.console_level == logging.WARNING


def test_log_config_invalid_level_raises() -> None:
    with pytest.raises(ValidationError):
        LogConfig(level="NOTLEVEL")  # type: ignore[arg-type]


def test_log_config_level_from_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLI_APP_LOG_LEVEL", "WARNING")
    config = LogConfig()
    assert config.level == logging.WARNING


def test_log_config_dir_from_env_var(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CLI_APP_LOG_DIR", str(tmp_path))
    assert LogConfig().dir == tmp_path


def test_setup_logging_creates_log_dir(tmp_path: Path, clean_root_logger: logging.Logger) -> None:
    _ = clean_root_logger
    log_dir = tmp_path / "logs"
    config = LogConfig(dir=log_dir)
    setup_logging(config)
    assert log_dir.exists()


def test_setup_logging_does_not_add_duplicate_handlers(
    tmp_path: Path, clean_root_logger: logging.Logger
) -> None:
    config = LogConfig(dir=tmp_path / "logs2")
    setup_logging(config)
    count_after_first = len(clean_root_logger.handlers)
    setup_logging(config)
    assert len(clean_root_logger.handlers) == count_after_first


def test_setup_logging_preserves_unrelated_handlers(
    tmp_path: Path, clean_root_logger: logging.Logger
) -> None:
    foreign_console = logging.StreamHandler()
    foreign_file = logging.handlers.RotatingFileHandler(tmp_path / "foreign.log")
    clean_root_logger.addHandler(foreign_console)
    clean_root_logger.addHandler(foreign_file)

    config = LogConfig(dir=tmp_path / "app")
    setup_logging(config)
    setup_logging(config)

    assert foreign_console in clean_root_logger.handlers
    assert foreign_file in clean_root_logger.handlers
    assert sum(isinstance(h, _AppFileHandler) for h in clean_root_logger.handlers) == 1
    assert sum(isinstance(h, _AppConsoleHandler) for h in clean_root_logger.handlers) == 1


def test_setup_logging_replaces_own_handlers_on_reconfiguration(
    tmp_path: Path, clean_root_logger: logging.Logger
) -> None:
    setup_logging(LogConfig(dir=tmp_path / "first"))
    previous_file = next(
        handler for handler in clean_root_logger.handlers if isinstance(handler, _AppFileHandler)
    )

    setup_logging(
        LogConfig(
            dir=tmp_path / "second",
            file_name="changed.log",
            file_level=logging.DEBUG,
            console_level=logging.WARNING,
            use_json_formatter=True,
        )
    )

    assert (
        sum(
            isinstance(h, (_AppFileHandler, _AppConsoleHandler)) for h in clean_root_logger.handlers
        )
        == _EXPECTED_HANDLER_COUNT
    )
    assert previous_file not in clean_root_logger.handlers
    assert previous_file.stream is None
    current_file = next(
        handler for handler in clean_root_logger.handlers if isinstance(handler, _AppFileHandler)
    )
    current_console = next(
        handler for handler in clean_root_logger.handlers if isinstance(handler, _AppConsoleHandler)
    )
    assert Path(current_file.baseFilename) == tmp_path / "second" / "changed.log"
    assert current_file.level == logging.DEBUG
    assert current_console.level == logging.WARNING

    clean_root_logger.warning("reconfigured")
    event = json.loads((tmp_path / "second" / "changed.log").read_text())
    assert event["event"] == "reconfigured"


def test_setup_logging_sets_root_level(tmp_path: Path, clean_root_logger: logging.Logger) -> None:
    config = LogConfig(dir=tmp_path / "logs3", level=logging.WARNING)
    setup_logging(config)
    assert clean_root_logger.level == config.level


def test_setup_logging_adds_two_handlers(tmp_path: Path, clean_root_logger: logging.Logger) -> None:
    config = LogConfig(dir=tmp_path / "logs4")
    setup_logging(config)
    app_handlers = [
        h
        for h in clean_root_logger.handlers
        if isinstance(h, (_AppFileHandler, _AppConsoleHandler))
    ]
    assert len(app_handlers) == _EXPECTED_HANDLER_COUNT


def test_setup_logging_json_formatter(
    tmp_path: Path, clean_root_logger: logging.Logger, capsys: pytest.CaptureFixture[str]
) -> None:
    config = LogConfig(dir=tmp_path / "logs5", use_json_formatter=True)
    setup_logging(config)
    clean_root_logger.warning("json event")
    event = json.loads((config.dir / config.file_name).read_text())
    assert event["event"] == "json event"
    assert json.loads(capsys.readouterr().err)["event"] == "json event"
