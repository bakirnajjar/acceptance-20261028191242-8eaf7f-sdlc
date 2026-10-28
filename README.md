# acceptance-20261028191242-8eaf7f-sdlc

Synthetic, disposable repository for a Futuristic Agentic SDLC deployed acceptance run
(batch acceptance-20261028191242-8eaf7f). The platform's agents deliver the generated application as a draft pull request.

## Python package scaffold

This is a Python 3.12 Flask/Jinja project using a `src/` package layout.
The application factory serves the sign-in page at `/sign-in` and the password
reset request form at `/password/forgot`. POSTing a valid form returns the same
generic confirmation for registered, unknown, and rate-limited addresses.
Registered synthetic accounts receive at most five private reset links in a
rolling hour. An eligible link opens a new-password form, expires 30 minutes
after issuance, and can complete a reset only once. Sign-in success is not
implemented.

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
  generated per application instance; configure a stable, private value when
  running more than one instance or retaining cookies across restarts. Never
  put a real secret in source.
- `PASSWORD_RESET_ORIGIN`: trusted absolute HTTPS origin for private reset
  links (for example `https://example.test`); only local `http://localhost`
  and `http://127.0.0.1` are also accepted. The disposable local default is
  `http://localhost:5000`. Links never derive their origin from the HTTP Host.

Cookies are Secure, HttpOnly, and SameSite=Lax, so use HTTPS outside local
testing. The generated random default secret and local origin are development
defaults, not a production configuration. The public confirmation never
displays an address or link. Tests seed synthetic accounts and inspect links
via private state, not a public mail service.

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

## Production limitations (TC-025 / REQ-016)

**This exercise is not production ready.** Accounts are synthetic, seeded
through private application state; there is no real production identity
integration or successful sign-in flow. Reset-link and reset-success
notifications go only to a private in-memory sink, not a real mail provider;
no message is actually delivered to an account owner.

Account, accepted-request, reset-token, fixture-registered server-side
session, and notification-sink state are volatile and local to one application
process. **All of this state is lost on restart.** The in-process lock provides
no cross-worker consistency: separate worker processes cannot share account
records, rate limits, tokens, session generations, or notifications. Flask's
browser session cookie carries the recovery-form CSRF token and is signed
with the configured secret; it does not make the server-side recovery state
durable or shared.

Before any production use, this would need durable storage and coordinated
transactions for resets and state changes, a transactional outbox or
equivalent reliable notification delivery, real identity and mail integration,
retention/cleanup policies for sensitive records, signing-key rotation,
abuse prevention beyond the per-account request limit, and delivery and
failure monitoring. None is implemented here. Do not deploy this exercise
or use the Flask development server as a production server.
