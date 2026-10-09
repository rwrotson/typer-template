# Notes

## Build Backend

`uv_build` loads the `cli_app` package from `src/`:

```toml
[tool.uv.build-backend]
module-name = "cli_app"
module-root = "src"
```

## Package Metadata at Runtime

`cli_app.utils.meta` reads the installed distribution's name, version, and dependencies. Editable `uv_build` installs omit `top_level.txt`, so `Meta.load_from_installed_package()` resolves the distribution through `direct_url.json` before using `packages_distributions()`.

## structlog Integration

`cli_app.utils.log` connects [structlog](https://www.structlog.org/) to stdlib logging through `ProcessorFormatter`:

- `get_logger()` creates first-party loggers; third-party stdlib loggers use the same handlers.
- Console logs use Rich-style output or JSON when `CLI_APP_LOG_USE_JSON_FORMATTER=true`.
- File logs use JSON in the user log directory; `CLI_APP_LOG_DIR` overrides the directory.
- `structlog.contextvars.bind_contextvars()` adds fields to subsequent logs in the current context.

`main()` calls `setup_logging()`. Before setup, structlog writes to stderr to keep JSON command output on stdout valid.

## Output Format Pattern

Commands read `ctx.obj["output_format"]` from the root callback and call `render_output()`:

```python
render_output(
    {"key": value},
    fmt,
    text_render=lambda: console.print(...),
)
```

JSON output goes to stdout; diagnostics go to stderr. In text mode, `render_output()` uses `text_render` when provided and the Rich console otherwise.

## Stdin Piping Pattern

`read_stdin_if_piped()` returns `None` for a TTY and the available content for piped stdin:

```python
resolved = argument if argument is not None else read_stdin_if_piped()
if not resolved:
    raise Exit(1)
```

`CliRunner` provides non-TTY stdin in tests, even when no input is passed. The empty-string check rejects that case.

## Commitizen & Versioning

[Commitizen](https://commitizen-tools.github.io/commitizen/) reads Conventional Commit messages to select the next version and update `CHANGELOG.md`. Its settings are in `pyproject.toml`:

```toml
version_provider = "uv"
update_changelog_on_bump = true
major_version_zero = true
```

The `commit-msg` hook checks Conventional Commit format.

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
