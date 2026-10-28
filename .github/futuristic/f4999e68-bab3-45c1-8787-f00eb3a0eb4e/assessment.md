# Phase 1 assessment: Risk notes

## Scope and evidence

- Stage: `custom_document`; pinned key `acceptance_20261028191242_8eaf7f_risk`; risk-item prefix `RD8CDC`. The eventual deliverables are `docs/sdlc/acceptance_20261028191242_8eaf7f_risk.json` and `.md`, governed by the pinned `CustomDocumentOutput` schema. No deliverable is created during assessment.
- The full story requests a Python 3.12 Flask, server-rendered password-reset application using the sign-in wireframe and curated recovery standard, synthetic accounts, an in-memory notification sink, pytest coverage and production-limitations documentation; it prohibits deployment and deployment workflows. Story source reference: `{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}`.
- Supplied image `sign-in-wireframe.png`: a bordered sign-in panel with bold "Sign in" heading; "Email address" and "Password" labels; `name@example.com` and masked `********` placeholders; a blue underlined "Forgot password?" link beneath the password field; a dark rectangular "Sign in" button; and muted "No account? Contact your administrator." footer. Attachment source reference: `{"source_type":"attachment","source_id":"457acc5e-8bce-44d6-abec-d204c28e4d84","locator":"sign-in-wireframe.png"}`. This is an observed visual hierarchy, not an exact pixel/color specification.
- The curated *Account recovery standard (v1)* requires an account-independent reset response, at most five requests per account per hour, single-use links expiring 30 minutes after issue, all-session sign-out on successful reset, and owner notification after each successful reset. Knowledge source reference: `{"source_type":"knowledge","source_id":"28e06fb4-ccd1-4117-8f7b-b2a6c9bfaf1f","locator":"v1, chunk 0"}`.
- Authorized, approved predecessor output: `requirements_analysis` (read in full; `next_offset: null`), containing `REQ-001` through `REQ-018`, their acceptance criteria, assumptions and two nonblocking questions. Link risk items only to these approved IDs. The predecessor's account-existence-independent response criterion includes throttled requests, and link expiration is measured from issue time with ineligibility at the exact 30-minute boundary.

## Risk assessment for the later document

| Delivery-risk area | Approved requirements | Exposure and evidence to seek during implementation |
| --- | --- | --- |
| Sign-in and recovery entry diverge from the supplied image | REQ-001, REQ-002, REQ-014 | Reproducing only the controls but omitting their hierarchy, labels, link placement or functioning transition would miss the approved sign-in criteria; confirm rendered HTML and link navigation. |
| Account enumeration or limit-state disclosure | REQ-003, REQ-004, REQ-005 | Different visible responses for known/unknown or throttled accounts, or issuing a sixth link within the preceding hour, would violate recovery policy; compare public responses and sink entries in tests. |
| Reset-link lifecycle and password state | REQ-006, REQ-007, REQ-008 | Reuse, off-by-one expiration, measuring 30 minutes from the wrong event, or failing to update the password would invalidate recovery; test reuse and both sides of the issue-time boundary. |
| Incomplete post-reset cleanup or notification | REQ-009, REQ-010, REQ-012 | Active sessions might remain signed in, or the owner might not receive the success notification; test available active-session invalidation and recorded in-memory notification after each successful reset. |
| Demo-only architecture mistaken for production-ready behavior | REQ-011, REQ-012, REQ-013, REQ-014, REQ-016 | Synthetic accounts and volatile notifications are required for this exercise but do not provide persistence or external delivery; state limitations explicitly and keep the implementation within Python 3.12, Flask and server-rendered pages. |
| Inadequate automated coverage or out-of-scope deployment | REQ-015, REQ-017, REQ-018 | Passing a narrow happy-path test may conceal recovery-policy failures; no deployment or added deployment workflow is authorized. |

## Gaps and boundaries

- No implementation or test results are established by the authorized story, image, standard and predecessor output. These are prospective delivery risks, not claims of current defects; the later document should not claim observed failures without evidence.
- The approved predecessor leaves sign-in success behavior/session model and reset-page wording/layout unspecified. Keep its interim assumptions: apply the wireframe to sign-in only, require invalidation of all active sessions where they exist, and do not invent a successful sign-in destination or reset-page design. These remain nonblocking open questions, not new approved requirements.
- The story does not specify a production account store, notification delivery provider or deployment target; do not invent one. The later contract must include grounded source references, unique `RD8CDC-###` identifiers, explicit assumptions/open questions, and `requirement_ids` drawn only from `REQ-001` through `REQ-018`.
