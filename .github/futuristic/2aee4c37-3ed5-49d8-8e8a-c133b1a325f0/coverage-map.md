# T001 — prospective test-case coverage map

This is a planning artifact for T002, **not** a test contract or a report of implemented/executed tests. It maps every individual criterion of approved REQ-001–REQ-018 to a stable proposed TC ID and approved implementation TASK ID. The approved solution design has no `coverage_dispositions`, so none is excluded. Test setup may use the proposed injectable clock, synthetic store, private sink and session fixtures; their presence in this map does not claim an implementation exists.

## Original evidence and citation boundaries

The following aliases mean **only** these original source references (use the exact objects/locators in the eventual contract):

| Alias | `source_type` | `source_id` | `locator` | Appropriate use |
| --- | --- | --- | --- | --- |
| S | `user_story` | `user_story` | `characters 0-16000` | Python 3.12/Flask, server-rendered exercise, synthetic accounts, in-memory notifications, pytest, limitations, no deployment. |
| I | `attachment` | `457acc5e-8bce-44d6-abec-d204c28e4d84` | `sign-in-wireframe.png` | Observed sign-in composition only, as directly observed in the supplied image; the attachment tool itself returns a reference, not pixels. |
| K | `knowledge` | `28e06fb4-ccd1-4117-8f7b-b2a6c9bfaf1f` | `v1, chunk 0` | Generic account-independent request response, five requests per account per hour, single-use 30-minute links, all-session sign-out and owner notice. |

Approved `requirements_analysis`, `ui_analysis`, `solution_design` and `acceptance_20261028191242_8eaf7f_risk` supply REQ/TASK identifiers and prospective risk context, **not** stage-output citation locators. Do not fabricate such locators. The sign-in image does not specify recovery-screen styling, working authentication, exact pixels/hex colors, or a sign-in success destination. Proposed UI accessibility checks below are supplementary verification proposals, not image observations or additional approved acceptance criteria.

## Criterion-to-case ledger

Criterion numbers below are local positions in each approved requirement's `acceptance_criteria` array. The descriptions paraphrase each full criterion without replacing it.

| Criterion | Approved criterion, individually | Prospective cases | Approved implementation task(s) |
| --- | --- | --- | --- |
| REQ-001.1 | Sign-in renders the specified bordered panel, heading, field labels/placeholders, ordered link/button and footer treatment. | TC-001, TC-002 | TASK-001 |
| REQ-002.1 | Following the sign-in recovery link reaches the reset-request flow. | TC-003, TC-028 | TASK-001 |
| REQ-003.1 | Equivalent existing/unknown-account request responses are identical. | TC-004, TC-030 | TASK-003 |
| REQ-003.2 | At-limit existing/unknown responses remain identical, with no account/throttle disclosure. | TC-005, TC-030 | TASK-003 |
| REQ-004.1 | Sixth request inside the preceding hour issues no additional link and gives the same generic public response. | TC-006 | TASK-003 |
| REQ-004.2 | Requests while fewer than five precede them in the hour can be accepted. | TC-007, TC-008 | TASK-003 |
| REQ-005.1 | An accepted below-limit request for an existing synthetic account records its reset link in the in-memory sink. | TC-009 | TASK-003 |
| REQ-006.1 | Reusing a link that completed a reset cannot complete another. | TC-010, TC-011, TC-015, TC-029 | TASK-004 |
| REQ-007.1 | Unused link is eligible strictly before 30 minutes from actual link issue time, not request/send/open time. | TC-012 | TASK-004 |
| REQ-007.2 | Unused link is ineligible exactly at issue time + 30 minutes and thereafter. | TC-013 | TASK-004 |
| REQ-008.1 | Eligible link completion updates its synthetic account's password. | TC-014, TC-015, TC-016, TC-029 | TASK-004 |
| REQ-009.1 | On successful reset, every previously active session of that account is signed out. | TC-017 | TASK-002, TASK-004 |
| REQ-010.1 | Every successful reset records an owner-directed notification in the in-memory sink. | TC-018 | TASK-004 |
| REQ-011.1 | Exercise recovery uses synthetic accounts without a production account integration. | TC-019 | TASK-002 |
| REQ-012.1 | Generated recovery notices are accessible in an in-memory sink without an external provider. | TC-020, TC-030 | TASK-002 |
| REQ-013.1 | Under Python 3.12 with dependencies, Flask serves the application's web behavior. | TC-021 | TASK-001 |
| REQ-014.1 | Flask returns already server-rendered page content. | TC-022 | TASK-001, TASK-003, TASK-004 |
| REQ-015.1 | Running pytest automatically checks sign-in and recovery, including responses, rate limit, links, completion, sessions and notices. | TC-023, TC-024 | TASK-005 |
| REQ-016.1 | Project documentation explains production limitations, including synthetic accounts and in-memory notifications. | TC-025 | TASK-006 |
| REQ-017.1 | Review of delivered actions finds no application deployment. | TC-026 | TASK-006 |
| REQ-018.1 | Review of delivered repository changes finds no added deployment workflow. | TC-027 | TASK-006 |

**Coverage count:** 21/21 individual acceptance criteria across 18/18 requirements have proposed cases; TASK-001 through TASK-006 are linked. The case IDs below are unique and reserved for T002; do not renumber them casually.

## Prospective cases: preconditions/data, action and observable result

Each entry provides seed data and a compact action/expected-result pair for expansion into numbered steps and explicit expected results in T002. `S`, `I`, `K` designate the original references above; do not cite prior-output tools as evidence.

### Sign-in and recovery entry

- **TC-001** (`REQ-001`; `TASK-001`; S,I,K; positive/visual): With a running Flask test client, GET sign-in and inspect HTML plus rendered visual hierarchy. Observe white page/centered bordered panel, bold **Sign in**, stacked programmatically labeled **Email address** and **Password**, `name@example.com` and masked `********` placeholders, blue underlined **Forgot password?** below password and above a wide dark **Sign in** button, and muted **No account? Contact your administrator.** footer. Do not assert pixel dimensions, exact colors, or sign-in success.
- **TC-002** (`REQ-001`; `TASK-001`; S,I; accessibility/supportive): On sign-in using keyboard and screen reader, traverse email → password → recovery link → submit; verify persistent associated labels (not placeholder-only names), discernible link/button names, visible focus, readable text including muted footer, and logical order. These checks derive from approved UI proposals, not extra facts observed in the image.
- **TC-003** (`REQ-002`; `TASK-001`; S,I,K; positive): From the server-rendered sign-in response activate **Forgot password?**, following the real anchor with the client. Expect a reachable reset-request page containing an email request control; a decorative or dead link fails. Do not require a specific recovery-page design.
- **TC-028** (`REQ-002`, `REQ-003`; `TASK-001`, `TASK-003`; S,K; accessibility/supportive): On the reset-request and generic response states, keyboard/tab and screen-reader inspect a persistent email label, named submit/navigation, focus order/visible focus and announced status; submit empty and malformed email separately. Expect actionable field-associated validation without account-status disclosure; for a valid request the generic status is perceivable and a return action accessible. Treat precise validation copy and any loading/transport presentation as provisional UI decisions, not invented criteria.

### Request privacy, issuance and limit

- **TC-004** (`REQ-003`; `TASK-003`; S,K; privacy/negative): With one synthetic owner and one unknown but well-formed address, reset isolated sink/state and POST otherwise identical below-limit requests. Compare public status, server-rendered body and navigation class after neutralizing only unavoidable request-specific transport data; they must match without revealing which address exists. Inspect private sink separately, never through the public response.
- **TC-005** (`REQ-003`; `TASK-003`; S,K; privacy/boundary): Preload five accepted requests for owner in the preceding hour; POST another owner request and an equivalent unknown-address request. Public status/content/navigation are identical and do not say "throttled", identify the owner, or disclose issuance; owner sink count stays at five.
- **TC-006** (`REQ-004`; `TASK-003`; S,K; negative/limit): Freeze UTC time; make five owner requests within one rolling hour and count five link entries. Submit the sixth before the oldest ages out; expect zero new owner links and the same generic response as an accepted valid request. Examine private sink independently.
- **TC-007** (`REQ-004`; `TASK-003`; S,K; positive/limit): Fresh owner at a controlled UTC time; submit requests one through five within the hour. Each can be accepted and records one owner link; another synthetic account's independent allowance is unaffected.
- **TC-008** (`REQ-004`; `TASK-003`; S,K; boundary): With oldest of five accepted owner requests at `t0`, verify a sixth just before `t0 + 1 hour` records no link; advance to `t0 + 1 hour` where the oldest is outside the preceding rolling hour and retry. Expect one new link and the same generic public response in both cases; timestamps for the remaining four still count.
- **TC-009** (`REQ-005`; `TASK-003`; S,K; positive): An existing synthetic account below cap submits a well-formed request. Inspect the private in-memory sink: exactly one new reset-link entry is addressed to that owner and contains a usable link for that account; public content does not expose the link or confirm existence.
- **TC-030** (`REQ-003`, `REQ-005`, `REQ-012`; `TASK-002`, `TASK-003`; S,K; security/supportive): Fetch public sign-in/request/confirmation responses for existing, unknown and capped accounts. Expect no account inventory, notification-sink contents, raw tokens or private limit decisions exposed; confirm any issued link is inspectable only via the internal sink test fixture. This is a public/private-boundary check, not a demand for a new API.

### Link lifecycle, password and post-reset effects

- **TC-010** (`REQ-006`; `TASK-004`; S,K; negative/replay): Issue an owner link, submit one valid new nonempty password before expiry, then submit that same link again with a different password. First completion succeeds; second has no success state, no further password change, session-generation change or reset-success notification.
- **TC-011** (`REQ-006`; `TASK-004`; S,K; concurrency/boundary): Coordinate two near-simultaneous POST submissions of the same unused, eligible link. Exactly one succeeds and changes the password/records one success notice; the other is ineligible without additional success effects. GET viewing an eligible link beforehand does not consume it.
- **TC-012** (`REQ-007`; `TASK-004`; S,K; time/positive): Use an injected clock and a recorded actual `issued_at`; make request time, sink/read time and form-open time distinguishable from issue time. Open valid form, then submit an unused link at `issued_at + 30 minutes - ε` (e.g. one microsecond). Expect it still eligible and, with a valid new password, reset completion; eligibility is computed from issuance, not those other timestamps.
- **TC-013** (`REQ-007`; `TASK-004`; S,K; time/negative): In separate fresh-token fixtures, open the form before expiry but submit exactly at `issued_at + 30 minutes`, then test another at `issued_at + 30 minutes + ε`. Both are ineligible on POST despite earlier GET, with unchanged password, no new success notice and no false success display.
- **TC-014** (`REQ-008`; `TASK-004`; S,K; positive/isolation): Seed accounts A and B with distinct password hashes; complete A's eligible reset using a nonempty new value. Verify A's stored hash changes, verifies the new value but not old value, is not stored as plaintext, and B's hash stays unchanged. Do not invent password complexity or a working sign-in contract.
- **TC-015** (`REQ-006`, `REQ-008`; `TASK-004`; S,K; security/negative): POST a malformed/unknown token, then attempt to apply A's valid link to B (e.g. tampered link or account-identifying field), and retry a consumed A link. None can alter B or complete an additional reset; invalid paths have no success notice and never echo token material. A valid token is bound to its original account irrespective of client-controlled fields.
- **TC-016** (`REQ-008`; `TASK-004`; S,K; validation/supportive): With a valid link, submit an empty new-password field, then a nonempty field on the same still-unused link. Empty input must not report success, change a password or consume the token; nonempty input can complete if still eligible. Field-associated actionable error is proposed UI behavior; no unapproved length/complexity policy is assumed.
- **TC-017** (`REQ-009`; `TASK-002`, `TASK-004`; S,K; authorization/security): Register two independent active sessions for A and one for B using synthetic fixtures; verify all initially pass the proposed server-side session check. Complete A's eligible reset. Both old A sessions now fail their next authorization check, while B's remains valid. Fixture registration does **not** assert implemented sign-in success or a destination.
- **TC-018** (`REQ-010`; `TASK-004`; S,K; positive/negative): Perform two distinct successful resets of the same owner with two independently issued eligible links; inspect the sink after each. Exactly one owner-addressed `reset-success` notice is added per completion, distinguishable from link issuance, and notice creation precedes visible success. Expired/replayed/malformed submissions add no success notice.
- **TC-029** (`REQ-006`, `REQ-008`; `TASK-004`; S,K; accessibility/supportive): Navigate the new-password form and post-reset success/non-success states using keyboard and assistive technology. Expect a programmatically named password field, focusable named action, sensible focus/announced success or non-success, visible focus/readable contrast and no token in visible errors; a used/expired link must not display success. Exact copy/layout and any optional confirmation field remain unspecified.

### Architecture, tests, documentation and delivery scope

- **TC-019** (`REQ-011`; `TASK-002`; S; architecture): Instantiate exercise state with synthetic A and B, request A recovery and inspect its private state. Expect the flow to work without production account credentials, API or identity integration; public responses expose no account inventory.
- **TC-020** (`REQ-012`; `TASK-002`; S,K; architecture): Generate a link notice and a successful-reset owner notice via synthetic flow, then inspect the injected private in-memory sink. Entries are available in process by recipient/kind without a network mail/SMS provider; public routes do not serve the sink.
- **TC-021** (`REQ-013`; `TASK-001`; S; runtime): In the declared Python **3.12** environment with dependencies, load the app factory and request sign-in with Flask's test client. Expect successful Flask-served web response; inspect runtime/dependency metadata rather than presuming a different interpreter suffices.
- **TC-022** (`REQ-014`; `TASK-001`, `TASK-003`, `TASK-004`; S; rendering): With JS disabled or a raw HTTP client, request sign-in, reset-request, generic confirmation and eligible/ineligible reset pages as applicable. Flask responds with populated HTML content/labels/status rather than an empty client-only shell requiring browser JavaScript to construct the page.
- **TC-023** (`REQ-015`; `TASK-005`; S,I,K; test-inventory/positive): In the future project test environment, collect and run pytest; inspect automated assertions for sign-in hierarchy/link navigation, existing/unknown/at-limit public response equivalence, first five/sixth/rolling-hour link counts and absence of public sink disclosure. Passing tests are a future validation target, **not** an outcome of T001.
- **TC-024** (`REQ-015`; `TASK-005`; S,K; test-inventory/boundary): Collect and run pytest; inspect automated assertions for issue-time-relative just-before/exactly-at/after 30 minutes, replay and competing POSTs, correct account password, multiple old sessions rejected where sessions exist, and one owner notice per success but none on rejected submissions. Do not mark tests as present or passing based on this plan.
- **TC-025** (`REQ-016`; `TASK-006`; S; documentation): Read future project documentation. Expect explicit synthetic-account and in-memory-notification limitations, volatile single-process account/token/request/session state lost on restart, lack of cross-worker durability and real production account/mail integration; no claim that this exercise is production-ready.
- **TC-026** (`REQ-017`; `TASK-006`; S; negative delivery-action review): At delivery, inspect the work/action record for the approved run, including executed commands and published endpoints where available. Expect no app deployment or deployment target reached. Repository absence alone cannot prove this negative; if action history is unavailable, record a verification gap rather than a pass.
- **TC-027** (`REQ-018`; `TASK-006`; S; negative repository-change review): At delivery, inspect the complete repository diff/new files against the starting revision, especially automation/configuration paths. Expect no newly added deployment workflow, deployment job or deployment-config change that performs deployment; review actual changed content rather than filenames alone.

## Gaps and handoff cautions

- **Unmapped approved requirements/criteria: none.** Additional cases TC-002, TC-015, TC-016, TC-028, TC-029 and TC-030 deepen accessibility, invalid-input and public/private-boundary checks; their supportive UI specifics are provisional rather than newly approved requirements.
- **Verification not yet possible:** no app, pytest result, delivery-action history or final repository diff was established by these evidence tools. TC-026 requires action evidence, TC-027 requires the final diff, and TC-023/024 require actual pytest files/execution. Do not report any case as implemented, run or passing.
- **Open, nonblocking predecessors:** sign-in success/session creation, exact recovery copy/layout, additional password policy/confirmation and invalid-link presentation are unspecified. Use synthetic session fixtures, functional eligibility and nonempty-password checks without inventing a login destination, CSS measurements, password-complexity threshold or external service.
- **T002 handoff:** the final pinned schema 1.0 contract needs top-level `schema_version`, `source_references`, `assumptions`, `open_questions`, `stage`, `test_cases`; every test case needs `id`, `title`, `requirement_ids`, `task_ids`, `steps`, `expected_results`, `source_references`. Expand the actions above into numbered steps and unambiguous observable expected results, incorporating preconditions/test data in those available fields, and cite only the exact original S/I/K references relevant to each case.
