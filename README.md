# eia-contracts

Canonical API, event, and schema contracts for **EIA Open Insurance**.

- GitHub organization: `eia-open-insurance`
- Repository type: contracts (not deployable)
- Owner: Architecture
- Runtime: YAML 1.2 documents and JSON Schema 2020-12; no runtime dependencies
- Depends on: none

## Purpose

This repository is the contract-first source of truth for the platform:

- **OpenAPI 3.1** per vertical, one document covering both the public domain
  API and the internal expert API of that vertical.
- **AsyncAPI 3** for the event catalog and for the events published by each
  vertical.
- **JSON Schema 2020-12** for the common types shared by HTTP and events.
- A **standard-library validation script** that every contributor and release
  engineer runs locally before merge.

The normative requirements live in `../../SPEC.md`, chiefly sections 3.6 (book
wall), 6.11 (errors), 7.5 (eventing), 7.6 (API conventions), 7.18-7.23
(reinsurance administration and the integration standard), 10.3 (money),
11.1-11.10 (verticals), 12 (canonical contracts), and 16.9 (repository
standard).

## Layout

| Path | Contents |
|---|---|
| `openapi/components.yaml` | Shared parameters, headers, responses, and schemas: canonical `Problem` error envelope, money, offset page envelope, global-search envelope, ETag/If-Match, Idempotency-Key (Policy and the claim task/note creates), the optional `X-EIA-Actor` header, audit fields, entity references, tenant and book headers, including the optional Policy billing `X-EIA-Book`. |
| `openapi/party.yaml` … `openapi/notifications.yaml` | One OpenAPI 3.1 document per vertical. Ten documents, each covering `/api/v1/**` and `/internal/v1/**`. |
| `asyncapi/event-catalog.yaml` | Authoritative catalog of the published event names, their publisher, and the subscribers named in SPEC 11. |
| `asyncapi/{vertical}.yaml` | Published event channels for one vertical. One channel and one `send` operation per event name. |
| `schemas/error-envelope.schema.json` | Canonical RFC 9457 error envelope (`Problem`) with the EIA extension members. |
| `schemas/money.schema.json` | Canonical `Money`, `MoneyAmount`, and `CurrencyCode` definitions. |
| `schemas/event-envelope.schema.json` | Canonical event envelope from SPEC 7.5.4 and 12.4. |
| `scripts/validate_contracts.py` | Contract validation. Python standard library only. |
| `MISMATCHES.md` | Contract-to-implementation audit: every known difference between these documents and the running services. |

The per-vertical file names use the repository vertical identifiers
(`direct-claims`, `assumed-claims`). Event names and `EntityRef.vertical` use
the shorter identifiers `direct` and `assumed` that SPEC 11 and 12 use.

SPEC 12.1 shows contract artifacts under an illustrative `contracts/` prefix.
This repository keeps `openapi/`, `asyncapi/`, `schemas/`, and `scripts/` at the
repository root, as required by the layout for `eia-contracts`. The file names
are unchanged.

## Authority, status, and deviation policy

These documents are **canonical**: they state the agreed contract, not
necessarily the current behaviour of every service. Each document carries
machine-readable status:

| Annotation | Meaning |
|---|---|
| `x-implementation.status: implemented` | The document was checked against the controller mappings in the named services. |
| `x-implementation.verifiedAgainst` | Exact source files that were read to verify paths, methods, fields, and enums. |
| `x-status` | Object-level status. `planned` means the object is agreed but not implemented; `implemented` marks a component, channel, or operation that the current code emits or uses; `partial` means a document mixes implemented and planned objects. |
| `x-implemented-by` | AsyncAPI only: the source file that emits an implemented event. |
| `x-path-alias` | OpenAPI only: a second implemented path that serves the same operation with a different prefix (Assumed Claims). |
| `x-planned-operations` | Routes declared by SPEC 11 but not implemented by the current slice. |
| `x-planned-notes` | Known differences between the SPEC route shape and the implemented route shape. |
| `x-compatibility` | Per-document compatibility classification: contract version, previous version, breaking changes, compatible changes. |
| `x-fsri-error-mapping` | Cession and Retrocession: how an upstream FS-RI failure becomes a public 400, 409, 502, or 503 and which code it carries. |

Rules:

1. **Implemented endpoints and fields are documented as they exist**, including
   names that differ from the SPEC prose (`effectiveDate`, `documentType`,
   `classification`, `causeCode`).
2. **A field or endpoint that is not implemented is omitted from `paths` and
   schemas** and listed under `x-planned-operations` or in a schema
   description. No schema claims a field the service never returns.
3. **Where the implementation differs from a normative SPEC rule** (for example
   the offset page envelope versus the SPEC 7.6 cursor envelope), the canonical
   schema documents the agreed shape and `MISMATCHES.md` records the deviation
   with the exact source location and the open decision.
4. **No official ACORD, NAIC, ISO, or SAP code list is invented here.** The
   enumerations in these documents are the internal values that the services
   actually enforce. External code-list mappings belong in `mappings/` and are
   not part of this change.

## Versioning

| Artifact | Version | Rule |
|---|---|---|
| Contract document | SemVer in `info.version` | Major bump for any breaking change. Minor for additive and compatible. Patch for corrections that do not change the wire contract. |
| HTTP API | Major version in the path (`/api/v1`) | A breaking change moves to `/v2`. Additive changes stay in `/v1`. |
| Event | `eventVersion` in the envelope | Additive payload fields keep the version. Removing or re-meaning a field creates a new version with dual publication for at least one release. |
| JSON Schema | `$id` carries the schema name; the version travels with the contract release tag | A breaking schema change creates a new file name or a new `$id`. |

The repository itself is released as `vMAJOR.MINOR.PATCH` from `main`. The
contract version in `info.version` and the repository tag move together.

### Round 2 compatibility notes (2026-10-19)

Round 2 hardens Policy as the reference vertical and adds the SAP FS-RI hand-off
to Cession and Retrocession.

| Document | Version | Classification | Round 2 change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.0.0 | Breaking | Lists return the page envelope; errors become RFC 9457 `Problem`; illegal transitions and duplicate policy numbers become 409; ETag/If-Match and Idempotency-Key are added. |
| `openapi/components.yaml` | 1.1.0 | Additive and documentation | The `Page`, `PageLinks`, `IdempotencyKey`, `IfMatch`, and header components move from planned to implemented; `Problem`, `BadGateway`, and the book headers are described against the Round 2 behaviour. |
| `openapi/cession.yaml` | 1.1.0 | Additive | `fsriHandoffId`, `fsriStatus`, `fsriHandedOffAt`, and `fsriLastError` response fields; optional `fsriContractNumber` request field; hand-off and error-mapping documentation; two internal hand-off persistence operations. |
| `openapi/retrocession.yaml` | 1.1.0 | Additive | The same additive fields and operations for the ASSUMED book. |

The Policy list response changed from a bare JSON array to the page envelope,
and the error body changed from the vertical `ApiError` to `Problem`; both are
breaking for a generated client, so the Policy contract takes a major version.
The HTTP path stays `/api/v1/policies` because the only consumer,
`eia-policy-web`, is updated in the same release. A future external consumer
that needs the old array or error shape requires a `/v2` surface and the
deprecation window above.

Cession and Retrocession changes are additive: optional response fields,
optional request fields, and documentation of behaviour that was not previously
described. The other seven vertical documents are unchanged in Round 2.

### Round 5 compatibility notes (2026-10-19)

Round 5 adds the second vertical-depth slice to Policy, Contract, Direct
Claims, and Assumed Claims, and records the transactional-outbox event rollout.

| Document | Version | Classification | Round 5 change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.1.0 | Additive | Versions, coverage and limits, aggregate erosion, endorsements, insureds, locations, cancellations, and reinstatements; 422 and 428 responses; the second-slice schemas. |
| `openapi/contract.yaml` | 2.0.0 | Breaking | Layers, participants, terms, security, cessions, bordereaux, commutations, bind-eligibility, and bind. `PATCH /status` to BOUND now returns 409 `BIND_REQUIRES_COMMAND`. |
| `openapi/direct-claims.yaml` | 1.1.0 | Additive | Injuries, exposures, reserve history, coverage decision, litigation, settlements, recoveries, liens, and close; the full claim projection. |
| `openapi/assumed-claims.yaml` | 1.1.0 | Additive | Loss advices, bordereaux, reserves, cash calls, recoveries, commutation, disputes, audit, financials, and close; 422 and 428 responses. |
| `openapi/components.yaml` | 1.2.0 | Additive and documentation | `UnprocessableContent` (422) and `PreconditionRequired` (428) become shared responses; `Percent` becomes implemented; the page envelope covers the Policy second slice. |
| `asyncapi/party.yaml` | 1.1.0 | Additive | `party.party.created` and `party.party.updated` become implemented. |
| `asyncapi/cession.yaml` | 1.1.0 | Additive | Three implemented case events (`created`, `updated`, `handed-off`). |
| `asyncapi/retrocession.yaml` | 1.1.0 | Additive | Three implemented case events (`created`, `updated`, `handed-off`). |
| `asyncapi/document.yaml` | 1.1.0 | Additive | Three implemented document metadata events. |
| `asyncapi/payment.yaml` | 1.1.0 | Additive | `created` becomes implemented; `updated` and `status-changed` are added. |
| `asyncapi/notifications.yaml` | 1.1.0 | Additive | `created` and `sent` are added and implemented. |
| `asyncapi/event-catalog.yaml` | 1.1.0 | Additive | The implemented subset is recorded per vertical; 13 new event names are published. |

Contract is the only breaking Round 5 document. Reaching BOUND through
`PATCH /status` bypassed the SPEC 11.3.8 bind preconditions; the guard is the
canonical behaviour and the only consumer, the Contract web remote, is updated
in the same release. The HTTP path stays `/api/v1/contracts`. The other three
OpenAPI documents only add paths, schemas, and response codes.

### Outbox rollout completion (2026-10-20)

The four remaining vertical experts now publish through the transactional
outbox, completing the rollout across all ten publishing verticals. The change
is additive: four event names are added and the implemented channels are
documented against the emitting source.

| Document | Version | Classification | Change |
|---|---|---|---|
| `asyncapi/policy.yaml` | 1.1.0 | Additive | Six implemented events. `policy.policy.created` and `policy.policy.updated` are added to the catalog and carry minimal payload schemas. |
| `asyncapi/contract.yaml` | 1.1.0 | Additive | Five implemented events. `contract.contract.updated` is added with a minimal payload schema. |
| `asyncapi/direct-claims.yaml` | 1.1.0 | Additive | Six implemented events; every name already existed in SPEC 11.4.9 and the catalog. |
| `asyncapi/assumed-claims.yaml` | 1.1.0 | Additive | Nine implemented events. `assumed.claim.updated` is added with a minimal payload schema. |
| `asyncapi/event-catalog.yaml` | 1.2.0 | Additive | Four new names (168 published in total) and the implemented subset for all ten verticals. |

No existing event name is renamed or removed. The new names are the generic
create and update facts that the services already emitted; the catalog now
publishes them, so a consumer generated from the catalog sees every implemented
name. The Contract status command can also emit the cataloged `signed`,
`endorsed`, `expired`, and `cancelled` names; those remain published but
outside the declared implemented subset recorded by this change (M-14).

### Global-search compatibility notes (2026-10-20)

The ten public search operations are additive. No existing path, parameter,
response field, or event changed.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/components.yaml` | 1.3.0 | Additive | `SearchResponse`, `SearchItem`, `SearchType`, `SearchQuery`, and `SearchLimit` become shared components. |
| `openapi/party.yaml` | 1.1.0 | Additive | `GET /api/v1/parties/search`. |
| `openapi/policy.yaml` | 2.2.0 | Additive | `GET /api/v1/policies/search` on the DIRECT book. |
| `openapi/contract.yaml` | 2.1.0 | Additive | `GET /api/v1/contracts/search` on the ASSUMED book. |
| `openapi/direct-claims.yaml` | 1.2.0 | Additive | `GET /api/v1/claims/search` on the DIRECT book. |
| `openapi/assumed-claims.yaml` | 1.2.0 | Additive | `GET /api/v1/assumed-claims/search` and its `/claims/search` alias on the ASSUMED book. |
| `openapi/cession.yaml` | 1.2.0 | Additive | `GET /api/v1/cessions/search` on the DIRECT book. |
| `openapi/retrocession.yaml` | 1.2.0 | Additive | `GET /api/v1/retrocessions/search` on the ASSUMED book. |
| `openapi/document.yaml` | 1.1.0 | Additive | `GET /api/v1/documents/search`. |
| `openapi/payment.yaml` | 1.1.0 | Additive | `GET /api/v1/payments/search`. |
| `openapi/notifications.yaml` | 1.1.0 | Additive | `GET /api/v1/notifications/search`. |

`q` is optional, so a client that never calls search is unaffected. The new
`limit` maximum of 25 applies only to the search envelope and does not change
the Policy page envelope. The search operations keep the document-level
security and add no required request field outside the tenant and book headers.

### Direct Claims task and note contract (2026-10-20)

Direct Claims 1.3.0 adds the diary task and append-only note surface. The change
is additive: no existing path, request field, response field, or event changed.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/direct-claims.yaml` | 1.3.0 | Additive | `GET/POST /api/v1/claims/{claimId}/tasks`, `PATCH /api/v1/claims/{claimId}/tasks/{taskId}`, `GET/POST /api/v1/claims/{claimId}/notes`, their expert equivalents, and the `Task`, `TaskCreate`, `TaskStatusChange`, `Note`, and `NoteCreate` schemas. |
| `asyncapi/direct-claims.yaml` | 1.2.0 | Additive | Four implemented events: `direct.claim.task-created`, `direct.claim.task-completed`, `direct.claim.task-updated`, and `direct.claim.note-added`. |
| `asyncapi/event-catalog.yaml` | 1.3.0 | Additive | The four names are published and implemented (172 published in total). |

The public routes keep the document-level session-cookie security and the
DIRECT book wall: `X-EIA-Tenant` and `X-EIA-Book: DIRECT` are required, and a
missing or different book is hidden as 404. Task `PATCH` is version-checked
(`version` is the task version, not the claim version): a stale version is 409
and an illegal transition is 400. A status command that repeats the current
status is a no-op that returns the task and writes no event.

**Idempotent creation (1.4.0).** Both `POST /tasks` and `POST /notes` accept an
optional `Idempotency-Key` (1-64 printable ASCII characters without spaces). A
retry with the same key and an identical canonical body replays the original 201
task or note with `Idempotent-Replay: true` and writes no second row or event; a
fresh create with a key returns 201 with `Idempotent-Replay: false`. Reusing the
key with a different body is 409 `EIA-DIR-4091` with category
`IDEMPOTENCY_KEY_REUSED`; a key longer than 64 characters or containing a
character outside printable ASCII is 400 `VALIDATION_ERROR` (a blank key is
treated as absent). A concurrent parent-claim version bump is also 409. The
Direct Claims expert reserves the key with a find-then-insert rather than an
atomic upsert, so two truly concurrent first attempts with the same key can
race; `MISMATCHES.md` M-07 records that caveat.

### Assumed Claims task and note contract (2026-10-20)

Assumed Claims 1.3.0 adds the diary task and append-only note surface under the
`/claims` path form. The change is additive: no existing path, request field,
response field, or event changed.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/assumed-claims.yaml` | 1.3.0 | Additive | `GET/POST /api/v1/assumed-claims/claims/{claimId}/tasks`, `PATCH /api/v1/assumed-claims/claims/{claimId}/tasks/{taskId}`, `GET/POST /api/v1/assumed-claims/claims/{claimId}/notes`, and the `Task`, `TaskCreate`, `TaskStatusChange`, `Note`, and `NoteCreate` schemas. |
| `asyncapi/assumed-claims.yaml` | 1.2.0 | Additive | Four implemented events: `assumed.claim.task-created`, `assumed.claim.task-completed`, `assumed.claim.task-updated`, and `assumed.claim.note-added`. |
| `asyncapi/event-catalog.yaml` | 1.4.0 | Additive | The four names are published and implemented (176 published in total). |

The public routes keep the document-level session-cookie security and the
ASSUMED book wall: `X-EIA-Tenant` and `X-EIA-Book: ASSUMED` are required, and a
missing or different book is hidden as 404 `EIA-RNS-7005`. Task `PATCH` is
version-checked against the task version (not the claim version): a stale
version is 409 `EIA-RNS-7802`, an illegal transition is 400 `EIA-RNS-7004`, and
an unknown task is 404 `EIA-RNS-7801`. A status command that repeats the current
status is a no-op that returns the task and writes no event. Task creation and
note append each bump the parent claim version and write their event in the same
transaction.

**Idempotent creation (1.4.0).** Both `POST .../tasks` and `POST .../notes`
accept an optional `Idempotency-Key` (1-64 characters). A retry with the same key
and an identical canonical body replays the original 201 task or note with
`Idempotent-Replay: true` and writes no second row or event; a fresh create
returns 201 with `Idempotent-Replay: false` (the header is always present on an
Assumed Claims task or note 201). Reusing the key with a different body is 409
`EIA-RNS-4091` with category `CONFLICT` and `errors[0].code =
IDEMPOTENCY_KEY_REUSED`. A key that is empty after trimming or longer than 64
characters is 400 `EIA-RNS-7004` with field `Idempotency-Key` and code
`INVALID_IDEMPOTENCY_KEY`, before any write. The domain validates the bounds and
the expert reserves the key with an atomic insert, so concurrent first attempts
either create once or replay. Task `PATCH` remains the only version-checked
write in this slice: a stale task version is 409, and a repeated status is a
no-op.

### Payment source linkage (2026-10-20)

Payment 1.2.0 adds the optional link from a payment to the business record it
disburses. The change is additive: every new field is optional, a client that
omits all three fields sees no change, and the event payload only gains optional
members.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/payment.yaml` | 1.2.0 | Additive | `sourceType`, `sourceId`, and `sourceReference` on `Payment`, `CreatePaymentRequest`, and `CreatePaymentRequestInternal`; the `PaymentSourceType` enum; the create rules; the search matching and `secondary` behaviour. |
| `asyncapi/payment.yaml` | 1.2.0 | Additive | `payment.payment.created` carries a minimal `PaymentPaymentCreatedData` schema with the optional source fields. |

`sourceReference` is the denormalized human label. Storing it on the payment lets
the shell, the queue, and the record subtitle render and link the source claim or
policy without an N+1 lookup against the Direct Claims, Assumed Claims, or Policy
API. The payment still does not embed the source object and does not verify that
the source exists (M-12, M-24).

### Payment source filter (2026-10-20)

Payment 1.3.0 adds an optional source filter to the tenant-scoped list. The
change is additive: a caller that omits both parameters keeps the unfiltered
list, and the response shape is unchanged.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/payment.yaml` | 1.3.0 | Additive | `GET /api/v1/payments` and `GET /internal/v1/payments` accept the optional `sourceType` + `sourceId` pair; the 400 `INVALID_SOURCE_TYPE`/`INVALID_SOURCE_FILTER` behaviour and the tenant scope are documented. |

Both parameters are optional, but they form a pair: supplying one without the
other is 400 `INVALID_SOURCE_FILTER`, not a silently widened list. `sourceType`
is trimmed and upper-cased against the four-value enum, so an unknown value is
400 `INVALID_SOURCE_TYPE`; `sourceId` is a UUID, and a malformed value is 400
`INVALID_PARAMETER`. The filter matches the exact `(sourceType, sourceId)` pair
inside the caller's tenant and keeps the newest-first order. Because the pair is
always required, `OTHER` cannot be listed by type alone. The full semantics are
under [Payment source filter semantics](#payment-source-filter-semantics).

### Claim task and note idempotency (2026-10-20)

Direct Claims and Assumed Claims 1.4.0 make task and note creation retry-safe
with an optional `Idempotency-Key`. The change is additive: the header is
optional, no existing path, request body field, or response body field changed,
and a caller that omits the key keeps the previous create behaviour.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/components.yaml` | 1.4.0 | Additive | `ClaimIdempotencyKey` (`Idempotency-Key`, 1-64 characters) and the `IdempotentReplay` (`true`/`false`) 201 header; the shared 400 and 409 descriptions name the invalid-key and reuse codes. |
| `openapi/direct-claims.yaml` | 1.4.0 | Additive | The public and expert `POST /tasks` and `POST /notes` accept the key, document the 201 `Idempotent-Replay` header, 400 `VALIDATION_ERROR` for an invalid key, and 409 `EIA-DIR-4091` `IDEMPOTENCY_KEY_REUSED`. |
| `openapi/assumed-claims.yaml` | 1.4.0 | Additive | The public `POST .../tasks` and `POST .../notes` accept the key, always emit `Idempotent-Replay` on 201, and document 400 `EIA-RNS-7004` `INVALID_IDEMPOTENCY_KEY` and 409 `EIA-RNS-4091` with `errors[0].code = IDEMPOTENCY_KEY_REUSED`. |

Semantics:

- The key is trimmed and must be 1-64 characters. Assumed Claims rejects an
  empty (after trimming) or longer value as 400; Direct Claims rejects a value
  longer than 64 characters or containing a character outside printable ASCII
  or a space as 400, and treats a blank value as absent.
- The scope is tenant + command type + key. The same key may be used once for a
  task and once for a note because the command type is part of the stored key.
- A retry with the same key and an identical canonical body replays the original
  201 task or note with `Idempotent-Replay: true` and writes no second row or
  event. A fresh create returns 201; Direct Claims emits
  `Idempotent-Replay: false` when a non-blank key was supplied, and Assumed
  Claims emits it on every task or note 201.
- Reusing the key with a different body is 409. Direct Claims uses code
  `EIA-DIR-4091` and category `IDEMPOTENCY_KEY_REUSED`; Assumed Claims uses
  `EIA-RNS-4091` with category `CONFLICT` and the `IDEMPOTENCY_KEY_REUSED`
  field-error code. Both are non-retryable; use a new key for a new command.
- The header spelling is `Idempotent-Replay` (not Policy's
  `Idempotent-Replayed`), and a replay keeps the original 201 status. Both
  differences are recorded in `MISMATCHES.md` M-07.
- Direct Claims reserves the key with a find-then-insert rather than an atomic
  upsert. Two truly concurrent first attempts with the same key can both miss
  the check and one then violates the unique constraint, which the service maps
  to 400 rather than a replay or 409. Retrying sequentially after the first
  commit replays correctly. Assumed Claims uses `INSERT ... ON CONFLICT DO
  NOTHING` and is race-safe. This is the remaining M-07 idempotency caveat.

### Claim assignment contract (2026-10-20)

Direct Claims and Assumed Claims 1.5.0 add claim ownership assignment. The
change is additive: the two PATCH operations are new, the three response fields
are nullable and default to null for an unassigned claim, and the actor header
is optional.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/components.yaml` | 1.5.0 | Additive | The optional shared `ActorHeader` (`X-EIA-Actor`, at most 128 characters). |
| `openapi/direct-claims.yaml` | 1.5.0 | Additive | `PATCH /api/v1/claims/{claimId}/assignment`, its `/internal/v1` expert route, the `AssignClaimRequest` schema, the nullable `assignedAdjuster`/`assignedTeam`/`assignedAt` claim fields, and the optional actor header. |
| `openapi/assumed-claims.yaml` | 1.5.0 | Additive | `PATCH /api/v1/assumed-claims/claims/{claimId}/assignment` (alias `/api/v1/assumed-claims/{claimId}/assignment`), its `/internal/v1` expert route, the `AssignClaimRequest` schema, the nullable assignment fields on `AssumedClaim`, and the optional actor header. |
| `asyncapi/direct-claims.yaml` | 1.3.0 | Additive | The implemented `direct.claim.assigned` channel and operation. |
| `asyncapi/assumed-claims.yaml` | 1.3.0 | Additive | The implemented `assumed.claim.assigned` channel and operation. |
| `asyncapi/event-catalog.yaml` | 1.5.0 | Additive | The two assignment names are published and implemented (178 published in total). |

Ownership semantics:

- The command replaces the claim's current adjuster and, optionally, team. Both
  values are trimmed; `assignedAdjuster` is required (1-128 characters) and
  `assignedTeam` is optional (at most 64 characters). `assignedAt` is the
  instant of the last real change; a claim that has never been assigned returns
  null for all three fields.
- `expectedVersion` is the claim version the caller observed and is required. A
  stale value is 409 `CONFLICT` and writes nothing. Repeating the current
  assignment at the current version is a no-op: the claim, its version,
  `assignedAt`, audit trail, and event stream are unchanged. A real change bumps
  the claim version, appends the assignment audit entry, and writes
  `direct.claim.assigned` or `assumed.claim.assigned` in the same transaction.
- The acting identity is the optional `X-EIA-Actor` header. It is recorded as
  `assignedBy` and in the audit entry, and defaults to the assigned adjuster
  when the header is absent or blank. `assignedBy` is not returned in the public
  claim projection, matching the other audit actor fields (M-20).
- A missing or different book is hidden as 404 (`BOOK_SCOPE_VIOLATION` in
  Direct Claims, `EIA-RNS-7005` in Assumed Claims), consistent with every other
  claim route and SPEC 3.6.2/WALL-06.
- The two event names are new and have no SPEC 11.4.9 or 11.5.9 equivalent
  (M-22). The Direct Claims expert also accepts `X-EIA-User` as an actor alias,
  and the Assumed Claims domain still requires a team that the contract and
  expert make optional; both differences are recorded in M-25.

### Document association links (2026-10-20)

Document 1.2.0 adds the association-link surface. The change is additive: the
link routes are new, the list filter pair is optional, and no existing path,
request field, response field, or event changed.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/document.yaml` | 1.2.0 | Additive | `GET|POST /api/v1/documents/{documentId}/links`, `DELETE /api/v1/documents/{documentId}/links/{linkId}`, their three `/internal/v1` expert aliases, the `DocumentLink`, `CreateDocumentLinkRequest`, and `DocumentLinkedType` schemas, and the optional `linkedType` + `linkedId` filter on the document list. |
| `asyncapi/document.yaml` | 1.2.0 | Additive | The implemented `document.link.added` and `document.link.removed` channels and operations. |
| `asyncapi/event-catalog.yaml` | 1.6.0 | Additive | The two link names are published and implemented (180 published in total). |

Link semantics:

- A link is a tenant-scoped association from a document to one target record:
  `linkedType` is one of `DIRECT_CLAIM`, `ASSUMED_CLAIM`, `POLICY`, `CONTRACT`,
  `PARTY`, `PAYMENT`, or `OTHER`, and `linkedId` is the target UUID. Both are
  required on create. `linkedReference` is an optional display snapshot of at
  most 64 characters; it never resolves or validates the target.
- The projection is `{id, documentId, linkedType, linkedId, linkedReference,
  linkedLabel, createdAt}`. `linkedLabel` is the reference when present,
  otherwise the first eight characters of `linkedId`, so a picker always has a
  label without a cross-vertical call.
- A duplicate `(documentId, linkedType, linkedId)` for the tenant is 409
  `DUPLICATE_LINK` and writes no row or event. A document outside the tenant,
  an unknown link id, and a link under another document are all 404, so the
  response cannot confirm another tenant's or document's link.
- Delete is 204 with no body. The create returns 201 with the link. An unknown
  `linkedType` is 400 `INVALID_LINKED_TYPE`; a request body missing
  `linkedType` or `linkedId` is 400 `VALIDATION_ERROR`.
- `GET /api/v1/documents` accepts the optional `linkedType` + `linkedId` pair.
  Supplying one without the other is 400 `INVALID_LINK_FILTER`; both absent
  means no association filter. `GET /api/v1/documents/search` matches `q`
  against document metadata and any link's `linkedReference`; the expert list
  accepts the pair plus `q`.
- `X-EIA-Tenant` is required on every public route. The expert aliases also use
  the `tenantId` query parameter for the domain call and accept the
  `X-EIA-Tenant` header as a fallback.
- The link is deliberately flat and denormalized: it has no association role,
  no book, and no subject-vertical column, and the create does not check the
  target with its owning vertical (SPEC DOC-09). The SPEC 11.6.10
  `/associations` route and the subject triple plus role remain unimplemented;
  M-26 records the gap.
- Link writes append `document.link.added` or `document.link.removed` to the
  transactional outbox in the same transaction as the row. Both use the
  `DocumentLink` aggregate with the link id and version 1. The names are new
  and have no SPEC 11.6.9 equivalent (the SPEC association fact is
  `document.document.associated`); M-22 records the naming gap.

### Policy billing contract (2026-10-20)

Policy 2.3.0 adds the premium installment plan and its settlement surface. The
change is additive: the three routes are new, the four schemas are new, and no
existing path, request field, response field, or event changed.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.3.0 | Additive | `GET/POST /api/v1/policies/{policyId}/billing`, `PATCH /api/v1/policies/{policyId}/billing/installments/{installmentId}`, and the `BillingPlan`, `Installment`, `CreateBillingPlanRequest`, and `UpdateInstallmentRequest` schemas. |
| `openapi/components.yaml` | 1.6.0 | Additive | The optional shared `BookHeaderDirectOptional` (`X-EIA-Book`, DIRECT when present). |
| `asyncapi/policy.yaml` | 1.2.0 | Additive | Three implemented billing channels and `send` operations. |
| `asyncapi/event-catalog.yaml` | 1.7.0 | Additive | The three names are published and implemented (183 published in total). |

Billing semantics:

- `GET .../billing` returns the public flat plan: `planId`, `planNumber`,
  `policyId`, `totalPremium`, `currency`, `installmentCount`, `frequency`,
  `firstDueDate`, `status`, and the ordered `installments[]`. The ACTIVE plan is
  returned when one exists; otherwise the most recently created closed plan is
  returned. A policy with no plan is 404 `BILLING_PLAN_NOT_FOUND`.
- `POST .../billing` creates the single ACTIVE plan from the policy premium. The
  caller chooses `installmentCount` (1..24), `frequency` (`MONTHLY`,
  `QUARTERLY`, `SEMI_ANNUAL`, `ANNUAL`), and `firstDueDate`. The first n-1
  installments are equal and the last absorbs the rounding remainder, so the
  schedule sums exactly to the premium at scale 4. A second ACTIVE plan is 409
  `BILLING_PLAN_ALREADY_EXISTS`.
- `PATCH .../billing/installments/{installmentId}` settles a DUE or OVERDUE
  installment as `PAID` (recording `paidAt` and the optional `paymentId`) or
  `WAIVED` (no payment evidence). Repeating the same terminal status is an
  idempotent no-op with no event and no version bump; switching PAID to WAIVED
  or back is 409 `INSTALLMENT_ALREADY_SETTLED`.
- The plan total and currency come from the policy, not the request. Mutation
  errors preserve the Policy problem body: 400 for body fields and the 1..24
  window, 404 for an unknown policy, plan, or installment, and 409 for the
  duplicate plan, a settled installment, or a concurrent policy change.
- `X-EIA-Tenant` is required. `X-EIA-Book` is optional for compatibility with
  the other Policy proxy routes, but a supplied value must be DIRECT; another
  book is hidden as 404 `BOOK_SCOPE_VIOLATION`. An absent header is accepted.
  The domain always forwards DIRECT to the expert.
- The plan create writes `policy.billing-plan.created` with the complete
  schedule; settlement writes `policy.installment.paid` or
  `policy.installment.waived`, each in the same transaction as the row change.
  The commands do not accept `Idempotency-Key` or `If-Match` in this slice;
  repeating a terminal settlement is the retry-safe path (M-06, M-07).
- Billing account, billing instructions, receivables, credit notes, dunning,
  disputes, and commission statements from SPEC 11.2.13 remain unimplemented
  (M-12, M-27).

### Policy renewal contract (2026-10-20)

Policy 2.4.0 adds the renewal command. The change is additive: the route, the
request schema, and the nullable lineage field are new; no existing path,
request field, response field, or event changed.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.4.0 | Additive | `POST /api/v1/policies/{policyId}/renew`, the `RenewPolicyRequest` schema, the nullable `Policy.renewedFromPolicyId` lineage field, and the 201/400/404/409 responses. |
| `asyncapi/policy.yaml` | 1.3.0 | Additive | The `policy.policy.renewed` channel and `send` operation become implemented and carry a `PolicyPolicyRenewedData` payload schema. |
| `asyncapi/event-catalog.yaml` | 1.8.0 | Additive | `policy.policy.renewed` joins the Policy implemented subset (10 of 23 Policy names; the platform total stays 183 published events). |

Renewal semantics:

- `POST /api/v1/policies/{policyId}/renew` creates a **new DRAFT successor
  term** and never mutates the source. The successor inherits the source
  product, insured party, coverages, limit schedules, insureds, and locations;
  each copied limit starts with a fresh zeroed erosion state, and the successor
  gets its own initial DRAFT policy version.
- The request body is `RenewPolicyRequest`: `effectiveDate` and
  `expirationDate` are required; `premiumAmount`, `premiumCurrency`,
  `limitAmount`, and `limitCurrency` are optional and default to the source
  policy values. `effectiveDate` must be on or after the source expiration date
  and `expirationDate` must be after `effectiveDate`.
- Only a source in `ISSUED`, `IN_FORCE`, `ENDORSED`, or `REINSTATED` can be
  renewed. Any other status (including `DRAFT`, `QUOTED`, `BOUND`, `RENEWED`,
  `CANCELLED`, `EXPIRED`, `NON_RENEWED`, and `VOID`) is 409
  `RENEWAL_NOT_ALLOWED` with `meta.sourcePolicyId`, `meta.sourceStatus`, and
  `meta.allowedStatuses`; nothing is written. A malformed body or invalid term
  is 400 `VALIDATION_ERROR`; an unknown policy or another tenant's policy is 404
  `POLICY_NOT_FOUND`.
- The 201 body is the **successor** `Policy`, not the source, and carries the
  successor's strong `ETag` (`"<version>"`, which is `"0"` for the new DRAFT
  row). The successor's nullable `renewedFromPolicyId` points at the source;
  policies created directly keep it null. The source keeps its status and has
  no forward pointer on the wire.
- The command requires `X-EIA-Tenant` and `X-EIA-Book: DIRECT`. The older Policy
  proxy routes keep the book header optional for compatibility (see Policy
  billing); renewal, as a new DIRECT command, requires it.
- The successor policy, its children, its initial version, and the
  `policy.policy.renewed` outbox event are written in one transaction, so a
  rollback leaves none of them behind. The event payload carries the successor
  identity and term plus both lineage sides: `renewedFromPolicyId`,
  `sourcePolicyId`/`sourcePolicyNumber`, and
  `newPolicyId`/`newPolicyNumber`.
- The command does not accept `If-Match` or `Idempotency-Key` in this slice.
  The domain currently emits `Idempotent-Replayed: false` from its shared
  mutation helper even though no key is accepted, the expert accepts an omitted
  `effectiveDate` and defaults it, and the domain accepts an absent
  `X-EIA-Book`; the canonical contract requires both dates and the DIRECT book.
  `MISMATCHES.md` M-06, M-07, and M-28 record these differences.
- SPEC 11.2.6 defines renewal as a source transition to `RENEWED`, and SPEC
  11.2.10 mounts the route under `/api/v1/policy/policies/{policyId}/renew`.
  The implementation instead creates a successor DRAFT and keeps the source
  untouched, on the short `/api/v1/policies/{policyId}/renew` path. M-01 and
  M-28 record the deviation.

### Contract technical accounts (2026-10-20)

Contract 2.2.0 adds the periodic technical-account statement for an ASSUMED
treaty. The change is additive: the three operations and four schemas are new,
the three event names are new, and no existing path, request field, response
field, or event changed.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/contract.yaml` | 2.2.0 | Additive | `GET/POST /api/v1/contracts/{contractId}/technical-accounts`, `PATCH /api/v1/contracts/{contractId}/technical-accounts/{accountId}/status`, and the `TechnicalAccount`, `TechnicalAccountStatus`, `CreateTechnicalAccountRequest`, and `UpdateTechnicalAccountStatusRequest` schemas. |
| `asyncapi/contract.yaml` | 1.2.0 | Additive | Three implemented child-aggregate channels and `send` operations: `contract.technical-account.created`, `.issued`, and `.settled`. |
| `asyncapi/event-catalog.yaml` | 1.9.0 | Additive | The three names are published and implemented (186 published in total). |

Technical-account semantics:

- `GET .../technical-accounts` returns a bare array of the contract's accounts,
  newest period first (`periodStart` descending, then `periodEnd` and
  `createdAt`). A missing tenant is 400; an unknown contract, another tenant's
  contract, or an account under another contract is 404.
- `POST .../technical-accounts` produces one period in DRAFT. `periodStart` must
  be before `periodEnd`, `currency` must be an uppercase ISO 4217 code, and
  `cededPremium`, `cededLosses`, `commission`, and `otherCharges` are required
  and non-negative. `accountNumber` is generated as `TA-{year}-{sequence}` and
  `balance` as `cededPremium - commission - cededLosses + otherCharges`; neither
  is accepted from the caller. A positive balance is due from the cedent to the
  reinsurer.
- The exact `(tenant, contract, periodStart, periodEnd)` period is unique. A
  duplicate is 409 `DUPLICATE_TECHNICAL_ACCOUNT_PERIOD`; overlapping but
  non-identical periods are not rejected in this slice (M-29).
- `PATCH .../{accountId}/status` applies only `DRAFT -> ISSUED -> SETTLED`. The
  request enum is `ISSUED` or `SETTLED`; `DRAFT` is 400 `INVALID_STATUS` and a
  skipped or repeated edge is 409 `INVALID_STATUS_TRANSITION`. Each accepted
  transition writes `contract.technical-account.issued` or `.settled` in the
  same transaction as the row update.
- `X-EIA-Tenant` is required. The canonical contract requires
  `X-EIA-Book: ASSUMED`; another book is hidden as 404
  `BOOK_SCOPE_VIOLATION`. The domain currently accepts an absent header for
  compatibility with the other Contract proxy routes, which M-29 records.
- The projection is `{accountId, accountNumber, contractId, periodStart,
  periodEnd, currency, cededPremium, cededLosses, commission, otherCharges,
  balance, status, createdAt}`. `tenantId` is not part of the public projection.
  The SPEC 11.3.4 `technical_account_line` breakdown, the `AGREED`, `DISPUTED`,
  and `SUPERSEDED` statuses, and the SPEC 11.3.10 `/accounts` path remain gaps
  (M-29).
- The three event names are child-aggregate facts with no SPEC 11.3.9
  equivalent (M-22, M-29). The envelope uses the account id and its lifecycle
  version (1, 2, 3) while the outbox partition key stays the contract id.

### Contract period bordereaux (2026-10-20)

Contract 3.0.0 replaces the public bordereau header with the period-bordereau
financial slice. The public path stays
`/api/v1/contracts/{contractId}/bordereaux`; the legacy source-document ingest
header moves to the internal-only `/internal/v1` surface on the same table. The
change is breaking for a generated client of the old public header shape; the
running service and the gateway already use the period projection.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/contract.yaml` | 3.0.0 | Breaking | `GET/POST /api/v1/contracts/{contractId}/bordereaux` now use the period `Bordereau`, `CreateBordereauRequest`, and `BordereauStatus`; adds `PATCH .../bordereaux/{bordereauId}/status` with `UpdateBordereauStatusRequest`; keeps the legacy `BordereauHeader`, `BordereauHeaderStatus`, and `CreateBordereauHeaderRequest` on the internal ingest routes. |
| `asyncapi/contract.yaml` | 1.3.0 | Additive | `contract.bordereau.received` becomes implemented; `contract.bordereau.processed` and `contract.bordereau.failed` are added as implemented child-aggregate channels. |
| `asyncapi/event-catalog.yaml` | 1.10.0 | Additive | The two terminal names are published and implemented, and `received` joins the Contract implemented subset (188 published in total; Contract 26 published and 11 implemented). |

Semantics:

- `GET .../bordereaux` returns a bare array ordered by `periodStart` descending,
  then `periodEnd` and `createdAt` descending. Only period rows are returned;
  the legacy ingest headers are invisible to the public list.
- `POST .../bordereaux` creates the row in RECEIVED. `periodStart` must be
  before `periodEnd`; `receivedDate` and an uppercase ISO 4217 `currency` are
  required; the four declared amounts and `lineCount` are required and
  non-negative. `bordereauNumber` is generated as `BRD-{year}-{sequence}` and
  `status` starts at RECEIVED; neither is accepted from the caller. The exact
  `(tenant, contract, periodStart, periodEnd)` period is unique, so a duplicate
  is 409 `DUPLICATE_BORDEREAU_PERIOD`.
- `PATCH .../bordereaux/{bordereauId}/status` applies only
  `RECEIVED -> PROCESSED` or `RECEIVED -> FAILED`. The request enum is
  `PROCESSED` or `FAILED`; `RECEIVED` is 400 `INVALID_STATUS`, and a skipped or
  repeated edge is 409 `INVALID_STATUS_TRANSITION`. Processing creates or reuses
  the DRAFT technical account for the same contract period and links it through
  `technicalAccountId`; failing creates no account. Both terminal states are
  immutable.
- The public projection is `{bordereauId, bordereauNumber, contractId,
  periodStart, periodEnd, receivedDate, currency, premiumAmount, lossAmount,
  commissionAmount, otherChargesAmount, lineCount, notes, status,
  technicalAccountId, createdAt}`. The expert's row id is serialized as `id`
  internally and remapped to `bordereauId` by the domain; `tenantId` is not part
  of the public projection. Money fields are decimal strings (SPEC 10.3).
- `X-EIA-Tenant` is required. The canonical contract requires
  `X-EIA-Book: ASSUMED`; another book is hidden as 404
  `BOOK_SCOPE_VIOLATION`. The domain currently accepts an absent header for
  compatibility with the other Contract proxy routes, which M-30 records.
- The three facts are child-aggregate events: the envelope uses the bordereau id
  and aggregate version 1 (received) or 2 (processed or failed), while the
  outbox partition key stays the contract id. `contract.bordereau.processed` and
  `.failed` are new names; SPEC 11.3.9 publishes `contract.bordereau.posted` and
  `.rejected` instead, and those names remain planned (M-22, M-30).
- The SPEC `bordereau_line` and `bordereau_exception` staging, duplicate-line
  detection, reconciliation to a declared total, the exception report, and the
  SPEC single-bordereau `GET` remain gaps (M-30).

### Compatibility matrix

| Change | Classification | Requirement |
|---|---|---|
| Add an optional response field | Compatible | Document it; consumers ignore unknown fields. |
| Add an optional request field | Compatible | The default must preserve current behaviour. |
| Add an enum value | Compatible only if consumers tolerate unknown values | Consumers MUST tolerate unknown enum values; otherwise a major version is required. |
| Change a field type or meaning | Breaking | New major version and a migration plan. |
| Remove a field | Breaking | Deprecation window of at least two releases. |
| Change an event payload | Breaking unless additive | New `eventVersion` and dual publication. |
| Change a link type direction | Breaking | New link type and migration. |
| Add an event or channel | Compatible | Add it to the catalog and the vertical document. |
| Rename or remove an event | Breaking | Keep publishing the old name for two releases while the new name is introduced. |

### Breaking-change procedure

1. Open an ADR in the owning service repository describing the migration.
2. Add the new major contract document (`v2`) or the new `eventVersion`.
3. Keep the old contract published for at least two releases.
4. Announce through `Deprecation` and `Sunset` response headers and release
   notes.
5. Remove the old document or version only after the deprecation window.

## Common conventions

### Tenancy and book headers

Every request carries a resolved tenant; no request body may override it.

| Header | Where | Rule |
|---|---|---|
| `X-EIA-Tenant` | All public routes and some internal routes | Required, UUID. Missing or malformed is a 400. |
| `X-EIA-Book` | Direct Claims, Assumed Claims, Cession, Retrocession | Required and fixed to the vertical's book. A different book is hidden as 404 `BOOK_SCOPE_VIOLATION` in all four, so the response cannot confirm existence (SPEC 3.6.2, WALL-06). A missing header is still a 400 `BOOK_REQUIRED` in Cession and Retrocession; that is a validation error, not a book mismatch. |
| `X-EIA-Book` | Policy billing | Optional for compatibility with the other Policy proxy routes, but a supplied value must be DIRECT; another book is hidden as 404 `BOOK_SCOPE_VIOLATION`. An absent header is accepted. The guard runs before the expert call. |
| `X-EIA-Book` | Policy renewal | Required and fixed to `DIRECT`. The contract makes a missing header a 400 and hides another book as 404 `BOOK_SCOPE_VIOLATION`; the domain currently accepts an absent header, which M-28 records. |
| `X-EIA-Book` | Contract technical accounts | Required and fixed to `ASSUMED`. Another book is hidden as 404 `BOOK_SCOPE_VIOLATION`; the domain currently accepts an absent header for compatibility with the other Contract proxy routes, which M-29 records. |
| `X-EIA-Book` | Contract period bordereaux | Required and fixed to `ASSUMED`. Another book is hidden as 404 `BOOK_SCOPE_VIOLATION`; the domain currently accepts an absent header for compatibility with the other Contract proxy routes, which M-30 records. |
| `X-EIA-Actor` | Claim assignment (`PATCH .../assignment`) | Optional acting identity, at most 128 characters. Recorded as `assignedBy` and in the claim audit trail; defaults to the assigned adjuster when absent or blank. The Direct Claims expert also accepts `X-EIA-User` as an alias (M-25). |
| `?tenantId=` | Most internal expert routes | The expert is network-restricted and receives the tenant resolved by its domain service. |

Each operation documents the exact parameter it accepts. Internal routes are
marked `x-internal-api: true` and declare `security: []` because they are not
reachable through the gateway.

### Error envelope

The canonical error body is `Problem` (`schemas/error-envelope.schema.json`),
used with `application/problem+json`:

- Required: `type`, `title`, `status`, `detail`, `instance`, `code`,
  `category`, `retryable`.
- `code` follows the SPEC 6.11 scheme `EIA-<VERT|-PLT|-TX>-<NNNN>`.
- `category` is the SPEC 6.11 category set.
- `errors[]` carries field-level problems.
- `correlationId`, `transactionId`, and `meta` are canonical; Policy emits
  `correlationId` and `meta` and keeps `transactionId` absent until a
  transaction submission exists.

Policy (domain and expert) now emits this shape and media type, but keeps its
legacy code strings (`POLICY_NOT_FOUND`, `CONCURRENT_MODIFICATION`,
`INVALID_STATUS_TRANSITION`, `IDEMPOTENCY_CONFLICT`, and so on) instead of the
`EIA-XXX-NNNN` scheme. The code migration remains open. Assumed Claims also
emits the RFC 9457 shape and media type, with `EIA-RNS-7xxx` codes. The other
eight vertical documents still describe services that emit their own `ApiError`
bodies; their `Problem` responses are the canonical target, and `MISMATCHES.md`
M-02 and M-17 list every variant.

### Money

`schemas/money.schema.json` defines `Money` as
`{ "amount": "1250000.00", "currency": "USD" }`:

- `amount` is a decimal **string** with at most four fraction digits and is
  never a JSON number.
- `currency` is an ISO 4217 alpha-3 code.
- Zero is valid; negative values only for explicit reversal or return fields.

The current vertical payloads use flat pairs (`premiumAmount`/`premiumCurrency`,
`reserveAmount`/`reserveCurrency`, `cededPremium`/`cededLoss` + `currency`).
Those field names are documented. Every money-bearing service serializes the
amount as a decimal string (M-03 is closed); moving the flat pairs to the
canonical `Money` object is M-12/M-13.

### Concurrency, idempotency, and conflicts

Policy is the reference implementation:

- `ETag: "<version>"` is returned on detail, create, status, and every
  second-slice mutation response.
- `If-Match` on a mutation performs optimistic concurrency. A stale tag or body
  version is 409 `CONCURRENT_MODIFICATION` with `meta.currentVersion`,
  `meta.expectedVersion`, and `errors[0].code = STALE_VERSION`; a malformed
  header is 400 `INVALID_IF_MATCH`. The header is optional for backward
  compatibility and takes precedence over the body `expectedVersion`.
- `Idempotency-Key` on create and on every second-slice command is optional but
  recommended. A same-key replay of an identical request returns 200 with
  `Idempotent-Replayed: true`; reusing the key with a different request is 409
  `IDEMPOTENCY_CONFLICT`; a duplicate business key is 409
  `DUPLICATE_POLICY_NUMBER`, `DUPLICATE_COVERAGE_CODE`, or a similar code.
- An illegal lifecycle transition is 409 `INVALID_STATUS_TRANSITION`; a domain
  policy rejection is 422 `BUSINESS_RULE`; a missing approval is 428
  `APPROVAL_REQUIRED`.

No other vertical emits `ETag` or accepts `If-Match`.
Contract bind takes `expectedVersion` and `approvedBy`; the Direct Claims child
PATCH commands take `expectedVersion`; Assumed Claims propagates the expert's
409/422/428; Cession/Retrocession still return 400 for an illegal lifecycle
edge. Their FS-RI hand-off is a separate case: an FS-RI conflict is 409
`FSRI_CONFLICT`, an unusable FS-RI response is 502, and an FS-RI outage is 503.
See `MISMATCHES.md` M-06, M-07, M-11, and M-21.

The Direct Claims and Assumed Claims task and note POSTs are the second
idempotency implementation. They accept the optional `Idempotency-Key`
(1-64 characters), replay an identical canonical body as 201 with
`Idempotent-Replay: true`, and return 409 `EIA-DIR-4091` or `EIA-RNS-4091`
(`IDEMPOTENCY_KEY_REUSED`) when the key is reused with a different body. Unlike
Policy they keep the original 201 status on replay, spell the marker
`Idempotent-Replay`, and Direct Claims only emits it when a key was supplied.
Assumed Claims always emits it on a task or note 201. The Direct Claims
find-then-insert reservation has a narrow concurrent-first-attempt race; the
Assumed Claims reservation is atomic. Task `PATCH` remains version-checked, and
a repeated status is a no-op, so it is retry-safe. The residual differences are
part of M-07.

### Claim assignment

Claim assignment is the ownership command for both claim verticals:

| Vertical | Public route | Expert route | Book |
|---|---|---|---|
| Direct Claims | `PATCH /api/v1/claims/{claimId}/assignment` | `PATCH /internal/v1/claims/{claimId}/assignment` | `DIRECT` |
| Assumed Claims | `PATCH /api/v1/assumed-claims/claims/{claimId}/assignment` (alias `/api/v1/assumed-claims/{claimId}/assignment`) | `PATCH /internal/v1/assumed-claims/{claimId}/assignment` | `ASSUMED` |

The body is `AssignClaimRequest`: `assignedAdjuster` (required, at most 128
characters), `assignedTeam` (optional, at most 64), and `expectedVersion`
(required integer, zero or greater). The response is the updated claim with
nullable `assignedAdjuster`, `assignedTeam`, and `assignedAt`.

The claim version is the concurrency token. A stale `expectedVersion` is 409 and
nothing is written; repeating the current assignment at the current version is a
no-op that keeps the previous `assignedAt`, version, audit entry, and event. A
real reassignment bumps the version, appends the audit entry, and publishes
`direct.claim.assigned` or `assumed.claim.assigned` in the same transaction. The
optional `X-EIA-Actor` header supplies the acting identity (defaulting to the
assigned adjuster); it is stored as `assignedBy` and is deliberately not part of
the public claim projection. A missing or wrong book is hidden as 404, and a
same-tenant claim that does not exist is 404.

### Pagination and collections

The implemented Policy page envelope is `Page` in `openapi/components.yaml`:
`{items, page, size, total, _links:{self, next, prev}}`, with `?page=` (default
0) and `?size=` (default 20, maximum 100). `next` is omitted on the last page
and `prev` on the first page; hrefs are relative. Both the public and the expert
list operations return it, and every Policy second-slice collection
(versions, coverages, limits, aggregate state, endorsements, insureds,
locations, cancellations, and reinstatements) returns the same envelope with
`items` narrowed to its resource in `policy.yaml`.

Every other vertical still returns a bare JSON array, including the Contract
second-slice collections, the period-bordereau and technical-account lists, and
the Direct Claims and Assumed Claims child collections. SPEC 7.6 and 12.2
specify a different, cursor-based envelope
(`data`, `page:{size, hasMore, nextCursor, total?}`, `?page[size]` and
`?page[after]`, default 25, maximum 200). The offset form is the implemented
contract; the divergence and the migration choice are recorded in
`MISMATCHES.md` M-04.

### Payment source linkage

The Payment slice does not embed the source claim or policy. A payment may
carry a flat, optional source link instead:

| Field | Type | Rule |
|---|---|---|
| `sourceType` | enum | `DIRECT_CLAIM`, `ASSUMED_CLAIM`, `POLICY`, or `OTHER`. Required whenever `sourceId` is supplied. |
| `sourceId` | UUID | UUID of the source direct claim, assumed claim, or policy. Required for the three classified types; omitted for an `OTHER` reference-only source. |
| `sourceReference` | string, max 64 | Human-readable reference, for example `CLM-2026-0000001`. Optional metadata; it never replaces `sourceId` for a classified source. |

Rules and semantics:

- A classified source (`DIRECT_CLAIM`, `ASSUMED_CLAIM`, `POLICY`) requires
  `sourceId`; supplying `sourceId` without `sourceType` is a 400
  (`sourceType is required when sourceId is supplied`).
- `OTHER` is the escape hatch: it may carry only `sourceReference`, with no
  `sourceId`. A payment with no source at all is valid.
- `sourceType` accepts `DIRECT_CLAIM` and `ASSUMED_CLAIM` even though the
  Direct Claims and Assumed Claims books are separate; the payment is not book
  scoped, so the type, not the book header, identifies the source vertical.
- The link is deliberately denormalized. `sourceReference` is the label the
  list, queue, and record subtitle render, and the payment web remote uses
  `sourceType` to cross-link to `/direct-claims`, `/assumed-claims`, or
  `/policy`. Rendering a page of payments therefore needs no N+1 lookup of the
  source vertical; the reference is stored at create time.
- The source is not a foreign key: there is no referential-integrity or
  existence check against the source vertical, and `sourceId` is not resolved
  before create. The SPEC 11.7.4 `claim_vertical`/`claim_id`/`claim_number`
  projection, claim-capacity check, and source object remain planned (M-12,
  M-24).
- `sourceReference` is trimmed and limited to 64 characters; the search
  matching and `secondary` suffix behaviour are described under
  [Global search](#global-search).

### Payment source filter semantics

The tenant-scoped list accepts an optional `sourceType` + `sourceId` pair:

| Parameter | Type | Rule |
|---|---|---|
| `sourceType` | enum | `DIRECT_CLAIM`, `ASSUMED_CLAIM`, `POLICY`, or `OTHER`. Must be supplied with `sourceId`. The value is trimmed and upper-cased, so a lower-case value selects the canonical value. |
| `sourceId` | UUID | Must be supplied with `sourceType`; a value that is not a UUID is 400 `INVALID_PARAMETER`. |

Rules and semantics:

- Both or neither. Supplying only `sourceType` or only `sourceId` is 400
  `INVALID_SOURCE_FILTER`, with the message naming the missing member; the
  expert rejects the partial pair instead of returning a wider list.
- An unknown `sourceType` is 400 `INVALID_SOURCE_TYPE`. The type is normalized
  before the pairing check, so an unknown type alone reports
  `INVALID_SOURCE_TYPE` rather than `INVALID_SOURCE_FILTER`.
- The match is exact on the normalized `(sourceType, sourceId)` pair and stays
  inside the caller's tenant. A payment whose link has a different type, a
  different id, or no link is not returned.
- `OTHER` is part of the filter enum, but the pair is still mandatory, so a
  type-only `OTHER` query is 400 and there is no way to list every OTHER
  payment through this filter.
- `sourceReference` is not a filter parameter; global search still matches it
  through `q`.
- The filtered list keeps the unfiltered list's order: `createdAt` descending,
  with `paymentNumber` as the tie-break. Omitting both parameters returns the
  unchanged unfiltered list.
- `X-EIA-Tenant` is required. The domain forwards the pair and the tenant header
  to the expert, and the expert owns the closed-set and pairing validation, so
  the public 400 code and message are the expert's. A missing tenant is 400
  `MISSING_TENANT_HEADER`; a malformed tenant is 400 `INVALID_PARAMETER`.

### Policy billing

Policy owns the premium installment plan (SPEC 11.2.13). The public billing
surface is a domain proxy over the Policy expert; the expert also exposes the
same resource under `/internal/v1/policies/{policyId}/billing` for the domain
adapter, but that internal route is not part of the public contract.

| Operation | Path | Success | Errors |
|---|---|---|---|
| Read plan | `GET /api/v1/policies/{policyId}/billing` | 200 `BillingPlan` | 400, 404 |
| Create plan | `POST /api/v1/policies/{policyId}/billing` | 201 `BillingPlan` | 400, 404, 409 |
| Settle installment | `PATCH /api/v1/policies/{policyId}/billing/installments/{installmentId}` | 200 `Installment` | 400, 404, 409 |

The plan projection is flat and uses the domain DTO names: `planId`,
`planNumber`, `policyId`, `totalPremium` (decimal string), `currency`,
`installmentCount`, `frequency`, `firstDueDate`, `status`, and
`installments[]`. Each installment is `installmentId`, `installmentNumber`,
`dueDate`, `amount` (decimal string), `status`, `paidAt`, and `paymentId`.
`paidAt` and `paymentId` are populated only for PAID; a WAIVED installment has
no payment evidence.

Rules:

- At most one ACTIVE plan exists per policy. The create command takes the
  total and currency from the policy and splits the premium across 1..24
  installments; the first n-1 amounts are equal and the last one absorbs the
  rounding remainder, so the schedule sums exactly to `totalPremium` at scale 4.
  A second ACTIVE plan is 409 `BILLING_PLAN_ALREADY_EXISTS`.
- Plan `frequency` is `MONTHLY`, `QUARTERLY`, `SEMI_ANNUAL`, or `ANNUAL`; the
  due-date cadence applies that step to `firstDueDate`. A blank or unknown
  frequency is 400 `INVALID_BILLING_FREQUENCY`.
- Installment `status` is `DUE`, `OVERDUE`, `PAID`, or `WAIVED`. The settle
  command accepts only the terminal targets `PAID` and `WAIVED`; a DUE or
  OVERDUE row can be settled once. Repeating the same terminal status returns
  the unchanged row and writes no event; switching terminal statuses is 409
  `INSTALLMENT_ALREADY_SETTLED`.
- `X-EIA-Tenant` is required. `X-EIA-Book` is optional on the public routes for
  compatibility, but a supplied value must be DIRECT and any other book is
  hidden as 404 `BOOK_SCOPE_VIOLATION` (SPEC 3.6.2, WALL-06). The domain always
  sends DIRECT to the expert.
- The plan create and each settlement bump the policy row version and write
  `policy.billing-plan.created`, `policy.installment.paid`, or
  `policy.installment.waived` in the same transaction. The billing commands do
  not accept `Idempotency-Key` or `If-Match`; a repeated terminal settlement is
  the retry-safe path (M-06, M-07).
- The SPEC 11.2.13 `/installments` route and `policy.billing.plan-created`
  event name differ from the implemented `/billing` route and
  `policy.billing-plan.created` name; the two installment facts have no SPEC
  name. The naming difference and the still-unimplemented billing-account,
  instruction, receivable, credit-note, dunning, dispute, and commission
  surfaces are recorded in M-22 and M-27.

### Global search

The shell's `/search` page fans out to one search operation per vertical. Every
search route is public, is `GET /api/v1/{resource}/search`, and returns the
shared `SearchResponse` envelope from `openapi/components.yaml`.

| Vertical | Search path | Book |
|---|---|---|
| Party | `/api/v1/parties/search` | none |
| Policy | `/api/v1/policies/search` | `DIRECT` |
| Contract | `/api/v1/contracts/search` | `ASSUMED` |
| Direct Claims | `/api/v1/claims/search` | `DIRECT` |
| Assumed Claims | `/api/v1/assumed-claims/search` (alias `/api/v1/assumed-claims/claims/search`) | `ASSUMED` |
| Cession | `/api/v1/cessions/search` | `DIRECT` |
| Retrocession | `/api/v1/retrocessions/search` | `ASSUMED` |
| Document | `/api/v1/documents/search` | none |
| Payment | `/api/v1/payments/search` | none |
| Notifications | `/api/v1/notifications/search` | none |

Request rules:

- `q` is optional. It is trimmed and matched case-insensitively as a contains
  over the searchable fields named in the vertical's operation description. An
  absent or blank `q` returns the most recently updated records.
- `limit` is optional, defaults to 10, and must be between 1 and 25. A
  non-integer or out-of-range value is a 400.
- `X-EIA-Tenant` is required on every search. `X-EIA-Book` is required and
  fixed on the six book-scoped verticals; another book is hidden as 404
  `BOOK_SCOPE_VIOLATION` (SPEC 3.6.2).
- The contract requires a missing tenant, a missing book, or an invalid limit
  to be a 400 `application/problem+json` `Problem`; a different book is hidden
  as 404 `BOOK_SCOPE_VIOLATION`. Security is the document-level session cookie,
  the same requirement as the list operation.

Payment search additionally matches `sourceId` and `sourceReference`. When a
matched payment has a `sourceReference`, it is appended to `secondary` after
the payment type (or currency) and the status, separated by ` · `:
`INDEMNITY · DRAFT · CLM-2026-0000001`. The source UUID is searchable but is not
rendered in `secondary`, and `label` remains the payment number. This keeps the
source visible and linkable in the result row without an N+1 lookup per
payment.

Response shape:

```json
{
  "query": "ACME",
  "limit": 10,
  "items": [
    {
      "id": "0192f3a4-...",
      "type": "PARTY",
      "label": "PTY-000000001",
      "secondary": "Acme Holdings · ORGANIZATION",
      "status": "ACTIVE",
      "href": "/party?record=0192f3a4-..."
    }
  ]
}
```

`type` is one of `PARTY`, `POLICY`, `CONTRACT`, `DIRECT_CLAIM`,
`ASSUMED_CLAIM`, `CESSION`, `RETROCESSION`, `DOCUMENT`, `PAYMENT`, or
`NOTIFICATION`. `href` is relative to the shell origin. The services currently
clamp an over-limit value instead of returning 400, and the claim verticals
hide a missing book as 404; the canonical target and the divergence are
recorded in `MISMATCHES.md` M-23.

## Validation

### Run the validator

```sh
python scripts/validate_contracts.py
python scripts/validate_contracts.py --verbose
```

Requirements: Python 3.9 or later. **No third-party package, Node.js install,
Maven, or network access is required.** The script uses only the standard
library.

Exit codes: `0` every check passed, `1` one or more checks failed, `2` usage or
missing directory.

### What the validator checks

1. **YAML parses.** A strict parser for the YAML subset this repository uses
   (block mappings and sequences, plain and quoted scalars, flow lists and
   maps, folded and literal block scalars, comments). Unsupported constructs
   and tab indentation fail with a file and line number.
2. **File inventory.** Exactly the ten vertical OpenAPI documents plus
   `components.yaml`, the ten vertical AsyncAPI documents plus
   `event-catalog.yaml`, and the three JSON Schemas.
3. **OpenAPI structure.** `openapi: 3.1.0`, SemVer `info.version`, the JSON
   Schema 2020-12 dialect, non-empty `paths`, operation IDs (unique per file and
   across the repository), summaries, tags, responses with a 2xx, request-body
   content types, internal-route security markers, the required shared
   components (schemas, parameters, headers, and responses), the complete table
   of required paths and methods per vertical (including the Round 5 second
   slice, the Direct Claims and Assumed Claims task and note routes, and the ten
   global-search routes), the task/note schemas, the claim task/note idempotency
   header parameter, the 201 `Idempotent-Replay` header, the shared 400
   invalid-key documentation, and the 409 code on all six create operations,
   the claim assignment paths on both claim verticals, the `AssignClaimRequest`
   schema and its field bounds, the nullable assignment fields on `Claim` and
   `AssumedClaim`, the optional shared `ActorHeader`, the assignment
   200/400/404/409 responses, the six document association-link operations on
   the public and expert surfaces, the `DocumentLink`, `CreateDocumentLinkRequest`,
   and `DocumentLinkedType` schemas, the `linkedType` + `linkedId` list filter,
   the expert list `q`, and the search `linkedReference` match, the ten search
   operations' shared parameters and `SearchResponse`/400/404 responses, the
   `SearchResponse` and `SearchItem` keys, the required 422/409/428 response
   codes on the Round 5 mutations, the payment source fields and their create
   rules, the optional `sourceType` + `sourceId` list filter on the public and
   expert payment lists with its enum, UUID, tenant parameter, 400 response, and
   `INVALID_SOURCE_TYPE`/`INVALID_SOURCE_FILTER` documentation, the three Policy
   billing operations, the optional shared
   `BookHeaderDirectOptional` parameter, the `BillingPlan`, `Installment`,
   `CreateBillingPlanRequest`, and `UpdateInstallmentRequest` schemas and their
   field bounds and enums, the Policy renewal operation with its required
   `TenantHeader` and `BookHeaderDirect` parameters, the `RenewPolicyRequest`
   required/optional field split, the 201 successor `Policy` with the shared
   `ETag`, the 400/404/409 responses with `RENEWAL_NOT_ALLOWED` on the 409, the
   nullable `Policy.renewedFromPolicyId` lineage field, the three public
   period-bordereau operations with their required `TenantHeader` and
   `BookHeaderAssumed` parameters, the `Bordereau`, `BordereauStatus`,
   `CreateBordereauRequest`, and `UpdateBordereauStatusRequest` schemas and
   their field types, the nullability of `notes`/`technicalAccountId`, the
   `PROCESSED`/`FAILED` request enum, the 201/200 successes, and the
   400/404/409 responses, and agreement between `info.version` and
   `x-compatibility.contractVersion`.
4. **AsyncAPI structure.** `asyncapi: 3.0.0`, channel addresses, `x-event-type`,
   `x-status: planned|implemented`, `x-implemented-by` on every implemented
   channel, one `send` operation per channel, a `DomainEvent` message on
   every channel, and the optional source fields on the payment created
   payload.
5. **Event catalog cross-check.** The published set in `event-catalog.yaml`
   must equal the channel addresses in the matching vertical document, event
   names must be unique across the platform and must match
   `{vertical}.{aggregate}.{verb}`, every consumed event must have a publisher,
   and the catalog `implemented` list must equal the channels marked
   `x-status: implemented`. The implemented event names for all ten publishing
   verticals are required explicitly, including `direct.claim.assigned`,
   `assumed.claim.assigned`, `document.link.added`,
   `document.link.removed`, `policy.policy.renewed`,
   `policy.billing-plan.created`, `policy.installment.paid`,
   `policy.installment.waived`, `contract.bordereau.received`,
   `contract.bordereau.processed`, and `contract.bordereau.failed`.
6. **JSON Schema checks.** All three files parse as JSON, declare the 2020-12
   dialect and an `$id`, carry the required members, keep required properties
   defined, and validate their own examples against a small schema subset.
7. **Reference resolution.** Every `$ref` in every YAML document resolves,
   including references into `components.yaml`, `schemas/*.json`, and the
   `$defs` of those schemas.

### What the validator does not do

- It is not a full OpenAPI or AsyncAPI validator. Schema semantics beyond the
  required members and the examples are not checked. A release engineer may
  additionally run an official validator if one is available, but the
  repository itself takes no dependency on one.
- It does not start the services. Contract conformance against a running
  service is the contract test described in SPEC 12.7 and is executed by
  `eia-quality`; this script protects the documents, not the runtime.
- It does not validate external code lists. Those belong in `mappings/`.

## Adding or changing a contract

1. Read the owning SPEC section and the implemented controller or client.
2. Change the vertical OpenAPI document and, when a shared type changes,
   `openapi/components.yaml` and the JSON Schema together.
3. For an event change, update the vertical AsyncAPI document **and** the
   catalog entry in the same commit.
4. Run `python scripts/validate_contracts.py` and keep the output with the
   release evidence.
5. Update `MISMATCHES.md` when a deviation is added, resolved, or discovered.
6. Update `CHANGELOG.md` under `Unreleased`.
7. Open a pull request; do not push to `main`. Conventional commits, signed
   commits, at least one approval, and CODEOWNERS approval are required.

## Known deviations

`MISMATCHES.md` is the authoritative list. The largest open ones are:

- Policy emits the canonical `Problem` body and media type with legacy code
  strings; the other nine verticals still emit their own `ApiError` bodies, and
  the `EIA-XXX-NNNN` code migration is open;
- the Policy page envelope is offset-based (`items`, `page`, `size`, `total`,
  `_links`) rather than the cursor envelope in SPEC 7.6/12.2, and the other
  verticals still return bare arrays;
- `ETag`/`If-Match` exist only in Policy, and the billing plan, installment, and
  renewal commands do not accept them. `Idempotency-Key` covers Policy plus
  the Direct Claims and Assumed Claims task/note creates; the remaining vertical
  creates do not accept it, the claim task/note responses spell the marker
  `Idempotent-Replay`, and the Direct Claims reservation has a narrow concurrent
  first-attempt race (M-06, M-07). Detail `_links` exist nowhere, and
  Cession/Retrocession still return 400 for an illegal lifecycle edge;
- the Cession/Retrocession FS-RI hand-off is synchronous, with no hand-off
  queue or hand-off resource (SPEC 7.18.3/HAND-05);
- the ten global-search routes are implemented under the short
  `/api/v1/{resource}/search` form. SPEC defines global search only as the shell
  `/search` page and the `?q=` convention, not as a per-vertical API; the
  services also clamp an over-limit `limit` instead of returning 400 and the
  claim verticals hide a missing book as 404. The contract records the canonical
  400/1-25 behaviour and `MISMATCHES.md` M-23 records the divergence;
- a payment carries a flat `sourceType`/`sourceId`/`sourceReference` link rather
  than the SPEC 11.7.4 `claim_vertical`/`claim_id`/`claim_number` projection, and
  the source is neither resolved nor checked for existence (M-12, M-24);
- document associations are implemented as tenant-scoped `/links` with a flat
  `linkedType`/`linkedId` target and no role, book, or DOC-09 target-existence
  check, and publish `document.link.added`/`.removed` rather than the SPEC
  `document.document.associated` (M-22, M-26);
- claim assignment is implemented on both claim verticals but has no SPEC 11.4.10
  or 11.5.10 route or SPEC 11.4.9/11.5.9 event name. The Assumed Claims domain
  still requires a team the contract and expert make optional, the Direct Claims
  expert returns 409 instead of 400 for a negative `expectedVersion`, and the
  Direct Claims expert accepts `X-EIA-User` as an extra actor alias (M-22,
  M-25);
- Policy billing is implemented under `/api/v1/policies/{policyId}/billing`
  with the flat `BillingPlan`/`Installment` projection, while SPEC 11.2.13 names
  the route `/installments` and defines the plan event as
  `policy.billing.plan-created`; the installment paid and waived facts have no
  SPEC name. Billing accounts, instructions, receivables, credit notes, dunning,
  disputes, and commission statements remain unimplemented (M-12, M-22, M-27);
- Policy renewal creates a successor DRAFT policy and leaves the source in its
  current status, whereas SPEC 11.2.6 turns the source to `RENEWED`; the public
  path is the short `/api/v1/policies/{policyId}/renew` rather than SPEC
  11.2.10's `/api/v1/policy/policies/{policyId}/renew`. The canonical contract
  requires both term dates and `X-EIA-Book: DIRECT`, but the expert defaults an
  omitted `effectiveDate`, the domain accepts an absent book header, and the
  domain emits `Idempotent-Replayed: false` without accepting a key (M-06, M-07,
  M-28);
- contract period bordereaux keep the implemented `RECEIVED -> PROCESSED|FAILED`
  lifecycle and the `contract.bordereau.processed`/`.failed` event names, while
  SPEC 11.3.9 publishes `contract.bordereau.posted`/`.rejected`; the line and
  exception staging, duplicate-line detection, reconciliation to a declared
  total, the exception report, and the SPEC single-bordereau `GET` remain gaps.
  The domain also accepts an absent `X-EIA-Book` and the expert has no book
  check of its own (M-22, M-30);
- ten experts publish a subset of their events through the transactional
  outbox into the platform `event-ingest` inbox, but no vertical consumes
  another vertical's events, there is no subscription registry or gap
  detection, and the implemented event names still differ from the SPEC
  catalog names (M-14, M-22).

## Repository standard

- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [Implementation notes](IMPLEMENTATION.md)
- Repository standard: `../../SPEC.md` section 16.9
- Workspace conventions: `../CONVENTIONS.md`

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
