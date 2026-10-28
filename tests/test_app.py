"""Smoke coverage for the initial application package."""

from flask import Flask

from password_reset_exercise import create_app


def test_application_factory_smoke() -> None:
    app = create_app()

    assert isinstance(app, Flask)
    assert app.test_client().get("/__smoke__").status_code == 404
