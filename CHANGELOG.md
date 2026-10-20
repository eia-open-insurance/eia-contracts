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

### Notes

- No runtime dependency, CI workflow, Maven build, or hosted pipeline was
  added. Validation is local and deterministic.
