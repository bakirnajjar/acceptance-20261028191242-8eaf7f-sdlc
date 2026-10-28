# acceptance-20261028191242-8eaf7f-sdlc

Synthetic, disposable repository for a Futuristic Agentic SDLC deployed acceptance run
(batch acceptance-20261028191242-8eaf7f). The platform's agents deliver the generated application as a draft pull request.

## Python package scaffold

This is a Python 3.12 Flask/Jinja project using a `src/` package layout.
The current scaffold exposes an application factory but **no feature routes yet**;
the development server will return 404 for application pages until the later tasks
implement them. Do not use the Flask development server for production.

Install [uv](https://docs.astral.sh/uv/) and Python 3.12, then from the repository root:

```sh
uv sync --python 3.12 --locked
uv run --python 3.12 flask --app password_reset_exercise:create_app run
```

The development server listens on `127.0.0.1:5000` by default. To opt into
local debugging, set `FLASK_DEBUG=1` in your shell; do not use debug mode in
production. There are no required application environment variables or secrets
in this scaffold. Future recovery-specific settings will be documented when
those features are implemented.

Run the quality gates from the repository root:

```sh
# Build/syntax
uv run --python 3.12 python3.12 -m compileall -q src tests
# Tests
uv run --python 3.12 python3.12 -m pytest
# Lint and format
uv run --python 3.12 ruff check .
uv run --python 3.12 ruff format --check .
```

`uv.lock` pins the resolved dependency versions; use `uv sync --locked`
to reproduce them without updating the lockfile.
