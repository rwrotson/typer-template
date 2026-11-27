# CLI

- `cli` holds the Typer apps and is the only layer besides `main` that loads settings. Commands are thin adapters: read input, call a use case in `cli_app.services`, render the result. See [the invocation flow](../../../architecture.md#an-invocation-through-the-layers).
- `src/cli_app/main.py` is the `cli-app` console script (`cli_app.main:main`): it loads `Settings` (invalid configuration exits with code 2), calls `setup_logging(settings.log)` and `get_console()`, then `app()`.
- `cli/app.py` defines the root Typer app, registers subcommand groups, and declares the global options (`--version`, `--authors`, `--verbose`, `--output-format`). The root callback stores an `AppContext` (`cli/context.py`: settings, console, output format) in `ctx.obj`; commands read it with `get_app_context(ctx)`. `--verbose` lowers the root logger and its handlers to `DEBUG`.
- `cli/callbacks/` holds eager option callbacks that print metadata and exit.
- `cli/commands/` holds subcommand groups; each file creates its own Typer sub-app. To add a group: put the use case in `src/cli_app/services/`, create a file in `cli/commands/`, define a Typer app, export it from `cli/commands/__init__.py`, and add `app.add_typer(...)` in `cli/app.py`. `cli/commands/command.py` shows the pattern.
- Commands do not catch `ServiceError`. `ServiceErrorGroup` (`cli/errors.py`, the `cls` of the root app) maps errors in one place: it logs the error with `extra=FILE_ONLY`, prints `Error: ...` to stderr once (a JSON object with `--output-format json`), and exits with the error's `exit_code`. Other exceptions propagate with their traceback.
- Commands log through `get_logger()` from `cli_app.utils.log` and render output with `render_output()`; see the [utilities guide](utils.md).
- Test argument parsing, output, and exit codes with `CliRunner` in `tests/cli/`; see the [test guide](../../tests.md).
- When changing global options or commands, update README and the docs.
