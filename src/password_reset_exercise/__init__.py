"""Application factory for the synthetic password recovery exercise."""

from flask import Flask, render_template


def create_app() -> Flask:
    """Create the server-rendered entry pages for sign-in and recovery."""
    app = Flask(__name__)

    @app.get("/sign-in")
    def sign_in() -> str:
        return render_template("sign_in.html")

    @app.get("/password/forgot")
    def forgot_password() -> str:
        return render_template("forgot_password.html")

    return app
