"""Partial TC-017/019/020/030 evidence for TASK-002's fixture-only state."""

from datetime import UTC, datetime, timedelta, timezone

import pytest
from werkzeug.security import check_password_hash

from password_reset_exercise import create_app
from password_reset_exercise.state import (
    Notification,
    RecoveryState,
    ResetRequest,
    ResetToken,
)


def test_tc_019_synthetic_accounts_have_normalized_keys_and_hashes() -> None:
    """TC-019 (partial): Synthetic accounts require no identity integration."""
    state = RecoveryState()
    account = state.register_account("  Alice@Example.TEST ", "fixture password")
    other = state.register_account("bob@example.test", "another fixture password")

    assert account.account_id != other.account_id
    assert account.normalized_email == "alice@example.test"
    assert account.password_hash != "fixture password"
    assert check_password_hash(account.password_hash, "fixture password")
    assert not check_password_hash(account.password_hash, "wrong password")
    assert state.account_for_email(" ALICE@example.test ") == account
    assert state.account_for_email("missing@example.test") is None
    with pytest.raises(ValueError, match="already exists"):
        state.register_account("alice@EXAMPLE.test", "replacement")
    assert state.account_for_email("alice@example.test") == account


def test_tc_017_fixture_sessions_require_current_owner_generation() -> None:
    """TC-017 (partial): Revocation logic; no reset completion or login yet."""
    state = RecoveryState()
    alice = state.register_account("alice@example.test", "alice password")
    bob = state.register_account("bob@example.test", "bob password")
    first = state.register_session(alice.account_id)
    second = state.register_session(alice.account_id)
    unrelated = state.register_session(bob.account_id)

    assert first.server_side_id != second.server_side_id
    assert first.saved_generation == second.saved_generation == 0
    assert all(
        state.is_session_active(session.server_side_id, alice.account_id)
        for session in (first, second)
    )
    assert state.is_session_active(unrelated.server_side_id, bob.account_id)
    assert not state.is_session_active(first.server_side_id, bob.account_id)
    assert not state.is_session_active("unknown-server-side-id", alice.account_id)

    state.advance_session_generation(alice.account_id)
    assert not state.is_session_active(first.server_side_id, alice.account_id)
    assert not state.is_session_active(second.server_side_id, alice.account_id)
    assert state.is_session_active(unrelated.server_side_id, bob.account_id)
    fresh = state.register_session(alice.account_id)
    assert fresh.saved_generation == 1
    assert state.is_session_active(fresh.server_side_id, alice.account_id)


def test_tc_020_private_sink_enforces_owner_link_and_success_shapes() -> None:
    """TC-020 (partial): Fixtures may inspect notices; no delivery is claimed."""
    instant = datetime(2026, 10, 28, 21, 0, tzinfo=UTC)
    state = RecoveryState(clock=lambda: instant)
    owner = state.register_account("Owner@Example.test", "fixture password")
    link = "https://example.test/password/reset/fixture-only"
    reset_link = state.record_notification("reset_link", owner.account_id, link=link)
    success = state.record_notification("reset_success", owner.account_id)

    assert reset_link == Notification("reset_link", "owner@example.test", instant, link)
    assert success == Notification("reset_success", "owner@example.test", instant)
    assert success.link is None
    assert state.notifications == (reset_link, success)
    with pytest.raises(ValueError, match="Only reset_link"):
        state.record_notification("reset_link", owner.account_id)
    with pytest.raises(ValueError, match="Only reset_link"):
        state.record_notification("reset_success", owner.account_id, link=link)
    with pytest.raises(KeyError):
        state.record_notification("reset_success", "unknown-account")
    assert state.notifications == (reset_link, success)


def test_tc_019_020_app_instances_have_independent_private_state() -> None:
    """TC-019/020 (partial): Accounts, sessions and notices are per factory call."""
    first_app = create_app()
    second_app = create_app()
    first: RecoveryState = first_app.extensions["recovery_state"]
    second: RecoveryState = second_app.extensions["recovery_state"]
    owner = first.register_account("owner@example.test", "fixture password")
    session = first.register_session(owner.account_id)
    first.record_notification("reset_success", owner.account_id)

    assert first is not second
    assert second.account_for_email("owner@example.test") is None
    assert not second.is_session_active(session.server_side_id, owner.account_id)
    assert second.notifications == ()
    second_owner = second.register_account("owner@example.test", "other password")
    assert second_owner.account_id != owner.account_id
    assert second.notifications == ()


def test_tc_030_state_has_no_public_inspection_or_authentication_routes() -> None:
    """TC-030 (partial): GET entry pages cannot expose seeded private state."""
    app = create_app()
    state: RecoveryState = app.extensions["recovery_state"]
    owner = state.register_account("hidden@example.test", "private-password")
    session = state.register_session(owner.account_id)
    private_link = "https://example.test/password/reset/fixture-only"
    state.record_notification("reset_link", owner.account_id, link=private_link)
    client = app.test_client()

    for path in ("/sign-in", "/password/forgot"):
        response = client.get(path)
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        for secret in (
            owner.normalized_email,
            owner.account_id,
            owner.password_hash,
            session.server_side_id,
            private_link,
        ):
            assert secret not in body
    for path in ("/accounts", "/tokens", "/sessions", "/notifications", "/sink"):
        assert client.get(path).status_code == 404
    assert (
        client.post("/sign-in", data={"email": owner.normalized_email}).status_code
        == 405
    )


def test_injected_clock_requires_aware_utc_and_models_record_exact_times() -> None:
    instant = datetime(2026, 10, 28, 21, 0, tzinfo=UTC)
    state = RecoveryState(clock=lambda: instant)
    owner = state.register_account("clock@example.test", "fixture password")
    accepted = ResetRequest(owner.account_id, state.now())
    token = ResetToken("digest-of-fixture", owner.account_id, state.now())
    assert accepted.accepted_at == token.issued_at == instant
    assert token.used is False

    for bad_time in (
        instant.replace(tzinfo=None),
        instant.astimezone(timezone(timedelta(hours=2))),
    ):
        with pytest.raises(ValueError, match="timezone-aware UTC"):
            RecoveryState(clock=lambda value=bad_time: value).now()
