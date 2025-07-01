import typer

from cli.command import app as command_app
from cli.meta_commands import app as version_app

app = typer.Typer()

app.add_typer(version_app)
app.add_typer(command_app)


if __name__ == "__main__":
    app()
