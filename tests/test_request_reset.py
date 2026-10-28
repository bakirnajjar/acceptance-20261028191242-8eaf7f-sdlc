"""TASK-003 request privacy, rolling allowance, and private issuance."""

import re
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from urllib.parse import urlsplit

import pytest

from password_reset_exercise import create_app
from password_reset_exercise.state import RecoveryState

ORIGIN = "https://trusted.example.test"
START = datetime(2026, 10, 28, 21, 20, 30, 123456, tzinfo=UTC)


def setup():
    """Give every test its own client, state, and controllable UTC clock."""
    now = [START]
    app = create_app(
        clock=lambda: now[0], secret_key="fixture-only-secret", reset_origin=ORIGIN
    )
    state: RecoveryState = app.extensions["recovery_state"]
    owner = state.register_account(" Owner@Example.test ", "private-password")
    client = app.test_client()
    response = client.get("/password/forgot")
    csrf = re.search(
        r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True)
    )
    assert csrf is not None
    return client, state, owner, now, csrf.group(1)


def submit(client, csrf, email):
    return client.post("/password/forgot", data={"email": email, "csrf_token": csrf})


def public_result(response):
    return (
        response.status_code,
        response.mimetype,
        response.headers.get("Location"),
        response.get_data(as_text=True),
    )


def test_tc_004_existing_unknown_have_identical_public_responses() -> None:
    client, state, owner, _, csrf = setup()
    accepted = submit(client, csrf, "  OWNER@EXAMPLE.TEST ")
    unknown = submit(client, csrf, "unknown@example.test")

    assert public_result(accepted) == public_result(unknown)
    assert accepted.status_code == 200
    assert 'href="/sign-in"' in accepted.get_data(as_text=True)
    assert 'role="status"' in accepted.get_data(as_text=True)
    assert len(state.notifications) == 1
    assert state.notifications[0].recipient == owner.normalized_email
    assert len(state._requests) == len(state._tokens) == 1
    assert len(state._accounts_by_id) == 1


def test_tc_022_request_confirmation_is_populated_server_rendered_html() -> None:
    client, _, _, _, csrf = setup()
    response = submit(client, csrf, "unknown@example.test")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert '<html lang="en">' in body
    assert "<main>" in body
    assert '<h1 id="page-heading">Request received</h1>' in body
    assert '<p role="status">' in body
    assert '<a class="back-link" href="/sign-in">' in body
    assert "<script" not in body


def test_tc_005_006_cap_never_changes_public_result_or_issues_sixth_link() -> None:
    client, state, _, _, csrf = setup()
    first = submit(client, csrf, "owner@example.test")
    for expected in range(2, 6):
        assert public_result(submit(client, csrf, "owner@example.test")) == (
            public_result(first)
        )
        assert len(state.notifications) == expected
    sixth = submit(client, csrf, "owner@example.test")
    unknown = submit(client, csrf, "unknown@example.test")
    assert public_result(first) == public_result(sixth) == public_result(unknown)
    assert len(state.notifications) == len(state._requests) == len(state._tokens) == 5
    for sensitive in (
        "owner@example.test",
        "unknown@example.test",
        state.notifications[0].link,
        "limit",
        "throttl",
    ):
        assert sensitive not in first.get_data(as_text=True).lower()
        assert sensitive not in sixth.get_data(as_text=True).lower()


def test_tc_007_019_first_five_are_per_synthetic_account() -> None:
    client, state, owner, _, csrf = setup()
    other = state.register_account("other@example.test", "second-password")
    for count in range(1, 6):
        assert submit(client, csrf, owner.normalized_email).status_code == 200
        assert (
            sum(n.recipient == owner.normalized_email for n in state.notifications)
            == count
        )
    assert submit(client, csrf, other.normalized_email).status_code == 200
    assert len(state.notifications) == 6
    assert state.notifications[-1].recipient == other.normalized_email
    assert [r.account_id for r in state._requests].count(other.account_id) == 1


def test_tc_008_oldest_falls_out_at_exact_rolling_hour_boundary() -> None:
    client, state, _, now, csrf = setup()
    for offset in (0, 1, 2, 3, 4):
        now[0] = START + timedelta(microseconds=offset)
        submit(client, csrf, "owner@example.test")
    now[0] = START + timedelta(hours=1, microseconds=-1)
    before = submit(client, csrf, "owner@example.test")
    assert len(state.notifications) == 5
    now[0] = START + timedelta(hours=1)
    at_boundary = submit(client, csrf, "owner@example.test")
    assert public_result(before) == public_result(at_boundary)
    assert len(state.notifications) == len(state._requests) == 6
    assert state._requests[-1].accepted_at == now[0]


def test_tc_009_020_030_link_only_in_private_sink_and_digest_only_in_state() -> None:
    client, state, owner, now, csrf = setup()
    response = submit(client, csrf, "owner@example.test")
    notice = state.notifications[0]
    assert notice.kind == "reset_link"
    assert notice.recipient == owner.normalized_email
    assert notice.timestamp == now[0]
    assert notice.link is not None
    link = urlsplit(notice.link)
    assert (link.scheme, link.netloc, link.path.rsplit("/", 1)[0]) == (
        "https",
        "trusted.example.test",
        "/password/reset",
    )
    raw = link.path.rsplit("/", 1)[-1]
    assert re.fullmatch(r"[A-Za-z0-9_-]{40,}", raw)
    assert link.query == link.fragment == ""
    digest = sha256(raw.encode("ascii")).hexdigest()
    token = state._tokens[digest]
    assert token.digest == digest
    assert token.account_id == owner.account_id
    assert token.issued_at == now[0]
    assert token.used is False
    assert raw not in repr(token)
    assert raw not in repr(state._tokens)
    assert raw not in response.get_data(as_text=True)
    assert notice.link not in response.get_data(as_text=True)
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "form-action 'self'" in response.headers["Content-Security-Policy"]
    for path in ("/notifications", "/sink", "/tokens", "/accounts"):
        assert client.get(path).status_code == 404
    # The reset form itself is deliberately reserved for TASK-004/T005.
    assert client.get(link.path).status_code == 404


def test_tc_028_invalid_email_has_associated_error_without_echo_or_issuance() -> None:
    client, state, _, _, csrf = setup()
    for invalid in ("", "no-at-sign", "owner@", "@example.test", "a@bad", "a@@b.test"):
        response = submit(client, csrf, invalid)
        body = response.get_data(as_text=True)
        assert response.status_code == 400
        assert 'aria-describedby="email-error"' in body
        assert 'id="email-error" role="alert"' in body
        assert "Enter a valid email address." in body
        if invalid:
            assert invalid not in body
    assert state.notifications == ()
    assert state._requests == []
    assert state._tokens == {}


def test_tc_030_missing_invalid_and_foreign_csrf_cannot_issue() -> None:
    client, state, _, _, csrf = setup()
    for proof in ("", "incorrect", csrf + "tamper"):
        response = submit(client, proof, "owner@example.test")
        assert response.status_code == 400
        assert "owner@example.test" not in response.get_data(as_text=True)
    foreign_client, _, _, _, foreign_csrf = setup()
    assert foreign_client is not client
    assert submit(client, foreign_csrf, "owner@example.test").status_code == 400
    assert state.notifications == ()
    assert state._requests == []
    assert submit(client, csrf, "owner@example.test").status_code == 200
    assert len(state.notifications) == 1


def test_tc_006_shared_lock_limits_concurrent_issuance() -> None:
    _, state, _, _, _ = setup()
    with ThreadPoolExecutor(max_workers=10) as pool:
        list(
            pool.map(
                lambda _: state.request_reset("owner@example.test", ORIGIN), range(10)
            )
        )
    assert len(state.notifications) == len(state._requests) == len(state._tokens) == 5
    assert len({n.link for n in state.notifications}) == 5


def test_tc_009_trusted_origin_rejects_untrusted_configuration(monkeypatch) -> None:
    for invalid in (
        "https://trusted.example.test.evil/path",
        "https://trusted.example.test@evil.test",
        "https://trusted.example.test/?token=evil",
        "https://trusted.example.test?",
        "https://trusted.example.test#",
        "https://trusted.example.test\\@evil.test",
        "http://evil.test",
        "javascript://evil.test",
    ):
        with pytest.raises(ValueError, match="Reset link origin"):
            create_app(reset_origin=invalid)
    monkeypatch.setenv("PASSWORD_RESET_ORIGIN", ORIGIN)
    monkeypatch.setenv("PASSWORD_RESET_SECRET_KEY", "fixture-env-secret")
    app = create_app()
    assert app.secret_key == "fixture-env-secret"
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    state = app.extensions["recovery_state"]
    state.register_account("owner@example.test", "password")
    client = app.test_client()
    csrf = re.search(
        r'name="csrf_token" value="([^"]+)"',
        client.get("/password/forgot").get_data(as_text=True),
    )
    assert csrf is not None
    submit(client, csrf.group(1), "owner@example.test")
    assert state.notifications[0].link.startswith(ORIGIN + "/password/reset/")
    assert state.notifications[0].link != "http://localhost:5000"


def test_tc_030_untrusted_request_host_never_controls_private_link() -> None:
    client, state, _, _, _ = setup()
    host = "https://attacker.example.test"
    get_response = client.get("/password/forgot", base_url=host)
    csrf = re.search(
        r'name="csrf_token" value="([^"]+)"', get_response.get_data(as_text=True)
    )
    assert csrf is not None
    response = client.post(
        "/password/forgot",
        base_url=host,
        data={"email": "owner@example.test", "csrf_token": csrf.group(1)},
    )
    assert response.status_code == 200
    assert len(state.notifications) == 1
    assert state.notifications[0].link.startswith(ORIGIN + "/password/reset/")
