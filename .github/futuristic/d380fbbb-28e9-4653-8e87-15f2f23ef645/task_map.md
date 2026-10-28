# Proposed implementation task map

**Status:** Dependency-ordered candidates for the later solution-design contract, not completed implementation or tests. These notes are the only output of T002. The approved `requirements_analysis` defines REQ-001–REQ-018; `ui_analysis` distinguishes observed sign-in details from proposed recovery states; `acceptance_20261028191242_8eaf7f_risk` supplies prospective verification risks RD8CDC-001–RD8CDC-006, not defects or test results. The prior-stage reader provided no independent stage-output citation locator. The records below cite only original authorized evidence.

## Candidate `DesignTask` records

### TASK-001 — Flask shell and recovery entry

```json
{
  "id": "TASK-001",
  "title": "Build Flask sign-in shell and recovery entry",
  "description": "Set up a Python 3.12 Flask application factory and server-rendered templates. Render the observed sign-in panel and a working Forgot password? link to a server-rendered reset-request form. Keep sign-in authentication and successful-login destination unspecified; the wireframe does not define them. Proposed recovery-page copy and styling are not wireframe facts.",
  "requirement_ids": ["REQ-001", "REQ-002", "REQ-013", "REQ-014"],
  "acceptance_criteria": [
    "On Python 3.12, Flask serves rendered HTML for the sign-in and reset-request pages; a browser can follow the sign-in Forgot password? link to the request form.",
    "The sign-in page displays a centered bordered panel with bold Sign in heading, labeled Email address and Password fields with name@example.com and masked ******** placeholders, a blue underlined Forgot password? link below the password field, a wide dark Sign in button below the link, and a muted No account? Contact your administrator. footer; exact pixels and color values are not asserted."
  ],
  "depends_on": [],
  "source_references": [
    {"source_type": "user_story", "source_id": "user_story", "locator": "characters 0-16000"},
    {"source_type": "attachment", "source_id": "457acc5e-8bce-44d6-abec-d204c28e4d84", "locator": "sign-in-wireframe.png"},
    {"source_type": "knowledge", "source_id": "28e06fb4-ccd1-4117-8f7b-b2a6c9bfaf1f", "locator": "v1, chunk 0"}
  ]
}
```

### TASK-002 — Synthetic state and private sink

```json
{
  "id": "TASK-002",
  "title": "Implement injectable synthetic recovery state",
  "description": "Provide in-process synthetic accounts with hashed passwords, synchronized request timestamps and token-digest records, an injected UTC clock, a test-inspectable but nonpublic notification sink, and server-side account/session-generation checks. Allow fixtures to register multiple sessions without inventing sign-in success behavior. Keep sensitive state out of visitor responses.",
  "requirement_ids": ["REQ-009", "REQ-011", "REQ-012"],
  "acceptance_criteria": [
    "A test can construct a synthetic account with a hashed password, register two independent active sessions, record and inspect internal reset-link and reset-success notification kinds, and observe no production account or external notification dependency.",
    "A session check rejects a registered session whose saved generation differs from its account's current generation; no public endpoint exposes the account inventory, token state, or notification sink."
  ],
  "depends_on": [],
  "source_references": [
    {"source_type": "user_story", "source_id": "user_story", "locator": "characters 0-16000"},
    {"source_type": "knowledge", "source_id": "28e06fb4-ccd1-4117-8f7b-b2a6c9bfaf1f", "locator": "v1, chunk 0"}
  ]
}
```

### TASK-003 — Reset request and issuance

```json
{
  "id": "TASK-003",
  "title": "Implement private reset-request eligibility and link issuance",
  "description": "Connect the server-rendered request form to a service using the synthetic state. Normalize an email for lookup, count accepted requests per existing account over the preceding rolling hour under a shared lock, and privately issue an opaque single-account link into the in-memory sink only for an accepted existing-account request. Present an account-independent generic response for equivalent valid existing, unknown, and at-limit requests; never expose issuance or throttle decisions.",
  "requirement_ids": ["REQ-003", "REQ-004", "REQ-005"],
  "acceptance_criteria": [
    "Equivalent valid requests for an existing account, an unknown account, and an existing account at its cap have identical public status, rendered content, and response/navigation class, without account or throttle disclosure.",
    "With controlled time, the first five requests for an existing account in a rolling hour each record one reset link; a sixth inside that hour records none and receives the same generic response; once the oldest accepted request is outside the preceding hour, another can issue a link."
  ],
  "depends_on": ["TASK-001", "TASK-002"],
  "source_references": [
    {"source_type": "user_story", "source_id": "user_story", "locator": "characters 0-16000"},
    {"source_type": "knowledge", "source_id": "28e06fb4-ccd1-4117-8f7b-b2a6c9bfaf1f", "locator": "v1, chunk 0"}
  ]
}
```

### TASK-004 — Redemption and successful-reset effects

```json
{
  "id": "TASK-004",
  "title": "Complete single-use resets and post-reset effects",
  "description": "Implement server-rendered new-password, ineligible-link, and success states. Check opaque token eligibility against its private digest and exact issue time, then recheck on POST and atomically update the token's account password hash, consume the token, advance that account's session generation, and append an owner-directed success notice before reporting success. Reject expired, malformed, and replayed tokens without successful side effects. A GET never consumes a token; do not assume a specified login destination or password-complexity rule.",
  "requirement_ids": ["REQ-006", "REQ-007", "REQ-008", "REQ-009", "REQ-010"],
  "acceptance_criteria": [
    "An eligible unused link submitted before issue_time + 30 minutes updates only its associated account's password and succeeds once; at exactly issue_time + 30 minutes or later it is ineligible, and a consumed link cannot complete a second reset.",
    "For an account with multiple previously active sessions, each successful reset makes every earlier session fail subsequent authorization checks and records one owner-directed reset-success notice in the private sink for that success; rejected or replayed submissions neither change a password nor record a success notice.",
    "Two submissions of one eligible link cannot both succeed, and rendered success is returned only after the password change, token consumption, session invalidation, and notification entry complete in-process."
  ],
  "depends_on": ["TASK-002", "TASK-003"],
  "source_references": [
    {"source_type": "user_story", "source_id": "user_story", "locator": "characters 0-16000"},
    {"source_type": "knowledge", "source_id": "28e06fb4-ccd1-4117-8f7b-b2a6c9bfaf1f", "locator": "v1, chunk 0"}
  ]
}
```

### TASK-005 — Automated verification

```json
{
  "id": "TASK-005",
  "title": "Verify sign-in and recovery behavior with pytest",
  "description": "Add pytest coverage using the Flask client, synthetic accounts, controlled issue-time clock, multiple session fixtures, and private sink inspection. Verify the sign-in visual hierarchy and navigation, generic response equality including at the cap, rolling-hour issuance, token use/replay and exact expiry boundary, password change, all-session invalidation, and notification after each success. Treat risk items as prospective checks, not recorded defects.",
  "requirement_ids": ["REQ-015"],
  "acceptance_criteria": [
    "Running pytest checks the rendered sign-in evidence and recovery navigation, existing/unknown/at-limit public response equality, first-five/sixth-request/rolling-hour link counts, and absence of public notification-sink disclosure.",
    "Running pytest checks token submission just before, at, and after issue_time + 30 minutes; replay and competing submissions; correct password update; invalidation of multiple earlier active sessions; and one owner notice for each successful reset without a notice for rejected attempts."
  ],
  "depends_on": ["TASK-001", "TASK-002", "TASK-003", "TASK-004"],
  "source_references": [
    {"source_type": "user_story", "source_id": "user_story", "locator": "characters 0-16000"},
    {"source_type": "attachment", "source_id": "457acc5e-8bce-44d6-abec-d204c28e4d84", "locator": "sign-in-wireframe.png"},
    {"source_type": "knowledge", "source_id": "28e06fb4-ccd1-4117-8f7b-b2a6c9bfaf1f", "locator": "v1, chunk 0"}
  ]
}
```

### TASK-006 — Limitations and delivery boundary

```json
{
  "id": "TASK-006",
  "title": "Document production limitations and verify no deployment",
  "description": "Document synthetic accounts, volatile single-process account/token/request/session state, in-memory rather than externally delivered notifications, restart and cross-worker limitations, and unresolved production hardening. Review delivered actions and changed paths to verify no application deployment and no added deployment workflow. This is documentation and negative-scope verification, not deployment authorization.",
  "requirement_ids": ["REQ-016", "REQ-017", "REQ-018"],
  "acceptance_criteria": [
    "Project documentation explicitly identifies synthetic-account and in-memory-notification limitations, lost state at restart, lack of cross-worker durability, and the absence of a production account or mail integration; it does not claim production readiness.",
    "Review of delivery actions finds no performed deployment, and review of repository changes finds no added deployment workflow."
  ],
  "depends_on": ["TASK-005"],
  "source_references": [
    {"source_type": "user_story", "source_id": "user_story", "locator": "characters 0-16000"}
  ]
}
```

## Requirement coverage and disposition

Every approved requirement maps to at least one candidate. **Missing: none; no “not implemented” disposition is proposed.** TASK-005 verifies additional requirements besides the direct REQ-015 linkage; verification does not replace their implementation-task linkage.

| Requirement | Candidate implementing / verifying task | Disposition |
| --- | --- | --- |
| REQ-001 | TASK-001; TASK-005 verification | Covered |
| REQ-002 | TASK-001; TASK-005 verification | Covered |
| REQ-003 | TASK-003; TASK-005 verification | Covered |
| REQ-004 | TASK-003; TASK-005 verification | Covered |
| REQ-005 | TASK-003; TASK-005 verification | Covered |
| REQ-006 | TASK-004; TASK-005 verification | Covered |
| REQ-007 | TASK-004; TASK-005 verification | Covered |
| REQ-008 | TASK-004; TASK-005 verification | Covered |
| REQ-009 | TASK-002, TASK-004; TASK-005 verification | Covered where active sessions exist; sign-in behavior remains unspecified |
| REQ-010 | TASK-004; TASK-005 verification | Covered |
| REQ-011 | TASK-002; TASK-005 verification | Covered |
| REQ-012 | TASK-002; TASK-005 verification | Covered |
| REQ-013 | TASK-001; TASK-005 verification | Covered |
| REQ-014 | TASK-001; TASK-005 verification | Covered |
| REQ-015 | TASK-005 | Covered |
| REQ-016 | TASK-006 | Covered |
| REQ-017 | TASK-006 | Covered by explicit no-deployment check, not a deployment task |
| REQ-018 | TASK-006 | Covered by explicit no-workflow check, not workflow work |

Prospective risk-check alignment: RD8CDC-001 → TASK-001/005; RD8CDC-002 → TASK-003/005; RD8CDC-003 and RD8CDC-004 → TASK-004/005; RD8CDC-005 → TASK-002/005/006; RD8CDC-006 → TASK-005/006. These are planning links only, not extra requirements or completed verification.

**Open evidence boundaries:** The sign-in wireframe does not specify successful authentication, a sign-in destination, recovery-page layout, or exact CSS values. Neither the story nor standard specifies a password-complexity policy. Session fixtures make all-session invalidation testable without claiming the sign-in button implements login. Volatile in-process state and a private sink do not constitute durable persistence, real message delivery, or production readiness.
