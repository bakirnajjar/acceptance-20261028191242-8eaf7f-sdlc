# Prospective delivery-risk map

**Run:** `f4999e68-bab3-45c1-8787-f00eb3a0eb4e`  
**Stage:** `custom_document` / `acceptance_20261028191242_8eaf7f_risk`  
**Basis:** approved `requirements_analysis` predecessor, `REQ-001`–`REQ-018`, and this run's assessment. These are prospective risks and suggested checks, **not observed implementation defects or test results**. No final custom-document contract is produced by this task.

## Evidence references

The identifiers below refer to authorized evidence; the reference objects preserve the returned source IDs and locators exactly. The approved predecessor provides the requirement identifiers and acceptance criteria, not an additional invented evidence citation.

- **S1 — story:** `{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}` — Python 3.12, Flask, server-rendered password recovery, synthetic accounts, in-memory notification sink, pytest, production-limitations documentation, no deployment or deployment workflows.
- **S2 — sign-in image:** `{"source_type":"attachment","source_id":"457acc5e-8bce-44d6-abec-d204c28e4d84","locator":"sign-in-wireframe.png"}` — observed sign-in hierarchy and wording as described in the assessment and predecessor; no exact pixel or color specification.
- **S3 — recovery standard:** `{"source_type":"knowledge","source_id":"28e06fb4-ccd1-4117-8f7b-b2a6c9bfaf1f","locator":"v1, chunk 0"}` — identical reset-request response for existing and missing accounts, five requests per account per hour, single-use links expiring 30 minutes after issue, all-session sign-out, and owner notification after every successful reset.

## Risk-to-requirement map

### RD8CDC-001 — Sign-in surface or recovery entry diverges

- **Approved requirements:** `REQ-001`, `REQ-002`, `REQ-014`.
- **Source references:** S1, S2, S3.
- **Prospective exposure and impact:** A sign-in page might contain fields but omit the observed bordered-panel hierarchy, exact labels and placeholder treatment, or the visible link might fail to start recovery. Client-only rendering would also miss the server-rendered-page requirement. Users might be unable to reach recovery, and the supplied sign-in evidence would not be honored.
- **Mitigation / verification ideas:** Render the sign-in page through Flask as server-rendered HTML. Check the bordered panel, bold “Sign in” heading, “Email address” and “Password” labels, `name@example.com` and masked `********` placeholders, blue underlined “Forgot password?” link **beneath** the password field, dark rectangular “Sign in” button below the link, and muted “No account? Contact your administrator.” footer. Exercise the link from the rendered sign-in page and confirm it reaches the reset-request flow. Review hierarchy and visual treatment without imposing exact dimensions or color codes. Do not infer successful sign-in behavior or a reset-page design from the image.

### RD8CDC-002 — Enumeration, throttling disclosure, or excess link issuance

- **Approved requirements:** `REQ-003`, `REQ-004`, `REQ-005`.
- **Source references:** S1, S3.
- **Prospective exposure and impact:** Distinct public responses for existing, missing, or throttled accounts could reveal account existence or limit state. Issuing a sixth link for an account within the preceding hour breaches the request cap; failing to issue a link for an accepted existing-account request blocks recovery.
- **Mitigation / verification ideas:** Keep the user-visible reset-request response identical across otherwise equivalent existing-account, missing-account, and throttled-account cases while separately deciding whether an existing synthetic account is eligible for link issuance. With controlled time and an inspected in-memory sink, exercise requests one through five, a sixth within the preceding hour, and a request once the applicable hour window has passed; verify no extra link on the sixth, eligible requests can yield a link, and public responses remain indistinguishable. Do not expose sink contents or throttle status through the public response.

### RD8CDC-003 — Reset link accepted outside its lifecycle or password unchanged

- **Approved requirements:** `REQ-006`, `REQ-007`, `REQ-008`.
- **Source references:** S1, S3.
- **Prospective exposure and impact:** A reused link, an expiry computed from request/sending/opening time rather than issue time, or an off-by-one comparison could permit an ineligible reset. Conversely, a valid link might not update the intended synthetic account password.
- **Mitigation / verification ideas:** Track when each link is **issued**, treat an unused eligible link as usable only before `issue_time + 30 minutes`, and prevent a successful link from completing any later reset. With controlled time, test immediately before the boundary, exactly at `issue_time + 30 minutes` (ineligible), and after it; test second submission of a used link. Verify an eligible completion changes the intended account's password, while ineligible/reused submissions cannot complete another password change.

### RD8CDC-004 — Successful reset leaves sessions active or owner uninformed

- **Approved requirements:** `REQ-009`, `REQ-010`, `REQ-012`.
- **Source references:** S1, S3.
- **Prospective exposure and impact:** A password change without invalidating every active session would leave old access in place. A missing owner-directed notification after any successful reset would conceal the change; notifications not recorded in the required in-memory sink would not be inspectable in this exercise.
- **Mitigation / verification ideas:** Make successful reset completion include all-session sign-out where active sessions exist and an owner-directed success notification recorded in the in-memory sink **after every success**. Set up multiple active sessions for a synthetic account where the implementation supports them and verify none remains signed in after completion; verify a sink entry per successful reset. Keep the session-model question open rather than prescribing sign-in success behavior. Distinguish these success notifications from reset-link issuance in the sink.

### RD8CDC-005 — Exercise architecture misrepresented as production-ready

- **Approved requirements:** `REQ-011`, `REQ-012`, `REQ-013`, `REQ-014`, `REQ-016`.
- **Source references:** S1, S3.
- **Prospective exposure and impact:** Substituting a production account integration or an external notification provider for the specified synthetic accounts and in-memory sink would change the exercise's scope; conversely, presenting volatile demo mechanisms as production-grade persistence or delivery would mislead readers. A different runtime/framework or non-server-rendered pages would also violate the approved delivery constraints.
- **Mitigation / verification ideas:** Inspect the Python 3.12/Flask runtime and rendered page responses; exercise recovery with synthetic accounts and inspect generated notifications in the in-memory sink without requiring an external service. Confirm the project documentation clearly describes synthetic-account and volatile-notification limitations and does not suggest production persistence, actual external notification delivery, or a deployment target.

### RD8CDC-006 — Policy gaps in tests or unauthorized deployment work

- **Approved requirements:** `REQ-015`, `REQ-017`, `REQ-018`.
- **Source references:** S1, S2, S3.
- **Prospective exposure and impact:** A narrow happy-path pytest suite could miss image/entry-flow deviations, enumeration including at-limit responses, the sixth-request cutoff, link reuse/expiry boundary, password update, all-session sign-out where active sessions exist, or notification after each success. Deploying the app or adding a deployment workflow would exceed the expressly approved scope.
- **Mitigation / verification ideas:** Review pytest coverage for the sign-in surface, link navigation, equivalent public responses, per-account-hour limit and sink effects, link issue-time boundary and single use, password update, session invalidation where applicable, and owner notifications after every successful reset. Run pytest when an implementation exists. Review delivery actions and repository changes to verify no deployment was performed and no deployment workflow was added; do not propose a deployment target.

## Coverage and interpretation

| Requirement | Risk item(s) | Requirement | Risk item(s) |
| --- | --- | --- | --- |
| `REQ-001` | RD8CDC-001 | `REQ-010` | RD8CDC-004 |
| `REQ-002` | RD8CDC-001 | `REQ-011` | RD8CDC-005 |
| `REQ-003` | RD8CDC-002 | `REQ-012` | RD8CDC-004, RD8CDC-005 |
| `REQ-004` | RD8CDC-002 | `REQ-013` | RD8CDC-005 |
| `REQ-005` | RD8CDC-002 | `REQ-014` | RD8CDC-001, RD8CDC-005 |
| `REQ-006` | RD8CDC-003 | `REQ-015` | RD8CDC-006 |
| `REQ-007` | RD8CDC-003 | `REQ-016` | RD8CDC-005 |
| `REQ-008` | RD8CDC-003 | `REQ-017` | RD8CDC-006 |
| `REQ-009` | RD8CDC-004 | `REQ-018` | RD8CDC-006 |

All 18 approved predecessor requirements have at least one risk link. The verification ideas are prospective checks tied to existing acceptance criteria, not new requirements or claims that the implementation currently passes or fails.

## Assumptions and nonblocking questions

- The sign-in image governs its observed hierarchy, wording, and visual treatments, **not** exact pixels or color codes; its read returned a reference, and the visual observations used here come from the task and assessment.
- Synthetic accounts and the in-memory notification sink are test/development mechanisms, not production integrations. An accepted request for an existing account records a link in the sink without disclosing whether a link was recorded in the public response.
- **Nonblocking:** “What sign-in success behavior and session model are expected?” Interim assumption: specify the visible sign-in surface and require invalidation of every active session when a reset succeeds, without inventing sign-in success behavior.
- **Nonblocking:** “What exact reset-page wording and layout are expected?” Interim assumption: the wireframe governs sign-in only; recovery pages are evaluated by their functional behavior, not an invented layout.
