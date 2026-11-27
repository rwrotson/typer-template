# Services

- `services` holds use cases, their result types, and the `ServiceError` hierarchy. It imports only the standard library and other `services` modules: never Typer, Click, Rich, structlog, Pydantic Settings, platformdirs, `cli_app.cli`, `cli_app.config`, or `cli_app.utils`. import-linter enforces this.
- Use cases take plain values (or settings sections passed by the caller) as arguments and return a result; they do not print or read the environment.
- Expected failures raise a `ServiceError` subclass with its own `exit_code` class attribute instead of `typer.Exit`. `InvalidInputError` exits with 2, the same as Click usage errors. Add the new error to [the error table](../../../architecture.md#errors-and-exit-codes).
- Use cases do not log the errors they raise; `ServiceErrorGroup` reports them.
- To add a use case: put it in `src/cli_app/services/`, test it directly in `tests/services/`, and expose it through a command; see the [CLI guide](cli.md). `services/example.py` shows the pattern.
