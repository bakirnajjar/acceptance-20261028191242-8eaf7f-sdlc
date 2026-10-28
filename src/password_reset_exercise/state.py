"""Private, single-process synthetic recovery state; no authentication routes."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from threading import RLock
from typing import Literal

from werkzeug.security import generate_password_hash

type Clock = Callable[[], datetime]
type NotificationKind = Literal["reset_link", "reset_success"]


def utc_now() -> datetime:
    """Default clock; injectable so recovery timing does not depend on wall time."""
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class Account:
    account_id: str
    normalized_email: str
    password_hash: str
    session_generation: int = 0


@dataclass(frozen=True, slots=True)
class ResetRequest:
    account_id: str
    accepted_at: datetime


@dataclass(frozen=True, slots=True)
class ResetToken:
    digest: str
    account_id: str
    issued_at: datetime
    used: bool = False


@dataclass(frozen=True, slots=True)
class Session:
    server_side_id: str
    account_id: str
    saved_generation: int


@dataclass(frozen=True, slots=True)
class Notification:
    kind: NotificationKind
    recipient: str
    timestamp: datetime
    link: str | None = None


class RecoveryState:
    """One app's volatile store and private sink, protected by one shared lock.

    Future request and completion operations must hold ``_lock`` across their
    entire check-and-write sequences, including changes to requests, tokens,
    accounts, sessions and notifications.
    """

    def __init__(self, clock: Clock | None = None) -> None:
        self._clock = clock if clock is not None else utc_now
        self._lock = RLock()
        self._accounts_by_id: dict[str, Account] = {}
        self._account_ids_by_email: dict[str, str] = {}
        self._requests: list[ResetRequest] = []
        self._tokens: dict[str, ResetToken] = {}
        self._sessions: dict[str, Session] = {}
        self._notifications: list[Notification] = []

    def now(self) -> datetime:
        """Return UTC or reject an invalid injected clock before recording time."""
        current = self._clock()
        if current.tzinfo is None or current.utcoffset() != timedelta(0):
            raise ValueError("Recovery clock must return a timezone-aware UTC time")
        return current.astimezone(UTC)

    def register_account(self, email: str, password: str) -> Account:
        """Seed a synthetic account, never a production identity or plain password."""
        normalized_email = email.strip().casefold()
        if not normalized_email:
            raise ValueError("An account needs an email address")
        password_hash = generate_password_hash(password)
        with self._lock:
            if normalized_email in self._account_ids_by_email:
                raise ValueError("Synthetic account already exists")
            account = Account(token_urlsafe(24), normalized_email, password_hash)
            self._accounts_by_id[account.account_id] = account
            self._account_ids_by_email[normalized_email] = account.account_id
            return account

    def account_for_email(self, email: str) -> Account | None:
        """Fixture/service-only lookup; never attach it to a visitor endpoint."""
        with self._lock:
            account_id = self._account_ids_by_email.get(email.strip().casefold())
            return self._accounts_by_id.get(account_id) if account_id else None

    def register_session(self, account_id: str) -> Session:
        """Register a fixture session without defining any sign-in success flow."""
        with self._lock:
            account = self._accounts_by_id[account_id]
            session = Session(token_urlsafe(32), account_id, account.session_generation)
            self._sessions[session.server_side_id] = session
            return session

    def is_session_active(self, server_side_id: str, account_id: str) -> bool:
        """Authorize only a registered session for this account and generation."""
        with self._lock:
            session = self._sessions.get(server_side_id)
            account = self._accounts_by_id.get(account_id)
            return (
                session is not None
                and account is not None
                and session.account_id == account_id
                and session.saved_generation == account.session_generation
            )

    def advance_session_generation(self, account_id: str) -> None:
        """Fixture hook for simulating revocation; completion will use this lock."""
        with self._lock:
            account = self._accounts_by_id[account_id]
            self._accounts_by_id[account_id] = replace(
                account, session_generation=account.session_generation + 1
            )

    def record_notification(
        self, kind: NotificationKind, account_id: str, *, link: str | None = None
    ) -> Notification:
        """Fixture-only sink append, addressed to an account owner, not a route."""
        if kind not in ("reset_link", "reset_success"):
            raise ValueError("Unknown recovery notification kind")
        if (kind == "reset_link" and not link) or (
            kind == "reset_success" and link is not None
        ):
            raise ValueError("Only reset_link notifications carry a link")
        with self._lock:
            account = self._accounts_by_id[account_id]
            notification = Notification(
                kind, account.normalized_email, self.now(), link
            )
            self._notifications.append(notification)
            return notification

    @property
    def notifications(self) -> tuple[Notification, ...]:
        """A read-only snapshot for private test fixtures."""
        with self._lock:
            return tuple(self._notifications)
