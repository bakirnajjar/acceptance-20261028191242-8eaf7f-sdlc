"""TASK-005: TC-023/024 exercise behavior, not mere test discovery.

HTML/CSS checks elsewhere are structural; screenshot fidelity, browser contrast,
keyboard usability, and screen-reader announcements still require manual review.
"""

import re
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from threading import Barrier
from urllib.parse import urlsplit

from werkzeug.security import check_password_hash

from password_reset_exercise import create_app

START = datetime(2026, 10, 28, 19, 12, 42, 123456, tzinfo=UTC)


def environment():
    now = [START]
    app = create_app(
        clock=lambda: now[0],
        secret_key="verification-fixture-only",
        reset_origin="https://trusted.example.test",
    )
    state = app.extensions["recovery_state"]
    alice = state.register_account("alice@example.test", "original alice")
    bob = state.register_account("bob@example.test", "original bob")
    return app, state, alice, bob, now


def csrf_for(client, path):
    page = client.get(path)
    assert page.status_code == 200
    match = re.search(r'name="csrf_token" value="([^"]+)"', page.get_data(as_text=True))
    assert match is not None
    return match.group(1)


def request_link(client, state, csrf, email="alice@example.test"):
    before = len(state.notifications)
    response = client.post(
        "/password/forgot", data={"email": email, "csrf_token": csrf}
    )
    assert response.status_code == 200
    assert len(state.notifications) == before + 1
    notice = state.notifications[-1]
    assert (notice.kind, notice.recipient) == ("reset_link", email)
    assert notice.link is not None
    return response, urlsplit(notice.link).path


def reset(client, path, csrf, password):
    return client.post(path, data={"csrf_token": csrf, "new_password": password})


def public_response(response):
    return (
        response.status_code,
        response.mimetype,
        response.headers.get("Location"),
        response.get_data(as_text=True),
    )


def test_tc_023_entry_privacy_rolling_limit_and_private_sink_integration():
    """TC-023: hierarchy/link, accepted/unknown/capped parity, 5/6, hour, B, sink."""
    app, state, alice, bob, now = environment()
    client = app.test_client()
    sign_in = client.get("/sign-in")
    html = sign_in.get_data(as_text=True)
    assert sign_in.status_code == 200
    assert (
        '<section class="panel sign-in-panel" aria-labelledby="page-heading">' in html
    )
    assert html.index("Sign in</h1>") < html.index('for="email"')
    assert html.index('for="email"') < html.index('for="password"')
    assert html.index('for="password"') < html.index('href="/password/forgot"')
    assert html.index('href="/password/forgot"') < html.index("Sign in</button>")
    assert html.index("Sign in</button>") < html.index("Contact your administrator.")
    assert 'placeholder="name@example.com"' in html
    assert 'placeholder="********"' in html
    assert client.post("/sign-in").status_code == 405

    csrf = csrf_for(client, "/password/forgot")
    for offset in range(5):
        now[0] = START + timedelta(microseconds=offset)
        accepted, path = request_link(client, state, csrf)
        assert client.get(path).status_code == 200
        assert len(state.notifications) == offset + 1
    unknown = client.post(
        "/password/forgot",
        data={"email": "unknown@example.test", "csrf_token": csrf},
    )
    now[0] = START + timedelta(hours=1, microseconds=-1)
    capped = client.post(
        "/password/forgot",
        data={"email": alice.normalized_email, "csrf_token": csrf},
    )
    assert (
        public_response(accepted) == public_response(unknown) == public_response(capped)
    )
    assert len(state.notifications) == len(state._tokens) == len(state._requests) == 5
    assert all(
        notice.recipient == alice.normalized_email for notice in state.notifications
    )
    private_links = [notice.link for notice in state.notifications]
    assert len(set(private_links)) == 5
    for response in (accepted, unknown, capped):
        body = response.get_data(as_text=True)
        assert 'href="/sign-in"' in body
        assert 'role="status"' in body
        assert alice.normalized_email not in body
        assert alice.account_id not in body
        assert "unknown@example.test" not in body
        assert all(
            link not in body and link.rsplit("/", 1)[-1] not in body
            for link in private_links
        )
    assert client.get("/notifications").status_code == 404
    assert client.get("/tokens").status_code == 404

    # The allowance is per owner, not per client or per global request volume.
    bob_response, _ = request_link(client, state, csrf, bob.normalized_email)
    assert public_response(bob_response) == public_response(capped)
    now[0] = START + timedelta(hours=1)
    reopened, _ = request_link(client, state, csrf)
    assert public_response(reopened) == public_response(capped)
    assert [r.account_id for r in state._requests].count(alice.account_id) == 6
    assert [r.account_id for r in state._requests].count(bob.account_id) == 1
    assert state._requests[-1].accepted_at == now[0]


def test_tc_024_issue_time_expiry_replay_sessions_and_notices_integration():
    """TC-024: GET, just-before/exact/after deadline, replay, A/B, sessions, notices."""
    app, state, alice, bob, now = environment()
    old_alice = [state.register_session(alice.account_id) for _ in range(3)]
    old_bob = state.register_session(bob.account_id)
    assert all(
        state.is_session_active(s.server_side_id, alice.account_id) for s in old_alice
    )
    assert state.is_session_active(old_bob.server_side_id, bob.account_id)
    client = app.test_client()
    # Opening the request page precedes actual issuance; expiration starts at issue.
    csrf = csrf_for(client, "/password/forgot")
    now[0] += timedelta(minutes=2)
    paths = [request_link(client, state, csrf)[1] for _ in range(3)]
    issued = now[0]
    digests = [
        sha256(path.rsplit("/", 1)[-1].encode("ascii")).hexdigest() for path in paths
    ]
    assert all(state._tokens[d].issued_at == issued for d in digests)
    assert [n.kind for n in state.notifications] == ["reset_link"] * 3
    now[0] += timedelta(minutes=3)
    form_csrf = [csrf_for(client, path) for path in paths]
    assert all(state._tokens[d].used is False for d in digests)
    assert client.get(paths[0]).status_code == 200
    assert state._tokens[digests[0]].used is False

    now[0] = issued + timedelta(minutes=30, microseconds=-1)
    success = reset(client, paths[0], form_csrf[0], "new alice")
    assert success.status_code == 200
    assert "Password reset complete" in success.get_data(as_text=True)
    assert state._tokens[digests[0]].used is True
    changed = state.account_for_email(alice.normalized_email)
    assert changed.session_generation == alice.session_generation + 1
    assert check_password_hash(changed.password_hash, "new alice")
    assert not check_password_hash(changed.password_hash, "original alice")
    assert state.account_for_email(bob.normalized_email) == bob
    assert all(
        not state.is_session_active(s.server_side_id, alice.account_id)
        for s in old_alice
    )
    assert state.is_session_active(old_bob.server_side_id, bob.account_id)
    assert [(n.kind, n.recipient, n.link) for n in state.notifications[3:]] == [
        ("reset_success", alice.normalized_email, None)
    ]
    assert state.notifications[-1].timestamp == now[0]
    snapshot = (dict(state._accounts_by_id), dict(state._tokens), state.notifications)
    rejected = [reset(client, paths[0], form_csrf[0], "replayed")]
    now[0] = issued + timedelta(minutes=30)
    rejected.append(reset(client, paths[1], form_csrf[1], "exact"))
    now[0] += timedelta(microseconds=1)
    rejected.append(reset(client, paths[2], form_csrf[2], "late"))
    for response, path in zip(rejected, paths, strict=True):
        assert response.status_code == 410
        body = response.get_data(as_text=True)
        assert "Password reset complete" not in body
        assert path.rsplit("/", 1)[-1] not in body
    assert (dict(state._accounts_by_id), dict(state._tokens), state.notifications) == (
        snapshot
    )
    assert all(client.get(path).status_code == 410 for path in paths)


def test_tc_024_competing_posts_have_single_owner_notice_and_no_loser_effect():
    """TC-024: two distinct Flask clients race one token; the loser changes nothing."""
    app, state, alice, bob, _ = environment()
    clients = [app.test_client(), app.test_client()]
    csrf = csrf_for(clients[0], "/password/forgot")
    _, path = request_link(clients[0], state, csrf)
    forms = [csrf_for(client, path) for client in clients]
    assert state.notifications[0].recipient == alice.normalized_email
    assert len(state.notifications) == 1
    barrier = Barrier(2)

    def compete(client, proof, password):
        barrier.wait(timeout=10)
        return password, reset(client, path, proof, password)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(compete, client, proof, password)
            for client, proof, password in zip(
                clients, forms, ("alpha", "beta"), strict=True
            )
        ]
        results = [future.result(timeout=20) for future in futures]
    winners = [
        password for password, response in results if response.status_code == 200
    ]
    losers = [response for _, response in results if response.status_code == 410]
    assert len(winners) == len(losers) == 1
    assert "Password reset complete" not in losers[0].get_data(as_text=True)
    updated = state.account_for_email(alice.normalized_email)
    assert updated.session_generation == alice.session_generation + 1
    assert check_password_hash(updated.password_hash, winners[0])
    assert state.account_for_email(bob.normalized_email) == bob
    assert [n.kind for n in state.notifications] == ["reset_link", "reset_success"]
    assert state.notifications[-1].recipient == alice.normalized_email
    assert sum(token.used for token in state._tokens.values()) == 1
