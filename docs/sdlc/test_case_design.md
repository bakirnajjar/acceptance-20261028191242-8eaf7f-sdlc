# Test case design — password-reset exercise

**Stage:** `test_case_design` · **Contract:** `docs/sdlc/test_case_design.json` · **Status:** proposed verification design, not implemented or executed test results.

## Evidence and interpretation

- **S — story:** `user_story` / `user_story` / `characters 0-16000`. Python 3.12, Flask server-rendered pages, synthetic accounts, in-memory notification sink, pytest, production-limitations documentation, and no deployment or deployment workflows.
- **I — image:** `attachment` / `457acc5e-8bce-44d6-abec-d204c28e4d84` / `sign-in-wireframe.png`. The supplied image shows a white page, centered bordered sign-in panel, bold heading, stacked labeled email/password inputs, their placeholders, recovery link, dark button, and muted footer. The attachment reader supplied a reference only; visual observations were supplied directly with the task. It does not establish exact CSS, working authentication, or recovery-screen design.
- **K — recovery standard:** `knowledge` / `28e06fb4-ccd1-4117-8f7b-b2a6c9bfaf1f` / `v1, chunk 0`. Identical reset-request response regardless of account existence; at most five requests per account per hour; single-use links expiring 30 minutes after issue; every successful reset signs out all active sessions and notifies the owner.

Approved `requirements_analysis`, `ui_analysis`, `solution_design`, and `acceptance_20261028191242_8eaf7f_risk` determine the REQ/TASK identifiers and prospective verification context. Their reader supplied no citation locator, so this document uses only the original S/I/K references above. Accessibility and recovery-state presentation are **proposed checks**, not additional image observations or an invented password policy.

## Coverage

**21/21 approved acceptance criteria** across **18/18 requirements** have at least one proposed case; uncovered criteria: **none**. All **TASK-001–TASK-006** are linked. Criterion positions refer to the order of the approved requirements' `acceptance_criteria` arrays.

| Criterion | Case(s) | Task(s) |
| --- | --- | --- |
| REQ-001.1 | TC-001, TC-002 | TASK-001 |
| REQ-002.1 | TC-003, TC-028 | TASK-001 |
| REQ-003.1 | TC-004, TC-030 | TASK-003 |
| REQ-003.2 | TC-005, TC-030 | TASK-003 |
| REQ-004.1 | TC-006 | TASK-003 |
| REQ-004.2 | TC-007, TC-008 | TASK-003 |
| REQ-005.1 | TC-009 | TASK-003 |
| REQ-006.1 | TC-010, TC-011, TC-015, TC-029 | TASK-004 |
| REQ-007.1 | TC-012 | TASK-004 |
| REQ-007.2 | TC-013 | TASK-004 |
| REQ-008.1 | TC-014, TC-015, TC-016, TC-029 | TASK-004 |
| REQ-009.1 | TC-017 | TASK-002, TASK-004 |
| REQ-010.1 | TC-018 | TASK-004 |
| REQ-011.1 | TC-019 | TASK-002 |
| REQ-012.1 | TC-020, TC-030 | TASK-002 |
| REQ-013.1 | TC-021 | TASK-001 |
| REQ-014.1 | TC-022 | TASK-001, TASK-003, TASK-004 |
| REQ-015.1 | TC-023, TC-024 | TASK-005 |
| REQ-016.1 | TC-025 | TASK-006 |
| REQ-017.1 | TC-026 | TASK-006 |
| REQ-018.1 | TC-027 | TASK-006 |

### Sign-in and recovery entry

#### TC-001 — Sign-in surface matches observed wireframe hierarchy
**Trace:** REQ-001 · TASK-001 · S, I, K · positive visual.

1. With a Flask test client running, GET sign-in and render the returned HTML in a browser.
2. Inspect the panel, heading, fields, placeholders, link, button, footer, and order against the supplied image.

**Expected:** A white page has a centered bordered panel, bold **Sign in** heading, stacked **Email address** and **Password** labeled fields, `name@example.com` and masked `********` placeholders. The blue underlined **Forgot password?** link lies below Password and above a wide dark **Sign in** button; muted footer reads **No account? Contact your administrator.** No exact pixels or color codes are asserted.

#### TC-002 — Sign-in controls remain usable without placeholders
**Trace:** REQ-001 · TASK-001 · S, I · proposed accessibility check.

1. Open sign-in with keyboard and screen reader; traverse email → password → recovery link → submit.
2. Enter sample values to hide placeholders; inspect accessible names, focus indicators, and muted footer readability.

**Expected:** Fields retain programmatically associated labels; link and submit have discernible names and logical order. Focus is visible and text, including the footer, readable. These checks do not turn image pixels into accessibility specifications.

#### TC-003 — Recovery link enters a usable reset request
**Trace:** REQ-002 · TASK-001 · S, I, K · positive.

1. GET sign-in and locate the actual **Forgot password?** anchor.
2. Follow it with the client, with JavaScript disabled.

**Expected:** A reachable server-rendered password-reset request page has an email request control; the link is not dead or decorative. No exact recovery styling or successful sign-in destination is required.

### Request privacy, issuance, and rolling limit

#### TC-004 — Existing and unknown accounts receive equivalent responses
**Trace:** REQ-003 · TASK-003 · S, K · privacy.

1. Seed synthetic owner A and one distinct well-formed unknown address; isolate sink and counters.
2. POST otherwise equivalent valid below-limit requests for each; capture public status, rendered body, and redirect/navigation class.
3. Inspect issuance only through the private sink fixture.

**Expected:** Public status, body, and navigation match after neutralizing only unavoidable request-specific transport data, with no existence or issuance disclosure. Private issuance may differ (A can have a link, unknown cannot).

#### TC-005 — At-limit responses do not identify accounts or throttling
**Trace:** REQ-003 · TASK-003 · S, K · negative/boundary.

1. Freeze UTC time and record five accepted requests and five links for A within the preceding hour.
2. POST A's sixth valid request and an otherwise equivalent well-formed unknown request; compare public status, body, and navigation.
3. Inspect A's private link count.

**Expected:** Public results are identical and disclose neither owner, issuance, nor throttling; A retains exactly five links.

#### TC-006 — Sixth request inside rolling hour issues no link
**Trace:** REQ-004 · TASK-003 · S, K · negative limit.

1. At controlled UTC `t0`, submit five A requests in one rolling hour; inspect A's private links.
2. Before the oldest ages out, submit a sixth; compare public result with an accepted request and recount.

**Expected:** The first five each yield one private link; the sixth yields zero additional links and the same generic public response as an otherwise equivalent accepted request.

#### TC-007 — First five requests allowed independently per account
**Trace:** REQ-004 · TASK-003 · S, K · positive limit.

1. Seed A and B with empty counters and a controlled UTC clock.
2. Submit A's first through fifth valid requests within the hour, checking private count after each.
3. Submit B's first request within that hour; inspect B's count.

**Expected:** A's counts progress **1, 2, 3, 4, 5**. B independently obtains its first link; A's count does not consume B's allowance.

#### TC-008 — Rolling-hour allowance reopens at oldest timestamp
**Trace:** REQ-004 · TASK-003 · S, K · exact boundary.

1. Preload five accepted A requests: oldest at `t0`, four strictly later; count five links.
2. Try again at `t0 + 1 hour - 1 microsecond`; capture public result and count.
3. Retry at exactly `t0 + 1 hour`; capture result and count.

**Expected:** Just before the boundary all five still count and no new link is issued. At the boundary the oldest falls outside the preceding rolling hour, so one new link is issued (six total); both public results remain generic and identical.

#### TC-009 — Accepted owner request privately issues a usable link
**Trace:** REQ-005 · TASK-003 · S, K · positive.

1. Seed A below the cap and snapshot the private sink.
2. Submit a well-formed A request; inspect new sink entry and open its link before expiry.

**Expected:** Exactly one new reset-link entry addressed to A has a link eligible for A's new-password form. The public response exposes neither the link nor A's existence.

### Reset link lifecycle and post-reset effects

#### TC-010 — Used link cannot complete a second password reset
**Trace:** REQ-006 · TASK-004 · S, K · replay.

1. Issue A's link and POST one nonempty new password before expiry; snapshot A's hash, session generation, and success notices.
2. POST the same link with a different nonempty password.

**Expected:** First completion succeeds and consumes the link; replay does not display success or change A's hash/session generation or add a success notice.

#### TC-011 — Competing submissions of one link yield one winner
**Trace:** REQ-006 · TASK-004 · S, K · concurrent boundary.

1. Issue an eligible A link and GET its form twice; check that GET did not consume it.
2. Coordinate near-simultaneous POSTs with distinct nonempty passwords; inspect both results and internal effects.

**Expected:** Exactly one POST succeeds and changes A's password once with exactly one reset-success notice. The other is ineligible, cannot overwrite the winner, and adds no success effect.

#### TC-012 — Link remains eligible immediately before issue-time expiry
**Trace:** REQ-007 · TASK-004 · S, K · positive time boundary.

1. With an injected UTC clock distinguish request at `t0`, actual issue at `t0 + 2 minutes`, sink read at `t0 + 4 minutes`, and form open at `t0 + 5 minutes`; record `issued_at`.
2. Submit the unused link with a nonempty new password at `issued_at + 30 minutes - 1 microsecond`.

**Expected:** The POST is eligible and completes the reset. The deadline uses actual issuance, not request, sink-read/send, or GET/open time.

#### TC-013 — Exact thirty-minute boundary and later POSTs are ineligible
**Trace:** REQ-007 · TASK-004 · S, K · negative time boundary.

1. Issue two fresh A tokens with recorded `issued_at`; open both forms before expiry.
2. POST one at exactly `issued_at + 30 minutes`, and the other at `issued_at + 30 minutes + 1 microsecond`, using nonempty passwords.
3. Inspect password, success notices, and rendered states after each.

**Expected:** Both are ineligible despite the earlier GET. Neither changes A's password, adds a success notice, or displays reset success. The 30-minute deadline is exclusive.

#### TC-014 — Eligible reset updates only its associated account password
**Trace:** REQ-008 · TASK-004 · S, K · positive isolation.

1. Seed A and B with distinct password hashes, capture both, and issue an eligible A link.
2. Submit a nonempty new A password before expiry; inspect hashes and use the password verifier on old/new A values.

**Expected:** A's hash changes, differs from plaintext, verifies the new value and not the old; B's hash is unchanged. This does not assume sign-in success behavior or a complexity rule.

#### TC-015 — Malformed or misbound tokens cannot change another account
**Trace:** REQ-006, REQ-008 · TASK-004 · S, K · security/negative.

1. Seed A/B, issue A's link, and snapshot both hashes and success-notice count.
2. POST a malformed/unknown token; try A's link with a client-controlled B identifier or tampered account-bearing URL if such input exists.
3. Complete A's original link legitimately if still unused, then replay it; inspect accounts, notices, and displayed errors.

**Expected:** Malformed, tampered, and consumed tokens cannot alter B or complete another reset; invalid paths add no notice or token echo. An untampered eligible A token remains bound to A despite any client-controlled account value; B's hash never changes.

#### TC-016 — Empty password cannot consume eligible link
**Trace:** REQ-008 · TASK-004 · S, K · invalid input.

1. Issue fresh A link and POST an empty new-password field while eligible; inspect password, token status, and result.
2. Before expiry, POST a nonempty value using the same link; inspect A's password.

**Expected:** Empty input yields no success, password change, or token consumption; proposed UI feedback is field-associated and actionable. The still-eligible link can complete once with nonempty input; no unapproved complexity or maximum-length threshold is asserted.

#### TC-017 — Reset invalidates every old session of its account
**Trace:** REQ-009 · TASK-002, TASK-004 · S, K · authorization.

1. Register two independent active server-side sessions for A and one for B through synthetic fixtures; verify all pass an initial authorization check.
2. Complete A's eligible reset and repeat all three authorization checks.

**Expected:** Both old A sessions fail their next check; unrelated B remains valid. Fixtures do not imply implemented sign-in or a login destination.

#### TC-018 — Each successful reset records one owner notice
**Trace:** REQ-010 · TASK-004 · S, K · positive and rejection.

1. Issue A's first eligible link, snapshot the private sink, complete reset, and inspect sink before accepting visible success.
2. Issue a **distinct** second A link; complete a second reset and inspect sink again.
3. Separately submit expired, malformed, and consumed links; recount success notices.

**Expected:** Each success adds exactly one A-addressed `reset-success` entry, distinguishable from link issuance and present before success is reported (increments **+1, +1**). Rejected attempts add zero success notices.

### Architecture, automation, documentation, and delivery scope

#### TC-019 — Recovery operates on synthetic accounts alone
**Trace:** REQ-011 · TASK-002 · S · architecture.

1. Instantiate isolated state with synthetic A/B and no production identity credentials or account API.
2. Request A recovery; inspect private account/link state and public response.

**Expected:** Recovery can issue a link using synthetic state without a production identity integration; public response does not expose account inventory.

#### TC-020 — Link and success notifications stay in private in-memory sink
**Trace:** REQ-012 · TASK-002 · S, K · architecture/security.

1. Inject an empty in-process sink with no mail/SMS provider.
2. Request A's link and complete its reset; query private entries by recipient and kind.
3. Request public routes without fixture access.

**Expected:** An A-addressed reset-link and A-addressed reset-success entry are accessible in process without an external notification service; public routes do not serve sink or link/token contents.

#### TC-021 — Python 3.12 Flask runtime serves sign-in
**Trace:** REQ-013 · TASK-001 · S · runtime.

1. In the declared Python 3.12 environment with dependencies, inspect interpreter and framework metadata.
2. Load the Flask app factory and GET sign-in through Flask's test client.

**Expected:** Interpreter is Python 3.12, the web app is Flask, and sign-in returns a successful web response. Execution under another interpreter alone is not proof.

#### TC-022 — Pages are populated server-rendered HTML
**Trace:** REQ-014 · TASK-001, TASK-003, TASK-004 · S · rendering.

1. With JavaScript disabled or a raw HTTP client, GET sign-in and reset-request.
2. Submit a valid request and fetch generic confirmation; GET separate eligible/ineligible reset links.
3. Inspect HTML without running scripts.

**Expected:** Flask returns populated HTML containing sign-in labels, request control, generic status, and eligible form/ineligible status. No primary page depends on JavaScript constructing content from an empty shell.

#### TC-023 — Pytest exercises entry, privacy and rate limits
**Trace:** REQ-015 · TASK-005 · S, I, K · future test inventory.

1. In the future project test environment, collect pytest and inspect the assertion inventory.
2. Run pytest; inspect assertions for sign-in hierarchy/link navigation, existing/unknown/at-limit response equality, first-five/sixth/rolling-hour issuance, and public sink nondisclosure.

**Expected:** Collected automated assertions cover all named entry, privacy, limit, and public/private checks; pytest exits successfully **when implemented**. This design is not an execution result.

#### TC-024 — Pytest exercises expiry, replay and post-reset effects
**Trace:** REQ-015 · TASK-005 · S, K · future test inventory.

1. Collect the future suite and inspect assertions for just-before/exactly-at/after issue-time expiry, replay, competing POSTs, and correct account updates.
2. Run pytest; inspect checks for multiple old sessions rejected and one owner notice per success, with none for rejected attempts.

**Expected:** Collected assertions cover each named lifecycle, isolation, session, and notice case; pytest exits successfully **when implemented**. No current passing status is claimed.

#### TC-025 — Project documentation discloses production limitations
**Trace:** REQ-016 · TASK-006 · S · documentation.

1. Read future project documentation and locate production limitations.
2. Inspect descriptions of synthetic accounts, in-memory notices, persistence, and integration boundaries.

**Expected:** It explicitly describes synthetic accounts, volatile single-process account/token/request/session and notification state lost on restart, lack of cross-worker durability and real production identity/mail integration. It does not claim production readiness.

#### TC-026 — Delivery-action record establishes no deployment
**Trace:** REQ-017 · TASK-006 · S · negative action review.

1. At delivery obtain complete run action history, executed commands, and published endpoints/deployment records where available.
2. Review for performed app deployment or a reached target, separately from repository changes.
3. If records are missing or incomplete, document the evidence gap.

**Expected:** A complete record finds no performed app deployment. **Evidence gap:** without an adequate action record the result is *unverified*, not a pass; absence of a workflow or repository deployment file alone cannot prove no deployment action.

#### TC-027 — Delivered diff adds no deployment workflow
**Trace:** REQ-018 · TASK-006 · S · negative repository review.

1. At delivery inspect the complete repository diff and added paths against the starting revision, including automation/configuration.
2. Read changed contents for deployment jobs, workflow triggers, or deployment-performing configuration, not filenames alone.

**Expected:** No added deployment workflow/job or deployment-performing configuration appears in the final diff; this cannot be pre-judged from the design.

### Supplementary accessibility and security cases

#### TC-028 — Request and generic response are accessible without disclosure
**Trace:** REQ-002, REQ-003 · TASK-001, TASK-003 · S, K · proposed accessibility/invalid input.

1. Navigate the request form with keyboard/screen reader; inspect persistent email label, named submit/return controls, focus order/visibility, and readable text.
2. Submit empty and malformed email separately; inspect field errors and account-status disclosure.
3. Submit an otherwise valid request; inspect generic-status announcement and keyboard-accessible return action.

**Expected:** Controls have discernible names and logical focus; invalid fields get associated actionable errors without account-status disclosure. Valid requests have a perceivable generic status and accessible return. Exact copy, loading, and recovery-page layout remain provisional UI decisions.

#### TC-029 — Reset and success or rejection states are accessible
**Trace:** REQ-006, REQ-008 · TASK-004 · S, K · proposed accessibility/security.

1. Keyboard/screen-reader inspect an eligible password form's label, named action, focus, and contrast; submit valid input.
2. Inspect success/return navigation, then used and expired link non-success/navigation; inspect errors for token echo.

**Expected:** Password control/actions have discernible names, logical visible focus, and perceivable success/navigation. Used/expired links announce actionable non-success, never success or token material. Exact layout/copy and an optional confirmation field are unspecified.

#### TC-030 — Public routes cannot reveal private recovery state
**Trace:** REQ-003, REQ-005, REQ-012 · TASK-002, TASK-003 · S, K · security boundary.

1. Seed existing A, unknown address, and at-limit A; request sign-in, request, and confirmation routes for equivalent cases.
2. Compare public status/content and inspect for inventory, link URLs, raw tokens, sink data, or throttle decisions.
3. Use only the private fixture to determine eligible A link issuance.

**Expected:** Public response class is account-independent and exposes none of these private values. An issued link is visible internally to the sink fixture, not through a public sink/inventory endpoint; no new public API is required.

## Assumptions and unresolved questions

- No application, test execution, delivery-action log, or final diff is established by these evidence reads. TC-023/024 require actual pytest files and execution; TC-026 requires an action record; TC-027 requires the final diff. No case is reported as run or passed.
- The image governs only sign-in hierarchy and treatment, not precise CSS, a recovery layout, sign-in authentication, or a success destination. Accessible recovery states are verification proposals.
- The allowance is **per account over a preceding rolling hour**: an accepted timestamp at or before `now - 1 hour` is outside it. An unused link is eligible only on POST **strictly before** actual issue time + 30 minutes; viewing it does not extend expiry.
- An accepted existing-account request records a link privately; equivalent public requests reveal neither issuance nor account existence. A nonempty password exercises completion without presuming a complexity, maximum-length, or confirmation requirement. Session fixtures permit testing old-session rejection without inventing login.
- **Nonblocking:** What sign-in authentication, success destination, and session-creation behavior are expected? TC-017 uses synthetic independent sessions meanwhile.
- **Nonblocking:** What exact recovery copy/layout and invalid-link navigation are expected? Tests assert functional non-success and proposed accessibility, not unsupported visual details.
- **Nonblocking:** Is there an additional new-password policy or confirmation-field requirement? TC-016 assumes only nonempty input.
- **Nonblocking:** Will a complete delivery-action record be available? If not, TC-026 must record an explicit verification gap rather than a pass.
