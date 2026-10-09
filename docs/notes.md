# Notes

## Build Backend

The project uses `uv_build` with the standard `src/` layout: source lives in `src/cli_app/`. This is the conventional approach and is configured with:

```toml
[tool.uv.build-backend]
module-name = "cli_app"
module-root = "src"
```

`module-root = "src"` tells uv_build to look for `./src/cli_app/__init__.py` as the package root.

## Package Metadata at Runtime

`src/cli_app/utils/meta.py` uses `importlib.metadata` to read the installed distribution's name, version, and dependencies. For editable installs (the default with `uv sync`), uv_build does not write a `top_level.txt`, so `packages_distributions()` cannot always map the `cli_app` package back to the `cli-app` distribution. Instead, `Meta.load_from_installed_package()` scans all installed distributions and finds the one whose `direct_url.json` points to a directory containing the current file.

## structlog Integration

Logging is built on [structlog](https://www.structlog.org/) bridged through stdlib's `logging` module via `ProcessorFormatter`. This means:

- **First-party loggers** use `get_logger()` from `utils/log.py` with keyword-argument context binding (`log.info("event", key=value)`).
- **Third-party stdlib loggers** (e.g. `httpx`, `sqlalchemy`) are automatically picked up by the same handler chain.
- **Console output** uses `ConsoleRenderer` (colourised, human-readable) by default, switching to `JSONRenderer` when `CLI_APP_LOG_USE_JSON_FORMATTER=true`.
- **File output** always writes JSON for structured log analysis. By default, logs are stored in the platform-specific user log directory; `CLI_APP_LOG_DIR` overrides it.
- `structlog.contextvars.bind_contextvars()` lets you attach fields that appear on every subsequent log line within a request or command invocation.

`setup_logging()` in `utils/log.py` is called at startup (`main.py`). Importing `get_logger()` also installs the early stderr fallback, so direct Typer app use cannot send debug logs to JSON stdout before startup.

## Output Format Pattern

Commands read `ctx.obj["output_format"]` (set by the root callback) and call `render_output()` from `utils/output.py`:

```python
render_output(
    {"key": value},  # data for JSON mode
    fmt,
    text_render=lambda: console.print(...),  # callable for text mode
)
```

This keeps JSON and human output co-located in the command while staying testable independently. JSON data goes to stdout; diagnostics go to stderr.

## Stdin Piping Pattern

`utils/stdin.py` provides `read_stdin_if_piped()` which returns `None` when stdin is a TTY (interactive) and the stdin content when piped. The recommended pattern is:

```python
resolved = argument if argument is not None else read_stdin_if_piped()
if not resolved:
    ...raise Exit(1)
```

This lets commands accept both `cli-app cmd arg` and `echo arg | cli-app cmd`.

Note: `CliRunner` in tests uses a BytesIO stdin whose `isatty()` returns `False`, so `is_stdin_piped()` always returns `True` in tests. Checking `if not resolved:` (rather than `if resolved is None:`) correctly rejects the empty-string case that CliRunner produces when no `input=` is given.

## Commitizen & Versioning

[Commitizen](https://commitizen-tools.github.io/commitizen/) reads Conventional Commit messages to determine the next version and generate CHANGELOG entries. Configuration lives in `[tool.commitizen]` in `pyproject.toml`:

```toml
version_provider = "uv"          # reads/writes the version in pyproject.toml
update_changelog_on_bump = true
major_version_zero = true        # 0.x.y — breaking changes don't force 1.0
```

The `commit-msg` pre-commit hook rejects commits that don't follow the format (`feat:`, `fix:`, `chore:`, etc.).

## Renaming the Template

Choose three names before editing: a distribution name (for example, `my-tool`), an import
package (`my_tool`), and a CLI command (`my-tool`). They can differ, but each use of a name
must stay consistent.

1. Rename `src/cli_app/` to `src/my_tool/`. Replace `cli_app` in imports throughout `src/`
   and `tests/`, including mock targets and the metadata test. Update `module-name` under
   `[tool.uv.build-backend]`, `[tool.coverage.run].source`, and
   `[tool.ruff.lint.isort].known-local-folder` in `pyproject.toml`.
2. Set `[project].name` and `[project.scripts]` in `pyproject.toml`. Point the script at
   `my_tool.main:main`. Update the project description, authors, keywords, and other metadata.
3. Change the `CLI_APP_` environment prefixes in `src/my_tool/core/settings.py`,
   `src/my_tool/utils/console.py`, and `src/my_tool/utils/log.py`. Update `.env.example`,
   README examples, and tests using those variables. Adjust the default log directory and
   filename in `src/my_tool/utils/log.py`.
4. Update `mkdocs.yml` (`site_name`, repository links, and the source watch path) and
   `docs/gen_ref_pages.py`, which scans the import package for API pages. Update names and
   links in README, docs, and `AGENTS.md`. If you host docs on GitHub Pages, configure Pages
   Source as **GitHub Actions** and allow release tags in the `github-pages` environment.
5. Regenerate the lockfile with `uv lock`, then run `uv sync --all-groups --locked`,
   `uv run pytest`, `uv build`, and `uv run --group docs mkdocs build`. Check that
   `uv run my-tool --help` and `uv run my-tool --version` show the new project identity.

The release workflow only deploys documentation. Add a separate publishing workflow if the
new project should publish packages to PyPI.
