# Contract-to-implementation audit

Status: open, reviewed 2026-10-19 (Round 5).

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
| M-14 | Six experts publish a subset of their events; no subscriber or inbox | M |
| M-16 | Assumed Claims mounts two public path sets | L |
| M-17 | Error content type is `application/json` outside Policy, Notifications, and one book filter | M |
| M-18 | SPEC 12.4 example envelope omits the book required by SPEC 3.6 | L |
| M-19 | SPEC 7.6 base-path rule contradicts the SPEC vertical tables | L |
| M-20 | Audit actor fields (`createdBy`, `updatedBy`) are not returned | L |
| M-21 | Cession/Retrocession FS-RI hand-off is synchronous | M |
| M-22 | Implemented outbox event names differ from the SPEC catalog names | M |

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
| Assumed Claims (domain and expert) | `com.eia.assumedclaims.*.ApiError` | `{type, title, status, detail, instance, code, category, retryable, errors[{field, code, message}]}` with `application/problem+json` and `EIA-RNS-7xxx` codes |
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

Policy list operations and every Policy second-slice collection (versions,
coverages, limits, aggregate state, endorsements, insureds, locations,
cancellations, and reinstatements) return the offset page envelope
`{items, page, size, total, _links:{self, next, prev}}` on both the public and
the expert routes. `page` defaults to 0 and `size` to 20 with a maximum of 100
(`Pagination.DEFAULT_SIZE` / `MAX_SIZE`). `next` is omitted on the last page and
`prev` on the first page; `_links` hrefs are relative and the expert links keep
the required `tenantId` query parameter. The second-slice domain service
rebuilds the links against the public base path.

Every other vertical still returns a bare `List<Dto>`: for example
`ClaimController.list`, `ContractController.list`,
`NotificationController.list`, `CessionController.list` (public and expert), and
`RetrocessionController.list` (public and expert). The Contract second-slice
collections, the Direct Claims child collections, and the Assumed Claims child
collections in Round 5 are also bare arrays. There is no `page` object, no
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

Policy page responses carry `_links.self`, `_links.next`, and `_links.prev`; so
do the Policy second-slice collection responses (versions, coverages, limits,
aggregate state, endorsements, insureds, locations, cancellations, and
reinstatements). No Policy detail representation carries `_links`; `PolicyDto`
has no links member. No other vertical has `_links` on a collection or a
detail.

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
| Policy public second-slice mutations (coverage, endorsement, insured, location, cancel, reinstate) | Accept optional `If-Match` and return the policy `ETag`; stale tag is 409 `CONCURRENT_MODIFICATION` |
| Policy public erosion | Returns the policy `ETag`; the derived limit state is version-checked internally and a lost update is 409 |
| Policy expert GET/create/PATCH | Same ETag and If-Match behaviour as the public service |
| Contract public PATCH | Required `expectedVersion` body field; no ETag |
| Contract public bind and commutation | Required `expectedVersion` on bind; the commutation has no caller-supplied version |
| Direct Claims public PATCH | Not accepted; the domain reads and forwards the current version |
| Direct Claims expert PATCH | Optional body version |
| Direct Claims child PATCH (injuries, exposures, litigation, recoveries, liens) | Required body `expectedVersion` on the public and expert routes; stale is 409 |
| Assumed Claims public POST status | Required body version |
| Assumed Claims child mutations | No caller-supplied version on most child commands; reserves use an effective-date guard |
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
- Every Policy second-slice mutation returns the policy `ETag` from the expert's
  version-issuing write; a replay returns 200 with the same ETag and
  `Idempotent-Replayed: true`.
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
header. In Round 5 every Policy second-slice mutation (coverage, erosion,
endorsement, insured, location, cancellation, and reinstatement) accepts the
same header on both the public and the expert route:

- The key is normalized (trimmed, maximum 255 characters) and scoped to the
  tenant. A blank key is treated as absent.
- The expert stores `tenant + key + request hash` in `policy_idempotency` in
  the same transaction as the policy row. The domain forwards the header.
- The same key and an identical request replay the original resource with 200
  and `Idempotent-Replayed: true`; a fresh create is 201 with
  `Idempotent-Replayed: false`.
- Reusing the key with a different request is 409 `IDEMPOTENCY_CONFLICT`. The
  create response carries `meta.existingPolicyId`; the second-slice commands
  carry `meta.existingResourceId`.
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
  `PolicyContractController.java` (second-slice header),
  `PolicyClient.java` (forwards the header and reads `Idempotent-Replayed`).
- `repos/eia-policy-expert/.../IdempotencyKeys.java` (normalize, request hash),
  `CommandIdempotency.java` (second-slice replay/conflict),
  `PolicyService.java:64-90` (create reserve/replay/conflict),
  `PolicyRepository.findCommandIdempotency` / `insertCommandIdempotencyIfAbsent`,
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
| Policy second-slice expert routes | `?tenantId=` query parameter |
| Direct Claims expert status transition | `X-EIA-Tenant` header instead of the query parameter (`ClaimController.java:52-58`) |
| Direct Claims expert child routes | `?tenantId=` on GET, `X-EIA-Tenant` on POST/PATCH |
| Assumed Claims expert create and status | `tenantId` in the body plus `X-EIA-Tenant` sent by the domain client |
| Assumed Claims expert close, financials, audit, and second-slice routes | `X-EIA-Tenant` header |

The contracts document each route exactly. A future cleanup should make the
internal tenant a header only, and remove `tenantId` from request bodies.

## M-10 Lifecycle method inconsistency

The same conceptual operation is exposed with four shapes:

- `PATCH /{id}/status` - Policy, Contract, Direct Claims, Payment expert.
- `POST /{id}/status` - Assumed Claims, Document.
- `PUT /{id}/status` - Cession, Retrocession expert.
- `POST /{id}/transition` - Cession, Retrocession public.
- Named action POSTs - Payment public `/submit`, `/authorize`, `/approve`,
  `/issue`; Policy second-slice `/cancel`, `/reinstate`, `/erosion`; Contract
  `/bind`, `/approve`, `/execute`; Direct Claims `/close`, `/approve`,
  `/execute`; Assumed Claims `/accept`, `/resolve`, `/commute`, `/close`.

Contract `BOUND` and Assumed Claims `COMMUTED` are intentionally not reachable
through the generic status endpoint: they are commands with preconditions
(`POST /bind` and `POST /commute`). The other named actions are ordinary
sub-resource commands. A future harmonization should use one
action-on-a-sub-resource convention, preferably `POST /{id}/{action}` for
lifecycle commands, as SPEC 6.1 does for transactions.

## M-11 Illegal-transition status codes

| Service | Status | Code |
|---|---|---|
| Policy | 409 | `INVALID_STATUS_TRANSITION` |
| Direct Claims | 400 | `VALIDATION_ERROR` |
| Contract | 409 | `INVALID_STATUS_TRANSITION`; `BIND_REQUIRES_COMMAND` for `BOUND` |
| Assumed Claims | 409 | `EIA-RNS-7003`; `EIA-RNS-7505` for `COMMUTED` |
| Document | 400 | `INVALID_STATUS_TRANSITION` |
| Cession / Retrocession | 400 | `INVALID_STATUS_TRANSITION` |
| Payment | 400 | `INVALID_STATUS_TRANSITION` / `PAYMENT_NOT_APPROVED` |

Policy follows SPEC 6.11 for state conflicts (409) and additionally separates
business-rule rejections (422) from missing approvals (428): coverage, limit,
endorsement, party, cancellation, and reinstatement rules are 422 with
`category: BUSINESS_RULE`; a missing `approvedBy`/`approvalRef` is 428 with
`category: APPROVAL_REQUIRED`. Assumed Claims does the same with its
`EIA-RNS-7xxx` codes (422 for `EIA-RNS-7102`, -7204, -7301, -7401, -7502,
-7603, -7701; 428 for -7203, -7302, -7501). Contract `POST /bind` returns 409
`BIND_PRECONDITION_FAILED` for failed preconditions and 400
`BIND_APPROVAL_REQUIRED` for a missing approver. Cession, Retrocession, and
Document still return 400 for an illegal edge; their contracts document 400.
Standardize the remaining five on 409 for a version or state conflict and 422
for a domain policy rejection, then update the contracts.

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
- Policy: no `policyType`, `productLine`, `insured` object, `limits[]` array on
  the header, `massTort`, `claimSummary`, occurrences, programs, billing, or
  the claims/reinsurance projections. Round 5 adds versions, coverage and limit
  schedules, aggregate erosion, endorsements, insureds, locations,
  cancellations, and reinstatements, so those are no longer gaps.
- Contract: no `treatyNumber`, `contractBasis`, inception-date naming,
  `contract_section`, `contract_version`, `contract_sliding_scale`,
  `contract_premium`, `contract_reinstatement`, `contract_wording`,
  `technical_account`, `bordereau_line`, loss-aggregate, or mass-tort profile.
  Round 5 adds layers, participants, terms, security, cessions, bordereaux,
  commutations, and bind, so those are no longer gaps.
- Direct Claims: no `tortCode` (the implemented name is `causeCode`),
  `claimant` object, policy-year allocations, financial summary, reopen,
  documents, lineage, or work queues. Round 5 adds injuries, exposures,
  reserve history, the coverage decision, litigation, settlements, recoveries,
  liens, and close.
- Assumed Claims: no policy-year allocations, documents, lineage, or work
  queues. Round 5 adds loss advices, bordereau ingest, reserve history, cash
  calls, recoveries, commutation, disputes, audit, financials, and close.
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
  is implemented; the FS-RI hand-off fields were added in Round 2 and the
  outbox events in Round 5.

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
| Policy `coinsurancePct` | a decimal fraction (`0.150000`) |
| Contract `sharePct`, `signedLinePct`, `cessionPct` | percentages of 100 (`15.000000`), not the SPEC 12.2 fraction |

The contracts use the implemented names. Renaming any of these is a breaking
change and needs a major version.

## M-14 Eventing

The platform gained a transactional outbox library in Round 2
(`eia-platform/libs`) and the Party expert writes its event in the same
transaction as the Party row. Round 5 rolled the outbox out to five more
experts. The implemented publishers are:

| Vertical | Implemented event names | Source |
|---|---|---|
| Party | `party.party.created`, `party.party.updated` | `repos/eia-party-expert/.../PartyEvents.java` |
| Cession | `cession.cession.created`, `cession.cession.updated`, `cession.cession.handed-off` | `repos/eia-cession-expert/.../CessionEvents.java` |
| Retrocession | `retrocession.retrocession.created`, `retrocession.retrocession.updated`, `retrocession.retrocession.handed-off` | `repos/eia-retrocession-expert/.../RetrocessionEvents.java` |
| Document | `document.document.created`, `document.document.updated`, `document.document.status-changed` | `repos/eia-document-expert/.../DocumentEvents.java` |
| Payment | `payment.payment.created`, `payment.payment.updated`, `payment.payment.status-changed` | `repos/eia-payment-expert/.../PaymentEvents.java` |
| Notifications | `notifications.notification.created`, `notifications.notification.sent` | `repos/eia-notifications-expert/.../NotificationEvents.java` |

Each `*Service` calls `outbox.insert(OutboxEvent.fromEnvelope(...))` in the same
transaction as the aggregate write; for example
`repos/eia-payment-expert/.../PaymentService.java:39-66` and
`repos/eia-document-expert/.../DocumentService.java:38-55`.

Every other AsyncAPI channel and operation is marked `x-status: planned`, and
the catalog carries the implemented subset per vertical. The platform outbox
dispatcher (`RestClientOutboxDispatcher`, `OutboxDispatchService`,
`OutboxDispatchJob`) is implemented and is scheduled by a Quartz trigger in
each of these services when `eia.outbox.enabled=true`; it posts each event to a
subscriber-defined HTTPS endpoint with the HMAC-SHA256 signature. There is
still no subscriber, inbox, subscription registry, or gap detection, so no
event has been consumed by another vertical. The `consumed` lists in the
catalog remain the planned SPEC subscriptions. The event names also differ from
the SPEC catalog names; see M-22.

## M-16 Assumed Claims path alias

`AssumedClaimController`, `LossAdviceController`, `ReserveController`,
`CashCallController`, `RecoveryController`, `CommutationController`, and
`DisputeController` are each mapped to both `/api/v1/assumed-claims` and
`/api/v1/assumed-claims/claims` (`@RequestMapping({...})` on every controller).
The web remote calls the `/claims` form. Both are documented: the base routes
under both path forms and the second-slice routes under the short form with an
`x-path-alias` naming the `/claims` equivalent. The duplicate surface should be
reduced to one path; the alias is compatible today because both are
implemented.

## M-17 Error content type

Policy now sets `application/problem+json` on every handled error, in both the
domain and the expert (`ApiExceptionHandler` uses
`MediaType.APPLICATION_PROBLEM_JSON`). Assumed Claims now does the same in both
services, and Notifications also sets it (`ApiExceptionHandler.java:110-112`).
All other handlers return `ResponseEntity<ApiError>` without a content type, so
Spring writes `application/json`. SPEC 6.11 and 7.6 require
`application/problem+json` for errors; this is part of M-02.

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

Every persisted aggregate projection carries `createdAt`, `updatedAt`, and
`version` (the Policy and Contract headers, the Direct Claim, and the Assumed
Claim). The second-slice child projections are append-only or immutable, so they
carry `createdAt` and either a row `version` or `sequence` but not always
`updatedAt`. None carries `createdBy` or `updatedBy`. SPEC 7.10 requires actor
attribution in the audit record, which the services keep in their audit tables
and not in the resource projection. The shared `AuditFields` component therefore
documents only the three implemented header fields and notes the planned actor
fields in its description. If actor identity is added to the projection later,
it is an additive, compatible change.

## M-21 Synchronous FS-RI hand-off

SPEC 7.18.3 requires the vertical to write the hand-off to its outbox as
PENDING and deliver it to FS-RI asynchronously; HAND-05 requires an FS-RI outage
to queue hand-offs. The vertical still calls FS-RI synchronously from the
`HANDOFF_PENDING` transition:

- On a 2xx acknowledgement the case is persisted as `HANDED_OFF` with
  `fsriHandoffId`, `fsriStatus`, and `fsriHandedOffAt` in one optimistic write,
  and the caller receives 200 with that record.
- On failure the lifecycle status is unchanged, `fsriLastError` records the
  cause, and the caller receives the mapped 400/409/502/503 problem. There is no
  FS-RI delivery queue, retry scheduler, or `GET /handoffs` endpoint.
- Round 5 added the transactional outbox for domain events, including
  `<vertical>.<vertical>.handed-off`, but that event records the already
  completed synchronous hand-off; it does not queue the FS-RI call. The outbox
  is not a substitute for the SPEC hand-off queue.

Evidence:

- `repos/eia-cession-domain/.../CessionService.java` (transition,
  `handOff`, failure recording).
- `repos/eia-cession-domain/.../FsriCessionClient.java` (synchronous `POST`,
  timeout, error translation).
- `repos/eia-retrocession-domain/.../RetrocessionService.java`,
  `FsriRetroClient.java`.
- `repos/eia-cession-expert/.../CessionEvents.java`,
  `repos/eia-retrocession-expert/.../RetrocessionEvents.java` (handed-off event).
- `repos/eia-cession-expert/.../schema.sql` and
  `repos/eia-retrocession-expert/.../schema.sql` - hand-off columns.

Resolution: either implement the outbox and queue (return 202 with a hand-off
resource and expose `GET /handoffs`), or accept the synchronous hand-off as the
canonical Round 2 behaviour and amend SPEC 7.18.3/HAND-05. The contracts document
the synchronous behaviour until that decision.

## M-22 Event names differ from the SPEC catalog

The outbox rollout uses the names actually emitted by the services, which do
not match every name in SPEC 11.9.6, 11.10.6, 11.6.9, 11.7.10, and 11.8.9:

| Vertical | Implemented | SPEC /
planned name |
|---|---|---|
| Cession | `cession.cession.created` / `.updated` / `.handed-off` | `cession.case.created`, `cession.handoff.sent`/`.acknowledged` |
| Retrocession | `retrocession.retrocession.created` / `.updated` / `.handed-off` | `retrocession.case.created`, `retrocession.handoff.sent`/`.acknowledged` |
| Document | `document.document.created` / `.updated` / `.status-changed` | `document.document.registered`, plus the SPEC lifecycle verbs |
| Payment | `payment.payment.updated` / `.status-changed` | the SPEC per-verb names such as `payment.payment.authorized` |
| Notifications | `notifications.notification.created` / `.sent` | `notifications.notification.issued` / `.delivered` |

The catalog lists both sets and marks only the implemented ones. Publishing a
SPEC name in addition to the implemented name is additive; renaming or removing
an implemented name is breaking and needs the EV-05 dual-publish window.

Evidence:

- `repos/eia-cession-expert/.../CessionEvents.java:27-29`
- `repos/eia-retrocession-expert/.../RetrocessionEvents.java:28-30`
- `repos/eia-document-expert/.../DocumentEvents.java:29-31`
- `repos/eia-payment-expert/.../PaymentEvents.java:31-33`
- `repos/eia-notifications-expert/.../NotificationEvents.java:36-37`

Resolution: either align the implemented names with the SPEC (with a
dual-publish window) or amend the SPEC event tables. The contracts document
both until that decision.

## Validation evidence

The repository validator was run on the working tree after the Round 5 changes:

```text
$ python scripts/validate_contracts.py
EIA canonical contract validation
repository: .../repos/eia-contracts
python: 3.12.8 (standard library only)

OpenAPI 3.1 documents
  OK openapi/party.yaml  4 paths, 6 operations
  OK openapi/policy.yaml  36 paths, 46 operations
  OK openapi/contract.yaml  35 paths, 51 operations
  OK openapi/direct-claims.yaml  38 paths, 56 operations
  OK openapi/assumed-claims.yaml  35 paths, 50 operations
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
  OK asyncapi/cession.yaml  17 event channels
  OK asyncapi/retrocession.yaml  17 event channels
  OK asyncapi/document.yaml  18 event channels
  OK asyncapi/payment.yaml  18 event channels
  OK asyncapi/notifications.yaml  12 event channels
  OK catalog: 164 unique published events across 10 verticals

JSON Schema 2020-12 documents

JSON Reference resolution
  OK walked 22 YAML documents

Result
  PASS 8481 checks, 0 failures
```

Additional checks and limits:

- The validator's own YAML parser rejects duplicate keys and unsupported
  constructs; all 22 YAML documents parsed.
- The JSON Schema documents are checked by the validator's schema subset and
  their own examples; no external JSON Schema validator was installed for this
  round.
- No official OpenAPI or AsyncAPI meta-schema validator and no PyYAML run was
  performed in this round, because the repository deliberately takes no
  runtime dependency on either. A release engineer may run one additionally.
- Negative checks were run on a throwaway copy: removing the required
  `/api/v1/policies/{policyId}/coverages` path, changing an implemented event
  channel back to `x-status: planned` without updating the catalog, and
  inventing an event in the catalog each produce a non-zero exit and a specific
  failure message.

## Resolution policy

1. A deviation is fixed in the service, not by weakening the contract, unless
   the Architecture owner accepts the implemented shape as canonical.
2. When a deviation is fixed, remove it from this file in the same change that
   updates the contract, and record the closure in the closed-mismatches table.
3. A new deviation must be added here with the same evidence standard: source
   path and symbol or line, and the SPEC section it violates.
