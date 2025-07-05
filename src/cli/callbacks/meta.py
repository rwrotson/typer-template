from typer import Exit

from utils.console import get_console
from utils.meta import get_project_meta


def version_cb(v: bool = False):
    """Show the version of the CLI."""
    if v:
        meta, console = get_project_meta(), get_console()

        version_string = f"[bold]{meta['name']} {meta['version']}[/bold]"
        dependencies_strings = (
            f" - {name} {version}" for name, version in meta["dependencies"].items()
        )
        console.print(
            version_string + "\n\nUses:\n" + "\n".join(dependencies_strings)
            if dependencies_strings
            else version_string
        )

        raise Exit(0)


def authors_cb(v: bool = False):
    """Show contacts of authors of the CLI."""
    if v:
        meta, console = get_project_meta(), get_console()

        authors_strings = [
            f"{author['name']} <[bold]{author['email']}[/bold]>" for author in meta["authors"]
        ]
        console.print("\n".join(authors_strings))

        raise Exit(0)


def summary_cb(v: bool = False):
    """Show the summary of the CLI."""
    if v:
        meta, console = get_project_meta(), get_console()

        console.print(f"{meta['summary']}")

        raise Exit(0)
