"""Application factory for the synthetic password recovery exercise."""

from flask import Flask


def create_app() -> Flask:
    """Create an application; feature routes are added in later tasks."""
    return Flask(__name__)
