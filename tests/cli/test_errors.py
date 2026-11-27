import json
import logging
from pathlib import Path

import typer
from rich.console import Console
from typer.testing import CliRunner

from cli_app.cli.context import AppContext, get_app_context
from cli_app.cli.errors import ServiceErrorGroup
from cli_app.config import LogSettings, Settings
from cli_app.services.errors import InvalidInputError, ServiceError
from cli_app.utils.log import setup_logging
from cli_app.utils.output import OutputFormat

runner = CliRunner()


def make_app(output_format: OutputFormat | None = None) -> typer.Typer:
    app = typer.Typer(cls=ServiceErrorGroup)

    @app.callback()
    def root(ctx: typer.Context) -> None:
        if output_format is not None:
            ctx.obj = AppContext(
                settings=Settings(), console=Console(), output_format=output_format
            )

    @app.command()
    def fail() -> None:
        raise ServiceError("boom")

    @app.command()
    def invalid() -> None:
        raise InvalidInputError("bad input")

    @app.command()
    def context(ctx: typer.Context) -> None:
        get_app_context(ctx)

    return app


def test_service_error_without_context_is_reported_as_text() -> None:
    result = runner.invoke(make_app(), ["fail"])
    assert result.exit_code == 1
    assert result.stderr == "Error: boom\n"


def test_get_app_context_requires_root_callback() -> None:
    result = runner.invoke(make_app(), ["context"])
    assert isinstance(result.exception, RuntimeError)


def test_service_error_in_text_mode_uses_its_exit_code() -> None:
    result = runner.invoke(make_app(OutputFormat.text), ["invalid"])
    assert result.exit_code == 2
    assert result.stdout == ""
    assert result.stderr == "Error: bad input\n"


def test_service_error_in_json_mode_is_reported_as_json() -> None:
    result = runner.invoke(make_app(OutputFormat.json), ["invalid"])
    assert result.exit_code == 2
    assert result.stdout == ""
    assert json.loads(result.stderr) == {
        "error": {"type": "InvalidInputError", "message": "bad input"}
    }


def test_service_error_is_logged_to_the_file_once_and_printed_once(
    tmp_path: Path, clean_root_logger: logging.Logger
) -> None:
    _ = clean_root_logger
    setup_logging(LogSettings(dir=tmp_path))
    result = runner.invoke(make_app(), ["invalid"])
    assert result.stderr.count("Error: bad input") == 1
    assert "Command failed" not in result.stderr
    events = [json.loads(line) for line in (tmp_path / "cli-app.log").read_text().splitlines()]
    assert len(events) == 1
    assert events[0]["event"] == "Command failed: bad input"
    assert "InvalidInputError: bad input" in events[0]["exception"]
