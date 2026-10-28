"""TASK-004: traceable reset lifecycle and private post-reset effects."""

import re
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from threading import Barrier
from urllib.parse import urlsplit

from werkzeug.security import check_password_hash

from password_reset_exercise import create_app

START = datetime(2026, 10, 28, 20, 0, 0, 123456, tzinfo=UTC)


def setup():
    now = [START]
    app = create_app(
        clock=lambda: now[0],
        secret_key="synthetic-fixture-secret",
        reset_origin="https://trusted.example.test",
    )
    state = app.extensions["recovery_state"]
    alice = state.register_account("alice@example.test", "old alice")
    bob = state.register_account("bob@example.test", "old bob")
    return app, state, alice, bob, now


def csrf_for(client, path):
    response = client.get(path)
    assert response.status_code == 200
    match = re.search(
        r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True)
    )
    assert match is not None
    return match.group(1)


def issue(state, client, email="alice@example.test"):
    csrf = csrf_for(client, "/password/forgot")
    before = len(state.notifications)
    response = client.post(
        "/password/forgot", data={"csrf_token": csrf, "email": email}
    )
    assert response.status_code == 200
    assert len(state.notifications) == before + 1
    notice = state.notifications[-1]
    assert notice.kind == "reset_link"
    return urlsplit(notice.link).path


def record(state):
    return (
        dict(state._accounts_by_id),
        dict(state._tokens),
        dict(state._sessions),
        list(state._requests),
        state.notifications,
    )


def post(client, path, csrf, password="replacement", **extra):
    return client.post(
        path, data={"csrf_token": csrf, "new_password": password, **extra}
    )


def test_tc_010_replay_has_no_effect_and_get_does_not_consume():
    app, state, alice, _, _ = setup()
    client = app.test_client()
    path = issue(state, client)
    csrf = csrf_for(client, path)
    assert csrf_for(client, path) == csrf
    digest = sha256(path.rsplit("/", 1)[-1].encode("ascii")).hexdigest()
    assert state._tokens[digest].used is False
    first = post(client, path, csrf, "first new password")
    assert first.status_code == 200
    assert "Password reset complete" in first.get_data(as_text=True)
    assert state._tokens[digest].used is True
    snapshot = record(state)
    second = post(client, path, csrf, "second new password")
    assert second.status_code == 410
    assert "Password reset complete" not in second.get_data(as_text=True)
    assert record(state) == snapshot
    assert check_password_hash(
        state.account_for_email(alice.normalized_email).password_hash,
        "first new password",
    )
    assert client.get(path).status_code == 410


def test_tc_011_simultaneous_posts_from_distinct_clients_have_one_winner():
    app, state, alice, _, _ = setup()
    first_client, second_client = app.test_client(), app.test_client()
    path = issue(state, first_client)
    first_csrf = csrf_for(first_client, path)
    second_csrf = csrf_for(second_client, path)
    assert first_csrf != second_csrf
    old_generation = alice.session_generation
    ready = Barrier(2)

    def compete(client, csrf, password):
        ready.wait(timeout=10)
        return password, post(client, path, csrf, password)

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(compete, first_client, first_csrf, "alpha winner")
        second = pool.submit(compete, second_client, second_csrf, "beta winner")
        results = (first.result(timeout=20), second.result(timeout=20))

    winners = [
        password for password, response in results if response.status_code == 200
    ]
    losers = [response for _, response in results if response.status_code == 410]
    assert len(winners) == len(losers) == 1
    assert "Password reset complete" not in losers[0].get_data(as_text=True)
    updated = state.account_for_email(alice.normalized_email)
    assert updated.session_generation == old_generation + 1
    assert check_password_hash(updated.password_hash, winners[0])
    assert sum(n.kind == "reset_success" for n in state.notifications) == 1
    assert sum(token.used for token in state._tokens.values()) == 1


def test_tc_012_expiry_measured_from_issuance_not_request_or_open():
    app, state, alice, _, now = setup()
    client = app.test_client()
    # The private issuance is two minutes after the hypothetical request start.
    now[0] = START + timedelta(minutes=2)
    path = issue(state, client)
    issued = next(iter(state._tokens.values())).issued_at
    assert issued == START + timedelta(minutes=2)
    now[0] = START + timedelta(minutes=4)
    assert state.notifications[0].timestamp == issued
    now[0] = START + timedelta(minutes=5)
    csrf = csrf_for(client, path)
    now[0] = issued + timedelta(minutes=30, microseconds=-1)
    result = post(client, path, csrf)
    assert result.status_code == 200
    assert check_password_hash(
        state.account_for_email(alice.normalized_email).password_hash, "replacement"
    )


def test_tc_013_exact_and_after_expiry_are_ineligible_even_if_opened():
    app, state, alice, _, now = setup()
    client = app.test_client()
    first_path = issue(state, client)
    second_path = issue(state, client)
    first_csrf = csrf_for(client, first_path)
    second_csrf = csrf_for(client, second_path)
    assert first_path != second_path
    snapshot = record(state)
    now[0] = START + timedelta(minutes=30)
    for path, csrf in ((first_path, first_csrf), (second_path, second_csrf)):
        if path == second_path:
            now[0] += timedelta(microseconds=1)
        result = post(client, path, csrf)
        assert result.status_code == 410
        assert "Password reset complete" not in result.get_data(as_text=True)
        assert client.get(path).status_code == 410
        assert record(state) == snapshot
    assert check_password_hash(
        state.account_for_email(alice.normalized_email).password_hash, "old alice"
    )


def test_tc_014_017_only_bound_account_changes_and_all_old_sessions_revoke():
    app, state, alice, bob, _ = setup()
    alice_sessions = [state.register_session(alice.account_id) for _ in range(2)]
    bob_session = state.register_session(bob.account_id)
    assert all(
        state.is_session_active(s.server_side_id, alice.account_id)
        for s in alice_sessions
    )
    assert state.is_session_active(bob_session.server_side_id, bob.account_id)
    client = app.test_client()
    path = issue(state, client)
    csrf = csrf_for(client, path)
    assert post(client, path, csrf, "my new value").status_code == 200
    updated = state.account_for_email(alice.normalized_email)
    assert updated.password_hash != alice.password_hash
    assert updated.password_hash != "my new value"
    assert check_password_hash(updated.password_hash, "my new value")
    assert not check_password_hash(updated.password_hash, "old alice")
    assert state.account_for_email(bob.normalized_email) == bob
    assert all(
        not state.is_session_active(s.server_side_id, alice.account_id)
        for s in alice_sessions
    )
    assert state.is_session_active(bob_session.server_side_id, bob.account_id)
    fresh = state.register_session(alice.account_id)
    assert state.is_session_active(fresh.server_side_id, alice.account_id)


def test_tc_015_malformed_unknown_and_account_tampering_never_redirect_binding():
    app, state, alice, bob, _ = setup()
    client = app.test_client()
    path = issue(state, client)
    csrf = csrf_for(client, path)
    snapshot = record(state)
    for bad_path in (
        "/password/reset/not-a-token",
        "/password/reset/" + "A" * 43,
        path[:-1] + ("A" if path[-1] != "A" else "B"),
    ):
        for result in (client.get(bad_path), post(client, bad_path, csrf)):
            assert result.status_code == 410
            body = result.get_data(as_text=True)
            assert bad_path.rsplit("/", 1)[-1] not in body
            assert "Password reset complete" not in body
        assert record(state) == snapshot
    assert (
        post(
            client,
            path,
            csrf,
            "bound password",
            account_id=bob.account_id,
            email=bob.normalized_email,
        ).status_code
        == 200
    )
    assert state.account_for_email(bob.normalized_email) == bob
    assert check_password_hash(
        state.account_for_email(alice.normalized_email).password_hash, "bound password"
    )
    snapshot = record(state)
    assert post(client, path, csrf, "try again").status_code == 410
    assert record(state) == snapshot


def test_tc_016_029_empty_password_has_field_error_and_can_retry():
    app, state, alice, _, _ = setup()
    client = app.test_client()
    path = issue(state, client)
    csrf = csrf_for(client, path)
    snapshot = record(state)
    for empty in ("", "  "):
        response = post(client, path, csrf, empty)
        body = response.get_data(as_text=True)
        assert response.status_code == 400
        assert 'aria-describedby="password-error"' in body
        assert 'id="password-error" role="alert"' in body
        assert "Enter a new password." in body
        assert "Password reset complete" not in body
        assert record(state) == snapshot
    assert post(client, path, csrf, "x").status_code == 200
    assert check_password_hash(
        state.account_for_email(alice.normalized_email).password_hash, "x"
    )


def test_tc_018_two_distinct_resets_each_notify_owner_once_before_public_success():
    app, state, alice, _, _ = setup()
    client = app.test_client()
    for number in (1, 2):
        path = issue(state, client)
        csrf = csrf_for(client, path)
        before = sum(n.kind == "reset_success" for n in state.notifications)
        result = post(client, path, csrf, f"password {number}")
        assert result.status_code == 200
        assert sum(n.kind == "reset_success" for n in state.notifications) == before + 1
        notice = state.notifications[-1]
        assert (notice.kind, notice.recipient, notice.link) == (
            "reset_success",
            alice.normalized_email,
            None,
        )
        assert notice.timestamp == START
        assert "Password reset complete" in result.get_data(as_text=True)
        snapshot = record(state)
        assert post(client, path, csrf).status_code == 410
        assert record(state) == snapshot
    assert [n.kind for n in state.notifications] == [
        "reset_link",
        "reset_success",
        "reset_link",
        "reset_success",
    ]
    now_expired = issue(state, client)
    state._clock = lambda: START + timedelta(minutes=30)
    snapshot = record(state)
    assert post(client, now_expired, csrf).status_code == 410
    assert post(client, "/password/reset/invalid", csrf).status_code == 410
    assert record(state) == snapshot


def test_tc_020_022_029_server_rendered_private_and_accessible_states():
    app, state, alice, _, now = setup()
    client = app.test_client()
    path = issue(state, client)
    token = path.rsplit("/", 1)[-1]
    response = client.get(path)
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert '<html lang="en">' in body
    assert '<h1 id="page-heading">Reset password</h1>' in body
    assert '<label for="new-password">New password</label>' in body
    assert 'id="new-password" name="new_password" type="password"' in body
    assert 'autocomplete="new-password" required' in body
    assert '<button type="submit">Reset password</button>' in body
    assert 'href="/password/forgot"' in body
    assert "<script" not in body
    assert token not in body and alice.normalized_email not in body
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "form-action 'self'" in response.headers["Content-Security-Policy"]
    csrf = csrf_for(client, path)
    success = post(client, path, csrf)
    assert success.status_code == 200
    assert 'role="status"' in success.get_data(as_text=True)
    assert 'href="/sign-in"' in success.get_data(as_text=True)
    for response in (success, client.get(path)):
        body = response.get_data(as_text=True)
        assert response.mimetype == "text/html"
        assert token not in body and alice.normalized_email not in body
        assert "<script" not in body
    rejection = client.get(path)
    assert rejection.status_code == 410
    assert 'role="alert"' in rejection.get_data(as_text=True)
    assert 'href="/password/forgot"' in rejection.get_data(as_text=True)
    assert 'href="/sign-in"' in rejection.get_data(as_text=True)
    expired_path = issue(state, client)
    now[0] += timedelta(minutes=30)
    expired = client.get(expired_path)
    assert expired.status_code == 410
    assert 'role="alert"' in expired.get_data(as_text=True)
    assert len(state.notifications) == 3
    for route in ("/tokens", "/notifications", "/sink"):
        assert client.get(route).status_code == 404


def test_tc_015_016_invalid_csrf_never_consumes_or_notifies():
    app, state, alice, _, _ = setup()
    client = app.test_client()
    path = issue(state, client)
    csrf = csrf_for(client, path)
    foreign = csrf_for(app.test_client(), path)
    snapshot = record(state)
    for proof in ("", "tampered", foreign):
        response = post(client, path, proof)
        assert response.status_code == 400
        assert 'role="alert"' in response.get_data(as_text=True)
        assert path.rsplit("/", 1)[-1] not in response.get_data(as_text=True)
        assert record(state) == snapshot
    assert post(client, path, csrf).status_code == 200
    assert state.account_for_email(alice.normalized_email).session_generation == 1


def test_tc_018_sink_failure_rolls_back_and_never_reports_success():
    app, state, alice, _, _ = setup()
    client = app.test_client()
    path = issue(state, client)
    csrf = csrf_for(client, path)
    snapshot = record(state)

    class FailedSink(list):
        def append(self, item):
            super().append(item)
            raise RuntimeError("synthetic sink failure")

    state._notifications = FailedSink(state.notifications)
    response = post(client, path, csrf)
    assert response.status_code != 200
    assert "Password reset complete" not in response.get_data(as_text=True)
    assert record(state) == snapshot
    assert check_password_hash(
        state.account_for_email(alice.normalized_email).password_hash, "old alice"
    )
    state._notifications = list(state.notifications)
    assert post(client, path, csrf).status_code == 200
