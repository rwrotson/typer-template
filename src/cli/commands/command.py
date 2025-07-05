import logging
from typing import Annotated

from typer import Argument, Option, Typer

from utils.console import get_console


app = Typer()
console = get_console()
logger = logging.getLogger(__name__)


@app.command()
def example_command(
    argument: Annotated[
        str | None,
        Argument(
            ...,
            help="Help text for string argument.",
        ),
    ],
    output_file: [
        int | None,
        Option(
            None,
            "-o",
            "--option",
            "--opt",
            help="Help text for integer option.",
        ),
    ],
):
    """Help text for command example."""
    pass
