# Configuration

- `src/cli_app/config/settings.py` defines `Settings` (Pydantic `BaseSettings`, prefix `CLI_APP_`, nested delimiter `__`) with defaults in code and the sections `ConsoleSettings` (`CLI_APP_CONSOLE__*`) and `LogSettings` (`CLI_APP_LOG__*`).
- Only `load_settings()` reads the environment and `.env`; empty values use defaults. `main` and the root callback call it; `setup_logging()` and `build_console()` take a section instead of reading the environment themselves.
- `config` imports only Pydantic, Pydantic Settings, platformdirs, and the standard library; it imports no other layer.
- Every setting needs a `Field(description=...)` and a line in `.env.example`; tests in `tests/config/` enforce both. The docs configuration page is generated from `Settings`; see the [docs guide](../../docs.md).
- When changing settings, update `.env.example`, README, and the docs.
- A setting that holds a credential is a `SecretStr` and gets step-by-step instructions in a README "Credentials" section in the same change.
