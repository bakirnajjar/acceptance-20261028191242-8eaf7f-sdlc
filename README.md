# acceptance-20261028191242-8eaf7f-sdlc

Synthetic, disposable repository for a Futuristic Agentic SDLC deployed acceptance run
(batch acceptance-20261028191242-8eaf7f). The platform's agents deliver the generated application as a draft pull request.

## Python package scaffold

This is a Python 3.12 Flask/Jinja project using a `src/` package layout.
The application factory serves the sign-in page at `/sign-in` and the password
reset request form at `/password/forgot`. POSTing a valid form returns the same
generic confirmation for registered, unknown, and rate-limited addresses.
Registered synthetic accounts receive at most five private reset links in a
rolling hour. Reset-link redemption and sign-in success are not implemented yet;
the link path will return 404 until the next task.
Do not use the Flask development server for production.

Install [uv](https://docs.astral.sh/uv/) and Python 3.12, then from the repository root:

```sh
uv sync --python 3.12 --locked
uv run --python 3.12 flask --app password_reset_exercise:create_app run
```

The development server listens on `127.0.0.1:5000` by default. To opt into
local debugging, set `FLASK_DEBUG=1` in your shell; do not use debug mode in
production. Recovery settings (also injectable through `create_app` for tests):

- `PASSWORD_RESET_SECRET_KEY`: Flask session signing secret used for the
  session-bound recovery-form CSRF token. If omitted, a random secret is
  generated per application instance; configure a stable, private value in any
  persistent environment. Never put a real secret in source.
- `PASSWORD_RESET_ORIGIN`: trusted absolute HTTPS origin for private reset
  links (for example `https://example.test`); only local `http://localhost`
  and `http://127.0.0.1` are also accepted. The disposable local default is
  `http://localhost:5000`. Links never derive their origin from the HTTP Host.

Cookies are Secure, HttpOnly, and SameSite=Lax, so use HTTPS outside local
testing. The generated random default secret and local origin are development
defaults, not a production configuration. Accounts and owner-addressed link
notifications exist only in each application's private in-memory state; the
public confirmation never displays an address or link. Tests seed synthetic
accounts and inspect links via the private state, not a public mail service.

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
