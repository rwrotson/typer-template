# Utilities

- `utils` may import `config` and third-party packages, never `cli` or `services`.

| Module | Purpose |
|--------|---------|
| `utils/console.py` | Singleton Rich `Console` with theming, built from `ConsoleSettings` |
| `utils/log.py` | structlog setup; console and file handlers configured from `LogSettings` |
| `utils/output.py` | `OutputFormat` enum; `render_output()`, `echo_json()`, and `error_json()` helpers |
| `utils/stdin.py` | `is_stdin_piped()`, `read_stdin_if_piped()`, `iter_stdin_lines()` |
| `utils/meta.py` | Reads distribution metadata at runtime; scans `direct_url.json` for editable-install compat |
| `utils/format.py` | Rich `Theme` with `info`/`warning`/`danger` styles |
| `utils/emoji.py` | `Emoji` StrEnum for consistent emoji usage |
| `utils/progress.py` | Rich `Progress` bar wired to the project console |
| `utils/misc.py` | `find_project_root()` helper |

- `get_console()` and `get_project_meta()` cache their results; tests clear the console cache.
- JSON output goes to stdout through `render_output()`/`echo_json()`; diagnostics go to stderr. See the [output and stdin notes](../../../notes.md#output-format-pattern).

## Logging

- `setup_logging()` configures structlog bridged through stdlib via `ProcessorFormatter`: a stderr handler (`ConsoleRenderer`, or JSON with `CLI_APP_LOG__FORMAT=json`) and a rotating JSON file handler in the configured or platform user log directory. Without arguments it uses `LogSettings` defaults and never reads the environment.
- First-party code logs through `get_logger()` from `cli_app.utils.log`, so early logs go to stderr; third-party stdlib loggers share the same handler chain. Use a constant message and pass values as keyword fields. Do not call `structlog.configure()` or `logging.basicConfig()` elsewhere.
- `setup_logging(console=False)` installs a marked `NullHandler` instead of the stderr handler so `logging.lastResort` stays silent. Records logged with `extra=FILE_ONLY` skip the console handler and still reach the file handler; use it for errors the CLI prints itself.
- Calling `setup_logging()` again replaces only its own handlers; if creating a handler fails, the previous configuration stays.
- Before `setup_logging()` is called (for example in tests), structlog writes to stderr so it never pollutes stdout.
- `structlog.contextvars.bind_contextvars(key=value)` attaches context to every subsequent log line. See [the logging section](../../../architecture.md#logging) and the [structlog notes](../../../notes.md#structlog-integration).
