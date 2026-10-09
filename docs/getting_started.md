# Getting Started

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Installation

```bash
git clone <repo-url>
cd typer-template
uv sync --all-groups --locked
uv run pre-commit install
```

`pre-commit install` sets up three Git hooks:

- `pre-commit` — file hygiene checks, `uv lock` check, actionlint, ruff (with `--fix`), mypy
- `commit-msg` — Conventional Commit format (Commitizen)
- `pre-push` — pytest without coverage

Ruff and mypy run from the locked project environment (`uv run --no-sync`), so hook and CI versions match.

## Running the CLI

```bash
uv run cli-app --help
uv run cli-app --version
uv run cli-app --authors
```

### Global flags

Place global flags before the subcommand:

```bash
uv run cli-app --verbose command example-command hello

uv run cli-app --output-format json command example-command hello

echo "hello" | uv run cli-app command example-command
```

### Shell completion

```bash
uv run cli-app completion install

uv run cli-app completion install --shell zsh

uv run cli-app completion show
```

## Development Commands

Tasks are available via [poethepoet](https://poethepoet.natn.io/) — run with `uv run poe <name>`:

```bash
uv run poe check       # fmt-check, lint, typecheck, test
uv run poe fmt         # ruff format .
uv run poe fmt-check   # ruff format --check .
uv run poe lint        # ruff check .
uv run poe typecheck   # mypy (strict: src, tests, docs)
uv run poe test        # pytest (parallel, 95% branch coverage enforced)
uv run poe test-fast   # pytest without coverage, parallel, random order
uv run poe docs        # mkdocs serve
uv run poe audit       # pip-audit over locked dependencies
```

Or run the tools directly:

```bash
uv run pytest                        # full suite without coverage
uv run pytest --cov                  # with the coverage gate
uv run pytest tests/path/to/test.py  # single file
```

## Versioning & Changelog

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) — enforced by the `commit-msg` pre-commit hook.

```bash
uv run cz bump            # bump version, update CHANGELOG, create tag
uv run cz changelog       # update CHANGELOG without bumping
uv run cz changelog --dry-run
```

Bump type is inferred from commits: `fix:` → patch · `feat:` → minor · `feat!:` / `BREAKING CHANGE:` → major.

## Adding a Command Group

1. Create `src/cli_app/cli/commands/my_command.py`:

```python
from rich.markup import escape
from typer import Context, Typer

from cli_app.utils.console import get_console
from cli_app.utils.log import get_logger
from cli_app.utils.output import OutputFormat, render_output

app = Typer()
log = get_logger()


@app.command()
def my_action(ctx: Context, name: str) -> None:
    """Greet a named user in text or JSON."""
    console = get_console()
    log.debug("my_action called", name=name)
    fmt = ctx.obj.get("output_format", OutputFormat.text) if ctx.obj else OutputFormat.text
    render_output(
        {"name": name},
        fmt,
        text_render=lambda: console.print(f"Hello, [bold]{escape(name)}[/bold]!"),
    )
```

2. Export it from `src/cli_app/cli/commands/__init__.py`:

```python
from .my_command import app as my_command_app
```

3. Register it in `src/cli_app/cli/app.py`:

```python
from cli_app.cli.commands import my_command_app

app.add_typer(my_command_app, name="my-command")
```

### Stdin support

Use `read_stdin_if_piped()` to accept piped input as a fallback when an argument is omitted:

```python
from cli_app.utils.stdin import read_stdin_if_piped


@app.command()
def process(ctx: Context, text: str | None = None) -> None:
    resolved = text if text is not None else read_stdin_if_piped()
    if not resolved:
        raise typer.Exit(1)
    ...
```

## Configuration

Behaviour can be overridden via environment variables or a `.env` file. Sections are nested with `__`:

| Prefix | Controls |
|--------|----------|
| `CLI_APP_CONSOLE__*` | Rich console (width, colors, markup, quiet mode) |
| `CLI_APP_LOG__*` | Log levels, console renderer, log directory, file rotation |

```env
CLI_APP_LOG__LEVEL=DEBUG
CLI_APP_LOG__FORMAT=json
CLI_APP_CONSOLE__WIDTH=120
```

All variables are listed on the [configuration page](configuration.md).
