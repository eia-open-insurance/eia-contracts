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

The normative requirements live in `../../SPEC.md`, chiefly sections 6.11
(errors), 7.5 (eventing), 7.6 (API conventions), 10.3 (money), 11.1–11.10
(verticals), 12 (canonical contracts), and 16.9 (repository standard).

## Layout

| Path | Contents |
|---|---|
| `openapi/components.yaml` | Shared parameters, responses, and schemas: canonical `Problem` error envelope, money, cursor pagination, audit fields, entity references, tenant and book headers. |
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
| `x-status` | Object-level status. `planned` means the object is agreed but not implemented. |
| `x-planned-operations` | Routes declared by SPEC 11 but not implemented by the current slice. |
| `x-planned-notes` | Known differences between the SPEC route shape and the implemented route shape. |

Rules:

1. **Implemented endpoints and fields are documented as they exist**, including
   names that differ from the SPEC prose (`effectiveDate`, `documentType`,
   `classification`, `causeCode`).
2. **A field or endpoint that is not implemented is omitted from `paths` and
   schemas** and listed under `x-planned-operations` or in a schema
   description. No schema claims a field the service never returns.
3. **Where the implementation violates a normative SPEC rule** (for example a
   money amount serialized as a JSON number), the canonical schema follows the
   SPEC and `MISMATCHES.md` records the deviation with the exact source
   location. Contracts are the target, not a snapshot of drift.
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
| `X-EIA-Book` | Direct Claims, Assumed Claims, Cession, Retrocession | Required and fixed to the vertical's book. The public services are expected to hide a mismatch as 404 (SPEC 3.6.2). Assumed Claims and Direct Claims do; Cession and Retrocession currently return 400. See `MISMATCHES.md`. |
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
- `correlationId`, `transactionId`, and `meta` are canonical but not emitted by
  every service yet.

The services do not all emit this shape today; `MISMATCHES.md` lists every
variant. The canonical schema is what new work must target.

### Money

`schemas/money.schema.json` defines `Money` as
`{ "amount": "1250000.00", "currency": "USD" }`:

- `amount` is a decimal **string** with at most four fraction digits and is
  never a JSON number.
- `currency` is an ISO 4217 alpha-3 code.
- Zero is valid; negative values only for explicit reversal or return fields.

The current vertical payloads use flat pairs (`premiumAmount`/`premiumCurrency`,
`reserveAmount`/`reserveCurrency`, `cededPremium`/`cededLoss` + `currency`).
Those field names are documented; `MISMATCHES.md` records which services
serialize the value as a number and which already use a string.

### Pagination and collections

The canonical collection envelope is `Page` in `openapi/components.yaml`:
`data`, `page` (`size`, `hasMore`, `nextCursor`, optional `total`), and
`_links`, with `?page[size]` and `?page[after]`. It is marked `planned`.

Every implemented list operation currently returns a bare JSON array. Moving to
the `Page` envelope is a breaking change and requires a new major version or a
compatible opt-in, so the current array shape is documented explicitly.

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
   content types, internal-route security markers, and the complete table of
   required paths and methods per vertical.
4. **AsyncAPI structure.** `asyncapi: 3.0.0`, channel addresses, `x-event-type`,
   `x-status: planned`, one `send` operation per channel, and a `DomainEvent`
   message on every channel.
5. **Event catalog cross-check.** The published set in `event-catalog.yaml`
   must equal the channel addresses in the matching vertical document, event
   names must be unique across the platform and must match
   `{vertical}.{aggregate}.{verb}`, and every consumed event must have a
   publisher.
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

`MISMATCHES.md` is the authoritative list. The largest ones are:

- five different error-body shapes across ten verticals plus a shared-library
  variant;
- money serialized as a JSON number by four services;
- no cursor pagination, `_links`, `ETag`/`If-Match`, or `Idempotency-Key`
  anywhere;
- different book-mismatch status codes between the claim verticals (404) and
  the reinsurance verticals (400);
- no outbox publisher or subscriber, so every AsyncAPI channel is planned.

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
