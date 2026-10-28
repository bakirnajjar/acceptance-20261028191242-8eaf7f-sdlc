# Solution design — synthetic password recovery

**Status:** Proposed architecture and future implementation tasks, not an implemented application, passing test result, or deployment. This document covers the approved `requirements_analysis` identifiers REQ-001–REQ-018 and considers the approved `ui_analysis` and prospective `acceptance_20261028191242_8eaf7f_risk` checks RD8CDC-001–RD8CDC-006. Those predecessor outputs supplied no independent stage-output reference locator; citations below are only to the original evidence.

| Citation | Exact original source reference | Authority |
| --- | --- | --- |
| [STORY] | `{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}` | Python 3.12, Flask, server-rendered pages, synthetic accounts, in-memory notification sink, pytest, production limitations, and no deployment or deployment workflows. |
| [IMAGE] | `{"source_type":"attachment","source_id":"457acc5e-8bce-44d6-abec-d204c28e4d84","locator":"sign-in-wireframe.png"}` | Sign-in appearance only. The reader supplied a reference rather than image pixels; the host-observed description and approved UI analysis supply the visual observations. |
| [STANDARD] | `{"source_type":"knowledge","source_id":"28e06fb4-ccd1-4117-8f7b-b2a6c9bfaf1f","locator":"v1, chunk 0"}` | ACC-STD-01/02/03: account-independent request response and five requests per account per hour; one-use links expiring 30 minutes after issuance and all-session sign-out; owner notification after every successful reset. |

## Scope and component interactions

A Python 3.12 Flask **application factory** wires server-rendered Jinja templates and route handlers to a recovery service, an injected UTC clock, a synchronized in-process state container, and a test-inspectable but nonpublic notification sink. The state container holds synthetic accounts, accepted request timestamps, token digests, and server-side sessions; a shared lock surrounds issuance and completion check-and-write sequences. There is no public account inventory, notification-sink browser view, or token-inspection endpoint. Authentication success is **not** specified by the sign-in image; this design does not claim a working login or prescribe its successful destination. [STORY] [IMAGE] [STANDARD]

The sign-in page is a white page with a centered bordered panel, bold **Sign in** heading, labeled **Email address** and **Password** fields with `name@example.com` and masked `********` placeholders, a blue underlined **Forgot password?** link below the password field and above a wide dark **Sign in** button, and a muted **No account? Contact your administrator.** footer. Exact dimensions and color codes are not established. The image does not establish an actual link destination, recovery-page appearance, or sign-in success semantics; a functioning recovery link is required separately by REQ-002/ACC-STD-01. [IMAGE] [STANDARD]

### Proposed HTTP and service contracts

Route names, error copy, and layouts for recovery are **design choices**, not visual facts:

| Route | Input and private work | Public result |
| --- | --- | --- |
| `GET /sign-in` | No recovery input. | Render sign-in HTML matching the observed hierarchy, with an `href` to `/password/forgot`; no implied successful-login handler. |
| `GET /password/forgot` | No account lookup. | Render a labeled email request form; its styling and copy remain provisional. |
| `POST /password/forgot` | Form `email` and CSRF proof; normalize for lookup; `request_reset(normalized_email, now)` privately determines eligibility. | For otherwise equivalent **valid** existing, unknown, and at-limit submissions, the same visible status, response class, content, and navigation (e.g., one generic confirmation). Format errors, if any, are independent of account existence. Never expose link issuance or throttle state. |
| `GET /password/reset/<token>` | `check_link(raw_token, now)` validates digest, unused flag, and expiry, but does **not** consume. | Render a labeled new-password form if eligible; otherwise a non-success state with a request-another-link action. Never echo the token in visible copy. |
| `POST /password/reset/<token>` | Form `new_password` and CSRF proof; `complete_reset(raw_token, new_password, now)` rechecks eligibility at submission. | Only after all in-process successful-reset effects, render/redirect to a server-rendered success state with sign-in navigation. Invalid, used, or expired links never produce a success state or successful side effects. |

`request_reset` returns a public outcome independent of eligibility. For an eligible existing account, under the same lock it counts accepted timestamps strictly newer than `now - 1 hour`; the first five within that rolling window each record a link, while the sixth records none. At exactly the rollover boundary the oldest accepted request falls out. Unknown accounts are neither created nor sent a link. The link contains a cryptographically random opaque value (e.g., `secrets.token_urlsafe`); storage retains its digest and the **UTC issuance time**, not the raw token. Only the private sink's `reset_link` record includes the actual link. [STORY] [STANDARD; REQ-003–REQ-005]

`check_link` compares a token digest and tests `unused && now < issued_at + 30 minutes`: at precisely the 30-minute instant it is ineligible, measured from *issuance*, not request, notification, or first-open time. A GET does not reserve or consume the token. `complete_reset` validates a nonempty password, hashes it (a maintained Flask-compatible utility such as Werkzeug is a proposed choice), and rechecks the token, stored account, and current time inside the completion lock. On success it replaces **only that account's password hash**, marks the token used, advances its session-generation counter, and appends **one** owner-directed `reset_success` sink entry after the state changes and before reporting success. Replayed or competing submissions cannot both succeed. Failed completion must not falsely report success; an implementation should stage/roll back in-process changes if the sink append fails. The exercise cannot guarantee crash-atomic or durable effects. No password-complexity rule or confirmation field is supplied. [STORY] [STANDARD; REQ-006–REQ-010]

`is_session_active(session_id, account_id)` requires a live server-side session associated with that account **and** a session generation equal to the account's current generation. Completion increments the generation in the same critical section; every session created before the reset therefore fails its next authorization check, even if its browser cookie remains. Test fixtures can register multiple synthetic sessions without claiming the sign-in button implements login. If a later specified login flow creates authenticated sessions, **every** authenticated request must apply this check. Clearing only the resetting browser's cookie is insufficient. [STANDARD; REQ-009]

Recovery forms and status pages should use persistent labels, logical keyboard order, visible focus, readable contrast, actionable associated errors, neutral progress, and clearly announced generic success/non-success states. These are **proposed** accessibility and UI practices from `ui_analysis`, not an observed recovery-page design or an additional password policy. [STORY] [IMAGE] [STANDARD]

## State, persistence, and migration

| In-process record | Fields / invariant |
| --- | --- |
| `Account` | Stable internal `account_id`, normalized email key, password **hash**, monotonic `session_generation`; synthetic only. |
| `ResetRequest` | `account_id`, `accepted_at` UTC; retain/count accepted existing-account requests in the rolling interval `(now - 1 hour, now]`. Counting and issuing share a lock. |
| `ResetToken` | Token digest, `account_id`, exact UTC `issued_at`, `used`; eligible only before `issued_at + 30 minutes` and before first successful completion. Raw values are never stored in the token table or exposed in generic responses. |
| `Session` | Unpredictable server-side session ID, account ID, generation at creation, and active state where maintained; a signed/client cookie alone cannot authorize access. |
| `Notification` | `kind` (`reset_link` or `reset_success`), owner recipient, timestamp; only `reset_link` has a private link. A success notice contains neither password nor token. |

Normalize email consistently (e.g., trim and case-fold for lookup); format checks must not leak account existence. Inject a timezone-aware UTC clock for deterministic tests of rollover and the just-before/exactly-at/after-expiry boundary. This is **one-process, volatile** state: restart loses accounts, counters, tokens, sessions, and notifications; multi-worker execution has no shared rate cap or atomicity guarantee. There is no data migration in this exercise. Production replacement would require separately designed durable account/request/token/session/notification stores, transactional or outbox-backed effects, legacy-state migration, retention, key management, and cross-worker coordination; none is authorized implementation or a proposed hosting target. [STORY] [STANDARD]

## Decisions, alternatives, and constraints

| Proposed decision | Alternative considered | Reason and qualification |
| --- | --- | --- |
| Python 3.12 Flask factory with server-rendered Jinja HTML. | SPA/client-only rendering or another runtime. | Directly meets REQ-013/REQ-014 without introducing an unrelated frontend architecture. [STORY] |
| One injectable, locked in-memory state container and private notification sink. | External database, identity provider, queue, or mail service. | Keeps synthetic exercise fixtures observable and check-and-write operations consistent within **one process**; not durable or production safe. [STORY] [STANDARD] |
| Per-account rolling accepted-request timestamps, counting `(now - 1 hour, now]`, and one generic public response. | Fixed wall-clock-hour bucket, per-IP-only throttling, or a distinct rate-limit page. | Enforces five in the preceding hour without boundary bursts or a publicly exposed throttle/account indicator. Further abuse controls remain production work. [STANDARD] |
| Unpredictable opaque tokens with stored digests and exact issue-time UTC expiry. | Sequential/plaintext tokens or expiry measured at link opening/sending. | Limits exposure, supports single use and the required exact 30-minute issuance boundary; token-bearing URLs still require protection. [STANDARD] |
| Password hashes in synthetic account records. | Plaintext/reversible passwords or production identity integration. | Protects demonstration account data without inventing a required complexity policy; confirm the hashing utility during implementation. [STORY] |
| Server-side session registry with account revocation generation. | Clearing only the current browser cookie or relying solely on stateless client sessions. | Rejects **all** earlier active sessions; fixture-backed checks remain possible before login behavior is specified. [STANDARD] |
| Synchronously append one owner-directed success notice for each successful completion before public success. | Actual email or relying on a success page as proof of delivery. | Supports private, inspectable in-memory notifications; crash durability and real delivery remain unproven. [STORY] [STANDARD] |

## Security, reliability, and operations

- A token authorizes a reset for its **stored account**, never for an account chosen in form data. CSRF protection is proposed for both POST forms, with configured (not checked-in) secret material, safe session-cookie settings, escaped server templates, and a restrictive referrer/content policy. Build reset links using a configured trusted origin, not an unchecked Host header. Prevent token-bearing URLs, submitted email, passwords, and links from reaching application logs, analytics, public errors, or cross-origin referrers. [STORY] [STANDARD]
- The identical public request outcome covers equivalent valid existing, unknown, and at-limit cases; no public sink/introspection endpoint is allowed. Basic response equality is testable, but exact network-timing indistinguishability is **not** established and is a production limitation. An invalid/malformed/reused/expired token must not change a password, invalidate sessions, or emit a success notice. A link opened while valid still requires a fresh POST eligibility check. [STANDARD]
- The single lock protects concurrent in-process rate decisions and token completion, so two simultaneous submissions of one link cannot both succeed. It does not protect state against a process crash, restart, multiple workers, or real notification failure. On any in-process failure, do not present a false success; external transactions and delivery guarantees are outside this exercise. [STORY] [STANDARD]
- Proposed local privacy-safe observability counts generic request attempts, private link issuances, throttling, successes, rejected resets, and sink failures, without identifying account or token data in public responses or logs. No external monitoring, mail delivery, deployment target, or infrastructure is requested. Documentation must explicitly disclose synthetic accounts, ephemeral single-process storage, lost rate/session state at restart, lack of cross-worker consistency, private nondelivered notices, and missing production account, notification, security, and operations integrations. [STORY] [STANDARD]

## Dependency-ordered implementation tasks

These are **future** independently reviewable slices, not completed work. The task descriptions and acceptance checks below match `solution_design.json`. Citations in each heading refer to the exact original references in the evidence table; no predecessor-stage locator is invented.

### TASK-001 — Build Flask sign-in shell and recovery entry [STORY] [IMAGE] [STANDARD]

**Requirements:** REQ-001, REQ-002, REQ-013, REQ-014. **Depends on:** none.

Set up a Python 3.12 Flask application factory and server-rendered templates. Render the observed sign-in panel and a working Forgot password? link to a server-rendered reset-request form. Keep sign-in authentication and successful-login destination unspecified; the wireframe does not define them. Proposed recovery-page copy and styling are not wireframe facts.

1. On Python 3.12, Flask serves rendered HTML for the sign-in and reset-request pages; a browser can follow the sign-in Forgot password? link to the request form.
2. The sign-in page displays a centered bordered panel with bold Sign in heading, labeled Email address and Password fields with name@example.com and masked ******** placeholders, a blue underlined Forgot password? link below the password field, a wide dark Sign in button below the link, and a muted No account? Contact your administrator. footer; exact pixels and color values are not asserted.

### TASK-002 — Implement injectable synthetic recovery state [STORY] [STANDARD]

**Requirements:** REQ-009, REQ-011, REQ-012. **Depends on:** none.

Provide in-process synthetic accounts with hashed passwords, synchronized request timestamps and token-digest records, an injected UTC clock, a test-inspectable but nonpublic notification sink, and server-side account/session-generation checks. Allow fixtures to register multiple sessions without inventing sign-in success behavior. Keep sensitive state out of visitor responses.

1. A test can construct a synthetic account with a hashed password, register two independent active sessions, record and inspect internal reset-link and reset-success notification kinds, and observe no production account or external notification dependency.
2. A session check rejects a registered session whose saved generation differs from its account's current generation; no public endpoint exposes the account inventory, token state, or notification sink.

### TASK-003 — Implement private reset-request eligibility and link issuance [STORY] [STANDARD]

**Requirements:** REQ-003, REQ-004, REQ-005. **Depends on:** TASK-001, TASK-002.

Connect the server-rendered request form to a service using the synthetic state. Normalize an email for lookup, count accepted requests per existing account over the preceding rolling hour under a shared lock, and privately issue an opaque single-account link into the in-memory sink only for an accepted existing-account request. Present an account-independent generic response for equivalent valid existing, unknown, and at-limit requests; never expose issuance or throttle decisions.

1. Equivalent valid requests for an existing account, an unknown account, and an existing account at its cap have identical public status, rendered content, and response/navigation class, without account or throttle disclosure.
2. With controlled time, the first five requests for an existing account in a rolling hour each record one reset link; a sixth inside that hour records none and receives the same generic response; once the oldest accepted request is outside the preceding hour, another can issue a link.

### TASK-004 — Complete single-use resets and post-reset effects [STORY] [STANDARD]

**Requirements:** REQ-006, REQ-007, REQ-008, REQ-009, REQ-010. **Depends on:** TASK-002, TASK-003.

Implement server-rendered new-password, ineligible-link, and success states. Check opaque token eligibility against its private digest and exact issue time, then recheck on POST and atomically update the token's account password hash, consume the token, advance that account's session generation, and append an owner-directed success notice before reporting success. Reject expired, malformed, and replayed tokens without successful side effects. A GET never consumes a token; do not assume a specified login destination or password-complexity rule.

1. An eligible unused link submitted before issue_time + 30 minutes updates only its associated account's password and succeeds once; at exactly issue_time + 30 minutes or later it is ineligible, and a consumed link cannot complete a second reset.
2. For an account with multiple previously active sessions, each successful reset makes every earlier session fail subsequent authorization checks and records one owner-directed reset-success notice in the private sink for that success; rejected or replayed submissions neither change a password nor record a success notice.
3. Two submissions of one eligible link cannot both succeed, and rendered success is returned only after the password change, token consumption, session invalidation, and notification entry complete in-process.

### TASK-005 — Verify sign-in and recovery behavior with pytest [STORY] [IMAGE] [STANDARD]

**Requirements:** REQ-015. **Depends on:** TASK-001, TASK-002, TASK-003, TASK-004.

Add pytest coverage using the Flask client, synthetic accounts, controlled issue-time clock, multiple session fixtures, and private sink inspection. Verify the sign-in visual hierarchy and navigation, generic response equality including at the cap, rolling-hour issuance, token use/replay and exact expiry boundary, password change, all-session invalidation, and notification after each success. Treat risk items as prospective checks, not recorded defects.

1. Running pytest checks the rendered sign-in evidence and recovery navigation, existing/unknown/at-limit public response equality, first-five/sixth-request/rolling-hour link counts, and absence of public notification-sink disclosure.
2. Running pytest checks token submission just before, at, and after issue_time + 30 minutes; replay and competing submissions; correct password update; invalidation of multiple earlier active sessions; and one owner notice for each successful reset without a notice for rejected attempts.

### TASK-006 — Document production limitations and verify no deployment [STORY]

**Requirements:** REQ-016, REQ-017, REQ-018. **Depends on:** TASK-005.

Document synthetic accounts, volatile single-process account/token/request/session state, in-memory rather than externally delivered notifications, restart and cross-worker limitations, and unresolved production hardening. Review delivered actions and changed paths to verify no application deployment and no added deployment workflow. This is documentation and negative-scope verification, not deployment authorization.

1. Project documentation explicitly identifies synthetic-account and in-memory-notification limitations, lost state at restart, lack of cross-worker durability, and the absence of a production account or mail integration; it does not claim production readiness.
2. Review of delivery actions finds no performed deployment, and review of repository changes finds no added deployment workflow.

### Coverage and verification alignment

| Requirement IDs | Implementing / verifying tasks |
| --- | --- |
| REQ-001, REQ-002, REQ-013, REQ-014 | TASK-001; TASK-005 verifies behavior. |
| REQ-003, REQ-004, REQ-005 | TASK-003; TASK-005 verifies behavior. |
| REQ-006, REQ-007, REQ-008, REQ-010 | TASK-004; TASK-005 verifies behavior. |
| REQ-009 | TASK-002 and TASK-004; TASK-005 verifies multiple-session invalidation without assuming login success. |
| REQ-011, REQ-012 | TASK-002; TASK-005 verifies exercise boundaries. |
| REQ-015 | TASK-005. |
| REQ-016, REQ-017, REQ-018 | TASK-006; REQ-017/018 are negative-scope checks, **not** deployment tasks. |

All REQ-001–REQ-018 have implementation or negative-scope verification task coverage; `coverage_dispositions` is empty. Prospective risks map RD8CDC-001 → TASK-001/005; RD8CDC-002 → TASK-003/005; RD8CDC-003/004 → TASK-004/005; RD8CDC-005 → TASK-002/005/006; RD8CDC-006 → TASK-005/006. These links are planning coverage, not test results. The proposed future test command is `python3.12 -m pytest`; no build or lint command/package manager was specified, and hosting is **none**. [STORY] [IMAGE] [STANDARD]

## Explicit assumptions and open questions

**Assumptions and evidence limits:** The sign-in image shows appearance only; the attachment reader returned a reference, while visual observations were host-supplied and also appear in approved UI analysis. Routes, account-state modeling, token storage, CSRF implementation, accessibility choices, local diagnostics, and rollback handling are proposals, not evidence of existing code. The sink and synthetic accounts are private, volatile exercise mechanisms; no production integration, durable delivery, deployment, or workflow is implied. No independent stage-output source-reference locator was supplied; approved predecessor IDs are used for coverage without fabricating citations.

1. **Nonblocking — sign-in and sessions:** What sign-in authentication behavior, successful-login destination, and live-session creation model are expected? Until clarified, use a fixture-testable session registry for REQ-009; do not infer authentication from the wireframe. [IMAGE] [STANDARD]
2. **Nonblocking — recovery appearance:** What exact copy, layout, and styling should the request, generic-response, new-password, invalid-link, and success pages use? Only sign-in has visual evidence; functional accessible states remain proposals. [IMAGE] [STORY]
3. **Nonblocking — password policy:** What new-password validation rules and optional confirmation field should apply? Require a nonempty value and hash for now; no complexity rule was supplied. [STORY]
4. **Nonblocking — ineligible-link presentation:** Should malformed, expired, and reused links share one non-success page and which return actions should it offer? None may complete a reset; a common page with a request-another-link action is provisional. [STANDARD]
