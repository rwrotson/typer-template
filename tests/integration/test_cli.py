import pytest
from typer.testing import CliRunner

from cli_app.cli.app import app

runner = CliRunner()


@pytest.mark.enable_socket
def test_example_command_end_to_end() -> None:
    result = runner.invoke(app, ["command", "example-command", "hello", "--option", "3"])

    assert result.exit_code == 0
    assert "hello" in result.output
