# Changelog

All notable changes to this repository are documented here.

The format is based on Keep a Changelog and the project uses Semantic Versioning.

## [Unreleased]

### Added

- OpenAPI 3.1 contracts for the party, policy, contract, direct-claims,
  assumed-claims, cession, retrocession, document, payment, and notifications
  verticals, covering the implemented public domain API and internal expert API.
- `openapi/components.yaml` with the canonical Problem error envelope, money,
  the offset page envelope, ETag and If-Match, Idempotency-Key, audit fields,
  entity references, and tenant/book headers.
- AsyncAPI 3 event catalog and ten vertical event documents for the 151 domain
  events declared in SPEC 11.
- JSON Schema 2020-12 documents for the error envelope, money, and event
  envelope.
- `scripts/validate_contracts.py`, a standard-library-only validator for YAML
  parsing, required paths, shared components, event catalog consistency, schema
  members, and JSON References.
- `MISMATCHES.md`, the contract-to-implementation audit with source evidence,
  including the closed-mismatch table and the Round 2 synchronous FS-RI
  hand-off deviation.
- README sections for versioning, compatibility, validation, and the deviation
  policy.

### Changed in Round 2 (2026-10-19)

- `openapi/policy.yaml` is contract 2.0.0: list responses use the page envelope
  `{items, page, size, total, _links:{self, next, prev}}`; errors are canonical
  RFC 9457 `Problem` responses; `ETag`/`If-Match` and `Idempotency-Key` are
  documented with 409 `CONCURRENT_MODIFICATION`, 409 `IDEMPOTENCY_CONFLICT`,
  and the 200 `Idempotent-Replayed` replay; illegal transitions and duplicate
  policy numbers are 409.
- `openapi/components.yaml` is contract 1.1.0: `Page`, `PageMeta`/`PageLinks`,
  `IdempotencyKey`, `IfMatch`, `ETag`, and `Idempotent-Replayed` describe the
  implemented Policy behaviour; `Problem` and the shared responses document the
  Policy codes and the FS-RI/API error categories.
- `openapi/cession.yaml` and `openapi/retrocession.yaml` are contract 1.1.0:
  `fsriHandoffId`, `fsriStatus`, `fsriHandedOffAt`, and `fsriLastError` on the
  case; optional `fsriContractNumber` on the transition; HANDOFF_PENDING calls
  FS-RI and returns HANDED_OFF on success; the document-level
  `x-fsri-error-mapping` records the 400/409/502/503 mappings; the internal
  hand-off persistence operations are documented.
- `schemas/error-envelope.schema.json` notes the Policy adoption, the legacy
  code strings, and the `correlationId` behaviour.
- `README.md` records the Round 2 compatibility and version classification:
  Policy is a breaking 2.0.0 contract retained on `/api/v1` because its only
  consumer is co-released; Cession and Retrocession are additive 1.1.0.
- `MISMATCHES.md` closes M-03, M-09, and M-15, updates M-02, M-04, M-05, M-06,
  M-07, M-11, and M-17 for Policy, notes that the remaining verticals are
  unchanged, and adds M-21 for the synchronous FS-RI hand-off.

### Changed in Round 5 (2026-10-19)

- `openapi/policy.yaml` is contract 2.1.0: adds policy versions, coverage and
  limits, aggregate erosion, endorsements, insureds, locations, cancellations,
  and reinstatements on both the public and the expert surfaces; adds the 422
  `UnprocessableContent` and 428 `PreconditionRequired` responses with the
  business-rule and approval codes; keeps the page envelope, ETag/If-Match,
  Idempotency-Key, and Problem schemas unchanged.
- `openapi/contract.yaml` is contract 2.0.0: adds layers, participants, terms,
  security, cessions, bordereaux, commutations, bind-eligibility, and bind on
  both surfaces. `PATCH /status` to BOUND is now 409 `BIND_REQUIRES_COMMAND`;
  bind is the only path to BOUND.
- `openapi/direct-claims.yaml` is contract 1.1.0: adds injuries, exposures,
  append-only reserve history, the coverage decision, litigation, settlements,
  recoveries, liens, and close, and completes the claim projection.
- `openapi/assumed-claims.yaml` is contract 1.1.0: adds loss advices,
  bordereau ingest, reserve history, cash calls, recoveries, commutation,
  disputes, audit, financials, and close, with 422 and 428 responses.
- `openapi/components.yaml` is contract 1.2.0: `UnprocessableContent` and
  `PreconditionRequired` become shared responses, `Percent` becomes
  implemented, and the page envelope covers the Policy second-slice
  collections.
- `asyncapi/party.yaml`, `asyncapi/cession.yaml`,
  `asyncapi/retrocession.yaml`, `asyncapi/document.yaml`,
  `asyncapi/payment.yaml`, and `asyncapi/notifications.yaml` are 1.1.0 and mark
  the events the transactional-outbox rollout actually emits as implemented.
- `asyncapi/event-catalog.yaml` is 1.1.0: it publishes 164 event names and
  records the implemented subset per vertical (`implemented`).
- `scripts/validate_contracts.py` now requires the Round 5 paths, the two new
  shared responses, the implemented-channel/catalog cross-check, and the
  Round 5 implemented event names.
- `README.md` records the Round 5 versions and compatibility classes;
  `MISMATCHES.md` shrinks M-04, M-06, M-07, M-08, M-10, M-11, M-12, M-13,
  M-14, M-16, M-20, and M-21, and adds M-22 for the implemented event names.

### Changed in the outbox completion (2026-10-20)

- `asyncapi/policy.yaml` is 1.1.0: `policy.policy.created` and
  `policy.policy.updated` are added and, with `version-issued`, `endorsed`,
  `cancelled`, and `reinstated`, marked implemented; the two new channels carry
  a minimal data schema and name their emitter.
- `asyncapi/contract.yaml` is 1.1.0: `contract.contract.updated` is added and,
  with `created`, `bound`, `commuted`, and `cession.recorded`, marked
  implemented; the new channel carries a minimal data schema.
- `asyncapi/direct-claims.yaml` is 1.1.0: `registered`, `updated`,
  `coverage-assessed`, `reserve-changed`, `settlement-authorized`, and `closed`
  are marked implemented.
- `asyncapi/assumed-claims.yaml` is 1.1.0: `assumed.claim.updated` is added and,
  with `registered`, `closed`, `reopened`, `loss-advice-posted`,
  `reserve-changed`, `cash-call-requested`, `recovery-recorded`, and
  `commuted`, marked implemented; the new channel carries a minimal data schema.
- `asyncapi/event-catalog.yaml` is 1.2.0: the four new names are published
  (168 total) and all ten verticals record their implemented subset; the
  implementation notes now name the platform `event-ingest` inbox.
- `scripts/validate_contracts.py` requires the implemented event names for all
  ten verticals instead of the Round 5 six.
- `MISMATCHES.md` expands M-14 to the ten publishers and the `event-ingest`
  inbox, updates M-22 with the four names that have no SPEC equivalent, and
  records 8,607 passing validation checks.
- `README.md` records the completed rollout and its additive compatibility
  class.

### Added in the global-search contract (2026-10-20)

- `openapi/components.yaml` is contract 1.3.0: adds the shared
  `SearchResponse` (`query`, `limit`, `items`), `SearchItem` (`id`, `type`,
  `label`, `secondary`, `status`, `href`), and `SearchType` schemas and the
  `SearchQuery` (`q`) and `SearchLimit` (`limit`, default 10, minimum 1,
  maximum 25) parameters.
- The ten vertical OpenAPI documents add one public search operation each:
  `GET /api/v1/parties/search`, `/policies/search`, `/contracts/search`,
  `/claims/search`, `/assumed-claims/search`, `/cessions/search`,
  `/retrocessions/search`, `/documents/search`, `/payments/search`, and
  `/notifications/search`. Each requires `X-EIA-Tenant`, requires and validates
  `X-EIA-Book` on the six book-scoped verticals, documents the shared
  `SearchResponse` 200, and documents a problem+json 400 for a missing tenant
  or book or an invalid limit. Each operation keeps the document-level
  security and the list operation's security requirement, and carries an
  `x-search-type` naming the `SearchType` it emits.
- Document versions are additive: party 1.1.0, policy 2.2.0, contract 2.1.0,
  direct-claims 1.2.0, assumed-claims 1.2.0, cession 1.2.0, retrocession 1.2.0,
  document 1.1.0, payment 1.1.0, and notifications 1.1.0.
- `scripts/validate_contracts.py` now requires the ten search paths, the shared
  search parameters and `SearchResponse` schema, the `SearchResponse` and
  `SearchItem` keys, the operation-level `x-search-type`, the 200 schema
  reference, the problem+json 400, the 404 book-scope response on the six
  book-scoped verticals, and security parity with each list operation.
- `README.md` documents the ten routes, request rules, response shape, the book
  matrix, and the additive compatibility classification; `MISMATCHES.md` adds
  M-23 for the SPEC naming gap and the current limit/book validation divergence.
- `python scripts/validate_contracts.py` passes 8,874 checks with 0 failures.

### Added in the Direct Claims task and note contract (2026-10-20)

- `openapi/direct-claims.yaml` is 1.3.0: adds `GET/POST
  /api/v1/claims/{claimId}/tasks`, `PATCH
  /api/v1/claims/{claimId}/tasks/{taskId}`, and `GET/POST
  /api/v1/claims/{claimId}/notes`, their `/internal/v1` expert equivalents, and
  the `Task`, `TaskCreate`, `TaskStatusChange`, `Note`, and `NoteCreate`
  schemas. Every route keeps the DIRECT book wall, the tenant header, the
  document-level session-cookie security, and the 400/404 responses; the
  mutations also document 409.
- `asyncapi/direct-claims.yaml` is 1.2.0: adds implemented channels and `send`
  operations for `direct.claim.task-created`, `direct.claim.task-completed`,
  `direct.claim.task-updated`, and `direct.claim.note-added`, each naming
  `ClaimEvents.java` in `x-implemented-by`.
- `asyncapi/event-catalog.yaml` is 1.3.0: the four task/note names are added to
  the Direct Claims published and implemented lists (172 published in total).
- `scripts/validate_contracts.py` requires the five public and five internal
  task/note paths, the five schemas, and the four task/note events in the
  Direct Claims implemented list.
- `README.md` records the task/note versions, routes, and schemas;
  `MISMATCHES.md` extends M-07 with the retry caveat for the task/note POSTs and
  updates M-22 for the four names that have no SPEC equivalent.
- `python scripts/validate_contracts.py` passes 9,155 checks with 0 failures.

### Added in the Assumed Claims task and note contract (2026-10-20)

- `openapi/assumed-claims.yaml` is 1.3.0: adds `GET/POST
  /api/v1/assumed-claims/claims/{claimId}/tasks`, `PATCH
  /api/v1/assumed-claims/claims/{claimId}/tasks/{taskId}`, and `GET/POST
  /api/v1/assumed-claims/claims/{claimId}/notes`, and the `Task`, `TaskCreate`,
  `TaskStatusChange`, `Note`, and `NoteCreate` schemas. Every route requires
  `X-EIA-Tenant` and `X-EIA-Book: ASSUMED`, keeps the document-level
  session-cookie security, and documents 400/404; the mutations also document
  409. The short `/api/v1/assumed-claims/{claimId}/...` form is recorded in
  `x-path-alias`.
- `asyncapi/assumed-claims.yaml` is 1.2.0: adds implemented channels and `send`
  operations for `assumed.claim.task-created`,
  `assumed.claim.task-completed`, `assumed.claim.task-updated`, and
  `assumed.claim.note-added`, each naming `AssumedClaimEvents.java` in
  `x-implemented-by`.
- `asyncapi/event-catalog.yaml` is 1.4.0: the four task/note names are added to
  the Assumed Claims published and implemented lists (176 published in total).
- `scripts/validate_contracts.py` requires the five Assumed Claims task/note
  paths, the five schemas, and the four task/note events in the Assumed Claims
  implemented list.
- `README.md` records the task/note versions, routes, schemas, and the
  idempotency caveat; `MISMATCHES.md` extends M-07 with the Assumed Claims
  retry caveat, M-06 with the task version check, M-14 with the four implemented
  events, and M-22 with the four names that have no SPEC 11.5.9 equivalent.
- `python scripts/validate_contracts.py` passes 9,361 checks with 0 failures.

### Added in the payment source linkage contract (2026-10-20)

- `openapi/payment.yaml` is 1.2.0: adds `sourceType`, `sourceId`, and
  `sourceReference` to the `Payment` projection and to
  `CreatePaymentRequest` and `CreatePaymentRequestInternal`; adds the
  `PaymentSourceType` enum (`DIRECT_CLAIM`, `ASSUMED_CLAIM`, `POLICY`, `OTHER`);
  and documents the create rules. A classified source requires `sourceId`,
  `sourceId` requires `sourceType`, `OTHER` may be reference-only, and
  `sourceReference` is at most 64 characters. The search operation now documents
  that matching covers `sourceId` and `sourceReference` and that a present
  `sourceReference` is appended to the `secondary` line.
- `asyncapi/payment.yaml` is 1.2.0: the implemented `payment.payment.created`
  channel carries a `PaymentPaymentCreatedData` message whose payload schema
  includes the optional `sourceType`, `sourceId`, and `sourceReference` fields.
- `scripts/validate_contracts.py` requires the source fields on `Payment`,
  both create request schemas, and the created event payload; it also requires
  the classified-source/sourceId rule, the sourceId/sourceType pairing rule, the
  four-value enum, the UUID format, the 64-character reference limit, and the
  source fields to remain optional on the create requests and the event payload.
- `README.md` documents the source semantics, the search suffix behaviour, and
  why the denormalized `sourceReference` avoids an N+1 lookup; the
  `MISMATCHES.md` M-12 "no claim" gap is replaced with the implemented source
  link, M-13 records the naming difference, and the new M-24 records the SPEC
  `claim_vertical`/`claim_id`/`claim_number` deviation and the absent source
  existence check.
- `python scripts/validate_contracts.py` passes 9,411 checks with 0 failures.

### Added in the payment source filter contract (2026-10-20)

- `openapi/payment.yaml` is 1.3.0: `GET /api/v1/payments` accepts the optional
  `sourceType` and `sourceId` query parameters. Both must be supplied together;
  `sourceType` references the four-value `PaymentSourceType` enum
  (`DIRECT_CLAIM`, `ASSUMED_CLAIM`, `POLICY`, `OTHER`) and is trimmed and
  upper-cased before validation, and `sourceId` is a UUID. The tenant header
  stays required. The operation documents the exact, tenant-scoped,
  newest-first filter, 400 `INVALID_SOURCE_TYPE` for an unknown type, 400
  `INVALID_SOURCE_FILTER` for a partial pair, and 400 `INVALID_PARAMETER` for a
  malformed `sourceId` or tenant. The expert list documents the same pair and
  its `tenantId` scope.
- `scripts/validate_contracts.py` requires the `sourceType` + `sourceId` pair
  on both payment list operations, both parameters to stay optional query
  parameters, the `PaymentSourceType` reference and its four-value enum, the
  UUID `sourceId`, the tenant parameter, the 400 response, and the
  `INVALID_SOURCE_TYPE`/`INVALID_SOURCE_FILTER` codes in each operation
  description.
- `README.md` records the 1.3.0 additive compatibility class and the filter
  semantics; `MISMATCHES.md` extends M-24 with the exact-pair filter, its
  evidence, and the new validation evidence.
- `python scripts/validate_contracts.py` passes 10,199 checks with 0 failures.

### Added in the claim command idempotency contract (2026-10-20)

- `openapi/components.yaml` is 1.4.0: adds the optional
  `ClaimIdempotencyKey` parameter (`Idempotency-Key`, 1-64 characters) and the
  `IdempotentReplay` response header (`true`/`false`) used by claim task and
  note creates, and documents the invalid-key 400 (`INVALID_IDEMPOTENCY_KEY`)
  and the `EIA-DIR-4091`/`EIA-RNS-4091` (`IDEMPOTENCY_KEY_REUSED`) 409 in the
  shared BadRequest and Conflict descriptions.
- `openapi/direct-claims.yaml` is 1.4.0: the public and expert task and note
  POSTs accept the optional header, document the 201 `Idempotent-Replay` header,
  400 `VALIDATION_ERROR` for a key that is too long or contains a non-printable
  character, and 409 `EIA-DIR-4091` with category `IDEMPOTENCY_KEY_REUSED` for
  the same key with a different body. A concurrent parent-claim change remains
  a 409.
- `openapi/assumed-claims.yaml` is 1.4.0: the public task and note POSTs accept
  the optional header, always emit `Idempotent-Replay` on a 201, and document
  400 `EIA-RNS-7004` with field code `INVALID_IDEMPOTENCY_KEY` and 409
  `EIA-RNS-4091` with category `CONFLICT` and
  `errors[0].code = IDEMPOTENCY_KEY_REUSED`.
- `scripts/validate_contracts.py` requires the shared 1-64 character
  `ClaimIdempotencyKey` parameter, the shared `IdempotentReplay` header, the
  201 `Idempotent-Replay` header, the shared 400 invalid-key description, and
  the 409 code and Problem schema on all six claim task and note POST
  operations in both documents.
- `README.md` records the additive versions, the request and response
  semantics, and the remaining Direct Claims reservation race;
  `MISMATCHES.md` M-07 is narrowed to the remaining coverage gap plus the
  Direct Claims race and the `Idempotent-Replay` spelling difference.
- `python scripts/validate_contracts.py` passes 9,470 checks with 0 failures.

### Added in the claim assignment contract (2026-10-20)

- `openapi/components.yaml` is 1.5.0: adds the optional shared `ActorHeader`
  (`X-EIA-Actor`, at most 128 characters) used by the claim assignment
  operations, and documents the default-to-adjuster and audit/`assignedBy`
  semantics.
- `openapi/direct-claims.yaml` is 1.5.0: adds `PATCH
  /api/v1/claims/{claimId}/assignment` and the `/internal/v1` expert route, the
  `AssignClaimRequest` schema (`assignedAdjuster` required, max 128;
  `assignedTeam` optional, max 64; `expectedVersion` required, integer >= 0),
  the optional `X-EIA-Actor` header, and the nullable `assignedAdjuster`,
  `assignedTeam`, and `assignedAt` fields on `Claim`. The operations document
  the 200/400/404/409 problem responses, the stale-version 409, the
  same-assignment no-op, and the `direct.claim.assigned` event.
- `openapi/assumed-claims.yaml` is 1.5.0: adds `PATCH
  /api/v1/assumed-claims/claims/{claimId}/assignment` (alias
  `/api/v1/assumed-claims/{claimId}/assignment`) and the `/internal/v1` expert
  route, the `AssignClaimRequest` schema, the optional `X-EIA-Actor` header, and
  the nullable assignment fields on `AssumedClaim`, with the same 200/400/404/409
  and no-op semantics and the `assumed.claim.assigned` event.
- `asyncapi/direct-claims.yaml` is 1.3.0 and `asyncapi/assumed-claims.yaml` is
  1.3.0: adds implemented channels and `send` operations for
  `direct.claim.assigned` and `assumed.claim.assigned`, each naming its
  `*ClaimEvents.java` emitter and describing the payload, the actor, and the
  no-op rule.
- `asyncapi/event-catalog.yaml` is 1.5.0: the two assignment names are added to
  the Direct Claims and Assumed Claims published and implemented lists (178
  published in total).
- `scripts/validate_contracts.py` requires the public and expert assignment
  paths on both claim verticals, the `AssignClaimRequest` schema and its field
  bounds (including the optional nullable team), the nullable
  `assignedAdjuster`/`assignedTeam`/`assignedAt` projection fields, the shared
  optional `ActorHeader`, the assignment 200/400/404/409 responses, and the two
  implemented event names.
- `README.md` records the assignment ownership and actor semantics, the route
  and version table, and the validator coverage; `MISMATCHES.md` adds M-25 for
  the Assumed Claims domain team requirement, the Direct Claims negative-version
  409, and the `X-EIA-User` alias, and updates M-14 and M-22 with the two new
  event names.
- `python scripts/validate_contracts.py` passes 9,656 checks with 0 failures.

### Added in the document association-link contract (2026-10-20)

- `openapi/document.yaml` is 1.2.0: adds `GET|POST
  /api/v1/documents/{documentId}/links` and `DELETE
  /api/v1/documents/{documentId}/links/{linkId}`, the same three operations on
  the expert's `/internal/v1` base, the `DocumentLink` projection (`id`,
  `documentId`, `linkedType`, `linkedId`, `linkedReference`, `linkedLabel`,
  `createdAt`), the `CreateDocumentLinkRequest` command, and the closed
  `DocumentLinkedType` enum. `GET /api/v1/documents` accepts the optional
  `linkedType` + `linkedId` pair, search `q` matches a link's
  `linkedReference`, and the link operations document 201/204/400/404/409
  (`DUPLICATE_LINK`) with the required tenant header.
- `asyncapi/document.yaml` is 1.2.0: adds implemented channels and `send`
  operations for `document.link.added` and `document.link.removed`, naming
  `DocumentLinkEvents.java` and describing the `DocumentLink` aggregate and
  payload.
- `asyncapi/event-catalog.yaml` is 1.6.0: the two link names are published and
  implemented (180 published in total).
- `scripts/validate_contracts.py` requires the six link operations, the
  `DocumentLink`, `CreateDocumentLinkRequest`, and `DocumentLinkedType` schemas
  and their bounds, the list `linkedType` + `linkedId` pair, the expert `q`,
  the search `linkedReference` match, and the two implemented event names.
- `README.md` records the link routes, projection, enum, filter, duplicate and
  delete semantics, events, and versions; `MISMATCHES.md` adds M-26 for the
  flat tenant-scoped link against the SPEC association triple, role, book, and
  DOC-09 check, and updates M-14 and M-22 with the two new event names.
- `python scripts/validate_contracts.py` passes 9,865 checks with 0 failures.

### Added in the Policy billing contract (2026-10-20)

- `openapi/policy.yaml` is 2.3.0: adds `GET/POST
  /api/v1/policies/{policyId}/billing` and `PATCH
  /api/v1/policies/{policyId}/billing/installments/{installmentId}`, the flat
  `BillingPlan` and `Installment` projections, the `CreateBillingPlanRequest`
  (`installmentCount` 1..24, `frequency` enum, `firstDueDate`) and
  `UpdateInstallmentRequest` (`status` PAID or WAIVED, optional `paymentId`)
  commands, and the 200/201/400/404/409 responses. A policy has at most one
  ACTIVE plan; the premium split preserves the total exactly at scale 4.
- `openapi/components.yaml` is 1.6.0: adds the optional
  `BookHeaderDirectOptional` parameter (`X-EIA-Book`; DIRECT when present, an
  absent header accepted for compatibility, another book hidden as 404
  `BOOK_SCOPE_VIOLATION`).
- `asyncapi/policy.yaml` is 1.2.0: adds implemented channels and `send`
  operations for `policy.billing-plan.created`, `policy.installment.paid`, and
  `policy.installment.waived`, each naming `PolicyEvents.java`.
- `asyncapi/event-catalog.yaml` is 1.7.0: the three billing names are published
  and implemented (183 published in total).
- `scripts/validate_contracts.py` requires the three billing paths, the optional
  shared book parameter, the `BillingPlan`, `Installment`,
  `CreateBillingPlanRequest`, and `UpdateInstallmentRequest` schemas with their
  bounds and enums, and the three implemented billing events.
- `README.md` records the billing routes, projection, split and settlement
  semantics, the DIRECT book rule, and the additive versions; `MISMATCHES.md`
  updates M-06, M-07, M-12, M-14, and M-22 and adds M-27 for the SPEC 11.2.13
  route, event-name, and status-vocabulary differences.
- `python scripts/validate_contracts.py` passes 10,105 checks with 0 failures.

### Added in the Policy renewal contract (2026-10-20)

- `openapi/policy.yaml` is 2.4.0: adds `POST
  /api/v1/policies/{policyId}/renew`, the `RenewPolicyRequest` schema
  (`effectiveDate` and `expirationDate` required; `premiumAmount`,
  `premiumCurrency`, `limitAmount`, and `limitCurrency` optional and defaulting
  to the source policy), the nullable `Policy.renewedFromPolicyId` lineage
  field, and the 201 successor `Policy` with the shared `ETag`. The operation
  requires `X-EIA-Tenant` and `X-EIA-Book: DIRECT` and documents 400
  `VALIDATION_ERROR`, 404 `POLICY_NOT_FOUND`, and 409 `RENEWAL_NOT_ALLOWED` for
  a source that is not `ISSUED`, `IN_FORCE`, `ENDORSED`, or `REINSTATED`. The
  source policy is never mutated.
- `asyncapi/policy.yaml` is 1.3.0: the existing `policy.policy.renewed` channel
  and `send` operation are marked implemented, name `PolicyEvents.java`, and
  carry a `PolicyPolicyRenewedData` payload schema with the successor identity
  and term, `renewedFromPolicyId`, and both lineage sides.
- `asyncapi/event-catalog.yaml` is 1.8.0: `policy.policy.renewed` joins the
  Policy `implemented` subset. It was already published, so the platform total
  stays 183 published events and the Policy subset becomes 10 of its 23 names.
- `scripts/validate_contracts.py` requires the renewal path, the required tenant
  and DIRECT book parameters, the `RenewPolicyRequest` required/optional split
  and date/money/currency field types, the 201 successor `Policy` with the
  shared ETag, the 400/404/409 responses with `RENEWAL_NOT_ALLOWED` on the 409,
  the nullable `Policy.renewedFromPolicyId`, and `policy.policy.renewed` in the
  Policy implemented event list.
- `README.md` records the renewal route, request rules, successor semantics,
  eligibility statuses, the required DIRECT book, the no-idempotency caveat, and
  the additive versions; `MISMATCHES.md` adds M-28 for the SPEC 11.2.6 RENEWED
  transition and SPEC 11.2.10 base-path deviations plus the relaxed expert
  `effectiveDate`, and updates M-06, M-07, M-12, M-14, and M-22 with the renewal
  command and event.
- `python scripts/validate_contracts.py` passes 10,171 checks with 0 failures.

### Added in the contract technical accounts contract (2026-10-20)

- `openapi/contract.yaml` is 2.2.0: adds `GET/POST
  /api/v1/contracts/{contractId}/technical-accounts` and `PATCH
  /api/v1/contracts/{contractId}/technical-accounts/{accountId}/status`, the
  `TechnicalAccount` projection (`accountId`, `accountNumber`, `contractId`,
  `periodStart`, `periodEnd`, `currency`, `cededPremium`, `cededLosses`,
  `commission`, `otherCharges`, `balance`, `status`, `createdAt`), the
  `TechnicalAccountStatus` enum (DRAFT, ISSUED, SETTLED), the
  `CreateTechnicalAccountRequest` command (period, currency, and four required
  non-negative amounts; server-derived account number and balance), and the
  `UpdateTechnicalAccountStatusRequest` command (status ISSUED or SETTLED). The
  operations document `X-EIA-Tenant`, `X-EIA-Book: ASSUMED`, 200/201, 400, 404,
  and 409 `DUPLICATE_TECHNICAL_ACCOUNT_PERIOD`/`INVALID_STATUS_TRANSITION`.
- `asyncapi/contract.yaml` is 1.2.0: adds implemented child-aggregate channels
  and `send` operations for `contract.technical-account.created`,
  `contract.technical-account.issued`, and `contract.technical-account.settled`,
  a shared `ContractTechnicalAccountData` payload, and the account aggregate
  versions 1/2/3.
- `asyncapi/event-catalog.yaml` is 1.9.0: the three names are published and
  implemented (186 published in total; Contract 24 published and 8 implemented).
- `scripts/validate_contracts.py` requires the three public operations, the
  `TenantHeader` and `BookHeaderAssumed` parameters, the 200/201, 400, 404, and
  409 responses, the four schemas and their field types and enums, and the
  three implemented technical-account events in the catalog and channels.
- `README.md` records the technical-account routes, projection, period,
  balance, lifecycle, book, and event semantics, and the additive versions;
  `MISMATCHES.md` adds M-29 for the SPEC path, status-vocabulary, line-breakdown,
  overlap/window, and absent-book differences, and updates M-12, M-14, and M-22
  with the new slice and event names.
- `python scripts/validate_contracts.py` passes 10,406 checks with 0 failures.

### Added in the contract period-bordereaux contract (2026-10-20)

- `openapi/contract.yaml` is 3.0.0: the public
  `GET/POST /api/v1/contracts/{contractId}/bordereaux` operations now use the
  period-bordereau `Bordereau`, `CreateBordereauRequest`, and `BordereauStatus`
  schemas. The projection is `{bordereauId, bordereauNumber, contractId,
  periodStart, periodEnd, receivedDate, currency, premiumAmount, lossAmount,
  commissionAmount, otherChargesAmount, lineCount, notes, status,
  technicalAccountId, createdAt}`; the create command owns the period,
  received date, currency, four non-negative amounts, line count, and optional
  note, while the number and initial RECEIVED status are server-owned. Adds
  `PATCH /api/v1/contracts/{contractId}/bordereaux/{bordereauId}/status` with
  `UpdateBordereauStatusRequest` (`status` PROCESSED or FAILED, optional
  `notes`), the RECEIVED -> PROCESSED|FAILED transition table, the
  technical-account linkage on PROCESSED, and the 201/200, 400, 404, and 409
  responses. The public bordereau list is a bare array, newest period first.
  The legacy source-document ingest header moves to the internal
  `BordereauHeader`, `BordereauHeaderStatus`, and
  `CreateBordereauHeaderRequest` schemas on the `/internal/v1` routes. The
  public projection change is breaking, so the contract takes a major version.
- `asyncapi/contract.yaml` is 1.3.0: `contract.bordereau.received` becomes
  implemented and adds the `ContractBordereauData` payload schema;
  `contract.bordereau.processed` and `contract.bordereau.failed` are added as
  implemented child-aggregate channels and `send` operations, both naming
  `ContractEvents.java`. Aggregate version is 1 for received and 2 for a
  terminal fact; the outbox partition key stays the contract id. The SPEC
  `contract.bordereau.posted` and `.rejected` channels remain planned.
- `asyncapi/event-catalog.yaml` is 1.10.0: `contract.bordereau.processed` and
  `contract.bordereau.failed` are published, and `received`, `processed`, and
  `failed` join the Contract implemented subset (188 published in total;
  Contract 26 published and 11 implemented).
- `scripts/validate_contracts.py` requires the three public period-bordereau
  operations, the `TenantHeader` and `BookHeaderAssumed` parameters, the
  201/200, 400, 404, and 409 responses, the `Bordereau`, `BordereauStatus`,
  `CreateBordereauRequest`, and `UpdateBordereauStatusRequest` schemas with
  their field types and enums, and the three implemented bordereau events.
- `README.md` records the period-bordereau route, projection, create and status
  rules, technical-account linkage, book rule, events, and breaking 3.0.0
  classification; `MISMATCHES.md` adds M-30 for the status-vocabulary, event
  naming, absent-book, and line/exception gaps, and updates M-12, M-14, and
  M-22.
- `python scripts/validate_contracts.py` passes 10,593 checks with 0 failures.

### Added in the Direct Claims allocations contract (2026-10-20)

- `openapi/direct-claims.yaml` is 1.6.0: adds `GET/POST
  /api/v1/claims/{claimId}/allocations`, the `AllocationSummary` (`items`,
  `totalPct`, `totalAmount`), `Allocation` (`allocationId`, `claimId`,
  `policyId`, `policyYear`, `layer`, `allocationPct`, `allocatedAmount`,
  `createdAt`), and `CreateClaimAllocationRequest` (`policyId`; `policyYear`
  1900-2200; `layer` at most 32 characters; `allocationPct` greater than 0 and
  at most 1; `allocatedAmount` zero or greater) schemas, and the
  200/201/400/404/409 responses with 400 `POLICY_MISMATCH` and 409
  `ALLOCATION_EXCEEDS_100`. The implemented path is removed from
  `x-planned-operations`.
- `asyncapi/direct-claims.yaml` is 1.4.0: adds the implemented
  `direct.claim.allocation-created` channel and `send` operation, naming
  `ClaimEvents.java`. The SPEC `direct.claim.allocated` channel remains
  planned.
- `asyncapi/event-catalog.yaml` is 1.11.0: `direct.claim.allocation-created`
  is published and implemented (189 published in total; Direct Claims 26
  published and 12 implemented).
- `scripts/validate_contracts.py` requires the two public allocation
  operations, the `AllocationSummary`, `Allocation`, and
  `CreateClaimAllocationRequest` schemas and their field bounds, the
  `TenantHeader`/`BookHeaderDirect` parameters, the 200/201 successes, the 400
  `POLICY_MISMATCH` and 409 `ALLOCATION_EXCEEDS_100` documentation, the
  absence of the path from `x-planned-operations`, and the implemented event
  name.
- `README.md` records the routes, projection, field bounds, percentage guard,
  DIRECT book rule, event, and additive versions; `MISMATCHES.md` adds M-31 for
  the domain error-code remap, removes policy-year allocations from the Direct
  Claims resource gaps, and updates M-14 and M-22 with the event.
- `python scripts/validate_contracts.py` passes 10,738 checks with 0 failures.

### Added in the Policy premium receivables contract (2026-10-20)

- `openapi/policy.yaml` is 2.5.0: adds `GET /api/v1/billing/installments`, the
  cross-policy premium-receivables queue. The response is the bare
  `ReceivableSummary` (`items`, `totalAmount`, `overdueAmount`, `count`); each
  `Receivable` is `{installmentId, planId, planNumber, policyId, policyNumber,
  insuredPartyId, installmentNumber, dueDate, amount, currency, status,
  daysPastDue, paidAt, paymentId}`. The operation requires `X-EIA-Tenant`,
  accepts the optional `X-EIA-Book` fixed to DIRECT when present, filters by the
  DUE/OVERDUE `status` and the inclusive `dueBefore` cutoff, and documents the
  default-20 1..200 `limit` with its 400 `VALIDATION_ERROR`/
  `INVALID_INSTALLMENT_STATUS` and 404 `BOOK_SCOPE_VIOLATION` responses. The
  route is outside `/api/v1/policies` because it spans the tenant's policies;
  the per-policy billing routes are unchanged.
- `scripts/validate_contracts.py` requires the receivable path, the
  `TenantHeader`/`BookHeaderDirectOptional` parameters, the DUE/OVERDUE enum,
  the `dueBefore` date, the 1..200 limit, the 200 `ReceivableSummary`, the
  400/404 responses, and the `Receivable`/`ReceivableSummary` fields,
  nullability, money, currency, and count bounds; it also requires the operation
  description to note that the route is outside `/api/v1/policies`.
- `README.md` records the queue route, projection, filters, DIRECT book rule,
  ordering, and the additive 2.5.0 class; `MISMATCHES.md` extends M-27 with the
  implemented cross-policy receivable read and updates M-12.
- `python scripts/validate_contracts.py` passes 10,847 checks with 0 failures.

### Added in the Policy mass tort profile contract (2026-10-20)

- `openapi/policy.yaml` is 2.6.0: adds `GET/PUT
  /api/v1/policies/{policyId}/mass-tort-profile`, the `MassTortProfile`
  projection (`profileId`, `policyId`, `tortType`, `triggerType`,
  `allocationMethod`, `allocationNotes`, `coverageBlockStart`,
  `coverageBlockEnd`, `status`, `updatedAt`), the
  `UpdateMassTortProfileRequest` upsert body (`tortType`, `triggerType`,
  `allocationMethod`, and `status` required; notes and both block dates
  optional for DRAFT), and the `MassTortTortType`, `MassTortTriggerType`,
  `MassTortAllocationMethod`, and `MassTortProfileStatus` enums. GET documents
  200/400/404; PUT documents 200/201/400/404/409. Both operations require
  `X-EIA-Tenant` and constrain a supplied `X-EIA-Book` to DIRECT. The
  implemented path is removed from `x-planned-operations`. The canonical PUT
  keeps the 201 create response; the domain currently returns 200 for both
  outcomes, which M-32 records.
- `asyncapi/policy.yaml` is 1.4.0: `policy.mass-tort-profile.updated` becomes
  implemented and carries a `PolicyMassTortProfileUpdatedData` payload with the
  policy identity, profile status, tort, trigger, allocation method, and
  coverage-block dates.
- `asyncapi/event-catalog.yaml` is 1.12.0: `policy.mass-tort-profile.updated`
  joins the Policy `implemented` subset. The name was already in `published`,
  so the platform total stays 189 published names; Policy becomes 23 published
  and 11 implemented.
- `scripts/validate_contracts.py` requires the two mass tort operations, the
  tenant and optional DIRECT book parameters, the 200/201/400/404/409
  responses, the `MassTortProfile` and `UpdateMassTortProfileRequest` schemas
  and their field bounds, the four enum schemas, the event payload schema, the
  implemented channel/operation, and the new implemented event name. It also
  rejects the implemented route under `x-planned-operations`.
- `README.md` records the routes, projection, vocabulary, COMPLETE gate,
  DIRECT book rule, event, and additive versions; `MISMATCHES.md` adds M-32 for
  the SPEC route, trigger/status vocabulary, tort catalog, projection, and
  command-step differences, and updates M-06, M-07, M-12, M-13, and M-14.
- `python scripts/validate_contracts.py` passes 11,032 checks with 0 failures.

### Added in the Direct Claims list claimant filter contract (2026-10-20)

- `openapi/direct-claims.yaml` is 1.7.0: `GET /api/v1/claims` and
  `GET /internal/v1/claims` document the optional `claimantPartyId` UUID query
  parameter alongside the existing optional `status` filter. The public
  operation documents the required `X-EIA-Tenant` and `X-EIA-Book: DIRECT`
  headers, the 404 `BOOK_SCOPE_VIOLATION` book wall, the bare `Claim[]`
  response, the newest-first order, and the exact-match semantics (an unknown
  party yields an empty array, not a 404). The expert operation documents the
  `tenantId` query scope and the same two independent filters. The change is
  additive: no path, request body field, response body field, or event changed.
- `scripts/validate_contracts.py` requires the `claimantPartyId` inline query
  parameter on both list operations, its optional `string`/`uuid` schema, the
  retained shared `DirectClaimStatusFilter`, the tenant and
  `BookHeaderDirect` parameters, the `DIRECT` scope in the operation
  description, and the bare `Claim` array 200 schema.
- `README.md` records the filter semantics, the AND combination, the
  exact-match/no-Party-lookup caveat, and the 1.7.0 additive classification;
  `MISMATCHES.md` adds M-33 for the exact-match filter and no party reference
  check, and updates the validation evidence.
- `python scripts/validate_contracts.py` passes 11,054 checks with 0 failures.

### Added in the Contract cash-call contract (2026-10-20)

- `openapi/contract.yaml` is 3.1.0: adds `GET/POST
  /api/v1/contracts/{contractId}/cash-calls` and `PATCH
  /api/v1/contracts/{contractId}/cash-calls/{cashCallId}/status`, the `CashCall`
  projection (`cashCallId`, `callNumber`, `contractId`, `periodStart`,
  `periodEnd`, `amount`, `currency`, `dueDate`, `status`, `notes`,
  `createdAt`), the `CashCallStatus` enum (`REQUESTED`, `ISSUED`, `SETTLED`,
  `CANCELLED`), the `CreateCashCallRequest` body (`periodStart`, `periodEnd`,
  `amount`, `currency`, and `dueDate` required; optional nullable
  4000-character `notes`), and `UpdateCashCallStatusRequest` (`status` is
  `ISSUED`, `SETTLED`, or `CANCELLED`). GET documents 200/400/404; POST
  documents 201/400/404/409 `DUPLICATE_CASH_CALL_NUMBER`; PATCH documents
  200/400/404/409 `INVALID_STATUS_TRANSITION`. Both mutations require
  `X-EIA-Tenant` and `X-EIA-Book: ASSUMED`. The change is additive.
- `asyncapi/contract.yaml` is 1.4.0: `contract.cash-call.requested`, `.issued`,
  `.settled`, and `.cancelled` become implemented child-aggregate channels with
  `send` operations and the `ContractCashCallData` payload schema; the envelope
  uses the cash-call id and aggregate version 1 (requested), 2 (issued or
  cancelled), or 3 (settled) while the outbox partition key stays the contract
  id. `.issued` moves from planned to implemented.
- `asyncapi/event-catalog.yaml` is 1.13.0: `contract.cash-call.requested`,
  `.settled`, and `.cancelled` are published, and all four cash-call names join
  the Contract implemented subset (192 published in total; Contract 29
  published and 15 implemented).
- `scripts/validate_contracts.py` requires the three public cash-call
  operations, the `TenantHeader` and `BookHeaderAssumed` parameters, the
  201/200/400/404/409 responses, the `CashCall`, `CashCallStatus`,
  `CreateCashCallRequest`, and `UpdateCashCallStatusRequest` schemas and their
  field types, the notes nullability and 4000-character cap, the
  ISSUED/SETTLED/CANCELLED request enum, the four implemented channels and
  `send` operations, the `ContractCashCallData` payload fields, and the four
  implemented event names.
- `README.md` records the routes, projection, create and status rules, ASSUMED
  book rule, event semantics, and additive versions; `MISMATCHES.md` adds M-34
  for the SPEC route/event and cash-limit gaps and updates the validation
  evidence.
- `python scripts/validate_contracts.py` passes 11,292 checks with 0 failures.

### Added in the Payment allocations contract (2026-10-20)

- `openapi/payment.yaml` is 1.4.0: adds `GET/POST
  /api/v1/payments/{paymentId}/allocations`, the
  `PaymentAllocationSummary` (`items`, `paymentAmount`, `totalAllocated`,
  `unallocated`, `currency`), `PaymentAllocation` (`allocationId`, `paymentId`,
  `targetType`, `targetId`, `component`, `amount`, `currency`, `createdAt`),
  and `CreatePaymentAllocationRequest` (`targetType` DIRECT_CLAIM,
  ASSUMED_CLAIM, or POLICY; `targetId` UUID; `component` INDEMNITY,
  DEFENSE_COST, ALAE, EXPENSE, COMMISSION, or OTHER; `amount` greater than zero
  with at most four fraction digits) schemas, and the
  `PaymentAllocationTargetType` and `PaymentAllocationComponent` enums. GET
  documents 200/400/404; POST documents 201/400/404/409 with the stable
  `ALLOCATION_EXCEEDS_PAYMENT` and `PAYMENT_NOT_ALLOCATABLE` codes. Both
  operations require `X-EIA-Tenant`, are not book-scoped, and the implemented
  path is removed from `x-planned-operations`. The change is additive.
- `asyncapi/payment.yaml` is 1.3.0: adds the implemented
  `payment.allocation.created` channel, `send` operation, and a
  `PaymentAllocationCreatedData` payload with the parent payment identity, the
  target and component enums, the amount and currency, and the payment-level
  `totalAllocated`/`paymentAmount` totals. The envelope uses the allocation id
  as the `PaymentAllocation` aggregate at version 1.
- `asyncapi/event-catalog.yaml` is 1.14.0: `payment.allocation.created` is
  published and implemented (193 published in total; Payment 19 published and
  4 implemented). The name is a new child-aggregate fact with no SPEC 11.7.10
  equivalent.
- `scripts/validate_contracts.py` requires the two public allocation
  operations, the `TenantHeader` parameter, the 200/201 successes, the
  400/404/409 responses, the `PaymentAllocation`, `PaymentAllocationSummary`,
  and `CreatePaymentAllocationRequest` schemas with their field bounds and
  enums, the `ALLOCATION_EXCEEDS_PAYMENT`/`PAYMENT_NOT_ALLOCATABLE`
  documentation, the absence of the implemented path from
  `x-planned-operations`, and the implemented `payment.allocation.created`
  channel, payload, and implemented-event list entry.
- `README.md` records the routes, projection, target and component vocabularies,
  amount and currency rules, status and overallocation guards, tenant wall,
  event, and additive versions; `MISMATCHES.md` adds M-35 for the new POST route
  and event name and updates the validation evidence.
- `python scripts/validate_contracts.py` passes 11,477 checks with 0 failures.

### Added in the Direct Claims allocation erosion contract (2026-10-20)

- `openapi/direct-claims.yaml` is 1.8.0: `Allocation` gains the nullable
  `limitId`, `erosionMessage`, and `erosionPostedAt` fields and the required
  `erosionStatus` enum (`NOT_POSTED`, `POSTED`, `FAILED`);
  `CreateClaimAllocationRequest` gains the optional `limitId` UUID; and
  `POST /api/v1/claims/{claimId}/allocations/{allocationId}/erosion` is a
  bodyless orchestration retry. It loads the allocation, requires the stored
  `limitId`, reposts the limit to the Policy domain, and records the resulting
  `POSTED` or `FAILED` state. The operation requires `X-EIA-Tenant` and
  `X-EIA-Book: DIRECT`, returns 200 `Allocation`, and documents 400
  `VALIDATION_ERROR` for a missing stored limit, 404, and 409 `CONFLICT` when
  the retry would change an already-`POSTED` allocation. A Policy rejection or
  outage is recorded as `FAILED` and still returns 200. A create that supplies
  `limitId` also attempts the posting and returns `POSTED` or `FAILED`; a
  create without a limit stays `NOT_POSTED`. Adds the `AllocationErosionStatus`
  enum. No public `AllocationErosionRequest` schema and no public request body;
  the retry writes no event.
- `scripts/validate_contracts.py` requires the four erosion projection fields
  and the required status, the nullable field shapes, the optional create
  `limitId`, the `AllocationErosionStatus` enum, the bodyless erosion retry
  with its tenant and DIRECT book parameters, the 200 `Allocation`, the
  400/404/409 responses, the 400 stored-limit and `VALIDATION_ERROR`
  documentation, the 409 `CONFLICT` documentation, the rejection of a public
  `AllocationErosionRequest` schema, and the absence of the path from
  `x-planned-operations`.
- `README.md` records the erosion fields, bodyless retry, state rules, and
  additive 1.8.0 classification; `MISMATCHES.md` updates M-36 for the public
  domain swallowing the expert 409 and the record-write failure, and updates the
  validation evidence.
- `python scripts/validate_contracts.py` passes 11,527 checks with 0 failures.

### Added in the Contract security/collateral contract (2026-10-20)

- `openapi/contract.yaml` is 4.0.0: the public
  `GET/POST /api/v1/contracts/{contractId}/security` operations now use the
  ten-field `SecurityRecord` projection (`id`, `securityType`,
  `requiredAmount`, `heldAmount`, `currency`, `providerPartyId`, `expiryDate`,
  `approvalRef`, `status`, `createdAt`) and the `CreateContractSecurityRequest`
  body (`securityType`, `requiredAmount`, `currency` required; `heldAmount`,
  `providerPartyId`, `expiryDate`, `approvalRef`, and `approvedAt` optional).
  Both operations require `X-EIA-Tenant` and `X-EIA-Book: ASSUMED`, document
  400/404, and the POST documents 409. The create derives `ACTIVE` or
  `EXPIRED`, defaults `heldAmount` to `0.0000`, requires the contract currency,
  and documents `COLLATERAL_EXCEEDS_OBLIGATION`,
  `COLLATERAL_APPROVAL_INCOMPLETE`, `SECURITY_CURRENCY_MISMATCH`, and
  `CONTRACT_LOCKED`. The response status enum carries `ACTIVE` plus the
  implemented bind-slice vocabulary, including `OUTSTANDING`, because the list
  can return internal-expert rows. The wide `Security` and
  `CreateSecurityRequest` schemas remain on the internal expert surface. The
  public projection/request correction is breaking for a generated client of
  the old public shape.
- `asyncapi/contract.yaml` is 1.5.0: `contract.security.recorded` becomes an
  implemented channel and `send` operation with a `ContractSecurityData` payload
  (`contractId`, `securityId`, `securityType`, `requiredAmount`, `heldAmount`,
  `currency`, `status`). The event is a child aggregate keyed by the security
  id at aggregate version 1 while the outbox partition key stays the contract
  id.
- `asyncapi/event-catalog.yaml` is 1.15.0: `contract.security.recorded` joins
  the Contract implemented subset. It was already published, so the platform
  total stays 193 published names; Contract becomes 29 published and 16
  implemented, and the platform implemented total becomes 72.
- `scripts/validate_contracts.py` requires the two public security operations
  with the shared tenant and ASSUMED book parameters, the `SecurityRecord` and
  its ten required fields, the `CreateContractSecurityRequest`
  required/optional split with no caller `status`, the `SecurityStatus` enum
  including `ACTIVE` and `OUTSTANDING`, the 201/200 successes and 400/404/409
  responses, the four documented conflict codes, the implemented
  `contract.security.recorded` channel and `ContractSecurityData` payload, and
  the event's place in the catalog implemented list.
- `README.md` records the routes, projection, request rules, derived and legacy
  status values, book rule, event, versions, and validator coverage;
  `MISMATCHES.md` adds M-37 for the narrow projection, derived `ACTIVE` status
  outside the SPEC enum, the legacy `OUTSTANDING` vocabulary, the absent-book
  acceptance, and the release/status gaps, and updates M-14 with the event.
- `python scripts/validate_contracts.py` passes 11,646 checks with 0 failures.

### Added in the Policy installment dunning contract (2026-10-20)

- `openapi/policy.yaml` is 2.7.0: adds `GET/POST
  /api/v1/billing/installments/{installmentId}/dunning`, the `DunningAction`
  projection (`dunningId`, `installmentId`, `planId`, `policyId`, `level`,
  `channel`, `notes`, `status`, `sentAt`) and the `CreateDunningRequest` command
  (`level` and `channel` required and closed to
  `REMINDER`/`FIRST_NOTICE`/`SECOND_NOTICE`/`COLLECTIONS` and
  `EMAIL`/`LETTER`/`PORTAL`; optional 2000-character `notes`). Both operations
  require `X-EIA-Tenant` and `X-EIA-Book: DIRECT`; GET returns the bare
  `DunningAction[]` newest first and documents 400/404, while POST documents
  201/400/404/409 with the `INSTALLMENT_NOT_DUNNABLE` and
  `DUNNING_ALREADY_SENT` conflict codes. The nullable
  `Receivable.lastDunningLevel` and `Receivable.lastDunningAt` members summarize
  the latest SENT action and stay null until the installment is first dunned.
- `asyncapi/policy.yaml` is 1.5.0: adds the implemented `policy.dunning.sent`
  channel and `send` operation with a `PolicyDunningSentData` payload
  (`policyId`, `policyNumber`, `installmentId`, `level`, `channel`, `sentAt`,
  `status`).
- `asyncapi/event-catalog.yaml` is 1.16.0: `policy.dunning.sent` is published
  and implemented (194 published in total; Policy becomes 24 published and 12
  implemented, and the platform implemented total becomes 73).
- `scripts/validate_contracts.py` requires the dunning GET/POST, the
  `TenantHeader`/`BookHeaderDirect` parameters, the required uuid
  `installmentId`, the `DunningAction` and `CreateDunningRequest` schemas and
  their field types, enums, notes cap, and required/optional split, the 200
  `DunningAction[]`, the 201 `DunningAction`, the 400/404/409 responses, the
  `INSTALLMENT_NOT_DUNNABLE`/`DUNNING_ALREADY_SENT` documentation, the nullable
  receivable dunning members, and the implemented event channel, payload, and
  catalog entries.
- `README.md` records the dunning routes, projection, vocabularies, state and
  uniqueness rules, DIRECT book rule, event, receivable members, and the
  additive versions; `MISMATCHES.md` adds M-38 for the SPEC 11.2.13 route,
  level-vocabulary, book, and event-name differences and updates M-12, M-14,
  M-22, and M-27.
- `python scripts/validate_contracts.py` passes 11,808 checks with 0 failures.

### Added in the Direct Claims mass-tort allocation guard contract (2026-10-20)

- `openapi/direct-claims.yaml` is 1.9.0: `POST
  /api/v1/claims/{claimId}/allocations` documents the policy mass-tort
  coverage-block guard. When the policy's mass-tort profile is COMPLETE and
  carries both `coverageBlockStart` and `coverageBlockEnd`, `policyYear` must
  fall within the inclusive start/end years; a year outside the block is 400
  `MASS_TORT_YEAR_OUTSIDE_BLOCK`, in addition to the existing 400
  `POLICY_MISMATCH` and `VALIDATION_ERROR`, and writes nothing. A DRAFT
  profile, a policy without a profile, and an unavailable or unreadable Policy
  profile all allow the allocation, so the profile read is not an availability
  dependency. The operation description, the 400 description, the
  `CreateClaimAllocationRequest` schema, and its `policyYear` member document
  the rule; the guard runs on the public create only and the expert allocation
  write is unchanged. The change is additive.
- `scripts/validate_contracts.py` requires `MASS_TORT_YEAR_OUTSIDE_BLOCK` in
  the allocation create 400 description alongside `POLICY_MISMATCH`.
- `README.md` records the guard semantics, the fail-open allow-list, the
  SPEC 11.4.7 `DIR-15`/11.2.7 `POL-14` rationale, and the 1.9.0 additive
  classification, and adds the code to the validator and known-deviation
  coverage; `MISMATCHES.md` updates M-31 with the third public 400 code and
  M-32 with the profile consumer, and updates the validation evidence.
- `python scripts/validate_contracts.py` passes 11,809 checks with 0 failures.

### Added in the Policy program catalog contract (2026-10-20)

- `openapi/policy.yaml` is 2.8.0: adds `GET/POST /api/v1/programs`,
  `GET /api/v1/programs/{programId}`, and
  `PATCH /api/v1/policies/{policyId}/program`, the flat `Program` projection
  (`programId`, `programNumber`, `name`, `programType`, inclusive
  `effectiveFrom`/`effectiveTo`, `status`, nullable `leadPolicyId`, and
  `createdAt`), the closed `ProgramType` (`CAPTIVE`, `POOL`, `FRONTING`,
  `COINSURANCE`, `MASS_TORT`) and `ProgramStatus` (`ACTIVE`, `CLOSED`) enums,
  the `CreateProgramRequest` body (`name`, `programType`, both dates required,
  optional `leadPolicyId`), and the `UpdatePolicyProgramRequest` body with a
  required nullable `programId`. Adds the nullable, optional
  `Policy.programId`. All four operations require `X-EIA-Tenant` and
  `X-EIA-Book: DIRECT` and document the 400 `MISSING_TENANT_HEADER`/
  `INVALID_TENANT_HEADER`/`VALIDATION_ERROR`/`INVALID_PROGRAM_*` codes, 404
  `PROGRAM_NOT_FOUND`/`POLICY_NOT_FOUND`/`BOOK_SCOPE_VIOLATION`, and the
  assignment 409 `CONCURRENT_MODIFICATION`; POST returns 201 with `Location`,
  the reads and PATCH return 200, and PATCH returns the shared `ETag`. The
  implemented `/api/v1/programs` entry leaves `x-planned-operations`.
- `asyncapi/policy.yaml` is 1.6.0: adds the implemented
  `policy.program.created` and `policy.policy.program-assigned` channels and
  `send` operations with the `PolicyProgramCreatedData` and
  `PolicyPolicyProgramAssignedData` payloads. The program event is keyed by the
  program aggregate at version 1; the assignment event is keyed by the policy
  aggregate and carries both sides of the nullable link plus
  `changedFields: ["programId"]`.
- `asyncapi/event-catalog.yaml` is 1.17.0: both program names are published and
  implemented (196 published in total; Policy becomes 26 published and 14
  implemented, and the platform implemented total becomes 75).
- `scripts/validate_contracts.py` requires the four public paths, the five
  schemas, the nullable and optional `Policy.programId`, the shared tenant and
  DIRECT book parameters, the 201/200/400/404/409 responses, the 201 `Location`
  and 200 `ETag` headers, the documented validation, not-found, and concurrency
  codes and event names, both implemented channels with their payload fields
  and enums, the two catalog entries, and the absence of an implemented program
  path from `x-planned-operations`.
- `README.md` records the routes, projection, validation and membership rules,
  the book and tenant scope, both events, the additive versions, and the
  validator coverage; `MISMATCHES.md` adds M-39 for the SPEC 10.11.3/11.2.10
  route, vocabulary, field, and command gaps, the unresolved `leadPolicyId`,
  and the absent-book acceptance, and updates M-01, M-14, and M-22.
- `python scripts/validate_contracts.py` passes 12,109 checks with 0 failures.

### Added in the document content contract (2026-10-20)

- `openapi/document.yaml` is 1.3.0: adds `PUT|GET
  /api/v1/documents/{documentId}/content` and `GET
  /api/v1/documents/{documentId}/content/metadata`, the `DocumentContent`
  projection (`documentId`, `fileName`, `contentType`, `sizeBytes`, `sha256`,
  `uploadedAt`), and the raw-byte upload and download representations. The
  upload documents the `Content-Type` header (optional, default
  `application/octet-stream`) and the required URL-encoded `X-File-Name`
  header, the 200 `DocumentContent` response, 400 `EMPTY_CONTENT` and the
  filename/content-type rule codes, 404, and 413 `FILE_TOO_LARGE` above
  10 MiB. The download documents the binary response and the `Content-Type`,
  `Content-Disposition`, and `X-Content-SHA256` headers. All three operations
  require the shared `TenantHeader`; the implemented content path leaves
  `x-planned-operations`. The change is additive.
- `asyncapi/document.yaml` is 1.3.0: adds the implemented
  `document.content.uploaded` channel and `send` operation with a
  `DocumentContentUploadedData` payload (document identity and number,
  filename, MIME type, size, and SHA-256). The event is keyed by the
  `DocumentContent` aggregate on the document id with the content version, and
  names `DocumentContentEvents.java` in `x-implemented-by`.
- `asyncapi/event-catalog.yaml` is 1.18.0: `document.content.uploaded` is
  published and implemented (197 published in total; Document becomes 21
  published and 6 implemented, and the platform implemented total becomes 76).
  The name is new and has no SPEC 11.6.9 equivalent.
- `scripts/validate_contracts.py` requires the three content operations, the
  shared tenant and `documentId` parameters, the `Content-Type` and
  `X-File-Name` upload headers, the binary request and response bodies, the
  `Content-Disposition` and `X-Content-SHA256` download headers, the
  `DocumentContent` fields and bounds, the 400 `EMPTY_CONTENT` and 413
  `FILE_TOO_LARGE` documentation, the implemented content channel and payload,
  the catalog entry, and the absence of the implemented path from
  `x-planned-operations`. The raw request-body rule is now explicit: an
  operation marked `x-raw-body: true` must declare a binary string body.
- `README.md` records the routes, metadata projection, upload and download
  headers, 10 MiB and empty-body rules, tenant wall, event, and additive
  versions; `MISMATCHES.md` adds M-40 for the SPEC download, content-fact, and
  lifecycle gaps, and updates M-14, M-22, and the validation evidence.
- `python scripts/validate_contracts.py` passes 12,255 checks with 0 failures.

### Added in the contract security status action (2026-10-20)

- `openapi/contract.yaml` is 4.1.0: adds
  `PATCH /api/v1/contracts/{contractId}/security/{securityId}/status` and the
  `UpdateContractSecurityStatusRequest` schema (`status` is `RELEASED` or
  `EXPIRED`). The action moves a record in `ACTIVE`, `OUTSTANDING`, `PARTIAL`,
  or `REQUIRED` to `RELEASED` or `EXPIRED` and an `EXPIRED` record to
  `RELEASED`; `RELEASED` is terminal and `BREACH` is rejected. A target outside
  the two outcomes is 400 `INVALID_STATUS`, an illegal, repeated, or terminal
  edge is 409 `INVALID_STATUS_TRANSITION`, and an unknown or foreign record is
  404. The 200 body is the ten-field `SecurityRecord`. The route requires the
  shared tenant and ASSUMED book parameters, and its description records that
  the action is available in every contract lifecycle state. The change is
  additive.
- `asyncapi/contract.yaml` is 1.6.0: adds the implemented
  `contract.security.status-changed` channel and `send` operation with a
  `ContractSecurityStatusChangedData` payload (`contractId`, `securityId`,
  `securityType`, `previousStatus`, `status`). The event is a child aggregate
  at aggregate version 2, or 3 for the release of an expired record, while the
  outbox partition key stays the contract id; the name is new and has no SPEC
  11.3.9 equivalent.
- `asyncapi/event-catalog.yaml` is 1.19.0: `contract.security.status-changed`
  is published and implemented (198 published in total; Contract becomes 30
  published and 17 implemented, and the platform implemented total becomes 77).
- `scripts/validate_contracts.py` requires the status path, the tenant and
  ASSUMED book parameters, both path parameters, the required
  `UpdateContractSecurityStatusRequest` with exactly the two-value enum, the
  200 `SecurityRecord` and 400/404/409 responses, the transition, terminal, and
  `BREACH` documentation, the implemented channel and `send` operation, the
  payload fields and status enums, and the catalog entry.
- `README.md` records the route, transitions, error codes, event, and additive
  versions; `MISMATCHES.md` updates M-37 and M-22 for the added action, event
  name, and remaining gaps.
- `python scripts/validate_contracts.py` passes 12,333 checks with 0 failures.

### Added in the Policy credit-note contract (2026-10-20)

- `openapi/policy.yaml` is 2.9.0: adds `GET/POST
  /api/v1/policies/{policyId}/credit-notes` and `PATCH
  /api/v1/policies/{policyId}/credit-notes/{creditNoteId}/status`, the
  ten-field `CreditNote` projection (`creditNoteId`, `noteNumber`, `policyId`,
  `amount`, `currency`, `reason`, `status`, `issuedAt`, `appliedAt`,
  `createdAt`), the `CreditNoteStatus` enum
  (`DRAFT`/`ISSUED`/`APPLIED`/`CANCELLED`), `CreateCreditNoteRequest` (positive
  amount, policy currency, optional 500-character reason), and
  `UpdateCreditNoteStatusRequest` (`ISSUED`/`APPLIED`/`CANCELLED`). Both
  operations require the shared `TenantHeader` and `BookHeaderDirect`; the list
  returns 200, the create returns 201, and the status action returns 200, with
  400/404 on every operation and 409 on both mutations. The descriptions record
  the DRAFT -> ISSUED -> APPLIED graph, CANCELLED from DRAFT or ISSUED, the
  terminal APPLIED/CANCELLED states, and the `policy.credit-note.*` events. The
  change is additive.
- `asyncapi/policy.yaml` is 1.7.0: adds the implemented
  `policy.credit-note.issued`, `policy.credit-note.applied`, and
  `policy.credit-note.cancelled` channels and `send` operations with a shared
  `PolicyCreditNoteData` payload (policy and note identity, note number, amount,
  currency, and status).
- `asyncapi/event-catalog.yaml` is 1.20.0: all three names are published and
  implemented (201 published and 80 implemented in total; Policy becomes 29
  published and 17 implemented).
- `scripts/validate_contracts.py` requires the two paths, the three operations,
  the shared tenant and DIRECT book parameters, the ten-field `CreditNote`
  schema and its status enum, the positive amount pattern and 500-character
  reason cap, the three-value status request enum, the 201/200/400/404/409
  responses, the documented transition and event rules, the three implemented
  channels, the shared payload fields, and the catalog entries; the implemented
  routes must not reappear under `x-planned-operations`.
- `README.md` records the routes, lifecycle, book rule, events, and additive
  versions; `MISMATCHES.md` adds M-41 for the SPEC route, lifecycle, reason
  vocabulary, approval/SAP, and event-name gaps, and updates M-12, M-22, M-27,
  and the validation evidence.
- `python scripts/validate_contracts.py` passes 12,561 checks with 0 failures.

### Added in the Document content version contract (2026-10-21)

- `openapi/document.yaml` is 1.4.0: adds
  `GET /api/v1/documents/{documentId}/content/versions` (bare
  `DocumentContentVersion[]`, newest first) and
  `GET /api/v1/documents/{documentId}/content/versions/{version}` (binary
  revision download), the seven-field `DocumentContentVersion` schema, the
  required `DocumentContent.currentVersion` member, and the `X-Content-Version`
  header on both content downloads. Every upload now appends an immutable
  revision and advances the current pointer. The two SPEC 11.6.10 `/versions`
  entries are removed from `x-planned-operations` because the history is
  implemented (nested under `/content/versions`) and the upload is the
  version-creating command. The change is additive.
- `asyncapi/document.yaml` is 1.4.0: the implemented
  `document.content.uploaded` payload gains the required `version` member (the
  content revision and aggregate version). No channel or event name is added,
  and `eventVersion` stays 1.
- `asyncapi/event-catalog.yaml` is 1.21.0: no published or implemented name is
  added or removed, so the totals stay 201 published and 80 implemented
  (Document 21 published and 6 implemented); the description records the
  payload-only change.
- `scripts/validate_contracts.py` requires the two version operations, the
  tenant header and `documentId` parameter, the required positive `version`
  path parameter, the `DocumentContentVersion` array and schema fields, the
  four binary download headers, the `CONTENT_VERSION_NOT_FOUND` and
  `INVALID_PARAMETER` documentation, the required `DocumentContent.currentVersion`,
  the required payload `version`, and the absence of the implemented version
  paths from `x-planned-operations`; it also asserts that
  `document.content.uploaded` remains the only `document.content.*` event.
- `README.md` records the two routes, the revision rules, the response shapes,
  the headers, the error codes, the event-payload change, the additive versions,
  and the validation count; `MISMATCHES.md` updates M-40 for the implemented
  revision history, the `/content/versions` path, the payload `version`, and the
  remaining SPEC gaps, and refreshes the validation evidence.
- `python scripts/validate_contracts.py` passes 12,657 checks with 0 failures.

### Added in the contract technical-account lines contract (2026-10-21)

- `openapi/contract.yaml` is 4.2.0: adds `GET/POST
  /api/v1/contracts/{contractId}/technical-accounts/{accountId}/lines` and
  `DELETE .../lines/{lineId}`, the `TechnicalAccountLine` projection
  (`lineId`, `accountId`, `lineType`, `reference`, `description`, `amount`,
  `createdAt`), the `TechnicalAccountLineType` enum (`PREMIUM`, `LOSS`,
  `COMMISSION`, `OTHER`), the `LineSummary` read model (`items` plus
  `totals` for premium, loss, commission, and other), the
  `TechnicalAccountLineTotals` schema, and the
  `CreateTechnicalAccountLineRequest` body. The list returns 200, the create
  201, and the delete 204, with 400/404 on every operation and 409
  `ACCOUNT_NOT_EDITABLE` on both mutations. The account status PATCH now
  documents the issue-time reconciliation: when at least one line exists, each
  line-type total must equal its matching header component, otherwise the
  transition is 409 `ACCOUNT_LINES_DO_NOT_RECONCILE` with one `details[]`
  entry per offending type. The change is additive; the reconciliation only
  rejects an issue that has line detail.
- `asyncapi/contract.yaml` is 1.7.0: adds the implemented
  `contract.technical-account.line-added` and `.line-removed` grandchild
  channels and `send` operations with a shared
  `ContractTechnicalAccountLineData` payload (`contractId`, `accountId`,
  `lineId`, `lineType`, `amount`). Each event uses the line id and aggregate
  version 1 while the outbox partition key stays the contract id; both are
  emitted only while the account is DRAFT and have no SPEC 11.3.9 equivalent.
- `asyncapi/event-catalog.yaml` is 1.22.0: both line names are published and
  implemented (203 published in total; Contract becomes 32 published and 19
  implemented, and the platform implemented total becomes 82).
- `scripts/validate_contracts.py` requires the two line paths and their
  GET/POST/DELETE operations, the tenant and ASSUMED book parameters, the
  contract/account/line path parameters, the `TechnicalAccountLine`,
  `TechnicalAccountLineType`, `LineSummary`, `TechnicalAccountLineTotals`, and
  `CreateTechnicalAccountLineRequest` schemas and their field bounds, the
  200/201/204 successes, the 400/404/409 responses with
  `ACCOUNT_NOT_EDITABLE`, the issue-time `ACCOUNT_LINES_DO_NOT_RECONCILE`
  documentation on the status PATCH, the absence of the implemented paths from
  `x-planned-operations`, the two implemented channels and `send` operations,
  the shared payload fields and enums, and the two catalog entries.
- `README.md` records the routes, the `LineSummary` and line projections, the
  DRAFT-only edit guard, the issue-time reconciliation rule, the book rule, the
  two events, the additive versions, and the remaining line-vocabulary gaps;
  `MISMATCHES.md` updates M-29 and adds M-42 for the reduced line types and
  the other SPEC `technical_account_line` gaps, and refreshes the validation
  evidence.
- `python scripts/validate_contracts.py` passes 12,857 checks with 0 failures.

### Added in the Policy legal entity contract (2026-10-21)

- `openapi/policy.yaml` is 2.10.0: adds `GET/POST /api/v1/legal-entities`,
  `GET /api/v1/legal-entities/{legalEntityId}`, and
  `PATCH /api/v1/policies/{policyId}/legal-entity`; the `LegalEntity`
  projection (`legalEntityId`, `code`, `name`, `entityType`, `jurisdiction`,
  `regulator`, `licenseNumber`, `status`, `createdAt`), the
  `LegalEntityType` enum (`INSURER`, `MGA`, `CAPTIVE`, `POOL`, `FRONTER`), the
  `LegalEntityStatus` enum (`ACTIVE`, `INACTIVE`), the
  `CreateLegalEntityRequest` create body, the
  `UpdatePolicyLegalEntityRequest` nullable assignment body, and the nullable
  `Policy.legalEntityId`. The list and detail return 200, the create returns
  201 with `Location`, and the assignment returns 200 with the updated `Policy`
  and the shared `ETag`. Every operation requires `X-EIA-Tenant` and accepts an
  optional `X-EIA-Book` that must be DIRECT when present; the catalog reads
  document 400/404, the create documents 400/404/409, and the assignment
  documents 400/404/409. The change is additive: three new paths, four new
  operations, five new schemas, one nullable `Policy` property, and no changed
  existing path, request field, response field, or event.
- `asyncapi/policy.yaml` is 1.8.0: adds the implemented
  `policy.legal-entity.created` and `policy.policy.legal-entity-assigned`
  channels and `send` operations with the `PolicyLegalEntityCreatedData` and
  `PolicyPolicyLegalEntityAssignedData` payloads. The created fact is keyed by
  the `LegalEntity` aggregate at version 1; the assignment fact is keyed by the
  `Policy` aggregate at the new version and carries the nullable new and
  previous entity ids plus `changedFields: ["legalEntityId"]`. Both names are
  new and have no SPEC 11.2.9 equivalent (M-22, M-43).
- `asyncapi/event-catalog.yaml` is 1.23.0: both names are published and
  implemented (205 published and 84 implemented in total; Policy becomes 31
  published and 19 implemented).
- `scripts/validate_contracts.py` requires the three paths and four operations,
  the required tenant and optional DIRECT book parameters, the
  `legalEntityId`/`policyId` path parameters, the `LegalEntity`,
  `LegalEntityType`, `LegalEntityStatus`, `CreateLegalEntityRequest`, and
  `UpdatePolicyLegalEntityRequest` schemas with their field bounds, nullability,
  and enums, the nullable optional `Policy.legalEntityId`, the 201 `Location`,
  the assignment 200 `ETag`, the 201/200/400/404/409 responses, the absence of
  the implemented paths from `x-planned-operations`, the two implemented
  channels and payloads, and the two catalog entries.
- `README.md` records the routes, projection, create and assignment semantics,
  the DIRECT book rule, the two events, the additive versions, and the
  validation count; `MISMATCHES.md` adds M-43 for the narrow catalog, the
  nullable assignment against LE-01, the path and vocabulary differences, and
  the two new event names, and updates M-01, M-12, M-13, M-14, and M-22.
- `python scripts/validate_contracts.py` passes 13,143 checks with 0 failures.

### Notes

- No runtime dependency, CI workflow, Maven build, or hosted pipeline was
  added. Validation is local and deterministic.
