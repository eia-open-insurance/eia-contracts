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

### Notes

- No runtime dependency, CI workflow, Maven build, or hosted pipeline was
  added. Validation is local and deterministic.
