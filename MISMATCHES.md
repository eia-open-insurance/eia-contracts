# Contract-to-implementation audit

Status: open, reviewed 2026-10-21 (Document content versions).

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
  FS-RI hand-off in `eia-cession-domain` and `eia-retrocession-domain`. The
  2026-10-20 pass additionally reads the ten global-search controllers, their
  services, their query repositories, and the shell's `GlobalSearch.jsx`. The
  Contract technical-account pass reads the domain controller, service, client,
  and projection plus the expert controller, rules, repository, status enum,
  event factory, and `schema.sql`. The Contract period-bordereau pass reads the
  domain controller, service, client, projection, and command rules plus the
  expert period controller, legacy header controller, rules, repositories,
  status enum, event factory, and `schema.sql`. The Direct Claims allocation
  pass reads the domain allocation controller, service, client, projection, and
  command plus the expert allocation controller, service, projection, summary,
  request, exception handler, event factory, repository, and tests. The Policy
  premium-receivables pass reads the domain receivable controller, service,
  book scope, projection, and client plus the expert billing-receivables
  controller, service, projection, row mapper, query, rules, and tests. The
  Policy mass tort profile pass reads the domain profile controller, service,
  projection, command, book scope, and client plus the expert profile
  controller, service, rules, repository, result, request, projection, event
  factory, `schema.sql`, and tests. The Direct Claims list-filter pass reads
  the public and expert claim controllers, services, and repository plus the
  domain claim client and projection. The Contract cash-call pass reads the
  domain cash-call controller, service, client, projection, and command rules
  plus the expert controller, rules, repository, status enum, event factory,
  and `schema.sql`. The Payment allocation pass reads the domain payment
  controller, service, client, allocation projection, summary, command, and
  rules plus the expert allocation controller, service, repository, rules,
  projection, summary, request, event factory, `schema.sql`, and tests. The
  Direct Claims allocation-erosion pass reads the domain allocation controller,
  service, policy-erosion client, projection, command, and tests plus the expert
  allocation controller, erosion request, service, repository, projection,
  exception handler, and tests. The Contract security/collateral pass reads the
  domain security controller, service, client, projection, and both commands
  plus the expert public security controller, rules, view, both requests,
  entity, event factory, internal security controller, repository, exception
  handler, `schema.sql`, and tests. The Direct Claims mass-tort allocation
  guard pass reads the domain claim detail controller and service, the Policy
  mass-tort client, the guard exception, the domain exception handler, and the
  domain tests. The Policy program pass reads the domain program controller,
  service, projection, command, book scope, policy-program controller and
  service, and client plus the expert program controller, service, rules,
  repository, view, entity, request, event factory, `schema.sql`, and the domain
  and expert tests.
  The Document content pass reads the domain content controller, service,
  client, projection, policy, size-limit filter, and exception handler plus the
  expert content controller, service, rules, repository, event factory,
  tenant resolver, `schema.sql`, and the domain and expert tests.
  The Document content-version pass reads the domain content controller,
  service, client, and metadata/version projections plus the expert content
  controller, service, repository, both version records, the
  `ContentVersionNotFoundException` mapping, `DocumentContentEvents`, the
  pointer/revision `schema.sql` tables and backfill, and the domain and expert
  version tests.
  The Policy credit-note pass reads the domain credit-note controller, service,
  projection, commands, book scope, and client plus the expert credit-note
  controller, service, rules, repository, entity, requests, event factory,
  `schema.sql`, and the domain and expert tests.
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
| M-07 | `Idempotency-Key` covers Policy and claim task/note creates only | M |
| M-08 | Tenant context is passed three different ways | M |
| M-10 | Lifecycle operations use PATCH, POST, and PUT inconsistently | M |
| M-11 | Illegal-transition status codes: Policy is 409, five verticals are 400 | M |
| M-12 | Resource models are narrower than the SPEC aggregates | M |
| M-13 | Field names differ from the SPEC representations | L |
| M-14 | Ten experts publish a subset of their events; the platform inbox has no business subscriber | M |
| M-16 | Assumed Claims mounts two public path sets | L |
| M-17 | Error content type is `application/json` outside Policy, Notifications, and one book filter | M |
| M-18 | SPEC 12.4 example envelope omits the book required by SPEC 3.6 | L |
| M-19 | SPEC 7.6 base-path rule contradicts the SPEC vertical tables | L |
| M-20 | Audit actor fields (`createdBy`, `updatedBy`) are not returned | L |
| M-21 | Cession/Retrocession FS-RI hand-off is synchronous | M |
| M-22 | Implemented outbox event names differ from the SPEC catalog names | M |
| M-23 | Global search paths and validation differ from the SPEC naming and canonical limit rules | M |
| M-24 | Payment source link is a flat triple, not the SPEC claim projection | M |
| M-25 | Claim assignment contract alignment: team is optional, negative expectedVersion is 400, and X-EIA-Actor is the only actor header. Resolved 2026-10-20. | — |
| M-26 | Document association links are a flat tenant-scoped link, not the SPEC association | M |
| M-27 | Policy billing and premium-receivables routes, event names, and status vocabulary differ from SPEC 11.2.13 | L |
| M-28 | Policy renewal creates a successor instead of transitioning the source, and the route/body are narrower than SPEC 11.2.6/11.2.10 | L |
| M-29 | Contract technical accounts use the `/technical-accounts` path, a narrow status set, and no period-overlap/window check | L |
| M-30 | Contract period bordereaux use a PROCESSED/FAILED vocabulary and event names, omit the SPEC line/exception staging, and accept an absent book header | L |
| M-31 | Direct Claims allocation error codes are remapped at the public surface | L |
| M-32 | Policy mass tort profile is a narrow DRAFT/COMPLETE upsert with different vocabularies and route | L |
| M-33 | Direct Claims list claimant filter is exact-match with no party reference check | L |
| M-34 | Contract cash calls add a SPEC-less route, lifecycle, and event names and omit the cash-call limit gate | L |
| M-35 | Payment allocations add a SPEC-less POST route and event name | L |
| M-36 | Direct Claims allocation erosion retry swallows the expert conflict and record failure | M |
| M-37 | Contract security/collateral uses a narrow derived-status projection and a wider legacy status vocabulary | L |
| M-38 | Policy installment dunning adds a SPEC-less route and event name and a different level vocabulary and book rule | L |
| M-39 | Policy program catalog uses a short read/create path, a different type/status vocabulary, and SPEC-less membership and event names | L |
| M-40 | Document content keeps a current pointer plus revisions under `/content/versions`, not the SPEC `/versions` store | L |
| M-41 | Policy credit notes use a short path, a four-state lifecycle, free-text reason, and new event names, with no approval or SAP step | L |

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

Policy programs add a second short-form row: the implemented catalog is
`/api/v1/programs` and `/api/v1/programs/{programId}`, while SPEC 11.2.10 lists
`/api/v1/policy/programs` and `/api/v1/policy/programs/{programId}` (M-39).
Policy credit notes add another short-form row: the implemented
`/api/v1/policies/{policyId}/credit-notes` versus SPEC 11.2.13's
`/api/v1/policy/policies/{policyId}/credit-notes` (M-41).

The ten global-search routes follow the same shorter form
(`/api/v1/{resource}/search`); their SPEC naming gap and validation differences
are recorded in M-23.

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
- `repos/eia-policy-domain/.../ProgramController.java:26` and
  `PolicyProgramController.java:22` - `/api/v1/programs` and
  `/api/v1/policies/{policyId}/program`
- `repos/eia-policy-domain/.../PolicyCreditNoteController.java:27` -
  `/api/v1/policies/{policyId}/credit-notes`, and
  `repos/eia-policy-expert/.../CreditNoteController.java:27-31` - the same
  public path plus the internal alias.
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
| Direct Claims (domain and expert) | `com.eia.directclaims.*.ApiError` | `{timestamp, status, code, message, path, details[{field, message}]}` plus `category` on the idempotency-reuse 409 |
| Payment (domain and expert) | `com.eia.payment.*.ApiError` | `{timestamp, status, code, message, path, details[{field, message}]}` |
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
collections in Round 5 are also bare arrays. The Policy program catalog list
(`GET /api/v1/programs`) is also a bare `Program[]` rather than the Policy page
envelope (M-39). There is no `page` object, no cursor, and no `total` in those
responses.

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
| Policy public billing | No `ETag`/`If-Match`; the expert still version-checks the policy row and a concurrent change is 409 `CONCURRENT_MODIFICATION` |
| Policy public renewal | No `If-Match`; the 201 successor carries its own `ETag` and a replay path does not exist |
| Policy public mass tort profile | No `ETag`/`If-Match`; a concurrent profile or policy change is 409 `CONCURRENT_MODIFICATION` |
| Policy expert GET/create/PATCH | Same ETag and If-Match behaviour as the public service |
| Contract public PATCH | Required `expectedVersion` body field; no ETag |
| Contract public bind and commutation | Required `expectedVersion` on bind; the commutation has no caller-supplied version |
| Direct Claims public PATCH | Not accepted; the domain reads and forwards the current version |
| Direct Claims expert PATCH | Optional body version |
| Direct Claims child PATCH (injuries, exposures, litigation, recoveries, liens) | Required body `expectedVersion` on the public and expert routes; stale is 409 |
| Assumed Claims public POST status | Required body version |
| Assumed Claims task PATCH | Required body `version` (the task version, not the claim version); a stale value is 409 `EIA-RNS-7802` and a repeated status is a no-op |
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
same header on both the public and the expert route. The 2026-10-20 billing
slice is the exception: the plan create and installment PATCH accept no key,
and a repeated terminal settlement is the retry-safe path:

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
  requires it on transaction submission. `Idempotent-Replayed` is not emitted
  by any other vertical.

The Direct Claims and Assumed Claims task and note POSTs are the second
implementation. As of contract 1.4.0 they accept the same header in both
verticals:

| Aspect | Direct Claims | Assumed Claims |
|---|---|---|
| Routes | `POST /api/v1/claims/{claimId}/tasks` and `/notes`, plus the `/internal/v1` expert equivalents | `POST /api/v1/assumed-claims/claims/{claimId}/tasks` and `/notes`; the domain calls the expert's `/internal/v1` alias |
| Key bounds | 1-64 printable ASCII characters without spaces; a blank value is treated as absent | 1-64 characters after trimming; a blank value is 400 |
| Invalid key | 400 `VALIDATION_ERROR`; no write | 400 `EIA-RNS-7004`, field `Idempotency-Key`, code `INVALID_IDEMPOTENCY_KEY`; no write |
| Scope | tenant + command type (`TASK_CREATE` / `NOTE_CREATE`) + key | tenant + command type (`CLAIM_TASK_CREATE` / `CLAIM_NOTE_CREATE`) + key |
| Store | `claim_command_idempotency`, primary key `(tenant_id, idempotency_key, command_type)` | `claim_command_idempotency`, primary key `(tenant_id, command_type, idempotency_key)` |
| Replay | 201 original body, `Idempotent-Replay: true`, no second row, claim bump, or event | the same |
| Fresh create | 201, `Idempotent-Replay: false` only when a non-blank key was supplied | 201, `Idempotent-Replay: false` on every create |
| Reuse | 409 `EIA-DIR-4091`, category `IDEMPOTENCY_KEY_REUSED`, `retryable: false` | 409 `EIA-RNS-4091`, category `CONFLICT`, `errors[0].code = IDEMPOTENCY_KEY_REUSED` |
| Concurrent first attempts | find-then-insert; see the race caveat below | atomic `INSERT ... ON CONFLICT DO NOTHING`, then replay the winner |

Residual differences:

- **Direct Claims reservation race.** `ClaimTaskService.create` and
  `ClaimNoteService.add` call `ClaimCommandIdempotencyRepository.find` and, on a
  miss, insert the dedupe row in the same transaction as the task or note. The
  insert is not an atomic upsert. Two truly concurrent first attempts with the
  same key can both miss the check; the second insert then violates the unique
  primary key and the request fails as 400 `DATA_CONSTRAINT` instead of a replay
  or 409. Sequential retries after the first commit replay correctly. A fix is
  an `INSERT ... ON CONFLICT DO NOTHING` reservation like the Assumed Claims
  one.
- **Header spelling and replay status.** The claim responses use
  `Idempotent-Replay` (no `d`) and keep the original 201 status on a replay;
  Policy and SPEC 12.6 use `Idempotent-Replayed` and replay a create as 200.
  The contract documents the implemented claim spelling.
- **Error category.** Direct Claims emits `category: IDEMPOTENCY_KEY_REUSED` on
  the 409, which is not one of the SPEC 6.11 categories (`CONFLICT` is).
  Assumed Claims uses `CONFLICT` and carries `IDEMPOTENCY_KEY_REUSED` as
  `errors[0].code`. The contract records the implemented Direct Claims value;
  canonicalizing it is part of the M-02 error-envelope work.
- **Blank-key handling.** Direct Claims treats a blank header as absent, while
  Assumed Claims rejects it as 400. Both otherwise accept 1-64 character
  values, except that Direct Claims also rejects non-printable ASCII and
  embedded spaces.
- **No TTL or purge.** Both implementations keep the idempotency row
  indefinitely; SPEC 12.6 specifies a 24-hour scope for transaction-submission
  idempotency but does not require a cleanup job for claim creates. Rows are
  scoped by tenant and are never replayed across tenants.
- **Coverage.** Contract, Cession, Retrocession, Document, Payment, and
  Notifications create commands still accept no `Idempotency-Key` and emit no
  replay marker. Policy billing's plan create and installment PATCH, the Policy
  renewal command, and the Policy mass tort profile upsert are also outside the
  Policy idempotency mechanism. The domain's shared mutation helper still emits
  `Idempotent-Replayed: false` on the renewal 201 even though no key is
  accepted, so a client must not read that header as proof that a retry is
  safe. A repeated mass tort PUT rewrites the profile and emits another event,
  so it is not retry-safe either. The header remains optional everywhere it
  exists, so a client that omits it is unaffected.

Evidence:

- `repos/eia-direct-claims-domain/.../ClaimDetailController.java` (tasks and
  notes), `ClaimDetailService.addTask`/`addNote`,
  `ClaimClient.addTask`/`changeTaskStatus`/`addNote` (forwards the header and
  reads `Idempotent-Replay`), `ClaimCommandResult.java`.
- `repos/eia-direct-claims-expert/.../ClaimTaskController.java`,
  `ClaimTaskService.create`/`changeStatus`, `ClaimNoteController.java`,
  `ClaimNoteService.add`, `IdempotencyKeys.java` (normalize, canonical hash),
  `ClaimCommandIdempotencyRepository.java` (find and insert),
  `IdempotencyKeyReusedException.java`,
  `src/main/resources/schema.sql:344-357` (`claim_command_idempotency`,
  primary key `(tenant_id, idempotency_key, command_type)`).
- `repos/eia-assumed-claims-domain/.../ClaimTaskNoteController.java`,
  `ClaimTaskNoteService.addTask`/`changeTaskStatus`/`addNote`,
  `IdempotencyKeys.java` (1-64 bounds), `AssumedClaimClient.addTask`/`addNote`
  (forwards the header and reads `Idempotent-Replay`), `ApiException`.
- `repos/eia-assumed-claims-expert/.../ClaimTaskController.java`,
  `ClaimTaskService.create`/`changeStatus`, `ClaimNoteController.java`,
  `ClaimNoteService.add`, `IdempotencyKeys.java` (canonical hash),
  `ClaimCommandIdempotency.java` (reserve/replay/complete),
  `ClaimCommandIdempotencyRepository.java` (`INSERT ... ON CONFLICT DO
  NOTHING`), `ApiException.idempotencyKeyReused` (`EIA-RNS-4091`),
  `src/main/resources/schema.sql:326-345` (`claim_command_idempotency`).
- Direct Claims expert tests: `ClaimTaskNoteIdempotencyIntegrationTest`
  (`taskCreateReplaysTheOriginal201WithoutDuplicateRowOrEvent`,
  `reusingATaskKeyWithADifferentBodyIs409AndWritesNothing`,
  `taskKeyIsScopedByCommandSoTheSameKeyCanCreateANote`,
  `anInvalidTaskKeyIsRejectedBeforeAnythingIsWritten`, and the note
  equivalents); `ClaimTaskNoteEndpointTest`. Domain test:
  `ClaimDetailControllerTest.expertIdempotencyKeyReuseIsPreservedAs409`.
- Assumed Claims expert tests: `ClaimTaskNoteIdempotencyIntegrationTest`
  (`taskReplayReturnsTheOriginalProjectionAndWritesNoDuplicateRowOrEvent`,
  `taskKeyReusedWithADifferentBodyIs409AndWritesNothing`,
  `aKeyIsScopedByCommandType`, `aKeyOutsideTheLengthBoundsIs400AndWritesNothing`,
  and the note equivalents). Domain tests: `ClaimTaskNoteControllerTest`
  (`forwardsAnIdempotencyKeyOnTaskCreate`, `rejectsAnIdempotencyKeyOutsideTheLengthBounds`,
  `preservesTheExpertIdempotencyConflict`).
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
  the header, `claimSummary`, occurrences, programs, or the
  claims/reinsurance projections. Round 5 adds versions, coverage and limit
  schedules, aggregate erosion, endorsements, insureds, locations,
  cancellations, and reinstatements, so those are no longer gaps. The
  2026-10-20 billing slice adds the installment plan and settlement; billing
  accounts, billing instructions, disputes, and commission statements from
  SPEC 11.2.13 remain gaps (M-27). The credit-note slice adds the narrow
  DRAFT/ISSUED/APPLIED/CANCELLED adjustment (M-41), so the request surface
  exists, but the SPEC approval, SAP credit-memo, tax, and original-invoice
  members remain gaps. The premium-receivables
  slice adds the tenant-wide receivable queue and the dunning slice adds the
  per-installment dunning history and command (M-38), so receivables and
  dunning are no longer resource gaps. The renewal
  slice adds successor-term creation with `renewedFromPolicyId`; the reverse
  `renewed_by_policy_id` pointer, the renewal-bound source transition, the
  renewal batch, non-renewal reasons, and renewal invitations remain gaps
  (M-28). The mass tort slice adds the narrow one-per-policy DRAFT/COMPLETE
  profile (M-32); the SPEC mass tort program, the wider profile columns, and
  the SPEC trigger/status vocabularies remain gaps.
- Contract: no `treatyNumber`, `contractBasis`, inception-date naming,
  `contract_section`, `contract_version`, `contract_sliding_scale`,
  `contract_premium`, `contract_reinstatement`, `contract_wording`,
  loss-aggregate, or mass-tort profile. Round 5 adds layers, participants,
  terms, security, cessions, commutations, and bind, so those are no longer
  gaps. The period-bordereau slice adds the cedent financial schedule and its
  RECEIVED -> PROCESSED|FAILED lifecycle; the legacy ingest header remains an
  internal surface. The SPEC `bordereau_line` and `bordereau_exception`
  staging, duplicate-line detection, reconciliation to a declared total, the
  exception report, and the SPEC single-bordereau `GET` remain gaps (M-30). The
  technical-account slice adds the periodic statement (`accountNumber`, period,
  the four financial components, derived balance, and DRAFT/ISSUED/SETTLED);
  the SPEC `technical_account_line` breakdown, the AGREED/DISPUTED/SUPERSEDED
  statuses, and the `/accounts` path remain gaps (M-29).
- Direct Claims: no `tortCode` (the implemented name is `causeCode`),
  `claimant` object, financial summary, reopen, documents, lineage, or work
  queues. Round 5 adds injuries, exposures, reserve history, the coverage
  decision, litigation, settlements, recoveries, liens, and close. The
  allocation slice adds policy-year/layer splits with summary totals, so those
  are no longer gaps. The list accepts the optional exact-match
  `claimantPartyId` filter in addition to `status` (M-33).
- Assumed Claims: no policy-year allocations, documents, lineage, or work
  queues. Round 5 adds loss advices, bordereau ingest, reserve history, cash
  calls, recoveries, commutation, disputes, audit, financials, and close.
- Document: no content, versions, associations, hashes, page count, OCR status,
  tags, holds, packages, requests, or retention class.
- Payment: no embedded `claim` object, `payee` object, `netAmount`, `method`,
  `dueDate`, `authority`, SAP postings, allocations, requests, batches,
  reconciliations, or escheatment. The implemented source link
  (`sourceType`/`sourceId`/`sourceReference`) is a flat denormalized reference,
  not the SPEC 11.7.4 `claim_vertical`/`claim_id`/`claim_number` projection, and
  there is no referential-integrity check that `sourceId` exists in the source
  vertical (M-24). `sourceReference` is stored on the payment so lists and
  record views can render and link the source without an N+1 lookup. The list
  also accepts a complete `sourceType` + `sourceId` pair to return the payments
  linked to one source; that filter is documented in `openapi/payment.yaml`
  1.3.0 and M-24.
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
| Policy `tortType` | Policy `direct_tort_code` (SPEC 11.2.4) |
| Policy `triggerType` | Policy `trigger_theory` (SPEC 11.2.4) |
| Contract `sharePct`, `signedLinePct`, `cessionPct` | percentages of 100 (`15.000000`), not the SPEC 12.2 fraction |
| Payment `sourceType` + `sourceId` + `sourceReference` | Payment `claim_vertical` + `claim_id` + `claim_number` (or the contract link) |

The contracts use the implemented names. Renaming any of these is a breaking
change and needs a major version.

## M-14 Eventing

The platform gained a transactional outbox library in Round 2
(`eia-platform/libs`) and the Party expert wrote its event in the same
transaction as the Party row. Round 5 rolled the outbox out to five more
experts, and the 2026-10-20 completion added the four remaining verticals. All
ten publishing verticals now emit a subset:

| Vertical | Implemented event names | Source |
|---|---|---|
| Party | `party.party.created`, `party.party.updated` | `repos/eia-party-expert/.../PartyEvents.java` |
| Policy | `policy.policy.created`, `policy.policy.updated`, `policy.policy.version-issued`, `policy.policy.endorsed`, `policy.policy.cancelled`, `policy.policy.reinstated`, `policy.policy.renewed`, `policy.billing-plan.created`, `policy.installment.paid`, `policy.installment.waived`, `policy.dunning.sent`, `policy.mass-tort-profile.updated`, `policy.program.created`, `policy.policy.program-assigned`, `policy.credit-note.issued`, `policy.credit-note.applied`, `policy.credit-note.cancelled` | `repos/eia-policy-expert/.../PolicyEvents.java` |
| Contract | `contract.contract.created`, `contract.contract.updated`, `contract.contract.bound`, `contract.contract.commuted`, `contract.cession.recorded`, `contract.technical-account.created`, `contract.technical-account.issued`, `contract.technical-account.settled`, `contract.bordereau.received`, `contract.bordereau.processed`, `contract.bordereau.failed`, `contract.cash-call.requested`, `contract.cash-call.issued`, `contract.cash-call.settled`, `contract.cash-call.cancelled`, `contract.security.recorded`, `contract.security.status-changed` | `repos/eia-contract-expert/.../ContractEvents.java` |
| Direct Claims | `direct.claim.registered`, `direct.claim.updated`, `direct.claim.assigned`, `direct.claim.coverage-assessed`, `direct.claim.reserve-changed`, `direct.claim.settlement-authorized`, `direct.claim.closed`, `direct.claim.task-created`, `direct.claim.task-completed`, `direct.claim.task-updated`, `direct.claim.note-added`, `direct.claim.allocation-created` | `repos/eia-direct-claims-expert/.../ClaimEvents.java` |
| Assumed Claims | `assumed.claim.registered`, `assumed.claim.updated`, `assumed.claim.assigned`, `assumed.claim.closed`, `assumed.claim.reopened`, `assumed.claim.loss-advice-posted`, `assumed.claim.reserve-changed`, `assumed.claim.cash-call-requested`, `assumed.claim.recovery-recorded`, `assumed.claim.commuted`, `assumed.claim.task-created`, `assumed.claim.task-completed`, `assumed.claim.task-updated`, `assumed.claim.note-added` | `repos/eia-assumed-claims-expert/.../AssumedClaimEvents.java` |
| Cession | `cession.cession.created`, `cession.cession.updated`, `cession.cession.handed-off` | `repos/eia-cession-expert/.../CessionEvents.java` |
| Retrocession | `retrocession.retrocession.created`, `retrocession.retrocession.updated`, `retrocession.retrocession.handed-off` | `repos/eia-retrocession-expert/.../RetrocessionEvents.java` |
| Document | `document.document.created`, `document.document.updated`, `document.document.status-changed`, `document.link.added`, `document.link.removed`, `document.content.uploaded` | `repos/eia-document-expert/.../DocumentEvents.java`, `DocumentLinkEvents.java`, `DocumentContentEvents.java` |
| Payment | `payment.payment.created`, `payment.payment.updated`, `payment.payment.status-changed` | `repos/eia-payment-expert/.../PaymentEvents.java` |
| Notifications | `notifications.notification.created`, `notifications.notification.sent` | `repos/eia-notifications-expert/.../NotificationEvents.java` |

The Payment `payment.payment.created` payload now also carries the optional
`sourceType`, `sourceId`, and `sourceReference` fields in its `data` object.
They are additive: `eventVersion` stays 1, the fields are absent or null on an
unlinked payment, and `payment.payment.updated` and `.status-changed` keep their
existing identity-only payloads.

The Document expert's link writes append `document.link.added` or
`document.link.removed` from `DocumentLinkEvents.java` in the same transaction
as the link row. Both use the `DocumentLink` aggregate with the link id and
version 1; the three document metadata events are unchanged. A content upload
appends `document.content.uploaded` from `DocumentContentEvents.java` in the
same transaction as the revision row, keyed by the `DocumentContent` aggregate
on the document id with the content revision as the aggregate version; the
payload repeats that revision as `version` while `eventVersion` stays 1.

Each controller or service calls `outbox.insert(OutboxEvent.fromEnvelope(...))`
in the same transaction as the aggregate write; for example
`repos/eia-payment-expert/.../PaymentService.java:39-66`,
`repos/eia-document-expert/.../DocumentService.java:38-55`, and the four
completion tests `PolicyOutboxIntegrationTest`, `ContractOutboxIntegrationTest`,
`DirectClaimsOutboxIntegrationTest`, and `AssumedClaimsOutboxIntegrationTest`.

Every other AsyncAPI channel and operation is marked `x-status: planned`, and
the catalog carries the implemented subset per vertical. The platform outbox
dispatcher (`RestClientOutboxDispatcher`, `OutboxDispatchService`,
`OutboxDispatchJob`) is implemented and is scheduled by a Quartz trigger in
each expert when `eia.outbox.enabled=true`; it posts each event to the
subscriber-defined HTTPS endpoint with the HMAC-SHA256 signature. The platform
`event-ingest` service (`eia-platform/event-ingest`, port 8102) is the inbox: it
validates the canonical envelope, verifies the signature when configured, and
stores each event idempotently in `eia_platform.inbox_event`; the
`/api/v1/events/{recent,stats}` endpoints expose the stream. It is not a
business subscriber: no vertical consumes another vertical's events, there is
no subscription registry or gap detection, and the `consumed` lists in the
catalog remain the planned SPEC subscriptions.

The dunning fact is a policy-level action: `PolicyEvents.dunningSent` builds
the payload from the policy, the dunned installment, the escalation level, the
delivery channel, the send instant, and the action status. The policy row
version advances with the action, so every dunning event is distinct. The name
is `policy.dunning.sent`; SPEC 11.2.13 publishes
`policy.billing.dunning-changed` instead, which remains planned (M-22, M-38).

The three credit-note facts are policy-level transitions:
`PolicyEvents.creditNoteStatusChanged` picks `policy.credit-note.issued`,
`.applied`, or `.cancelled` from the new status and builds the payload from the
policy identity and number, the credit-note identity and number, the amount as
a decimal string, the currency, and the status. Each accepted transition bumps
the policy row version, so every event is distinct. Creating the DRAFT note
bumps the policy version but writes no event; SPEC 11.2.13 publishes only
`policy.billing.credit-note-issued` (M-22, M-41).

The Contract expert's generic status command can additionally emit the
already-cataloged `contract.contract.signed`, `.endorsed`, `.expired`, and
`.cancelled` names when the target status matches. Those names remain published
and are not part of the implemented subset recorded in this change; the catalog
declares only the seventeen Contract events listed above. The three
technical-account facts are child-aggregate events: the envelope uses the
account id and its lifecycle version (1 for created, 2 for issued, 3 for
settled) while the outbox partition key stays the contract id. They have no
SPEC 11.3.9 equivalent (M-22, M-29). The three bordereau facts are also
child-aggregate events: the envelope uses the bordereau id and version 1 for
received and 2 for processed or failed, with the contract id as the partition
key. `received` matches SPEC; `processed` and `failed` replace the SPEC
`posted`/`rejected` names, which remain planned (M-22, M-30). The four cash-call
facts are child-aggregate events with cash-call versions 1/2/3 (M-34). The
security fact is a child aggregate with the security id at version 1 and the
contract id as the partition key; its payload carries the derived
`ACTIVE`/`EXPIRED` status of the public create, or a legacy bind-slice status
when the internal expert surface records it (M-37). The security status fact is
also a child aggregate, with the security id at version 2, or 3 when an expired
record is released, and the contract id as the partition key; its payload
carries the previous and new status (M-22, M-37).

Live evidence (2026-10-20): the running `eia-event-ingest` pod reported 14
events, all processed, and the recent types included `policy.policy.created`,
`contract.contract.created`, `direct.claim.registered`, and
`assumed.claim.registered`. The update and lifecycle names had not been
exercised by a live smoke at the time of this audit, so their implementation
status rests on the source and the integration tests, not on inbox data.

## M-16 Assumed Claims path alias

`AssumedClaimController`, `LossAdviceController`, `ReserveController`,
`CashCallController`, `RecoveryController`, `CommutationController`,
`DisputeController`, and `ClaimTaskNoteController` are each mapped to both
`/api/v1/assumed-claims` and `/api/v1/assumed-claims/claims`
(`@RequestMapping({...})` on every controller).
The web remote calls the `/claims` form. Both are documented: the base routes
under both path forms, the second-slice routes under the short form with an
`x-path-alias` naming the `/claims` equivalent, and the task/note routes under
the `/claims` form with an `x-path-alias` naming the short equivalent. The
duplicate surface should be reduced to one path; the alias is compatible today
because both are implemented.

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

The outbox rollout uses the names actually emitted by the services. Several
implemented names have no SPEC 11 definition; the rest exist in the SPEC
tables. The differences are:

| Vertical | Implemented | SPEC /
planned name |
|---|---|---|
| Policy | `policy.policy.created` / `.updated`; `policy.billing-plan.created`; `policy.installment.paid` / `.waived`; `policy.dunning.sent`; `policy.program.created` / `policy.policy.program-assigned`; `policy.credit-note.issued` / `.applied` / `.cancelled` | No SPEC name for created/updated: SPEC 11.2.9 starts at `policy.policy.quoted`. The billing plan name differs from SPEC 11.2.13 `policy.billing.plan-created`; the installment facts have no SPEC name; the dunning fact differs from SPEC 11.2.13 `policy.billing.dunning-changed`; the two program facts have no SPEC name because SPEC defines no program create or policy-assignment event. SPEC 11.2.13 publishes only `policy.billing.credit-note-issued` and defines no applied or cancelled fact, so all three credit-note names are new (M-41). `version-issued`, `endorsed`, `cancelled`, `reinstated`, `renewed`, and `mass-tort-profile.updated` match SPEC. |
| Contract | `contract.contract.updated`; `contract.technical-account.created` / `.issued` / `.settled`; `contract.bordereau.processed` / `.failed`; `contract.security.status-changed` | No SPEC name for updated, the technical-account facts, the two terminal bordereau facts, or the security status fact: SPEC 11.3.9 lists lifecycle verbs, the contract-level `contract.account.issued` / `.agreed` facts, `contract.bordereau.posted` / `.rejected`, and only the `contract.security.recorded` / `.breached` security facts. `created`, `bound`, `commuted`, `cession.recorded`, `contract.bordereau.received`, and `contract.security.recorded` match SPEC. |
| Direct Claims | `direct.claim.task-created` / `.task-completed` / `.task-updated` / `.note-added`; `direct.claim.assigned`; `direct.claim.allocation-created` | No SPEC names: SPEC 11.4.9 defines no assignment, task, note, or allocation-created event; it names the allocation fact `direct.claim.allocated`, which remains planned. `registered`, `updated`, `coverage-assessed`, `reserve-changed`, `settlement-authorized`, and `closed` match SPEC. |
| Assumed Claims | `assumed.claim.updated`; `assumed.claim.assigned`; `assumed.claim.task-created` / `.task-completed` / `.task-updated` / `.note-added` | No SPEC names: SPEC 11.5.9 lists lifecycle verbs only and defines no assignment, task, or note event. `registered`, `closed`, `reopened`, `loss-advice-posted`, `reserve-changed`, `cash-call-requested`, `recovery-recorded`, and `commuted` match SPEC. |
| Cession | `cession.cession.created` / `.updated` / `.handed-off` | `cession.case.created`, `cession.handoff.sent`/`.acknowledged` |
| Retrocession | `retrocession.retrocession.created` / `.updated` / `.handed-off` | `retrocession.case.created`, `retrocession.handoff.sent`/`.acknowledged` |
| Document | `document.document.created` / `.updated` / `.status-changed`; `document.link.added` / `.removed`; `document.content.uploaded` | `document.document.registered`, `document.document.associated`, plus the SPEC lifecycle verbs; no SPEC content-upload fact |
| Payment | `payment.payment.updated` / `.status-changed` | the SPEC per-verb names such as `payment.payment.authorized` |
| Notifications | `notifications.notification.created` / `.sent` | `notifications.notification.issued` / `.delivered` |

The catalog lists both sets and marks only the implemented ones. The names
without a SPEC equivalent are additive under EV-05: the catalog now publishes
them and records them in the implemented subset. Publishing a SPEC name in
addition to the implemented name is additive; renaming or removing an
implemented name is breaking and needs the EV-05 dual-publish window.

Evidence:

- `repos/eia-policy-expert/.../PolicyEvents.java:37-56` (policy, billing, dunning,
  mass tort, program, and credit-note names)
- `repos/eia-contract-expert/.../ContractEvents.java:41-56`
- `repos/eia-direct-claims-expert/.../ClaimEvents.java:57-68`
- `repos/eia-assumed-claims-expert/.../AssumedClaimEvents.java:52-65`
- `repos/eia-cession-expert/.../CessionEvents.java:27-29`
- `repos/eia-retrocession-expert/.../RetrocessionEvents.java:28-30`
- `repos/eia-document-expert/.../DocumentEvents.java:29-31`
- `repos/eia-document-expert/.../DocumentLinkEvents.java:26-28`
- `repos/eia-document-expert/.../DocumentContentEvents.java:26-27`
- `repos/eia-payment-expert/.../PaymentEvents.java:31-33`
- `repos/eia-notifications-expert/.../NotificationEvents.java:36-37`

Resolution: either align the implemented names with the SPEC (with a
dual-publish window) or amend the SPEC event tables. The contracts document
both until that decision.

## M-23 Global search paths and validation

The ten domain controllers expose a public search operation under the short
`/api/v1/{resource}/search` form and return the shared `SearchResponse`
envelope. The endpoints are implemented, routed by the gateway, and called by
the shell and the web remotes.

**SPEC naming.** SPEC has no per-vertical search API. SPEC 5.6 lists `/search`
as the shell page provided by "Shell + all", and SPEC 7.6 defines search only
as the `?q=` collection convention (minimum two characters, result highlights).
The SPEC 11 vertical tables name resources as `/api/v1/{vertical}/{resource}`.
Every search path therefore differs from the SPEC section naming, in the same
way as M-01. The contracts document the implemented short form because the
gateway, the shell, and every web remote already use it.

| Vertical | Documented path | Book | Implemented `limit` outside 1-25 |
|---|---|---|---|
| Party | `/api/v1/parties/search` | none | `< 1` is 400; `> 25` becomes 25 |
| Policy | `/api/v1/policies/search` | DIRECT | `< 1` is 400; `> 25` becomes 25 |
| Contract | `/api/v1/contracts/search` | ASSUMED | clamped to 1 or 25 |
| Direct Claims | `/api/v1/claims/search` | DIRECT | `<= 0` becomes 10; `> 25` becomes 25 |
| Assumed Claims | `/api/v1/assumed-claims/search` | ASSUMED | `<= 0` becomes 10; `> 25` becomes 25 |
| Cession | `/api/v1/cessions/search` | DIRECT | clamped to 1 or 25 |
| Retrocession | `/api/v1/retrocessions/search` | ASSUMED | clamped to 1 or 25 |
| Document | `/api/v1/documents/search` | none | clamped to 1 or 25 |
| Payment | `/api/v1/payments/search` | none | clamped to 1 or 25 |
| Notifications | `/api/v1/notifications/search` | none | clamped to 1 or 25 |

The canonical contract states the target: `limit` defaults to 10, must be
between 1 and 25, and an invalid value is 400 `application/problem+json`. No
service returns 400 for `limit > 25`; only Party and Policy return 400 for
`limit < 1`. The services therefore do not yet implement the documented
validation.

**Book wall.** Policy, Contract, Cession, and Retrocession return 400
`BOOK_REQUIRED` for a missing header and 404 `BOOK_SCOPE_VIOLATION` for a
different book, which matches the contract. Direct Claims and Assumed Claims
return 404 for both a missing and a different header; their documents therefore
describe 400 for the missing header as the canonical target and 404 for the
book mismatch. Tenant validation is 400 in all ten.

**Query semantics.** Every service trims `q` and performs a case-insensitive
contains; an absent or blank term returns the latest records. SPEC 7.6 requires
at least two characters and result highlights, neither of which is implemented.
The contract keeps `q` optional because the shell's empty-search landing state
depends on the blank-query behaviour.

Evidence:

- `repos/eia-party-domain/.../PartySearchController.java`, `SearchQuery.java`,
  `PartySearchRepository.java`
- `repos/eia-policy-domain/.../PolicySearchController.java`, `SearchQuery.java`,
  `PolicySearchRepository.java`
- `repos/eia-contract-domain/.../ContractController.java` (`search`),
  `ContractSearch.java`, `SearchResult.java`
- `repos/eia-direct-claims-domain/.../ClaimController.java` (`search`),
  `ClaimService.search`/`normalizeLimit`, `RequestGuard.java`
- `repos/eia-assumed-claims-domain/.../AssumedClaimController.java` (`search`),
  `AssumedClaimService.search`/`normalizeLimit`, `BookScopeFilter.java`
- `repos/eia-cession-domain/.../CessionController.java` (`search`),
  `CessionService.search`, `SearchResult.effectiveLimit`
- `repos/eia-retrocession-domain/.../RetrocessionController.java` (`search`),
  `RetrocessionService.search`, `SearchResult.effectiveLimit`
- `repos/eia-document-domain/.../DocumentController.java` (`search`),
  `DocumentService.search`
- `repos/eia-payment-domain/.../PaymentController.java` (`search`),
  `PaymentService.search`
- `repos/eia-notifications-domain/.../NotificationController.java` (`search`),
  `NotificationService.search`
- `repos/eia-frontend/shell/src/GlobalSearch.jsx` - the shell calls the ten
  documented paths and sends the book shown in the matrix.

Resolution: either implement the 400 for an out-of-range limit and the 400 for
a missing book in Direct Claims and Assumed Claims, or amend the contract and
SPEC 7.6 to the clamp and 404 behaviour. Add a per-vertical search section to
SPEC 11 (or a global-search section to SPEC 7.6) so the canonical paths have a
normative home. No path change is proposed now because the gateway, the shell,
and every web remote already call the documented routes.

## M-24 Payment source link is a flat triple, not the SPEC claim projection

SPEC 11.7.4 models the payment's business context as separate columns:
`claim_vertical` (`direct` or `assumed`), `claim_id`, `claim_number`,
`settlement_id`, `contract_id`, `contract_number`, and `payment_request_id`.
The implemented payment instead stores one optional, generic source link:

| Implemented field | Type | Rule | SPEC 11.7.4 equivalent |
|---|---|---|---|
| `sourceType` | enum | `DIRECT_CLAIM`, `ASSUMED_CLAIM`, `POLICY`, or `OTHER`; required whenever `sourceId` is supplied | `claim_vertical` plus the relation name |
| `sourceId` | UUID | Required for `DIRECT_CLAIM`, `ASSUMED_CLAIM`, and `POLICY`; omitted for an `OTHER` reference-only source | `claim_id` or `contract_id` |
| `sourceReference` | string, max 64 | Optional human label (for example `CLM-2026-0000001`); never replaces `sourceId` for a classified source | `claim_number` / `contract_number` projection |

Consequences:

- `sourceType` does not distinguish a claim from a settlement, or a policy from
  a contract; a contract payment has no matching classified value and falls
  under `OTHER`.
- `sourceId` is a plain UUID with no foreign key and no existence check against
  the Direct Claims, Assumed Claims, or Policy service. A create succeeds for a
  well-formed UUID that names no source record. The SPEC 11.7.8
  `payment.authorize` step 2 claim-capacity check is not implemented, and
  nothing in the payment flow resolves `sourceId` against the claim or
  contract.
- The link is denormalized on purpose. `sourceReference` is stored on the
  payment and appended to the global-search `secondary` line, and the payment
  web remote builds the cross-link from `sourceType`. A payment list or record
  therefore renders the source without an N+1 lookup per row. The full source
  object, the projected `claim_number`, and the source-vertical API call remain
  unimplemented.
- A payment with no source link is valid; the fields are optional on the create
  request, the projection, and the `payment.payment.created` payload. A created
  payment cannot add or change its source afterwards because the implemented
  API has no update command.
- The tenant-scoped list accepts the same optional `sourceType` + `sourceId`
  pair. The filter matches the exact normalized pair inside the tenant wall and
  keeps the newest-first order. Both values are required together, so `OTHER`
  cannot be listed by type alone, and `sourceReference` is not a filter
  parameter (global search matches it).

Evidence:

- `repos/eia-payment-domain/.../PaymentRules.java:110-137` and
  `repos/eia-payment-expert/.../PaymentRules.java:147-175`
  (`validateSourceLinkage`); the expert constants are at `:39-45`
  (`SOURCE_TYPES`, `SOURCE_REFERENCE_MAX_LENGTH`).
- `repos/eia-payment-expert/.../CreatePaymentRequest.java:19-21` and
  `Payment.java:26-28`; `repos/eia-payment-domain/.../PaymentDto.java:23-25`
  and `CreatePaymentCommand.java:17-19`.
- `repos/eia-payment-domain/.../PaymentService.java:107-117` (search matches
  `sourceId` and `sourceReference`) and `:134-155` (secondary suffix).
- `repos/eia-payment-domain/.../PaymentController.java:27-32` (optional
  `sourceType`/`sourceId` query parameters) and `PaymentService.java:29-45`
  (trim, forward, otherwise unfiltered); `PaymentClientTest.java:75-184`
  (forwarding and preserved 400 codes).
- `repos/eia-payment-expert/.../PaymentController.java:27-32`,
  `PaymentService.java:29-45` (normalization and pair rule),
  `PaymentRules.java:261-301` (`normalizeSourceType` and
  `validateSourceFilter`), and `PaymentRepository.java:57-68`
  (`findAllBySource` exact SQL and order).
- `repos/eia-payment-expert/src/test/java/com/eia/payment/expert/PaymentSourceFilterIntegrationTest.java:49-100`
  (newest-first exact match, tenant wall, unfiltered list, and invalid/partial
  pair rejection).
- `repos/eia-payment-expert/.../PaymentEvents.java:52-54` (created payload).
- `repos/eia-payment-expert/src/test/java/com/eia/payment/expert/PaymentOutboxIntegrationTest.java:87-127`
  (source persisted and emitted; OTHER reference-only).
- `repos/eia-payment-web/README.md:16-26` and `CHANGELOG.md:22-32` (hand-off
  parameters and source cross-links).

Resolution: either model `claim_vertical`/`claim_id`/`claim_number` explicitly,
validate `sourceId` against the source vertical before create or authorize, and
add the contract/settlement context, or accept the generic source triple as the
canonical Round 2 shape and amend SPEC 11.7.4 and the M-12 gap accordingly.

## M-25 Claim assignment contract gaps

Claim assignment is implemented on both claim verticals:

| Aspect | Direct Claims | Assumed Claims |
|---|---|---|
| Public route | `PATCH /api/v1/claims/{claimId}/assignment` | `PATCH /api/v1/assumed-claims/claims/{claimId}/assignment`, alias `/api/v1/assumed-claims/{claimId}/assignment` |
| Expert route | `PATCH /internal/v1/claims/{claimId}/assignment` | `PATCH /internal/v1/assumed-claims/{claimId}/assignment` |
| Body | `assignedAdjuster` required (max 128), `assignedTeam` optional (max 64), `expectedVersion` required | the same |
| Projection | nullable `assignedAdjuster`, `assignedTeam`, `assignedAt` on `Claim` | the same on `AssumedClaim` |
| Event | `direct.claim.assigned` | `assumed.claim.assigned` |
| Actor header | `X-EIA-Actor`; the expert also accepts `X-EIA-User` | `X-EIA-Actor` only |

The ownership semantics are the same on both verticals. The claim version is the
optimistic token: a stale `expectedVersion` is 409 and writes nothing.
`assignedAt` is the instant of the last real change, and a same-assignment retry
at the current version is a no-op that keeps the previous `assignedAt`, version,
audit trail, and event stream. A real change bumps the claim version, appends
the assignment audit entry, and writes the assignment event in the same
transaction. The acting identity is the optional `X-EIA-Actor` header, recorded
as `assigned_by` and in the audit entry, and defaults to the assigned adjuster
when the header is absent or blank. `assignedBy` is deliberately not returned in
the public `Claim`/`AssumedClaim` projection (M-20); it appears only in the
event payload and the audit trail.

Residual differences:

- **Assumed Claims requires a team at the domain edge.** The contract and the
  Assumed Claims expert allow `assignedTeam` to be omitted, but
  `repos/eia-assumed-claims-domain/.../AssignClaimCommand.java:16-17` declares
  it `@NotBlank`. A teamless assignment through the public route is therefore a
  400 before the expert call, while the same body sent directly to the expert is
  accepted with a null team (`AssumedClaimAssignmentEndpointTest.aTeamIsOptional...`).
  Direct Claims accepts a teamless assignment on both surfaces.
- **Direct Claims returns 409 for a negative expected version.** The contract
  requires an integer `>= 0` and a 400 for a violation. The Assumed Claims
  expert enforces `@PositiveOrZero`, but
  `repos/eia-direct-claims-expert/.../ClaimAssignmentRequest.java:14-18` only
  annotates `expectedVersion` with `@NotNull`, so `-1` reaches the service and
  is answered with 409 as a stale version rather than 400. The stale-version 409
  itself is correct.
- **Actor header alias.** The contract documents the shared optional
  `X-EIA-Actor` header. The Direct Claims expert controller also accepts
  `X-EIA-User` and lets it win when both are present; the Direct Claims domain
  public controller forwards only `X-EIA-Actor`. Assumed Claims accepts only
  `X-EIA-Actor`. A client that sends `X-EIA-Actor` behaves identically on every
  route, so the alias is additive rather than breaking.
- **Book wall.** Both public routes hide a missing or different book as 404
  (`BOOK_SCOPE_VIOLATION` in Direct Claims, `EIA-RNS-7005` in Assumed Claims),
  consistent with the other claim routes and SPEC 3.6.2/WALL-06, not the
  canonical 400 for a missing header that M-23 records for search.
- **Event names.** `direct.claim.assigned` and `assumed.claim.assigned` have no
  SPEC 11.4.9 or 11.5.9 equivalent; M-22 records that naming gap. The events are
  additive under EV-05.

Evidence:

- `repos/eia-direct-claims-domain/.../ClaimController.java:62-70` (public route
  and `X-EIA-Actor`), `ClaimService.assign`, `ClaimClient.assign`,
  `ClaimCommands.Assignment`, `ClaimDto.java:27-29`.
- `repos/eia-direct-claims-expert/.../ClaimAssignmentController.java:36-49`
  (`X-EIA-User`/`X-EIA-Actor`), `ClaimAssignmentRequest.java:14-18`,
  `ClaimService.assign:157-185`, `ClaimRepository.assign`,
  `ClaimEvents.assigned:199-206`.
- `repos/eia-assumed-claims-domain/.../AssumedClaimController.java:73-80`
  (public route and actor), `AssumedClaimService.assign:89-91`,
  `AssumedClaimClient.assign`, `AssignClaimCommand.java:12-21`,
  `AssumedClaimDto.java:25-27`.
- `repos/eia-assumed-claims-expert/.../AssumedClaimAssignmentController.java:29-49`
  (all three routes and `X-EIA-Actor`), `ClaimAssignmentRequest.java:18-27`,
  `AssumedClaimService.assign:160-190`, `AssumedClaimRepository.assign`,
  `AssumedClaimEvents.assigned:99-118`.
- Tests: `ClaimAssignmentControllerTest`, `ClaimAssignmentIntegrationTest`,
  `AssumedClaimAssignmentEndpointTest`, `AssumedClaimAssignmentServiceTest`,
  `AssumedClaimAssignmentOutboxIntegrationTest`, and
  `AssumedClaimAssignmentControllerTest` / `AssumedClaimAssignmentClientTest`
  on the domain side.

Resolution: drop `@NotBlank` from the Assumed Claims domain
`AssignClaimCommand.assignedTeam` (and the corresponding domain test
expectation), add `@PositiveOrZero` to the Direct Claims expert
`ClaimAssignmentRequest.expectedVersion`, and decide whether the `X-EIA-User`
alias is promoted into the shared contract or removed from the Direct Claims
expert. The contract documents the agreement (optional team, `expectedVersion >=
0`, shared `X-EIA-Actor`); the service fixes should follow in their own
repositories.

## M-26 Document association links are flat, not the SPEC association

SPEC 11.6.10 exposes `POST /api/v1/document/documents/{documentId}/associations`
and `DELETE .../associations/{associationId}`. SPEC 7.9 and 11.6 model an
association as a subject triple plus role, unique on `(document_id,
subject_vertical, subject_type, subject_id, role)`, and DOC-09 requires the
association to reference an existing subject, verified synchronously with the
owning vertical.

The implemented surface is a document-owned, tenant-scoped link:

| Aspect | Implemented | SPEC 11.6.10 / 7.9 |
|---|---|---|
| Routes | `GET|POST /api/v1/documents/{documentId}/links`, `DELETE .../links/{linkId}`, plus the same three on `/internal/v1` | `POST .../associations`, `DELETE .../associations/{associationId}` |
| Target | `linkedType` (closed enum) + `linkedId` UUID | `subject_vertical` + `subject_type` + `subject_id` |
| Role | none | required association role (`AUTHORITATIVE`, `SUPPORTING`, and so on) |
| Display | optional cached `linkedReference` (64 characters); `linkedLabel` is the reference or the first eight characters of `linkedId` | derived from the subject projection |
| Uniqueness | `(tenant_id, document_id, linked_type, linked_id)` | `(document_id, subject_vertical, subject_type, subject_id, role)` |
| Book | none; tenant-scoped only | the association carries the subject's book (SPEC 3.6) |
| Existence check | none; `linkedId` is stored without a call to the owning vertical | DOC-09 synchronous validation |
| Duplicate | 409 `DUPLICATE_LINK`, no second row or event | conflict |
| Remove | 204; unknown link is 404 `LINK_NOT_FOUND` | removal |
| Events | `document.link.added` / `document.link.removed` | `document.document.associated`; SPEC defines no removal event |

Consequences:

- The Document vertical owns the link and never resolves the target. A
  well-formed `linkedId` that names no record is accepted, so DOC-09 and the
  cross-vertical existence contract are not met.
- There is no role, book, or subject-vertical column, so a link cannot express
  the SPEC association role or be authorized by the subject's book.
- The list `GET /api/v1/documents` accepts only a complete `linkedType` +
  `linkedId` pair; a partial pair is 400 `INVALID_LINK_FILTER` and an unknown
  type is 400 `INVALID_LINKED_TYPE`. Search forwards `q` to the expert and
  matches document metadata or any link's `linkedReference`.
- The two event names have no SPEC 11.6.9 equivalent (M-22). They are additive
  under EV-05; the SPEC association fact remains planned.

Evidence:

- `repos/eia-document-domain/.../DocumentController.java:58-78` (public link
  routes and tenant header), `DocumentService.java:47-58`,
  `DocumentExpertClient.java` (link calls), `DocumentLinkDto.java:12-20`,
  `CreateDocumentLinkCommand.java:13-21`.
- `repos/eia-document-expert/.../DocumentLinkController.java:33-59` (public and
  internal routes, `X-EIA-Tenant`/`tenantId` fallback),
  `DocumentService.java:83-135` (list, duplicate guard, insert/delete plus
  outbox), `LinkedType.java:13-20`, `DocumentLink.java:15-40`,
  `CreateDocumentLinkRequest.java:16-20`, `DocumentLinkEvents.java:26-76`.
- `repos/eia-document-expert/src/main/resources/schema.sql` (`document_link`
  table, `uq_document_link_subject` unique key, `linked_type` check).
- Tests: `DocumentLinkApiTest`, `DocumentLinkClientTest`,
  `DocumentLinkControllerTest`, `DocumentLinkIntegrationTest`,
  `DocumentLinkRepositoryPostgresTest`.

Resolution: either model the SPEC association triple, role, and book, validate
the target with its owning vertical (DOC-09), and publish
`document.document.associated`, or accept the flat tenant-scoped link as the
canonical shape and amend SPEC 7.9, 11.6.9, 11.6.10, and DOC-09. The contract
documents the implemented link shape.

## M-27 Policy billing and premium-receivable route, event, and status naming

SPEC 11.2.13 defines the billing surface as
`GET/POST /api/v1/policy/policies/{policyId}/installments` plus the billing
account, billing-instruction, receivable, credit-note, dunning, dispute, and
commission-statement routes. The 2026-10-20 slices implement the installment
plan and its settlement, the tenant-wide receivable read, and the
per-installment dunning history:

| Aspect | Implemented | SPEC 11.2.13 |
|---|---|---|
| Read plan | `GET /api/v1/policies/{policyId}/billing` | `GET /api/v1/policy/.../installments` |
| Create plan | `POST /api/v1/policies/{policyId}/billing` | `POST /api/v1/policy/.../installments` |
| Settle installment | `PATCH /api/v1/policies/{policyId}/billing/installments/{installmentId}` | No API row; billing instructions carry the status |
| Receivable queue | `GET /api/v1/billing/installments` (tenant-wide, outside `/api/v1/policies`) | No API row; SPEC 11.2.13 defines the per-policy plan, not a cross-policy receivable read |
| Dunning | `GET/POST /api/v1/billing/installments/{installmentId}/dunning` (per installment, outside `/api/v1/policies`) | No public API row; the only dunning command is the internal `POST /internal/v1/policies/{id}/dunning-status` |
| Plan event | `policy.billing-plan.created` | `policy.billing.plan-created` |
| Installment events | `policy.installment.paid`, `policy.installment.waived` | No SPEC name |
| Dunning event | `policy.dunning.sent` | `policy.billing.dunning-changed` |
| Plan status | `ACTIVE`, `COMPLETE`, `CANCELLED` | `DRAFT`, `ACTIVE`, `SUPERSEDED`, `CANCELLED` |
| Installment status | `DUE`, `OVERDUE`, `PAID`, `WAIVED` | Billing-instruction status values |
| Dunning level | `REMINDER`, `FIRST_NOTICE`, `SECOND_NOTICE`, `COLLECTIONS` | `billing_account.dunning_status`: `CLEAR`, `REMINDER`, `DUNNING`, `LEGAL`, `BLOCKED`; collections flow `CURRENT -> REMINDER -> DUNNING_1 -> DUNNING_2 -> NOTICE -> CANCELLATION_PENDING -> CANCELLED` |

The projection is the domain's flat public DTO, which renames the plan identity
`planId` and the installment identity `installmentId`; the expert's internal
view nests `{plan, installments}` and is not part of the public contract. The
public billing routes accept an absent `X-EIA-Book` for compatibility with the
other Policy proxy routes, while a supplied value must be DIRECT and another
book is hidden as 404 `BOOK_SCOPE_VIOLATION`. The domain always sends DIRECT to
the expert.

The receivable queue is a separate read over the same installment plan. It has
no `policyId`, so it is mounted at `/api/v1/billing/installments`, outside
`/api/v1/policies`, and the gateway routes `/api/v1/billing/**` to the Policy
domain. The domain normalizes the optional DUE/OVERDUE `status` (trim and
upper-case), defaults and validates `limit` to 1..200 (default 20), forwards
`dueBefore` as an inclusive cutoff, and proxies the expert's
`/internal/v1/billing/installments` read with the tenant and DIRECT book. The
expert clamps the limit to 1..200 and defaults it to 100 for internal callers,
derives OVERDUE and `daysPastDue` from the due date without rewriting the
stored row, and returns only unsettled installments, so `paidAt` and `paymentId`
are null on every item. The public projection is the domain's
`Receivable`/`ReceivableSummary`: `{installmentId, planId, planNumber,
policyId, policyNumber, insuredPartyId, installmentNumber, dueDate, amount,
currency, status, daysPastDue, paidAt, paymentId}` inside `{items, totalAmount,
overdueAmount, count}`.

The dunning slice is a separate per-installment surface at
`/api/v1/billing/installments/{installmentId}/dunning`: it records and lists
actions instead of reading a SAP-sourced level, uses its own closed level and
channel vocabularies, and its history is keyed by installment rather than by
billing account. The route, vocabulary, book rule, and event naming are
recorded in M-38.

Evidence:

- `repos/eia-policy-domain/.../PolicyBillingController.java` (public routes and
  the `requireDirectWhenPresent` guard).
- `repos/eia-policy-domain/.../BillingPlan.java`, `Installment.java` (flat
  public DTO names).
- `repos/eia-policy-domain/.../ReceivableController.java`,
  `ReceivableService.java`, `Receivable.java`, `ReceivableSummary.java`
  (`/api/v1/billing/installments`, status and limit normalization, projection).
- `repos/eia-policy-domain/.../PolicyClient.java:379-450`
  (`/internal/v1/billing/installments` call and projection remap).
- `repos/eia-policy-expert/.../BillingController.java`,
  `BillingRules.java`, `PolicyEvents.java` (route, vocabulary, event names).
- `repos/eia-policy-expert/.../BillingReceivablesController.java`,
  `BillingService.java:75-102`, `BillingRepository.java:155-194`,
  `BillingRules.java:101-140`, `InstallmentReceivable.java`,
  `ReceivablesView.java` (tenant-wide query, derived status, totals).
- `repos/eia-policy-expert/src/main/resources/schema.sql:388-433` (plan and
  installment status check constraints).

Resolution: either amend SPEC 11.2.13 to the implemented `/billing`,
`/billing/installments/{installmentId}/dunning`, and cross-policy
`/api/v1/billing/installments` routes, flat projections, event names, and
status/level vocabularies, or add the SPEC route and names as aliases with an
EV-05 dual-publish window. The billing account, instruction, dispute, and
commission-statement routes remain unimplemented (M-12); the receivable queue
and the dunning history are implemented as above, and policy credit notes are
implemented as a separate child resource recorded in M-41.

## M-28 Policy renewal creates a successor instead of transitioning the source

SPEC 11.2.6 puts renewal on the policy lifecycle: `IN_FORCE` or `EXPIRED`
transitions to `RENEWED` when the renewal is bound, and the SPEC `policy` table
carries `renewal_of_policy_id` (prior) and `renewed_by_policy_id` (successor).
SPEC 11.2.10 mounts the command at
`POST /api/v1/policy/policies/{policyId}/renew`. The 2026-10-20 slice implements
a successor-creation command instead:

| Aspect | Implemented | SPEC |
|---|---|---|
| Public path | `/api/v1/policies/{policyId}/renew` | `/api/v1/policy/policies/{policyId}/renew` (the M-01 short form) |
| Source effect | Unchanged: stays `ISSUED`, `IN_FORCE`, `ENDORSED`, or `REINSTATED` | Transition to `RENEWED` |
| New term | Brand-new DRAFT policy row with its own number and initial DRAFT version | Renewal bound on the policy with a `RENEWAL` change type |
| Lineage | One field, `renewedFromPolicyId` (successor -> source) | `renewal_of_policy_id` plus the reverse `renewed_by_policy_id` |
| Eligibility | 409 `RENEWAL_NOT_ALLOWED` outside the four statuses | The transition table allows `IN_FORCE` and `EXPIRED` |
| Body | `effectiveDate` and `expirationDate` required; premium and limit overrides optional | SPEC defines no renewal command body |
| Headers | `X-EIA-Tenant` required and `X-EIA-Book: DIRECT` required | The SPEC 3.6 book wall |
| Idempotency / concurrency | No `Idempotency-Key` or `If-Match` (M-06, M-07) | SPEC 12.6 |

The expert's internal route also diverges from the public contract:

- `repos/eia-policy-expert/.../RenewPolicyRequest.effectiveDate` is optional and
  defaults to the source expiration plus one day, while the domain
  `RenewPolicyCommand` marks both dates `@NotNull` and the public contract
  requires both. The expert's `/internal/v1` alias and its relaxed default are
  not part of the public contract.
- The domain guard is `BookScope.requireDirectWhenPresent`, so an absent
  `X-EIA-Book` is accepted even though the contract requires `DIRECT` and a
  different book is hidden as 404 `BOOK_SCOPE_VIOLATION`.
- The domain's shared mutation response helper emits
  `Idempotent-Replayed: false` on the renewal 201 although the route accepts no
  `Idempotency-Key`, so that header does not make a retry safe.

Evidence:

- `repos/eia-policy-expert/.../PolicyRenewalController.java`,
  `PolicyRenewalService.java`, `PolicyRenewalRules.java`,
  `RenewPolicyRequest.java`, `Policy.java`, and `PolicyEvents.java` (the
  `renewed` factory).
- `repos/eia-policy-expert/src/main/resources/schema.sql:24,40,44`
  (`renewed_from_policy_id` and its index).
- `repos/eia-policy-domain/.../PolicyContractController.java` (`/renew`),
  `PolicyContractService.renewPolicy`/`validateRenewal`,
  `PolicyClient.renewPolicy`/`mutateDirect`, `RenewPolicyCommand.java`, and
  `PolicyDto.java` (`renewedFromPolicyId`).
- Tests: `PolicyRenewalControllerTest`, `PolicyRenewalIntegrationTest`,
  `PolicyRenewalRulesTest`, and `PolicyContractControllerTest`
  (`renewsAPolicyAndReturnsTheSuccessor`, `validatesTheRenewalBody`,
  `rejectsANonDirectBookBeforeCallingTheExpert`,
  `preservesTheExpertRenewalConflictProblem`).

Resolution: either implement the SPEC 11.2.6 source transition (mark the source
`RENEWED`, issue a `RENEWAL` version, and expose the reverse
`renewed_by_policy_id` pointer) plus the renewal batch, or amend SPEC
11.2.4/11.2.6/11.2.10 to the successor-DRAFT lineage and the short public path.
The contract documents the implemented successor creation, requires both dates
and `DIRECT` on the new public route, and keeps the expert's relaxed default out
of the public contract.

## M-29 Contract technical accounts are a flat period summary

The Contract technical-account slice implements the periodic statement of an
ASSUMED treaty, but narrower than SPEC 11.3.4, 11.3.9, and 11.3.10.

| Area | Implemented | SPEC / gap |
|---|---|---|
| Path and mount | `GET/POST /api/v1/contracts/{contractId}/technical-accounts`, `PATCH /api/v1/contracts/{contractId}/technical-accounts/{accountId}/status` | SPEC 11.3.10 names `GET /api/v1/contracts/{contractId}/accounts`; the implemented controller uses `/technical-accounts`. The public path is documented; the expert also mounts the same controller under `/internal/v1`. |
| Statuses | `DRAFT`, `ISSUED`, `SETTLED`; only DRAFT -> ISSUED -> SETTLED | SPEC 11.3.4 also names `AGREED`, `DISPUTED`, and `SUPERSEDED`. A request with `DRAFT` is 400 `INVALID_STATUS`; a skipped or repeated edge is 409 `INVALID_STATUS_TRANSITION`. |
| Lines | One row with `cededPremium`, `cededLosses`, `commission`, `otherCharges`, and a derived `balance` | SPEC's separate `technical_account_line` breakdown and the cash-call/settlement linkage are absent. |
| Period | `periodStart < periodEnd`; unique exact `(tenant, contract, periodStart, periodEnd)` | There is no overlap rejection (CTR-07) and no contract-window or contract-currency equality check (CTR-08). The unique key catches only an identical period, so two overlapping but non-identical periods are accepted. |
| Book | `X-EIA-Book: ASSUMED` when present; another book is 404 `BOOK_SCOPE_VIOLATION` | The canonical contract requires the header, but the domain accepts an absent header for compatibility with the other Contract proxy routes (`requireAssumedBookWhenPresent`). The expert internal alias does not check the book at all. |
| Events | `contract.technical-account.created`, `.issued`, `.settled` | SPEC 11.3.9 defines `contract.account.issued` and `contract.account.agreed`; the implemented names have no SPEC equivalent (M-22). The envelope uses the account id and lifecycle version 1/2/3 while the outbox partition key stays the contract id. |
| Balance | Derived at create as `cededPremium - commission - cededLosses + otherCharges`; positive means due from the cedent to the reinsurer | The balance is not reconciled against paid losses, cash calls, or settlement evidence, and there is no accounting line or payment link. |

Evidence:

- `repos/eia-contract-domain/.../TechnicalAccountController.java:68-77`
  (the book wall runs only when the header is present) and
  `TechnicalAccountClient.java:28-36` (forwards ASSUMED to the expert).
- `repos/eia-contract-expert/.../technicalaccount/TechnicalAccountController.java:45-49,69-131`
  (public and internal prefixes, tenant resolution, create and status flow).
- `repos/eia-contract-expert/.../technicalaccount/TechnicalAccountRules.java:30-87`
  (period order, ISO currency, non-negative amounts, derived balance, status
  parsing, and the transition table; no contract-window, currency-equality, or
  overlap check).
- `repos/eia-contract-expert/.../technicalaccount/TechnicalAccountStatus.java:11-22`
  (DRAFT/ISSUED/SETTLED only).
- `repos/eia-contract-expert/.../technicalaccount/TechnicalAccountRepository.java:49-114`
  (newest-first list, unique-period conflict, compare-and-set status update).
- `repos/eia-contract-expert/src/main/resources/schema.sql:354-381`
  (unique exact period, non-negative amounts, currency pattern, status check).
- `repos/eia-contract-expert/.../ContractEvents.java:54-56,195-246`
  (event names, child-aggregate id/version, contract partition key).
- `openapi/contract.yaml` (introduced in 2.2.0, now 3.1.0) and the README
  technical-account section record the implemented shape.

Resolution: the implemented slice is documented as canonical for now. Closing
the gap means adding the SPEC `/accounts` alias (or amending SPEC 11.3.10),
implementing the AGREED/DISPUTED/SUPERSEDED transitions and the line breakdown,
and enforcing period overlap plus the contract window and currency equality. The
event names follow EV-05: keep publishing the implemented names and add a SPEC
name only through a dual-publish window. Renaming the path or statuses is
breaking and needs an ADR and a `/v2` or dual-mount period.

## M-30 Contract period bordereaux use a narrower lifecycle and omit line staging

SPEC 11.3.4 defines `contract_bordereau` with `bordereau_type`,
`period_from`/`period_to`, `received_at`, source metadata, the seven-value ingest
status (`RECEIVED`, `PARSING`, `VALIDATED`, `PARTIALLY_POSTED`, `POSTED`,
`REJECTED`, `SUPERSEDED`), counts, total, and checksum, plus the separate
`bordereau_line` and `bordereau_exception` tables. SPEC 11.3.8 `contract.bordereau`
parses, validates, reconciles, posts, and emits `contract.bordereau.posted`;
SPEC 11.3.9 also names `contract.bordereau.rejected`. The 2026-10-20 slice
implements a narrower financial period bordereau on the shared table:

| Area | Implemented | SPEC / gap |
|---|---|---|
| Routes | `GET/POST /api/v1/contracts/{contractId}/bordereaux` and `PATCH .../bordereaux/{bordereauId}/status` (the M-01 short form) | SPEC 11.3.10 also has `GET /api/v1/contract/bordereaux/{bordereauId}`; the public API has no single-bordereau GET. |
| Projection | Flat financial period: number, period, received date, currency, four amounts, line count, notes, status, technical account, createdAt | The ingest fields `bordereauType`, `sourceFormat`, `sourceReference`, `checksum`, `validLineCount`, `exceptionCount`, `totalAmount`, and `processedAt` remain only on the internal `BordereauHeader`; the public projection is the domain DTO, which remaps the expert's `id` to `bordereauId` and drops `tenantId`. |
| Status | `RECEIVED`, `PROCESSED`, `FAILED`; only `RECEIVED -> PROCESSED|FAILED`, both terminal | SPEC also names `PARSING`, `VALIDATED`, `PARTIALLY_POSTED`, `POSTED`, `REJECTED`, and `SUPERSEDED`. Processing is a terminal success rather than a staged posting, so there is no partial posting or supersession. |
| Lines and exceptions | None; one header row per period | No `bordereau_line` or `bordereau_exception` persistence, duplicate-line detection, reconciliation to a declared total, exception report, or partial posting. CTR-09 and CTR-10 and the SPEC 11.3.11 staging contract are not met. |
| Period and currency | `periodStart < periodEnd`; exact `(tenant, contract, periodStart, periodEnd)` unique; uppercase ISO 4217 currency required | No period-overlap rejection, no contract-window check, and no currency reconciliation against the contract; a currency that differs from the contract is accepted. |
| Technical account | `PROCESSED` creates or reuses the DRAFT account for the same period and links `technicalAccountId`; the account lifecycle is DRAFT/ISSUED/SETTLED | The SPEC account paths, the AGREED/DISPUTED/SUPERSEDED statuses, and the line breakdown remain M-29 gaps. |
| Book | Canonical contract requires `X-EIA-Book: ASSUMED`; another book is 404 `BOOK_SCOPE_VIOLATION` | The domain's `requireAssumedBookWhenPresent` accepts an absent header, and the expert checks no book at all; the tenant is a header on the domain and a header or `tenantId` query on the expert (M-08). |
| Events | `contract.bordereau.received`, `.processed`, `.failed` | SPEC 11.3.9 publishes `.received`, `.posted`, and `.rejected`. `received` matches; the two terminal names are new and `posted`/`rejected` remain planned (M-22). |

Evidence:

- `repos/eia-contract-domain/.../BordereauController.java:38-67` (tenant
  header, optional ASSUMED book guard, list/create/status routes) and
  `ContractCommandRules.java:151-184` (domain create and status validation).
- `repos/eia-contract-domain/.../BordereauClient.java:32-104` (public path,
  `tenantId` query, forwarded `ASSUMED` header, status path) and
  `Bordereau.java:23-40` (`@JsonAlias("id")` remap and the flat projection).
- `repos/eia-contract-expert/.../bordereau/BordereauController.java:52-144`
  (public period controller, tenant resolution, technical-account reuse, outbox).
- `repos/eia-contract-expert/.../bordereau/BordereauRules.java:33-102`
  (period order, currency, non-negative amounts, status parsing and transitions).
- `repos/eia-contract-expert/.../bordereau/BordereauRepository.java:61-132`
  (period-row filter, newest-first order, unique-period conflict,
  compare-and-set status).
- `repos/eia-contract-expert/.../bordereau/BordereauStatus.java:11-33`
  (RECEIVED/PROCESSED/FAILED and versions 1/2) and
  `ContractBordereauHeader.java:18-57` (legacy ingest header).
- `repos/eia-contract-expert/.../ContractEvents.java:218-287` (bordereau event
  names, child aggregate id/version, nested and flat period, contract partition
  key).
- `repos/eia-contract-expert/src/main/resources/schema.sql:255-369`
  (`contract_bordereau` columns, status check with both vocabularies, period
  unique index, non-negative financial amounts).
- `openapi/contract.yaml` 3.1.0 and the README period-bordereau section record
  the implemented shape.

Resolution: document the implemented period slice as canonical for now. Closing
the gap means adding the line and exception staging with duplicate detection,
reconciliation, and an exception report; enforcing period overlap, the contract
window, and contract-currency equality; exposing the SPEC single-bordereau GET;
and either enforcing `X-EIA-Book: ASSUMED` at the domain edge and in the expert
or relaxing the contract. Renaming the statuses or the two terminal event names
is breaking and needs an ADR and an EV-05 dual-publish window.

## M-31 Direct Claims allocation error codes are remapped at the public surface

The canonical contract documents the Direct Claims allocation error codes at the
public surface:

| Status | Canonical code | Meaning |
|---|---|---|
| 400 | `POLICY_MISMATCH` | The requested `policyId` is not the claim's own policy. |
| 400 | `MASS_TORT_YEAR_OUTSIDE_BLOCK` | The requested `policyYear` is outside the coverage block of a COMPLETE policy mass-tort profile. |
| 409 | `ALLOCATION_EXCEEDS_100` | The allocation percentages already recorded for the claim plus the new one would exceed 1. |

The expert emits `POLICY_MISMATCH` and `ALLOCATION_EXCEEDS_100` from
`ApiExceptionHandler.java`. The Direct Claims domain receives them as an
upstream `RestClientResponseException` and maps the status in its own
`ApiExceptionHandler`:

- an expert 400 becomes 400 `VALIDATION_ERROR` with the expert detail preserved;
- an expert 409 becomes 409 `CONFLICT` unless the expert code is
  `EIA-DIR-4091`, the only code the domain preserves.

`MASS_TORT_YEAR_OUTSIDE_BLOCK` is different: the public domain raises it
itself. `ClaimDetailService.requireMassTortCoverageBlock` reads the policy's
mass-tort profile before it forwards the create and throws
`MassTortYearOutsideBlockException`, which the domain handler maps to 400
`MASS_TORT_YEAR_OUTSIDE_BLOCK`. The code is preserved end to end and is not part
of the upstream remap.

The domain tests assert only the status and detail for the two expert codes:
`ClaimDetailControllerTest.expertPolicyMismatchIsPreservedAs400` expects 400
`VALIDATION_ERROR`, and `expertAllocationExceedsHundredIsPreservedAs409` does
not assert the code. A third test,
`allocationOutsideTheMassTortBlockIsA400`, asserts the mass-tort code. A public
client therefore sees the right statuses and detail for the two expert codes but
not `POLICY_MISMATCH` or `ALLOCATION_EXCEEDS_100`; it does see
`MASS_TORT_YEAR_OUTSIDE_BLOCK`.

Evidence:

- `repos/eia-direct-claims-expert/.../ClaimAllocationService.java` (claim-policy
  match and percentage-total guard).
- `repos/eia-direct-claims-expert/.../ApiExceptionHandler.java:87-101`
  (`POLICY_MISMATCH`, `ALLOCATION_EXCEEDS_100`).
- `repos/eia-direct-claims-domain/.../ApiExceptionHandler.java:56-61,75-100`
  (the mass-tort 400 mapping; 400 -> `VALIDATION_ERROR`, 409 -> `CONFLICT`;
  `EIA-DIR-4091` preserved).
- `repos/eia-direct-claims-domain/.../ClaimDetailService.java:181,189-212`
  (the profile read and inclusive coverage-block guard) and
  `MassTortYearOutsideBlockException.java` (the guard exception).
- `repos/eia-direct-claims-domain/.../ClaimDetailControllerTest.java:342-435`
  (the two remap tests and the mass-tort test).

Resolution: preserve the two expert codes in the domain's upstream-error
mapping, or amend this contract and SPEC 11.4.10 to the remapped codes. The
contract keeps the stable expert codes because they are the only codes that
distinguish the policy and percentage rules from generic validation and
concurrency failures. The statuses and detail text already match, and the
mass-tort code needs no remap.

## M-32 Policy mass tort profile is a narrow DRAFT/COMPLETE upsert

SPEC 11.2.4 defines `policy_mass_tort_profile` with `direct_tort_code`,
`trigger_theory`, the six-value `allocation_method`, the optional secondary
tort codes, product names, exposure period, claimant estimate, known claim
count, defense strategy, settlement authority, claims-handling instructions,
MDL and bankruptcy-trust references, coverage counsel, review dates, and
`status` `ACTIVE`/`SUPERSEDED`/`UNDER_REVIEW`. SPEC 11.2.10 mounts GET/PUT at
`/api/v1/policy/policies/{policyId}/mass-tort-profile`; SPEC 11.2.9 publishes
`policy.mass-tort-profile.updated`; the SPEC command validates allocation
percentages and requires a human approval. The 2026-10-20 slice implements a
narrow one-per-policy profile:

| Area | Implemented | SPEC / gap |
|---|---|---|
| Path | `GET/PUT /api/v1/policies/{policyId}/mass-tort-profile` (the M-01 short form) | SPEC 11.2.10 `/api/v1/policy/policies/{policyId}/mass-tort-profile` |
| Projection | `{profileId, policyId, tortType, triggerType, allocationMethod, allocationNotes, coverageBlockStart, coverageBlockEnd, status, updatedAt}` | SPEC also has secondary tort codes, product names, exposure window, claimant estimate, known claim count, defense strategy, settlement authority, claims-handling instructions, MDL and bankruptcy-trust references, coverage counsel, review frequency and dates, and version. |
| Tort catalog | `ASBESTOS`, `SILICA`, `TALC`, `PFAS`, `OPIOIDS`, `PRODUCT_LIABILITY`, `ENVIRONMENTAL`, `OTHER` | SPEC Appendix E adds `BENZENE`, `OPIOID` (singular), `GLYPHOSATE`, `HAIR_RELAXER`, `HERNIA_MESH`, `TV_MESH`, `IVC_FILTER`, `ESSure`, `CPAP`, `EARPLUG`, `ZANTAC`, `E_CIGARETTE`, `PARAQUAT`, `ACETAMINOPHEN`, `Zofran`, `DEPAKOTE`, `RISPERDAL`, `ROUNDUP`, `SEXUAL_ABUSE`, `CLERGY_ABUSE`, `CTE`, `WILDFIRE`, and `COVID_BI`, among others. `PRODUCT_LIABILITY` is not an Appendix E code. |
| Trigger vocabulary | `EXPOSURE`, `MANIFESTATION`, `INJURY`, `REVISIONIST` | SPEC `EXPOSURE`, `INJURY_IN_FACT`, `MANIFESTATION`, `CONTINUOUS_TRIGGER`, `ALL_SUMS`, `CLAIMS_MADE` |
| Status | `DRAFT`, `COMPLETE`; COMPLETE gates the notes and both block dates | SPEC `ACTIVE`, `SUPERSEDED`, `UNDER_REVIEW`; no COMPLETE gate |
| Command | PUT upsert. The expert returns 201 on create and 200 on replace, but the public domain controller returns 200 for both. No approval step and no allocation percentages; 2000-character notes cap; inclusive date block. | SPEC `policy.update-mass-tort-profile` is an approval command and validates allocation percentages that sum to 1; the canonical contract keeps the 201 create response. |
| Concurrency and idempotency | No `If-Match` or `Idempotency-Key`; `updatedAt` is informational; a concurrent write is 409 `CONCURRENT_MODIFICATION`, and a repeated PUT rewrites the profile and emits another event | SPEC 12.6 |
| Book | `X-EIA-Book: DIRECT` when present; an absent header is accepted; another book is 404 `BOOK_SCOPE_VIOLATION` | The canonical contract requires DIRECT; `BookScope.requireDirectWhenPresent` accepts an absent header |
| Event | `policy.mass-tort-profile.updated`; payload has the policy identity, status, tort, trigger, allocation method, and coverage-block dates; no profile id or notes | The name matches SPEC 11.2.9. The profile id is deliberately omitted because the policy is the aggregate; the notes are not part of the allocation context. |

The Direct Claims allocation create consumes the profile.
`ClaimDetailService.requireMassTortCoverageBlock` reads
`GET /api/v1/policies/{policyId}/mass-tort-profile` and, when the profile is
COMPLETE with both block dates, rejects a `policyYear` outside the inclusive
start/end years with 400 `MASS_TORT_YEAR_OUTSIDE_BLOCK`. Both boundary years are
allowed. A DRAFT profile, a COMPLETE profile without both dates, a policy
without a profile (404), and an unavailable or unreadable Policy profile all
allow the allocation: `PolicyMassTortClient.findProfile` turns every non-2xx and
every transport or conversion failure into an empty result, so the profile read
fails open and is never an availability dependency. The guard runs on the public
create only; the expert allocation write does not re-read the profile. SPEC
11.4.7 `DIR-15` and SPEC 11.2.7 `POL-14` require the year to be consistent with
the policy terms, so the fail-open path can admit an inconsistent year during a
Policy outage; M-31 records the preserved 400 code.

Evidence:

- `repos/eia-policy-domain/.../PolicyMassTortProfileController.java:22-49`
  (public GET/PUT, tenant header, optional DIRECT book guard; the PUT returns
  the body directly, so the public success is always 200) and
  `PolicyMassTortProfileService.java:20-27` (proxy).
- `repos/eia-policy-domain/.../MassTortProfile.java:14-25` (flat public
  projection), `UpdateMassTortProfileCommand.java:16-24` (required fields,
  `trigger` alias, 2000-character notes cap, max-32 status), and
  `PolicyClient.java:373-408` (expert `/internal/v1` calls and projection
  remap).
- `repos/eia-policy-expert/.../MassTortProfileController.java:24-64` (public
  and internal prefixes, tenant resolution, 201/200 upsert) and
  `MassTortProfileService.java:53-99` (tenant wall, 404, upsert, policy version
  bump, outbox write).
- `repos/eia-policy-expert/.../MassTortProfileRules.java:45-164` (tort, trigger,
  allocation, and status vocabularies; notes cap; block order; COMPLETE gate)
  and `MassTortProfileRepository.java:46-82` (tenant-scoped read, insert,
  update).
- `repos/eia-policy-expert/.../PutMassTortProfileRequest.java:14-22`,
  `PolicyMassTortProfile.java:16-28`, `MassTortProfileResult.java:7`, and
  `PolicyEvents.java:47,89-101` (event name and payload).
- `repos/eia-policy-expert/src/main/resources/schema.sql:452-490`
  (`policy_mass_tort_profile` uniqueness, vocabulary, block, and COMPLETE
  constraints and the tenant index).
- Tests: `PolicyMassTortProfileControllerTest`
  (`returnsTheMassTortProfile`, `updatesTheMassTortProfile`,
  `acceptsTheTriggerAliasUsedByThePolicyUi`,
  `rejectsAnyOtherBookBeforeCallingTheExpert`, `validatesTheUpdateBody`),
  `PolicyMassTortProfileClientTest`, `MassTortProfileControllerTest`
  (`createsAProfileWith201`, `updatesAnExistingProfileWith200`,
  `surfacesServiceValidationCodes`), `MassTortProfileRulesTest`, and
  `MassTortProfileServiceTest` (`createsTheProfileAndWritesTheUpdatedEvent`,
  `updatesTheExistingProfileInPlaceAndKeepsADistinctEventVersion`,
  `completeRequiresNotesAndBothCoverageBlockDates`,
  `enforcesTheTenantWallOnReadsAndWrites`).
- `openapi/policy.yaml` 2.6.0, `asyncapi/policy.yaml` 1.4.0, and
  `asyncapi/event-catalog.yaml` 1.12.0 record the implemented shape; and
  `openapi/direct-claims.yaml` 1.9.0 records the allocation guard that consumes
  the profile.
- Direct Claims consumer: `repos/eia-direct-claims-domain/.../ClaimDetailService.java:164-212`
  (`allocate` and `requireMassTortCoverageBlock`), `PolicyMassTortClient.java:40-79`
  (profile read, 404/5xx/transport -> empty, COMPLETE and block test),
  `MassTortYearOutsideBlockException.java`, and
  `ApiExceptionHandler.java:56-61` (400 `MASS_TORT_YEAR_OUTSIDE_BLOCK`). Tests:
  `ClaimDetailServiceTest` (`allocationInsideACompleteMassTortBlockIsCreated`,
  `bothMassTortBlockBoundaryYearsAreCreated`,
  `anAllocationOutsideTheMassTortBlockIsRejectedBeforeCreate`,
  `aDraftMassTortProfileDoesNotRestrictThePolicyYear`,
  `aCompleteMassTortProfileWithoutABlockDoesNotRestrictThePolicyYear`,
  `anEmptyMassTortProfileAllowsTheAllocation`) and
  `ClaimDetailControllerTest.allocationOutsideTheMassTortBlockIsA400`.

Resolution: the narrow profile is canonical for now. Closing the gap means
adding the SPEC `trigger_theory` and status vocabulary, the Appendix E tort
catalog, the remaining profile columns, and the approval and
allocation-percentage steps, propagating the expert's 201 create from the
public domain controller, and either adding the SPEC 11.2.10 path alias or
correcting the SPEC to the short path. Renaming the implemented vocabularies or
the event is breaking and needs an ADR and an EV-05 dual-publish window.

## M-33 Direct Claims list claimant filter is exact-match with no party reference check

The 2026-10-20 Direct Claims contract adds the optional `claimantPartyId` UUID
query parameter to `GET /api/v1/claims` and `GET /internal/v1/claims`. The
running services already implement it: the domain controller accepts the
parameter and forwards it through `ClaimService` and `ClaimClient`; the expert
passes it to `ClaimRepository.findAll` alongside `status`. The two filters are
independent and combine as an AND, and the query is ordered
`created_at DESC, claim_number DESC`.

The filter is an exact equality against the stored `claim.claimant_party_id`.
Neither service calls the Party service, requires the party to belong to the
caller's tenant, or distinguishes an unknown party from a party with no claims:
a well-formed UUID that matches nothing returns an empty array, not a 404, and
a malformed UUID is a 400. SPEC 11.4.10 does not name a claimant filter, so the
parameter is an implementation extension that this contract release makes
canonical. The list remains unpaginated (M-04) and the public path remains the
short M-01 form.

Evidence:

- `repos/eia-direct-claims-domain/.../ClaimController.java:28-35` (public list
  headers, optional `status` and `claimantPartyId` query parameters, DIRECT book
  guard).
- `repos/eia-direct-claims-domain/.../ClaimService.java:31-36` and
  `ClaimClient.java:30-45` (filter forwarding to the expert).
- `repos/eia-direct-claims-expert/.../ClaimController.java:28-35`,
  `ClaimService.java:56-61`, and `ClaimRepository.java:70-94` (exact-match
  predicates for status and claimant, tenant/book scope, newest-first order).
- `openapi/direct-claims.yaml` 1.7.0 records the parameter on both list
  operations and the validator requires it.

Resolution: keep the exact-match filter. If cross-vertical referential checks
become required, resolve the party and hide a foreign or unknown party; that
would turn an empty result into a 404 and needs a contract revision.
Pagination remains M-04.

## M-34 Contract cash calls add a SPEC-less route, lifecycle, and event names

SPEC 11.3.4 names the `ISSUE_CASH_CALL` command and the `cash_call_allowed` and
`cash_call_limit_amount` terms, and SPEC 11.3.11 describes a cash call as an
advance issued before the periodic account when a large loss exceeds the
cash-loss limit and paid through Payment as a `CASH_CALL` linked to the contract
and the claim. SPEC 11.3.9 publishes only `contract.cash-call.issued`, and SPEC
11.3.10 defines no cash-call route. The 2026-10-20 slice implements a
standalone cash-call child aggregate:

| Area | Implemented | SPEC / gap |
|---|---|---|
| Routes | `GET/POST /api/v1/contracts/{contractId}/cash-calls` and `PATCH .../cash-calls/{cashCallId}/status` (the M-01 short form) | SPEC 11.3.10 has no cash-call operation; only the SPEC 11.3.4 command name and the 11.3.11 narrative exist. |
| Projection | Flat `{cashCallId, callNumber, contractId, periodStart, periodEnd, amount, currency, dueDate, status, notes, createdAt}`; the expert row id is remapped to `cashCallId` and `tenantId` is not exposed | No claim link, Payment link, cash-call limit/remaining amount, contract-period relation, or settlement evidence. |
| Status | `REQUESTED`, `ISSUED`, `SETTLED`, `CANCELLED`; only `REQUESTED -> ISSUED -> SETTLED` or `REQUESTED -> CANCELLED` | SPEC names no cash-call status vocabulary. `REQUESTED` as a target is 400 `INVALID_STATUS`; a skipped or repeated edge is 409 `INVALID_STATUS_TRANSITION`. |
| Gate | `periodStart < periodEnd`, `amount > 0`, uppercase ISO 4217 currency, required `dueDate`, notes at most 4000 characters | No `cash_call_allowed` or `cash_call_limit_amount` term check, no large-loss-above-cash-loss-limit authorization, and no contract-window or contract-currency equality check. |
| Events | `contract.cash-call.requested`, `.issued`, `.settled`, `.cancelled` | SPEC 11.3.9 publishes only `.issued`; the other three are new child-aggregate facts (M-22). The envelope uses the cash-call id and aggregate version 1/2/3 while the outbox partition key stays the contract id. |
| Book | Canonical contract requires `X-EIA-Book: ASSUMED`; another book is 404 `BOOK_SCOPE_VIOLATION` | The domain's `requireAssumedBookWhenPresent` accepts an absent header, and the expert's `/internal/v1` alias checks no book at all (M-08). |

Evidence:

- `repos/eia-contract-domain/.../CashCallController.java:29-77` (public routes
  and the book wall) and `CashCallClient.java:32-99` (tenant and ASSUMED
  forwarding to the expert alias).
- `repos/eia-contract-domain/.../CashCall.java:23-36` (`@JsonAlias("id")` remap
  and the flat projection) and `ContractCommandRules.java:242-262` (domain
  create and status validation).
- `repos/eia-contract-expert/.../cashcall/CashCallController.java:50-156`
  (public and internal prefixes, tenant resolution, create and status flow,
  transactional outbox).
- `repos/eia-contract-expert/.../cashcall/CashCallRules.java:29-103` (period
  order, positive amount, currency, due date, notes, status parsing, and the
  transition table), `CashCallStatus.java:11-37` (four statuses and event
  versions), and `CashCallRepository.java:49-118` (newest-first list, unique
  call number, compare-and-set status).
- `repos/eia-contract-expert/src/main/resources/schema.sql:459-481`
  (`contract_cash_call` columns, unique `(tenant_id, contract_id, call_number)`,
  period/amount/currency/status checks).
- `repos/eia-contract-expert/.../ContractEvents.java:67-70,248-318` (event names,
  child-aggregate id/version, contract partition key).
- `openapi/contract.yaml` 3.1.0 and the README cash-call section record the
  implemented shape.

Resolution: the implemented slice is documented as canonical for now. Closing
the gap means adding the cash-call limit/term gate and the large-loss
authorization, enforcing the contract window and currency equality, linking the
call to the claim and the Payment settlement, and adding the SPEC route/status
names or amending SPEC 11.3.10. The three new event names need an EV-05
dual-publish window before a SPEC name is introduced; renaming the route,
statuses, or event names is breaking and needs an ADR and a `/v2` or dual-mount
period.

## M-35 Payment allocations add a SPEC-less POST route and event name

SPEC 11.7.11 lists only `GET
/api/v1/payment/payments/{paymentId}/allocations`; it defines no allocation
create operation. SPEC 11.7.10 publishes no allocation event. The 2026-10-20
slice implements a standalone allocation child aggregate:

| Area | Implemented | SPEC / gap |
|---|---|---|
| Routes | `GET/POST /api/v1/payments/{paymentId}/allocations` (the M-01 short form) | SPEC 11.7.11 lists only the GET, under the longer `/api/v1/payment/payments` base. |
| Projection | `PaymentAllocation` `{allocationId, paymentId, targetType, targetId, component, amount, currency, createdAt}` and `PaymentAllocationSummary` `{items, paymentAmount, totalAllocated, unallocated, currency}`; the expert row id is remapped to `allocationId` and `tenantId` is not exposed | SPEC 11.7.4 defines `claim_id`, `policy_id`, `policy_year`, `contract_id`, `layer_id`, `reserve_component`, `gl_account`, `company_code`, `cost_center`, `profit_center`, `business_area`, `tax_code`, and `allocation_pct`; the flat `targetType`/`targetId`/`component` trio replaces those columns, and the summary envelope is not in SPEC. |
| Command | `CreatePaymentAllocationRequest` with `targetType` DIRECT_CLAIM/ASSUMED_CLAIM/POLICY, `targetId` UUID, `component` INDEMNITY/DEFENSE_COST/ALAE/EXPENSE/COMMISSION/OTHER, and `amount` greater than zero at numeric(19,4); the currency always comes from the payment | The target record is not resolved or validated against the Direct Claims, Assumed Claims, or Policy API; there is no policy-year, layer, contract, reserve-component, allocation-percentage, or SAP GL coding input. |
| Status gate | 409 `PAYMENT_NOT_ALLOCATABLE` when the payment is CANCELLED, REVERSED, or FAILED | The SPEC lifecycle names the allocatable and terminal states but defines no error code. |
| Overallocation | 409 `ALLOCATION_EXCEEDS_PAYMENT` when `totalAllocated + amount` exceeds the payment amount; zero or partial allocations are accepted | SPEC 11.7.7 PAY-06 requires at least one allocation and a total equal to the payment amount within 0.01. The implemented slice does not gate issue on an allocation or require the sum to reach the payment, and the error code is an implementation name. |
| Event | `payment.allocation.created`; envelope aggregate is the allocation id at version 1, the payload carries the parent payment identity, allocation fields, and `totalAllocated`/`paymentAmount` | SPEC 11.7.10 publishes no allocation event, so the name is new (M-22). The outbox partition key stays the payment id. |
| Book | Not book-scoped; `payment_allocation` has no book column and the routes require only `X-EIA-Tenant`; the event is stamped DIRECT | SPEC 3.6.1 says every payment and allocation carries the book. The implemented payment and allocation rows carry no book (M-08, M-12). |

Evidence:

- `repos/eia-payment-domain/.../PaymentController.java:73-85` (public GET/POST
  allocation routes) and `PaymentService.java:122-139` (proxy and command
  normalization).
- `repos/eia-payment-domain/.../PaymentAllocationRules.java:29-102` (target,
  component, and amount validation), `PaymentAllocation.java:20-29`,
  `PaymentAllocationSummary.java:17-23`, and
  `CreatePaymentAllocationCommand.java:11-16` (flat public projection).
- `repos/eia-payment-domain/.../PaymentClient.java:121-168` (expert
  `/internal/v1` calls, missing-total normalization, and upstream-error
  translation).
- `repos/eia-payment-expert/.../PaymentAllocationController.java:26-62` (same
  public path plus the internal alias, tenant resolution, 201 create) and
  `PaymentAllocationService.java:38-87` (tenant wall, status gate,
  overallocation guard, allocation insert, and outbox write in one
  transaction).
- `repos/eia-payment-expert/.../PaymentAllocationRules.java:22-114` (closed
  target and component sets, amount normalization, non-allocatable statuses),
  `PaymentAllocationRepository.java:46-93` (oldest-first list and allocated
  total), `PaymentAllocationItem.java:15-35`, and
  `PaymentAllocationSummary.java:13-20` (public field names).
- `repos/eia-payment-expert/.../PaymentEvents.java:37,101-136`
  (`payment.allocation.created`, `PaymentAllocation` aggregate at version 1,
  parent payment partition key) and `schema.sql:44-68` (`payment_allocation`
  columns and the positive-amount, target-type, and component checks).
- Tests: `PaymentAllocationControllerTest` (list totals, create, internal
  alias, `TENANT_REQUIRED`, `VALIDATION_ERROR`, both 409 codes, 404),
  `PaymentAllocationIntegrationTest` (oldest-first ordering, empty summary,
  over-allocation and status guards, tenant wall, field validation, event
  payload, rollback), and `PaymentAllocationRulesTest`.
- `openapi/payment.yaml` 1.4.0, `asyncapi/payment.yaml` 1.3.0,
  `asyncapi/event-catalog.yaml` 1.14.0, and the README payment allocation
  section record the implemented shape.

Resolution: the implemented slice is documented as canonical for now. Closing
the gap means adding the SPEC allocation create operation and the
`payment.allocation.created` event name (or recording the GET-only contract),
enforcing PAY-06 (at least one allocation per payment and the exact
payment-amount sum within 0.01), resolving and validating the target against
the owning claim or policy API, adding the policy-year, layer, contract,
reserve-component, allocation-percentage, and SAP GL coding fields, and
carrying the book on the payment and allocation. A new event name needs an
EV-05 dual-publish window before it can replace a SPEC name; renaming the route
or event is breaking and needs an ADR and a `/v2` or dual-mount period. A
`paymentId` outside the caller's tenant stays 404 `PAYMENT_NOT_FOUND`.

## M-36 Direct Claims allocation erosion retry swallows the expert conflict and record failure

The 2026-10-20 contract adds the optional allocation `limitId`, the
`NOT_POSTED`/`POSTED`/`FAILED` erosion state, and the public
`POST /api/v1/claims/{claimId}/allocations/{allocationId}/erosion`
orchestration retry. The contract now matches the implemented public shape: the
retry has **no request body**, loads the tenant-scoped allocation, requires its
stored `limitId`, reposts the limit to the Policy domain, and records the
computed `POSTED` or `FAILED` outcome through the expert. The create with
`limitId`, the missing-limit 400, the 404 scope, and the "Policy failure becomes
`FAILED` with 200" behaviour also match. The remaining difference is the
terminal-conflict and record-failure handling:

| Area | Canonical contract | Implementation |
|---|---|---|
| Public command | Bodyless orchestration retry; no request body and no public `AllocationErosionRequest` schema | `ClaimDetailController.retryAllocationErosion` takes no body and calls `ClaimDetailService.retryErosion`, which reads the allocation, requires a non-null `limitId`, posts the limit to Policy, and records the computed `POSTED` or `FAILED` |
| Policy posting | A Policy rejection or an unavailable Policy service is recorded as `FAILED` and returned with 200, not a 5xx | `PolicyErosionClient.postErosion` calls `POST /api/v1/policies/{policyId}/erosion` with the allocation id as `Idempotency-Key` and the allocation amount as `reservedAmount`; its result becomes `POSTED` or `FAILED`, and the failure message is stored on the allocation |
| Missing limit | 400 `VALIDATION_ERROR` | `ClaimDetailService.retryErosion` throws `DomainValidationException` (`limitId is required to retry erosion for allocation ...`), mapped to 400 `VALIDATION_ERROR` |
| 404 | Unknown claim or allocation, foreign tenant, missing/non-DIRECT book | `ClaimDetailService.findAllocation` reads the tenant-scoped list and maps an absent id to `AllocationNotFoundException` (404 `NOT_FOUND`); the controller enforces the DIRECT book wall |
| 409 | A retry that would record a different state after `POSTED` is 409 `CONFLICT`; the posted state is terminal | The expert `ClaimAllocationService.updateErosion` throws `ClaimConflictException` (409 `CONFLICT`) for a different status after `POSTED`, but `ClaimDetailService.postErosion` catches the resulting `RestClientException` from `updateAllocationErosion`, logs it, and returns the **pre-update** allocation. The public caller therefore sees 200, never the documented 409 |
| Record failure | The 200 body is the allocation with the newly recorded state | The same catch also swallows a transport/5xx failure of the expert record call: a successful Policy posting whose state write failed is returned as `NOT_POSTED` or `FAILED`, not as the recorded state, with 200 |
| Same-state retry | A retry that computes the same `POSTED` state is an idempotent 200 no-op | The expert returns the stored allocation and instant; the public path returns 200 with the stored state, matching |

Evidence:

- `repos/eia-direct-claims-domain/.../ClaimDetailController.java:159-172`
  (public POST with no request body), `ClaimDetailService.java:159-250`
  (`allocate`, `retryErosion`, `postErosion`, `findAllocation`), and
  `PolicyErosionClient.java:55-142` (Policy call, idempotency key, and message
  extraction).
- `repos/eia-direct-claims-domain/.../ClaimCommands.java:71-86` and
  `ClaimDetailDtos.java:109-146` (optional `limitId` and erosion projection),
  `ClaimClient.java:225-255` (create and expert PATCH forwarding), and
  `ApiExceptionHandler.java:39-42,51-53,81-102` (404, 400, and 409 mappings).
- `repos/eia-direct-claims-expert/.../ClaimAllocationController.java:61-69`
  (`PATCH .../erosion` on both prefixes), `AllocationErosionRequest.java:10-15`
  (`@NotBlank status`, optional `message`; expert-only), `ClaimAllocation.java:18-38`
  (projection), and `ClaimAllocationService.java:115-162` (normalization,
  4000-character message cap, same-status no-op, terminal `POSTED` conflict).
- `repos/eia-direct-claims-expert/.../ApiExceptionHandler.java:78-101` (409
  `CONFLICT` for `ClaimConflictException`, 400 `VALIDATION_ERROR`, and the two
  allocation create codes).
- Tests: `ClaimAllocationControllerTest` (POSTED and FAILED bodies, the
  internal alias, repeated status, 409, missing status), `ClaimAllocationServiceTest`
  (`marksAnAllocationErosionPosted`, `recordsAFailedErosion...`,
  `repeatingTheCurrentErosionStatusIsA200NoOp`, terminal-conflict cases),
  `ClaimAllocationIntegrationTest` (projection, posting instant, retry,
  tenant and claim walls), `ClaimDetailControllerTest.retriesAllocationErosion`
  (200 only), and `PolicyErosionClientTest`.
- `openapi/direct-claims.yaml` 1.8.0 and the README allocation-erosion section
  record the canonical shape.

Why the contract keeps its shape: the retry's job is to record the Policy
outcome, so returning the pre-update state after a failed expert write hides
whether the allocation was posted; and a terminal `POSTED` allocation that
would be re-marked `FAILED` is a real conflict a client must see. A future fix
maps the expert 409 to a public 409 `CONFLICT` and stops swallowing the expert
record failure (or returns it as a 5xx), while keeping the missing-limit 400 and
the Policy-failure-as-`FAILED` 200. Until then the contract is canonical and
this entry records the difference.

Resolution: surface the expert conflict as 409 `CONFLICT` and the record-write
failure as an error instead of returning the pre-update allocation with 200, or
amend this contract and SPEC 11.4.10 to the 200/stale-state behaviour. Preserve
the two expert create codes as M-31 requires. Renaming the route or the
`CONFLICT` code is breaking for a generated client and needs an ADR.

## M-37 Contract security/collateral projection and status vocabulary

The public security/collateral slice is implemented on the Contract domain and
expert and is documented as canonical. The public status action in
`openapi/contract.yaml` 4.1.0 releases or expires a record and writes
`contract.security.status-changed`; the remaining differences from SPEC 11.3.4
and 11.3.10 are:

| Area | Implemented | SPEC / gap |
|---|---|---|
| Routes | `GET/POST /api/v1/contracts/{contractId}/security` and `PATCH /api/v1/contracts/{contractId}/security/{securityId}/status` (the M-01 short form) on both the domain and expert, plus the wide internal `/internal/v1/contracts/{contractId}/security` surface | SPEC 11.3.10 uses `/api/v1/contract/contracts/{contractId}/security` and lists an internal `POST /security/{securityId}/release` command instead of a public status action. |
| Projection | `SecurityRecord` with exactly `id`, `securityType`, `requiredAmount`, `heldAmount`, `currency`, `providerPartyId`, `expiryDate`, `approvalRef`, `status`, `createdAt`; `tenantId`, `contractId`, `beneficiaryPartyId`, effective dates, `collateralQuality`, `documentId`, `releaseConditions`, and the audit columns stay internal | SPEC 11.3.4 `contract_security` defines the tenant, contract, beneficiary, effective dates, collateral quality, document, and release-condition columns; the broad `Security` row remains only on the internal expert surface. |
| Status | The public create derives `EXPIRED` when `expiryDate` is past and `ACTIVE` otherwise; `status` is not a create input. The public status action accepts only `RELEASED` and `EXPIRED`, so the working states are never requestable and `BREACH` is never a target. The public response enum still carries `REQUIRED`, `OUTSTANDING`, `PARTIAL`, `RELEASED`, and `BREACH` because the list returns internal-expert and legacy rows | SPEC 11.3.4 enumerates `REQUIRED`, `OUTSTANDING`, `PARTIAL`, `RELEASED`, `EXPIRED`, and `BREACH` and has no `ACTIVE`. `OUTSTANDING` exists in the implemented internal lifecycle, the database check, and `SecurityRules`; the public create never derives it, but the public list can return it. The SPEC release command has no equivalent status-action vocabulary. |
| Command | `CreateContractSecurityRequest` accepts `securityType`, `requiredAmount`, optional `heldAmount` (default `0.0000`), `currency` (must equal the contract currency), optional `providerPartyId`, `expiryDate`, `approvalRef`, and `approvedAt`; a separate `UpdateContractSecurityStatusRequest` accepts only `{status}` with `RELEASED` or `EXPIRED` | SPEC 11.3.4 also models beneficiary, effective from/to, collateral quality, document, release conditions, and status; the public commands have no field for them. Held collateral above the obligation requires both an approval reference and an approved timestamp, and the create requires the contract to be `DRAFT`, `QUOTED`, `PLACED`, or `BOUND`. |
| Book | The canonical contract requires `X-EIA-Book: ASSUMED`; another book is 404 `BOOK_SCOPE_VIOLATION` | The domain accepts an absent header for compatibility with the other Contract proxy routes, the same difference recorded for the technical-account, bordereau, and cash-call slices (M-29, M-30, M-34). |
| Event | `contract.security.recorded` and `contract.security.status-changed` are implemented; both are child aggregates keyed by the security id (version 1 for the record, 2 for the first status change, 3 for the release of an expired record) while the outbox partition key stays the contract id. The recorded payload is `{contractId, securityId, securityType, requiredAmount, heldAmount, currency, status}`; the status payload is `{contractId, securityId, securityType, previousStatus, status}` | SPEC 11.3.9 names `contract.security.recorded`, so that name matches, and its payload omits the contract number, provider, approval reference, expiry date, and the wide row fields. SPEC publishes no security status-change fact, so `contract.security.status-changed` is a new child name (M-22). `contract.security.breached` remains planned and is never emitted. |

Consequences:

- A caller can release or expire a record and can release an expired record,
  but cannot mark `OUTSTANDING`/`PARTIAL`, reopen an expired record, or request
  `BREACH` through the public API; `BREACH` is written by the collateral checks
  and is deliberately not a public target. There is still no public
  single-record GET, and the only public writes are the create and the status
  action.
- A generated client must tolerate the full seven-value response status enum,
  including `OUTSTANDING`, even though the public create only derives `ACTIVE`
  or `EXPIRED` and the status action only returns `RELEASED` or `EXPIRED`. The
  list is unfiltered by status and reveals internal-expert rows for the same
  contract by design.
- The recorded event payload cannot drive a UI row without an extra read: it
  carries the identity, type, amounts, currency, and derived status but not the
  provider, expiry, or approval evidence. The status event is smaller still and
  is intended for cache invalidation and audit, not for rendering the row.

Evidence:

- `repos/eia-contract-domain/.../SecurityController.java:27,38-73` (public
  routes, tenant header, optional ASSUMED book wall, status action) and
  `SecurityService.java:23-29`, `SecurityClient.java:33-40,53-109` (expert
  forwarding, expert-public status path, and 400/404/409 translation).
- `repos/eia-contract-domain/.../SecurityRecord.java:23-34` (ten-field public
  projection), `CreateSecurityCommand.java:18-34`, and
  `UpdateSecurityStatusCommand.java:13` (domain command shapes).
- `repos/eia-contract-expert/.../security/ContractSecurityController.java:44,66-93,98-125`
  (public list, create, and status action, tenant resolution, 201) and
  `ContractSecurityRules.java:27-68,82-129` (closed type, positive required
  amount, default held, contract-currency reconciliation, derived status,
  approval reference, target parsing, and the transition matrix).
- `repos/eia-contract-expert/.../security/ContractSecurityView.java:18-43`
  (public field cut), `CreateContractSecurityRequest.java:16-25` (eight request
  fields), and `UpdateContractSecurityStatusRequest.java:10` (the `{status}`
  action payload).
- `repos/eia-contract-expert/.../security/SecurityController.java:29,43-62`
  (internal wide surface) and `SecurityRules.java:19-27,32-84,90-99` (full
  status/quality vocabulary, over-collateralisation approval, breach gate).
- `repos/eia-contract-expert/.../ContractEvents.java:74-77,283-351`
  (`contract.security.recorded` at version 1 and
  `contract.security.status-changed` at version 2 or 3, the `Security`
  aggregate, the contract partition key, and the five- and seven-field data)
  and `ContractGuard.java:15-37` (`CONTRACT_LOCKED` for a non-editable create;
  the status action deliberately does not require an editable contract).
- `repos/eia-contract-expert/src/main/resources/schema.sql:165-218`
  (`contract_security` columns, the full status check including `ACTIVE` and
  `OUTSTANDING`, and the public-create defaults).
- Tests: `ContractSecurityControllerTest` (newest-first ten-field list,
  derived `ACTIVE`/`EXPIRED`, invalid type/amount/currency/approval reference,
  tenant wall, tenant mismatch, `CONTRACT_LOCKED`, the release and expire
  transitions, `RELEASED` terminality, `BREACH` rejection, invalid and missing
  target, 404, and concurrent 409),
  `ContractSecurityOutboxIntegrationTest` (row and status event in one
  transaction, rollback, tenant wall, field payload), and the domain
  `SecurityControllerTest` and `SecurityClientTest` (book wall, tenant, status
  forwarding, error preservation, `OUTSTANDING` pass-through).
- `openapi/contract.yaml` 4.1.0, `asyncapi/contract.yaml` 1.6.0,
  `asyncapi/event-catalog.yaml` 1.19.0, and the README security sections record
  the implemented shape.

Resolution: the narrow public projection, derived create status, and the
release/expire action are canonical for now. The action closes the
release/expire half of the gap but not the SPEC `POST .../release` spelling or
the working-state vocabulary. Closing the rest means adding the single-record
read and the missing SPEC columns to the public projection, or amending SPEC
11.3.4/11.3.10 to the derived-status public slice and the status action.
`ACTIVE` is outside the SPEC status enum, so either the SPEC must add it or the
public statuses must be renamed. `contract.security.recorded` already exists in
SPEC 11.3.9, so no dual-publish window is needed for that event;
`contract.security.status-changed` is a new name and is additive, but promoting
it into SPEC 11.3.9 would need the usual event-name review.

## M-38 Policy installment dunning is a SPEC-less per-installment route, vocabulary, and event

SPEC 11.2.13 models dunning on the billing account: `billing_account.dunning_level`
is an integer fed from SAP, `dunning_status` is one of `CLEAR`, `REMINDER`,
`DUNNING`, `LEGAL`, `BLOCKED`, the collections flow is
`CURRENT -> REMINDER -> DUNNING_1 -> DUNNING_2 -> NOTICE -> CANCELLATION_PENDING -> CANCELLED`,
and the only dunning command is the internal
`POST /internal/v1/policies/{id}/dunning-status`. The 2026-10-20 slice records
and lists dunning actions against an installment:

| Aspect | Implemented | SPEC 11.2.13 |
|---|---|---|
| Route | `GET/POST /api/v1/billing/installments/{installmentId}/dunning` (short public path, outside `/api/v1/policies`) | No public dunning route; internal `POST /internal/v1/policies/{id}/dunning-status` |
| Subject | One premium installment resolved through its plan and policy | `billing_account` (policy, legal entity, company code, currency) |
| Levels | `REMINDER`, `FIRST_NOTICE`, `SECOND_NOTICE`, `COLLECTIONS` (closed) | Integer SAP level plus `dunning_status` `CLEAR`, `REMINDER`, `DUNNING`, `LEGAL`, `BLOCKED` |
| Channels | `EMAIL`, `LETTER`, `PORTAL` (closed) | No channel column or API field |
| Status | `SENT`, `CANCELLED` | `dunning_status` is the SAP-sourced collection state, not an action state |
| Projection | `{dunningId, installmentId, planId, policyId, level, channel, notes, status, sentAt}` | `dunning_status` row: policy, level, status, amount, currency, next action, SAP run |
| Event | `policy.dunning.sent` | `policy.billing.dunning-changed` |
| Book | Canonical contract requires `X-EIA-Book: DIRECT`; the domain accepts an absent header | The SPEC 3.6 book wall |
| Idempotency | No `Idempotency-Key`/`If-Match`; the unique `(tenant, installment, level)` row is the retry guard | SPEC 12.6 |

Consequences:

- Dunning is per installment rather than per billing account, and there is no
  `nextAction`, promise-to-pay, dispute hold, agency referral, write-off, or
  cancellation trigger. The SPEC dunning workbench fields and the COL-01..COL-05
  controls are not modelled.
- The level vocabulary is not SAP's and does not map to the SPEC `dunning_status`
  enum; a consumer must translate `REMINDER`/`FIRST_NOTICE`/`SECOND_NOTICE`/
  `COLLECTIONS` itself. No SAP sync job writes these rows.
- One action per level per installment is allowed, including after a CANCELLED
  history row, so the action history cannot express a re-sent level.
- A missing `X-EIA-Book` is accepted by the domain even though the canonical
  contract requires DIRECT and the SPEC 3.6 wall expects it; another book is
  still hidden as 404 `BOOK_SCOPE_VIOLATION`.
- The event payload carries the policy identity, the dunned installment, level,
  channel, sent instant, and status but not the amount, currency, due date,
  notes, or SAP run, so it cannot drive a collections row without a follow-up
  read.

Evidence:

- `repos/eia-policy-domain/.../DunningController.java` (`@RequestMapping` on the
  public path, `@GetMapping` history, `@PostMapping` 201, tenant header,
  `requireDirectWhenPresent`), `DunningService.java`, `DunningAction.java`
  (`dunningId` projection), and `CreateDunningActionCommand.java` (level/channel
  `@NotBlank`, notes `@Size(max = 2000)`).
- `repos/eia-policy-domain/.../PolicyClient.java:511-564` (`/internal/v1` calls,
  `ExpertDunningAction` alias of `id` to `dunningId`) and
  `PolicyClient.java:886-903` (`lastDunningLevel`/`lastDunningAt` remap).
- `repos/eia-policy-expert/.../BillingDunningController.java:25-60` (public and
  internal aliases, 201, list), `BillingDunningService.java:58-106` (tenant
  target, effective-status gate, duplicate level, policy touch, outbox insert),
  `BillingDunningRules.java:16-85` (level/channel/status vocabularies,
  2000-character notes, dunnable states), `BillingDunningRepository.java:62-109`
  (tenant-safe target join, newest-first history, unique level), and
  `CreateDunningActionRequest.java`.
- `repos/eia-policy-expert/.../PolicyEvents.java:47,106-122` (`DUNNING_SENT` and
  the seven-field `dunningSent` payload) and
  `src/main/resources/schema.sql:453-480` (`billing_dunning_action`, the unique
  level constraint, the level/channel/status checks, and the two indexes).
- `repos/eia-policy-expert/.../BillingRepository.java:150-183` (latest-SENT
  dunning subqueries on the receivables queue).
- Tests: `DunningControllerTest`, `DunningServiceTest`,
  `PolicyDunningClientTest`, `BillingDunningControllerTest`,
  `BillingDunningServiceTest`, and `BillingDunningRulesTest`.
- `openapi/policy.yaml` 2.7.0, `asyncapi/policy.yaml` 1.5.0, and
  `asyncapi/event-catalog.yaml` 1.16.0 record the implemented shape.

Resolution: the per-installment action history is canonical for now. Closing
the gap means adding the SPEC billing-account dunning level/status and
next-action fields, the `POST .../dunning-status` command, and the
COL-01..COL-05 controls, or amending SPEC 11.2.13 to the per-installment route
and vocabulary. Renaming `policy.dunning.sent` to
`policy.billing.dunning-changed` requires the EV-05 dual-publish window;
publishing the SPEC name alongside the implemented one is additive.

## M-39 Policy program catalog is a short-path, SPEC-less create and membership surface

The Policy expert and domain implement a commercial program catalog plus a
policy-to-program membership command. SPEC 10.11.3 defines the `program`
master-data table and SPEC 11.2.10 lists two read APIs; the implemented surface
is wider and uses a different path, vocabulary, and projection.

| Aspect | Canonical contract / implemented | SPEC 10.11.3 and 11.2.10 |
|---|---|---|
| Paths | `GET/POST /api/v1/programs`, `GET /api/v1/programs/{programId}`, `PATCH /api/v1/policies/{policyId}/program` | `GET /api/v1/policy/programs`, `GET /api/v1/policy/programs/{programId}`; no create and no membership command |
| Identity | `programId` UUID; per-tenant `programNumber` `PRG-{YEAR}-{7 digits}` from `policy_program_number_seq` | `id` and an immutable `code` varchar(16) |
| Name | `name` varchar(200) | `name` varchar(200) plus optional `description` |
| Types | `CAPTIVE`, `POOL`, `FRONTING`, `COINSURANCE`, `MASS_TORT` | `CASUALTY`, `PROPERTY`, `COMMERCIAL`, `AUTO`, `SPECIALTY`, `OTHER` |
| Status | `ACTIVE`, `CLOSED` (CLOSED is reserved; no close command exists) | `ACTIVE`, `INACTIVE` |
| Dates | inclusive `effectiveFrom`/`effectiveTo`, both required and NOT NULL; the same day is valid | both nullable |
| Owner and manager | not modelled | `owner_legal_entity_id`, `manager_org_unit_id`, `program_org_unit`, `program_legal_entity`, `program_lob` |
| Capacity | not modelled | `program_version`, `program_capacity`, and the LE-02 capacity-share rules |
| Membership | one nullable `policy.program_id`; PATCH assignment command; returns the policy ETag | `policy.program_id` and the `POLICY_IN_PROGRAM` link; LE-01 requires one program per policy |
| Lead policy | optional `leadPolicyId` stored as supplied, with no FK or tenant check | no lead-policy concept on `program` |
| Events | `policy.program.created` (Program aggregate, version 1) and `policy.policy.program-assigned` (Policy aggregate, version + 1) | no program event in SPEC 11.2.9 |
| Book | The canonical contract requires `X-EIA-Book: DIRECT`; the domain and expert accept an absent header | SPEC 3.6 book wall |

Consequences:

- A consumer cannot map the implemented program types to the SPEC 10.11.3
  catalog without a translation table; the types describe legal structures
  (captive, pool, fronting, coinsurance, mass tort) while the SPEC catalog
  describes business classes. The same applies to CLOSED versus INACTIVE.
- The projection has no `code`, `description`, owner legal entity, manager
  organization unit, LOB/legal-entity assignments, `program_version`, or
  capacity structure, so the LE-02 share-sum check, LE-06 versioning, and the
  program detail/capacity/fronting views cannot be served from it.
- `CLOSED` is accepted by the database CHECK constraint and the status enum but
  no command can reach it; every created program stays ACTIVE.
- `leadPolicyId` is written without a foreign key, existence check, or tenant
  check, so a caller can store a dangling policy id or another tenant's policy
  id. The program projection returns it unchanged.
- The `PATCH` body is required by the canonical contract, but the public domain
  also treats an absent body as a clear; a caller that omits the body silently
  clears the membership instead of receiving a 400.
- The create and assignment commands accept neither `Idempotency-Key` nor
  `If-Match`; a retried create produces a second program, and a retried
  assignment emits a second event and bumps the policy version again.
- A missing `X-EIA-Book` is accepted by both the domain and the expert even
  though the canonical contract requires DIRECT; another book is still hidden
  as 404 `BOOK_SCOPE_VIOLATION` by the domain.

Evidence:

- `repos/eia-policy-domain/.../ProgramController.java:25-65` (public
  `/api/v1/programs`, tenant header, `requireDirectWhenPresent`, 201 and
  `Location`), `ProgramService.java:31-43` (date-range pre-check),
  `ProgramDto.java`, and `CreateProgramCommand.java` (name and type
  constraints).
- `repos/eia-policy-domain/.../PolicyProgramController.java:21-47` (public
  PATCH, optional body, ETag echo) and `PolicyProgramService.java`,
  `UpdatePolicyProgramCommand.java`.
- `repos/eia-policy-domain/.../PolicyClient.java:418-494` (`/internal/v1`
  program calls and projection remap).
- `repos/eia-policy-expert/.../PolicyProgramController.java:29-85` (public and
  internal aliases, tenant query or header, 201 create, 200 assignment with
  ETag), `PolicyProgramService.java:54-112` (number generation, ACTIVE default,
  null clear, version check and 409), and `ProgramRules.java:17-95`
  (vocabulary, name cap, date order).
- `repos/eia-policy-expert/.../PolicyProgramRepository.java:45-84`
  (tenant-scoped reads, newest-first list, number sequence) and
  `PolicyProgram.java`, `ProgramView.java`, `CreateProgramRequest.java`,
  `AssignPolicyProgramRequest.java`.
- `repos/eia-policy-expert/.../PolicyEvents.java:50-51,94-153`
  (`policy.program.created` against Program at version 1 and
  `policy.policy.program-assigned` against Policy with both link sides) and
  `src/main/resources/schema.sql:52-85` (`policy_program`, its CHECK
  constraints, the nullable `policy.program_id` FK, and the indexes; no FK on
  `lead_policy_id`).
- Tests: `ProgramControllerTest`, `PolicyProgramControllerTest`,
  `ProgramClientTest`, `PolicyProgramControllerTest`,
  `PolicyProgramServiceTest`, `PolicyProgramIntegrationTest`, and
  `ProgramRulesTest`.
- `openapi/policy.yaml` 2.8.0, `asyncapi/policy.yaml` 1.6.0, and
  `asyncapi/event-catalog.yaml` 1.17.0 record the implemented shape.

Resolution: either extend SPEC 10.11.3/11.2.10 with the implemented catalog,
membership command, and event names, or align the implemented paths,
vocabulary, and projection with the SPEC master data. Until then the contract
documents the short paths and the CAPTIVE/POOL/FRONTING/COINSURANCE/MASS_TORT
vocabulary. Separately, either resolve and tenant-check `leadPolicyId` or
remove it, add an explicit close command before exposing CLOSED as a reachable
state, and decide whether the DIRECT book header is required or optional.

## M-40 Document content keeps a current pointer plus revisions, not the SPEC versioned store

SPEC 11.6.10 defines an authorized content download (presigned) and mounts the
content history at `GET /versions` and the version-creating command at `POST
/versions`; the SPEC 11.6 model carries content, versions, hashes, page counts,
OCR status, holds, and retention. The implemented slice stores one current
content pointer per document plus immutable revision rows, serves the bytes
through a raw-byte proxy under `/content`, exposes the history under
`/content/versions`, and emits a content-upload fact that has no SPEC 11.6.9
name.

| Aspect | Implemented | SPEC 11.6.10 / 11.6 |
|---|---|---|
| Routes | `PUT|GET /api/v1/documents/{documentId}/content`, `GET .../content/metadata`, `GET .../content/versions`, and `GET .../content/versions/{version}` | authorized content download (presigned), `GET`/`POST .../versions`, preview, text, access log |
| Upload | raw bytes; each accepted body appends an immutable revision and advances the current pointer | versioned content with a history |
| Size limit | 10 MiB (10,485,760 bytes); a zero-byte body is 400 `EMPTY_CONTENT`; an over-limit body is 413 `FILE_TOO_LARGE` | no implemented limit stated |
| Metadata | `DocumentContent` with `documentId`, `fileName`, `contentType`, `sizeBytes`, `sha256`, `uploadedAt`, `currentVersion` | content, hash, page count, OCR status, tags, versions |
| Download | proxied bytes with `Content-Type`, `Content-Disposition`, `X-Content-SHA256`, and `X-Content-Version`; one revision is downloadable through `/content/versions/{version}`; no `Range`, no presigned URL | short-lived presigned URL |
| Filename | URL-encoded `X-File-Name`, reduced to its last path component; at most 255 characters | not specified |
| Versioning | append-only `document_content_version` rows; revisions start at 1 and the history is newest first; every upload appends one revision and advances `current_version`; no deletion, retention, or lineage | superseded/version rows at `/versions` |
| Concurrency | a per-document pointer lock allocates the next revision, so concurrent uploads both retain their bytes; the last committed upload wins the current pointer without `If-Match` or `Idempotency-Key` | not specified |
| Book | none; tenant-scoped only | SPEC 3.6 book wall |
| Event | `document.content.uploaded` (new; no SPEC 11.6.9 name); payload `version` is the revision and the aggregate version, `eventVersion` 1 | no content-upload fact |
| Missing tenant | 404 `NOT_FOUND` on the expert; 400 `TENANT_REQUIRED` on the public domain route | canonical 400 Problem |

Consequences:

- A consumer can now list and download prior revisions and read the current
  revision number, but still cannot retrieve a preview rendition, OCR text, a
  page count, tags, an access log, a legal hold, or a retention disposition.
- The history is implemented at `/content/versions`, not the SPEC `/versions`
  route, and the version-creating command is the content upload rather than
  `POST /versions`. A client generated from SPEC 11.6.10 must be adapted to the
  nested path.
- The public download proxies the bytes instead of issuing a short-lived
  presigned URL, so the Document domain remains a data-path hop and the
  response has no `Range` support. A caller that expected a redirect or a
  presigned target must instead consume a binary body.
- Revision allocation is serialized per document, but the current pointer has
  no optimistic concurrency token: two concurrent uploads both retain a
  revision and the last writer wins the current read. No `If-Match` or
  `Idempotency-Key` is accepted.
- The public 413 is `application/problem+json` `FILE_TOO_LARGE` and an unknown
  revision is 404 `CONTENT_VERSION_NOT_FOUND`, but the missing-tenant 400 is
  still the compact `TENANT_REQUIRED` `ApiError` rather than the canonical
  Problem (M-02).
- The event name is new and has no SPEC 11.6.9 equivalent, so a subscriber
  cannot rely on a SPEC-defined content fact. The added payload `version` is
  additive under EV-05 and keeps `eventVersion` 1; no event name is added
  (M-22).
- The SPEC 11.6.9 names (`document.document.registered`, `.classified`,
  `.superseded`, `.generated`, `.signed`, `.held`, `.hold-released`,
  `.archived`, `.disposed`, `.requested`, `.request-fulfilled`,
  `document.package.built`, and the two processing facts) remain planned.

Evidence:

- `repos/eia-document-domain/.../DocumentController.java:61-132` (public
  upload, current download, metadata, version list, and version download;
  `X-EIA-Tenant` required), the `DocumentContentMetadata`,
  `DocumentContentVersion`, `DocumentContentDownload`, `DocumentContentPolicy`,
  `DocumentContentSizeLimitFilter`, and `DocumentContentTooLargeException`
  helpers, and `DocumentExpertClient.java:163-230` (expert calls and header
  pass-through).
- `repos/eia-document-expert/.../DocumentContentController.java:43-106` (raw
  upload, current download, metadata, newest-first version list, and revision
  download), `DocumentContentService.java:39-101` (tenant document lookup,
  revision append, pointer refresh, outbox, version reads),
  `DocumentContentRepository.java:97-193` (revision allocation, pointer update,
  newest-first list, revision read), `DocumentContentRules.java:27-157`
  (10 MiB, filename, MIME, SHA-256 rules), `DocumentContentEvents.java:35-68`
  (`document.content.uploaded` with `version`), `DocumentContentVersion.java`,
  `DocumentContentVersionMetadata.java`, `ContentVersionNotFoundException.java`,
  `ApiExceptionHandler.java:35-39` (`CONTENT_VERSION_NOT_FOUND`),
  `TenantResolver.java:28-41` (content routes hide a missing tenant as 404),
  and `DocumentContentRules`/`DocumentContentMetadata`/`DocumentContent.java`.
- `repos/eia-document-expert/src/main/resources/schema.sql:48-110`
  (`document_content` current pointer, `document_content_version` revision
  table with `UNIQUE (document_id, version)` and the newest-first index, and the
  version-1 backfill).
- Tests: `DocumentContentApiTest`, `DocumentContentVersionApiTest`,
  `DocumentContentClientTest`, `DocumentContentVersionClientTest`,
  `DocumentContentIntegrationTest`, and `DocumentContentRulesTest`.
- `openapi/document.yaml` 1.4.0, `asyncapi/document.yaml` 1.4.0, and
  `asyncapi/event-catalog.yaml` 1.21.0 record the implemented shape.

Resolution: either align the implementation with SPEC 11.6.10 (move the
history to `/versions`, add the `POST /versions` command, presigned download,
renditions, OCR text, book scope, and the SPEC lifecycle/content facts) or
amend SPEC 11.6.9 and 11.6.10 to the current-pointer plus revision proxy, the
`/content/versions` path, the upload-as-version-command, and the new
`document.content.uploaded` payload. The contract documents the implemented
shape until that decision.

## M-41 Policy credit notes use a short path, a four-state lifecycle, and new event names

SPEC 11.2.13 defines the `credit_note_request` row, mounts the request at
`POST /api/v1/policy/policies/{policyId}/credit-notes`, routes the request
through a human approval step and the Payment SAP subtransaction, and publishes
`policy.billing.credit-note-issued`. The implemented slice is a narrower
tenant-scoped child resource with its own lifecycle, free-text reason, and three
new event names.

| Aspect | Implemented | SPEC 11.2.13 |
|---|---|---|
| Paths | `GET/POST /api/v1/policies/{policyId}/credit-notes` and `PATCH .../{creditNoteId}/status` | `POST /api/v1/policy/policies/{policyId}/credit-notes`; no public list or status action row |
| Identity | `creditNoteId` UUID; server-generated `noteNumber` `CN-{7 digits}` | `id`; optional `original_invoice_number` and `sap_credit_memo_number` |
| Status | `DRAFT`, `ISSUED`, `APPLIED`, `CANCELLED` | `REQUESTED`, `APPROVED`, `SENT_TO_SAP`, `ISSUED`, `REJECTED` |
| Transitions | DRAFT -> ISSUED -> APPLIED; CANCELLED from DRAFT or ISSUED; APPLIED and CANCELLED terminal | Request, approve, send to SAP, persist the SAP reference, issue, reject |
| Reason | free text, trimmed, optional, at most 500 characters | closed enum `CANCELLATION`, `ENDORSEMENT`, `AUDIT_RETURN`, `OVERPAYMENT`, `REFUND`, `CORRECTION` |
| Money | positive `amount` plus `currency`, which must equal the policy premium currency | `amount`, optional `tax_amount`, and `currency` |
| Approval | none | `policy.credit-note.approve` human approval with `approved_by` |
| SAP | no credit-memo number, no `payment.finance.credit-note` call, and no Payment link | SAP credit-memo request and persisted reference |
| Original invoice | not modelled | optional `original_invoice_number` |
| Projection | flat ten fields; `tenantId` is not exposed | the full request row including tax, approval, and SAP columns |
| Events | `policy.credit-note.issued`, `.applied`, `.cancelled` | only `policy.billing.credit-note-issued` |
| Book | the canonical contract requires `X-EIA-Book: DIRECT`; the domain and expert accept an absent header | SPEC 3.6 book wall |

Consequences:

- A consumer cannot see the approval, SAP credit-memo number, tax amount, or
  original invoice reference because none of them is modelled or returned.
- The free-text reason cannot be mapped to the SPEC six-value enum without a
  translation table; the domain test's `CANCELLATION`/`ENDORSEMENT`/... example
  is illustrative, not enforced by the expert's `CreditNoteRules`.
- The four-state lifecycle collapses the SPEC request/approval/SAP flow into
  DRAFT/ISSUED/APPLIED/CANCELLED, so a client cannot observe REQUESTED,
  APPROVED, SENT_TO_SAP, or REJECTED.
- Creating a note bumps the policy row version but writes no event, so a
  consumer that only subscribes to the credit-note facts never sees the DRAFT
  creation. Only the three transition facts are published.
- The create has no `Idempotency-Key` and no caller-supplied business key, so a
  retried request produces a second note and consumes a second server-assigned
  number; the status command accepts no `If-Match`, and a replay of a terminal
  target is a 409 rather than a no-op.
- A missing `X-EIA-Book` is accepted by both the domain and the expert even
  though the canonical contract requires DIRECT; another book is hidden as 404
  `BOOK_SCOPE_VIOLATION`.
- The three event names are new and have no SPEC equivalent other than the
  issued fact, so aligning them requires the EV-05 dual-publish window (M-22).

Evidence:

- `repos/eia-policy-domain/.../PolicyCreditNoteController.java:27-76` (public
  GET/POST/PATCH, required tenant header, `requireDirectWhenPresent`, 201),
  `PolicyCreditNoteService.java` (expert delegation), `CreditNote.java`,
  `CreateCreditNoteCommand.java`, and `UpdateCreditNoteStatusCommand.java`.
- `repos/eia-policy-domain/.../PolicyClient.java:652-720` (expert
  `/internal/v1` calls) and `:1103-1121` (`ExpertCreditNote` aliases; `id` ->
  `creditNoteId`, `tenantId` dropped).
- `repos/eia-policy-expert/.../CreditNoteController.java:27-77` (public and
  internal aliases, tenant query/header, 201/200),
  `CreditNoteService.java:47-124` (policy wall, currency match, number
  consumption, conditional transition, policy version bump, outbox),
  `CreditNoteRules.java:16-127` (four states, transition graph, positive
  amount, currency, 500-character reason), `CreditNoteRepository.java:20-118`
  (tenant/policy-scoped reads, `CN-{7 digits}` sequence, conditional update),
  `PolicyCreditNote.java`, `CreateCreditNoteRequest.java`, and
  `UpdateCreditNoteStatusRequest.java`.
- `repos/eia-policy-expert/.../PolicyEvents.java:22-24,92-116`
  (`policy.credit-note.issued` / `.applied` / `.cancelled` with policy and note
  identity, amount, currency, and status) and
  `src/main/resources/schema.sql:525-554` (`policy_credit_note`, its CHECK
  constraints, and the number sequence).
- Tests: `PolicyCreditNoteControllerTest`, `PolicyCreditNoteServiceTest`,
  `PolicyCreditNoteClientTest`, `CreditNoteControllerTest`,
  `CreditNoteServiceTest`, and `CreditNoteRulesTest`.
- `openapi/policy.yaml` 2.9.0, `asyncapi/policy.yaml` 1.7.0, and
  `asyncapi/event-catalog.yaml` 1.20.0 record the implemented shape.

Resolution: either extend SPEC 11.2.13 with the implemented short route,
four-state lifecycle, free-text reason, and three event names, or add the SPEC
request/approval/SAP lifecycle, reason enum, and `policy.billing.credit-note-issued`
name behind an EV-05 dual-publish window. Until then the contract documents the
implemented narrow surface and the DIRECT book requirement.

## Validation evidence

The repository validator was run on the working tree after the 2026-10-21
Document content version contract:

```text
$ python scripts/validate_contracts.py
EIA canonical contract validation
repository: .../repos/eia-contracts
python: 3.12.8 (standard library only)

OpenAPI 3.1 documents
  OK openapi/party.yaml  5 paths, 7 operations
  OK openapi/policy.yaml  48 paths, 63 operations
  OK openapi/contract.yaml  41 paths, 59 operations
  OK openapi/direct-claims.yaml  49 paths, 72 operations
  OK openapi/assumed-claims.yaml  41 paths, 58 operations
  OK openapi/cession.yaml  9 paths, 11 operations
  OK openapi/retrocession.yaml  9 paths, 11 operations
  OK openapi/document.yaml  15 paths, 20 operations
  OK openapi/payment.yaml  11 paths, 14 operations
  OK openapi/notifications.yaml  7 paths, 9 operations

AsyncAPI 3 documents
  OK asyncapi/party.yaml  9 event channels
  OK asyncapi/policy.yaml  29 event channels
  OK asyncapi/contract.yaml  30 event channels
  OK asyncapi/direct-claims.yaml  26 event channels
  OK asyncapi/assumed-claims.yaml  21 event channels
  OK asyncapi/cession.yaml  17 event channels
  OK asyncapi/retrocession.yaml  17 event channels
  OK asyncapi/document.yaml  21 event channels
  OK asyncapi/payment.yaml  19 event channels
  OK asyncapi/notifications.yaml  12 event channels
  OK catalog: 201 unique published events across 10 verticals

JSON Schema 2020-12 documents

JSON Reference resolution
  OK walked 22 YAML documents

Result
  PASS 12657 checks, 0 failures
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
  failure message. The 2026-10-20 pass added three more negative checks that
  each fail as expected: removing `/api/v1/parties/search`, dropping `items`
  from the required `SearchResponse` keys, and declaring a book header on the
  non-book-scoped `/api/v1/documents/search`. The Direct Claims task/note pass
  added three more: renaming the `/api/v1/claims/{claimId}/tasks` path, renaming
  the `TaskCreate` schema, and dropping `direct.claim.task-created` from the
  Direct Claims `implemented` list each fail with the specific path, schema, or
  implemented-event message. The Assumed Claims task/note pass added three more:
  renaming the `/api/v1/assumed-claims/claims/{claimId}/tasks` path, renaming
  the `TaskStatusChange` schema, and dropping
  `assumed.claim.note-added` from the Assumed Claims `implemented` list each
  fail with the specific path, schema, or implemented-event message. The payment
  source pass added three more: removing `sourceId` from the `Payment` schema,
  adding `OTHER` to the classified-source `if` enum, and removing
  `sourceReference` from the `PaymentPaymentCreatedData` payload each fail with
  the specific schema or rule message. The claim idempotency pass added three
  more: removing the `ClaimIdempotencyKey` parameter from
  `POST /api/v1/claims/{claimId}/tasks`, changing the shared key schema
  `maxLength` from 64 to 128, and removing the 409 response from an Assumed
  Claims task POST each fail with the specific parameter, bounds, or response
  message. The claim assignment pass added four more: renaming the
  `/api/v1/claims/{claimId}/assignment` path, removing `assignedAt` from the
  `AssumedClaim` schema, making `assignedTeam` required in
  `AssignClaimRequest`, and dropping `direct.claim.assigned` from the Direct
  Claims `implemented` list each fail with the specific path, schema, field, or
  implemented-event message. The document association-link pass added three
  more: removing the `/api/v1/documents/{documentId}/links` path, renaming the
  `DocumentLink` schema, and dropping `document.link.added` from the Document
  `implemented` list each fail with the specific path, schema, or
  implemented-event message. The Policy billing pass added three more: renaming
  the `/api/v1/policies/{policyId}/billing` path, renaming the `BillingPlan`
  schema, and dropping `policy.installment.paid` from the Policy `implemented`
  list each fail with the specific path, schema, or implemented-event message;
  each exited non-zero and named the removed object. The Policy renewal pass
  added three more: renaming the `/api/v1/policies/{policyId}/renew` path,
  removing `renewedFromPolicyId` from the `Policy` schema, and dropping
  `policy.policy.renewed` from the Policy catalog entries each fail with the
  specific path, schema, or implemented-event message. All three negatives were
  run on a throwaway copy; the catalog negative removed the name from both lists
  and produced the channel-set and implemented-event failures. The payment
  source filter pass added three more: removing the `sourceType` parameter from
  `GET /api/v1/payments`, dropping `OTHER` from `PaymentSourceType`, and
  removing `INVALID_SOURCE_FILTER` from the public list description each fail
  with the specific parameter, enum, or error-documentation message. All three
  were run on a throwaway copy and exited non-zero. The Contract
  technical-account pass added four more: renaming the
  `/api/v1/contracts/{contractId}/technical-accounts/{accountId}/status` path,
  renaming the `TechnicalAccount` schema, adding `DRAFT` to the
  `UpdateTechnicalAccountStatusRequest.status` enum, and removing
  `contract.technical-account.created` from the catalog `published` list each
  fail with the specific missing operation, schema, enum, or event message. All
  four were run on a throwaway copy and exited non-zero. The Contract
  period-bordereau pass added four more: renaming the
  `/api/v1/contracts/{contractId}/bordereaux/{bordereauId}/status` path,
  renaming the `Bordereau` schema, adding `RECEIVED` to the
  `UpdateBordereauStatusRequest.status` enum, and dropping
  `contract.bordereau.received` from the catalog `implemented` list each fail
  with the specific missing operation, schema, enum, or implemented-event
  message. All four were run on a throwaway copy and exited non-zero. The
  Direct Claims allocation pass added four more: renaming the
  `/api/v1/claims/{claimId}/allocations` path, renaming the `AllocationSummary`
  schema, widening `CreateClaimAllocationRequest.policyYear` from 1900-2200 to
  1800-2200, and dropping `direct.claim.allocation-created` from the Direct
  Claims `implemented` list each fail with the specific missing operation,
  schema, bounds, or implemented-channel message. All four were run against the
  working tree with the mutated file restored after each run and exited
  non-zero. The Policy premium-receivables pass added three more: renaming the
  `/api/v1/billing/installments` path, renaming the `Receivable` schema, and
  widening the receivable `limit` maximum from 200 to 500 each fail with the
  specific missing operation, schema, or limit-bounds message. All three were
  run on a throwaway copy and exited non-zero (exit 1); the working copy was
  left unchanged. The Policy mass tort profile pass added four more: renaming
  the `/api/v1/policies/{policyId}/mass-tort-profile` path, renaming the
  `MassTortProfile` schema, dropping `policy.mass-tort-profile.updated` from
  the Policy `implemented` list, and restoring the implemented route to
  `x-planned-operations` each fail with the specific missing operation,
  schema, implemented-event, or planned-route message. All four were run on a
  throwaway copy and exited non-zero (exit 1); the working copy was left
  unchanged. The Direct Claims list-filter pass added three more: removing the
  `claimantPartyId` parameter from `GET /api/v1/claims`, changing its schema
  `format` from `uuid` to no format, and removing the shared
  `DirectClaimStatusFilter` from the public list each fail with the specific
  parameter, schema, or retained-filter message. All three were run on a
  throwaway copy and exited non-zero (exit 1); the working copy was left
  unchanged. The Contract cash-call pass added four more: renaming the
  `/api/v1/contracts/{contractId}/cash-calls/{cashCallId}/status` path,
  renaming the `CashCall` schema, adding `REQUESTED` to the
  `UpdateCashCallStatusRequest.status` enum, and dropping
  `contract.cash-call.settled` from the catalog `implemented` list each fail
  with the specific missing operation, schema, enum, or implemented-event
  message. All four were run on a throwaway copy and exited non-zero (exit 1);
  the working copy was left unchanged. The Payment allocation pass added four
  more: renaming the `/api/v1/payments/{paymentId}/allocations` path, renaming
  the `PaymentAllocationSummary` schema, removing `ALLOCATION_EXCEEDS_PAYMENT`
  from the create description, and dropping `payment.allocation.created` from
  the Payment catalog `implemented` list each fail with the specific missing
  operation, schema, conflict-code documentation, or implemented-event message.
  All four were run on a throwaway copy and exited non-zero (exit 1); the
  working copy was left unchanged. The Direct Claims allocation-erosion pass
  added four more: adding a `requestBody` to the erosion retry, removing
  `erosionStatus` from the required `Allocation` keys, changing the 409 code to
  `STATE_CONFLICT`, and re-adding a public `AllocationErosionRequest` schema
  each fail with the specific request-body, required-field, conflict-code, or
  public-schema message. All four were run on a throwaway copy and exited
  non-zero (exit 1); the working copy was left unchanged. The Contract
  security/collateral pass added four more: renaming the
  `/api/v1/contracts/{contractId}/security` path, removing `OUTSTANDING` from
  the `SecurityStatus` enum, adding `status` to the
  `CreateContractSecurityRequest` properties, and dropping
  `contract.security.recorded` from the Contract catalog `implemented` list
  each fail with the specific missing operation, enum, caller-status, or
  implemented-event message. All four were run on a throwaway copy and exited
  non-zero (exit 1); the working copy was left unchanged. The Policy
  installment-dunning pass added four more: renaming the
  `/api/v1/billing/installments/{installmentId}/dunning` path, removing
  `lastDunningAt` from the `Receivable` schema, widening the
  `CreateDunningRequest.notes` cap from 2000 to 4000, and dropping
  `policy.dunning.sent` from the Policy catalog `implemented` list each fail
  with the specific missing operation, schema/nullability, notes-bound, or
  implemented-event message. All four were run on a throwaway copy and exited
  non-zero (exit 1); the working copy was left unchanged. The Direct Claims
  mass-tort allocation guard pass added one more: removing
  `MASS_TORT_YEAR_OUTSIDE_BLOCK` from the allocation create 400 description
  fails with the specific missing-code message. It was run on a throwaway copy
  and exited non-zero (exit 1); the working copy was left unchanged. The Policy
  program pass added five more: renaming the `GET/POST /api/v1/programs` path,
  renaming the `Program` schema, removing `programId` from
  `UpdatePolicyProgramRequest.required`, marking `policy.program.created`
  planned, and re-adding `/api/v1/programs` to `x-planned-operations` each fail
  with the specific missing-operation, schema/required-field, implemented-event,
  or planned-route message. All five were run on a throwaway copy and exited
  non-zero (exit 1); the working copy was left unchanged. The Document content
  pass added five more: renaming the
  `/api/v1/documents/{documentId}/content/metadata` path, renaming the
  `DocumentContent` schema, removing the required `X-File-Name` header,
  dropping `document.content.uploaded` from the Document catalog `implemented`
  list, and re-adding `/api/v1/documents/{documentId}/content` to
  `x-planned-operations` each fail with the specific missing-operation,
  schema, header, implemented-event, or planned-route message. All five were
  run on a throwaway copy and exited non-zero (exit 1); the working copy was
  left unchanged. The Contract security status pass added four more: renaming
  the `/api/v1/contracts/{contractId}/security/{securityId}/status` path,
  adding `ACTIVE` to the `UpdateContractSecurityStatusRequest.status` enum,
  replacing the `RELEASED` terminal wording, and dropping
  `contract.security.status-changed` from the Contract catalog `implemented`
  list each fail with the specific missing-operation, enum, terminal-state, or
  implemented-event message. All four were run on a throwaway copy and exited
  non-zero (exit 1); the working copy was left unchanged. The Policy credit-note
  pass added four more: renaming the
  `/api/v1/policies/{policyId}/credit-notes` path, renaming the `CreditNote`
  schema, adding `DRAFT` to the `UpdateCreditNoteStatusRequest.status` enum, and
  dropping `policy.credit-note.issued` from the Policy catalog `implemented`
  list each fail with the specific missing-operation, schema, enum, or
  implemented-event message. All four were run on a throwaway copy and exited
  non-zero (exit 1); the working copy was left unchanged. The Document
  content-version pass added three more: renaming the
  `/api/v1/documents/{documentId}/content/versions` path, removing
  `currentVersion` from the required `DocumentContent` keys, and removing
  `version` from the required `DocumentContentUploadedData` keys each fail with
  the specific missing-operation, required-metadata-field, or required-payload
  message. All three were run on a throwaway copy and exited non-zero
  (exit 1); the working copy was left unchanged.

## Resolution policy

1. A deviation is fixed in the service, not by weakening the contract, unless
   the Architecture owner accepts the implemented shape as canonical.
2. When a deviation is fixed, remove it from this file in the same change that
   updates the contract, and record the closure in the closed-mismatches table.
3. A new deviation must be added here with the same evidence standard: source
   path and symbol or line, and the SPEC section it violates.

