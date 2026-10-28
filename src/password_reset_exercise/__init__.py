"""Application factory for the synthetic password recovery exercise."""

from flask import Flask, render_template

from password_reset_exercise.state import Clock, RecoveryState


def create_app(*, clock: Clock | None = None) -> Flask:
    """Create entry pages with isolated, private synthetic state per app."""
    app = Flask(__name__)
    app.extensions["recovery_state"] = RecoveryState(clock=clock)

    @app.get("/sign-in")
    def sign_in() -> str:
        return render_template("sign_in.html")

    @app.get("/password/forgot")
    def forgot_password() -> str:
        return render_template("forgot_password.html")

    return app
