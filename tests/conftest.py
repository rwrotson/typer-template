import logging
import os
from collections.abc import Iterator
from pathlib import Path

import pytest
import structlog

from cli_app.utils.console import get_console


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--live", action="store_true", help="collect tests/integration")


def pytest_ignore_collect(collection_path: Path, config: pytest.Config) -> bool | None:
    if collection_path.name == "integration" and collection_path.parent.name == "tests":
        return not config.getoption("--live")
    return None


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Keep the developer's CLI_APP_* variables and .env file out of every test."""
    for name in list(os.environ):
        if name.startswith("CLI_APP_"):
            monkeypatch.delenv(name)
    monkeypatch.chdir(tmp_path)


@pytest.fixture(autouse=True)
def restore_logging() -> Iterator[None]:
    """Undo global logging setup performed by a test."""
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    config = structlog.get_config()
    yield
    for handler in root.handlers:
        if handler not in handlers:
            handler.close()
    root.handlers = handlers
    root.setLevel(level)  # Unlike assigning .level, this clears cached isEnabledFor results.
    structlog.configure(**config)


@pytest.fixture(autouse=True)
def reset_console() -> Iterator[None]:
    """Build a fresh console for each test from its own environment."""
    get_console.cache_clear()
    yield
    get_console.cache_clear()


@pytest.fixture
def clean_root_logger(restore_logging: None) -> logging.Logger:
    """Start with no root handlers; restore_logging puts them back."""
    root = logging.getLogger()
    root.handlers = []
    return root
