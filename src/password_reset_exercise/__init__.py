"""Application factory for the synthetic password recovery exercise."""

import os
import re
from secrets import compare_digest, token_urlsafe
from urllib.parse import urlsplit

from flask import Flask, render_template, request, session

from password_reset_exercise.state import Clock, RecoveryState

_EMAIL = re.compile(
    r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+",
    re.ASCII,
)


def _trusted_origin(value: str) -> str:
    """Accept one explicit web origin, never a request-supplied Host or path."""
    if any(char.isspace() or ord(char) < 32 for char in value) or any(
        char in value for char in ("?", "#", "\\")
    ):
        raise ValueError(
            "Reset link origin must not contain controls or URL parameters"
        )
    try:
        parts = urlsplit(value)
    except ValueError as exc:
        raise ValueError("Reset link origin must be a valid web origin") from exc
    if (
        parts.scheme not in ("http", "https")
        or not parts.hostname
        or re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", parts.hostname)
        is None
        or re.fullmatch(r"[A-Za-z0-9.-]+(?::[0-9]{1,5})?", parts.netloc) is None
        or parts.username is not None
        or parts.password is not None
        or parts.path not in ("", "/")
        or parts.query
        or parts.fragment
        or (parts.scheme == "http" and parts.hostname not in ("localhost", "127.0.0.1"))
    ):
        raise ValueError("Reset link origin must be an HTTPS origin (or local HTTP)")
    try:
        port = parts.port
    except ValueError as exc:
        raise ValueError("Reset link origin has an invalid port") from exc
    if not 0 < (port or 443) < 65536:
        raise ValueError("Reset link origin has an invalid port")
    return value.rstrip("/")


def _valid_email(value: str) -> bool:
    """Apply the same syntax check regardless of whether an account exists."""
    normalized = value.strip()
    local, separator, domain = normalized.partition("@")
    return (
        len(normalized) <= 254
        and bool(separator)
        and len(local) <= 64
        and not local.startswith(".")
        and not local.endswith(".")
        and ".." not in local
        and all(len(label) <= 63 for label in domain.split("."))
        and _EMAIL.fullmatch(normalized) is not None
    )


def create_app(
    *,
    clock: Clock | None = None,
    secret_key: str | None = None,
    reset_origin: str | None = None,
) -> Flask:
    """Create entry pages with isolated, private synthetic state per app."""
    app = Flask(__name__)
    # Per-process random default for the disposable local exercise; inject or set
    # a stable secret for a persistent instance. Neither is written to source.
    app.secret_key = (
        secret_key or os.environ.get("PASSWORD_RESET_SECRET_KEY") or (token_urlsafe(32))
    )
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    origin = _trusted_origin(
        reset_origin
        or os.environ.get("PASSWORD_RESET_ORIGIN")
        or "http://localhost:5000"
    )
    app.extensions["recovery_state"] = RecoveryState(clock=clock)

    @app.after_request
    def privacy_headers(response):
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; base-uri 'none'; form-action 'self'; "
            "frame-ancestors 'none'"
        )
        return response

    def form_csrf_token() -> str:
        if "recovery_csrf" not in session:
            session["recovery_csrf"] = token_urlsafe(32)
        return session["recovery_csrf"]

    def valid_csrf() -> bool:
        expected = session.get("recovery_csrf")
        provided = request.form.get("csrf_token", "")
        return (
            isinstance(expected, str)
            and isinstance(provided, str)
            and bool(expected)
            and compare_digest(expected, provided)
        )

    @app.get("/sign-in")
    def sign_in() -> str:
        return render_template("sign_in.html")

    @app.route("/password/forgot", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "GET":
            return render_template("forgot_password.html", csrf_token=form_csrf_token())

        if not valid_csrf():
            return (
                render_template(
                    "forgot_password.html",
                    csrf_token=form_csrf_token(),
                    form_error="Please refresh the form and try again.",
                ),
                400,
            )

        email = request.form.get("email", "")
        if not isinstance(email, str) or not _valid_email(email):
            return (
                render_template(
                    "forgot_password.html",
                    csrf_token=form_csrf_token(),
                    email_error="Enter a valid email address.",
                ),
                400,
            )

        app.extensions["recovery_state"].request_reset(email, origin)
        return render_template("request_received.html")

    @app.route("/password/reset/<token>", methods=["GET", "POST"])
    def reset_password(token: str):
        state: RecoveryState = app.extensions["recovery_state"]
        if not state.check_link(token):
            return render_template("reset_ineligible.html"), 410
        if request.method == "GET":
            return render_template("reset_password.html", csrf_token=form_csrf_token())

        if not valid_csrf():
            return (
                render_template(
                    "reset_password.html",
                    csrf_token=form_csrf_token(),
                    form_error="Please refresh the form and try again.",
                ),
                400,
            )
        new_password = request.form.get("new_password", "")
        if not isinstance(new_password, str) or not new_password.strip():
            return (
                render_template(
                    "reset_password.html",
                    csrf_token=form_csrf_token(),
                    password_error="Enter a new password.",
                ),
                400,
            )
        if not state.complete_reset(token, new_password):
            return render_template("reset_ineligible.html"), 410
        return render_template("reset_success.html")

    return app
