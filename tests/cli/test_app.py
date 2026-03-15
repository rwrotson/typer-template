import json

import pytest
from syrupy.assertion import SnapshotAssertion
from typer.testing import CliRunner

from cli_app.cli.app import app

runner = CliRunner()


def test_version_flag_exits_zero() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0


def test_version_output_contains_version_number() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "cli-app" in result.output


def test_authors_flag_exits_zero() -> None:
    result = runner.invoke(app, ["--authors"])
    assert result.exit_code == 0


def test_authors_flag_short_exits_zero() -> None:
    result = runner.invoke(app, ["-A"])
    assert result.exit_code == 0


def test_authors_output_contains_author_name() -> None:
    result = runner.invoke(app, ["--authors"])
    assert result.exit_code == 0
    assert "Igor Lashkov" in result.output


def test_command_help() -> None:
    result = runner.invoke(app, ["command", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_example_command_missing_argument_fails() -> None:
    result = runner.invoke(app, ["command", "example-command"])
    assert result.exit_code != 0


def test_example_command_with_argument_exits_zero() -> None:
    result = runner.invoke(app, ["command", "example-command", "hello"])
    assert result.exit_code == 0


def test_example_command_with_integer_option() -> None:
    result = runner.invoke(app, ["command", "example-command", "hello", "--option", "42"])
    assert result.exit_code == 0


def test_example_command_option_requires_integer() -> None:
    result = runner.invoke(app, ["command", "example-command", "hello", "--option", "notanint"])
    assert result.exit_code != 0


def test_help_flag() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output


# --verbose --------------------------------------------------------------------


def test_verbose_flag_exits_zero() -> None:
    result = runner.invoke(app, ["--verbose", "command", "example-command", "hello"])
    assert result.exit_code == 0


def test_verbose_short_flag_exits_zero() -> None:
    result = runner.invoke(app, ["-V", "command", "example-command", "hello"])
    assert result.exit_code == 0


# --output-format --------------------------------------------------------------


def test_output_format_json_produces_valid_json() -> None:
    result = runner.invoke(app, ["--output-format", "json", "command", "example-command", "hello"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["argument"] == "hello"
    assert data["option"] is None


def test_output_format_json_with_option() -> None:
    result = runner.invoke(
        app, ["--output-format", "json", "command", "example-command", "hello", "--option", "7"]
    )
    assert result.exit_code == 0
    _expected_option = 7
    data = json.loads(result.output)
    assert data["option"] == _expected_option


def test_output_format_text_is_default() -> None:
    result = runner.invoke(app, ["command", "example-command", "hello"])
    assert result.exit_code == 0
    # text output contains the argument value directly, not JSON
    assert "hello" in result.output
    with pytest.raises((json.JSONDecodeError, ValueError)):
        json.loads(result.output)


def test_output_format_invalid_value_fails() -> None:
    result = runner.invoke(app, ["--output-format", "xml", "command", "example-command", "hi"])
    assert result.exit_code != 0


# snapshot tests (syrupy) ------------------------------------------------------


def test_help_output_snapshot(snapshot: SnapshotAssertion) -> None:
    result = runner.invoke(app, ["--help"])
    assert result.output == snapshot


def test_version_output_snapshot(snapshot: SnapshotAssertion) -> None:
    result = runner.invoke(app, ["--version"])
    assert result.output == snapshot
