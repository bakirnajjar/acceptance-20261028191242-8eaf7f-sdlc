"""Structural entry-page coverage; visual and assistive-technology checks remain manual."""

import sys
from html.parser import HTMLParser

from flask import Flask

from password_reset_exercise import create_app


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[tuple[str, str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.events.append(("start", tag, dict(attrs)))

    def handle_data(self, data: str) -> None:
        if text := data.strip():
            self.events.append(("text", text, {}))


def page(html: str) -> Page:
    document = Page()
    document.feed(html)
    return document


def element(
    document: Page, tag: str, **attributes: str
) -> tuple[int, dict[str, str | None]]:
    for index, (kind, value, attrs) in enumerate(document.events):
        if (
            kind == "start"
            and value == tag
            and all(attrs.get(key) == expected for key, expected in attributes.items())
        ):
            return index, attrs
    raise AssertionError(f"Missing <{tag}> with attributes {attributes}")


def next_text(document: Page, index: int) -> str:
    return next(
        value for kind, value, _ in document.events[index + 1 :] if kind == "text"
    )


def test_tc_001_sign_in_surface_structure() -> None:
    """TC-001: Assert the observed hierarchy and linked styles, not pixel fidelity."""
    client = create_app().test_client()
    response = client.get("/sign-in")
    assert response.status_code == 200
    document = page(response.get_data(as_text=True))

    heading, _ = element(document, "h1")
    assert next_text(document, heading) == "Sign in"
    assert next_text(document, element(document, "label", **{"for": "email"})[0]) == (
        "Email address"
    )
    email, email_attrs = element(document, "input", id="email")
    assert email_attrs["placeholder"] == "name@example.com"
    assert next_text(
        document, element(document, "label", **{"for": "password"})[0]
    ) == ("Password")
    password, password_attrs = element(document, "input", id="password")
    assert password_attrs["type"] == "password"
    assert password_attrs["placeholder"] == "********"
    link, _ = element(document, "a", href="/password/forgot")
    assert next_text(document, link) == "Forgot password?"
    button, _ = element(document, "button", type="submit")
    assert next_text(document, button) == "Sign in"
    footer, _ = element(document, "p", **{"class": "footer-note"})
    assert next_text(document, footer) == "No account? Contact your administrator."
    assert heading < email < password < link < button < footer

    _, style = element(document, "link", rel="stylesheet")
    stylesheet = client.get(style["href"])
    assert stylesheet.status_code == 200
    css = stylesheet.get_data(as_text=True)
    assert "place-items: center" in css
    assert "border: 1px solid" in css
    assert "background: #fff" in css
    assert "text-decoration: underline" in css
    assert "width: 100%" in css


def test_tc_002_sign_in_labels_and_control_order() -> None:
    """TC-002: Check programmatic names, input types, order and focus CSS only."""
    document = page(create_app().test_client().get("/sign-in").get_data(as_text=True))
    email_label, _ = element(document, "label", **{"for": "email"})
    email_input, email = element(document, "input", id="email")
    password_label, _ = element(document, "label", **{"for": "password"})
    password_input, password = element(document, "input", id="password")
    recovery_link, _ = element(document, "a", href="/password/forgot")
    submit, _ = element(document, "button", type="submit")
    assert (
        email_label
        < email_input
        < password_label
        < password_input
        < recovery_link
        < submit
    )
    assert email["type"] == "email"
    assert password["type"] == "password"
    assert next_text(document, email_label) == "Email address"
    assert next_text(document, password_label) == "Password"
    assert next_text(document, recovery_link) == "Forgot password?"
    assert next_text(document, submit) == "Sign in"
    assert ":focus-visible" in (
        create_app().test_client().get("/static/style.css").get_data(as_text=True)
    )


def test_tc_003_recovery_link_reaches_request_form() -> None:
    """TC-003: The actual anchor navigates to a server-rendered email request."""
    client = create_app().test_client()
    sign_in = page(client.get("/sign-in").get_data(as_text=True))
    _, anchor = element(sign_in, "a", href="/password/forgot")
    response = client.get(anchor["href"])
    assert response.status_code == 200
    request = page(response.get_data(as_text=True))
    _, email = element(request, "input", id="email")
    assert email["name"] == "email"
    assert email["type"] == "email"


def test_tc_003_unimplemented_submissions_do_not_claim_success() -> None:
    """The entry forms deliberately have no POST handler in TASK-001."""
    client = create_app().test_client()
    assert (
        client.post(
            "/sign-in", data={"email": "a@example.com", "password": "x"}
        ).status_code
        == 405
    )
    assert (
        client.post("/password/forgot", data={"email": "a@example.com"}).status_code
        == 405
    )


def test_tc_021_python312_flask_serves_sign_in() -> None:
    """TC-021: The declared runtime is Python 3.12 and the factory serves Flask."""
    assert sys.version_info[:2] == (3, 12)
    app = create_app()
    assert isinstance(app, Flask)
    assert app.test_client().get("/sign-in").status_code == 200


def test_tc_022_entry_pages_have_server_rendered_content() -> None:
    """TC-022 (partial): Inspect raw sign-in and request responses without JS."""
    client = create_app().test_client()
    for path, heading in (
        ("/sign-in", "Sign in"),
        ("/password/forgot", "Forgot password"),
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert response.mimetype == "text/html"
        document = page(response.get_data(as_text=True))
        element(document, "html", lang="en")
        element(document, "main")
        index, _ = element(document, "h1")
        assert next_text(document, index) == heading
        element(document, "form", method="post")
        assert not any(
            kind == "start" and tag == "script" for kind, tag, _ in document.events
        )


def test_tc_028_request_controls_have_labels_and_navigation() -> None:
    """TC-028 (partial): Request GET has names, logical order and visible focus CSS."""
    client = create_app().test_client()
    document = page(client.get("/password/forgot").get_data(as_text=True))
    label, _ = element(document, "label", **{"for": "email"})
    email_index, email = element(document, "input", id="email")
    submit, _ = element(document, "button", type="submit")
    back, _ = element(document, "a", href="/sign-in")
    assert next_text(document, label) == "Email address"
    assert email["type"] == "email"
    assert email["required"] is None
    assert next_text(document, submit) == "Request password reset"
    assert next_text(document, back) == "Back to sign in"
    assert label < email_index < submit < back
    assert client.get("/sign-in").status_code == 200
    assert ":focus-visible" in client.get("/static/style.css").get_data(as_text=True)
