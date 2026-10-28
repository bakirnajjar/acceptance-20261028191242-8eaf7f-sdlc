# Requirements analysis

Schema version: `1.0`  
Stage: `requirements_analysis`

## Source references

- **S — story:** `{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}`
- **A — sign-in wireframe:** `{"source_type":"attachment","source_id":"457acc5e-8bce-44d6-abec-d204c28e4d84","locator":"sign-in-wireframe.png"}`
- **K — account recovery standard, ACC-STD-01–03:** `{"source_type":"knowledge","source_id":"28e06fb4-ccd1-4117-8f7b-b2a6c9bfaf1f","locator":"v1, chunk 0"}`

The image-reading tool returned a reference only; the wireframe observations below are the supplied image description recorded in the earlier evidence matrix. No earlier-stage output is cited as a source.

## Requirements

### REQ-001 — Render the supplied sign-in surface.

- **Acceptance criterion:** Given a visitor opens sign-in, when the page renders, then it shows a bordered panel headed “Sign in”, labeled “Email address” and “Password” inputs with “name@example.com” and masked “********” placeholders, a blue underlined “Forgot password?” link below the password input, a dark rectangular “Sign in” button below the link, and a muted “No account? Contact your administrator.” footer.
- **Sources:** S, A, K (ACC-STD-01).

### REQ-002 — Start a password-reset request from the sign-in recovery link.

- **Acceptance criterion:** Given the sign-in page is displayed, when the visitor follows “Forgot password?”, then they reach the password-reset request flow.
- **Sources:** S, A, K (ACC-STD-01).

### REQ-003 — Return an account-existence-independent response to password-reset requests.

- **Acceptance criterion:** Given otherwise equivalent reset requests for an existing and a nonexistent account, when they are submitted, then their user-visible responses are identical.
- **Acceptance criterion:** Given reset requests while an existing account is at its request limit, when those and otherwise equivalent requests for a nonexistent account are submitted, then the user-visible responses remain identical and do not disclose account existence or throttling state.
- **Sources:** S, K (ACC-STD-01).

### REQ-004 — Limit reset requests to five per account per hour.

- **Acceptance criterion:** Given five reset requests for an account in the preceding hour, when a sixth is submitted within that hour, then no additional reset link is issued for that account and the user-visible response remains the same generic response.
- **Acceptance criterion:** Given fewer than five reset requests for an account in the preceding hour, when another request is submitted, then it can be accepted within the limit.
- **Sources:** S, K (ACC-STD-01).

### REQ-005 — Issue a reset link for an accepted request for an existing account.

- **Acceptance criterion:** Given an existing synthetic account below its request limit, when its reset request is accepted, then a reset link for that account is recorded in the in-memory notification sink.
- **Sources:** S, K (ACC-STD-02).

### REQ-006 — Allow each reset link to complete a reset only once.

- **Acceptance criterion:** Given a valid reset link has already completed a password reset, when it is submitted again, then it cannot complete another reset.
- **Sources:** S, K (ACC-STD-02).

### REQ-007 — Expire reset links exactly 30 minutes after they are issued.

- **Acceptance criterion:** Given an otherwise valid unused link whose issue_time is when the link was issued (not when it was requested, sent, or first opened), when it is submitted before issue_time + 30 minutes, then it remains eligible for a password reset.
- **Acceptance criterion:** Given an otherwise valid unused link, when it is submitted at issue_time + 30 minutes or later, then it is ineligible for a password reset.
- **Sources:** S, K (ACC-STD-02).

### REQ-008 — Update an account password through an eligible reset link.

- **Acceptance criterion:** Given an eligible unused link for a synthetic account, when its reset is completed with a new password, then that account's password is updated.
- **Sources:** S, K (ACC-STD-02).

### REQ-009 — Sign an account out of every active session on successful reset.

- **Acceptance criterion:** Given an account has active sessions, when its password reset succeeds, then none of those sessions remains signed in.
- **Sources:** S, K (ACC-STD-02).

### REQ-010 — Notify the account owner after every successful password reset.

- **Acceptance criterion:** Given an account's password reset succeeds, when completion is processed, then an owner-directed notification for that reset is recorded in the in-memory sink.
- **Sources:** S, K (ACC-STD-03).

### REQ-011 — Use synthetic accounts in the application.

- **Acceptance criterion:** Given the application is exercised, when an account is needed for recovery, then it uses a synthetic account without requiring a production account integration.
- **Sources:** S.

### REQ-012 — Record recovery notifications in an in-memory sink.

- **Acceptance criterion:** Given a recovery notification is generated, when it is delivered, then it is available in an in-memory sink without requiring an external notification service.
- **Sources:** S, K (ACC-STD-03).

### REQ-013 — Run the application on Python 3.12 with Flask.

- **Acceptance criterion:** Given Python 3.12 and the project dependencies, when the application runs, then its web behavior is served by Flask.
- **Sources:** S.

### REQ-014 — Serve application pages as server-rendered HTML.

- **Acceptance criterion:** Given a browser requests an application page, when Flask responds, then the page content is rendered on the server.
- **Sources:** S.

### REQ-015 — Provide automated pytest coverage of the sign-in surface and recovery behavior.

- **Acceptance criterion:** Given the project test environment, when pytest runs, then automated tests check the sign-in surface and recovery behavior including requests, response equality, per-account limiting, links, reset completion, session sign-out where active sessions exist, and owner notification.
- **Sources:** S, A, K (ACC-STD-01–03).

### REQ-016 — Document production limitations.

- **Acceptance criterion:** Given a reader opens the project documentation, when they look for production limitations, then it explains limitations of this small implementation, including synthetic accounts and in-memory notifications.
- **Sources:** S.

### REQ-017 — Do not deploy the application.

- **Acceptance criterion:** Given the delivered work, when its actions are reviewed, then no application deployment has been performed.
- **Sources:** S.

### REQ-018 — Do not add deployment workflows.

- **Acceptance criterion:** Given the delivered repository, when its changes are reviewed, then they contain no added deployment workflow.
- **Sources:** S.

## Assumptions

- acceptance-20261028191242-8eaf7f-skill-sentinel — the acceptance skill produced this output.
- acceptance-20261028191242-8eaf7f-same-agent-revision
- The wireframe applies to the sign-in page's observed hierarchy, wording, and visual treatments, not exact pixel dimensions or color codes. The attachment read returned only a reference; the visual observations are supplied in the task and the prior evidence matrix.
- The story has no end marker and the attachment has no acceptance marker to reproduce.
- Synthetic accounts and the in-memory notification sink are development/test mechanisms, not production integrations. For accepted requests for existing accounts, a reset link is recorded in that sink to make the specified recovery flow exercisable; the public response does not reveal whether a link was recorded.
- Until sign-in success behavior and a session model are specified, require the visible sign-in surface and test all-session invalidation where active sessions exist, without prescribing a successful sign-in destination or authentication rules.
- Until reset-page wording and layout are specified, apply the supplied wireframe only to sign-in and use functional recovery criteria for the remaining pages.

## Non-blocking open questions

- **What sign-in success behavior and session model are expected?** Interim assumption: specify the visible sign-in surface and require invalidation of every active session when a reset succeeds, without inventing sign-in success behavior.
- **What exact reset-page wording and layout are expected?** Interim assumption: the wireframe governs sign-in only; recovery pages are evaluated by their functional behavior, not an invented layout.
