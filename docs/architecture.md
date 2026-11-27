# Architecture

Commands are thin adapters: they read input, call a use case, and render its result. Use cases do not know about Typer, Rich, or configuration.

| Layer | Location | Responsibility | May import |
| --- | --- | --- | --- |
| Services | `cli_app/services/` | Use cases, their result types, and `ServiceError` subclasses | Services and the standard library |
| CLI | `cli_app/cli/` | Typer apps, options, `AppContext`, error reporting, output | All layers |
| Configuration | `cli_app/config/` | `Settings` with defaults in code, loaded from `CLI_APP_*` and `.env` | Pydantic and the standard library |
| Utilities | `cli_app/utils/` | Console, logging, output, stdin, metadata helpers | Configuration and third-party libraries |
| Entry point | `cli_app/main.py` | Validate configuration, set up logging, run the app | All layers |

### Rules

- Layers, from top to bottom: entry point, CLI, utilities and services (independent of each other), configuration. A layer may import any layer below it and never one above it.
- Services import no other layer and none of Typer, Click, Rich, structlog, Pydantic Settings, or platformdirs.
- A module or package whose name starts with `_` is imported only by modules in the same package and its subpackages.
- Only `load_settings()`, called from `main` and the root callback, reads the environment and `.env`. Other code receives settings as arguments, such as `setup_logging(settings.log)`.
- Every package with more than one module has an exhaustive `layers` contract: a new module must be added to it.
- Packages installed only as transitive dependencies are not imported directly.
- Scripts in `docs/` import only the modules they document, such as `cli_app.config.settings`.

import-linter checks the layers (exhaustively per package), the third-party packages of each layer, and direct imports of transitive dependencies with `uv run poe lint-imports`; the contracts are in `pyproject.toml`. Rules that the contracts do not cover are checked in review.

## An invocation through the layers

1. `main()` loads `Settings`. Invalid configuration is printed to stderr and exits with code 2. It then configures logging from `settings.log`.
2. The root callback in `cli/app.py` stores an `AppContext` (settings, console, output format) in `ctx.obj`. Commands read it with `get_app_context(ctx)`.
3. A command resolves its input (arguments, options, piped stdin) and calls a use case in `services/`.
4. The use case returns a result or raises a `ServiceError` subclass for an expected failure.
5. The command renders the result with `render_output()`: JSON on stdout for `--output-format json`, Rich text otherwise.

## Errors and exit codes

The root app uses `ServiceErrorGroup` (`cli/errors.py`). It catches `ServiceError` raised by any command, writes the message to stderr, and exits with the error's `exit_code`. With `--output-format json` the message is a JSON object, so stdout stays empty:

```json
{"error": {"type": "InvalidInputError", "message": "argument required (or pipe input via stdin)"}}
```

| Error | Exit code |
| --- | --- |
| `ServiceError` | 1 |
| `InvalidInputError` | 2, the same as Click usage errors |

Add a subclass with its own `exit_code` for each new kind of expected failure. Unexpected exceptions are not caught and keep their traceback. `ServiceErrorGroup` also logs the error with its traceback to the log file only (`extra=FILE_ONLY`), so the message appears on the console once.

## Logging

`cli_app.utils.log.setup_logging()` configures logging for one process:

1. Without arguments it uses the `LogSettings` defaults; it never reads the environment.
2. It creates all handlers first; if one fails, the previous configuration stays in place.
3. It replaces the handlers it created before and keeps all others.
4. It adds a stderr handler (console or JSON) and a rotating JSON file handler. With `console=False` it adds a no-op handler instead of the stderr handler, so `logging.lastResort` does not print either.
5. It configures structlog to render through the same stdlib handlers, so structlog and stdlib records share one format.

A record logged with `extra=FILE_ONLY` skips the console handler and still reaches the file handler. Use cases do not log the errors they raise; the CLI reports them.

## Adding a command

- Put the use case and its result type in `services/`. Raise a `ServiceError` subclass instead of calling `typer.Exit`.
- Add a command in `cli/commands/`: read `AppContext`, call the use case, render the result. Register the group in `cli/app.py`.
- Test the use case directly in `tests/services/` and the argument parsing, output, and exit codes with `CliRunner` in `tests/cli/`.

`services/example.py` and `cli/commands/command.py` show this split.
