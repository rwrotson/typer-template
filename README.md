# typer-template

A Python CLI template with Typer, Rich output, structlog logging, and environment-based settings.

## Stack

- **[Typer](https://typer.tiangolo.com/)** — CLI framework
- **[Rich](https://rich.readthedocs.io/)** — terminal output and progress bars
- **[structlog](https://www.structlog.org/)** — structured logging with context binding; dev console output or JSON for aggregators
- **[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** — environment-based configuration
- **[uv](https://docs.astral.sh/uv/)** — package management
- **[Ruff](https://docs.astral.sh/ruff/)** — linting and formatting
- **[MyPy](https://mypy.readthedocs.io/)** — strict type checking
- **[pytest](https://docs.pytest.org/)** + **[pytest-xdist](https://github.com/pytest-dev/pytest-xdist)** — parallel testing with coverage enforcement
- **[commitizen](https://commitizen-tools.github.io/commitizen/)** — Conventional Commits + automated versioning and CHANGELOG
- **[MkDocs Material](https://squidfunk.github.io/mkdocs-material/)** — documentation site

## Requirements

- Python 3.14+
- uv

## Getting Started

```bash
uv sync --all-groups --locked

uv run cli-app --help

uv run pre-commit install
```

## Development

Run development tasks with [taskipy](https://github.com/taskipy/taskipy):

```bash
uv run task lint
uv run task fmt
uv run task typecheck
uv run task test
uv run task test-fast
uv run task audit
```

Or run the tools directly:

```bash
uv run pytest
uv run pytest tests/path/to/test.py
```

## Docs

```bash
uv run --group docs mkdocs serve
uv run --group docs mkdocs build
```

Source is in `docs/`. MkDocs generates the API reference from public docstrings. The release workflow deploys the site to GitHub Pages.

## Global CLI Flags

The root app exposes flags available to every subcommand:

| Flag | Short | Default | Effect |
|------|-------|---------|--------|
| `--verbose` | `-V` | off | Sets log level to DEBUG at runtime |
| `--output-format` | `-f` | `text` | `text` (Rich) or `json` (machine-readable) |
| `--version` | `-v` | — | Print version and dependency list, then exit |
| `--authors` | `-A` | — | Print author contacts, then exit |

JSON output is written to stdout; diagnostics are written to stderr.

```bash
cli-app --verbose command example-command hello
cli-app --output-format json command example-command hello
echo "hello" | cli-app command example-command
```

## Shell Completion

```bash
cli-app completion install
cli-app completion install --shell zsh
cli-app completion show
```

Or directly via the built-in Typer flags:

```bash
cli-app --install-completion
cli-app --show-completion
```

## Versioning & Changelog

This template uses [Conventional Commits](https://www.conventionalcommits.org/) enforced by a `commit-msg` pre-commit hook.

```bash
uv run cz bump

uv run cz changelog --dry-run
```

Bump type is inferred automatically: `fix:` → patch, `feat:` → minor, `feat!:` / `BREAKING CHANGE` → major.

## Configuration

Console and logging behaviour can be configured via environment variables or a `.env` file:

| Prefix | Controls |
|--------|----------|
| `CLI_APP_CONSOLE_*` | Rich console settings (theme, colors, width) |
| `CLI_APP_LOG_*` | Log level, file rotation, JSON output, user log directory |

```env
CLI_APP_LOG_LEVEL=DEBUG
CLI_APP_LOG_USE_JSON_FORMATTER=true
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
    ├── core/                # application Settings
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
| mypy | strict type checking for source, tests, and docs scripts |
| pytest | parallel tests, 95% branch coverage enforced |
| uv build | package build check |
| mkdocs build | documentation build check |
| pip-audit | known CVE check for dependencies |
| trivy | filesystem vulnerability scan (CRITICAL/HIGH, fails build) |

Dependabot opens weekly PRs for both pip packages and GitHub Actions.

`.github/workflows/release.yml` runs on version tags (`v*`) or via `workflow_dispatch`:

| Job | What it does |
|-----|-------------|
| `docs` | builds MkDocs and deploys it to GitHub Pages via GitHub Actions |

The workflow does not publish the package to PyPI. Set Pages Source to **GitHub Actions** and allow `v*` tags in the `github-pages` environment for tag-triggered deployments.

## Using This Template

The distribution, import package, and CLI command have separate names. Follow the [renaming checklist](https://rwrotson.github.io/typer-template/notes/#renaming-the-template) when copying this template into a new project.

## Author

Igor Lashkov — rwrotson@yandex.ru
