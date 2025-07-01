from typer import Argument, Option, Typer

from utils.console import get_console

app = Typer()
console = get_console()

@app.command()
def my_command(
    arg: str = Argument(...),
    option: str | None = Option(
        None,
        "-o",
        "--output",
        resolve_path=True,
        help="The path for the output PDF file. If not provided, saved as '[input]_inverted.pdf'.",
    ),
):
    """Help message."""
    console.print()
