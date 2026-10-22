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
| `openapi/components.yaml` | Shared parameters, headers, responses, and schemas: canonical `Problem` error envelope, money, offset page envelope, global-search envelope, ETag/If-Match, Idempotency-Key (Policy and the claim task/note creates), the optional `X-EIA-Actor` header, audit fields, entity references, tenant and book headers, including the optional Policy billing and receivables `X-EIA-Book`. |
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

### Notifications DUNNING_NOTICE type (2026-10-22)

Notifications 1.2.0 adds the implemented dunning escalation type. The change is
additive: one member joins the closed `NotificationType` enum, and no path,
request field, response field, or event changes.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/notifications.yaml` | 1.2.0 | Additive | `NotificationType` adds `DUNNING_NOTICE` between `ESCHEATMENT_DUE` and `NEW_DOCUMENT_UPLOAD`. |

- `DUNNING_NOTICE` is the type the receivables workbench prefills when a
  collector hands an overdue installment off to Notifications. The shell opens
  the new-notification form with `notificationType=DUNNING_NOTICE`, the
  Notifications web remote lists the value, and the domain and expert accept and
  persist it. The hand-off only drafts the notification; Notifications owns the
  send.
- The type is SPEC-less. SPEC 11.8.5 v1 ends the Payment category at
  `ESCHEATMENT_DUE`, begins Document at `NEW_DOCUMENT_UPLOAD`, and names no
  dunning notification; SPEC 11.2.13 models dunning levels on the billing
  account instead. `MISMATCHES.md` M-48 records the deviation.
- The enum stays closed. An unknown value is 400 `EIA-NTF-9403`
  `INVALID_NOTIFICATION_TYPE`; adding a type is an additive minor change and
  removing one is breaking (SPEC 10.4).
- `Notification.notificationType`, `CreateNotificationRequest.notificationType`,
  and `CreateNotificationRequestInternal.notificationType` all reference the one
  `NotificationType` schema, so the type is accepted on both create commands and
  returned by every read.
- The validator requires the member, its position between `ESCHEATMENT_DUE` and
  `NEW_DOCUMENT_UPLOAD`, no repeated value, and the three references with their
  required membership. The full run passes 14,069 checks.

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

### Payment allocations (2026-10-20)

Payment 1.4.0 adds the allocation surface: a payment can be split across the
claim or policy target and financial component it settles. The change is
additive: no existing path, request field, response field, or event changed.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/payment.yaml` | 1.4.0 | Additive | `GET/POST /api/v1/payments/{paymentId}/allocations`, the `PaymentAllocation`, `PaymentAllocationSummary`, and `CreatePaymentAllocationRequest` schemas, the `PaymentAllocationTargetType` and `PaymentAllocationComponent` enums, and the 409 `ALLOCATION_EXCEEDS_PAYMENT`/`PAYMENT_NOT_ALLOCATABLE` guards. |
| `asyncapi/payment.yaml` | 1.3.0 | Additive | The implemented `payment.allocation.created` channel, `send` operation, and `PaymentAllocationCreatedData` payload. |
| `asyncapi/event-catalog.yaml` | 1.14.0 | Additive | `payment.allocation.created` is published and implemented (193 published in total; Payment 19 published and 4 implemented). |

The allocation read is the reconciliation view of the payment amount: `items`
oldest first, `paymentAmount`, `totalAllocated`, `unallocated`, and `currency`.
An allocation is append-only and always uses the payment's currency. The create
is guarded by the payment status and by the payment amount, so it can return
409 `PAYMENT_NOT_ALLOCATABLE` or 409 `ALLOCATION_EXCEEDS_PAYMENT` without
writing a row or an event.

The SPEC 11.7.11 table lists only `GET .../allocations`, and SPEC 11.7.10 has
no allocation-created name; the implemented POST and
`payment.allocation.created` event are new names with no SPEC equivalent
(`MISMATCHES.md` M-22 and M-35).

### Payment status transitions (2026-10-21)

Payment 1.5.0 adds the public generic lifecycle command. The change is
additive: the route and the request schema are new, no existing path, request
field, response field, or event changes, and the four named actions remain.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/payment.yaml` | 1.5.0 | Additive | `PATCH /api/v1/payments/{paymentId}/status` and the `UpdatePaymentStatusRequest` schema; the implemented transition graph, terminal statuses, approval gate, optional `expectedVersion`, and optional 200-character `reason`. |

The route forwards `{status, expectedVersion?, reason?}` to the expert and
returns the updated `Payment`. The expert owns the graph, the approval gate,
and the concurrency check, and the public API preserves its 400/404/409 codes
(`INVALID_STATUS`, `INVALID_STATUS_TRANSITION`, `PAYMENT_NOT_APPROVED`,
`CONCURRENT_MODIFICATION`, `PAYMENT_NOT_FOUND`). The graph and its widening
over SPEC 11.7.6, plus the reason-length enforcement gap that 1.6.0 closes, are
recorded in `MISMATCHES.md` M-46. The full validation run passes 13,978 checks.

### Payment status reason projection (2026-10-22)

Payment 1.6.0 exposes the latest status reason on the payment projection. The
change is additive: one required-but-nullable response member, no path, request
field, or event changes, and a caller that ignores unknown response members is
unaffected.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/payment.yaml` | 1.6.0 | Additive | `Payment` adds the required-but-nullable 200-character `statusReason` and documents the latest-status-reason semantics; the status PATCH and both transition request schemas record that the accepted `reason` is returned and that an over-long value is 400 `VALIDATION_ERROR`. |

`statusReason` is the trimmed `reason` supplied with the most recent accepted
status change, whether through `PATCH /api/v1/payments/{paymentId}/status` or
one of the named actions (`/submit`, `/authorize`, `/approve`, and `/issue`
supply their own text). Each accepted change replaces the previous value, and a
change without a reason clears it, so the member describes the current `status`
only and is not a status history. A payment that has never changed status, or
whose latest change carried no reason, returns `null`; the member is always
present. The value is persisted in `payment.status_reason` (`varchar(200)`); the
expert rejects a longer request reason with 400 `VALIDATION_ERROR` before any
write. `MISMATCHES.md` M-46 records the SPEC-less route and graph and the closed
reason-validation and projection gaps. The full run passes 14,098 checks.

### Payment allocation reversal (2026-10-22)

Payment 1.7.0 documents the reversal of an allocation. The change is additive:
one route, one request schema, two nullable allocation members, two summary
money members, and a new event name; no existing path, request field, response
field, or event changes.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/payment.yaml` | 1.7.0 | Additive | `POST /api/v1/payments/{paymentId}/allocations/{allocationId}/reverse` with `ReversePaymentAllocationRequest` (`reason`, required, 1-200 characters); `PaymentAllocation` adds the required-but-nullable `reversedAt` and 200-character `reversalReason`; `PaymentAllocationSummary` adds `reversedTotal` and `net` and documents the gross `totalAllocated` and net-based `unallocated`. |
| `asyncapi/payment.yaml` | 1.4.0 | Additive | The implemented `payment.allocation.reversed` channel, `send` operation, and `PaymentAllocationReversedData` payload. |
| `asyncapi/event-catalog.yaml` | 1.30.0 | Additive | `payment.allocation.reversed` is published and implemented (212 published and 92 implemented in total; Payment 20 published and 5 implemented). |

The reversal keeps the append-only allocation row: `{reason}` is required,
trimmed, non-blank, and at most 200 characters; the accepted call stamps
`reversedAt`/`reversalReason` and leaves the amount, target, component, and
`createdAt` unchanged. A reversed allocation no longer counts toward the active
allocated total, so its amount can fund a later create. The summary keeps every
row in `items` and splits the reconciliation: `totalAllocated` is the gross sum
of all rows, `reversedTotal` is the sum of the reversed rows, `net` is
`totalAllocated - reversedTotal`, and `unallocated` is `paymentAmount - net`.
The expert owns the totals and the reversal guard; the domain forwards the
tenant, payment, allocation, and reason and preserves the expert's 404 code.

An unknown or foreign payment is 404 `PAYMENT_NOT_FOUND`; an unknown
allocation, an allocation under another payment, or another tenant's allocation
is 404 `ALLOCATION_NOT_FOUND`. A missing, blank, or over-long `reason` is 400
`VALIDATION_ERROR`. Repeating a reversal, including a concurrent repeat, is 409
`ALLOCATION_ALREADY_REVERSED` with no second write and no second event; the
payment lifecycle status does not gate a reversal. An accepted reversal writes
`payment.allocation.reversed` in the same transaction as the stamp: the
`PaymentAllocation` child aggregate moves to version 2 and the payload is
`{paymentId, allocationId, targetType, targetId, component, amount, reason,
reversedAt}`.

The reverse route and event are SPEC-less: SPEC 11.7.11 lists only the
allocation GET and no reversal, and SPEC 11.7.10 publishes no allocation fact.
`MISMATCHES.md` M-22 and M-35 record the extension. The full run passes 14,205
checks.

### Notifications template management (2026-10-22)

Notifications 1.3.0 adds the notification-template registry. The change is
additive: four new operations, four new schemas, and three new event names; no
existing path, request field, response field, or event changes.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/notifications.yaml` | 1.3.0 | Additive | `GET/POST /api/v1/notifications/templates`, `POST /api/v1/notifications/templates/{id}/approve`, `POST /api/v1/notifications/templates/{id}/retire`, and the `NotificationTemplate`, `NotificationTemplateStatus`, `CreateNotificationTemplateRequest`, and `ApproveNotificationTemplateRequest` schemas. |
| `asyncapi/notifications.yaml` | 1.2.0 | Additive | The implemented `notifications.template.created`, `.approved`, and `.retired` channels and operations with the shared `NotificationTemplateData` payload. |
| `asyncapi/event-catalog.yaml` | 1.31.0 | Additive | The three template names are published and implemented (215 published and 95 implemented in total; Notifications 15 published and 5 implemented). |

Semantics:

- A template is created DRAFT by `POST /api/v1/notifications/templates`. The
  body is `{templateCode, templateVersion, channel?, locale, bodyTemplate}`;
  `templateCode` is 1-64 characters, `templateVersion` is at least 1, `channel`
  is optional and null means channel-neutral, `locale` is 1-16 characters, and
  `bodyTemplate` is non-empty. `status`, `approvedBy`, and `approvedAt` are
  never accepted. The domain command also accepts `body` as an alias of
  `bodyTemplate`. The unique key is `(tenant, templateCode, templateVersion,
  locale)`: a duplicate, including a concurrent insert, is 409
  `TEMPLATE_ALREADY_EXISTS` (`EIA-NTF-9205`) with no row and no event.
- `POST /api/v1/notifications/templates/{id}/approve` requires `{approvedBy}`.
  Approval is the only path to ACTIVE (NTF-14) and records the approver and the
  server-assigned instant in `approvedBy` and `approvedAt`. An already-ACTIVE
  template is 409 `TEMPLATE_ALREADY_ACTIVE` (`EIA-NTF-9206`); a RETIRED template
  or a lost concurrent conditional update is 409 `TEMPLATE_STATUS_CONFLICT`
  (`EIA-NTF-9207`).
- `POST /api/v1/notifications/templates/{id}/retire` has no request body and
  moves a DRAFT or ACTIVE template to RETIRED, which is terminal. The approval
  evidence is retained. An already-RETIRED template or a lost concurrent update
  is 409 `TEMPLATE_STATUS_CONFLICT`. A template outside the caller's tenant is
  404, indistinguishable from a missing template.
- `GET /api/v1/notifications/templates` returns a bare JSON array ordered by
  `createdAt` newest first, then `code`, `version` descending, and `id`.
  `status` filters one lifecycle state and `code` filters one exact template
  code; both are optional and trimmed. An unknown `status` is 400
  `INVALID_TEMPLATE_STATUS` (`EIA-NTF-9408`). The tenant is always the required
  `X-EIA-Tenant` header.
- Every accepted write emits one template fact in the same transaction:
  `notifications.template.created` on the DRAFT insert,
  `notifications.template.approved` on the transition to ACTIVE, and
  `notifications.template.retired` on the transition to RETIRED. The
  `NotificationTemplate` aggregate version is 1, 2, and 3 respectively, while
  `eventVersion` stays 1. The payload is `{templateId, code, version, locale,
  status, approvedBy}`; `version` is the template identity version, and
  `approvedBy` is JSON null on a DRAFT create and on a retirement from DRAFT.
- SPEC 11.8.10 mounts template administration at
  `/api/v1/notifications/admin/templates` and names a publish command; the
  implemented short route and its approve/retire commands replace that shape,
  and SPEC 11.8.9 publishes no template event. `MISMATCHES.md` M-22 and M-49
  record the route, command, and event-name differences.
- The validator requires the four operations, the shared tenant header, the
  `status`/`code` list filters, the `NotificationTemplate` and
  `NotificationTemplateStatus` shapes, the create and approve request schemas,
  the DRAFT-on-create rule, the 201/200/400/404/409 responses, the three
  `TEMPLATE_*` conflict codes, the three implemented channels with the shared
  `NotificationTemplateData` payload, and the catalog entries. The full run
  passes 14,465 checks.

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

### Document content contract (2026-10-20)

Document 1.3.0 adds the raw content upload, download, and metadata surface. The
change is additive: three new routes, one new schema, and one new event name; no
existing path, request field, response field, or event changed. Document 1.4.0
extends the same surface with the retained revision history; see
[Document content versions](#document-content-versions-2026-10-21).

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/document.yaml` | 1.3.0 | Additive | `PUT|GET /api/v1/documents/{documentId}/content`, `GET /api/v1/documents/{documentId}/content/metadata`, the `DocumentContent` schema, and the `X-File-Name` and `Content-Type` upload headers. |
| `asyncapi/document.yaml` | 1.3.0 | Additive | The implemented `document.content.uploaded` channel and operation with a `DocumentContentUploadedData` payload. |
| `asyncapi/event-catalog.yaml` | 1.18.0 | Additive | The content name is published and implemented (197 published in total; Document 21 published and 6 implemented; the platform implemented total is 76). |

Content semantics:

- `PUT .../content` is a raw-byte upload. In 1.3.0 it replaced the document's
  single current content row; from 1.4.0 every accepted body is appended as an
  immutable revision while the current row still serves the newest bytes. The
  body is not JSON and is stored unchanged. `Content-Type` is the file MIME type
  and defaults to `application/octet-stream` when omitted; the stored type is
  the bare `type/subtype`. `X-File-Name` is required and is URL-decoded as
  UTF-8; a directory component is removed, a blank name is 400
  `FILE_NAME_REQUIRED`, a name longer than 255 characters is 400
  `FILE_NAME_TOO_LONG`, and a control character is 400 `INVALID_FILE_NAME`. An
  empty body is 400 `EMPTY_CONTENT`.
- A body above 10 MiB (10,485,760 bytes) is 413 `FILE_TOO_LARGE`; the public
  domain rejects it before the expert call, so no content revision or event is
  written. Exactly 10 MiB is accepted. The 413 body is
  `application/problem+json`.
- The 200 response is the `DocumentContent` projection:
  `{documentId, fileName, contentType, sizeBytes, sha256, uploadedAt}`. The
  bytes are deliberately absent from the projection. 1.4.0 adds the required
  `currentVersion`.
- `GET .../content` streams the stored bytes with the stored `Content-Type`,
  an attachment `Content-Disposition` built from the stored filename (with the
  RFC 5987 `filename*` parameter for a non-ASCII name), and
  `X-Content-SHA256` with the lowercase digest of the exact bytes. 1.4.0 adds
  `X-Content-Version` with the revision of the returned bytes. It is a binary
  response and must not be parsed as JSON. There is no presigned URL and no
  `Range` support.
- `GET .../content/metadata` returns the projection without touching the bytes.
- `X-EIA-Tenant` is required on all content routes. A document outside the
  caller's tenant and a document with no stored content are both 404, so the
  response cannot confirm another tenant's document; the latter is 404
  `CONTENT_NOT_FOUND`. The domain forwards the tenant to the expert's public
  content path; the expert also accepts `tenantId` as a fallback.
- An accepted upload writes `document.content.uploaded` to the transactional
  outbox in the same transaction as the revision append. The aggregate is
  `DocumentContent`, keyed by the document id, with the content revision as the
  aggregate version, so replacing the content produces a new event. The name is
  new and has no SPEC 11.6.9 equivalent; M-22 and M-40 record the naming and
  lifecycle gaps.
- The SPEC 11.6.10 presigned download, renditions, OCR text, packages,
  requests, and signatures remain planned and listed under
  `x-planned-operations`. Legal holds and retention disposition are implemented
  from 1.5.0 on the per-document routes described in
  [Document legal holds and disposition](#document-legal-holds-and-disposition-2026-10-21),
  not the SPEC hold collection. Version history is implemented from 1.4.0, but
  under `/content/versions` rather than the SPEC `/versions` route.
- The validator requires the content operations (five from 1.4.0), the tenant
  header and `documentId` parameter, the `X-File-Name` and `Content-Type` upload
  headers, the binary request and response bodies, the `Content-Disposition`,
  `X-Content-SHA256`, and `X-Content-Version` download headers, the
  `DocumentContent` fields and bounds, the 400 `EMPTY_CONTENT` and 413
  `FILE_TOO_LARGE` documentation, the `DocumentContentUploadedData` payload,
  and the implemented channel, operation, and catalog entry. The 1.3.0 run
  passed 12,255 checks.

### Document content versions (2026-10-21)

Document 1.4.0 adds the retained content-revision history. The change is
additive: two new routes, one new schema, one required metadata member, one
required event-payload member, and no new event name; no existing path, request
field, response field, or event is removed or changes meaning.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/document.yaml` | 1.4.0 | Additive | `GET /api/v1/documents/{documentId}/content/versions`, `GET /api/v1/documents/{documentId}/content/versions/{version}`, the `DocumentContentVersion` schema, the required `DocumentContent.currentVersion`, and the `X-Content-Version` download header. |
| `asyncapi/document.yaml` | 1.4.0 | Additive | The `DocumentContentUploadedData` payload gains the required `version` member; `eventVersion` stays 1. |
| `asyncapi/event-catalog.yaml` | 1.21.0 | Additive | No name is added or removed; the totals stay 201 published and 80 implemented (Document 21 published and 6 implemented). |

Version semantics:

- Every accepted `PUT .../content` appends one immutable revision and advances
  the current pointer. Revisions start at 1 and increase by one per accepted
  upload. The first upload and a replacement both create a revision; a failed
  upload writes no revision and no event.
- `GET .../content/versions` returns the revisions as a bare JSON array ordered
  newest first (`version` descending). Each `DocumentContentVersion` is
  `{documentId, version, fileName, contentType, sizeBytes, sha256, uploadedAt}`.
  A document with no stored content has no revisions and returns `[]`; a
  document outside the caller's tenant is 404.
- `GET .../content/versions/{version}` streams the exact bytes of one revision
  with the same representation headers as the current download: the stored
  `Content-Type`, an attachment `Content-Disposition` built from that
  revision's filename, `X-Content-SHA256` with the digest of the returned bytes,
  and `X-Content-Version` repeating the revision. It is a binary response and
  must not be parsed as JSON. There is no presigned URL and no `Range` support.
- `X-EIA-Tenant` is required on both routes. A document outside the tenant is
  404, indistinguishable from a missing document. An unknown revision,
  including a number below 1, is 404 `CONTENT_VERSION_NOT_FOUND`; a non-numeric
  `version` is 400 `INVALID_PARAMETER`. The expert returns the compact
  `CONTENT_VERSION_NOT_FOUND` `ApiError`; the domain preserves the expert's
  400/404 status and exposes it as an `application/problem+json` body.
- `DocumentContent.currentVersion` names the newest revision and is the value in
  the current download's `X-Content-Version` header. `GET .../content/metadata`
  and the upload response both return it.
- The accepted upload's `document.content.uploaded` payload now carries the
  revision as `version` (in addition to `documentId`, `documentNumber`,
  `fileName`, `contentType`, `sizeBytes`, and `sha256`). The revision is also
  the `DocumentContent` aggregate version. The event name, channel, and
  `eventVersion` 1 are unchanged, so no catalog name is added and no subscriber
  needs a new subscription.
- The history is nested under `/content/versions`; SPEC 11.6.10 mounts the
  history at `GET /versions` and the version-creating command at `POST
  /versions`. The upload is the version-creating command in this slice. The
  SPEC path shape and the remaining presigned-download, rendition, OCR,
  package, request, and signature gaps are recorded in M-40; the hold and
  disposition surface is described in
  [Document legal holds and disposition](#document-legal-holds-and-disposition-2026-10-21)
  and M-44.
- The validator requires both version routes, the tenant header and
  `documentId` parameter, the required positive `version` path parameter, the
  `DocumentContentVersion` array and fields, the four binary download headers,
  the `CONTENT_VERSION_NOT_FOUND` and `INVALID_PARAMETER` documentation, the
  `currentVersion` member, the required event-payload `version`, and the absence
  of the implemented version paths from `x-planned-operations`; it also asserts
  that `document.content.uploaded` remains the only `document.content.*` event.
  The full run passes 12,657 checks.

### Document legal holds and disposition (2026-10-21)

Document 1.5.0 adds the per-document legal-hold and retention-disposition
commands. The change is additive: three new routes, one new request schema,
four nullable response members, and three implemented event names; no existing
path, request field, response field, or event name is removed or changes
meaning.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/document.yaml` | 1.5.0 | Additive | `POST /api/v1/documents/{documentId}/hold` with the required `HoldDocumentRequest.reason`, `POST /api/v1/documents/{documentId}/hold/release`, `POST /api/v1/documents/{documentId}/dispose`, and the nullable `Document` members `holdReason`, `heldAt`, `statusBeforeHold`, and `disposedAt`. |
| `asyncapi/document.yaml` | 1.5.0 | Additive | The implemented `document.legal-hold.placed`, `document.legal-hold.released`, and `document.document.disposed` channels and operations with the shared `DocumentLifecycleData` payload. |
| `asyncapi/event-catalog.yaml` | 1.24.0 | Additive | The two legal-hold names are published and implemented and `document.document.disposed` moves into the implemented subset (207 published and 87 implemented in total; Document 23 published and 9 implemented). |

Hold and disposition semantics:

- A hold is placed per document with a required `reason` of 1-500 characters.
  The reason is trimmed and recorded in `holdReason`, the instant in `heldAt`,
  and the prior status in `statusBeforeHold`; the document moves to `ON_HOLD`.
  A hold may be placed from `ACTIVE`, `ARCHIVED`, `CLASSIFIED`, or `SUPERSEDED`.
  The last two are allowed even though the generic lifecycle has no edge to
  `ON_HOLD`. A second hold is 409 `DOCUMENT_ALREADY_ON_HOLD`; any other status
  is 409 `HOLD_STATUS_NOT_ALLOWED`.
- A release has no request body. It clears the three hold members and restores
  `statusBeforeHold`; an absent or unrecognised snapshot restores `ARCHIVED`, so
  a release always lands in a retrievable non-active state. A document that is
  not `ON_HOLD` is 409 `DOCUMENT_NOT_ON_HOLD`.
- Disposition is synchronous and requires an expired retention date and no
  active hold. A missing `retentionUntil` is 409 `RETENTION_DATE_REQUIRED`, a
  date after today is 409 `RETENTION_NOT_EXPIRED`, `ON_HOLD` is 409
  `DOCUMENT_ON_LEGAL_HOLD` (checked before the retention clock), and a status
  outside `ACTIVE`, `ARCHIVED`, or `SUPERSEDED` is 409
  `DISPOSAL_STATUS_NOT_ALLOWED`. The accepted command tombstones the document as
  `DISPOSED`, stamps `disposedAt`, keeps the metadata readable, and writes no
  content deletion.
- The public dispose command accepts no body, so the expert's optional
  `{reason}` is not forwarded and the recorded event reason is
  `RETENTION_EXPIRED`. The hold, release, and dispose writes each bump the
  document version and append their event in the same transaction; a rejected
  command writes no row change and no event.
- `X-EIA-Tenant` is required on all three routes; another tenant's document is
  404, indistinguishable from a missing document. The expert also accepts the
  `tenantId` query parameter as a fallback for the domain call.
- The accepted hold writes `document.legal-hold.placed` with
  `{documentId, documentNumber, reason, status: ON_HOLD}`; a release writes
  `document.legal-hold.released` with the lifted reason and the restored status;
  a disposition writes `document.document.disposed` with the disposition reason
  and `status: DISPOSED`. All three use the `Document` aggregate and the row
  version + 1. The two legal-hold names are new with no SPEC 11.6.9 equivalent:
  the SPEC facts are `document.document.held` and
  `document.document.hold-released`, which remain planned.
  `document.document.disposed` is a SPEC name and is now implemented.
- The implemented hold is the per-document `.../{documentId}/hold` surface, not
  the SPEC 11.6.10 hold collection with scope, approval, and release by hold id.
  Disposition has no approval step, retention-scan job, disposition certificate,
  or content deletion (SPEC 11.6.8). `MISMATCHES.md` M-44 records the deviation;
  the naming gap is also in M-22.
- The validator requires the three operations with the shared `TenantHeader` and
  `documentId` parameter, the `HoldDocumentRequest.reason` bounds, the 200
  `Document` response, the 400/404/409 responses, all seven conflict codes, the
  four nullable `Document` members, the `DocumentLifecycleData` payload, and the
  three implemented channels, operations, and catalog entries. It also asserts
  that the implemented paths leave `x-planned-operations` and that the SPEC
  `document.document.held`/`.hold-released` channels stay planned. The full run
  passes 13,501 checks.

### Document content tombstones (2026-10-22)

Document 1.6.0 adds the standalone content tombstone. The change is additive:
one new route, two always-serialized metadata members, two 410 responses, and
one implemented event name; no existing path, request field, response field, or
event name is removed or changes meaning.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/document.yaml` | 1.6.0 | Additive | `DELETE /api/v1/documents/{documentId}/content`, the `DocumentContent.deletedAt` and `deleted` members, and 410 `CONTENT_DELETED` on the current and revision downloads. |
| `asyncapi/document.yaml` | 1.6.0 | Additive | The implemented `document.content.deleted` channel and `send` operation with a `DocumentContentDeletedData` payload. |
| `asyncapi/event-catalog.yaml` | 1.28.0 | Additive | The name is published and implemented (211 published and 91 implemented in total; Document 24 published and 10 implemented). |

Tombstone semantics:

- `DELETE .../content` is a tombstone, not a row delete. It clears the bytes of
  the current pointer and of every not-yet-tombstoned revision and records
  `deletedAt`; `fileName`, `contentType`, `sizeBytes`, `sha256`, `uploadedAt`,
  and `currentVersion` stay readable. Success is 204 with no body.
- `X-EIA-Tenant` is required. A document with no stored content is 404
  `CONTENT_NOT_FOUND`; a missing document and another tenant's document are 404
  `NOT_FOUND`, indistinguishable from each other.
- A document under an active legal hold is 409 `DOCUMENT_ON_LEGAL_HOLD` and is
  left untouched (SPEC DOC-06). Repeating a delete is 409
  `CONTENT_ALREADY_DELETED`; the stored `deletedAt` is checked before the hold,
  so a repeated delete on a held document reports already deleted. Neither
  conflict writes a row change or an event.
- The accepted delete appends `document.content.deleted` in the same transaction
  as the byte clear. The aggregate is `DocumentContent`, keyed by the document
  id, and the aggregate version is the current revision that was tombstoned;
  `eventVersion` stays 1.
- The current download and every revision download answer 410
  `CONTENT_DELETED` for tombstoned bytes. `GET .../content/metadata` still
  answers 200 with the retained metadata, `deleted: true`, and the tombstone
  instant. The history still lists every revision.
- A later upload clears the tombstone on the current pointer and appends a
  fresh, downloadable revision; the earlier revisions keep their deletion
  timestamps and remain 410 on download.
- SPEC 11.6.8 deletes content as a step of the approved disposition job, and
  SPEC 11.6.9 names no content-tombstone event. The implemented standalone
  command carries no approval or disposition certificate. The 1.7.0
  disposition-content slice later makes a disposition apply the same tombstone
  (see the next section); M-40, M-44, and M-47 record the deviation. M-22
  records the new name.
- The validator requires the delete operation with the shared `TenantHeader`,
  the `documentId` parameter, the 204 response and no request body, the 404
  `CONTENT_NOT_FOUND` and 409 `DOCUMENT_ON_LEGAL_HOLD`/
  `CONTENT_ALREADY_DELETED` documentation, the `DocumentContent.deletedAt` and
  `deleted` members, the 410 responses on both downloads, the implemented
  `document.content.deleted` channel and its exact six-member payload, and the
  catalog published and implemented entries. The full run passes 14,058 checks.

### Document disposition content tombstone (2026-10-22)

Document 1.7.0 couples content tombstoning to retention disposition. The change
is additive on the wire: `POST /api/v1/documents/{documentId}/dispose` keeps its
200 `Document` response and its request and response schemas, but a successful
disposition of a document with live content now also clears the content bytes
and emits `document.content.deleted` in the same transaction as
`document.document.disposed`. No path, request field, response field, or event
name is removed or changes meaning.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/document.yaml` | 1.7.0 | Additive | `POST .../dispose` now tombstones live content and emits `document.content.deleted` beside `document.document.disposed`; the dispose, download, metadata, and `deletedAt` descriptions record the shared tombstone. |
| `asyncapi/document.yaml` | 1.7.0 | Additive | The `document.document.disposed` and `document.content.deleted` channel descriptions record that one disposition may emit both facts; no event name or payload changes. |
| `asyncapi/event-catalog.yaml` | 1.29.0 | Additive | No new name: the already-published `document.content.deleted` is now also emitted by a disposition (211 published and 91 implemented in total; Document 24 published and 10 implemented). |

Disposition coupling semantics:

- A disposition first applies the existing gates: an expired retention date, no
  active legal hold, and a status in `ACTIVE`, `ARCHIVED`, or `SUPERSEDED`.
  `ON_HOLD` is checked before the retention clock, so a held document is 409
  `DOCUMENT_ON_LEGAL_HOLD` and its bytes remain downloadable.
- If the document still has live stored content, the same transaction clears the
  bytes of the current pointer and of every not-yet-tombstoned revision, records
  `deletedAt`, and appends `document.content.deleted` with the same payload as an
  explicit content delete: `{documentId, documentNumber, fileName, sizeBytes,
  sha256, deletedAt}`, aggregate `DocumentContent` at the tombstoned revision,
  `eventVersion` 1. It also appends `document.document.disposed` at the Document
  aggregate, row version + 1.
- A document with no stored content, or whose content is already tombstoned, is
  disposed normally with only `document.document.disposed`. Disposition does not
  answer 404 `CONTENT_NOT_FOUND` or 409 `CONTENT_ALREADY_DELETED`; those remain
  specific to the explicit `DELETE .../content` command. The disposition
  response stays 200 with the DISPOSED document.
- The transaction is atomic: a rejected disposition writes no document row, no
  content change, and no event, and a tombstone or outbox failure rolls back the
  disposition as well.
- The standalone `DELETE .../content` command is unchanged, including its 204,
  the `CONTENT_NOT_FOUND`/`CONTENT_ALREADY_DELETED` conflicts, and the legal-hold
  block. A later upload still clears the pointer tombstone and appends a fresh
  downloadable revision.
- Downloads of the current bytes and of any revision are 410 `CONTENT_DELETED`
  after a disposition, and `GET .../content/metadata` still answers 200 with the
  retained metadata, `deleted: true`, and `deletedAt`.
- SPEC 11.6.8 deletes content inside an approved asynchronous disposition job
  with a disposition certificate. The implemented disposition is synchronous and
  has neither approval nor certificate; the deletion step and the event are now
  implemented, but the workflow deviation remains M-44/M-47. M-40 records the
  content-store shape.
- The validator requires the dispose description to name both events and the
  no-content/already-tombstoned no-op, forbids the explicit delete's
  404/409 vocabulary on the disposition conflicts, requires the disposition
  reference on both content downloads, the metadata description, and
  `DocumentContent.deletedAt`, and requires the disposed and content-deleted
  channel descriptions. The full run passes 14,088 checks.

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
- Billing account, billing instructions, disputes, and commission statements
  from SPEC 11.2.13 remain unimplemented (M-12, M-27); policy credit notes and
  the installment dunning history are separate surfaces documented below. The
  cross-policy premium-receivables queue is the next section.

### Policy premium receivables contract (2026-10-20)

Policy 2.5.0 adds the cross-policy premium-receivables queue. The change is
additive: the route and the two schemas are new, and no existing path, request
field, response field, or event changed.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.5.0 | Additive | `GET /api/v1/billing/installments`, the `Receivable` and `ReceivableSummary` schemas, and the DUE/OVERDUE, `dueBefore`, and 1..200 `limit` rules. |

Queue semantics:

- The route is **outside `/api/v1/policies`** because it is not scoped to one
  policy. It joins the tenant's billing plans, installments, policies, and
  insured parties; a client must not expect a `policyId` path parameter. The
  gateway maps `/api/v1/billing/**` to the Policy domain.
- The response is the bare `ReceivableSummary`: `items[]`, `totalAmount`,
  `overdueAmount`, and `count`. Each `Receivable` is `{installmentId, planId,
  planNumber, policyId, policyNumber, insuredPartyId, installmentNumber,
  dueDate, amount, currency, status, daysPastDue, paidAt, paymentId}`;
  `amount`, `totalAmount`, and `overdueAmount` are decimal strings, and
  `installmentNumber` and `daysPastDue` are integers.
- Only unsettled installments are returned, so `status` is DUE or OVERDUE and
  `paidAt` and `paymentId` are null. `totalAmount` sums every returned item;
  `overdueAmount` sums the effective OVERDUE subset; `count` is `items.length`.
  OVERDUE is derived at read time: a stored DUE row whose due date has passed is
  reported as OVERDUE with a positive `daysPastDue` without mutating the row.
- `status` is optional, trimmed, and upper-cased; any value other than DUE or
  OVERDUE is 400 `INVALID_INSTALLMENT_STATUS`. `dueBefore` is an inclusive
  `dueDate` cutoff. `limit` defaults to 20 and must be 1..200; a non-integer is
  400 `INVALID_PARAMETER` and an out-of-range integer is 400
  `VALIDATION_ERROR`. A missing or malformed tenant is 400.
- `X-EIA-Tenant` is required. `X-EIA-Book` is optional for compatibility with
  the other Policy proxy routes, but a supplied value must be DIRECT; another
  book is hidden as 404 `BOOK_SCOPE_VIOLATION`. Items are ordered by `dueDate`,
  then `policyNumber`, `installmentNumber`, and `installmentId`.
- The route is read-only and writes no event. SPEC 11.2.13 describes the
  per-policy installment plan rather than a cross-policy receivable resource;
  M-27 records this route and projection deviation alongside the still-missing
  billing-account, dispute, and commission-statement surfaces.

### Policy installment dunning contract (2026-10-20)

Policy 2.7.0 adds the per-installment dunning history and command. The change
is additive: the two operations and the two schemas are new, and the two
receivable members are nullable and absent until the first action is recorded.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.7.0 | Additive | `GET/POST /api/v1/billing/installments/{installmentId}/dunning`, the `DunningAction` and `CreateDunningRequest` schemas, and the nullable `Receivable.lastDunningLevel` and `Receivable.lastDunningAt` members. |
| `asyncapi/policy.yaml` | 1.5.0 | Additive | The implemented `policy.dunning.sent` channel and `send` operation with the `PolicyDunningSentData` payload. |
| `asyncapi/event-catalog.yaml` | 1.16.0 | Additive | `policy.dunning.sent` is published and implemented (194 published in total; Policy 24 published and 12 implemented). |

Dunning semantics:

- `GET .../dunning` returns the installment's recorded actions newest first
  (`sentAt`, then record time, then `dunningId`) and an empty array when none
  exists. The read applies the tenant wall through the installment, its plan,
  and its policy, and writes no event.
- `POST .../dunning` records one action with 201. `level` is `REMINDER`,
  `FIRST_NOTICE`, `SECOND_NOTICE`, or `COLLECTIONS`; `channel` is `EMAIL`,
  `LETTER`, or `PORTAL`. Both are trimmed and upper-cased, and an unknown value
  is 400 `INVALID_DUNNING_LEVEL` or `INVALID_DUNNING_CHANNEL`. `notes` is
  optional, trimmed, treated as absent when blank, and capped at 2000
  characters (400 `INVALID_DUNNING_NOTES`). A missing or blank `level` or
  `channel` is 400 `VALIDATION_ERROR`.
- Only an effective DUE or OVERDUE installment is dunnable. A stored DUE row
  past its due date is effectively OVERDUE and stays dunnable; a PAID or WAIVED
  installment is 409 `INSTALLMENT_NOT_DUNNABLE`. One action per escalation
  level is allowed per installment, so a repeated level is 409
  `DUNNING_ALREADY_SENT`; the unique `(tenantId, installmentId, level)` row is
  the concurrency arbiter. Neither conflict writes a row or an event.
- An unknown installment, another tenant's installment, or a non-DIRECT book is
  404 (`INSTALLMENT_NOT_FOUND` or `BOOK_SCOPE_VIOLATION`); the domain currently
  accepts an absent book header (M-38). A malformed tenant or `installmentId` is
  400 `INVALID_PARAMETER`; a missing tenant is 400 `MISSING_TENANT_HEADER`.
- The accepted action bumps the policy row version and writes
  `policy.dunning.sent` in the same transaction. The command accepts no
  `Idempotency-Key` or `If-Match`; the per-level uniqueness is the retry guard
  (M-06, M-07).
- SPEC 11.2.13 defines no public dunning route or `policy.dunning.sent` name:
  it models dunning as an internal `POST .../dunning-status` command over the
  SAP-sourced `billing_account` level and publishes
  `policy.billing.dunning-changed`. The implemented level/vocabulary and route
  are recorded in M-38; the event naming gap is also in M-22.
- The two receivable members summarize the latest `SENT` action only;
  `CANCELLED` history never contributes. Both are null until the installment is
  first dunned.

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
  skipped or repeated edge is 409 `INVALID_STATUS_TRANSITION`. A `SETTLED`
  transition requires a settlement `reference`; the expert trims it, requires a
  non-whitespace character, and caps it at 120 characters (400
  `INVALID_REFERENCE`), while `ISSUED` ignores it. Each accepted
  transition writes `contract.technical-account.issued` or `.settled` in the
  same transaction as the row update.
- `X-EIA-Tenant` is required. The canonical contract requires
  `X-EIA-Book: ASSUMED`; another book is hidden as 404
  `BOOK_SCOPE_VIOLATION`. The domain currently accepts an absent header for
  compatibility with the other Contract proxy routes, which M-29 records.
- The projection is `{accountId, accountNumber, contractId, periodStart,
  periodEnd, currency, cededPremium, cededLosses, commission, otherCharges,
  balance, status, settlementReference, createdAt}`. `settlementReference` is
  null until the account is SETTLED and then holds the trimmed payment
  reference. `tenantId` is not part of the public projection. Settlement
  references extend this projection from 4.5.0; see Contract technical-account
  settlement references. The SPEC 11.3.4 `technical_account_line` breakdown is
  implemented from 4.2.0 and expanded to the 13 detail types in 4.3.0 (see the
  next section); the `AGREED`, `DISPUTED`, and `SUPERSEDED` statuses and the
  SPEC 11.3.10
  `/accounts` path remain gaps (M-29).
- The three event names are child-aggregate facts with no SPEC 11.3.9
  equivalent (M-22, M-29). The envelope uses the account id and its lifecycle
  version (1, 2, 3) while the outbox partition key stays the contract id. The
  settled payload carries `settlementReference`; `created` and `issued` omit
  it.

### Contract technical-account lines (2026-10-21)

Contract 4.3.0 expands the financial line detail behind the technical-account
header to the 13 SPEC 11.3.4 detail types. The two paths, the four bucket
totals, and the line projection are unchanged. The `TechnicalAccountLineType`
enum gains the detail values and drops the interim aggregate `LOSS`, and
`LineSummary.totals` gains an optional per-line-type `details` map. The issue
guard is rebuilt on the four buckets: a DRAFT account that has lines can be
issued only when every bucket total equals its matching header amount.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/contract.yaml` | 4.3.0 | Additive | `TechnicalAccountLineType` enumerates the 13 SPEC 11.3.4 detail types (the retired aggregate `LOSS` is removed); `TechnicalAccountLineTotals` keeps the four required bucket members and adds the optional `details` map of the 13 types; the `LineSummary`, totals, and account status descriptions document the bucket-to-header mapping and the expert `bucketTotals` normalization; the issue reconciliation compares bucket sums with the header components. |
| `asyncapi/contract.yaml` | 1.8.0 | Additive | The `ContractTechnicalAccountLineData.lineType` enum carries the 13 detail types; no channel, operation, or event name changes. |
| `asyncapi/event-catalog.yaml` | 1.23.0 | No change | No event name is added or removed; the catalog totals stay 205 published and 84 implemented (Contract 32 published and 19 implemented). |

Line semantics:

- `GET .../lines` returns `items` in insertion order (`createdAt`, then line
  id) and `totals` with the four buckets `premium`, `loss`, `commission`, and
  `other`. All four are always present, as decimal strings, and a bucket with
  no line is `0.0000`. `totals.details` is optional: it maps each present line
  type to its summed amount, has only the 13 `TechnicalAccountLineType` keys,
  and is omitted when empty. The expert returns an authoritative `bucketTotals`
  map with the same four keys; the domain normalizes it into the public buckets
  and, when it is absent, derives the buckets from the detailed totals or the
  line rows. The account projection does not embed the lines.
- `POST .../lines` records one line and returns 201. `lineType` is required and
  is one of `PREMIUM`, `COMMISSION`, `BROKERAGE`, `PAID_LOSS`,
  `OUTSTANDING_LOSS`, `IBNR`, `ALAE`, `REINSTATEMENT`, `CASH_CALL`,
  `FUNDS_WITHHELD`, `TAX`, `ADJUSTMENT`, or `OTHER` (trimmed and
  case-insensitive). The retired aggregate `LOSS` is rejected with 400
  `INVALID_LINE_TYPE`; post `PAID_LOSS` instead. `amount` is required and must be strictly positive.
  `reference` (at most 64 characters) and `description` (at most 255) are
  optional, trimmed, and null when absent. The line id and `createdAt` are
  server-derived and are not accepted in the body.
- `DELETE .../lines/{lineId}` removes one line and returns 204 with no body.
  The line lookup is scoped by tenant, contract, and account, so an unknown
  line, a line under another account, and another tenant's record are all 404.
- Lines can be added and removed only while the account is DRAFT. An ISSUED or
  SETTLED account is 409 `ACCOUNT_NOT_EDITABLE`. A line does not change the
  header amounts; it is the audit detail that must reconcile to them.
- **Reconciliation on issue.** `PATCH .../{accountId}/status` to `ISSUED`
  reconciles the line detail when at least one line exists. The lines roll into
  four buckets and each bucket total must equal its header component:
  `premium` -> `cededPremium`, `loss` -> `cededLosses`, `commission` ->
  `commission`, and `other` -> `otherCharges`. The mapping is `PREMIUM` ->
  `premium`; `PAID_LOSS`, `OUTSTANDING_LOSS`, `IBNR`, `ALAE`,
  `REINSTATEMENT`, and `CASH_CALL` -> `loss`; `COMMISSION` and `BROKERAGE` ->
  `commission`; and `FUNDS_WITHHELD`, `TAX`, `ADJUSTMENT`, and `OTHER` ->
  `other`. Any mismatch rejects the transition with 409
  `ACCOUNT_LINES_DO_NOT_RECONCILE`, carrying one `details[]` entry per
  offending bucket (field `PREMIUM`, `LOSS`, `COMMISSION`, or `OTHER`) whose
  message names the contributing line types; the account stays DRAFT and no
  event is written. The account row lock makes the reconciliation and the
  status write atomic with respect to a concurrent line add or delete. An
  account with no lines (a header-only account, including one created or linked
  by a processed period bordereau) remains issuable. The rule applies only at
  DRAFT -> ISSUED; SETTLED changes no line.
- The line projection is `{lineId, accountId, lineType, reference, description,
  amount, createdAt}`; `tenantId` is not exposed and the expert's `id` is
  remapped to `lineId` by the domain. Money is a decimal string (SPEC 10.3).
- `X-EIA-Tenant` is required. The canonical contract requires
  `X-EIA-Book: ASSUMED`; another book is hidden as 404
  `BOOK_SCOPE_VIOLATION`. The domain currently accepts an absent header for
  compatibility with the other Contract proxy routes (M-29, M-42).
- Both line facts are grandchild-aggregate events written through the
  transactional outbox in the same transaction as the line row. The envelope
  uses the line id and aggregate version 1 while the outbox partition key stays
  the contract id. The payload is `{contractId, accountId, lineId, lineType,
  amount}`; `lineType` now carries the 13 detail types and never the retired
  `LOSS`. The optional reference and description are not carried. The names
  are new and have no SPEC 11.3.9 equivalent (M-22, M-42).
- The remaining SPEC 11.3.4 gaps are a line update or correction, a per-line
  currency, a line-level source document, and per-line approval or duplicate
  detection; negative or zero lines are also rejected. The domain accepts a
  300-character description but the expert caps it at 255, so the effective
  bound is 255. M-42 records these gaps.
- `python scripts/validate_contracts.py` passes 13,190 checks with 0 failures.

### Contract technical-account settlement references (2026-10-21)

Contract 4.5.0 documents the settlement reference that closes a technical
account. The change is additive: the status PATCH body gains an optional
`reference`, the `TechnicalAccount` projection gains a nullable
`settlementReference`, and the settled event payload gains the recorded
reference. No route, schema name, response status, or event name changes.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/contract.yaml` | 4.5.0 | Additive | `UpdateTechnicalAccountStatusRequest` adds optional nullable `reference`; `TechnicalAccount` adds the required-but-nullable `settlementReference`; the status PATCH documents the SETTLED reference gate and 400 `INVALID_REFERENCE`. |
| `asyncapi/contract.yaml` | 1.10.0 | Additive | `ContractTechnicalAccountData` adds the optional `settlementReference` property, present only on `contract.technical-account.settled`; `eventVersion` stays 1. |
| `asyncapi/event-catalog.yaml` | 1.26.0 | No change | No event name, channel, or count changes. |

Settlement-reference semantics:

- `PATCH .../{accountId}/status` takes `{status, reference?}`. `reference` is
  meaningful only for `SETTLED`: the expert trims it, requires at least one
  non-whitespace character, and caps it at 120 characters. A missing, blank, or
  over-long reference is 400 `INVALID_REFERENCE`; the account stays ISSUED and
  no settled event is written. `ISSUED` ignores a supplied reference, and the
  domain drops it before forwarding that transition.
- `TechnicalAccount.settlementReference` is always present but null until the
  account settles; it then holds the trimmed reference. The public projection
  still omits `tenantId`, and the expert row id is still remapped to
  `accountId`.
- `contract.technical-account.settled` carries `settlementReference` in its
  payload. `contract.technical-account.created` and `.issued` omit the member,
  and the settled fact keeps `eventVersion` 1. The reference is evidence
  recorded by the Contract expert; Payment and FS-RI still own execution and
  the actual payment record (SPEC 11.3.11, M-29).
- The validator requires the nullable 120-character projection member, the
  optional nullable 120-character status `reference`, its conditional
  non-blank SETTLED requirement, the 400 `INVALID_REFERENCE` documentation,
  the optional settled-event payload member, and the channel description that
  says the created and issued facts omit it. The full run passes 13,688 checks.

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

### Contract cash calls (2026-10-20)

Contract 3.1.0 adds the interim cash-call funding request for an ASSUMED
treaty. The change is additive: the three operations and four schemas are new,
the three event names are new, and no existing path, request field, response
field, or event changed. `contract.cash-call.issued` was already published and
moves into the implemented subset.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/contract.yaml` | 3.1.0 | Additive | `GET/POST /api/v1/contracts/{contractId}/cash-calls`, `PATCH /api/v1/contracts/{contractId}/cash-calls/{cashCallId}/status`, and the `CashCall`, `CashCallStatus`, `CreateCashCallRequest`, and `UpdateCashCallStatusRequest` schemas. |
| `asyncapi/contract.yaml` | 1.4.0 | Additive | Four implemented child-aggregate channels and `send` operations: `contract.cash-call.requested`, `.issued`, `.settled`, and `.cancelled`. |
| `asyncapi/event-catalog.yaml` | 1.13.0 | Additive | Three requested/terminal names are published and all four join the Contract implemented subset (192 published in total; Contract 29 published and 15 implemented). |

Cash-call semantics:

- `GET .../cash-calls` returns a bare array of the contract's cash calls,
  newest first (`createdAt` descending, then `callNumber` descending). The
  tenant comes from `X-EIA-Tenant`; an unknown contract, another tenant's
  contract, or a cash call under another contract is 404.
- `POST .../cash-calls` creates the row in REQUESTED. `periodStart` must be
  before `periodEnd`, `amount` must be greater than zero, `currency` must be an
  uppercase ISO 4217 code, `dueDate` is required, and `notes` is optional and
  capped at 4000 characters. `callNumber` is generated as
  `CC-{year}-{sequence}` and the initial REQUESTED status is server-derived;
  neither is accepted from the caller. Call numbers are unique per tenant and
  contract, so a duplicate is 409 `DUPLICATE_CASH_CALL_NUMBER`.
- `PATCH .../{cashCallId}/status` applies only
  `REQUESTED -> ISSUED`, `REQUESTED -> CANCELLED`, or `ISSUED -> SETTLED`. The
  request enum is `ISSUED`, `SETTLED`, or `CANCELLED`; `REQUESTED` is the
  creation state and is 400 `INVALID_STATUS`, and a skipped, repeated, or
  terminal edge is 409 `INVALID_STATUS_TRANSITION`. Both terminal statuses are
  immutable.
- The public projection is `{cashCallId, callNumber, contractId, periodStart,
  periodEnd, amount, currency, dueDate, status, notes, createdAt}`. The expert
  row id is serialized as `id` internally and remapped to `cashCallId` by the
  domain; `tenantId` is not part of the public projection. Money is a decimal
  string (SPEC 10.3). Settlement references extend this projection from 4.4.0;
  see Contract cash-call settlement references.
- `X-EIA-Tenant` is required. The canonical contract requires
  `X-EIA-Book: ASSUMED`; another book is hidden as 404
  `BOOK_SCOPE_VIOLATION`. The domain currently accepts an absent header for
  compatibility with the other Contract proxy routes, and the expert's
  `/internal/v1` alias does not check the book, which M-34 records.
- Every accepted write appends its event in the same transaction as the row
  change: `contract.cash-call.requested` on create, then `.issued`, `.settled`,
  or `.cancelled`. The envelope uses the cash-call id and aggregate version 1
  (requested), 2 (issued or cancelled), or 3 (settled) while the outbox
  partition key stays the contract id. SPEC 11.3.9 publishes only
  `contract.cash-call.issued`; the other three names are new child facts
  (M-22, M-34).
- A cash call is not a Payment: Payment and FS-RI own execution and settlement
  (SPEC 11.3.11). The implemented slice has no cash-call limit or
  `cash_call_allowed` term check, no contract-window or contract-currency
  reconciliation, and no claim/Payment link, so the SPEC "large loss above the
  cash-loss limit" gate and the SPEC 11.3.10 routes remain gaps (M-34).

### Contract cash-call settlement references (2026-10-21)

Contract 4.4.0 documents the settlement reference that closes a cash call. The
change is additive: the status PATCH body gains an optional `reference`, the
`CashCall` projection gains a nullable `settlementReference`, and the settled
event payload gains the recorded reference. No route, schema name, response
status, or event name changes.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/contract.yaml` | 4.4.0 | Additive | `UpdateCashCallStatusRequest` adds optional nullable `reference`; `CashCall` adds the required-but-nullable `settlementReference`; the status PATCH documents the SETTLED reference gate and 400 `INVALID_REFERENCE`. |
| `asyncapi/contract.yaml` | 1.9.0 | Additive | `ContractCashCallData` adds the optional `settlementReference` property, present only on `contract.cash-call.settled`; `eventVersion` stays 1. |
| `asyncapi/event-catalog.yaml` | 1.25.0 | No change | No event name, channel, or count changes. |

Settlement-reference semantics:

- `PATCH .../{cashCallId}/status` takes `{status, reference?}`. `reference` is
  meaningful only for `SETTLED`: the expert trims it, requires at least one
  non-whitespace character, and caps it at 120 characters. A missing, blank, or
  over-long reference is 400 `INVALID_REFERENCE`; the row stays ISSUED and no
  settled event is written. `ISSUED` and `CANCELLED` ignore a supplied
  reference, and the domain drops it before forwarding those transitions.
- `CashCall.settlementReference` is always present but null until the call
  settles; it then holds the trimmed reference. The public projection still
  omits `tenantId`, and the expert row id is still remapped to `cashCallId`.
- `contract.cash-call.settled` carries `settlementReference` in its payload.
  `contract.cash-call.requested`, `.issued`, and `.cancelled` omit the member,
  and the settled fact keeps `eventVersion` 1. The reference is evidence
  recorded by the Contract expert; Payment and FS-RI still own execution and
  the actual payment record (SPEC 11.3.11, M-34).
- The validator requires the nullable 120-character projection member, the
  optional nullable 120-character status `reference`, its conditional
  non-blank SETTLED requirement, the 400 `INVALID_REFERENCE` documentation,
  the optional settled-event payload member, and the channel description that
  says the other cash-call facts omit it. The full run passes 13,576 checks.

### Contract security/collateral contract (2026-10-20)

Contract 4.0.0 replaces the public security/collateral projection and command
with the implemented public surface. The change is breaking for a generated
client of the old public `Security` shape; the internal expert keeps the wide
row schema and the bind-slice `CreateSecurityRequest`.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/contract.yaml` | 4.0.0 | Breaking | `GET/POST /api/v1/contracts/{contractId}/security` now use the ten-field `SecurityRecord` response, the `CreateContractSecurityRequest` body, required `X-EIA-Tenant` and `X-EIA-Book: ASSUMED`, and the 201/400/404/409 responses. The wide `Security` and `CreateSecurityRequest` schemas remain on `/internal/v1`. |
| `asyncapi/contract.yaml` | 1.5.0 | Additive | `contract.security.recorded` becomes an implemented channel and `send` operation with a `ContractSecurityData` payload. |
| `asyncapi/event-catalog.yaml` | 1.15.0 | Additive | `contract.security.recorded` moves into the Contract implemented subset. It was already published, so the platform total stays 193 published names; Contract is 29 published and 16 implemented, and the platform implemented total is 72. |

Security semantics:

- The projection is exactly `{id, securityType, requiredAmount, heldAmount,
  currency, providerPartyId, expiryDate, approvalRef, status, createdAt}`. The
  tenant, contract, beneficiary, effective dates, collateral quality, document,
  release conditions, and audit columns are internal-only. Money is a decimal
  string (SPEC 10.3); `providerPartyId`, `expiryDate`, and `approvalRef` are
  nullable.
- The request accepts `securityType`, `requiredAmount`, optional `heldAmount`,
  `currency`, optional `providerPartyId`, `expiryDate`, `approvalRef`, and
  `approvedAt`. `securityType` is the seven-value closed set
  (`LETTER_OF_CREDIT`, `TRUST_FUND`, `FUNDS_WITHHELD`, `CASH_ADVANCE`,
  `PARENT_GUARANTEE`, `BANK_GUARANTEE`, `SECURITIES`); `requiredAmount` must be
  greater than zero; `heldAmount` defaults to `0.0000`; `currency` is required
  and must match the contract currency.
- The expert derives the status: `EXPIRED` when `expiryDate` is before today,
  otherwise `ACTIVE`. `status` is not a request field. The response enum also
  carries the bind-slice values `REQUIRED`, `OUTSTANDING`, `PARTIAL`,
  `RELEASED`, and `BREACH`, because the list returns every row on the contract,
  including rows written through the internal expert surface; `OUTSTANDING`
  exists in the implemented internal lifecycle even though the public create
  never derives it.
- Over-collateralisation is guarded: `heldAmount` above `requiredAmount`
  without `approvalRef` is 409 `COLLATERAL_EXCEEDS_OBLIGATION`; with a
  reference but no `approvedAt` it is 409 `COLLATERAL_APPROVAL_INCOMPLETE`. A
  currency that differs from the contract is 409
  `SECURITY_CURRENCY_MISMATCH`. The contract must be `DRAFT`, `QUOTED`,
  `PLACED`, or `BOUND`; another state is 409 `CONTRACT_LOCKED`. Invalid fields
  are 400 (`INVALID_SECURITY_TYPE`, `INVALID_REQUIRED_AMOUNT`,
  `INVALID_HELD_AMOUNT`, `INVALID_CURRENCY`, `INVALID_APPROVAL_REF`,
  `MISSING_TENANT`). An unknown or other-tenant contract is 404 `NOT_FOUND`.
- `X-EIA-Tenant` is required. The canonical contract requires
  `X-EIA-Book: ASSUMED`; another book is hidden as 404
  `BOOK_SCOPE_VIOLATION`. The domain currently accepts an absent header for
  compatibility with the other Contract proxy routes, which M-37 records.
- The create writes `contract.security.recorded` in the same transaction as the
  row. The event is a child aggregate: it uses the security id and aggregate
  version 1 while the outbox partition key stays the contract id. The payload
  is `{contractId, securityId, securityType, requiredAmount, heldAmount,
  currency, status}`; it deliberately omits the contract number, provider,
  approval reference, and expiry date.
- The implemented route keeps the short M-01 form and the SPEC 11.3.10 table
  uses `/api/v1/contract/contracts/{contractId}/security`. The SPEC 11.3.4
  status enum has no `ACTIVE` and the request is narrower than the SPEC
  `contract_security` columns. The public status action added in 4.1.0 is
  documented in the next section; M-37 records the remaining gaps.

### Contract security status action (2026-10-20)

Contract 4.1.0 adds the security/collateral status action. The change is
additive: one new path and one request schema; no existing path, request field,
response field, or event changed. The event name is new and adds one published
and one implemented catalog name.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/contract.yaml` | 4.1.0 | Additive | `PATCH /api/v1/contracts/{contractId}/security/{securityId}/status` and the `UpdateContractSecurityStatusRequest` schema (`status`: `RELEASED` or `EXPIRED`); the 200 `SecurityRecord` and 400/404/409 responses. |
| `asyncapi/contract.yaml` | 1.6.0 | Additive | The implemented `contract.security.status-changed` channel and `send` operation with a `ContractSecurityStatusChangedData` payload. |
| `asyncapi/event-catalog.yaml` | 1.19.0 | Additive | `contract.security.status-changed` is published and implemented (198 published in total; Contract 30 published and 17 implemented; the platform implemented total is 77). |

Status semantics:

- The body is `{status}`. Only `RELEASED` and `EXPIRED` are accepted; the value
  is trimmed and upper-cased, and any other target is 400 `INVALID_STATUS`
  (including `BREACH`, which is not a lifecycle action).
- A live record in `ACTIVE`, `OUTSTANDING`, `PARTIAL`, or `REQUIRED` can move to
  `RELEASED` or `EXPIRED`; an `EXPIRED` record can still move to `RELEASED`.
  `RELEASED` is terminal, so a repeated release or any action on a released
  record is 409 `INVALID_STATUS_TRANSITION`. A `BREACH` record cannot be
  released or expired; that is also 409 `INVALID_STATUS_TRANSITION`.
- The record is tenant- and contract-scoped. An unknown contract, an unknown
  security, another tenant's record, and a security id under another contract
  are all 404 `NOT_FOUND`. A compare-and-set that loses a concurrent status
  change is 409 `INVALID_STATUS_TRANSITION`.
- The status and `updated_at` row update and the
  `contract.security.status-changed` outbox event share one transaction; a
  rejected action writes neither. The action is not blocked by the contract
  lifecycle, so it works for a signed, in-force, or closed contract, unlike the
  create.
- `X-EIA-Tenant` is required. The canonical contract requires
  `X-EIA-Book: ASSUMED`; another book is hidden as 404 `BOOK_SCOPE_VIOLATION`.
  The domain currently accepts an absent header for compatibility with the
  other Contract proxy routes, which M-37 records.
- The 200 body is the same ten-field `SecurityRecord` the list and create
  return. The action is served by the domain `SecurityController` and by the
  expert's public `ContractSecurityController`; neither adds a public
  single-record GET.
- The event is a child aggregate: the envelope uses the security id at
  aggregate version 2 for the first status change and 3 when an expired record
  is released, while the outbox partition key stays the contract id. The
  payload is `{contractId, securityId, securityType, previousStatus, status}`.
  The name is new; SPEC 11.3.9 publishes only `contract.security.recorded` and
  `contract.security.breached` (M-22, M-37).
- The validator requires the path, the tenant and ASSUMED book parameters, both
  path parameters, the required `UpdateContractSecurityStatusRequest` with
  exactly the two-value status enum, the 200 `SecurityRecord` and 400/404/409
  responses, the transition and terminal-state documentation, the implemented
  channel, the `send` operation, the payload fields, and the catalog entry.

### Policy mass tort profile contract (2026-10-20)

Policy 2.6.0 adds the mass tort profile of a direct policy. The change is
additive: the two operations and the six schemas are new, and no existing path,
request field, response field, or event changed. The event name was already
published in the catalog, so it moves into the implemented subset without
changing the published total.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.6.0 | Additive | `GET/PUT /api/v1/policies/{policyId}/mass-tort-profile`, the `MassTortProfile` and `UpdateMassTortProfileRequest` schemas, and the `MassTortTortType`, `MassTortTriggerType`, `MassTortAllocationMethod`, and `MassTortProfileStatus` enums. |
| `asyncapi/policy.yaml` | 1.4.0 | Additive | `policy.mass-tort-profile.updated` becomes implemented and carries a `PolicyMassTortProfileUpdatedData` payload schema. |
| `asyncapi/event-catalog.yaml` | 1.12.0 | Additive | `policy.mass-tort-profile.updated` joins the Policy implemented subset (189 published names unchanged; Policy 23 published and 11 implemented). |

Semantics:

- A policy has exactly one profile. `GET` returns it; a policy without one is
  404 `MASS_TORT_PROFILE_NOT_FOUND`, and an unknown or other-tenant policy is
  404 `POLICY_NOT_FOUND`. `PUT` is an upsert: 201 when the row is created, 200
  when an existing row is replaced, and the `profileId` is preserved on update.
  The expert distinguishes the two outcomes; the public domain currently
  returns 200 for both, which M-32 records.
- The projection is `{profileId, policyId, tortType, triggerType,
  allocationMethod, allocationNotes, coverageBlockStart, coverageBlockEnd,
  status, updatedAt}`. `tortType`, `triggerType`, `allocationMethod`, and
  `status` are always present. `allocationNotes` and the two inclusive
  coverage-block dates are nullable; a DRAFT profile may omit them, while a
  COMPLETE profile requires all three (400
  `INCOMPLETE_MASS_TORT_PROFILE`). The coverage block is inclusive, so a
  one-day block is valid and an end before the start is 400
  `INVALID_COVERAGE_BLOCK`.
- `tortType` is one of `ASBESTOS`, `SILICA`, `TALC`, `PFAS`, `OPIOIDS`,
  `PRODUCT_LIABILITY`, `ENVIRONMENTAL`, or `OTHER`; `triggerType` is
  `EXPOSURE`, `MANIFESTATION`, `INJURY`, or `REVISIONIST`; `allocationMethod`
  is `ALL_SUMS`, `PRO_RATA_TIME_ON_RISK`, `PRO_RATA_PREMIUM`, `EQUAL_SHARES`,
  `STACKED_LIMITS`, or `CUSTOM_MATRIX`; `status` is `DRAFT` or `COMPLETE`.
  Values are trimmed and upper-cased before validation; an unknown value is 400
  `INVALID_TORT_TYPE`, `INVALID_TRIGGER_TYPE`, `INVALID_ALLOCATION_METHOD`, or
  `INVALID_MASS_TORT_PROFILE_STATUS`.
- The 2000-character notes cap is enforced on the stored trimmed value. The
  public domain also accepts `trigger` as an alias for `triggerType`, and
  read-only response members sent in the body are ignored.
- `X-EIA-Tenant` is required. The canonical contract requires
  `X-EIA-Book: DIRECT`; an absent header is accepted for compatibility with the
  other Policy proxy routes, a supplied value must be DIRECT, and another book
  is hidden as 404 `BOOK_SCOPE_VIOLATION`. The domain always forwards DIRECT
  to the expert.
- A create race is 409 `MASS_TORT_PROFILE_ALREADY_EXISTS`, and a concurrent
  policy or profile change is 409 `CONCURRENT_MODIFICATION`. The command
  accepts neither `Idempotency-Key` nor `If-Match`; repeating the same PUT
  rewrites the profile and emits another event (M-06, M-07, M-32).
- Every accepted write bumps the policy row version and writes
  `policy.mass-tort-profile.updated` in the same transaction. The payload
  carries `policyId`, `policyNumber`, `status`, `tortType`, `triggerType`,
  `allocationMethod`, `coverageBlockStart`, and `coverageBlockEnd`; the profile
  id and allocation notes are deliberately not in the payload because the
  policy is the aggregate and the event is keyed by the policy version.
- The implemented profile is narrower than SPEC 11.2.11: the SPEC
  `trigger_theory` and `ACTIVE`/`SUPERSEDED`/`UNDER_REVIEW` vocabularies, the
  wider Appendix E tort catalog, the secondary tort/product/exposure/review
  fields, and the approval and allocation-percentage command steps are not
  implemented. The public path is the short M-01 form. M-32 records the gap.

### Direct Claims list claimant filter (2026-10-20)

Direct Claims 1.7.0 adds the optional claimant filter to the claim list. The
change is additive: the query parameter is optional, no existing path, request
body field, response body field, or event changed, and a caller that omits it
keeps the unfiltered tenant list.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/direct-claims.yaml` | 1.7.0 | Additive | `GET /api/v1/claims` and `GET /internal/v1/claims` accept the optional `claimantPartyId` UUID query parameter alongside `status`; the public list documents the required tenant and DIRECT book, the bare `Claim[]` response, and the exact-match semantics. |

Filter semantics:

- `status` and `claimantPartyId` are independent optional filters. Supplying
  either narrows the list; supplying both applies an AND; omitting both returns
  every claim for the caller's tenant. The order stays newest first
  (`created_at DESC`, then `claim_number DESC`).
- `claimantPartyId` is matched exactly against the claim's stored claimant
  party UUID. There is no Party-service lookup and no tenant check on the
  party, so a well-formed UUID that matches no claim returns an empty array,
  not a 404. A malformed UUID is a 400.
- The public route takes `X-EIA-Tenant` and requires `X-EIA-Book: DIRECT`; a
  missing or different book is hidden as 404 `BOOK_SCOPE_VIOLATION` (SPEC 3.6.2,
  WALL-06). The response is the bare `Claim[]`, not the search envelope.
- The expert alias reads the tenant from `?tenantId=` and forwards the filter
  from the domain client. Both controllers and the expert repository already
  implement the parameter; this contract release documents it. `MISMATCHES.md`
  M-33 records the exact-match and no-reference-check caveat.

### Direct Claims allocation erosion (2026-10-20)

Direct Claims 1.8.0 records the policy-limit erosion of an allocation. The
change is additive: the new response fields are nullable except
`erosionStatus`, which starts at `NOT_POSTED`, the create `limitId` is optional,
and the erosion retry is a new bodyless path.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/direct-claims.yaml` | 1.8.0 | Additive | `Allocation` gains `limitId`, `erosionStatus` (`NOT_POSTED`, `POSTED`, `FAILED`), `erosionMessage`, and `erosionPostedAt`; `CreateClaimAllocationRequest` gains optional `limitId`; adds the bodyless `POST /api/v1/claims/{claimId}/allocations/{allocationId}/erosion` orchestration retry and the `AllocationErosionStatus` enum. |

Erosion semantics:

- An allocation without a limit starts in `NOT_POSTED`. The optional create
  `limitId` names the policy limit the allocation erodes; the create attempts
  the posting and returns the resulting `POSTED` or `FAILED` state, while an
  allocation without a limit keeps a null `limitId` and stays unposted.
- `POST .../{allocationId}/erosion` is an orchestration retry with **no request
  body**. It loads the tenant-scoped allocation, requires the stored `limitId`,
  reposts the limit to the Policy domain, and records the resulting `POSTED` or
  `FAILED` state. A Policy rejection or an unavailable Policy service is
  recorded as `FAILED` and returned with 200, not as a 5xx.
- A missing stored `limitId` is 400 `VALIDATION_ERROR`; an unknown claim or
  allocation, a foreign tenant, and a missing or non-DIRECT book are 404. Once
  `POSTED`, the state is terminal: a retry that computes the same `POSTED` state
  is an idempotent 200 no-op, while a retry that would record a different state
  is 409 `CONFLICT`.
- The validator requires the four new `Allocation` fields, the optional create
  `limitId`, the `AllocationErosionStatus` enum, the erosion path with no
  request body and the 200/400/404/409 responses, the 400 stored-limit
  documentation, and the 409 `CONFLICT` terminal guard. It also rejects a public
  `AllocationErosionRequest` schema.
- The expert implements the outcome write as
  `PATCH /internal/v1/claims/{claimId}/allocations/{allocationId}/erosion` with
  `{status, message?}`. The public domain retry calls it after the Policy
  posting, but currently catches the expert 409 for a terminal `POSTED`
  allocation and the record-write failure and returns the pre-update allocation
  with 200. `MISMATCHES.md` M-36 records that divergence.

### Direct Claims mass-tort allocation guard (2026-10-20)

Direct Claims 1.9.0 documents the policy mass-tort guard on the allocation
create. The change is additive: no path, request-body field, response-body
field, or event changed; one 400 code is added to an existing operation.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/direct-claims.yaml` | 1.9.0 | Additive | `POST /api/v1/claims/{claimId}/allocations` documents the 400 `MASS_TORT_YEAR_OUTSIDE_BLOCK` guard: when the policy's mass-tort profile is COMPLETE with both coverage-block dates, `policyYear` must fall within the inclusive start/end years. A DRAFT profile, a policy without a profile, and an unavailable Policy profile allow the allocation. |

An allocation is a policy-year split, so the year must be one the policy's
mass-tort coverage block actually covers (SPEC 11.4.7 `DIR-15`, SPEC 11.2.7
`POL-14`, and the `direct.claim.allocate` command's policy-trigger step). The
public domain reads `GET /api/v1/policies/{policyId}/mass-tort-profile` before
it forwards the create:

- A COMPLETE profile with both `coverageBlockStart` and `coverageBlockEnd`
  bounds the year to the inclusive start year through end year. A year outside
  the block is 400 `MASS_TORT_YEAR_OUTSIDE_BLOCK`, and it writes no allocation,
  no claim version bump, and no event. Both boundary years are allowed.
- A DRAFT profile, a COMPLETE profile without both block dates, a policy
  without a profile (404), and an unavailable or unreadable Policy profile all
  allow the allocation. The profile read fails open so it never becomes an
  availability dependency for claim allocation.
- The guard runs on the public create only; the expert allocation write does
  not re-read the profile. `MISMATCHES.md` M-31 records the stable code and
  M-32 the narrow profile that supplies the block.

### Direct Claims settlement payment links (2026-10-21)

Direct Claims 1.10.0 documents the Payment record that pays a settlement. The
change is additive: the settlement projection gains two nullable members and a
new PATCH command sets or clears them. No existing path, request field, response
status, or event name changed.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/direct-claims.yaml` | 1.10.0 | Additive | Adds `PATCH /api/v1/claims/{claimId}/settlements/{settlementId}/payment` and the `/internal/v1` expert alias, the `SettlementPaymentRequest` schema with its required-but-nullable `paymentId`, and the required-but-nullable `Settlement.paymentId` and `paymentLinkedAt` members. |
| `asyncapi/direct-claims.yaml` | 1.5.0 | Additive | The implemented `direct.claim.settlement-payment-linked` channel and `send` operation. |
| `asyncapi/event-catalog.yaml` | 1.27.0 | Additive | The new name is published and implemented (210 published and 90 implemented names; Direct Claims 27 published and 13 implemented). |

Payment-link semantics:

- `PATCH .../settlements/{settlementId}/payment` takes the required body
  `{paymentId}`. `paymentId` is required but nullable: a UUID links that
  Payment aggregate and the expert stamps `paymentLinkedAt` with the link
  instant; null clears both members. Repeating the current id is an idempotent
  no-op that bumps no version and writes no event.
- Only an AUTHORIZED or EXECUTED settlement is linkable. A PROPOSED or REJECTED
  settlement is 409 `SETTLEMENT_NOT_LINKABLE` and nothing is written; a
  concurrent settlement change that fails the version compare-and-set is 409
  `CONFLICT`. An unknown claim or settlement, a foreign tenant, and a missing or
  non-DIRECT book are 404, consistent with every other claim route.
- A real link or unlink bumps the settlement version and the claim row version
  and writes `direct.claim.settlement-payment-linked` in the same transaction.
  The payload carries the claim identity and version context plus `claimId`,
  `settlementId`, `settlementNumber`, `paymentId`, and `linkedAt`; an unlink
  omits `paymentId` and `linkedAt` while still recording the state change, and
  `eventVersion` stays 1.
- The event name is new and has no SPEC 11.4.9 equivalent. SPEC 11.4.4 models a
  `claim_settlement.payment_id` projection from Payment, but the implemented
  link is stored by the Direct Claims expert and no Payment service is called;
  the SPEC `PAID` settlement status is not implemented either. M-45 records the
  SPEC-less route, single-payment link, and event; M-22 records the naming gap.
- The public domain currently collapses the expert's stable
  `SETTLEMENT_NOT_LINKABLE` code to 409 `CONFLICT` while preserving the status
  and detail, so the stable code is documented as the canonical target. The
  validator requires both implemented operations, the required request body, the
  two projection members, the 400/404/409 responses, the DIRECT book scope, the
  implemented channel with its five payload members, and the catalog entry. The
  full run passes 13,815 checks.

### Policy program catalog and membership (2026-10-20)

Policy 2.8.0 adds the commercial program catalog and the policy-to-program
membership command. The change is additive: four new operations, five new
schemas, and the nullable `Policy.programId` member; no existing path, request
field, response field, or event changed. Policy 2.12.0 later adds the optional
capacity pair and the derived capacity usage to the same projection and create
body; that additive slice is documented under
[Policy program capacity](#policy-program-capacity-2026-10-21).

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.8.0 | Additive | `GET/POST /api/v1/programs`, `GET /api/v1/programs/{programId}`, `PATCH /api/v1/policies/{policyId}/program`, the `Program`, `ProgramType`, `ProgramStatus`, `CreateProgramRequest`, and `UpdatePolicyProgramRequest` schemas, and the nullable `Policy.programId` member. |
| `asyncapi/policy.yaml` | 1.6.0 | Additive | The implemented `policy.program.created` and `policy.policy.program-assigned` channels and `send` operations, with `PolicyProgramCreatedData` and `PolicyPolicyProgramAssignedData` payload schemas. |
| `asyncapi/event-catalog.yaml` | 1.17.0 | Additive | Both program names are published and implemented (196 published in total; Policy 26 published and 14 implemented; the platform implemented total is 75). |

Program semantics:

- A program groups policies into one commercial portfolio: a captive, pool,
  fronting arrangement, coinsurance facility, or mass tort program. The flat
  `Program` projection is `programId`, the server-generated
  `programNumber` (`PRG-{YEAR}-{7 digits}`), `name`, `programType`, the
  inclusive `effectiveFrom`/`effectiveTo` range, `status`, the nullable
  `leadPolicyId`, and `createdAt`; 2.12.0 adds the optional capacity pair and
  the `usedAmount`/`utilizationPct`/`policyCount` aggregates. The list is a
  bare newest-first array and is not part of the offset page envelope (M-04).
- `POST /api/v1/programs` always creates ACTIVE with a server-owned identity
  and returns 201 with `Location`. `name` is trimmed and capped at 200
  characters; `programType` is trimmed, upper-cased, and limited to `CAPTIVE`,
  `POOL`, `FRONTING`, `COINSURANCE`, or `MASS_TORT`; the effective range is
  inclusive, so a one-day program is valid and an end before the start is a
  400. The optional `leadPolicyId` is stored as supplied and is not resolved
  or checked against the tenant (M-39).
- `GET /api/v1/programs/{programId}` is tenant-scoped: an unknown program and
  a program in another tenant are both 404 `PROGRAM_NOT_FOUND`.
- `PATCH /api/v1/policies/{policyId}/program` sets the policy's program or
  clears it with a null `programId`; the body is required and the property is
  explicitly nullable. The accepted command bumps the policy row version and
  returns the updated `Policy` with its new strong `ETag`. An unknown or
  foreign policy is 404 `POLICY_NOT_FOUND`, an unknown or foreign program is
  404 `PROGRAM_NOT_FOUND`, and a concurrent policy change is 409
  `CONCURRENT_MODIFICATION`. The command accepts neither `If-Match` nor
  `Idempotency-Key`, so the response body's version is the only conflict
  token (M-06, M-07).
- `X-EIA-Tenant` is required on all four operations. The canonical contract
  requires `X-EIA-Book: DIRECT`; a missing tenant or book is a 400
  (`MISSING_TENANT_HEADER`/`INVALID_TENANT_HEADER` or `MISSING_HEADER`), and
  another book is hidden as 404 `BOOK_SCOPE_VIOLATION`. The domain and expert
  currently accept an absent book header, which M-39 records.
- The accepted create writes `policy.program.created` against the Program
  aggregate at version 1 in the same transaction as the row. The accepted
  assignment writes `policy.policy.program-assigned` against the Policy
  aggregate with `programId`, `previousProgramId`, and
  `changedFields: ["programId"]`; either id is null on a first assignment or a
  clear.
- The SPEC 10.11.3 catalogue uses `code`, `CASUALTY`/`PROPERTY`/`COMMERCIAL`/
  `AUTO`/`SPECIALTY`/`OTHER` types, and ACTIVE/INACTIVE status, and SPEC
  11.2.10 mounts the catalog under `/api/v1/policy/programs`. SPEC defines no
  program create, policy-assignment command, or program event names. The
  contract records the implemented shape and M-01, M-22, and M-39 record the
  deviations.
- The validator requires the four public paths, the five schemas, the
  nullable `Policy.programId`, both required headers, the 201/200/400/404/409
  responses, the 201 `Location`, the 200 `ETag`, both implemented channels and
  their payload fields and enums, and rejects any implemented program path that
  reappears under `x-planned-operations`. The full run passes 12,109 checks.

### Policy credit notes (2026-10-20)

Policy 2.9.0 adds the policy credit-note lifecycle. The change is additive:
three new operations and four new schemas; no existing path, request field,
response field, or event changed.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.9.0 | Additive | `GET/POST /api/v1/policies/{policyId}/credit-notes`, `PATCH /api/v1/policies/{policyId}/credit-notes/{creditNoteId}/status`, the `CreditNote`, `CreditNoteStatus`, `CreateCreditNoteRequest`, and `UpdateCreditNoteStatusRequest` schemas, and the required tenant and DIRECT book headers. |
| `asyncapi/policy.yaml` | 1.7.0 | Additive | The implemented `policy.credit-note.issued`, `policy.credit-note.applied`, and `policy.credit-note.cancelled` channels and `send` operations with a shared `PolicyCreditNoteData` payload. |
| `asyncapi/event-catalog.yaml` | 1.20.0 | Additive | All three names are published and implemented (201 published and 80 implemented in total; Policy 29 published and 17 implemented). |

Credit-note semantics:

- `GET .../credit-notes` returns the policy's notes as a bare newest-first
  array. A policy with no note returns `[]`. The projection is the ten-field
  `CreditNote`: `creditNoteId`, `noteNumber`, `policyId`, `amount`, `currency`,
  `reason`, `status`, `issuedAt`, `appliedAt`, and `createdAt`.
- `POST .../credit-notes` creates a DRAFT note and returns 201 with the stored
  projection. `amount` is a positive decimal money string, `currency` must equal
  the policy premium currency, and `reason` is optional and capped at 500
  characters. The server owns `creditNoteId`, `noteNumber` (`CN-{7 digits}`),
  the DRAFT state, the timestamps, and the policy-version bump.
- `PATCH .../credit-notes/{creditNoteId}/status` accepts only `ISSUED`,
  `APPLIED`, and `CANCELLED`. The only allowed edges are DRAFT -> ISSUED,
  DRAFT -> CANCELLED, ISSUED -> APPLIED, and ISSUED -> CANCELLED; APPLIED and
  CANCELLED are terminal. ISSUED stamps `issuedAt`, APPLIED stamps
  `appliedAt`, and CANCELLED stamps neither while preserving an earlier
  `issuedAt`.
- `X-EIA-Tenant` is required and `X-EIA-Book` is required and fixed to
  `DIRECT`; another book is hidden as 404 `BOOK_SCOPE_VIOLATION`. The domain
  currently accepts an absent book header for compatibility with the other
  Policy proxy routes (M-41).
- Creation bumps the policy version but emits no event. Each accepted
  transition writes `policy.credit-note.issued`, `.applied`, or `.cancelled`
  in the same transaction as the note row and the version bump. Errors are 400
  for the body, amount, currency, reason, and target status; 404 for an unknown
  policy or note; and 409 for an illegal transition or a concurrent change.
- SPEC 11.2.13 mounts the request at
  `/api/v1/policy/policies/{policyId}/credit-notes`, expects the
  REQUESTED/APPROVED/SENT_TO_SAP/ISSUED/REJECTED lifecycle with an approval
  gate and a SAP credit-memo reference, uses a closed reason enum, and publishes
  `policy.billing.credit-note-issued`. The implemented short path, four-state
  lifecycle, free-text reason, missing approval/SAP steps, and three new event
  names are recorded in M-22 and M-41.
- The validator requires the two paths, the three operations, the tenant and
  DIRECT book parameters, the `CreditNote` fields and status enum, the positive
  amount pattern, the optional 500-character reason, the three-value status
  request enum, the 201/200/400/404/409 responses, the three implemented
  channels and their payload fields, the catalog entries, and the absence of
  the implemented routes from `x-planned-operations`. The full run passes
  12,561 checks.

### Policy legal entities (2026-10-21)

Policy 2.10.0 adds the issuing legal entity catalog and the policy assignment
command. The change is additive: three new paths, four new operations, five new
schemas, and one nullable `Policy` property; no existing path, request field,
response field, or event changed.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.10.0 | Additive | `GET/POST /api/v1/legal-entities`, `GET /api/v1/legal-entities/{legalEntityId}`, `PATCH /api/v1/policies/{policyId}/legal-entity`, the `LegalEntity`, `LegalEntityType`, `LegalEntityStatus`, `CreateLegalEntityRequest`, and `UpdatePolicyLegalEntityRequest` schemas, and the nullable `Policy.legalEntityId`. |
| `asyncapi/policy.yaml` | 1.8.0 | Additive | The implemented `policy.legal-entity.created` and `policy.policy.legal-entity-assigned` channels and `send` operations with the `PolicyLegalEntityCreatedData` and `PolicyPolicyLegalEntityAssignedData` payloads. |
| `asyncapi/event-catalog.yaml` | 1.23.0 | Additive | Both names are published and implemented (205 published and 84 implemented in total; Policy 31 published and 19 implemented). |

Legal-entity semantics:

- `GET /api/v1/legal-entities` returns the tenant's legal entities newest first
  (`createdAt DESC`, then `legalEntityId ASC`) as a bare array (M-04);
  `GET .../{legalEntityId}` returns one. The projection is exactly
  `{legalEntityId, code, name, entityType, jurisdiction, regulator,
  licenseNumber, status, createdAt}` and never includes `tenantId`.
- `POST /api/v1/legal-entities` returns 201 with `Location` and the stored
  projection. `code` is trimmed, upper-cased, capped at 32 characters, and
  unique per tenant; a duplicate is 409 `DUPLICATE_LEGAL_ENTITY_CODE`. `name` is
  trimmed and capped at 200 characters. `entityType` is `INSURER`, `MGA`,
  `CAPTIVE`, `POOL`, or `FRONTER`; `jurisdiction` is a two-letter upper-case
  ISO 3166-1 alpha-2 code. `regulator` (120 characters) and `licenseNumber`
  (80 characters) are optional, trimmed, and stored as null when blank. A legal
  entity is created ACTIVE; INACTIVE is reserved for a later retirement command
  and no operation writes it.
- `PATCH /api/v1/policies/{policyId}/legal-entity` assigns the entity or clears
  the link with a null (or absent) id. The accepted command bumps the policy
  version, returns the updated `Policy` and its strong `ETag`, and writes the
  event. An unknown policy or legal entity is 404 `POLICY_NOT_FOUND` or
  `LEGAL_ENTITY_NOT_FOUND`; a concurrent policy change is 409
  `CONCURRENT_MODIFICATION`. The command accepts neither `If-Match` nor
  `Idempotency-Key` in this slice (M-06, M-07).
- `X-EIA-Tenant` is required. A supplied `X-EIA-Book` must be DIRECT and another
  book is hidden as 404 `BOOK_SCOPE_VIOLATION`; the domain and expert accept an
  absent book for compatibility with the other Policy proxy routes (M-43).
- The create writes `policy.legal-entity.created` against the `LegalEntity`
  aggregate at version 1. The assignment writes
  `policy.policy.legal-entity-assigned` against the policy at its new version,
  with nullable `legalEntityId`/`previousLegalEntityId` and
  `changedFields: [legalEntityId]`. Both events are written in the same
  transaction as the row change. The names are new and have no SPEC 11.2.9
  equivalent (M-22, M-43).
- SPEC 11.2.16 mounts the catalog at `/api/v1/policy/legal-entities`, and LE-01
  requires every policy to reference one issuing legal entity. The implemented
  short path, the five-type catalog against the wider SPEC 10.11.2 row, and the
  nullable assignment are recorded in M-01, M-12, and M-43.
- The validator requires the three paths, the four operations, the tenant and
  optional DIRECT book parameters, the path parameters, the five schemas and
  their field bounds and enums, the nullable `Policy.legalEntityId`, the
  201/200/400/404/409 responses, the two implemented channels and payloads, the
  catalog entries, and the absence of the implemented paths from
  `x-planned-operations`. The full run passes 13,143 checks.

### Policy credit application to installments (2026-10-21)

Policy 2.11.0 lets an APPLIED credit note settle an open billing installment.
The change is additive on the wire except that `ReceivableSummary.totalAmount`
and `.overdueAmount` now sum outstanding rather than gross amounts; no path,
event name, or required request field changes.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.11.0 | Additive, with a documented netting change | The optional `UpdateCreditNoteStatusRequest.installmentId`, the nullable `CreditNote.appliedInstallmentId`, the `BillingSummary` schema and `BillingPlan.summary`, the `Installment.creditedAmount`/`outstandingAmount` and `CREDITED` status, the `Receivable.creditedAmount`/`outstandingAmount` members, outstanding-based receivable totals, and the new credit-application rules and codes. |
| `asyncapi/policy.yaml` | 1.9.0 | Additive | The optional `installmentId` and `creditedAmount` members on the `policy.credit-note.applied` payload (`PolicyCreditNoteData`). |
| `asyncapi/event-catalog.yaml` | 1.23.0 | Unchanged | No event name or channel changes; 205 published and 84 implemented names, Policy 31 published and 19 implemented. |

Credit-application semantics:

- `PATCH .../credit-notes/{creditNoteId}/status` now accepts
  `{status, installmentId?}`. `installmentId` is required for APPLIED and
  ignored by ISSUED and CANCELLED.
- APPLIED credits the note amount to a DUE or OVERDUE installment on the same
  tenant and policy. A partial credit adds to the persisted `creditedAmount`
  and leaves the installment open; a credit that covers the uncredited
  remainder (`amount - creditedAmount`) also moves the installment to
  `CREDITED` with a zero `outstandingAmount`. The note transition and the
  installment update commit together.
- Applying rejects a missing `installmentId` with 400
  `INVALID_CREDIT_NOTE_INSTALLMENT`, an unknown or foreign installment with 404
  `INSTALLMENT_NOT_FOUND`, a PAID/WAIVED/CREDITED target with 409
  `INSTALLMENT_NOT_CREDITABLE` (`meta.installmentId`, `meta.currentStatus`), and
  an oversized note with 409 `CREDIT_NOTE_EXCEEDS_INSTALLMENT`
  (`meta.creditNoteId`, `meta.installmentId`, `meta.noteAmount`,
  `meta.availableAmount`). A concurrent application is 409
  `CONCURRENT_MODIFICATION`.
- `CreditNote` gains `appliedInstallmentId`, which is null until APPLIED and
  also null on a legacy APPLIED note that predates installment application.
- Billing `Installment` now carries the gross `amount`, `creditedAmount`, and
  the derived `outstandingAmount`; `CREDITED` joins DUE, OVERDUE, PAID, and
  WAIVED as a terminal status. A PAID, WAIVED, or fully CREDITED row has a zero
  outstanding amount. Settlement and dunning reject a CREDITED row.
- `BillingPlan` gains `summary` (`BillingSummary`): `totalAmount`, `paidAmount`,
  `waivedAmount`, `creditedAmount`, the net `outstandingAmount`,
  `overdueAmount`, `currency`, and `installmentCount`. `outstandingAmount` sums
  the per-installment outstanding amounts, so PAID, WAIVED, and CREDITED rows
  never contribute.
- `Receivable` gains `creditedAmount` and `outstandingAmount`; `amount` stays
  gross. A fully CREDITED installment leaves the queue, while a partially
  credited one stays listed with its reduced outstanding amount.
  `ReceivableSummary.totalAmount` and `.overdueAmount` sum the outstanding
  amounts, matching SPEC BIL-06.
- The `policy.credit-note.applied` payload adds `installmentId` and the
  installment's cumulative `creditedAmount`; the additions are optional and
  keep `eventVersion` 1. ISSUED and CANCELLED payloads are unchanged.
- SPEC 11.2.13's `credit_note_request` has no installment column and no APPLIED
  state; it defines only the BIL-06 netting rule. The installment link and the
  CREDITED installment status are recorded in M-27 and M-41.
- The validator requires the new request and response members, the conditional
  APPLIED requirement for `installmentId`, the `BillingSummary` fields and
  money references, the CREDITED status, the outstanding-based totals, the four
  new codes and their descriptions, and the applied payload members; it also
  rejects the nullable members becoming required. The full run passes 13,282
  checks.

### Policy program capacity (2026-10-21)

Policy 2.12.0 adds the optional program capacity and the derived capacity
usage. The change is additive: five `Program` response members and one optional
`CreateProgramRequest` pair; no path, event, required request field, or
existing field meaning changes.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.12.0 | Additive | The nullable `Program.capacityAmount`, `.capacityCurrency`, and `.utilizationPct` members; the `Program.usedAmount` and `.policyCount` members; the optional `CreateProgramRequest.capacityAmount`/`capacityCurrency` pair with its both-or-neither rule; the capacity usage derivation; and the 400 `INVALID_PROGRAM_CAPACITY` documentation. |
| `asyncapi/policy.yaml` | 1.9.0 | Unchanged | `PolicyProgramCreatedData` keeps its nine members; capacity is not published on the create event. |
| `asyncapi/event-catalog.yaml` | 1.23.0 | Unchanged | No event name or channel changes; 205 published and 84 implemented names. |

Capacity semantics:

- `Program.capacityAmount` and `Program.capacityCurrency` are the optional
  capacity limit. The pair is both null or both present; a program without a
  limit reports null for both. The amount is a positive decimal money string in
  the capacity currency.
- `Program.usedAmount` is the sum of the `limitAmount` values of the tenant's
  policies whose `programId` is the program. It is zero when no policy is
  assigned or no limit is recorded, and it is a bare decimal sum: the program
  neither converts nor validates the assigned policies' `limitCurrency`.
- `Program.policyCount` is the number of those policies across all statuses.
- `Program.utilizationPct` is `usedAmount / capacityAmount * 100`, rounded
  HALF_UP to two decimals; it is null without capacity and is not capped at
  100. A program with no capacity still reports `usedAmount` and `policyCount`.
- `POST /api/v1/programs` accepts the optional pair: both members or neither,
  the amount greater than zero with at most four fraction digits, and the
  currency a three-letter upper-case ISO 4217 code. A partial pair, a
  non-positive amount, or a malformed currency is 400
  `INVALID_PROGRAM_CAPACITY`; the public domain currently returns 400
  `VALIDATION_ERROR` with the field-specific `CAPACITY_AMOUNT_REQUIRED`/
  `CAPACITY_CURRENCY_REQUIRED`/`MIN_VALUE`/`INVALID_FORMAT` codes, which M-39
  records.
- The flat pair is narrower than the SPEC 10.11.3 `program_capacity` /
  `program_version` structure and the LE-02 capacity-share rules; M-39 records
  the gap.
- The validator requires the five new `Program` members and their
  nullability/patterns, the optional create pair with its positive-amount and
  currency constraints, the exact `dependentRequired` both-or-neither mapping,
  the capacity derivation in the schema descriptions, and the
  `INVALID_PROGRAM_CAPACITY` code on the create operation. The full run passes
  13,320 checks.

### Policy credit-note reversal (2026-10-21)

Policy 2.13.0 releases an applied credit note through the fifth lifecycle state.
The change is additive except that `CreditNoteStatus` and the status request gain
one enum value, which consumers must tolerate; no path, existing request field,
existing response field, or existing event name changes.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.13.0 | Additive, with a new enum value | The optional `UpdateCreditNoteStatusRequest.reason` (required for REVERSED, non-blank, at most 500 characters), REVERSED in the status and request enums, the nullable `CreditNote.reversedAt` and `.reversalReason`, the APPLIED -> REVERSED transition, the credit-release and installment-reopen rules, and the 400/409 rejections. |
| `asyncapi/policy.yaml` | 1.10.0 | Additive | The implemented `policy.credit-note.reversed` channel and `send` operation with the dedicated `PolicyCreditNoteReversedData` payload. |
| `asyncapi/event-catalog.yaml` | 1.25.0 | Additive | `policy.credit-note.reversed` is published and implemented (208 published and 88 implemented in total; Policy 32 published and 20 implemented). |

Reversal semantics:

- `PATCH .../credit-notes/{creditNoteId}/status` accepts
  `{status, installmentId?, reason?}`. `reason` is required for REVERSED,
  trimmed, non-blank, and capped at 500 characters; it is ignored by ISSUED,
  APPLIED, and CANCELLED. A missing or blank reason is 400
  `INVALID_CREDIT_NOTE_REASON`; a longer value is 400 `VALIDATION_ERROR` (the
  expert's `INVALID_CREDIT_NOTE_REASON` is the internal backstop).
- REVERSED is reachable only from APPLIED. APPLIED, CANCELLED, and REVERSED are
  terminal, so reversing a DRAFT, ISSUED, or CANCELLED note, or repeating a
  reversal, is 409 `INVALID_CREDIT_NOTE_TRANSITION` with `meta.currentStatus`
  and `meta.targetStatus`. A concurrent installment or policy change is 409
  `CONCURRENT_MODIFICATION`.
- Reversal releases the note amount from the installment recorded at application
  time. `creditedAmount` shrinks by the note amount, clamped at zero so the
  persisted credit never goes negative. A fully credited installment that no
  longer covers its gross amount reopens as `DUE` when its due date is today or
  later and as `OVERDUE` when it is already past; a partial credit on an open
  installment simply shrinks `creditedAmount` and keeps its status.
- A legacy APPLIED note with a null `appliedInstallmentId` is only marked
  REVERSED and changes no installment. A reversed note keeps `issuedAt`,
  `appliedAt`, and `appliedInstallmentId`, and stamps `reversedAt` plus
  `reversalReason`, so the original credit stays auditable.
- The note row, the installment release, the policy-version bump, and
  `policy.credit-note.reversed` are written in one transaction, so a rejected
  reversal changes neither the note nor the installment.
- The `reversed` payload is a dedicated `PolicyCreditNoteReversedData` with
  `creditNoteId`, `noteNumber`, the nullable `installmentId`, `amount`, `reason`,
  and `status: REVERSED`; it deliberately omits the policy identity members the
  other credit-note payload carries. The name and channel keep `eventVersion` 1.
- SPEC 11.2.13 has no reversal command or reversal fact; its
  `credit_note_request` lifecycle is REQUESTED/APPROVED/SENT_TO_SAP/ISSUED/
  REJECTED. The implemented fifth state, the release/reopen rules, and the new
  event name are recorded in M-22 and M-41.
- The validator requires the optional nullable `reason` with its 500-character
  cap and the conditional REVERSED requirement, the five-value
  `CreditNoteStatus` enum, the required-but-nullable `reversedAt` and
  `reversalReason` members, the APPLIED -> REVERSED documentation and the
  `INVALID_CREDIT_NOTE_REASON` code, the four implemented channels, the
  dedicated reversed payload fields, and the catalog entry. The full run passes
  13,558 checks.

### Policy cancellation-linked credit notes (2026-10-21)

Policy 2.14.0 links a return-premium credit note to the cancellation it refunds
and makes DRAFT creation observable. The change is additive: one optional
request member, three nullable response members, and one event name; no path,
required request field, existing response member, or existing event name
changes.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.14.0 | Additive | The optional nullable `CreateCreditNoteRequest.cancellationId`; the required-but-nullable `CreditNote.cancellationId` and `.cancellationNumber`; the nullable `Cancellation.cancellationNumber`; the same-tenant/policy, ACTIVE, return-premium amount, currency, and one-note-per-cancellation link rules with their 400/404/409 rejections; and the `policy.credit-note.created` creation event. |
| `asyncapi/policy.yaml` | 1.11.0 | Additive | The implemented `policy.credit-note.created` channel and `send` operation with the dedicated `PolicyCreditNoteCreatedData` payload. |
| `asyncapi/event-catalog.yaml` | 1.26.0 | Additive | `policy.credit-note.created` is published and implemented (209 published and 89 implemented in total; Policy 33 published and 21 implemented). |

Link semantics:

- `POST .../credit-notes` accepts `{amount, currency, reason?, cancellationId?}`.
  A supplied `cancellationId` must resolve on the same tenant and policy (404
  `CANCELLATION_NOT_FOUND`), still be ACTIVE (409 `CANCELLATION_NOT_ACTIVE` with
  `meta.cancellationId` and `meta.currentStatus`; REINSTATED and VOID cannot
  fund a note), and match the note. `amount` must equal the cancellation's
  `returnPremiumAmount` within one cent (400 `CREDIT_NOTE_AMOUNT_MISMATCH`) and
  `currency` must equal its `premiumCurrency` (400 `CURRENCY_MISMATCH`).
- A cancellation funds at most one note. A second request for the same
  cancellation is 409 `DUPLICATE_CANCELLATION_CREDIT_NOTE` with
  `meta.cancellationId` and, when the existing row is known, `meta.creditNoteId`
  and `meta.noteNumber`; the unique
  `(tenant_id, policy_id, cancellation_id)` key arbitrates a concurrent
  duplicate. A rejected link writes no note and no event.
- A linked note carries `cancellationId` and `cancellationNumber` in the
  projection; both are null for a general billing adjustment. The number is the
  cancellation's `CX-{7 digits}` reference, falling back to the cancellation id
  for a historical row that predates numbering.
- `Cancellation` adds the nullable `cancellationNumber` (`CX-{7 digits}`,
  unique per policy). New cancellations always carry one and a historical row
  may be null. The public domain `CancellationDto` does not yet forward the
  number, while the expert projection returns it; M-41 records the gap.
- Creation writes `policy.credit-note.created` in the same transaction as the
  note row and the policy-version bump. `PolicyCreditNoteCreatedData` requires
  the base policy/note identity, `noteNumber`, `amount`, `currency`,
  `status: DRAFT`, and `createdAt`, and carries the optional
  `cancellationId`/`cancellationNumber` for a linked note; an unlinked
  adjustment omits both link members. The event name and payload keep
  `eventVersion` 1.
- SPEC 11.2.13 has no cancellation-link column and no creation fact; it states
  only that a cancellation produces a credit note or additional invoice
  (BIL-05) and defines the non-negative net outstanding rule (BIL-06). The link
  rules, the new `CX-{7 digits}` reference, and the `policy.credit-note.created`
  name are recorded in M-22 and M-41.
- The validator requires the optional nullable `cancellationId` request member,
  the required-but-nullable `CreditNote.cancellationId`/`cancellationNumber`
  members with their 32-character cap, the nullable `Cancellation.cancellationNumber`,
  the link rules and their five 400/404/409 codes, the five implemented
  channels, the `PolicyCreditNoteCreatedData` payload and its optional link
  members, and the catalog entry. The full run passes 13,645 checks.

### Policy premium audit (2026-10-22)

Policy 2.15.0 adds the audited-premium command. The change is additive: one
public operation, one request schema, and one implemented event name; no
existing path, field, or event name changes.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.15.0 | Additive | `POST /api/v1/policies/{policyId}/premium-audit` with `ApplyPremiumAuditRequest`, the `BOUND`/`ISSUED`/`IN_FORCE`/`ENDORSED`/`REINSTATED` eligibility gate, the `PREMIUM_AUDIT` endorsement and version semantics, the 201 `Policy` with `ETag`, the 400/404/409/422/428 responses, and the implemented event name. |
| `asyncapi/policy.yaml` | 1.12.0 | Additive | The implemented `policy.policy.premium-audited` channel and `send` operation with the dedicated `PolicyPremiumAuditedData` payload. The SPEC 11.2.9 `policy.premium.audited` channel stays planned. |
| `asyncapi/event-catalog.yaml` | 1.32.0 | Additive | `policy.policy.premium-audited` is published and implemented (216 published and 96 implemented in total; Policy 34 published and 22 implemented). |

Command semantics:

- The body is `{auditedPremium, effectiveDate, reason, approvedBy?,
  approvalRef?}`. `auditedPremium` is the final written premium as a
  non-negative decimal string with four fraction digits; it must differ from
  the current policy premium, so an equal amount is 400 `NO_PREMIUM_CHANGE` and
  writes no endorsement, version, row change, or event. `reason` is trimmed,
  required, and capped at 500 characters.
- Only a `BOUND`, `ISSUED`, `IN_FORCE`, `ENDORSED`, or `REINSTATED` policy can
  be audited. Any other status is 409 `PREMIUM_AUDIT_NOT_ALLOWED` with
  `meta.sourceStatus` and `meta.allowedStatuses`, and nothing is written.
- The accepted command records a `PREMIUM_AUDIT` endorsement and an immutable
  `PREMIUM_AUDIT` policy version, replaces the policy premium with
  `auditedPremium`, and bumps the aggregate version. The endorsement and the
  version carry the signed delta and the description
  `Premium audit: <old> -> <new> (<delta>)`; coverage grants and limits are not
  touched. The first audit of a `BOUND` policy is later superseded by the
  `ISSUE` version so the policy keeps exactly one `ISSUED` version.
- The effective date is resolved by the version timeline. A date on or after
  policy expiration is 422 `VERSION_OUTSIDE_POLICY_TERM`; a regression without
  justification is 422 `VERSION_REGRESSION`; a pre-inception date without a
  reason is 422 `VERSION_BACKDATE_REASON_REQUIRED`; a pre-inception or
  regressing date without both `approvedBy` and `approvalRef` is 428
  `APPROVAL_REQUIRED`. A justified pre-inception date is clamped to the policy
  inception on the version while the endorsement keeps the requested business
  date and the backdate reason. `approvedBy` and `approvalRef` are optional for
  a normal audit.
- The 201 body is the updated `Policy` with its new strong `ETag`, and the 200
  replay path is not implemented. `If-Match` is optional; a stale tag is 409
  `CONCURRENT_MODIFICATION` with `meta.currentVersion`/`meta.expectedVersion`
  and a malformed tag is 400 `INVALID_IF_MATCH`. The domain forwards an
  optional `Idempotency-Key`, but the expert does not replay on it, so a retry
  applies a second audit (M-07).
- `X-EIA-Tenant` is required and a supplied `X-EIA-Book` must be DIRECT; an
  absent book is accepted for compatibility and another book is hidden as 404
  `BOOK_SCOPE_VIOLATION`. An unknown or foreign policy is 404
  `POLICY_NOT_FOUND`.
- The accepted command writes `policy.policy.premium-audited` and
  `policy.policy.version-issued` in the same transaction as the premium
  replacement. `PolicyPremiumAuditedData` requires `policyId`, `policyNumber`,
  `previousPremium`, `auditedPremium`, `delta`, `currency`, `effectiveDate`,
  and `reason`, and keeps `eventVersion` 1.
- SPEC 11.2.9 names the posting fact `policy.premium.audited`, which remains
  published and planned; the implemented name is the new
  `policy.policy.premium-audited`. The command does not create a
  `policy_premium_audit` row, so the SPEC 11.2.4 audit period, audit type,
  exposure, deposit/rated/additional/return premium, minimum-premium flag, and
  SCHEDULED..WAIVED status are not modelled, and the quarterly
  `policy.premium-audit-batch` job is not implemented. SPEC 11.2.10 names no
  premium-audit route. The deviations are recorded in M-22 and M-50.
- The validator requires the operation with the shared tenant, optional DIRECT
  book, `IfMatch`, and `policyId` parameters, the required request body and its
  field bounds, the 201 `Policy` with the shared `ETag`, the 400/404/409/422/428
  responses and their codes, the auditable-status, transaction, and event
  wording, the absence of the path from `x-planned-operations`, the implemented
  channel and its eight-member payload, the `IMPLEMENTED_EVENTS` entry, and the
  catalog entry. The full run passes 14,576 checks.

### Policy billing adjustment (2026-10-22)

Policy 2.16.0 adds the positive premium adjustment command. The change is
additive: one public operation, one request schema, one result envelope, and one
implemented event name; no existing path, field, or event name changes.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/policy.yaml` | 2.16.0 | Additive | `POST /api/v1/policies/{policyId}/billing/adjustment` with `BillingAdjustmentRequest` `{dueDate, reason}`, the derived positive-delta rule, the 201 `BillingAdjustmentResult` `{plan, installment, adjustmentAmount, newTotalPremium}` with `ETag`, the 400/404/409 responses, and the `policy.billing-plan.adjusted` fact. |
| `asyncapi/policy.yaml` | 1.13.0 | Additive | The implemented `policy.billing-plan.adjusted` channel and `send` operation with the dedicated nine-member `PolicyBillingPlanAdjustedData` payload. |
| `asyncapi/event-catalog.yaml` | 1.33.0 | Additive | `policy.billing-plan.adjusted` is published and implemented (217 published and 97 implemented in total; Policy 35 published and 23 implemented). |

Command semantics:

- The body is `{dueDate, reason}`. Both are required. `dueDate` must not
  precede the policy effective date (the effective date itself is accepted);
  `reason` is trimmed, non-blank, and capped at 500 characters. A missing,
  blank, or over-long member is 400 `VALIDATION_ERROR`; a pre-inception date is
  400 `INVALID_ADJUSTMENT_DUE_DATE`. The expert's service guard reports
  `INVALID_ADJUSTMENT_REASON` for a reason that bypasses request validation.
- The amount is derived, not supplied: `adjustmentAmount = policy premium -
  (plan totalPremium - creditedAmount)`, where `creditedAmount` is the sum of
  the credit notes already applied to the plan's installments and the plan's net
  premium is floored at zero. Only a positive remainder is billable; zero or
  negative is 400 `NO_PREMIUM_ADJUSTMENT` with `meta.delta`,
  `meta.policyPremiumAmount`, `meta.planTotalPremium`, `meta.creditedAmount`,
  and `meta.netPlanPremium`, and writes nothing. A premium decrease is a
  credit-note concern.
- The command requires an existing plan (404 `BILLING_PLAN_NOT_FOUND`), an
  ACTIVE plan (409 `BILLING_PLAN_NOT_ACTIVE` with `meta.planId` and
  `meta.currentStatus`), and fewer than 24 installments (409
  `MAX_INSTALLMENTS_REACHED`). A concurrent plan change, including a racing
  adjustment, is 409 `CONCURRENT_MODIFICATION` and rolls back the append.
- The accepted command appends one DUE installment numbered
  `plan.installmentCount + 1` at the requested `dueDate` for the derived amount,
  grows the plan total by that amount and the plan count by one, bumps the policy
  version, and writes `policy.billing-plan.adjusted` in the same transaction.
- The 201 body is `{plan, installment, adjustmentAmount, newTotalPremium}` with
  the new policy `ETag`. The `plan` member carries the updated flat plan identity
  and totals but no schedule: `plan.installments` is empty and the derived
  `plan.summary` is computed from that empty list, so `summary.installmentCount`
  and `summary.outstandingAmount` are zero while `plan.installmentCount` and
  `plan.totalPremium` are authoritative. The appended row travels separately as
  `installment`.
- `X-EIA-Tenant` is required and a supplied `X-EIA-Book` must be DIRECT; another
  book is hidden as 404 `BOOK_SCOPE_VIOLATION`. An unknown or foreign policy is
  404 `POLICY_NOT_FOUND`.
- The optional `If-Match` and `Idempotency-Key` headers are validated by the
  domain and forwarded to the expert. A malformed or blank tag is 400
  `INVALID_IF_MATCH`; a blank key is treated as absent and an over-long key is
  400 `INVALID_IDEMPOTENCY_KEY`. The expert neither compares the tag nor replays
  the key in this slice, so a retry appends a second installment (M-06, M-07).
- SPEC 11.2.10 names no billing-adjustment route and SPEC 11.2.13 names no
  positive premium adjustment event. The route, the derived-delta rule, and the
  new `policy.billing-plan.adjusted` name are recorded in M-22, M-27, and M-51.
  The event payload requires `policyId`, `policyNumber`, `planId`,
  `adjustmentAmount`, `newTotalPremium`, `installmentId`, `installmentNumber`,
  `dueDate`, and `reason`, and keeps `eventVersion` 1.
- The validator requires the operation with the shared tenant, optional DIRECT
  book, `IfMatch`, and `IdempotencyKey` parameters, the required request body
  and its field bounds, the 201 envelope and its `ETag`/`Idempotent-Replayed`
  headers, the 400/404/409 responses and their codes, the transaction and event
  wording, the absence of the path from `x-planned-operations`, the implemented
  channel and its nine-member payload, the `IMPLEMENTED_EVENTS` entry, and the
  catalog entry. The full run passes 14,694 checks.

### Direct Claims litigation damages and events (2026-10-22)

Direct Claims 1.11.0 documents the optional damages a litigation matter seeks
and the two litigation events the expert publishes. The change is additive: two
nullable request and projection members, no new route, and two event channels;
no existing path, request field, response status, or event name changed.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/direct-claims.yaml` | 1.11.0 | Additive | `Litigation` and `LitigationRequest` add the optional `damagesSought` and `damagesCurrency` pair; the public and expert create/update descriptions document the both-or-neither rule, the positive amount, the three-letter currency, and the PATCH omission. |
| `asyncapi/direct-claims.yaml` | 1.6.0 | Additive | The implemented `direct.claim.litigation-created` channel and `send` operation, and `direct.claim.litigation-updated` moves from planned to implemented with its documented payload. |
| `asyncapi/event-catalog.yaml` | 1.34.0 | Additive | The created name is published and both names are implemented (218 published and 99 implemented in total; Direct Claims 28 published and 15 implemented). |

Semantics:

- `damagesSought` is the amount the claimant seeks and `damagesCurrency` is its
  three-letter uppercase ISO 4217 code. Both are optional and nullable on the
  request and the projection. When damages are recorded the pair is
  both-or-neither: one member without the other is 400 `VALIDATION_ERROR`.
  `damagesSought` is a decimal string greater than zero with at most four
  fraction digits; the contract never returns it as a JSON number.
- The create and the update use the same body. On an update, omitting both
  members (or sending both as null) keeps the stored pair; supplying both
  replaces it. `expectedVersion` remains required on the public PATCH and a
  stale value is 409 `CONFLICT`.
- The `Litigation` projection always returns both members together: the recorded
  decimal string and uppercase currency when damages exist, and null for both
  when the matter has none. The stored amount is normalized to four fraction
  digits.
- An accepted create writes `direct.claim.litigation-created`; an accepted
  update writes `direct.claim.litigation-updated`. Both are written in the same
  transaction as the matter write and the parent claim version bump, so the
  per-claim event stream stays monotonic. The payload carries `claimId`,
  `claimNumber`, `claimVersion` (the claim's post-write row version, serialized
  as `version`), `litigationId`, `matterType`, `jurisdiction`,
  `counselPartyId`, `filingDate`, `litigationStatus`, and
  `litigationVersion`; `trialDate`, `caseNumber`, and the `damagesSought` /
  `damagesCurrency` pair are omitted when null. `eventVersion` stays 1 and the
  envelope aggregate version is the bumped claim version plus one, as for the
  other claim child events.
- The damages columns and the `direct.claim.litigation-created` name have no
  SPEC 11.4.4 or 11.4.9 definition; `direct.claim.litigation-updated` is the
  SPEC name and was previously planned. SPEC 11.4.9 publishes no
  matter-creation fact, so the created name is an EV-05 additive extension.
- The public domain pre-validates only a non-negative amount and a non-blank
  currency. A zero amount or a one-sided pair therefore passes the domain
  request validation and is rejected by the expert with 400
  `VALIDATION_ERROR`; the end-to-end response still matches this contract.
  `MISMATCHES.md` M-52 records the layering and the SPEC-less fields.
- The validator requires both schemas, the four create/update operations, the
  optional nullable pair, the `dependentRequired` mapping, the positive amount
  and currency patterns, the implemented channels with their documented payload
  members and both-or-neither wording, the `IMPLEMENTED_EVENTS` entries, and the
  catalog entries. The full run passes 14,825 checks.

### Notifications source linkage (2026-10-22)

Notifications 1.4.0 adds the optional flat source link that identifies the
business record a notification is about. The change is additive: three optional
nullable members on the projection and both create commands, one new enum, and
two enriched event payloads; no path, required field, or event name changes.

| Document | Version | Classification | Change |
|---|---|---|---|
| `openapi/notifications.yaml` | 1.4.0 | Additive | `Notification`, `CreateNotificationRequest`, and `CreateNotificationRequestInternal` add the optional nullable `sourceType`, `sourceId`, and `sourceReference`; the `NotificationSourceType` enum (`DIRECT_CLAIM`, `ASSUMED_CLAIM`, `POLICY`, `CONTRACT`, `PAYMENT`, `OTHER`); the both-or-neither type/id rule; and the 64-character reference cap. |
| `asyncapi/notifications.yaml` | 1.3.0 | Additive | The implemented `notifications.notification.created` and `.sent` channels gain the `NotificationCreatedData` and `NotificationSentData` payload schemas, each with the optional source members. `eventVersion` stays 1. |
| `asyncapi/event-catalog.yaml` | 1.34.0 | Unchanged | No event name changes; the catalog stays at 218 published and 99 implemented names (Notifications 15 published and 5 implemented). |

Semantics:

- `sourceType` is a closed six-value enum. An unknown value is 400
  `INVALID_SOURCE_TYPE` (`EIA-NTF-9409`); the value is trimmed and upper-cased,
  so `direct_claim` selects `DIRECT_CLAIM`. Adding a value is additive and
  removing one is breaking.
- `sourceType` and `sourceId` are supplied together or not at all. A type
  without an id, or an id without a type, is 400 `INVALID_SOURCE_LINKAGE`
  (`EIA-NTF-9410`). All six types require an id when the type is present;
  unlike Payment, `OTHER` has no reference-only escape.
- `sourceReference` is optional metadata of at most 64 characters (example
  `CLM-2026-0000001`). A longer value is 400 `INVALID_SOURCE_REFERENCE`
  (`EIA-NTF-9411`); the expert trims it and treats a blank value as absent. It
  never replaces `sourceId`, and a reference-only link with no type or id is
  accepted.
- The link is denormalized and has no referential-integrity check: `sourceId`
  is not resolved against the claim, policy, contract, payment, or other source
  vertical. The SPEC 11.8.4 `subject_vertical`/`subject_type`/`subject_id`/
  `subject_business_key` columns and the SPEC 12.5.5 `subject` EntityRef are
  still planned. `MISMATCHES.md` M-53 records the deviation.
- The created and sent facts carry each present field in their `data` object,
  so a consumer can correlate the notification without a second lookup. An
  unlinked notification omits all three members and both facts stay at
  `eventVersion` 1.
- The public create operation forwards the link to the expert, which owns the
  enum, pairing, and length rules; the domain's translated problem keeps the
  expert status and `EIA-NTF-94xx` code. A direct `/internal/v1` caller sees the
  same 400 codes.
- The validator requires the three members on the projection and both create
  requests, their optional/nullable status, the ordered six-value enum, the
  UUID id, the 64-character reference, both conditional rules, the two payload
  messages with optional source members, and the three documented 400 codes.
  The full run passes 14,914 checks.

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
| `X-EIA-Book` | Policy billing, billing adjustment, and receivables | Optional for compatibility with the other Policy proxy routes, but a supplied value must be DIRECT; another book is hidden as 404 `BOOK_SCOPE_VIOLATION`. An absent header is accepted. The guard runs before the expert call. |
| `X-EIA-Book` | Policy installment dunning | Required and fixed to `DIRECT`. A missing header is a 400 and another book is hidden as 404 `BOOK_SCOPE_VIOLATION`; the domain currently accepts an absent header, which M-38 records. |
| `X-EIA-Book` | Policy renewal | Required and fixed to `DIRECT`. The contract makes a missing header a 400 and hides another book as 404 `BOOK_SCOPE_VIOLATION`; the domain currently accepts an absent header, which M-28 records. |
| `X-EIA-Book` | Policy programs | Required and fixed to `DIRECT`. The contract makes a missing header a 400 and hides another book as 404 `BOOK_SCOPE_VIOLATION`; the domain and expert currently accept an absent header, which M-39 records. |
| `X-EIA-Book` | Policy credit notes | Required and fixed to `DIRECT`. Another book is hidden as 404 `BOOK_SCOPE_VIOLATION`. The domain currently accepts an absent header for compatibility with the other Policy proxy routes, which M-41 records. |
| `X-EIA-Book` | Policy legal entities and assignment | Optional for compatibility with the other Policy proxy routes, but a supplied value must be `DIRECT`; another book is hidden as 404 `BOOK_SCOPE_VIOLATION`. An absent header is accepted, which M-43 records against the canonical DIRECT-book rule. |
| `X-EIA-Book` | Contract technical accounts | Required and fixed to `ASSUMED`. Another book is hidden as 404 `BOOK_SCOPE_VIOLATION`; the domain currently accepts an absent header for compatibility with the other Contract proxy routes, which M-29 records. |
| `X-EIA-Book` | Contract technical-account lines | Required and fixed to `ASSUMED`. Another book is hidden as 404 `BOOK_SCOPE_VIOLATION`; the domain currently accepts an absent header for compatibility with the other Contract proxy routes, which M-29 and M-42 record. |
| `X-EIA-Book` | Contract period bordereaux | Required and fixed to `ASSUMED`. Another book is hidden as 404 `BOOK_SCOPE_VIOLATION`; the domain currently accepts an absent header for compatibility with the other Contract proxy routes, which M-30 records. |
| `X-EIA-Book` | Contract cash calls | Required and fixed to `ASSUMED`. Another book is hidden as 404 `BOOK_SCOPE_VIOLATION`; the domain currently accepts an absent header for compatibility with the other Contract proxy routes, which M-34 records. |
| `X-EIA-Book` | Contract security/collateral | Required and fixed to `ASSUMED`. Another book is hidden as 404 `BOOK_SCOPE_VIOLATION`; the domain currently accepts an absent header for compatibility with the other Contract proxy routes, which M-37 records. |
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

### Direct Claims allocations

A direct claim may be split across a policy year and layer, and each split may
erode a policy limit:

| Operation | Path | Success | Errors |
|---|---|---|---|
| List allocations | `GET /api/v1/claims/{claimId}/allocations` | 200 `AllocationSummary` | 400, 404 |
| Record allocation | `POST /api/v1/claims/{claimId}/allocations` | 201 `Allocation` | 400, 404, 409 |
| Retry erosion | `POST /api/v1/claims/{claimId}/allocations/{allocationId}/erosion` | 200 `Allocation` | 400, 404, 409 |

The summary is `{items, totalPct, totalAmount}`; `items` is ordered oldest
first and `totalPct`/`totalAmount` sum the claim's rows. An allocation is
`{allocationId, claimId, policyId, limitId, policyYear, layer, allocationPct,
allocatedAmount, erosionStatus, erosionMessage, erosionPostedAt, createdAt}`.
`allocationPct` and `allocatedAmount` are decimal strings; the tenant is implied
and is not part of the public projection. `limitId`, `erosionMessage`, and
`erosionPostedAt` are nullable; `erosionStatus` is always present and is
`NOT_POSTED` until a posting is recorded. A create that supplies `limitId`
attempts the policy posting and may return `POSTED` or `FAILED`.

Rules:

- `X-EIA-Tenant` is required. `X-EIA-Book` is required and must be DIRECT; a
  missing or different book is hidden as 404, consistent with every other claim
  route (SPEC 3.6.2, WALL-06).
- The create body is `CreateClaimAllocationRequest`: `policyId`, `policyYear`,
  `layer`, `allocationPct`, and `allocatedAmount` are required and `limitId` is
  optional. `policyId` must be the claim's own policy (400
  `POLICY_MISMATCH`); `policyYear` must be 1900-2200; `layer` is trimmed and at
  most 32 characters; `allocationPct` is a fraction greater than 0 and at most
  1; `allocatedAmount` is zero or greater. A supplied `limitId` is the policy
  limit the allocation erodes: the create attempts the policy posting and
  returns the resulting `POSTED` or `FAILED` state. A create without `limitId`
  stays `NOT_POSTED`.
- The create also enforces the policy's mass-tort coverage block: when the
  policy's mass-tort profile is COMPLETE with both block dates, `policyYear`
  must fall within the inclusive start/end years or the request is 400
  `MASS_TORT_YEAR_OUTSIDE_BLOCK`. A DRAFT profile, an absent profile, and an
  unavailable Policy profile allow the allocation. Both block boundary years
  are allowed, and a rejected year writes nothing.
- The percentages already recorded for the claim plus the new one may not
  exceed 1. An excess is 409 `ALLOCATION_EXCEEDS_100` and writes no row and no
  event. `allocatedAmount` is a booking figure and is not capped by the current
  reserve.
- `POST .../{allocationId}/erosion` is an orchestration retry with no request
  body. It loads the allocation, requires its stored `limitId`, reposts the
  limit to the Policy domain, and records the resulting `POSTED` or `FAILED`
  state. A Policy rejection or an unavailable Policy service is recorded as
  `FAILED` and returned with 200. A missing stored `limitId` is 400
  `VALIDATION_ERROR`; an unknown claim or allocation, a foreign tenant, and a
  missing or non-DIRECT book are 404. Once `POSTED`, the state is terminal: a
  retry that computes the same `POSTED` state is an idempotent 200 no-op, while
  a retry that would record a different state is 409 `CONFLICT`.
- The create bumps the parent claim version and writes
  `direct.claim.allocation-created` in the same transaction. The payload
  carries the claim identity and number, the allocation fields, and the claim's
  new `totalPct`/`totalAmount`.
- The expert serves the same public path and an `/internal/v1` alias that the
  domain calls; the domain remaps the expert's `id`/`tenantId` projection to
  the public `allocationId`. The public error codes for the create are the
  expert's stable `POLICY_MISMATCH` and `ALLOCATION_EXCEEDS_100`, but the domain
  currently collapses them to `VALIDATION_ERROR` and `CONFLICT` (M-31).
- Erosion is written on the expert as
  `PATCH /internal/v1/claims/{claimId}/allocations/{allocationId}/erosion` with
  `{status, message?}`. The public domain retry calls it after posting the
  stored limit to Policy. The domain currently catches the expert 409 for a
  terminal `POSTED` allocation and the expert record-write failure and returns
  the pre-update allocation with 200; M-36 records the difference from the
  canonical 409 and the "recorded state" contract.

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

### Payment allocations

A payment may be split across the claim or policy target and financial component
it settles:

| Operation | Path | Success | Errors |
|---|---|---|---|
| List allocations | `GET /api/v1/payments/{paymentId}/allocations` | 200 `PaymentAllocationSummary` | 400, 404 |
| Record allocation | `POST /api/v1/payments/{paymentId}/allocations` | 201 `PaymentAllocation` | 400, 404, 409 |
| Reverse allocation | `POST /api/v1/payments/{paymentId}/allocations/{allocationId}/reverse` | 200 `PaymentAllocation` | 400, 404, 409 |

The summary is `{items, paymentAmount, totalAllocated, reversedTotal, net,
unallocated, currency}`; `items` is ordered oldest first (`createdAt` ascending,
allocation id as the tie-break) and keeps reversed rows for audit.
`totalAllocated` is the gross sum of every recorded split, `reversedTotal` is the
sum of the reversed rows, `net` is `totalAllocated - reversedTotal`, and
`unallocated` is the payment amount minus `net`. An allocation is `{allocationId,
paymentId, targetType, targetId, component, amount, currency, createdAt,
reversedAt, reversalReason}`; `reversedAt` and `reversalReason` are null until
the allocation is reversed. Amounts are decimal strings in the payment currency;
the tenant is implied and is not part of the projection.

Rules:

- `X-EIA-Tenant` is required. The implemented route is tenant-scoped and not
  book-scoped: a payment outside the caller's tenant is reported exactly like a
  missing payment (404 `PAYMENT_NOT_FOUND`), so allocations never disclose
  another tenant's records. SPEC 3.6.1 requires the book on every payment and
  allocation; the implemented payment and allocation rows carry no book
  (M-08, M-12, and M-35).
- The create body is `CreatePaymentAllocationRequest`: all four fields are
  required. `targetType` is `DIRECT_CLAIM`, `ASSUMED_CLAIM`, or `POLICY` and
  `targetId` is the UUID of that record. `component` is `INDEMNITY`,
  `DEFENSE_COST`, `ALAE`, `EXPENSE`, `COMMISSION`, or `OTHER`. Both vocabularies
  are trimmed and matched case-insensitively, so `direct_claim` and `indemnity`
  are accepted and normalized. `amount` must be greater than zero with at most
  four fraction digits; the currency is never accepted from the caller because
  an allocation always uses the payment's currency.
- An allocation is append-only. The accumulated active allocations plus the new
  amount may not exceed the payment amount; an excess is 409
  `ALLOCATION_EXCEEDS_PAYMENT` and writes no row and no event. A `CANCELLED`,
  `REVERSED`, or `FAILED` payment is 409 `PAYMENT_NOT_ALLOCATABLE` and likewise
  writes nothing.
- A reversal is a stamp, not a delete. The body is `{reason}`: `reason` is
  required, trimmed, non-blank, and at most 200 characters, and a missing, blank,
  or over-long value is 400 `VALIDATION_ERROR`. The row keeps its amount,
  target, component, and `createdAt` and gains `reversedAt`/`reversalReason`; the
  released amount no longer counts toward the active allocated total and can
  fund a later create. The payment status does not gate a reversal. An unknown
  or foreign payment is 404 `PAYMENT_NOT_FOUND`; an unknown allocation, an
  allocation under another payment, or another tenant's allocation is 404
  `ALLOCATION_NOT_FOUND`; a repeat, including a concurrent repeat, is 409
  `ALLOCATION_ALREADY_REVERSED` with no second write and no second event.
- A missing or unknown body member is 400 `VALIDATION_ERROR` with per-field
  details. A missing tenant is 400 `MISSING_TENANT_HEADER`; a malformed tenant
  or `paymentId` is 400 `INVALID_PARAMETER`.
- The create returns the allocation and writes `payment.allocation.created` in
  the same transaction. The allocation is a child aggregate: the envelope
  carries the allocation id as the `PaymentAllocation` aggregate at version 1,
  while the payload carries the parent payment identity, the allocation fields,
  and the payment-level `totalAllocated`/`paymentAmount` totals. Because an
  allocation never bumps the payment row version, using the allocation id keeps
  the outbox aggregate-version key unique when one payment receives several
  allocations. The accepted reversal writes `payment.allocation.reversed` in the
  same transaction, advancing the same `PaymentAllocation` aggregate to version
  2; its payload is `{paymentId, allocationId, targetType, targetId, component,
  amount, reason, reversedAt}`.
- The expert serves the same public paths and an `/internal/v1` alias that the
  domain calls; the alias is an implementation detail and is not part of the
  public contract. The SPEC 11.7.11 table lists only the GET, and SPEC 11.7.10
  has no allocation event name; the POST, the reverse POST, and the two
  `payment.allocation.*` events are new names recorded in M-22 and M-35.

### Payment status transitions

`PATCH /api/v1/payments/{paymentId}/status` is the public generic lifecycle
command. The body is `{status, expectedVersion?, reason?}`. `X-EIA-Tenant` is
required and the route is tenant-scoped but not book-scoped, like the rest of
the Payment slice (M-08, M-12). The four named actions (`/submit`,
`/authorize`, `/approve`, and `/issue`) remain available; the PATCH route is
the expert's general transition command.

| Response | When |
|---|---|
| 200 `Payment` | The transition is accepted. The payment `version` is bumped and `payment.payment.updated` and `payment.payment.status-changed` are written in the same transaction. |
| 400 `INVALID_STATUS` | `status` is unknown after trimming and upper-casing. |
| 400 `INVALID_STATUS_TRANSITION` | The edge is not in the graph, or it repeats the current or a terminal status. |
| 400 `PAYMENT_NOT_APPROVED` | A pre-approval status requests an execution status. |
| 400 `VALIDATION_ERROR` | `status` is missing or blank, or the body is malformed. |
| 404 `PAYMENT_NOT_FOUND` | The payment does not exist in the caller's tenant. |
| 409 `CONCURRENT_MODIFICATION` | The supplied `expectedVersion` does not match the payment `version`. |
| 400 `MISSING_TENANT_HEADER` / `INVALID_PARAMETER` | The tenant header is missing or malformed. |
| 502 `EXPERT_UNAVAILABLE` | The domain cannot reach the expert. |

The implemented graph:

| From | Allowed to |
|---|---|
| `DRAFT` | `PENDING_AUTHORITY`, `CANCELLED`, `VOID` |
| `PENDING_AUTHORITY` | `AUTHORIZED`, `REJECTED`, `CANCELLED`, `VOID` |
| `AUTHORIZED` | `APPROVED`, `CANCELLED`, `VOID` |
| `APPROVED` | `SCHEDULED`, `STOPPED`, `VOID` |
| `SCHEDULED` | `SUBMITTED`, `CANCELLED`, `VOID` |
| `SUBMITTED` | `ACCEPTED`, `FAILED` |
| `ACCEPTED` | `PROCESSING`, `FAILED` |
| `PROCESSING` | `PAID`, `PARTIALLY_PAID`, `FAILED` |
| `PARTIALLY_PAID` | `PAID`, `RETURNED`, `REVERSED` |
| `PAID` | `RECONCILED`, `RETURNED`, `REVERSED` |
| `RETURNED` | `SCHEDULED`, `CANCELLED` |
| `FAILED` | `SCHEDULED`, `CANCELLED` |
| `RECONCILED` | `ESCHEATED` |

`CANCELLED`, `STOPPED`, `REJECTED`, `VOID`, `REVERSED`, and `ESCHEATED` are
terminal: no outgoing edge exists, so any later command, including a replay of
the same terminal status, is 400 `INVALID_STATUS_TRANSITION`. `PARTIALLY_PAID`
is not terminal and can still move to `PAID`, `RETURNED`, or `REVERSED`.

`status` is required, trimmed, and upper-cased. The approval gate runs before
the graph: `DRAFT`, `PENDING_AUTHORITY`, and `AUTHORIZED` may not jump directly
to an execution status (`SUBMITTED`, `ACCEPTED`, `PROCESSING`, `PAID`,
`PARTIALLY_PAID`, `RECONCILED`, or `ESCHEATED`), and such a request is 400
`PAYMENT_NOT_APPROVED`. `expectedVersion` is optional: when supplied, a stale
value is 409 `CONCURRENT_MODIFICATION` and writes nothing; when omitted, the
transition is not version-checked. `reason` is optional and capped at 200
characters; it is trimmed and stored as the latest status reason, which the
updated `Payment` returns as `statusReason`. Each accepted change replaces the
value, and a change without a reason clears it, so a payment that has never
transitioned, or whose latest change carried no reason, returns null. An
over-long reason is 400 `VALIDATION_ERROR` before the transition and version
checks and writes nothing; the named actions replace the value with their own
fixed text.

The graph is wider than the SPEC 11.7.6 mermaid: it adds the CANCELLED/VOID
escape edges, `SUBMITTED`/`ACCEPTED` -> `FAILED`, `PROCESSING` ->
`PARTIALLY_PAID`, and the `PARTIALLY_PAID` edges. SPEC 11.7.11 also lists only
named actions and no generic status route, and the status write publishes the
generic `payment.payment.updated`/`.status-changed` names rather than the SPEC
per-verb facts; M-22 and M-46 record the differences.

### Notification source linkage

A notification may carry a flat, optional source link to the business record
that caused it:

| Field | Type | Rule |
|---|---|---|
| `sourceType` | enum | `DIRECT_CLAIM`, `ASSUMED_CLAIM`, `POLICY`, `CONTRACT`, `PAYMENT`, or `OTHER`. Required whenever `sourceId` is supplied. |
| `sourceId` | UUID | UUID of the source record. Required for every `sourceType`; null when there is no source link. |
| `sourceReference` | string, max 64 | Human-readable reference, for example `CLM-2026-0000001`. Optional metadata; it never replaces `sourceId`. |

Rules and semantics:

- Both or neither. A supplied `sourceType` without `sourceId` is 400
  `INVALID_SOURCE_LINKAGE` (`EIA-NTF-9410`), and a supplied `sourceId` without
  `sourceType` is the same 400. All six types require an id; `OTHER` is the
  unclassified type but still needs one.
- `sourceType` is trimmed and upper-cased before validation, so
  `direct_claim` selects `DIRECT_CLAIM`. An unknown value is 400
  `INVALID_SOURCE_TYPE` (`EIA-NTF-9409`).
- `sourceReference` is optional. A supplied value is trimmed; a blank value is
  treated as absent, and a value longer than 64 characters is 400
  `INVALID_SOURCE_REFERENCE` (`EIA-NTF-9411`). It may accompany the pair or
  stand alone, but it never substitutes for `sourceId`.
- The link is deliberately denormalized. It lets a notification list or record
  render and cross-link the source without an N+1 lookup, but it is not a
  foreign key: there is no existence check against the source vertical and
  `sourceId` is not resolved before create.
- The SPEC 11.8.4 `subject_vertical`/`subject_type`/`subject_id`/
  `subject_business_key` columns and the SPEC 12.5.5 `subject` EntityRef remain
  planned. The implemented flat link covers the correlation need without the
  typed subject object; `MISMATCHES.md` M-53 records the difference.
- The `notifications.notification.created` and `.sent` payloads carry the
  optional link in their `data` object. Each present member is emitted and all
  three are omitted when the notification is unlinked; `eventVersion` stays 1.

### Policy billing

Policy owns the premium installment plan (SPEC 11.2.13). The public billing
surface is a domain proxy over the Policy expert; the expert also exposes the
same resource under `/internal/v1/policies/{policyId}/billing` for the domain
adapter, but that internal route is not part of the public contract.

| Operation | Path | Success | Errors |
|---|---|---|---|
| Read plan | `GET /api/v1/policies/{policyId}/billing` | 200 `BillingPlan` | 400, 404 |
| Create plan | `POST /api/v1/policies/{policyId}/billing` | 201 `BillingPlan` | 400, 404, 409 |
| Adjust plan | `POST /api/v1/policies/{policyId}/billing/adjustment` | 201 `BillingAdjustmentResult` | 400, 404, 409 |
| Settle installment | `PATCH /api/v1/policies/{policyId}/billing/installments/{installmentId}` | 200 `Installment` | 400, 404, 409 |

The plan projection is flat and uses the domain DTO names: `planId`,
`planNumber`, `policyId`, `totalPremium` (decimal string), `currency`,
`installmentCount`, `frequency`, `firstDueDate`, `status`, `installments[]`,
and `summary`. Each installment is `installmentId`, `installmentNumber`,
`dueDate`, `amount` (gross decimal string), `creditedAmount`,
`outstandingAmount`, `status`, `paidAt`, and `paymentId`. `amount` stays the
scheduled premium, `creditedAmount` is the sum of applied credit notes, and
`outstandingAmount` is the collectible remainder (`amount - creditedAmount`).
`summary` is `{totalAmount, paidAmount, waivedAmount, creditedAmount,
outstandingAmount, overdueAmount, currency, installmentCount}`; its
`outstandingAmount` nets paid, waived, and credited premium. `paidAt` and
`paymentId` are populated only for PAID; a WAIVED or CREDITED installment has no
payment evidence.

Rules:

- At most one ACTIVE plan exists per policy. The create command takes the
  total and currency from the policy and splits the premium across 1..24
  installments; the first n-1 amounts are equal and the last one absorbs the
  rounding remainder, so the schedule sums exactly to `totalPremium` at scale 4.
  A second ACTIVE plan is 409 `BILLING_PLAN_ALREADY_EXISTS`.
- Plan `frequency` is `MONTHLY`, `QUARTERLY`, `SEMI_ANNUAL`, or `ANNUAL`; the
  due-date cadence applies that step to `firstDueDate`. A blank or unknown
  frequency is 400 `INVALID_BILLING_FREQUENCY`.
- Installment `status` is `DUE`, `OVERDUE`, `PAID`, `WAIVED`, or `CREDITED`.
  PAID, WAIVED, and CREDITED are terminal. CREDITED is reached only by applying
  credit notes, never by the settle command. The settle command accepts only
  the terminal targets `PAID` and `WAIVED`; a DUE or OVERDUE row can be settled
  once. Repeating the same terminal status returns the unchanged row and writes
  no event; switching terminal statuses, or settling a CREDITED row, is 409
  `INSTALLMENT_ALREADY_SETTLED`.
- Applying a credit note to an installment is documented in the credit-note
  section: a partial credit leaves a DUE/OVERDUE row open with a reduced
  `outstandingAmount`, and a full credit sets `CREDITED` with a zero
  outstanding amount. CREDITED rows are excluded from the receivables queue and
  reject dunning with 409 `INSTALLMENT_NOT_DUNNABLE`.
- The adjustment command appends one DUE installment for the positive remainder
  between the policy written premium and the plan's net premium (its total less
  applied credits). The amount is derived, so the body is only
  `{dueDate, reason}`; zero or negative is 400 `NO_PREMIUM_ADJUSTMENT`. An
  absent plan is 404 `BILLING_PLAN_NOT_FOUND`, a non-ACTIVE plan is 409
  `BILLING_PLAN_NOT_ACTIVE`, the 24-installment ceiling is 409
  `MAX_INSTALLMENTS_REACHED`, and a concurrent plan change is 409
  `CONCURRENT_MODIFICATION`. The 201 envelope is
  `{plan, installment, adjustmentAmount, newTotalPremium}`; the plan member
  omits the schedule (`installments` is empty and `summary` is derived from that
  empty list), and the appended row is published separately as `installment`.
- `X-EIA-Tenant` is required. `X-EIA-Book` is optional on the public routes for
  compatibility, but a supplied value must be DIRECT and any other book is
  hidden as 404 `BOOK_SCOPE_VIOLATION` (SPEC 3.6.2, WALL-06). The domain always
  sends DIRECT to the expert.
- The plan create, the adjustment, and each settlement bump the policy row
  version and write `policy.billing-plan.created`,
  `policy.billing-plan.adjusted`, `policy.installment.paid`, or
  `policy.installment.waived` in the same transaction. `Idempotency-Key` and
  `If-Match` are accepted and forwarded by the adjustment route but not
  compared or replayed by the expert, so a retry appends a second installment;
  the other billing commands do not accept them (M-06, M-07).
- The SPEC 11.2.13 `/installments` route and `policy.billing.plan-created`
  event name differ from the implemented `/billing` route and
  `policy.billing-plan.created` name; the two installment facts have no SPEC
  name. The naming difference and the still-unimplemented billing-account,
  instruction, dispute, and commission surfaces are recorded in M-22 and M-27.
  Credit notes are implemented separately at
  `/api/v1/policies/{policyId}/credit-notes` (M-41). The dunning history is
  implemented separately at
  `/api/v1/billing/installments/{installmentId}/dunning` (M-38).

### Policy premium receivables

The cross-policy receivables queue is a separate read over the same billing
tables. It is served at `GET /api/v1/billing/installments`, deliberately
outside `/api/v1/policies`, because it spans every policy in the tenant.

| Operation | Path | Success | Errors |
|---|---|---|---|
| List receivables | `GET /api/v1/billing/installments` | 200 `ReceivableSummary` | 400, 404 |

The summary is `{items, totalAmount, overdueAmount, count}`. An item is
`{installmentId, planId, planNumber, policyId, policyNumber, insuredPartyId,
installmentNumber, dueDate, amount, creditedAmount, outstandingAmount,
currency, status, daysPastDue, paidAt, paymentId}`, matching the domain
`Receivable` DTO. `amount` stays gross, `creditedAmount` is the premium covered
by applied credit notes, and `outstandingAmount` is the collectible remainder.
Only DUE and OVERDUE rows are eligible, so `paidAt` and `paymentId` are null; a
partially credited row stays listed, while a fully CREDITED row is settled and
absent. `totalAmount` and `overdueAmount` sum the outstanding amounts, so
credits reduce the collectible total.

Rules:

- `status` is optional and accepts only DUE or OVERDUE; it is trimmed and
  upper-cased. Another value is 400 `INVALID_INSTALLMENT_STATUS`.
- `dueBefore` is an inclusive due-date cutoff. A malformed value is 400
  `INVALID_PARAMETER`.
- `limit` defaults to 20 and must be 1..200. A non-integer is 400
  `INVALID_PARAMETER`; an integer outside the window is 400 `VALIDATION_ERROR`.
- `X-EIA-Tenant` is required. `X-EIA-Book` is optional for compatibility, but a
  supplied value must be DIRECT; any other book is hidden as 404
  `BOOK_SCOPE_VIOLATION`.
- Items are ordered by `dueDate`, then `policyNumber`, `installmentNumber`, and
  `installmentId`. The read writes no event.
- A partial credit does not remove an installment from the queue: it is still
  collectible for its `outstandingAmount`. Only a fully credited (CREDITED)
  installment drops out.
- The domain proxies the expert's `/internal/v1/billing/installments` read; the
  expert additionally accepts `?tenantId=` for that internal call. Neither is
  part of the public contract.

### Policy installment dunning

Dunning is the collections history of one premium installment (SPEC 11.2.13).
The public surface is a domain proxy over the Policy expert; the expert also
exposes the same resource under
`/internal/v1/billing/installments/{installmentId}/dunning` for the domain
adapter, but that internal route is not part of the public contract.

| Operation | Path | Success | Errors |
|---|---|---|---|
| Read history | `GET /api/v1/billing/installments/{installmentId}/dunning` | 200 `DunningAction[]` | 400, 404 |
| Record action | `POST /api/v1/billing/installments/{installmentId}/dunning` | 201 `DunningAction` | 400, 404, 409 |

`DunningAction` is `{dunningId, installmentId, planId, policyId, level,
channel, notes, status, sentAt}`. `notes` is nullable, `status` is `SENT` or
`CANCELLED`, and `sentAt` is the instant the action was recorded. The request
is `CreateDunningRequest`: `level` and `channel` are required and `notes` is
optional.

Rules:

- `level` is `REMINDER`, `FIRST_NOTICE`, `SECOND_NOTICE`, or `COLLECTIONS`;
  `channel` is `EMAIL`, `LETTER`, or `PORTAL`. Both are trimmed and upper-cased
  before validation, so `first_notice` is accepted as `FIRST_NOTICE`. An unknown
  value is 400 `INVALID_DUNNING_LEVEL` or `INVALID_DUNNING_CHANNEL`; a blank or
  missing one is 400 `VALIDATION_ERROR`.
- `notes` is trimmed and treated as absent when blank. The stored value is
  capped at 2000 characters; a longer value is 400 `INVALID_DUNNING_NOTES`, and
  the expert's `@Size` guard rejects it with a field error before the service
  runs.
- Only an effective DUE or OVERDUE installment can be dunned. A stored DUE row
  past its due date is effectively OVERDUE and stays dunnable; PAID, WAIVED,
  and fully CREDITED installments are terminal, so dunning them is 409
  `INSTALLMENT_NOT_DUNNABLE` with `meta.currentStatus`.
- One action per level per installment is allowed. A repeated level is 409
  `DUNNING_ALREADY_SENT` with `meta.level`, including a level whose history row
  is `CANCELLED`; the unique `(tenantId, installmentId, level)` constraint also
  arbitrates a concurrent first attempt. A concurrent policy change is 409
  `CONCURRENT_MODIFICATION`.
- `X-EIA-Tenant` is required. The operation is a DIRECT-book command: the
  canonical contract requires `X-EIA-Book: DIRECT`, and another book is hidden
  as 404 `BOOK_SCOPE_VIOLATION`. The domain currently accepts an absent header
  for compatibility with the other Policy proxy routes (M-38).
- The accepted action bumps the policy row version and writes
  `policy.dunning.sent` in the same transaction as the row. A rejected action
  writes neither. The command accepts no `Idempotency-Key` or `If-Match`; the
  per-level uniqueness is the retry guard (M-06, M-07).
- The history read returns the action array newest first by `sentAt`, then
  record time, then `dunningId`. An installment with no action returns `[]`, not
  404. The read writes no event.
- The two receivable members `lastDunningLevel` and `lastDunningAt` summarize
  the latest `SENT` action for the installment and are null until the first
  action. CANCELLED history is ignored.
- SPEC 11.2.13 has no public dunning route and no `policy.dunning.sent` name.
  Its dunning model is an internal `POST .../dunning-status` command over the
  SAP-sourced `billing_account` level with the `CLEAR`/`REMINDER`/`DUNNING`/
  `LEGAL`/`BLOCKED` vocabulary, and its published fact is
  `policy.billing.dunning-changed`. The implemented route, level vocabulary, and
  event name are recorded in M-22 and M-38.

### Policy credit notes

Credit notes are policy billing adjustments (SPEC 11.2.13). The public surface
is a domain proxy over the Policy expert; the expert also exposes the same
resource under `/internal/v1/policies/{policyId}/credit-notes` for the domain
adapter, but that internal route is not part of the public contract.

| Operation | Path | Success | Errors |
|---|---|---|---|
| List notes | `GET /api/v1/policies/{policyId}/credit-notes` | 200 `CreditNote[]` | 400, 404 |
| Request note | `POST /api/v1/policies/{policyId}/credit-notes` | 201 `CreditNote` | 400, 404, 409 |
| Advance status | `PATCH /api/v1/policies/{policyId}/credit-notes/{creditNoteId}/status` | 200 `CreditNote` | 400, 404, 409 |

`CreditNote` is `{creditNoteId, noteNumber, policyId, amount, currency, reason,
status, issuedAt, appliedAt, appliedInstallmentId, createdAt, reversedAt,
reversalReason, cancellationId, cancellationNumber}`. `reason` is the optional
creation reason and `reversalReason` is the required reversal text; both are
nullable in the projection. `issuedAt` and `appliedAt` are null until their
transition, `appliedInstallmentId` is null until APPLIED, `reversedAt` and
`reversalReason` are null until REVERSED, and `status` is `DRAFT`, `ISSUED`,
`APPLIED`, `CANCELLED`, or `REVERSED`. `cancellationId` and
`cancellationNumber` link a return-premium note to the cancellation it refunds
and are null for a general billing adjustment; the number is the cancellation's
`CX-{7 digits}` reference. The create body is `CreateCreditNoteRequest`:
`amount` is a positive decimal string and `currency` is required to equal the
policy premium currency; `reason` is optional and capped at 500 characters; and
`cancellationId` is optional and makes the note a cancellation return-premium
credit. The status body is `UpdateCreditNoteStatusRequest`: `status` is
required, `installmentId` is optional but required when `status` is APPLIED, and
`reason` is optional but required when `status` is REVERSED.

Rules:

- The notes are ordered newest first by `createdAt`, then `noteNumber`, and an
  empty list is `[]`, not 404.
- `amount` must be positive. A zero, negative, or missing value is 400
  `VALIDATION_ERROR` from the domain; a positive value that rounds to zero at
  scale 4 is the expert's 400 `INVALID_CREDIT_NOTE_AMOUNT`. A blank or
  malformed currency is 400 `VALIDATION_ERROR` and a well-formed foreign
  currency is 400 `CURRENCY_MISMATCH`. A reason over 500 characters is 400
  `VALIDATION_ERROR`; the expert's `INVALID_CREDIT_NOTE_REASON` is the internal
  backstop.
- A supplied `cancellationId` is resolved on the same tenant and policy (404
  `CANCELLATION_NOT_FOUND`), must still be ACTIVE (409
  `CANCELLATION_NOT_ACTIVE` with `meta.cancellationId` and
  `meta.currentStatus`; a REINSTATED or VOID cancellation cannot fund a note),
  and must match the note: `amount` must equal its `returnPremiumAmount` within
  one cent (400 `CREDIT_NOTE_AMOUNT_MISMATCH`) and `currency` must equal its
  `premiumCurrency` (400 `CURRENCY_MISMATCH`). A cancellation funds at most one
  note, so a second note is 409 `DUPLICATE_CANCELLATION_CREDIT_NOTE` with
  `meta.cancellationId` and, when the existing row is known, `meta.creditNoteId`
  and `meta.noteNumber`; the unique
  `(tenant_id, policy_id, cancellation_id)` key arbitrates a concurrent
  duplicate. A rejected link writes neither the note nor an event.
- `Cancellation` adds the nullable `cancellationNumber` (`CX-{7 digits}`,
  unique per policy); a new cancellation always carries one and a historical row
  may be null. The public domain `CancellationDto` does not yet forward the
  number, which M-41 records; the expert projection returns it.
- The status command accepts only `ISSUED`, `APPLIED`, `CANCELLED`, and
  `REVERSED`. DRAFT and unknown values are 400 `INVALID_CREDIT_NOTE_STATUS`;
  only DRAFT -> ISSUED, DRAFT -> CANCELLED, ISSUED -> APPLIED,
  ISSUED -> CANCELLED, and APPLIED -> REVERSED are allowed. APPLIED, CANCELLED,
  and REVERSED are terminal, so any later edge is 409
  `INVALID_CREDIT_NOTE_TRANSITION` with `meta.currentStatus` and
  `meta.targetStatus`. A concurrent policy change is 409
  `CONCURRENT_MODIFICATION`.
- APPLIED requires `installmentId`. The installment must be DUE or OVERDUE on
  the same tenant and policy, and the note amount must fit inside its
  uncredited remainder (`amount - creditedAmount`). A partial credit raises
  `creditedAmount` and leaves the installment open; a credit that covers the
  remainder also sets `CREDITED` and a zero `outstandingAmount`. The note
  transition and the installment update commit together. A missing id is 400
  `INVALID_CREDIT_NOTE_INSTALLMENT`; an unknown or foreign installment is 404
  `INSTALLMENT_NOT_FOUND`; a PAID/WAIVED/CREDITED target is 409
  `INSTALLMENT_NOT_CREDITABLE` with `meta.installmentId` and
  `meta.currentStatus`; an oversized note is 409
  `CREDIT_NOTE_EXCEEDS_INSTALLMENT` with `meta.creditNoteId`,
  `meta.installmentId`, `meta.noteAmount`, and `meta.availableAmount`; a
  concurrent application is 409 `CONCURRENT_MODIFICATION`. ISSUED and
  CANCELLED ignore the optional `installmentId`.
- REVERSED requires a non-blank `reason` of at most 500 characters; a missing or
  blank value is 400 `INVALID_CREDIT_NOTE_REASON` and a longer value is 400
  `VALIDATION_ERROR`. Reversal is allowed only from APPLIED, so a DRAFT, ISSUED,
  or CANCELLED note, or a repeated reversal, is 409
  `INVALID_CREDIT_NOTE_TRANSITION`. It releases the note amount from
  `appliedInstallmentId`, clamps `creditedAmount` at zero, and reopens a fully
  credited installment as `DUE` or `OVERDUE` when it no longer covers its gross
  amount; a partial credit on an open row just shrinks `creditedAmount`. A
  legacy APPLIED note with a null `appliedInstallmentId` is only marked
  REVERSED. The note row, the release, the policy-version bump, and the event
  commit together.
- The create bumps the policy version and writes `policy.credit-note.created`
  in the same transaction as the note row. The `created` payload is
  `PolicyCreditNoteCreatedData`: the base policy/note identity, `noteNumber`,
  `amount`, `currency`, `status: DRAFT`, and `createdAt`, plus the optional
  `cancellationId`/`cancellationNumber` for a linked note; an unlinked
  adjustment omits both link members. Each accepted transition writes
  `policy.credit-note.issued`, `.applied`, `.cancelled`, or `.reversed` in the
  same transaction as the row and the version bump. The `applied` payload
  additionally carries `installmentId` and the installment's cumulative
  `creditedAmount`; the `reversed` payload is the dedicated
  `PolicyCreditNoteReversedData` carrying `creditNoteId`, `noteNumber`, the
  nullable `installmentId`, `amount`, `reason`, and `REVERSED`. Neither command
  accepts `Idempotency-Key` or `If-Match` (M-06, M-07).
- `X-EIA-Tenant` is required. The canonical contract requires
  `X-EIA-Book: DIRECT` and hides another book as 404 `BOOK_SCOPE_VIOLATION`;
  the domain currently accepts an absent header (M-41).
- SPEC 11.2.13 uses `/api/v1/policy/policies/{policyId}/credit-notes`, the
  REQUESTED/APPROVED/SENT_TO_SAP/ISSUED/REJECTED statuses, a closed reason
  enum, an approval gate, a SAP credit-memo reference, and the
  `policy.billing.credit-note-issued` fact. Its `credit_note_request` has no
  installment column, APPLIED state, reversal, or cancellation link; only the
  BIL-05/BIL-06 obligation to issue a credit or additional invoice and the
  non-negative net outstanding rule apply. The implemented narrow shape, the
  installment application and reversal, the cancellation link, and the five
  new event names are recorded in M-27, M-41, and M-22.

### Policy legal entities

The legal entity catalog is policy master data (SPEC 10.11.2, SPEC 11.2.16).
The public surface is a domain proxy over the Policy expert; the expert also
exposes the same resources under `/internal/v1` for the domain adapter, but
those aliases are not part of the public contract.

| Operation | Path | Success | Errors |
|---|---|---|---|
| List entities | `GET /api/v1/legal-entities` | 200 `LegalEntity[]` | 400, 404 |
| Create entity | `POST /api/v1/legal-entities` | 201 `LegalEntity` | 400, 404, 409 |
| Get entity | `GET /api/v1/legal-entities/{legalEntityId}` | 200 `LegalEntity` | 400, 404 |
| Assign or clear | `PATCH /api/v1/policies/{policyId}/legal-entity` | 200 `Policy` | 400, 404, 409 |

`LegalEntity` is `{legalEntityId, code, name, entityType, jurisdiction,
regulator, licenseNumber, status, createdAt}`. `regulator` and `licenseNumber`
are nullable; `status` is ACTIVE or INACTIVE and a row is created ACTIVE. The
create body is `CreateLegalEntityRequest`; the assignment body is
`UpdatePolicyLegalEntityRequest`, whose nullable `legalEntityId` assigns the
entity and whose null or absent value clears it.

Rules:

- The list is tenant-scoped and bare, newest first; an empty tenant is `[]`.
  There is no search, filter, or page envelope in this slice (M-04).
- `code` is trimmed and upper-cased, at most 32 characters, and unique per
  tenant; a duplicate is 409 `DUPLICATE_LEGAL_ENTITY_CODE`. `name` is trimmed
  and at most 200 characters. `entityType` is INSURER, MGA, CAPTIVE, POOL, or
  FRONTER; `jurisdiction` is a two-letter upper-case ISO 3166-1 alpha-2 code.
  `regulator` is at most 120 characters and `licenseNumber` at most 80; a blank
  optional value is stored as null.
- The assignment checks that the policy and legal entity share the caller's
  tenant. An unknown policy or entity is 404 `POLICY_NOT_FOUND` or
  `LEGAL_ENTITY_NOT_FOUND`; a concurrent policy change is 409
  `CONCURRENT_MODIFICATION` with the current and expected versions. The
  assignment accepts no `If-Match` or `Idempotency-Key` (M-06, M-07).
- `X-EIA-Tenant` is required. A supplied `X-EIA-Book` must be DIRECT and another
  book is hidden as 404 `BOOK_SCOPE_VIOLATION`; an absent header is accepted for
  compatibility with the other Policy proxy routes (M-43).
- The create writes `policy.legal-entity.created`; the accepted assignment
  writes `policy.policy.legal-entity-assigned`. Both are in the same transaction
  as the row change. The created event is keyed by the `LegalEntity` aggregate
  at version 1; the assignment event is keyed by the policy at its new version
  and carries both sides of the link and `changedFields`.
- SPEC 11.2.16 mounts the catalog at `/api/v1/policy/legal-entities` and LE-01
  requires one issuing legal entity per policy. The implemented short path, the
  reduced entity-type/status vocabulary, and the nullable clear are recorded in
  M-01, M-12, M-13, and M-43.

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
   200/400/404/409 responses, the Direct Claims allocation operations, the
   `AllocationSummary`, `Allocation`, and `CreateClaimAllocationRequest`
   schemas with their field bounds, the 201/200 successes, the 400
   `POLICY_MISMATCH`/`MASS_TORT_YEAR_OUTSIDE_BLOCK` and 409
   `ALLOCATION_EXCEEDS_100` documentation, the four
   erosion fields on `Allocation` and the optional create `limitId`, the
   `AllocationErosionStatus` enum, the
   `POST /api/v1/claims/{claimId}/allocations/{allocationId}/erosion` operation
   with no request body, its tenant and DIRECT book parameters, 200 `Allocation`,
   400 `VALIDATION_ERROR` with the stored-limit guard, 404, and 409 `CONFLICT`
   documentation, the rejection of a public `AllocationErosionRequest` schema,
   and the removal of the implemented allocations paths from
   `x-planned-operations`,
   the `claimantPartyId` filter on the public and expert Direct Claims lists
   with its optional UUID query schema, tenant and DIRECT book parameters,
   retained status filter, and bare `Claim` array response,
   the public and expert settlement payment-link PATCH operations with their
   required `TenantHeader` and `BookHeaderDirect` parameters, the
   `claimId`/`settlementId` path parameters, the required
   `SettlementPaymentRequest` nullable-uuid `paymentId`, the 200 `Settlement`,
   the 400/404/409 responses with `SETTLEMENT_NOT_LINKABLE` and the
   concurrent-change `CONFLICT`, the required-but-nullable
   `Settlement.paymentId`/`paymentLinkedAt`, and the idempotent-repeat and
   event documentation,
   the optional nullable `damagesSought`/`damagesCurrency` pair on
   `Litigation` and `LitigationRequest` with its `dependentRequired` mapping,
   positive-amount and currency patterns, the four litigation create/update
   operations, and the two implemented litigation events with their documented
   payload members and both-or-neither wording,
   the six document association-link operations on
   the public and expert surfaces, the `DocumentLink`, `CreateDocumentLinkRequest`,
   and `DocumentLinkedType` schemas, the `linkedType` + `linkedId` list filter,
   the expert list `q`, and the search `linkedReference` match, the six
   document content operations with their shared `TenantHeader` and
   `documentId` parameter, the required `X-File-Name` and optional
   `Content-Type` upload headers, the binary request and 200 response bodies,
   the `Content-Disposition`, `X-Content-SHA256`, and `X-Content-Version`
   download headers, the `DocumentContent` schema and its field bounds
   (including `currentVersion`, the nullable `deletedAt`, and the derived
   `deleted`), the 400 `EMPTY_CONTENT` and 413
   `FILE_TOO_LARGE` documentation, the bodyless content tombstone with its 204,
   the 404 `CONTENT_NOT_FOUND` and 409
   `DOCUMENT_ON_LEGAL_HOLD`/`CONTENT_ALREADY_DELETED` documentation, the 410
   `CONTENT_DELETED` responses on the current and revision downloads, the two
   content-version operations with
   their `DocumentContentVersion` array and schema, the required positive
   `version` path parameter, the four version-download headers, the
   `CONTENT_VERSION_NOT_FOUND`/`INVALID_PARAMETER` documentation, the three
   document hold/disposition operations with their shared `TenantHeader` and
   `documentId` parameter, the `HoldDocumentRequest.reason` 1..500 bounds, the
   200 `Document` and 400/404/409 responses, the seven hold and disposition
   conflict codes (`HOLD_STATUS_NOT_ALLOWED`, `DOCUMENT_ALREADY_ON_HOLD`,
   `DOCUMENT_NOT_ON_HOLD`, `RETENTION_DATE_REQUIRED`, `RETENTION_NOT_EXPIRED`,
   `DOCUMENT_ON_LEGAL_HOLD`, and `DISPOSAL_STATUS_NOT_ALLOWED`), the nullable
   `Document.holdReason`, `heldAt`, `statusBeforeHold`, and `disposedAt`
   members, the absence of a request body on release and dispose, the
   disposition's automatic content-tombstone wording (`document.content.deleted`
   beside `document.document.disposed`, plus the no-content and
   already-tombstoned no-ops), the disposition reference on both content
   downloads, the metadata and `deletedAt` descriptions, the disposed and
   content-deleted channel descriptions, and the
   removal of the disposition, content, and version paths from
   `x-planned-operations`, the ten search
   operations' shared parameters and `SearchResponse`/400/404 responses, the
   `SearchResponse` and `SearchItem` keys, the required 422/409/428 response
   codes on the Round 5 mutations, the payment source fields and their create
   rules, the optional `sourceType` + `sourceId` list filter on the public and
   expert payment lists with its enum, UUID, tenant parameter, 400 response, and
   `INVALID_SOURCE_TYPE`/`INVALID_SOURCE_FILTER` documentation, the three payment
   allocation operations with their 200/201 successes, the `PaymentAllocation`,
   `PaymentAllocationSummary`, and `CreatePaymentAllocationRequest` schemas and
   their field bounds and enums, the required-but-nullable
   `PaymentAllocation.reversedAt` and 200-character `reversalReason`, the
   `PaymentAllocationSummary.reversedTotal`/`net` members with the gross and net
   wording, the 400/404/409 responses, the 409
   `ALLOCATION_EXCEEDS_PAYMENT`/`PAYMENT_NOT_ALLOCATABLE` documentation, the
   `POST .../allocations/{allocationId}/reverse` operation with its shared
   `TenantHeader` and `paymentId`/`allocationId` parameters, the required
   `ReversePaymentAllocationRequest.reason` with its 200-character cap and trim
   rule, the 200 `PaymentAllocation` and 400/404/409 responses, the 404
   `PAYMENT_NOT_FOUND`/`ALLOCATION_NOT_FOUND`, 400 `VALIDATION_ERROR`/
   `MISSING_TENANT_HEADER`, and 409 `ALLOCATION_ALREADY_REVERSED` documentation,
   the `payment.allocation.reversed` event wording, and the absence of the
   implemented paths from `x-planned-operations`, the public
   payment status PATCH with its shared `TenantHeader` and `paymentId` path
   parameter, the required `UpdatePaymentStatusRequest`, the 200 `Payment` and
   400/404/409 responses, the required-but-nullable 200-character
   `Payment.statusReason` and its latest/trim/clear description, the returned
   status reason on the PATCH description, the 34 documented edges and terminal
   statuses, the `PaymentStatus` enum coverage, the optional `expectedVersion`
   and 200-character `reason` on both transition schemas, the error-code and
   event documentation, and the absence of the status path from
   `x-planned-operations`, the implemented
   `payment.allocation.created` and `payment.allocation.reversed` channels and
   payloads, the three
   Policy billing operations, the optional shared
   `BookHeaderDirectOptional` parameter, the `BillingPlan`, `Installment`,
   `CreateBillingPlanRequest`, and `UpdateInstallmentRequest` schemas and their
   field bounds and enums, the cross-policy receivable queue with its required
   `TenantHeader` and optional DIRECT book parameter, its DUE/OVERDUE `status`,
   `dueBefore`, default-20 1..200 `limit`, 200 `ReceivableSummary`, 400/404
   responses, and the `Receivable` and `ReceivableSummary` schemas, the
   installment-dunning GET/POST with its required `TenantHeader` and
   `BookHeaderDirect` parameters, its required uuid `installmentId`, the
   `DunningAction` and `CreateDunningRequest` schemas and their field types,
   the level, channel, and status enums, the 200 `DunningAction[]`, the 201
   `DunningAction`, the 400/404/409 responses, the
   `INSTALLMENT_NOT_DUNNABLE`/`DUNNING_ALREADY_SENT` documentation, and the
   nullable `Receivable.lastDunningLevel` and `Receivable.lastDunningAt`
   members, the Policy
   renewal operation with its required
   `TenantHeader` and `BookHeaderDirect` parameters, the `RenewPolicyRequest`
   required/optional field split, the 201 successor `Policy` with the shared
   `ETag`, the 400/404/409 responses with `RENEWAL_NOT_ALLOWED` on the 409, the
   nullable `Policy.renewedFromPolicyId` lineage field, the mass tort profile
   GET/PUT with its required `TenantHeader` and optional DIRECT book parameter,
   the `MassTortProfile` and `UpdateMassTortProfileRequest` schemas, the four
   mass tort enum schemas, the 200/201/400/404/409 responses, the rejection of
   the implemented route in `x-planned-operations`, the three public
   period-bordereau operations with their required `TenantHeader` and
   `BookHeaderAssumed` parameters, the `Bordereau`, `BordereauStatus`,
   `CreateBordereauRequest`, and `UpdateBordereauStatusRequest` schemas and
   their field types, the nullability of `notes`/`technicalAccountId`, the
   `PROCESSED`/`FAILED` request enum, the 201/200 successes, and the
   400/404/409 responses, the three public technical-account operations with
   their required `TenantHeader` and `BookHeaderAssumed` parameters, the
   `TechnicalAccount` projection and its nullable 120-character
   `settlementReference`, the optional nullable 120-character
   `UpdateTechnicalAccountStatusRequest.reference` with its conditional
   non-blank SETTLED requirement, the `ISSUED`/`SETTLED` request enum, the 400
   `INVALID_REFERENCE` documentation, the 201/200 successes, and the
   400/404/409 responses, the three public cash-call operations with their
   required `TenantHeader` and `BookHeaderAssumed` parameters, the `CashCall`,
   `CashCallStatus`, `CreateCashCallRequest`, and
   `UpdateCashCallStatusRequest` schemas and their field types, the nullable
   4000-character `notes` and nullable 120-character `settlementReference`, the
   optional nullable 120-character status `reference` with its conditional
   non-blank SETTLED requirement, the `ISSUED`/`SETTLED`/`CANCELLED` request
   enum, the 400 `INVALID_REFERENCE` documentation, the
   201/200 successes, and the 400/404/409 responses, the three public security
   operations with their required `TenantHeader` and `BookHeaderAssumed`
   parameters, the ten-field `SecurityRecord` projection, the
   `CreateContractSecurityRequest` required/optional split that rejects a
   caller `status`, the `UpdateContractSecurityStatusRequest` two-value
   `RELEASED`/`EXPIRED` enum, the status path and `securityId` parameter, the
   200 `SecurityRecord` and 400/404/409 responses, the
   `INVALID_STATUS`/`INVALID_STATUS_TRANSITION` and terminal/`BREACH` rules,
   the `SecurityStatus` enum with `ACTIVE` and `OUTSTANDING`,
   the 201/200 successes and 400/404/409 responses, the four documented
   security conflict codes, the two technical-account line paths and their
   GET/POST/DELETE operations with the required `TenantHeader` and
   `BookHeaderAssumed` parameters, the `contractId`/`accountId`/`lineId` path
   parameters, the `TechnicalAccountLine`, `TechnicalAccountLineType` (the 13
   detail types with the retired aggregate `LOSS` excluded), `LineSummary`,
   `TechnicalAccountLineTotals` (four required bucket members plus the optional
   13-key `details` map), and `CreateTechnicalAccountLineRequest` schemas and
   their field types, enums, and text bounds, the 200/201/204 successes, the
   400/404/409 responses with `ACCOUNT_NOT_EDITABLE`, the issue-time
   `ACCOUNT_LINES_DO_NOT_RECONCILE` documentation and the four-bucket/header
   mapping on the status PATCH, the `bucketTotals` normalization on the
   line-list description, and the absence of the implemented line paths from
   `x-planned-operations`, the two credit-note paths and their
   required `TenantHeader` and `BookHeaderDirect` parameters, the fifteen-field
   `CreditNote` projection and five-value `CreditNoteStatus` enum, the positive
   `CreateCreditNoteRequest.amount` pattern, the optional 500-character reason,
   and the optional nullable `cancellationId`, the required-but-nullable
   `CreditNote.cancellationId`/`cancellationNumber` members and the nullable
   `Cancellation.cancellationNumber`, the four-value
   `UpdateCreditNoteStatusRequest` enum with the optional nullable
   500-character `reason` and its conditional REVERSED requirement, the
   201/200/400/404/409 responses, the documented transition, cancellation-link,
   reversal, and event rules,
   the four program operations with their required `TenantHeader` and
   `BookHeaderDirect` parameters, the fourteen-field `Program` projection and
   its nullable capacity pair and non-null usage aggregates, the optional
   `CreateProgramRequest.capacityAmount`/`capacityCurrency` pair with its
   positive-money and three-letter-currency schemas and exact
   `dependentRequired` both-or-neither mapping, the capacity derivation and 400
   `INVALID_PROGRAM_CAPACITY` documentation, and the absence of the implemented
   program paths from `x-planned-operations`,
   the three legal-entity paths and four operations with their required
   `TenantHeader` and optional `BookHeaderDirectOptional` parameters, the
   `LegalEntity`, `LegalEntityType`, `LegalEntityStatus`,
   `CreateLegalEntityRequest`, and `UpdatePolicyLegalEntityRequest` schemas and
   their field bounds, nullability, and enums, the nullable optional
   `Policy.legalEntityId`, the 201 `Location`, the assignment 200 `ETag`, the
   201/200/400/404/409 responses, and the absence of the implemented paths from
   `x-planned-operations`, the premium-audit POST with the shared
   `TenantHeader`, optional DIRECT book, and `IfMatch` parameters, the
   `ApplyPremiumAuditRequest` required/optional split and non-negative money
   pattern, the 201 `Policy` with the shared `ETag`, the 400/404/409/422/428
   responses with `NO_PREMIUM_CHANGE`, `PREMIUM_AUDIT_NOT_ALLOWED`, and
   `CONCURRENT_MODIFICATION`, the auditable-status, version-timeline,
   same-transaction, and event wording, the billing-adjustment POST with the
   shared `TenantHeader`, optional DIRECT book, `IfMatch`, and
   `IdempotencyKey` parameters, the required `BillingAdjustmentRequest`
   `{dueDate, reason}` split and its field bounds, the 201
   `BillingAdjustmentResult` `{plan, installment, adjustmentAmount,
   newTotalPremium}` envelope with the shared `ETag` and
   `Idempotent-Replayed` headers, the 400/404/409 responses with
   `NO_PREMIUM_ADJUSTMENT`, `BILLING_PLAN_NOT_FOUND`,
   `BILLING_PLAN_NOT_ACTIVE`, `MAX_INSTALLMENTS_REACHED`,
   `INVALID_ADJUSTMENT_DUE_DATE`, and `INVALID_ADJUSTMENT_REASON`
   documentation, the derived-delta, transaction, and event wording, and the
   absence of the adjustment path from `x-planned-operations`, and agreement
   between
   `info.version` and `x-compatibility.contractVersion`. It also requires the
   Notifications `NotificationType` member `DUNNING_NOTICE`, its position
   between `ESCHEATMENT_DUE` and `NEW_DOCUMENT_UPLOAD`, no repeated enum value,
   and the `NotificationType` reference on the `Notification` projection and on
   both create commands with `notificationType` required on all three. It also
   requires the four notification-template operations with the shared
   `TenantHeader` and the `status`/`code` list filters, the eleven-member
   `NotificationTemplate` projection, the closed `NotificationTemplateStatus`
   enum, the create and approve request schemas and their field bounds, the
   DRAFT-on-create rule, the 201/200/400/404/409 responses, the
   `TEMPLATE_ALREADY_EXISTS`/`TEMPLATE_ALREADY_ACTIVE`/`TEMPLATE_STATUS_CONFLICT`
   documentation, and the absence of the implemented routes from
   `x-planned-operations`. It also requires the optional nullable notification
   source fields on `Notification`, `CreateNotificationRequest`, and
   `CreateNotificationRequestInternal`, the ordered six-value
   `NotificationSourceType` enum, the nullable UUID `sourceId`, the
   nullable 64-character `sourceReference`, the both-or-neither conditional
   rules, and the `INVALID_SOURCE_TYPE`/`INVALID_SOURCE_LINKAGE`/
   `INVALID_SOURCE_REFERENCE` documentation on both create operations.
4. **AsyncAPI structure.** `asyncapi: 3.0.0`, channel addresses, `x-event-type`,
   `x-status: planned|implemented`, `x-implemented-by` on every implemented
   channel, one `send` operation per channel, a `DomainEvent` message on
   every channel, the implemented `direct.claim.settlement-payment-linked`
   channel with its `claimId`, `settlementId`, `settlementNumber`, `paymentId`,
   and `linkedAt` payload members documented and the unlink omission, the
   optional source fields on the payment created payload,
   the `PaymentAllocationCreatedData` payload with its required payment
   identity, target, component, money, and allocation-total members, the
   `PaymentAllocationReversedData` payload with its required parent payment and
   allocation identity, target, component, released amount, 200-character
   reason, and reversal instant, the
   `PolicyDunningSentData` payload with its required policy, installment,
   level, channel, sent-at, and status members, the
   `PolicyMassTortProfileUpdatedData` payload with its required
   identity, status, tort, trigger, allocation, and coverage-block members,
   the `DocumentContentUploadedData` payload with its required document
   identity, revision, filename, MIME type, size, and digest members, the
   `DocumentContentDeletedData` payload with its exact six members (document
   identity and number, retained filename, size, digest, and `deletedAt`) and
   no MIME type or revision, the
   `DocumentLifecycleData` payload with its required document identity, reason,
   and status members for the hold, release, and disposition facts, and
   the `ContractSecurityData` payload with its contract/security identity,
   type, money, currency, and status members, and the
   `ContractSecurityStatusChangedData` payload with its contract/security
   identity, type, previous-status, and status members, the
   `ContractCashCallData` payload with its contract and cash-call identity,
   period, amount, currency, due date, status, and optional settlement
   reference members, the
   `ContractTechnicalAccountData` payload with its contract/account identity,
   period, currency, balance, status, and optional settlement reference
   members, the
   `ContractTechnicalAccountLineData` payload with its contract, account, line,
   13-value detail type enum, and amount members, the
   `PolicyCreditNoteData` payload with its policy and note identity, note
   number, amount, currency, and status members, the
   `PolicyCreditNoteCreatedData` payload with its DRAFT status, `createdAt`, and
   optional nullable cancellation-link members, the
   `PolicyCreditNoteReversedData` payload with its note identity and number,
   nullable released installment, amount, required reason, and REVERSED status
   members, and the
   `PolicyLegalEntityCreatedData` and
   `PolicyPolicyLegalEntityAssignedData` payloads with their catalog-row,
   enum, nullable-link, changed-fields, and policy/money members, the
   `PolicyPremiumAuditedData` payload with its policy identity, previous and
   audited premium, signed delta, currency, effective date, and reason members,
   the `PolicyBillingPlanAdjustedData` payload with its policy and plan
   identity, derived adjustment amount, resulting gross plan total, appended
   installment identity, number, and due date, and trimmed reason members,
   and the
   `NotificationTemplateData` payload with its template identity, code,
   template version, locale, status, and nullable approver members for the
   created, approved, and retired facts, and the `NotificationCreatedData` and
   `NotificationSentData` payloads with their optional `sourceType`,
   `sourceId`, and `sourceReference` members on the two notification facts.
5. **Event catalog cross-check.** The published set in `event-catalog.yaml`
   must equal the channel addresses in the matching vertical document, event
   names must be unique across the platform and must match
   `{vertical}.{aggregate}.{verb}`, every consumed event must have a publisher,
   and the catalog `implemented` list must equal the channels marked
   `x-status: implemented`. The implemented event names for all ten publishing
   verticals are required explicitly, including `direct.claim.assigned`,
   `direct.claim.allocation-created`, `direct.claim.settlement-payment-linked`,
   `direct.claim.litigation-created`, `direct.claim.litigation-updated`,
   `assumed.claim.assigned`,
   `document.link.added`,
   `document.link.removed`, `document.content.uploaded`,
   `document.content.deleted`,
   `document.legal-hold.placed`, `document.legal-hold.released`,
   `document.document.disposed`,
   `policy.policy.renewed`,
   `policy.policy.premium-audited`,
   `policy.billing-plan.created`, `policy.billing-plan.adjusted`,
   `policy.installment.paid`,
   `policy.installment.waived`, `policy.dunning.sent`,
   `policy.mass-tort-profile.updated`,
   `payment.allocation.created`,
   `payment.allocation.reversed`,
   `notifications.template.created`, `notifications.template.approved`,
   `notifications.template.retired`,
   `contract.bordereau.received`, `contract.bordereau.processed`,
   `contract.bordereau.failed`, the four `contract.cash-call.*` facts
   (`requested`, `issued`, `settled`, and `cancelled`),
   `contract.security.recorded`, `contract.security.status-changed`,
   `contract.technical-account.line-added`,
   `contract.technical-account.line-removed`,
   `policy.credit-note.created`, `policy.credit-note.issued`,
   `policy.credit-note.applied`, `policy.credit-note.cancelled`,
   `policy.credit-note.reversed`,
   `policy.legal-entity.created`, and
   `policy.policy.legal-entity-assigned`. The Document document must also keep
   the two content events `document.content.uploaded` and
   `document.content.deleted` as its complete `document.content.*` set, so a
   content slice cannot add an event name silently.
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
- a payment can be split through the flat allocation surface
  `GET/POST /api/v1/payments/{paymentId}/allocations` and a split can be
  reversed through `POST .../allocations/{allocationId}/reverse`. The
  allocation records a target type and component but does not resolve or
  validate the target record, accepts zero or partial allocations instead of
  enforcing PAY-06's exact-sum rule, and carries no book. A reversal stamps the
  row instead of deleting it and reports the gross `totalAllocated`, the
  `reversedTotal`, and the net `net`/`unallocated`; the slice publishes the new
  `payment.allocation.created` and `payment.allocation.reversed` names. SPEC
  11.7.11 lists only the GET, SPEC 11.7.10 has no allocation event, and SPEC
  3.6.1 requires the book on every allocation (M-22, M-35);
- the public payment status command is a SPEC-less `PATCH /{id}/status` route
  (SPEC 11.7.11 lists only named actions). The implemented graph is wider than
  the SPEC 11.7.6 mermaid (CANCELLED/VOID escape edges, `SUBMITTED`/`ACCEPTED`
  -> `FAILED`, `PROCESSING` -> `PARTIALLY_PAID`, and the `PARTIALLY_PAID`
  edges), the contract caps `reason` at the 200-character column width and the
  expert rejects a longer value with 400 `VALIDATION_ERROR`, the payment
  projection returns the latest trimmed `statusReason` but no status history,
  and a status write publishes the generic
  `payment.payment.updated`/`.status-changed` names rather than the SPEC
  per-verb facts (M-22, M-46);
- document associations are implemented as tenant-scoped `/links` with a flat
  `linkedType`/`linkedId` target and no role, book, or DOC-09 target-existence
  check, and publish `document.link.added`/`.removed` rather than the SPEC
  `document.document.associated` (M-22, M-26);
- document content keeps one current raw-byte pointer per document plus an
  append-only revision history
  (`PUT|GET|DELETE /api/v1/documents/{documentId}/content`,
  `GET .../content/metadata`,
  and `GET .../content/versions` plus `GET .../content/versions/{version}`) with
  a 10 MiB cap, SHA-256 verification, the new
  `document.content.uploaded` event, and the new
  `document.content.deleted` tombstone. The tombstone clears the bytes of the
  current and every not-yet-deleted revision, answers 204, keeps the metadata
  with `deletedAt`/`deleted`, hides both downloads as 410 `CONTENT_DELETED`,
  refuses a document under legal hold, and is also applied automatically by a
  disposition that finds live content. SPEC 11.6.10 mounts the history at
  `/versions` and the version-creating command at `POST /versions`, while the
  implemented history is under `/content/versions` and the upload creates the
  revision; the slice has no presigned download, `Range` support, rendition,
  OCR text, package, request, or signature surface, and the SPEC 11.6.9 content
  facts do not exist. A missing tenant on the content routes is still the
  compact `TENANT_REQUIRED` 400 rather than the canonical Problem, and the
  download exposes the stored bytes rather than a short-lived URL (M-02, M-22,
  M-40, M-47);
- Notifications accepts the implemented `DUNNING_NOTICE` type, which SPEC 11.8.5
  v1 does not list. The type is the target of the shell's dunning draft
  hand-off, and the expert still rejects any value outside the closed list
  (M-48);
- notification templates are implemented at the short
  `/api/v1/notifications/templates` resource with list, create DRAFT, approve,
  and retire, while SPEC 11.8.10 mounts `/api/v1/notifications/admin/templates`
  and names a publish command. The three lifecycle facts
  `notifications.template.created`/`.approved`/`.retired` have no SPEC 11.8.9
  name, and a template is channel-neutral when `channel` is null (M-22, M-49);
- a notification carries a flat `sourceType`/`sourceId`/`sourceReference` link
  rather than the SPEC 11.8.4 `subject_vertical`/`subject_type`/`subject_id`/
  `subject_business_key` columns and the SPEC 12.5.5 `subject` EntityRef. The
  link has no referential-integrity check against the source vertical. All six
  source types require a `sourceId`, while a reference-only link is accepted;
  the created and sent facts carry the optional members (M-12, M-13, M-53);
- document legal holds and disposition are implemented per document at
  `POST /api/v1/documents/{documentId}/hold`, `.../hold/release`, and
  `.../dispose`, with the new `document.legal-hold.placed`/`.released` events
  and the SPEC `document.document.disposed` event. SPEC 11.6.10 models a hold
  collection with scope, approval, and release by hold id, and SPEC 11.6.8
  requires an approved disposition job plus a certificate and content deletion;
  the implemented hold is per-document and synchronous, disposition is an
  immediate tombstone with no certificate, and it applies the same content
  tombstone when live content exists (a content-free or already-tombstoned
  disposition emits only the disposed fact). `statusBeforeHold` also admits
  CLASSIFIED and SUPERSEDED, wider than the SPEC ACTIVE/ARCHIVED hold states
  (M-22, M-44, M-47);
- claim assignment is implemented on both claim verticals but has no SPEC 11.4.10
  or 11.5.10 route or SPEC 11.4.9/11.5.9 event name. The Assumed Claims domain
  still requires a team the contract and expert make optional, the Direct Claims
  expert returns 409 instead of 400 for a negative `expectedVersion`, and the
  Direct Claims expert accepts `X-EIA-User` as an extra actor alias (M-22,
  M-25);
- Direct Claims allocations are implemented under
  `/api/v1/claims/{claimId}/allocations` and publish
  `direct.claim.allocation-created`, while SPEC 11.4.9 names the fact
  `direct.claim.allocated`. The domain also collapses the expert's stable 400
  `POLICY_MISMATCH` and 409 `ALLOCATION_EXCEEDS_100` to `VALIDATION_ERROR` and
  `CONFLICT` at the public surface, while the domain's own 400
  `MASS_TORT_YEAR_OUTSIDE_BLOCK` coverage-block guard is preserved. The create
  reads the policy mass-tort profile and fails open when the profile is DRAFT,
  absent, or unavailable, so a Policy outage can let a year through that SPEC
  11.4.7 `DIR-15` would reject (M-32). Allocation erosion is a bodyless public
  `POST .../{allocationId}/erosion` retry; the canonical contract documents 409
  `CONFLICT` when the retry would change an already-`POSTED` allocation and a
  200 with the recorded state, but the public domain currently catches the
  expert 409 and the expert record-write failure and returns the pre-update
  allocation with 200 (M-22, M-31, M-36);
- Direct Claims settlement payment links are implemented at
  `PATCH /api/v1/claims/{claimId}/settlements/{settlementId}/payment` and the
  expert alias, storing one optional Payment id on the settlement and publishing
  `direct.claim.settlement-payment-linked`. SPEC 11.4.10 has no link operation
  and SPEC 11.4.9 names no link fact; SPEC 11.4.4 instead models `payment_id`
  as a Payment projection and adds a `PAID` settlement status. The implemented
  link is owned by the Direct Claims expert, calls no Payment service, and the
  public domain collapses the expert's stable `SETTLEMENT_NOT_LINKABLE` code to
  409 `CONFLICT` (M-22, M-45);
- Direct Claims litigation matters carry an optional `damagesSought` /
  `damagesCurrency` pair that SPEC 11.4.4 `claim_litigation` does not define, and
  they publish `direct.claim.litigation-created` although SPEC 11.4.9 names only
  `direct.claim.litigation-updated`. The pair is both-or-neither, the amount
  must be greater than zero, and a PATCH that omits both keeps the stored pair.
  The public domain's request validation admits a zero amount or a one-sided
  pair and relies on the expert's 400 `VALIDATION_ERROR` (M-22, M-52);
- Policy billing is implemented under `/api/v1/policies/{policyId}/billing`
  with the flat `BillingPlan`/`Installment` projection, while SPEC 11.2.13 names
  the route `/installments` and defines the plan event as
  `policy.billing.plan-created`; the installment paid and waived facts have no
  SPEC name. Billing accounts, instructions, disputes, and commission
  statements remain unimplemented (M-12, M-22, M-27);
- policy credit notes are implemented at
  `GET/POST /api/v1/policies/{policyId}/credit-notes` and
  `PATCH .../{creditNoteId}/status` with the
  DRAFT/ISSUED/APPLIED/CANCELLED/REVERSED lifecycle and the new
  `policy.credit-note.created`, `.issued`, `.applied`, `.cancelled`, and
  `.reversed` events. A create may name an ACTIVE cancellation on the same
  tenant and policy; the note must refund that cancellation's return premium
  within one cent in the cancellation currency, and a cancellation funds at most
  one note (409 `DUPLICATE_CANCELLATION_CREDIT_NOTE`). The projection exposes
  `cancellationId`/`cancellationNumber`, and `Cancellation` gains the nullable
  `CX-{7 digits}` `cancellationNumber`. Reversal requires a free-text reason,
  releases the applied credit from the recorded installment, clamps
  `creditedAmount` at zero, and reopens a fully credited row as DUE or OVERDUE.
  SPEC 11.2.13 names the short-form request route
  `/api/v1/policy/policies/{policyId}/credit-notes`, uses the
  REQUESTED/APPROVED/SENT_TO_SAP/ISSUED/REJECTED statuses with a closed reason
  enum, an approval gate, and a SAP credit-memo reference, publishes only
  `policy.billing.credit-note-issued`, and defines no cancellation link,
  APPLIED state, reversal, or creation fact. The implemented lifecycle is
  narrower on the approval/SAP side but wider with APPLIED, REVERSED, and the
  cancellation link, the reason is free text capped at 500 characters, the
  public domain cancellation projection does not yet forward
  `cancellationNumber`, and the domain accepts an absent `X-EIA-Book` although
  the canonical contract requires DIRECT (M-22, M-41);
- installment dunning is implemented as a per-installment history and command at
  `GET/POST /api/v1/billing/installments/{installmentId}/dunning` with the
  `REMINDER`/`FIRST_NOTICE`/`SECOND_NOTICE`/`COLLECTIONS` level vocabulary and
  the new `policy.dunning.sent` event. SPEC 11.2.13 has no public dunning route,
  models dunning as an internal `POST .../dunning-status` command over the
  SAP-sourced `billing_account` level, and publishes
  `policy.billing.dunning-changed`. The canonical contract requires
  `X-EIA-Book: DIRECT` while the domain accepts an absent header, and the
  command has no `Idempotency-Key`/`If-Match`; M-22 and M-38 record the
  differences;
- policy legal entities are implemented at the short
  `GET/POST /api/v1/legal-entities` and
  `GET /api/v1/legal-entities/{legalEntityId}` paths plus
  `PATCH /api/v1/policies/{policyId}/legal-entity`, while SPEC 11.2.16 mounts
  the catalog at `/api/v1/policy/legal-entities` and defines no assignment
  command. The catalog uses a five-value type set
  (`INSURER`/`MGA`/`CAPTIVE`/`POOL`/`FRONTER`) with ACTIVE/INACTIVE and a
  two-letter jurisdiction, narrower than SPEC 10.11.2's wider type set,
  LIQUIDATING status, three-letter domicile country, and finance/effective-dating
  columns; `Policy.legalEntityId` is nullable and clearable although LE-01
  requires one issuing entity. The two new event names have no SPEC equivalent
  (M-01, M-12, M-13, M-22, M-43);
- the program catalog is implemented at the short `GET/POST /api/v1/programs`
  and `GET /api/v1/programs/{programId}` paths, with
  `PATCH /api/v1/policies/{policyId}/program` as the membership command, while
  SPEC 11.2.10 mounts only a read-only catalog at `/api/v1/policy/programs`.
  The implemented vocabulary is `CAPTIVE`/`POOL`/`FRONTING`/`COINSURANCE`/
  `MASS_TORT` and ACTIVE/CLOSED instead of the SPEC 10.11.3
  `CASUALTY`/`PROPERTY`/`COMMERCIAL`/`AUTO`/`SPECIALTY`/`OTHER` and
  ACTIVE/INACTIVE sets, uses a generated `programNumber` instead of `code`, and
  omits the owner legal entity, manager organization unit, description,
  `program_version`, and the SPEC capacity-share structure. The projection does
  model an optional flat `capacityAmount`/`capacityCurrency` pair and derives
  `usedAmount` (the bare sum of the assigned policies' limits),
  `utilizationPct`, and `policyCount`, but it still has no capacity-share rows
  or LE-02 share-sum check, and the public domain reports a capacity
  request-shape failure as 400 `VALIDATION_ERROR` where the canonical contract
  documents 400 `INVALID_PROGRAM_CAPACITY`. The create and assignment are
  SPEC-less commands that publish the new `policy.program.created` and
  `policy.policy.program-assigned` names. `leadPolicyId` is stored without a
  reference or tenant check, and the domain and expert accept an absent
  `X-EIA-Book` although the canonical contract requires DIRECT (M-01, M-22,
  M-39);
- the premium-receivables queue is a tenant-wide read at
  `GET /api/v1/billing/installments`, outside `/api/v1/policies`, and returns the
  flat `Receivable`/`ReceivableSummary` projection. SPEC 11.2.13 describes the
  per-policy installment plan rather than a cross-policy receivable resource, so
  the route and projection are recorded in M-27;
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
- contract cash calls are an interim funding request with a
  REQUESTED/ISSUED/SETTLED/CANCELLED lifecycle, while SPEC 11.3.9 publishes
  only `contract.cash-call.issued` and SPEC 11.3.10 defines no cash-call route.
  The slice has no cash-call limit or `cash_call_allowed` term check, no
  contract-window or contract-currency reconciliation, and no claim or Payment
  link; the domain also accepts an absent `X-EIA-Book` (M-22, M-34);
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
