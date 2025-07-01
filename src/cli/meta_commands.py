import typer

from utils.console import get_console
from utils.meta import get_project_meta

app = typer.Typer()
console = get_console()
meta = get_project_meta()


@app.command()
def version():
    console.print(f"{meta["name"]} {meta["version"]}")


@app.command()
def authors():
    console.print(meta)


@app.command()
def summary():
    console.print(meta["summary"])
