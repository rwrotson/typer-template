# Dependencies

- Put runtime imports in `[project].dependencies`, development tools in the `dev` group, and documentation tools in the `docs` group.
- Change dependencies through uv (`uv add`, `uv remove`) so `pyproject.toml` and `uv.lock` change together. Verify the lock with `uv sync --locked --all-groups`.
- Raise a direct dependency's lower bound when code needs a newer API. The locked environment does not check lower bounds; the CI `lowest` job does.
- Do not import packages that are installed only as transitive dependencies (for example `click`, which Typer vendors). The "Transitive dependencies are not imported directly" contract enforces this; add a package's import name there when a new transitive dependency appears in `uv.lock`.
- Add a new third-party dependency to the lowest layer that needs it and update the import-linter contracts that list each layer's forbidden packages.
- Security floors for transitive dependencies go in `[tool.uv] constraint-dependencies`.
- Use the project environment for tools. Do not install packages manually into `.venv`.
- `[tool.mypy] files` lists only existing directories (mypy fails on a missing path); when adding `scripts/`, add it there in the same change.
- The uv build backend loads `cli_app` from `src/` (`[tool.uv.build-backend]`, `module-name = "cli_app"`, `module-root = "src"`). `src/cli_app/py.typed` marks the package as typed (PEP 561); keep it in the wheel. See the [build backend notes](../notes.md#build-backend).
- Versioning: `uv run cz bump` bumps the version, updates `CHANGELOG.md`, and tags; `uv run cz changelog` updates the changelog only. Build with `uv build`.
