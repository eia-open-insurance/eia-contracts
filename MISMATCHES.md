# Contract-to-implementation audit

Status: open, reviewed 2026-10-19.

This document records every known difference between the canonical contracts in
this repository and the services that implement them. It is part of the
contract deliverable: the contracts state the agreed shape, and this file states
where the running code does not meet it yet.

## Scope and method

- Specification: `SPEC.md` sections 3.6, 6.11, 7.5, 7.6, 10.3, 11.1–11.10, 12,
  and 16.9.
- Implementation: all twenty vertical service controllers and their clients —
  `eia-party-*`, `eia-policy-*`, `eia-contract-*`, `eia-direct-claims-*`,
  `eia-assumed-claims-*`, `eia-cession-*`, `eia-retrocession-*`,
  `eia-document-*`, `eia-payment-*`, `eia-notifications-*`.
- Gateway routing: `repos/eia-platform/gateway/src/main/resources/application.yml`.
- Method: static review of controller mappings, request and response records,
  `@JsonFormat` annotations, exception handlers, book-wall filters, and
  repositories. No service was started and no database was seeded, so this
  audit proves source-level conformance, not runtime behaviour. Runtime
  conformance remains the contract test of SPEC 12.7.
- Evidence command: `python scripts/validate_contracts.py` (see
  [Validation evidence](#validation-evidence)).

Severity: **H** = a client breaking or a security-relevant difference, **M** =
a visible contract inconsistency, **L** = a naming or documentation difference.

## Summary

| ID | Area | Severity |
|---|---|---|
| M-01 | Public base paths differ from the SPEC vertical tables | M |
| M-02 | Five error-body shapes plus two extra variants | H |
| M-03 | Money serialized as a JSON number by four services — resolved 2026-10-19 | H |
| M-04 | No cursor pagination; lists are bare arrays | H |
| M-05 | No `_links` on detail resources | M |
| M-06 | No `ETag`/`If-Match`; inconsistent `expectedVersion` | H |
| M-07 | No `Idempotency-Key` enforcement | H |
| M-08 | Tenant context is passed three different ways | M |
| M-09 | Book mismatch is 404 in the claim verticals and 400 in the reinsurance verticals — resolved 2026-10-19 | H |
| M-10 | Lifecycle operations use PATCH, POST, and PUT inconsistently | M |
| M-11 | Illegal-transition status codes are inconsistent (400 vs 409 vs 422) | M |
| M-12 | Resource models are narrower than the SPEC aggregates | M |
| M-13 | Field names differ from the SPEC representations | L |
| M-14 | No event publisher, dispatcher, or subscriber | M |
| M-15 | Party domain has no exception mapping — resolved 2026-10-19 | H |
| M-16 | Assumed Claims mounts two public path sets | L |
| M-17 | Error content type is `application/json` in most services | M |
| M-18 | SPEC 12.4 example envelope omits the book required by SPEC 3.6 | L |
| M-19 | SPEC 7.6 base-path rule contradicts the SPEC vertical tables | L |
| M-20 | Audit actor fields (`createdBy`, `updatedBy`) are not returned | L |

## M-01 Public base paths

The implemented public route is the shorter vertical-less form; the SPEC
vertical tables use `/api/v1/{vertical}/{resource}`. The gateway and the web
remotes agree with the implementation, so the SPEC tables are the outlier.

| Vertical | Implemented (and gateway route) | SPEC 11 table |
|---|---|---|
| Party | `/api/v1/parties` | `/api/v1/party/parties` |
| Policy | `/api/v1/policies` | `/api/v1/policy/policies` |
| Contract | `/api/v1/contracts` | `/api/v1/contract/contracts` |
| Direct Claims | `/api/v1/claims` | `/api/v1/direct-claims/claims` |
| Assumed Claims | `/api/v1/assumed-claims` (alias `/api/v1/assumed-claims/claims`) | `/api/v1/assumed-claims/claims` |
| Cession | `/api/v1/cessions` | `/api/v1/cession/contracts` (contracts are a different aggregate) |
| Retrocession | `/api/v1/retrocessions` | `/api/v1/retrocession/contracts` |
| Document | `/api/v1/documents` | `/api/v1/document/documents` |
| Payment | `/api/v1/payments` | `/api/v1/payment/payments` |
| Notifications | `/api/v1/notifications` | `/api/v1/notifications/...` (matches) |

Evidence:

- `repos/eia-party-domain/.../PartyController.java:11` — `/api/v1/parties`
- `repos/eia-policy-domain/.../PolicyController.java:19` — `/api/v1/policies`
- `repos/eia-contract-domain/.../ContractController.java:27` — `/api/v1/contracts`
- `repos/eia-direct-claims-domain/.../ClaimController.java:20` — `/api/v1/claims`
- `repos/eia-cession-domain/.../CessionController.java:18` — `/api/v1/cessions`
- `repos/eia-retrocession-domain/.../RetrocessionController.java:19` — `/api/v1/retrocessions`
- `repos/eia-document-domain/.../DocumentController.java:15` — `/api/v1/documents`
- `repos/eia-payment-domain/.../PaymentController.java:18` — `/api/v1/payments`
- `repos/eia-notifications-domain/.../NotificationController.java:22` — `/api/v1/notifications`
- `repos/eia-platform/gateway/src/main/resources/application.yml:18-48` — the
  same public prefixes are routed.
- Web remotes call the implemented prefixes, for example
  `repos/eia-policy-web/src/App.jsx` (`/api/v1/policies`) and
  `repos/eia-assumed-claims-web/src/App.jsx` (`/api/v1/assumed-claims/claims`).

Resolution: the contracts document the implemented paths. Correct the SPEC
tables to the implemented form, or introduce the namespaced form as `/v2` with a
migration; do not silently rewrite the gateway.

## M-02 Error envelope

The canonical envelope is `Problem` in `schemas/error-envelope.schema.json`
(SPEC 6.11 and 12.2). The services emit five different shapes plus an unused
shared-library variant.

| Vertical | Implemented type | Emitted shape |
|---|---|---|
| Policy (domain and expert) | `com.eia.policy.*.ApiError` | `{timestamp, status, code, message, path, details[{field, message}]}` |
| Direct Claims (domain and expert) | `com.eia.directclaims.*.ApiError` | same as Policy |
| Payment (domain and expert) | `com.eia.payment.*.ApiError` | same as Policy |
| Contract (domain and expert) | `com.eia.contract.*.ApiError` | `{code, message, details[{field, message}]}` |
| Document (domain and expert) | `com.eia.document.*.ApiError` | `{code, message, details[{field, message}]}` |
| Cession (domain and expert) | `com.eia.cession.*.ApiError` | `{code, message, details{field: message}}` |
| Retrocession (domain and expert) | `com.eia.retrocession.*.ApiError` | `{code, message, details{field: message}}` |
| Assumed Claims (domain and expert) | `com.eia.assumedclaims.*.ApiError` | `{type, title, status, detail, instance, code, category, retryable, errors[{field, code, message}]}` |
| Notifications (domain) | Spring `ProblemDetail` plus properties | RFC 9457 body with `code`, `category`, `retryable`, `errors[{field, code, message}]`; no `correlationId`, `transactionId`, or `meta` |
| Party (expert) | inline `Map<String, String>` | `{code, message}` for `NOT_FOUND` only |
| Party (domain) | none | Spring default error body, status 500 for a missing party |
| Shared library | `com.eia.platform.libs.ApiError` | `{code, message, correlationId}`; defined but not used by any vertical |

Evidence:

- `repos/eia-policy-domain/.../ApiError.java:6`, `repos/eia-policy-expert/.../ApiError.java:6`
- `repos/eia-direct-claims-domain/.../ApiError.java:6`, `repos/eia-direct-claims-expert/.../ApiError.java:6`
- `repos/eia-payment-domain/.../ApiError.java:6`, `repos/eia-payment-expert/.../ApiError.java:6`
- `repos/eia-contract-domain/.../ApiError.java:6`, `repos/eia-contract-expert/.../ApiError.java:12`
- `repos/eia-document-domain/.../ApiError.java:12`, `repos/eia-document-expert/.../ApiError.java:12`
- `repos/eia-cession-domain/.../ApiError.java:8`, `repos/eia-cession-expert/.../ApiError.java:8`
- `repos/eia-retrocession-domain/.../ApiError.java:8`, `repos/eia-retrocession-expert/.../ApiError.java:8`
- `repos/eia-assumed-claims-domain/.../ApiError.java:12`, `repos/eia-assumed-claims-expert/.../ApiError.java:12`
- `repos/eia-notifications-domain/.../ApiExceptionHandler.java:97`
- `repos/eia-party-expert/.../ApiExceptionHandler.java:10-14`
- `repos/eia-platform/libs/src/main/java/com/eia/platform/libs/ApiError.java:3`

Resolution: move `Problem` into `eia-platform/libs` as the single error type,
map every `@RestControllerAdvice` to it, and change every service to
`application/problem+json`. Until then these contracts describe the canonical
target, and clients must tolerate the vertical shape in the table.

## M-03 Money representation

SPEC 10.3 and 12.2 require `{amount, currency}` with the amount as a decimal
string and never a JSON number. The implementation uses flat pairs; four
services serialize the number as a JSON number.

| Vertical | Fields | JSON type today | Canonical target |
|---|---|---|---|
| Policy | `premiumAmount`/`premiumCurrency`, `limitAmount`/`limitCurrency` | string (`@JsonFormat(shape = STRING)`) | `Money` object |
| Payment | `amount`/`currency` | string (`@JsonFormat(shape = STRING)`) | `Money` object |
| Direct Claims | `reserveAmount`/`reserveCurrency` | string (`@JsonFormat(shape = STRING)`) | `Money` object |
| Assumed Claims | `reserveAmount`/`reserveCurrency` | string (`@JsonFormat(shape = STRING)`) | `Money` object |
| Cession | `cededPremium`, `cededLoss`, `currency` | string (`@JsonFormat(shape = STRING)`) | two `Money` objects |
| Retrocession | `cededPremium`, `cededLoss`, `currency` | string (`@JsonFormat(shape = STRING)`) | two `Money` objects |

Evidence:

- `repos/eia-policy-expert/.../Policy.java:22,24` and
  `repos/eia-policy-domain/.../PolicyDto.java:19,21` — string format.
- `repos/eia-payment-expert/.../Payment.java:19` and
  `repos/eia-payment-domain/.../PaymentDto.java:16` — string format.
- `repos/eia-direct-claims-domain/.../ClaimDto.java:19`,
  `repos/eia-direct-claims-expert/.../Claim.java:25` — `BigDecimal`, no format.
- `repos/eia-assumed-claims-domain/.../AssumedClaimDto.java:21`,
  `repos/eia-assumed-claims-expert/.../AssumedClaim.java:22` — `BigDecimal`.
- `repos/eia-cession-domain/.../CessionDto.java:15-16`,
  `repos/eia-cession-expert/.../Cession.java:15-16` — `BigDecimal`.
- `repos/eia-retrocession-domain/.../RetrocessionDto.java:15-16` — `BigDecimal`.

The contracts declare the SPEC string form (`MoneyAmount`) and document the
flat field names. This is a wired inconsistency: a client generated from these
contracts will expect strings and receive numbers from four services.

## M-04 Pagination

All list operations return `List<Dto>` directly, for example
`PolicyController.list` (`PolicyController.java:27-30`,
`ClaimController.java:28-34`, `NotificationController.java:31-34`). There is no
`page` object, no `nextCursor`, no `?page[size]`/`?page[after]`, and no
`total`. SPEC 7.6 requires the cursor envelope. The contracts document the
implemented bare array and mark `Page` planned. Introducing pagination later
will be breaking for every current client.

## M-05 Hypermedia links

No detail projection carries `_links`. SPEC 7.6 requires `self`, `collection`,
and typed record links; SPEC 12.5 shows them on policy, claim, payment,
document, and notification representations. The shared `Links` component is
marked planned.

## M-06 Concurrency control

There is no `ETag` response header and no `If-Match` request handling anywhere.
`expectedVersion` in a request body is used inconsistently:

| Operation | Version handling |
|---|---|
| Policy public PATCH | Optional; when absent the domain reads the current version and forwards it (`PolicyService.java:37-40`) |
| Policy expert PATCH | Optional |
| Contract public PATCH | Required (`UpdateStatusCommand.java:8-11`) |
| Direct Claims public PATCH | Not accepted; the domain reads and forwards the current version (`ClaimService.java:37-50`) |
| Direct Claims expert PATCH | Optional (`StatusChangeRequest.java:5-8`) |
| Assumed Claims public POST status | Required (`StatusChangeCommand.java:6-13`) |
| Cession/Retrocession public POST transition | Not accepted; the domain reads and forwards the current version (`CessionService.java:36-43`, `RetrocessionService.java:36-43`) |
| Cession/Retrocession expert PUT status | Required `version` |
| Document public POST status | Not accepted; the domain forwards the current version (`DocumentService.java:34-38`) |
| Document expert POST status | Optional `expectedVersion` |
| Payment public actions | Not accepted; the domain reads and forwards the current version (`PaymentService.java:37-73`) |

Resolution: implement `ETag`/`If-Match` as required by SPEC 12.6, or promote
`expectedVersion` to a mandatory request field on every mutation and document
it. The contracts document the implemented body field where it exists.

## M-07 Idempotency

`Idempotency-Key` is not accepted, validated, persisted, or replayed by any
create operation. `Idempotent-Replayed` is not emitted. SPEC 12.3 and 12.6
require the header on transaction submission. The shared parameter is marked
planned.

## M-08 Tenant context

Three mechanisms coexist:

| Route family | Mechanism |
|---|---|
| Public routes | `X-EIA-Tenant` header |
| Party, Policy, Contract, Cession, Retrocession, Document, Payment, Notifications experts | `?tenantId=` query parameter, plus `tenantId` in the create body |
| Direct Claims expert status transition | `X-EIA-Tenant` header instead of the query parameter (`ClaimController.java:52-58`) |
| Assumed Claims expert create and status | `tenantId` in the body plus `X-EIA-Tenant` sent by the domain client |

The contracts document each route exactly. A future cleanup should make the
internal tenant a header only, and remove `tenantId` from request bodies.

## M-09 Book wall status code

| Vertical | Missing or wrong `X-EIA-Book` | Evidence |
|---|---|---|
| Direct Claims (public and expert) | 404, `NOT_FOUND` | `RequestGuard.java:13-17`, `BookWall.java:11-15` |
| Assumed Claims (public and expert) | 404, `EIA-RNS-7005` | `BookScopeFilter.java:36-43` in both services |
| Cession | 400 `BOOK_REQUIRED`; 404 `BOOK_SCOPE_VIOLATION` | `RequestScope.java:28-35` |
| Retrocession | 400 `BOOK_REQUIRED`; 404 `BOOK_SCOPE_VIOLATION` | `RequestScope.java:28-35` |

SPEC 3.6.2 requires a mismatch to be returned as 404 so the response cannot
confirm existence. Cession and Retrocession now hide a wrong book as 404; a
missing header still returns 400 `BOOK_REQUIRED`. The contracts document this.

## M-10 Lifecycle method inconsistency

The same conceptual operation is exposed with four shapes:

- `PATCH /{id}/status` — Policy, Contract, Direct Claims, Payment expert.
- `POST /{id}/status` — Assumed Claims, Document.
- `PUT /{id}/status` — Cession, Retrocession expert.
- `POST /{id}/transition` — Cession, Retrocession public.
- Named action POSTs — Payment public `/submit`, `/authorize`, `/approve`, `/issue`.

The contracts record the implemented method per route. A future harmonization
should use one action-on-a-sub-resource convention, preferably
`POST /{id}/{action}` for lifecycle commands, as SPEC 6.1 does for
transactions.

## M-11 Illegal-transition status codes

| Service | Status | Code |
|---|---|---|
| Direct Claims | 400 | `VALIDATION_ERROR` |
| Policy | 400 | `INVALID_STATUS_TRANSITION` |
| Contract | 409 | `INVALID_STATUS_TRANSITION` |
| Assumed Claims | 409 | `EIA-RNS-7003` |
| Document | 400 | `INVALID_STATUS_TRANSITION` |
| Cession / Retrocession | 400 | `INVALID_STATUS_TRANSITION` |
| Payment | 400 | `INVALID_STATUS_TRANSITION` / `PAYMENT_NOT_APPROVED` |

SPEC 6.11 maps `CONFLICT` to 409 and `BUSINESS_RULE` to 422. One vertical uses
409, five use 400, none use 422. Standardize on 409 for a version or state
conflict and 422 for a domain policy rejection, then update the contracts.

## M-12 Resource model gaps

The implemented aggregates are deliberate first slices. The contracts omit the
unimplemented fields and list the missing operations under
`x-planned-operations`. The largest gaps:

- Party: no addresses, roles, relationships, screenings, consents, KYC/AML
  data, or merge. `partyType`, `status`, `sanctionsStatus`, and
  `confidentiality` are unvalidated strings, not SPEC 11.1.5 enums.
- Policy: no `policyType`, `productLine`, `insured` object, `limits[]`,
  `massTort`, `claimSummary`, versions, coverages, occurrences, or programs.
- Contract: no `treatyNumber`, `contractBasis`, inception-date naming, layers,
  participants, terms, cessions, bordereaux, accounts, or security.
- Direct Claims: no `claimType`, `tortCode`, `claimant` object, injury,
  exposure, reserves list, financials, settlements, liens, or recoveries.
- Assumed Claims: no advices, reserves, allocations, recoveries, disputes,
  audits, or cash calls.
- Document: no content, versions, associations, hashes, page count, OCR status,
  tags, holds, packages, requests, or retention class.
- Payment: no `claim`, `payee` object, `netAmount`, `method`, `dueDate`,
  `authority`, SAP postings, allocations, requests, batches, reconciliations,
  or escheatment.
- Notifications: no `category`, `severity`, `subject` reference,
  `requiresAction`, `dueAt`, `actions[]`, inbox, read/acknowledge, stream,
  subscriptions, preferences, or admin surfaces.
- Cession / Retrocession: no contracts, layers, participants, terms, rules,
  cases, hand-offs, confirmations, recoverables, statements, or
  reconciliations.

## M-13 Field naming differences

| Implemented field | SPEC representation |
|---|---|
| Contract `effectiveDate` | Contract `inception_date` / "inception date" |
| Document `documentType` | Document `docType` |
| Document `classification` | Document `confidentiality` |
| Direct Claims `causeCode` | Direct Claims `tortCode` / cause concept |
| Direct Claims `reserveAmount` + `reserveCurrency` | `reserves[{component, amount: Money, asOf}]` |
| Notification `recipientPartyId` + `subject` text | `subject: EntityRef` + `title` |
| Policy `premiumAmount` + `premiumCurrency` | `premium: Money` |
| Assumed Claims `assumedClaimNumber` | `assumed_claim_number` (matches DB, not the SPEC JSON examples) |

The contracts use the implemented names. Renaming any of these is a breaking
change and needs a major version.

## M-14 Eventing

There is no outbox table, dispatcher, inbox, subscription registry, publisher,
or subscriber in any service. Searches for `outbox`, `eventType`, and
`ApplicationEventPublisher` in the Java sources return no implementation.
Every AsyncAPI channel and operation is therefore marked `x-status: planned`,
and `asyncapi/event-catalog.yaml` marks `x-implementation.publisher: none`.

## M-15 Party domain exception handling

Resolved 2026-10-19. `eia-party-domain` now has a `@RestControllerAdvice` and
`PartyClient` translates expert 404 to 404 `NOT_FOUND`, other 4xx to 400 with
the expert code, and 5xx/unreachable to 503 `EXPERT_UNAVAILABLE`. Missing or
malformed `X-EIA-Tenant` returns structured 400 responses. The expert still
returns `{code, message}` for `NOT_FOUND`.

## M-16 Assumed Claims path alias

`AssumedClaimController` is mapped to both
`/api/v1/assumed-claims` and `/api/v1/assumed-claims/claims`
(`AssumedClaimController.java:22`). The web remote calls the `/claims` form.
Both are documented with distinct operation IDs. The duplicate surface should
be reduced to one path; the alias is compatible today because both are
implemented.

## M-17 Error content type

Only Notifications sets `application/problem+json`
(`ApiExceptionHandler.java:110-112`) and only the Assumed Claims book filter
sets it explicitly (`BookScopeFilter.java:39`). All other handlers return
`ResponseEntity<ApiError>` without a content type, so Spring writes
`application/json`. SPEC 6.11 and 7.6 require `application/problem+json` for
errors. The contracts declare the canonical media type; this is part of M-02.

## M-18 Event envelope book

SPEC 3.6 requires every API and event contract to carry the book. The example
envelope in SPEC 12.4 and the outbox example in SPEC 7.5.4 do not show a `book`
member. `schemas/event-envelope.schema.json` makes `book` required and notes
the discrepancy. Resolve by correcting the SPEC examples, or by relaxing the
schema if the platform decides the event subject implies the book.

## M-19 Base-path rule

SPEC 7.6 says the public base path is `/api/v1/{vertical}` while the vertical
tables in SPEC 11 use `/api/v1/{vertical}/{resource}` and the services use
`/api/v1/{resource}`. Three different forms exist in normative text. The
contracts follow the services and the gateway. Correct SPEC 7.6 and the SPEC 11
tables in one change.

## M-20 Audit actor fields

Every projection carries `createdAt`, `updatedAt`, and `version`, but none
carries `createdBy` or `updatedBy`. SPEC 7.10 requires actor attribution in the
audit record, which the services keep in their audit tables and not in the
resource projection. The shared `AuditFields` component therefore documents only
the three implemented fields and notes the planned actor fields in its
description. If actor identity is added to the projection later, it is an
additive, compatible change.

## Validation evidence

The repository validator was run on the committed tree:

```text
$ python scripts/validate_contracts.py
EIA canonical contract validation
repository: .../repos/eia-contracts
python: 3.12.8 (standard library only)

OpenAPI 3.1 documents
  OK openapi/party.yaml  4 paths, 6 operations
  OK openapi/policy.yaml  6 paths, 8 operations
  OK openapi/contract.yaml  6 paths, 8 operations
  OK openapi/direct-claims.yaml  6 paths, 8 operations
  OK openapi/assumed-claims.yaml  9 paths, 12 operations
  OK openapi/cession.yaml  6 paths, 8 operations
  OK openapi/retrocession.yaml  6 paths, 8 operations
  OK openapi/document.yaml  6 paths, 8 operations
  OK openapi/payment.yaml  9 paths, 11 operations
  OK openapi/notifications.yaml  6 paths, 8 operations

AsyncAPI 3 documents
  OK asyncapi/party.yaml  9 event channels
  OK asyncapi/policy.yaml  18 event channels
  OK asyncapi/contract.yaml  20 event channels
  OK asyncapi/direct-claims.yaml  20 event channels
  OK asyncapi/assumed-claims.yaml  15 event channels
  OK asyncapi/cession.yaml  14 event channels
  OK asyncapi/retrocession.yaml  14 event channels
  OK asyncapi/document.yaml  15 event channels
  OK asyncapi/payment.yaml  16 event channels
  OK asyncapi/notifications.yaml  10 event channels
  OK catalog: 151 unique published events across 10 verticals

JSON Schema 2020-12 documents

JSON Reference resolution
  OK walked 22 YAML documents

Result
  PASS 3897 checks, 0 failures
```

Additional developer checks, not repository dependencies:

- The stdlib YAML parser output was compared recursively with PyYAML 6.0.3 for
  all 22 YAML documents: zero differences.
- All eleven OpenAPI documents validate against the official OpenAPI 3.1
  meta-schema (`https://spec.openapis.org/oas/3.1/schema/2022-10-07`) using the
  `jsonschema` package in a throwaway environment.
- The three JSON Schema documents pass `Draft202012Validator.check_schema`, and
  the error and money examples validate.
- Negative checks: removing a required operation, breaking indentation,
  renaming one channel address, and corrupting a `$ref` each produce a
  non-zero exit and a specific failure message.

## Resolution policy

1. A deviation is fixed in the service, not by weakening the contract, unless
   the Architecture owner accepts the implemented shape as canonical.
2. When a deviation is fixed, remove it from this file in the same change that
   updates the contract.
3. A new deviation must be added here with the same evidence standard: source
   path and symbol or line, and the SPEC section it violates.


