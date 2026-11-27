# AGENTS.md

A template for building Python CLI apps using [Typer](https://typer.tiangolo.com/) with Rich output, structlog-based structured logging, and Pydantic Settings-based configuration.

Distribution name: `cli-app` | Python package: `cli_app` | Entry point: `cli-app` | Environment prefix: `CLI_APP_`

## Load instructions by path

For each area of the task, mirror its repo-relative path under [docs/agents](docs/agents/) and read the matching guide before editing: for `src/cli_app/utils/log.py`, read the [utilities guide](docs/agents/src/cli_app/utils.md). For any code change, also read [docs/architecture.md](docs/architecture.md). The [Read when](#read-when) table lists every guide.

## Commands

This project uses [uv](https://docs.astral.sh/uv/) for package management; the full task list is in README "Development".

```bash
uv sync --all-groups --locked
uv run cli-app --help
uv run poe check        # fmt-check, lint, lint-imports, typecheck, test (95% branch coverage)
uv run poe quick        # lint, lint-imports, typecheck (no formatting check or tests)
uv run poe test-fast    # pytest without coverage, parallel, random order
uv run poe test-live    # tests/integration against real services; needs --live, reads .env
uv run poe fmt          # ruff format . (rewrites files)
uv run poe audit        # pip-audit over locked dependencies
uv run --group docs properdocs build --strict
```

## Change Workflow

- Inspect `git status` before editing. Preserve existing uncommitted changes and limit edits to the requested task.
- When working from an active staged plan in `docs/plans/`, read it before work, implement only the first incomplete stage, append dated evidence, and stop at the stage boundary.
- Run `uv run poe check` after code changes. After documentation, `properdocs.yml`, or public docstring changes, also run `uv run --group docs properdocs build --strict`.
- The Claude Code hooks in `.claude/` run `ruff format` and `ruff check --fix` on the Python file just edited (an intentional edit) and, at Stop, run `poe quick` when Python files changed during the turn; they do not replace `poe check`.
- Use non-rewriting checks (`poe fmt-check`, `poe lint`) for verification; run formatters or `--fix` only when intentionally editing files. Pre-commit's Ruff hooks rewrite files.
- Report which checks ran, which were skipped, and why. `poe test-fast` is not the full CI suite: it skips coverage, and CI also runs tests on macOS, the lowest-dependency job, package and docs builds, and security scans.
- When changing public settings, global options, or commands, update `.env.example`, README, and the docs.

## Commit Handoff

- Do not create or amend commits on the user's behalf.
- After completing and verifying a meaningful, self-contained part of the work, pause before starting the next part.
- At each pause, send the user a one-line English Conventional Commit message for the completed work. Resume when the user asks you to continue.

## Layers

```
main      src/cli_app/main.py   `cli-app` console script: loads settings, sets up logging, runs the app
cli       src/cli_app/cli/      Typer apps, global options, AppContext, error reporting
utils     src/cli_app/utils/    console, logging, output, stdin, metadata helpers
services  src/cli_app/services/ use cases, result types, ServiceError hierarchy
config    src/cli_app/config/   CLI_APP_* Settings with defaults in code
```

A layer imports only layers below it; `utils` and `services` are independent, and `services` imports no other layer or Typer, Rich, structlog, or settings. The rules are in [docs/architecture.md](docs/architecture.md#rules); `uv run poe lint-imports` enforces them.

## Invariants

- Do not lower coverage thresholds, disable checks, relax import-linter contracts, or add lint and type suppressions solely to pass CI. Explain necessary suppressions at the affected line.
- Only `load_settings()`, called from `main` and the root callback, reads the environment and `.env`; other code takes settings objects as arguments.
- Expected failures raise a `ServiceError` subclass with an `exit_code` instead of `typer.Exit`.
- JSON command output goes to stdout; diagnostics and logs go to stderr.
- Tests never use the network, except `tests/integration/` under `--live`.
- Code, docs, comments, and commit messages are in English.
- Keep the user's `.env` and secrets untracked.

## Code Style

- Internal imports use the `cli_app.` prefix. Ruff bans relative imports except in package `__init__.py`, which may re-export from sibling modules (`from .module import ...`, never `..`).
- Import a module or package whose name starts with `_` only from modules in the same package and its subpackages.
- MyPy runs with `strict = true` and the Pydantic plugin over `src/`, `tests/`, and `docs/`. All new code must have complete type annotations. Prefer `X | Y` over `Optional[X]`.

## Python Formatting

- Keep function signatures, calls, and collection literals on one line when they fit. When they need wrapping, put one parameter, argument, or item on each line. Add a trailing comma after the last entry when there are two or more entries so Ruff preserves the layout. Do not enable `COM812`.
- Omit optional trailing commas in single-entry forms. Keep the required comma in a single-element tuple and any comma Ruff inserts in a wrapped signature with one parameter.

## Documentation and Comments

- Keep documentation, docstrings, and comments short and factual. Describe each entity's purpose without editorial commentary or tutorials.
- Do not add module docstrings. Package docstrings in `__init__.py` are optional. Put package behavior and important module details in Markdown documentation such as `README.md` or `docs/`.
- Give public classes, functions, and ordinary methods a docstring. Prefer one line describing their overall purpose; do not repeat names, signatures, or type annotations. Ruff checks these in application code. Test functions, fixtures, and standard `dunder` methods are exempt.
- Add docstrings to protected or private objects only when they explain behavior that is not clear from code.
- Keep inline comments only for non-obvious behavior or decisions. Put a short comment on the relevant line when it fits; otherwise place it immediately above. Retain necessary tool directives such as `# noqa` and `# type: ignore`.
- A comment placed above a line or group of lines applies only to it. Separate that line or group from the code before and after it with a blank line, unless it starts or ends a block, so the comment's scope is clear. At module and class level, give each commented constant or attribute its own block, and keep uncommented related definitions together in one block.
- In long functions, methods, and tests, separate logical steps (input validation, setup, execution, result handling; arrange, act, assert) with a single blank line. Do not add comments to label the steps. Keep short functions compact.
- At module level, keep `UPPER_CASE` constants and lowercase objects (loggers, imported modules, apps, CLI runners) in separate blocks divided by a blank line.
- Prefer clearer names and more precise types over comments that restate code.

## Read when

| Task | Read |
| --- | --- |
| Any code change | [docs/architecture.md](docs/architecture.md) (layers, rules, invocation flow, errors, logging) |
| Working in `src/cli_app/cli/` or `src/cli_app/main.py`, adding a command | [CLI guide](docs/agents/src/cli_app/cli.md) |
| Working in `src/cli_app/services/` or adding a use case | [Services guide](docs/agents/src/cli_app/services.md) |
| Working in `src/cli_app/config/`, settings, `.env.example` | [Configuration guide](docs/agents/src/cli_app/config.md) |
| Working in `src/cli_app/utils/` (console, logging, output, stdin) | [Utilities guide](docs/agents/src/cli_app/utils.md) |
| Working in `tests/` | [Test guide](docs/agents/tests.md) |
| Working in `docs/`, `properdocs.yml`, or public docstrings | [Docs guide](docs/agents/docs.md) |
| Dependencies, `pyproject.toml`, `uv.lock` | [Dependency guide](docs/agents/pyproject.md) |
| CI, releases, docs deployment, Dependabot | [GitHub guide](docs/agents/github.md) |
| Renaming the template | [Renaming checklist](docs/notes.md#renaming-the-template) |
