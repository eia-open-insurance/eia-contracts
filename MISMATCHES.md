# Contract-to-implementation audit

Status: open, reviewed 2026-10-19 (Round 2).

This document records every known difference between the canonical contracts in
this repository and the services that implement them. It is part of the
contract deliverable: the contracts state the agreed shape, and this file states
where the running code does not meet it yet.

## Scope and method

- Specification: `SPEC.md` sections 3.6, 6.11, 7.5, 7.6, 7.18-7.23, 10.3,
  11.1-11.10, 12, and 16.9.
- Implementation: all twenty vertical service controllers and their clients -
  `eia-party-*`, `eia-policy-*`, `eia-contract-*`, `eia-direct-claims-*`,
  `eia-assumed-claims-*`, `eia-cession-*`, `eia-retrocession-*`,
  `eia-document-*`, `eia-payment-*`, `eia-notifications-*` - plus the Round 2
  FS-RI hand-off in `eia-cession-domain` and `eia-retrocession-domain`.
- Gateway routing: `repos/eia-platform/gateway/src/main/resources/application.yml`.
- Method: static review of controller mappings, request and response records,
  `@JsonFormat` annotations, exception handlers, book-wall filters, idempotency
  and ETag helpers, FS-RI clients, and repositories. No service was started and
  no database was seeded, so this audit proves source-level conformance, not
  runtime behaviour. Runtime conformance remains the contract test of
  SPEC 12.7.
- Evidence command: `python scripts/validate_contracts.py` (see
  [Validation evidence](#validation-evidence)).

Severity: **H** = a client breaking or a security-relevant difference, **M** =
a visible contract inconsistency, **L** = a naming or documentation difference.

## Closed in Round 2 (2026-10-19)

These identifiers are closed and are not reused. Their detail sections were
removed per the resolution policy.

| ID | Area | Resolution | Evidence |
|---|---|---|---|
| M-03 | Money serialized as a JSON number by four services | Every money-bearing service now serializes the amount as a decimal string. The remaining flat `amount`/`currency` pair shape is a field-shape gap covered by M-12 and M-13, not a JSON-type gap. | `@JsonFormat(shape = JsonFormat.Shape.STRING)` on `PolicyDto`, `Policy`, `ClaimDto`, `Claim`, `AssumedClaimDto`, `AssumedClaim`, `CessionDto`, `Cession`, `RetrocessionDto`, `Retrocession`, `PaymentDto`, and `Payment`. |
| M-09 | Book mismatch was 404 in the claim verticals and 400 in the reinsurance verticals | A wrong `X-EIA-Book` is hidden as 404 `BOOK_SCOPE_VIOLATION` in Direct Claims, Assumed Claims, Cession, and Retrocession. A missing header is still a 400 `BOOK_REQUIRED` in Cession and Retrocession, which is a validation error rather than a book mismatch, so it does not confirm existence. | `RequestScope.requireDirectBook` / `requireAssumedBook`, `BookWall`, and `BookScopeFilter` in the four book-scoped verticals. |
| M-15 | Party domain had no exception mapping | `eia-party-domain` now has a `@RestControllerAdvice`; `PartyClient` translates expert 404 to 404 `NOT_FOUND`, other 4xx to 400 with the expert code, and 5xx/unreachable to 503 `EXPERT_UNAVAILABLE`. | `repos/eia-party-domain/.../ApiExceptionHandler.java`, `PartyClient.java`. |

## Summary

| ID | Area | Severity |
|---|---|---|
| M-01 | Public base paths differ from the SPEC vertical tables | M |
| M-02 | Several error-body shapes remain; Policy is now canonical | H |
| M-04 | Pagination: Policy uses an offset envelope, other lists are bare arrays | H |
| M-05 | `_links` exist on Policy pages only; no detail links anywhere | M |
| M-06 | `ETag`/`If-Match` exist only in Policy; other verticals use body versions | H |
| M-07 | `Idempotency-Key` exists only on Policy create | H |
| M-08 | Tenant context is passed three different ways | M |
| M-10 | Lifecycle operations use PATCH, POST, and PUT inconsistently | M |
| M-11 | Illegal-transition status codes: Policy is 409, five verticals are 400 | M |
| M-12 | Resource models are narrower than the SPEC aggregates | M |
| M-13 | Field names differ from the SPEC representations | L |
| M-14 | Only the Party expert publishes an event; no dispatcher or subscriber | M |
| M-16 | Assumed Claims mounts two public path sets | L |
| M-17 | Error content type is `application/json` outside Policy, Notifications, and one book filter | M |
| M-18 | SPEC 12.4 example envelope omits the book required by SPEC 3.6 | L |
| M-19 | SPEC 7.6 base-path rule contradicts the SPEC vertical tables | L |
| M-20 | Audit actor fields (`createdBy`, `updatedBy`) are not returned | L |
| M-21 | Cession/Retrocession hand-off is synchronous; there is no outbox queue | M |

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

- `repos/eia-party-domain/.../PartyController.java:11` - `/api/v1/parties`
- `repos/eia-policy-domain/.../PolicyController.java:19` - `/api/v1/policies`
- `repos/eia-contract-domain/.../ContractController.java:27` - `/api/v1/contracts`
- `repos/eia-direct-claims-domain/.../ClaimController.java:20` - `/api/v1/claims`
- `repos/eia-cession-domain/.../CessionController.java:18` - `/api/v1/cessions`
- `repos/eia-retrocession-domain/.../RetrocessionController.java:19` - `/api/v1/retrocessions`
- `repos/eia-document-domain/.../DocumentController.java:15` - `/api/v1/documents`
- `repos/eia-payment-domain/.../PaymentController.java:18` - `/api/v1/payments`
- `repos/eia-notifications-domain/.../NotificationController.java:22` - `/api/v1/notifications`
- `repos/eia-platform/gateway/src/main/resources/application.yml:18-48` - the
  same public prefixes are routed.
- Web remotes call the implemented prefixes, for example
  `repos/eia-policy-web/src/App.jsx` (`/api/v1/policies`) and
  `repos/eia-assumed-claims-web/src/App.jsx` (`/api/v1/assumed-claims/claims`).

Resolution: the contracts document the implemented paths. Correct the SPEC
tables to the implemented form, or introduce the namespaced form as `/v2` with a
migration; do not silently rewrite the gateway.

## M-02 Error envelope

The canonical envelope is `Problem` in `schemas/error-envelope.schema.json`
(SPEC 6.11 and 12.2). Policy now emits it; the other services emit their own
shapes.

| Vertical | Implemented type | Emitted shape |
|---|---|---|
| Policy (domain and expert) | `com.eia.policy.*.Problem` | `{type, title, status, detail, instance, code, category, retryable, errors[{field, code, message}], meta, correlationId, transactionId}` with `application/problem+json` |
| Direct Claims (domain and expert) | `com.eia.directclaims.*.ApiError` | `{timestamp, status, code, message, path, details[{field, message}]}` |
| Payment (domain and expert) | `com.eia.payment.*.ApiError` | same as Direct Claims |
| Contract (domain and expert) | `com.eia.contract.*.ApiError` | `{code, message, details[{field, message}]}` |
| Document (domain and expert) | `com.eia.document.*.ApiError` | `{code, message, details[{field, message}]}` |
| Cession (domain and expert) | `com.eia.cession.*.ApiError` | `{code, message, details{field: message}}` |
| Retrocession (domain and expert) | `com.eia.retrocession.*.ApiError` | `{code, message, details{field: message}}` |
| Assumed Claims (domain and expert) | `com.eia.assumedclaims.*.ApiError` | `{type, title, status, detail, instance, code, category, retryable, errors[{field, code, message}]}` (RFC 9457 shape, not the canonical media type everywhere) |
| Notifications (domain) | Spring `ProblemDetail` plus properties | RFC 9457 body with `code`, `category`, `retryable`, `errors[{field, code, message}]`; no `correlationId`, `transactionId`, or `meta` |
| Party (expert) | inline `Map<String, String>` | `{code, message}` for `NOT_FOUND` only |
| Party (domain) | `com.eia.party.domain.ApiError` | `{code, message, details{field: message}}` |

Policy now matches the canonical shape and media type. Two Policy differences
remain:

1. The `code` values are the vertical legacy strings (`POLICY_NOT_FOUND`,
   `CONCURRENT_MODIFICATION`, `INVALID_STATUS_TRANSITION`,
   `IDEMPOTENCY_CONFLICT`, and so on), not the `EIA-XXX-NNNN` scheme that
   `schemas/error-envelope.schema.json` still requires. `Problems.java` states
   that existing business codes are preserved so current clients keep
   branching on them; migrating to the canonical code scheme is the remaining
   open work.
2. `transactionId` is always `null` and is omitted by Jackson because the
   Policy records use `NON_NULL` inclusion.

Evidence:

- `repos/eia-policy-domain/.../Problem.java:19-35`,
  `repos/eia-policy-expert/.../Problem.java:14-30` - record members.
- `repos/eia-policy-domain/.../Problems.java:52-83`,
  `repos/eia-policy-expert/.../Problems.java` - type/category/retryable mapping.
- `repos/eia-policy-domain/.../ApiExceptionHandler.java:35-149`,
  `repos/eia-policy-expert/.../ApiExceptionHandler.java` - handlers and
  `MediaType.APPLICATION_PROBLEM_JSON`.
- `repos/eia-direct-claims-domain/.../ApiError.java:6`, `repos/eia-direct-claims-expert/.../ApiError.java:6`
- `repos/eia-payment-domain/.../ApiError.java:6`, `repos/eia-payment-expert/.../ApiError.java:6`
- `repos/eia-contract-domain/.../ApiError.java:6`, `repos/eia-contract-expert/.../ApiError.java:12`
- `repos/eia-document-domain/.../ApiError.java:12`, `repos/eia-document-expert/.../ApiError.java:12`
- `repos/eia-cession-domain/.../ApiError.java:8`, `repos/eia-cession-expert/.../ApiError.java:8`
- `repos/eia-retrocession-domain/.../ApiError.java:8`, `repos/eia-retrocession-expert/.../ApiError.java:8`
- `repos/eia-assumed-claims-domain/.../ApiError.java:12`, `repos/eia-assumed-claims-expert/.../ApiError.java:12`
- `repos/eia-notifications-domain/.../ApiExceptionHandler.java:97`
- `repos/eia-party-expert/.../ApiExceptionHandler.java:10-14`
- `repos/eia-party-domain/.../ApiExceptionHandler.java`,
  `repos/eia-party-domain/.../PartyClient.java`

Resolution: move `Problem` into `eia-platform/libs` as the single error type,
map every `@RestControllerAdvice` to it, and use
`application/problem+json` everywhere. Adopt the `EIA-XXX-NNNN` code scheme in
Policy as a separate, coordinated change. Until then these contracts describe
the canonical target; the Policy document also records the legacy-code
difference in its description.

## M-04 Pagination

Policy list operations now return the offset page envelope
`{items, page, size, total, _links:{self, next, prev}}` on both the public and
the expert routes. `page` defaults to 0 and `size` to 20 with a maximum of 100
(`Pagination.DEFAULT_SIZE` / `MAX_SIZE`). `next` is omitted on the last page and
`prev` on the first page; `_links` hrefs are relative and the expert links keep
the required `tenantId` query parameter.

Every other vertical still returns a bare `List<Dto>`: for example
`ClaimController.list`, `ContractController.list`,
`NotificationController.list`, `CessionController.list` (public and expert), and
`RetrocessionController.list` (public and expert). There is no `page` object, no
cursor, and no `total` in those responses.

The implemented Policy envelope is **offset-based** and therefore differs from
SPEC 7.6 and 12.2, which specify a cursor envelope
(`?page[size]=50&page[after]=<opaque>`, response `data` plus
`page:{size, hasMore, nextCursor, total?}`, default 25, maximum 200). This is a
deliberate Round 2 shape, not a transcription of the SPEC. Resolving it means
either correcting SPEC 7.6/12.2 to the offset form or migrating Policy and the
other verticals to the cursor form; the contracts document the implemented
offset envelope until then.

Evidence:

- `repos/eia-policy-domain/.../PolicyController.java:32-37` (page/size request
  parameters), `PolicyPage.java`, `PageLinks.java`, `Pagination.java`.
- `repos/eia-policy-expert/.../PolicyController.java:31-36`,
  `PolicyPage.java`, `PageLinks.java`, `Pagination.java`.
- `repos/eia-policy-domain/.../ExpertPolicyPage.java` (wire shape read from the
  expert; links are rebuilt for the public path).
- Public tests: `PolicyControllerTest.listsPoliciesWithDefaultPageEnvelope`,
  `paginationLinksAtInteriorBoundary`, `lastPageHasPreviousButNoNextLink`,
  `rejectsSizeAboveMaximum`, `rejectsNegativePage` (domain and expert).

## M-05 Hypermedia links

Policy page responses carry `_links.self`, `_links.next`, and `_links.prev`.
No Policy detail representation carries `_links`; `PolicyDto` has no links
member. No other vertical has `_links` on a collection or a detail.

SPEC 7.6 and 12.5 require detail links (`self`, `collection`, and typed record
links). The shared `Links` component remains marked planned; `PageLinks` is the
implemented page-specific form.

Evidence:

- `repos/eia-policy-domain/.../PolicyPage.java` and
  `repos/eia-policy-expert/.../PolicyPage.java` - `Links(self, next, prev)`.
- `repos/eia-policy-domain/.../PageLinks.java`,
  `repos/eia-policy-expert/.../PageLinks.java` - link construction.
- `repos/eia-policy-domain/.../PolicyDto.java` - no `_links` member.

## M-06 Concurrency control

Policy now implements the SPEC 12.6 concurrency mechanism:

| Operation | Version handling |
|---|---|
| Policy public GET detail | Response `ETag: "<version>"` |
| Policy public create | Response `ETag: "<version>"` on both 201 and 200 replay |
| Policy public PATCH status | Accepts `If-Match` (`"<version>"`, `W/"<version>"`, a comma list, or `*`); response `ETag`; stale tag/version is 409 `CONCURRENT_MODIFICATION` with `meta.currentVersion`, `meta.expectedVersion`, and `errors[0].code = STALE_VERSION` |
| Policy expert GET/create/PATCH | Same ETag and If-Match behaviour as the public service |
| Contract public PATCH | Required `expectedVersion` body field; no ETag |
| Direct Claims public PATCH | Not accepted; the domain reads and forwards the current version |
| Direct Claims expert PATCH | Optional body version |
| Assumed Claims public POST status | Required body version |
| Cession/Retrocession public POST transition | Not accepted; the domain reads and forwards the current version |
| Cession/Retrocession expert PUT status | Required `version` |
| Document public POST status | Not accepted; the domain forwards the current version |
| Document expert POST status | Optional `expectedVersion` |
| Payment public actions | Not accepted; the domain reads and forwards the current version |

Policy nuances:

- `If-Match` is optional for backward compatibility even though SPEC 12.6
  requires it on PUT/PATCH; the body `expectedVersion` is a fallback and the
  header wins when both are present.
- The expert still accepts a body `expectedVersion`; the domain sends both the
  version it read and the original `If-Match`.
- Cession and Retrocession map an expert 409 on a plain status write to a
  public 400 `CONFLICT` (`CessionClient.translate` / `RetrocessionClient`), so
  their public transitions have no 409 concurrency response. The FS-RI
  hand-off persistence path catches an expert 409 and returns 502
  `FSRI_HANDOFF_NOT_RECORDED`.

Evidence:

- `repos/eia-policy-domain/.../EntityTags.java` (format/parse/ANY),
  `PolicyController.java` (ETag/If-Match), `PolicyService.java` (precedence and
  409).
- `repos/eia-policy-expert/.../EntityTags.java`, `PolicyController.java`,
  `PolicyService.java`.
- Tests: `PolicyControllerTest.returnsEtagDerivedFromVersionOnGet`,
  `rejectsStaleIfMatchWithCanonicalConflict`,
  `ifMatchTakesPrecedenceOverExpectedVersion`, `rejectsMalformedIfMatch`,
  `rejectsStaleExpectedVersionWithoutIfMatch` (domain and expert);
  `EntityTagsTest` in both services.
- `repos/eia-policy-web/src/App.jsx` reads `ETag` and sends `If-Match`.

## M-07 Idempotency

Policy create (public and expert) accepts the optional `Idempotency-Key`
header:

- The key is normalized (trimmed, maximum 255 characters) and scoped to the
  tenant. A blank key is treated as absent.
- The expert stores `tenant + key + request hash` in `policy_idempotency` in
  the same transaction as the policy row. The domain forwards the header.
- The same key and an identical request replay the original policy with 200 and
  `Idempotent-Replayed: true`; a fresh create is 201 with
  `Idempotent-Replayed: false`.
- Reusing the key with a different request is 409 `IDEMPOTENCY_CONFLICT` with
  `meta.existingPolicyId`.
- The request hash normalizes amounts numerically (`1000.0` and `1000.0000`
  hash the same), uppercases currencies, and defaults the initial status to
  DRAFT.
- The header is optional for backward compatibility, even though SPEC 12.6
  requires it on transaction submission. No other vertical accepts, validates,
  persists, or replays an idempotency key, and `Idempotent-Replayed` is not
  emitted elsewhere.

Evidence:

- `repos/eia-policy-domain/.../IdempotencyKeys.java`,
  `PolicyController.java` (`Idempotency-Key` request header),
  `PolicyClient.java` (forwards the header and reads `Idempotent-Replayed`).
- `repos/eia-policy-expert/.../IdempotencyKeys.java` (normalize, request hash),
  `PolicyService.java:64-90` (reserve/replay/conflict),
  `PolicyRepository.findIdempotency` / `insertIdempotencyIfAbsent`,
  `src/main/resources/schema.sql:37-46` (`policy_idempotency`, unique
  `(tenant_id, idempotency_key)`).
- Tests: `createsPolicyAndForwardsIdempotencyKey`,
  `replaysIdempotentCreateWithOkStatus`, `returnsConflictForReusedIdempotencyKey`,
  `rejectsOverlongIdempotencyKey` (domain); `createsDraftPolicyWithIdempotencyRecord`,
  `replaysIdempotentCreateWithOkStatus`,
  `rejectsIdempotencyKeyReuseWithDifferentRequest`,
  `createsWithoutKeyWithoutStoringIdempotency` (expert); `IdempotencyKeysTest`.

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

## M-10 Lifecycle method inconsistency

The same conceptual operation is exposed with four shapes:

- `PATCH /{id}/status` - Policy, Contract, Direct Claims, Payment expert.
- `POST /{id}/status` - Assumed Claims, Document.
- `PUT /{id}/status` - Cession, Retrocession expert.
- `POST /{id}/transition` - Cession, Retrocession public.
- Named action POSTs - Payment public `/submit`, `/authorize`, `/approve`, `/issue`.

The contracts record the implemented method per route. A future harmonization
should use one action-on-a-sub-resource convention, preferably
`POST /{id}/{action}` for lifecycle commands, as SPEC 6.1 does for
transactions.

## M-11 Illegal-transition status codes

| Service | Status | Code |
|---|---|---|
| Policy | 409 | `INVALID_STATUS_TRANSITION` |
| Direct Claims | 400 | `VALIDATION_ERROR` |
| Contract | 409 | `INVALID_STATUS_TRANSITION` |
| Assumed Claims | 409 | `EIA-RNS-7003` |
| Document | 400 | `INVALID_STATUS_TRANSITION` |
| Cession / Retrocession | 400 | `INVALID_STATUS_TRANSITION` |
| Payment | 400 | `INVALID_STATUS_TRANSITION` / `PAYMENT_NOT_APPROVED` |

Policy now follows SPEC 6.11: an illegal edge, including a no-op transition, is
a 409 `INVALID_STATUS_TRANSITION` (`CONFLICT`), and a duplicate policy number is
a 409 `DUPLICATE_POLICY_NUMBER`. Cession and Retrocession still return 400 for
an illegal edge; their contracts document 400. Standardize the remaining five
on 409 for a version or state conflict and 422 for a domain policy rejection,
then update the contracts.

Evidence:

- `repos/eia-policy-domain/.../PolicyLifecycle.java:64-73`,
  `repos/eia-policy-expert/.../PolicyRules.java` (invalid transition).
- `repos/eia-policy-expert/.../PolicyService.java:131-137` (duplicate number).
- `repos/eia-cession-domain/.../CessionService.java:63-70`,
  `repos/eia-retrocession-domain/.../RetrocessionService.java:64-71`.

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
  confirmations, recoverables, statements, or reconciliations. The case itself
  is implemented; the FS-RI hand-off fields were added in Round 2.

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
| Policy `limitAmount` + `limitCurrency` | `limits[{limitCode, amount: Money}]` |
| Cession `cededPremium` + `cededLoss` + `currency` | two `Money` objects |
| Retrocession `cededPremium` + `cededLoss` + `currency` | two `Money` objects |
| Assumed Claims `assumedClaimNumber` | `assumed_claim_number` (matches DB, not the SPEC JSON examples) |

The contracts use the implemented names. Renaming any of these is a breaking
change and needs a major version.

## M-14 Eventing

The platform gained a transactional outbox library in Round 2
(`eia-platform/libs`) and the Party expert writes its event in the same
transaction as the Party row. No other service publishes an event, and there is
no dispatcher, inbox, subscription registry, subscriber, or consumer. Every
other AsyncAPI channel and operation is therefore marked `x-status: planned`,
and `asyncapi/event-catalog.yaml` still describes the planned publisher set.

## M-16 Assumed Claims path alias

`AssumedClaimController` is mapped to both
`/api/v1/assumed-claims` and `/api/v1/assumed-claims/claims`
(`AssumedClaimController.java:22`). The web remote calls the `/claims` form.
Both are documented with distinct operation IDs. The duplicate surface should
be reduced to one path; the alias is compatible today because both are
implemented.

## M-17 Error content type

Policy now sets `application/problem+json` on every handled error, in both the
domain and the expert (`ApiExceptionHandler` uses
`MediaType.APPLICATION_PROBLEM_JSON`). Notifications also sets it
(`ApiExceptionHandler.java:110-112`) and the Assumed Claims book filter sets it
explicitly (`BookScopeFilter.java:39`). All other handlers return
`ResponseEntity<ApiError>` without a content type, so Spring writes
`application/json`. SPEC 6.11 and 7.6 require `application/problem+json` for
errors; this is part of M-02.

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

## M-21 Synchronous FS-RI hand-off

SPEC 7.18.3 requires the vertical to write the hand-off to its outbox as
PENDING and deliver it to FS-RI asynchronously; HAND-05 requires an FS-RI outage
to queue hand-offs. Round 2 instead calls FS-RI synchronously from the
`HANDOFF_PENDING` transition:

- On a 2xx acknowledgement the case is persisted as `HANDED_OFF` with
  `fsriHandoffId`, `fsriStatus`, and `fsriHandedOffAt` in one optimistic write,
  and the caller receives 200 with that record.
- On failure the lifecycle status is unchanged, `fsriLastError` records the
  cause, and the caller receives the mapped 400/409/502/503 problem. There is no
  outbox row, dispatcher, retry scheduler, or `GET /handoffs` queue.
- This is why the transition is documented as a synchronous hand-off rather
  than a 202 with a pending resource.

Evidence:

- `repos/eia-cession-domain/.../CessionService.java:61-137` (transition,
  `handOff`, failure recording).
- `repos/eia-cession-domain/.../FsriCessionClient.java` (synchronous `POST`,
  timeout, error translation).
- `repos/eia-retrocession-domain/.../RetrocessionService.java:61-138`,
  `FsriRetroClient.java`.
- `repos/eia-cession-expert/.../schema.sql:15-18` and
  `repos/eia-retrocession-expert/.../schema.sql` - hand-off columns.

Resolution: either implement the outbox and queue (return 202 with a hand-off
resource and expose `GET /handoffs`), or accept the synchronous hand-off as the
canonical Round 2 behaviour and amend SPEC 7.18.3/HAND-05. The contracts document
the synchronous behaviour until that decision.

## Validation evidence

The repository validator was run on the working tree:

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
  OK openapi/cession.yaml  8 paths, 10 operations
  OK openapi/retrocession.yaml  8 paths, 10 operations
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
  PASS 4043 checks, 0 failures
```

Additional developer checks, not repository dependencies:

- PyYAML 6.0.3 parses all 22 YAML documents with a duplicate-key-rejecting
  loader, and targeted structural assertions pass on the four changed
  documents (`components.yaml`, `policy.yaml`, `cession.yaml`,
  `retrocession.yaml`).
- All eleven OpenAPI documents validate against the official OpenAPI 3.1
  meta-schema (`https://spec.openapis.org/oas/3.1/schema/2022-10-07`) using the
  `jsonschema` package in a throwaway environment.
- The three JSON Schema documents pass `Draft202012Validator.check_schema`, and
  the error and money examples validate.
- Negative checks were run on a throwaway copy: removing the required
  `/api/v1/policies` path, corrupting the `Page` `$ref`, and renaming one
  channel address each produce a non-zero exit and a specific failure message.

## Resolution policy

1. A deviation is fixed in the service, not by weakening the contract, unless
   the Architecture owner accepts the implemented shape as canonical.
2. When a deviation is fixed, remove it from this file in the same change that
   updates the contract, and record the closure in the closed-mismatches table.
3. A new deviation must be added here with the same evidence standard: source
   path and symbol or line, and the SPEC section it violates.
