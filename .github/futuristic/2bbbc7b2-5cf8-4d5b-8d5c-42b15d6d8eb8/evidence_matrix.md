# Requirements evidence matrix (T001)

This is a traceability and acceptance-criteria draft, **not** the final JSON contract. Candidate IDs are reserved for the subsequent requirements output. The pinned story was read to `next_offset: null`; it has no end marker. The image-reading tool returned only an attachment reference, so the image observations below rely on the user's supplied description, not on inferred pixels. No attachment acceptance marker was observed.

## Exact source references

| Key | Source reference | Evidence |
| --- | --- | --- |
| S | `{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}` | Password-reset app; Python 3.12, Flask, server-rendered pages, pytest; supplied sign-in wireframe; curated recovery standard; synthetic accounts; in-memory notification sink; production-limitations documentation; automated tests; no deployment or deployment workflows. |
| A | `{"source_type":"attachment","source_id":"457acc5e-8bce-44d6-abec-d204c28e4d84","locator":"sign-in-wireframe.png"}` | User-observed bordered sign-in panel, heading “Sign in”, labeled “Email address” and “Password” inputs with `name@example.com` and masked `********` placeholders, underlined blue “Forgot password?” link beneath password, dark rectangular “Sign in” button beneath link, muted “No account? Contact your administrator.” footer. No exact dimensions or color codes established. |
| K | `{"source_type":"knowledge","source_id":"28e06fb4-ccd1-4117-8f7b-b2a6c9bfaf1f","locator":"v1, chunk 0"}` | ACC-STD-01: sign-in recovery link starts request, same response regardless of account existence, at most five requests per account per hour. ACC-STD-02: reset links single-use, expire 30 minutes after issue, reset completion signs out every active session. ACC-STD-03: owner notified after each successful reset. |

The “Sources” column keys expand to the **exact** references above; K's clause identifies the pertinent portion of the same knowledge result. There are no approved earlier-stage outputs.

## Candidate requirements

| ID | One observable behavior / constraint | Given / When / Then acceptance criterion | Sources |
| --- | --- | --- | --- |
| REQ-001 | Render the supplied sign-in surface. | **Given** a visitor opens sign-in, **when** the page renders, **then** it shows a bordered panel headed “Sign in”, labeled email and password inputs with `name@example.com` and masked `********` placeholders, a blue underlined “Forgot password?” link below the password input, a dark rectangular “Sign in” button below the link, and the muted “No account? Contact your administrator.” footer. | S; A; K (ACC-STD-01, recovery link only) |
| REQ-002 | Start a password-reset request from the sign-in recovery link. | **Given** the sign-in page is displayed, **when** the visitor follows “Forgot password?”, **then** they reach the password-reset request flow. | S; A; K (ACC-STD-01) |
| REQ-003 | Return the same reset-request response for existing and nonexistent accounts. | **Given** otherwise equivalent submitted reset requests for an existing and a nonexistent account, **when** each is processed, **then** the user-visible responses are identical. | S; K (ACC-STD-01) |
| REQ-004 | Limit reset requests to five per account per hour. | **Given** an account has made five reset requests within an hour, **when** a sixth is made within that hour, **then** it is not accepted as another reset request; a request outside that window can be accepted. | S; K (ACC-STD-01) |
| REQ-005 | Issue a reset link for an accepted request for an existing account. | **Given** an existing synthetic account and an accepted reset request, **when** the request is processed, **then** a reset link for that account is made available through the in-memory notification sink. | S; K (ACC-STD-02, links and issue time; issuance is necessary for the stated flow) |
| REQ-006 | Accept a reset link no more than once. | **Given** a valid reset link has been used to complete a reset, **when** it is submitted again, **then** it cannot complete another reset. | S; K (ACC-STD-02) |
| REQ-007 | Expire reset links 30 minutes after issue. | **Given** a reset link's recorded issue time, **when** it is submitted before the 30-minute expiry it remains eligible, and **when** it is submitted at or after expiry it cannot complete a reset. | S; K (ACC-STD-02) |
| REQ-008 | Update the account password through an eligible reset link. | **Given** an eligible unused link for a synthetic account, **when** its reset is completed with a new password, **then** that account's password is updated. | S; K (ACC-STD-02, successful completion) |
| REQ-009 | Sign the account out of every active session on reset completion. | **Given** an account has active sessions, **when** its password reset succeeds, **then** none of those sessions remains signed in. | S; K (ACC-STD-02) |
| REQ-010 | Notify the account owner after each successful reset. | **Given** an account's password reset succeeds, **when** completion is processed, **then** an owner-directed notification is recorded for that reset in the in-memory sink. | S; K (ACC-STD-03) |
| REQ-011 | Use synthetic accounts for the application. | **Given** the application is exercised, **when** an account is needed for sign-in or recovery, **then** it uses a synthetic account rather than requiring a production account integration. | S |
| REQ-012 | Keep notifications in an in-memory sink. | **Given** a recovery notification is generated, **when** it is delivered, **then** it is available in an in-memory sink without an external notification service. | S; K (ACC-STD-03, owner notification) |
| REQ-013 | Run the application on Python 3.12 with Flask. | **Given** Python 3.12 and the project dependencies, **when** the application runs, **then** its web behavior is served by Flask. | S |
| REQ-014 | Serve pages as server-rendered HTML. | **Given** a browser requests an application page, **when** Flask responds, **then** the page content is rendered on the server. | S |
| REQ-015 | Provide automated pytest coverage. | **Given** the project test environment, **when** pytest runs, **then** automated tests check the sign-in surface and recovery behavior including requests, links, reset completion, session sign-out, and owner notification. | S; A (sign-in surface); K (ACC-STD-01 through ACC-STD-03, recovery checks) |
| REQ-016 | Document production limitations. | **Given** a reader opens the project documentation, **when** they look for production limitations, **then** it explains the limitations of this small implementation, including synthetic accounts and in-memory notifications. | S |
| REQ-017 | Do not deploy the application. | **Given** the delivered work, **when** its actions are reviewed, **then** no application deployment has been performed. | S |
| REQ-018 | Do not add deployment workflows. | **Given** the delivered repository, **when** its changes are reviewed, **then** they contain no added deployment workflow. | S |

## Assumptions and non-blocking questions for the later contract

- **Assumption:** `acceptance-20261028191242-8eaf7f-skill-sentinel` — the acceptance skill produced this output.
- **Assumption:** Wireframe fidelity means reproducing its observed hierarchy and content; exact dimensions and color codes are unspecified. No image acceptance marker or pinned-story end marker exists to copy.
- **Assumption:** Synthetic accounts and an in-memory notification sink are development/test mechanisms, not production integrations. The application issues links for accepted requests for existing accounts as the minimum needed to exercise the recovery standard; the user-visible response remains identical for nonexistent accounts.
- **Non-blocking question:** What sign-in success behavior and session model are expected? **Interim assumption:** Specify the visible sign-in surface and the required sign-out of every active session where sessions exist, without inventing a success destination or authentication rules.
- **Non-blocking question:** What exact reset-page appearance and wording are expected? **Interim assumption:** Apply the wireframe only to sign-in; use functional recovery criteria for reset pages without prescribing their layout or text.

No unsupported password-policy, message-delivery, token-strength, deployment-readiness, timing, or visual-precision target is inferred from these sources.
