import os
from unittest.mock import patch

from cli_app.main import main


def test_main_calls_startup_sequence() -> None:
    with (
        patch("cli_app.main.setup_logging") as mock_logging,
        patch("cli_app.main.get_console") as mock_console,
        patch("cli_app.main.app") as mock_app,
    ):
        main()
        mock_logging.assert_called_once()
        mock_console.assert_called_once()
        mock_app.assert_called_once()


def test_no_app_variables_leak_into_tests() -> None:
    assert not [name for name in os.environ if name.startswith("CLI_APP_")]
