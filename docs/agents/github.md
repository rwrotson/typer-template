# GitHub

- `.github/workflows/ci.yml` triggers on push/PR to `main` and `dev` and is reusable via `workflow_call`. Workflow permissions are `contents: read`; actions are pinned to commit SHAs. Parallel jobs:
    - **`quality`** — `poe fmt-check`, `poe lint`, `poe lint-imports`, `poe typecheck`.
    - **`test`** — `poe test` (95% branch coverage) on Ubuntu and macOS.
    - **`lowest`** — installs the lowest allowed direct dependencies (`--resolution lowest-direct`) and runs pytest; it checks the declared lower bounds, which the lock does not.
    - **`build`** — `uv build` with a wheel smoke test (the `cli-app` console script runs from site-packages), `properdocs build --strict`, `poe audit`, trivy filesystem scan (CRITICAL/HIGH).
- When tests need an external program, install it in the `test` job on both systems (`apt-get` on Linux, `brew list <tool> || brew install <tool>` on macOS) and in the `lowest` job.
- `.github/workflows/release.yml` triggers on version tags (`v*`) and manual `workflow_dispatch`. It runs CI first, then:
    - **`docs`** — version tags only (the `github-pages` environment accepts only `v*` tags, so manual runs only run CI); builds the site with `properdocs build --strict` and deploys it to **GitHub Pages** via `actions/upload-pages-artifact` + `actions/deploy-pages`. Permissions: `pages: write`, `id-token: write`, `contents: read`. The Pages artifact is named `github-pages-<run_attempt>` because reruns keep earlier attempts' artifacts and `deploy-pages` rejects duplicate names.
    - There is **no PyPI publish**.
- Pages Source must be set to **"GitHub Actions"** (Settings → Pages), and the `github-pages` environment must allow the `v*` tag (Settings → Environments → Deployment branches and tags → no restriction, or a `v*` rule). Site: https://rwrotson.github.io/typer-template/
- Dependabot opens weekly grouped PRs for uv dependencies (`uv.lock`), GitHub Actions, and pre-commit hooks (`.github/dependabot.yml`).
- `uv run pre-commit install` installs the pre-commit, commit-msg, and pre-push hooks; `uv run pre-commit run --all-files` runs them on all files.
