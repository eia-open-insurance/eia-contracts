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

### Notes

- No runtime dependency, CI workflow, Maven build, or hosted pipeline was
  added. Validation is local and deterministic.
