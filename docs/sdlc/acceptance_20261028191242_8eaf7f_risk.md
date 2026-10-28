# Prospective password-reset delivery risks

**Stage:** `custom_document` / `acceptance_20261028191242_8eaf7f_risk`

Six prospective delivery risks for the approved password-reset application, linked to all 18 approved requirements. These are verification targets, not observed defects or test results.

## Scope and evidence

The approved `requirements_analysis` predecessor establishes `REQ-001` through `REQ-018` and their acceptance criteria; these IDs establish linkage but are not assigned an invented source-reference locator. Original evidence is the user story, sign-in attachment, and curated account recovery standard cited in source_references. Risks concern delivery of the requested Python 3.12/Flask server-rendered exercise with synthetic accounts, an in-memory notification sink, pytest, production-limitations documentation, and no deployment or deployment workflows. The image observations are a visual hierarchy rather than a pixel-perfect specification.

**Source references (exact source IDs and locators):**

- **S1 — user story:** `{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}`
- **S2 — sign-in attachment:** `{"source_type":"attachment","source_id":"457acc5e-8bce-44d6-abec-d204c28e4d84","locator":"sign-in-wireframe.png"}`
- **S3 — account recovery standard:** `{"source_type":"knowledge","source_id":"28e06fb4-ccd1-4117-8f7b-b2a6c9bfaf1f","locator":"v1, chunk 0"}`

## Risks and verification

### RD8CDC-001 — Sign-in surface or recovery entry diverges

- **Category:** Sign-in and recovery entry. **Priority:** unranked. **Related IDs:** none.
- **Approved requirements:** `REQ-001`, `REQ-002`, `REQ-014`. **Sources:** S1, S2, S3.
- **Risk and impact:** A sign-in page might contain fields but omit the observed bordered-panel hierarchy, exact labels and placeholder treatment, or the visible link might fail to start recovery. Client-only rendering would miss the server-rendered-page requirement. Users might be unable to reach recovery and the supplied sign-in evidence would not be honored.
- **Mitigation / verification:** Render the sign-in page through Flask as server-rendered HTML. Check the bordered panel, bold “Sign in” heading, “Email address” and “Password” labels, `name@example.com` and masked `********` placeholders, blue underlined “Forgot password?” link beneath the password field, dark rectangular “Sign in” button below the link, and muted “No account? Contact your administrator.” footer. Follow the link on the rendered page and confirm it reaches the reset-request flow. Review hierarchy and visual treatment without imposing exact dimensions or color codes. Do not infer successful sign-in behavior or a reset-page design from the image.

### RD8CDC-002 — Enumeration, throttling disclosure, or excess link issuance

- **Category:** Request privacy and rate limit. **Priority:** unranked. **Related IDs:** none.
- **Approved requirements:** `REQ-003`, `REQ-004`, `REQ-005`. **Sources:** S1, S3.
- **Risk and impact:** Distinct public responses for existing, missing, or throttled accounts could reveal account existence or limit state. Issuing a sixth link for an account within the preceding hour breaches the request cap; failing to issue a link for an accepted existing-account request blocks recovery.
- **Mitigation / verification:** Keep the user-visible reset-request response identical across otherwise equivalent existing-account, missing-account, and throttled-account cases while separately deciding whether an existing synthetic account is eligible for link issuance. With controlled time and an inspected in-memory sink, exercise requests one through five, a sixth within the preceding hour, and a request once the applicable hour window has passed. Verify no extra link on the sixth, eligible existing-account requests can yield a link, and public responses remain indistinguishable. Do not expose sink contents or throttle status through the public response.

### RD8CDC-003 — Reset link accepted outside its lifecycle or password unchanged

- **Category:** Reset link lifecycle. **Priority:** unranked. **Related IDs:** none.
- **Approved requirements:** `REQ-006`, `REQ-007`, `REQ-008`. **Sources:** S1, S3.
- **Risk and impact:** A reused link, an expiry computed from request, sending, or opening time rather than issue time, or an off-by-one comparison could permit an ineligible reset. Conversely, a valid link might not update the intended synthetic account password.
- **Mitigation / verification:** Track when each link is issued, treat an unused eligible link as usable only before `issue_time + 30 minutes`, and prevent a successful link from completing any later reset. With controlled time, test immediately before the boundary, exactly at `issue_time + 30 minutes` (ineligible), and after it; test second submission of a used link. Verify an eligible completion changes the intended account's password, while ineligible or reused submissions cannot complete another password change.

### RD8CDC-004 — Successful reset leaves sessions active or owner uninformed

- **Category:** Post-reset effects. **Priority:** unranked. **Related IDs:** none.
- **Approved requirements:** `REQ-009`, `REQ-010`, `REQ-012`. **Sources:** S1, S3.
- **Risk and impact:** A password change without invalidating every active session would leave old access in place. A missing owner-directed notification after any successful reset would conceal the change; notifications not recorded in the required in-memory sink would not be inspectable in this exercise.
- **Mitigation / verification:** Make successful reset completion include all-session sign-out where active sessions exist and an owner-directed success notification recorded in the in-memory sink after every success. Set up multiple active sessions for a synthetic account where the implementation supports them and verify none remains signed in after completion; verify a sink entry per successful reset. Keep the session-model question open rather than prescribing sign-in success behavior. Distinguish success notifications from reset-link issuance in the sink.

### RD8CDC-005 — Exercise architecture misrepresented as production-ready

- **Category:** Exercise architecture and limitations. **Priority:** unranked. **Related IDs:** none.
- **Approved requirements:** `REQ-011`, `REQ-012`, `REQ-013`, `REQ-014`, `REQ-016`. **Sources:** S1, S3.
- **Risk and impact:** Substituting a production account integration or external notification provider for the specified synthetic accounts and in-memory sink would change the exercise's scope; conversely, presenting volatile demo mechanisms as production-grade persistence or delivery would mislead readers. A different runtime or framework, or non-server-rendered pages, would also violate the approved delivery constraints.
- **Mitigation / verification:** Inspect the Python 3.12/Flask runtime and rendered page responses; exercise recovery with synthetic accounts and inspect generated notifications in the in-memory sink without requiring an external service. Confirm project documentation clearly describes synthetic-account and volatile-notification limitations and does not suggest production persistence, actual external notification delivery, or a deployment target.

### RD8CDC-006 — Policy gaps in tests or unauthorized deployment work

- **Category:** Test and delivery scope. **Priority:** unranked. **Related IDs:** none.
- **Approved requirements:** `REQ-015`, `REQ-017`, `REQ-018`. **Sources:** S1, S2, S3.
- **Risk and impact:** A narrow happy-path pytest suite could miss image and entry-flow deviations, account enumeration including at-limit responses, the sixth-request cutoff, link reuse or expiry boundary, password update, all-session sign-out where active sessions exist, or notification after each success. Deploying the app or adding a deployment workflow would exceed the expressly approved scope.
- **Mitigation / verification:** Review pytest coverage for the sign-in surface, link navigation, equivalent public responses, per-account-hour limit and sink effects, link issue-time boundary and single use, password update, session invalidation where applicable, and owner notifications after every successful reset. Run pytest when an implementation exists. Review delivery actions and repository changes to verify no deployment was performed and no deployment workflow was added; do not propose a deployment target.

## Coverage and interpretation

RD8CDC-001 covers REQ-001, REQ-002 and REQ-014. RD8CDC-002 covers REQ-003, REQ-004 and REQ-005. RD8CDC-003 covers REQ-006, REQ-007 and REQ-008. RD8CDC-004 covers REQ-009, REQ-010 and REQ-012. RD8CDC-005 covers REQ-011, REQ-012, REQ-013, REQ-014 and REQ-016. RD8CDC-006 covers REQ-015, REQ-017 and REQ-018. Thus every approved requirement has at least one risk link. Suggested checks are prospective, not observed implementation defects, test outcomes, additional requirements or authorization to deploy.

## Assumptions

- The sign-in image governs its observed hierarchy, wording, and visual treatments, not exact pixels or color codes; the attachment read returned a reference, while the visual observations come from the approved assessment and task.
- Synthetic accounts and the in-memory notification sink are development/test mechanisms, not production integrations. For an accepted request for an existing synthetic account, a link is recorded in the sink without disclosing issuance in the public response.
- Until sign-in success behavior and a session model are specified, require the visible sign-in surface and invalidation of every active session where active sessions exist, without prescribing a successful sign-in destination.
- Until reset-page wording and layout are specified, the supplied image governs sign-in only; recovery pages are evaluated by functional criteria, not an invented design.
- No implementation or test results are established by the authorized evidence. All six risks and suggested checks are prospective.

## Open questions (nonblocking)

1. **What sign-in success behavior and session model are expected?** Interim assumption: specify the visible sign-in surface and require invalidation of every active session when a reset succeeds, without inventing sign-in success behavior.
2. **What exact reset-page wording and layout are expected?** Interim assumption: the wireframe governs sign-in only; recovery pages are evaluated by their functional behavior, not an invented layout.
