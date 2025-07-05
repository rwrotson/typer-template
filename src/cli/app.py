from typing import Annotated

from typer import Option, Typer

from cli.callbacks import meta as meta_callbacks
from cli.commands import command_app
from utils.console import get_console

app = Typer()
app.add_typer(command_app, name="command")

console = get_console()


@app.callback()
def main(
    version: Annotated[
        bool,
        Option(
            "--version",
            "-v",
            help="Show the application's version and exit.",
            callback=meta_callbacks.version_cb,
            is_eager=True,
        ),
    ] = False,
    authors: Annotated[
        bool,
        Option(
            "--authors",
            "-A",
            help="Show the application's authors contacts and exit.",
            callback=meta_callbacks.authors_cb,
            is_eager=True,
        ),
    ] = False,
):
    """Manage the main application state and top-level options like --version."""
    pass
