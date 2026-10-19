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
| `openapi/components.yaml` | Shared parameters, headers, responses, and schemas: canonical `Problem` error envelope, money, offset page envelope, ETag/If-Match, Idempotency-Key, audit fields, entity references, tenant and book headers. |
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

No other vertical emits `ETag` or accepts `If-Match`/`Idempotency-Key`.
Contract bind takes `expectedVersion` and `approvedBy`; the Direct Claims child
PATCH commands take `expectedVersion`; Assumed Claims propagates the expert's
409/422/428; Cession/Retrocession still return 400 for an illegal lifecycle
edge. Their FS-RI hand-off is a separate case: an FS-RI conflict is 409
`FSRI_CONFLICT`, an unusable FS-RI response is 502, and an FS-RI outage is 503.
See `MISMATCHES.md` M-06, M-07, M-11, and M-21.

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
second-slice collections and the Direct Claims and Assumed Claims child
collections. SPEC 7.6 and 12.2 specify a different, cursor-based envelope
(`data`, `page:{size, hasMore, nextCursor, total?}`, `?page[size]` and
`?page[after]`, default 25, maximum 200). The offset form is the implemented
contract; the divergence and the migration choice are recorded in
`MISMATCHES.md` M-04.

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
   slice), the required 422/409/428 response codes on the Round 5 mutations, and
   agreement between `info.version` and `x-compatibility.contractVersion`.
4. **AsyncAPI structure.** `asyncapi: 3.0.0`, channel addresses, `x-event-type`,
   `x-status: planned|implemented`, `x-implemented-by` on every implemented
   channel, one `send` operation per channel, and a `DomainEvent` message on
   every channel.
5. **Event catalog cross-check.** The published set in `event-catalog.yaml`
   must equal the channel addresses in the matching vertical document, event
   names must be unique across the platform and must match
   `{vertical}.{aggregate}.{verb}`, every consumed event must have a publisher,
   and the catalog `implemented` list must equal the channels marked
   `x-status: implemented`. The Round 5 implemented event names are required
   explicitly.
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
- `ETag`/`If-Match` and `Idempotency-Key` exist only in Policy; detail
  `_links` exist nowhere, and Cession/Retrocession still return 400 for an
  illegal lifecycle edge;
- the Cession/Retrocession FS-RI hand-off is synchronous, with no hand-off
  queue or hand-off resource (SPEC 7.18.3/HAND-05);
- six experts publish a subset of their events through the transactional
  outbox, but there is no subscriber or inbox, and the implemented event names
  differ from the SPEC catalog names.

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
