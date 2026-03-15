# typer-template

A template for building Python CLI applications with [Typer](https://typer.tiangolo.com/), featuring Rich output, structured logging via structlog, snapshot testing, and environment-based configuration.

## Stack

- **[Typer](https://typer.tiangolo.com/)** — CLI framework
- **[Rich](https://rich.readthedocs.io/)** — terminal output and progress bars
- **[structlog](https://www.structlog.org/)** — structured logging with context binding; dev console output or JSON for aggregators
- **[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** — environment-based configuration
- **[uv](https://docs.astral.sh/uv/)** — package management
- **[Ruff](https://docs.astral.sh/ruff/)** — linting and formatting
- **[MyPy](https://mypy.readthedocs.io/)** — strict type checking
- **[Vulture](https://github.com/jendrikseipp/vulture)** — dead code detection
- **[pytest](https://docs.pytest.org/)** + **[pytest-xdist](https://github.com/pytest-dev/pytest-xdist)** + **[syrupy](https://github.com/syrupy-project/syrupy)** — parallel testing with snapshot assertions
- **[commitizen](https://commitizen-tools.github.io/commitizen/)** — Conventional Commits + automated versioning and CHANGELOG
- **[MkDocs Material](https://squidfunk.github.io/mkdocs-material/)** — documentation site

## Requirements

- Python 3.13+
- uv

## Getting Started

```bash
# Clone the repo and install dependencies
uv sync --all-extras

# Run the CLI
uv run cli-app --help

# Install pre-commit hooks (enforces Conventional Commits)
uv run pre-commit install
```

## Development

Tasks are available via [taskipy](https://github.com/taskipy/taskipy) — run with `uv run task <name>`:

```bash
uv run task lint        # ruff check
uv run task fmt         # ruff format
uv run task typecheck   # mypy src/
uv run task test        # pytest (parallel, 80% coverage enforced)
uv run task test-fast   # pytest --no-cov -n auto
uv run task dead        # vulture dead-code scan
uv run task audit       # pip-audit dependency audit
```

Or run the tools directly:

```bash
uv run pytest --no-cov -n auto          # fast parallel run
uv run pytest --snapshot-update         # update syrupy snapshots
uv run pytest tests/path/to/test.py     # single file
```

## Docs

```bash
uv run --group docs mkdocs serve      # live preview at http://127.0.0.1:8000
uv run --group docs mkdocs build      # build static site to site/
uv run --group docs mkdocs gh-deploy  # deploy to GitHub Pages (gh-pages branch)
```

Source is in `docs/`. Powered by [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) with `mkdocstrings` for API reference generation.

## Global CLI Flags

The root app exposes flags available to every subcommand:

| Flag | Short | Default | Effect |
|------|-------|---------|--------|
| `--verbose` | `-V` | off | Sets log level to DEBUG at runtime |
| `--output-format` | `-f` | `text` | `text` (Rich) or `json` (machine-readable) |
| `--version` | `-v` | — | Print version and dependency list, then exit |
| `--authors` | `-A` | — | Print author contacts, then exit |

```bash
cli-app --verbose command example-command hello
cli-app --output-format json command example-command hello
echo "hello" | cli-app command example-command   # stdin piping
```

## Shell Completion

```bash
cli-app completion install           # install for the current shell
cli-app completion install --shell zsh
cli-app completion show              # print the completion script
```

Or directly via the built-in Typer flags:

```bash
cli-app --install-completion
cli-app --show-completion
```

## Versioning & Changelog

This template uses [Conventional Commits](https://www.conventionalcommits.org/) enforced by a `commit-msg` pre-commit hook.

```bash
# Bump version, update CHANGELOG, tag
uv run cz bump

# Preview changelog without bumping
uv run cz changelog --dry-run
```

Bump type is inferred automatically: `fix:` → patch, `feat:` → minor, `feat!:` / `BREAKING CHANGE` → major.

## Configuration

Console and logging behaviour can be configured via environment variables or a `.env` file:

| Prefix | Controls |
|--------|----------|
| `CLI_APP_CONSOLE_*` | Rich console settings (theme, colors, width) |
| `CLI_APP_LOG_*` | Log level, file rotation, JSON output |

```env
CLI_APP_LOG_LEVEL=DEBUG
CLI_APP_LOG_USE_JSON_FORMATTER=true   # emit JSON logs (for Datadog, Loki, etc.)
CLI_APP_CONSOLE_WIDTH=120
```

## Project Structure

```
src/
└── cli_app/
    ├── main.py              # entry point
    ├── cli/
    │   ├── app.py           # root Typer app (--verbose, --output-format, --version, --authors)
    │   ├── callbacks/       # eager option callbacks (--version, --authors)
    │   └── commands/
    │       ├── command.py   # example command group (stdin + output-format patterns)
    │       └── completion.py # shell completion sub-app
    ├── core/                # domain logic + Settings
    └── utils/
        ├── console.py       # singleton Rich Console
        ├── log.py           # structlog setup (ConsoleRenderer dev / JSON prod)
        ├── output.py        # OutputFormat enum, render_output(), echo_json()
        ├── stdin.py         # is_stdin_piped(), read_stdin_if_piped(), iter_stdin_lines()
        ├── meta.py          # distribution metadata at runtime
        ├── format.py        # Rich Theme
        ├── emoji.py         # Emoji StrEnum
        ├── progress.py      # Rich Progress bar factory
        └── misc.py          # find_project_root()
```

## CI/CD

`.github/workflows/ci.yml` runs on every push/PR to `main` and `dev`:

| Step | What it does |
|------|-------------|
| ruff format | formatting check |
| ruff lint | linting |
| mypy | strict type checking |
| vulture | dead code detection |
| pytest | parallel tests, 80% coverage enforced |
| pip-audit | known CVE check for dependencies |
| trivy | filesystem vulnerability scan (CRITICAL/HIGH, fails build) |

Dependabot opens weekly PRs for both pip packages and GitHub Actions.

`.github/workflows/release.yml` runs on version tags (`v*`):

| Job | What it does |
|-----|-------------|
| `publish` | builds the package and publishes to PyPI via OIDC trusted publisher (no secrets) |
| `docs` | deploys MkDocs to GitHub Pages |

PyPI publishing uses keyless OIDC — configure a trusted publisher on PyPI pointing to this repo with workflow file `release.yml`.

## Author

Igor Lashkov — rwrotson@yandex.ru
