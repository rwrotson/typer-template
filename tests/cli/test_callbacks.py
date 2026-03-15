from unittest.mock import MagicMock, patch

import pytest
from typer import Exit

from cli_app.cli.callbacks.meta import authors_cb, summary_cb, version_cb


def test_summary_cb_noop_when_false() -> None:
    summary_cb(False)


def test_summary_cb_prints_and_exits_when_true() -> None:
    mock_meta = MagicMock()
    mock_meta.__getitem__ = MagicMock(return_value="A template CLI app.")
    mock_console = MagicMock()

    with (
        patch("cli_app.cli.callbacks.meta.get_project_meta", return_value=mock_meta),
        patch("cli_app.cli.callbacks.meta.get_console", return_value=mock_console),
        pytest.raises(Exit),
    ):
        summary_cb(True)

    mock_console.print.assert_called_once()


def test_version_cb_noop_when_false() -> None:
    version_cb(False)


def test_version_cb_prints_and_exits_when_true() -> None:
    mock_meta = MagicMock()
    mock_meta.__getitem__ = MagicMock(side_effect=lambda k: [] if k == "dependencies" else "1.0.0")
    mock_console = MagicMock()

    with (
        patch("cli_app.cli.callbacks.meta.get_project_meta", return_value=mock_meta),
        patch("cli_app.cli.callbacks.meta.get_console", return_value=mock_console),
        pytest.raises(Exit),
    ):
        version_cb(True)

    mock_console.print.assert_called_once()


def test_authors_cb_noop_when_false() -> None:
    authors_cb(False)


def test_authors_cb_prints_and_exits_when_true() -> None:
    mock_meta = MagicMock()
    mock_meta.__getitem__ = MagicMock(return_value=[{"name": "Test", "email": "test@test.com"}])
    mock_console = MagicMock()

    with (
        patch("cli_app.cli.callbacks.meta.get_project_meta", return_value=mock_meta),
        patch("cli_app.cli.callbacks.meta.get_console", return_value=mock_console),
        pytest.raises(Exit),
    ):
        authors_cb(True)

    mock_console.print.assert_called_once()
