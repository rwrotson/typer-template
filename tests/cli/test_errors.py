import typer
from typer.testing import CliRunner

from cli_app.cli.context import get_app_context
from cli_app.cli.errors import ServiceErrorGroup
from cli_app.services.errors import ServiceError

runner = CliRunner()


def make_app() -> typer.Typer:
    app = typer.Typer(cls=ServiceErrorGroup)

    @app.command()
    def fail() -> None:
        raise ServiceError("boom")

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
