# Contract-to-implementation audit

Status: open, reviewed 2026-10-22 (Notification template approver directory ids).

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
  event factory, and `schema.sql`. The Contract technical-account-line pass
  reads the domain line controller, service, client, projection, summary,
  line-type vocabulary, and command plus the expert line controller, rules,
  repository, line-type enum, list read model, request, reconciliation
  exception, event factory, `schema.sql`, and the domain and expert line tests;
  the 2026-10-21 expansion pass re-read the same sources for the 13-type
  vocabulary, the bucket roll-up, and the `bucketTotals` read model. The
  2026-10-21 technical-account settlement-reference pass re-reads the domain
  status command, client, and projection and the expert status request, rules,
  repository, event factory, and `schema.sql` for the reference field. The
  2026-10-21 Direct Claims settlement-payment-link pass reads the domain detail
  controller, service, command, projection, client, and exception mapping plus
  the expert settlement controller, request, service, repository, projection,
  not-linkable exception, event factory, `schema.sql`, and the domain and expert
  tests. The 2026-10-21 Payment status pass reads the domain status controller,
  command, service, client, projection, and exception mapping plus the expert
  status controller, request, service, rules, repository, event factory,
  `schema.sql`, and the status and outbox tests. The Contract period-bordereau
  pass reads the
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
  and expert tests. The program-capacity pass re-read the domain program
  service, projection, command, and client plus the expert program rules, view,
  entity, repository, request, `schema.sql`, and the domain and expert capacity
  tests.
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
  The credit-application pass re-read the same credit-note sources plus the
  expert billing repository, installment projection, summary, rules, and event
  factory, and the domain billing plan, installment, summary, receivable, and
  client remaps.
  The credit-note reversal pass re-read the same credit-note sources plus the
  expert reversal rule, repository transition, event factory, and `schema.sql`
  columns and the domain reversal command, projection, client forwarding, and
  the domain and expert reversal tests.
  The cancellation-linked credit-note pass re-read the domain credit-note
  command, projection, client, and tests plus the expert credit-note request,
  service, rules, repository, projection, event factory, cancellation
  repository/service/projection, `schema.sql`, and the domain and expert link
  tests. It also reads the domain `CancellationDto` and contract controller,
  which do not yet expose `cancellationNumber` on the public cancellation
  projection.
  The Policy legal-entity pass reads the domain legal-entity and
  policy-assignment controllers, services, DTO/commands, `PolicyDto`, and
  `PolicyClient` plus the expert legal-entity controller, service, rules,
  repository, entity, view, create and assignment requests, event factory,
  `schema.sql`, and the domain and expert tests.
  The Document content-tombstone pass reads the domain content controller,
  service, client, projection, and exception handling plus the expert content
  controller, service, rules, repository, tombstone SQL, content and metadata
  records, `DocumentContentEvents`, the two deletion exceptions, the exception
  handler, and the domain and expert tombstone tests.
  The Document disposition-content pass reads the expert `DocumentService`
  disposition and content-tombstone helper, the content repository tombstone SQL
  and event factory, and `DocumentDispositionContentTombstoneIntegrationTest`,
  and re-checks the domain content and disposition controllers and clients for
  the unchanged public response shape.
  The Notifications DUNNING_NOTICE pass reads the domain and expert
  `NotificationType` enums and their create validation, the notification
  service and controller tests, the web workbench's notification-type list and
  prefill defaults, and the shell receivables hand-off constants and links.
  The Notifications template-management pass reads the domain and expert
  template controllers, services, DTOs, status and channel enums, commands and
  requests, repository, event factory, `schema.sql`, expert client, exception
  mapping, and the template controller, service, integration, and outbox tests.
  The Notifications template-approver pass re-reads the domain approve command
  and service plus the expert approve request, template entity and DTO, service
  validation, repository `markApproved`, `NotificationTemplateEvents`,
  `schema.sql` and its H2 mirror, and the domain and expert template controller,
  service, integration, and outbox tests for the string directory identifier.
  The Policy premium-audit pass reads the domain premium-audit controller,
  service, command, result, projection, and `PolicyClient` plus the expert
  premium-audit controller, service, rules, request, `VersionTimeline`,
  `PolicyEvents`, `schema.sql` endorsement-type migration, and the domain and
  expert controller, service, and integration tests.
  The Policy billing-adjustment pass reads the domain billing controller,
  service, `BillingAdjustmentCommand`, `BillingAdjustmentResult`, book scope,
  `PolicyClient`, and tests plus the expert billing controller, adjustment
  request and view, service, rules, repository, event factory, `schema.sql`,
  and tests.
  The Direct Claims litigation pass reads the domain litigation controller,
  service, command, projection, client, and tests plus the expert litigation
  controller, request, matter, service, repository, event factory, `schema.sql`,
  and the domain and expert litigation tests.
  The Notifications source-linkage pass reads the domain notification
  controller, service, create command, projection, expert client, and exception
  mapping plus the expert controller, service, create request, notification
  record, `NotificationSourceType`, repository, `schema.sql` source columns,
  `NotificationEvents`, error codes, and the domain and expert source-linkage
  tests.
  The Notifications source-filter pass reads the domain list controller,
  service, expert client, projection, and exception mapping plus the expert
  list controller, service, `NotificationSourceType.validateFilter`, the
  `findAllBySource` repository query, error codes, and the domain and expert
  source-filter tests.
  The Notifications source-type pass re-reads the expert `NotificationSourceType`
  enum and its `normalize` loop, the create and list service rules, the
  `schema.sql` source columns, and the domain and expert source-linkage and
  source-filter tests against the widened ten-value set.
  The Party reference-data pass reads the domain identifier and address
  controllers, DTOs, client, and exception handler plus the expert shared
  reference-data controller and service, the identifier and address records,
  their repositories, `PartyEvents`, `schema.sql`, the expert
  `ApiExceptionHandler`, and the domain and expert reference-data tests.
  The Party status pass reads the domain status controller, command, client,
  projection, and exception handler plus the expert status controller, service,
  status request, party record, repository, `PartyEvents`, `schema.sql`, the
  expert `ApiExceptionHandler`, and the domain and expert status and outbox
  tests.
  The Party maintenance pass re-reads the domain identifier and address
  controllers, DTOs, client, and exception handler and the expert shared
  reference-data controller, service, `UpdatePartyIdentifierRequest`,
  `UpdatePartyAddressRequest`, `PartyChildNotFoundException`, both repositories,
  `PartyEvents`, `schema.sql`, `ApiExceptionHandler`, and the domain and expert
  update/delete tests, negatives, version bumps, no-ops, and outbox
  assertions.
  The Notifications delivery-attempt pass reads the domain attempts controller,
  service, expert client, delivery-attempt projection, and exception handling
  plus the expert attempts controller, service, attempt record and repository,
  the delivery-provider abstraction and simulator, the notification repository
  send transition, `NotificationEvents`, `schema.sql`, and the domain and expert
  delivery and controller tests.
  The Policy rating-worksheet pass reads the domain rating controller, service,
  `RatePolicyCommand`, `RatingWorksheetDto`, `PolicyRatingResult`, `PolicyClient`,
  book scope, ETag, and idempotency helpers plus the expert rating controller,
  service, `RatingRequest`, `RatingRules`, `PolicyRatingWorksheet`,
  `RatingWorksheetRepository`, `RatingResult`, `PolicyEvents`, `MutationGuard`,
  `schema.sql`, and the domain and expert controller, service, rules, client,
  and integration tests. The 2026-10-22 replay pass adds the expert
  `PolicyIdempotencyService`, `PolicyIdempotencyRepository`,
  `PolicyIdempotencyResponse`, `IdempotentResponse`, `IdempotencyKeys`, the
  `policy_idempotency` table, and `PolicyIdempotencyReplayIntegrationTest`.
  The Policy underwriting-submission pass reads the domain submission
  controller, service, `SubmissionDto`, `CreateSubmissionCommand`,
  `UpdateSubmissionStatusCommand`, `PolicyClient`, and `Problems` plus the
  expert submission controller, service, `UnderwritingSubmission`,
  `UnderwritingSubmissionView`, `UnderwritingSubmissionRules`,
  `UnderwritingSubmissionRepository`, `UnderwritingSubmissionNumberAllocator`,
  `CreateUnderwritingSubmissionRequest`,
  `UpdateUnderwritingSubmissionStatusRequest`, `PolicyEvents`, `schema.sql`,
  the shared `RequestScope`/`ApiExceptionHandler`, and the domain and expert
  controller, service, rules, client, and integration tests.
  The Policy submission-conversion pass reads the domain conversion controller,
  service, `ConvertSubmissionCommand`, `SubmissionConversionResult`,
  `SubmissionDto`, `PolicyDto`, `PolicyClient`, and ETag/replay mapping plus the
  expert conversion controller, `ConvertSubmissionRequest`,
  `SubmissionConversionService`, `SubmissionConversionResult`,
  `UnderwritingSubmissionRules`, `UnderwritingSubmissionRepository`,
  `UnderwritingSubmissionView`, `Policy`, `PolicyRepository`, `PolicyEvents`,
  the coverage repository, `schema.sql`, and the domain and expert controller,
  service, client, and integration tests. The replay pass also reads
  `PolicyIdempotencyService`, `PolicyIdempotencyRepository`,
  `IdempotentResponse`, `IdempotencyKeys`, and
  `PolicyIdempotencyReplayIntegrationTest`.
  The Policy idempotency request-hash pass re-reads the expert
  `PolicyIdempotencyService`, `PolicyIdempotencyRepository`,
  `PolicyIdempotencyResponse`, `IdempotentResponse`, `IdempotencyKeys`, the
  `policy_idempotency` table, `IdempotencyKeysTest`, and
  `PolicyIdempotencyReplayIntegrationTest` for the canonical rating and
  conversion hashes, the 409 `IDEMPOTENCY_CONFLICT` with
  `meta.operation`/`meta.key`, the concurrent-reservation outcome, and the
  legacy null-hash replay.
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
| M-03 | Money serialized as a JSON number by four services | Every money-bearing service now serializes the amount as a decimal string. The remaining flat `amount`/`currency` pair shape is a field-shape gap covered by M-12 and M-13, not a JSON-type gap. The later Policy underwriting-submission slice reintroduces one JSON-number amount (`requestedLimitAmount`), which M-59 records. | `@JsonFormat(shape = JsonFormat.Shape.STRING)` on `PolicyDto`, `Policy`, `ClaimDto`, `Claim`, `AssumedClaimDto`, `AssumedClaim`, `CessionDto`, `Cession`, `RetrocessionDto`, `Retrocession`, `PaymentDto`, and `Payment`. |
| M-09 | Book mismatch was 404 in the claim verticals and 400 in the reinsurance verticals | A wrong `X-EIA-Book` is hidden as 404 `BOOK_SCOPE_VIOLATION` in Direct Claims, Assumed Claims, Cession, and Retrocession. A missing header is still a 400 `BOOK_REQUIRED` in Cession and Retrocession, which is a validation error rather than a book mismatch, so it does not confirm existence. | `RequestScope.requireDirectBook` / `requireAssumedBook`, `BookWall`, and `BookScopeFilter` in the four book-scoped verticals. |
| M-15 | Party domain had no exception mapping | `eia-party-domain` now has a `@RestControllerAdvice`; `PartyClient` translates expert 404 to 404 `NOT_FOUND`, other 4xx to 400 with the expert code, and 5xx/unreachable to 503 `EXPERT_UNAVAILABLE`. | `repos/eia-party-domain/.../ApiExceptionHandler.java`, `PartyClient.java`. |

## Summary

| ID | Area | Severity |
|---|---|---|
| M-01 | Public base paths differ from the SPEC vertical tables | M |
| M-02 | Several error-body shapes remain; Policy is now canonical | H |
| M-04 | Pagination: Policy uses an offset envelope, other lists are bare arrays | H |
| M-05 | `_links` exist on Policy pages only; no detail links anywhere | M |
| M-06 | `ETag`/`If-Match` are complete only in Policy; the Party status response emits an ETag and accepts `If-Match` but does not compare it, and other verticals use body versions | H |
| M-07 | `Idempotency-Key` covers Policy (including request-hash conflicts for rating and conversion since 2.21.0) and claim task/note creates; the Party status command forwards but does not replay a key | M |
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
| M-35 | Payment allocations add a SPEC-less create/reverse route pair and event names | L |
| M-36 | Direct Claims allocation erosion retry swallows the expert conflict and record failure | M |
| M-37 | Contract security/collateral uses a narrow derived-status projection and a wider legacy status vocabulary | L |
| M-38 | Policy installment dunning adds a SPEC-less route and event name and a different level vocabulary and book rule | L |
| M-39 | Policy program catalog uses a short read/create path, a different type/status vocabulary, a flat optional capacity pair, and SPEC-less membership and event names | L |
| M-40 | Document content keeps a current pointer plus revisions under `/content/versions`, not the SPEC `/versions` store | L |
| M-41 | Policy credit notes use a short path, a five-state lifecycle, free-text reason, installment application and reversal, and new event names, with no approval or SAP step | L |
| M-42 | Contract technical-account lines implement the 13-type SPEC vocabulary and bucket reconciliation but omit line correction, per-line currency/source metadata, and per-line approval | L |
| M-43 | Policy legal entity catalog is a narrow five-type slice with a nullable issuing-entity link | M |
| M-44 | Document legal holds and disposition are a per-document, synchronous slice without the SPEC hold collection or the approval/certificate workflow | L |
| M-45 | Direct Claims settlement payment links are a SPEC-less route and event over one stored Payment id | L |
| M-46 | Payment public status PATCH is SPEC-less and its graph is wider than SPEC 11.7.6 | L |
| M-47 | Document content tombstones add a SPEC-less DELETE route and event and keep the metadata; a disposition now applies the same tombstone without the SPEC approval/certificate job | L |
| M-48 | Notifications adds a SPEC-less `DUNNING_NOTICE` type to the closed `NotificationType` enum | L |
| M-49 | Notification template administration uses a short path, approve/retire commands, SPEC-less events, and a directory-id approver | L |
| M-50 | Policy premium audit is a SPEC-less route/event that re-rates the policy premium without the SPEC `policy_premium_audit` worksheet or batch job | L |
| M-51 | Policy billing adjustment is a SPEC-less derived-delta route and event and does not honour the optional concurrency/idempotency headers | L |
| M-52 | Direct Claims litigation damages are a SPEC-less pair and the created event has no SPEC name | L |
| M-53 | Notification source linkage and list source filter are a flat SPEC-less triple and exact pair rather than the SPEC subject reference | L |
| M-54 | Party identifiers and addresses are SPEC-less append-only child routes with wider type sets, a plaintext value, and no implemented address duplicate guard | M |
| M-55 | Party status transitions are a SPEC-less command with no transition graph, no status history, event-only reason, and unenforced concurrency/idempotency headers | M |
| M-56 | Notification delivery attempts use a SPEC-less per-notification route, a narrower delivery row than SPEC 11.8.4, notification-level evidence, and a simulator-only provider with no retry | L |
| M-57 | Policy rating worksheets are a SPEC-less policy-scoped route and event with only two rating methods, a CALCULATED-only worksheet, no submission/product, exposure-line, factor-trace, tax, or fee model, and a tenant+operation keyed replay with a canonical request hash since 2.21.0 | L |
| M-58 | Party identifier and address maintenance adds SPEC-less PATCH/DELETE child routes with full replacement, a no-op update, a hard delete, and unenforced duplicate/in-use guards and concurrency headers | M |
| M-59 | Policy underwriting submissions are a SPEC-less pre-policy collection with a narrower six-state graph, no clearance/rating/referral/quote/producer slices, two new event names, unhonoured concurrency/idempotency headers, and a JSON-number limit amount | M |
| M-60 | Submission conversion is a SPEC-less command with a bare-policy expert shape, a stored-key 200 replay with a canonical request hash since 2.21.0 and a linked-policy 200 replay without one, a new event name, an unprojected public `Policy.submissionId`, and no SPEC clearance/rating gate | M |

## M-01 Public base paths

The implemented public route is the shorter vertical-less form; the SPEC
vertical tables use `/api/v1/{vertical}/{resource}`. The gateway and the web
remotes agree with the implementation, so the SPEC tables are the outlier.

| Vertical | Implemented (and gateway route) | SPEC 11 table |
|---|---|---|
| Party | `/api/v1/parties` | `/api/v1/party/parties` |
| Policy | `/api/v1/policies` | `/api/v1/policy/policies` |
| Policy legal entities | `/api/v1/legal-entities` | `/api/v1/policy/legal-entities` |
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
Policy legal entities add the short-form catalog row: the implemented
`/api/v1/legal-entities` versus SPEC 11.2.16's
`/api/v1/policy/legal-entities`; the implemented assignment command
`PATCH /api/v1/policies/{policyId}/legal-entity` has no SPEC route (M-43).
Policy premium audit adds a command row: the implemented
`POST /api/v1/policies/{policyId}/premium-audit` has no SPEC 11.2.10 route;
the SPEC 6.12 transaction inventory names the transaction `policy.premium-audit`
(M-50). The notification delivery-attempt history adds
`GET /api/v1/notifications/{notificationId}/attempts`, which SPEC 11.8.10 does
not list; its tenant-wide delivery diagnostics and retry command remain planned
(M-56). Policy rating adds a command and read row: the implemented
`POST/GET /api/v1/policies/{policyId}/rating` has no SPEC 11.2.10 route; SPEC
11.2.14 mounts rating under `/api/v1/policy/submissions/{submissionId}/rating`
and names no standalone worksheet read (M-57). Party identifier and address
maintenance adds no base-path row: the implemented
`PATCH/DELETE /api/v1/parties/{partyId}/identifiers/{identifierId}` and
`PATCH/DELETE /api/v1/parties/{partyId}/addresses/{addressId}` routes live under
the already-short Party base and have no SPEC 11.1.10 equivalent (M-58). Policy
underwriting submissions add a collection row: the implemented
`/api/v1/policies/submissions` lives under the short `/api/v1/policies` base,
while SPEC 11.2.14 lists `POST /api/v1/policy/submissions` (no list, read, or
status row) and mounts clearance, rating, referral, and quote as further
submission commands rather than status edges (M-59). Submission conversion adds
a command row: the implemented
`POST /api/v1/policies/submissions/{submissionId}/convert` (expert alias
`/internal/v1`) has no SPEC 11.2.14 route; the SPEC models the step as the
submission `quote`/`bind` commands and names no conversion event (M-60).

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
- `repos/eia-policy-domain/.../LegalEntityController.java:26`,
  `PolicyLegalEntityController.java:21`, and
  `repos/eia-policy-expert/.../LegalEntityController.java:29` -
  `/api/v1/legal-entities` and
  `/api/v1/policies/{policyId}/legal-entity` (the expert also maps the
  `/internal/v1` alias).
- `repos/eia-policy-domain/.../PolicyPremiumAuditController.java:25` and
  `repos/eia-policy-expert/.../PremiumAuditController.java:22-25` -
  `/api/v1/policies/{policyId}/premium-audit` (the expert also maps the
  `/internal/v1` alias).
- `repos/eia-policy-domain/.../SubmissionController.java:122-140` and
  `repos/eia-policy-expert/.../UnderwritingSubmissionController.java:106-122` -
  `POST /api/v1/policies/submissions/{submissionId}/convert` (the expert also
  maps the same path under `/internal/v1`).
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
| Party (expert) | inline `Map<String, String>` | `{code, message}` for `NOT_FOUND`, `CONFLICT`, `VALIDATION_ERROR`, and the malformed-body case |
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
- `repos/eia-party-expert/.../ApiExceptionHandler.java` (NOT_FOUND, CONFLICT,
  VALIDATION_ERROR, and malformed-body handlers)
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
collections, the Direct Claims child collections, the Assumed Claims child
collections in Round 5, and the Party identifier and address lists are also
bare arrays. The Policy program catalog list
(`GET /api/v1/programs`) is also a bare `Program[]` rather than the Policy page
envelope (M-39). The Policy underwriting-submission list
(`GET /api/v1/policies/submissions`) is also a bare `PolicySubmission[]` rather
than the Policy page envelope (M-59). There is no `page` object, no cursor, and
no `total` in those responses.

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
| Policy public premium audit | Accepts optional `If-Match` and returns the updated policy `ETag`; a stale tag is 409 `CONCURRENT_MODIFICATION` |
| Policy public rating | Accepts optional `If-Match` and compares it before any write; the applied 201 returns the refreshed policy `ETag`, while a calculation-only 201 has no `ETag`; a stale tag is 409 `CONCURRENT_MODIFICATION`; a keyed replay returns the stored 200 body and the stored `ETag` when the original applied |
| Policy public mass tort profile | No `ETag`/`If-Match`; a concurrent profile or policy change is 409 `CONCURRENT_MODIFICATION` |
| Policy public submissions | List/get/create return the submission `ETag`; the status command accepts and forwards `If-Match` but the expert compares neither it nor an `expectedVersion` body field, so a stale tag is not a 409 by itself; a concurrent transition is 409 `CONCURRENT_MODIFICATION` with the current and expected versions |
| Policy public submission conversion | Accepts no `If-Match`; the 201/200 returns the linked policy `ETag` and `Idempotent-Replayed`, and a stored-key replay returns the `ETag` captured by the first keyed call; the submission row is locked for the command and the tenant-scoped unique `submission_id` is the second guard, so a lost write is 409 `CONCURRENT_MODIFICATION` rather than a caller-tag comparison |
| Party public PATCH status | Returns `ETag: "<version>"`; accepts optional `If-Match` and `Idempotency-Key`, forwards both, but the expert compares neither, so a stale tag is not a 409 and a retry is not replayed |
| Party public child PATCH/DELETE | No `ETag`/`If-Match`; a replacement and a delete are unconditional once the party and child resolve, and a concurrent change is last-write-wins |
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
| Payment public PATCH status | Optional body `expectedVersion`; a stale value is 409 `CONCURRENT_MODIFICATION` with no ETag, and an omitted value is not version-checked |
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
- The Party status command is the only Party operation that emits an `ETag`; the
  domain builds it from the returned `version` and forwards a caller's
  `If-Match` and `Idempotency-Key` unchanged. The expert `PartyController`
  declares neither header, so it never compares the tag or replays the key; a
  same-status request is the only deduplicated retry and a different status on a
  retry applies again with a new version. The contract documents the headers and
  the missing 409 to keep that gap visible (M-55).
- The Party child maintenance routes accept no `If-Match` and return no `ETag`.
  The domain forwards the tenant and body and preserves an expert 409, but the
  expert raises 409 only for a duplicate identifier (and would for the canonical
  address and in-use guards). A lost update is not detected, so two concurrent
  replacements both apply and the later one wins with its own version bump
  (M-58).
- The submission collection returns the submission `ETag` from the aggregate
  `version` on create, read, and transition. The status command accepts and
  forwards `If-Match`, but the expert declares no `If-Match` parameter and no
  `expectedVersion` body field: the conditional update is keyed by the version
  and status the command itself read, so a stale caller tag changes nothing and
  only a write that loses that internal race is 409 `CONCURRENT_MODIFICATION`
  (M-59).
- Conversion takes no caller version at all: the domain forwards no `If-Match`
  and the expert command is not a `PATCH`. It locks the submission row with
  `SELECT ... FOR UPDATE`, re-reads the linked policy inside the transaction,
  and returns the policy `ETag` on both 201 and 200. The submitted premium is
  not protected by a caller tag; a retry after a successful conversion is the
  200 replay instead of a second policy (M-60).

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
and a repeated terminal settlement is the retry-safe path. The 2026-10-22
rating and submission-conversion replay adds the key to those two commands with
stored-response replay and, from Policy 2.21.0, canonical request-hash
conflicts:

- The key is normalized (trimmed) and capped at 128 characters. A blank value
  is treated as absent and a value longer than 128 characters is 400
  `INVALID_IDEMPOTENCY_KEY`. For the commands that store the key, the scope is
  `(tenant, operation, key)`: the create operation is `create`, rating is
  `rating`, conversion is `conversion`, and the second-slice commands use their
  own `(tenant, scope, key)` uniqueness. The reservation is not split by a
  policy, submission, or child id, so one key may be used once per operation and
  the rating and conversion namespaces do not collide; the canonical request
  hash does include the target id, so a key cannot replay a row from another
  aggregate.
- The expert reserves `tenant + operation + key` in `policy_idempotency` in the
  same transaction as the command and stores the canonical request hash on the
  reservation. Create also stores the policy id; rating and conversion store
  the serialized response and its status and leave the policy id null. The hash
  column is nullable so rows written before the hash existed remain readable.
- A same-key replay of an identical canonical request returns 200 with
  `Idempotent-Replayed: true`. Every stored-key command returns 409
  `IDEMPOTENCY_CONFLICT` when the canonical request differs: create and the
  second-slice commands carry `meta.existingPolicyId` or
  `meta.existingResourceId`, while rating and conversion carry
  `meta.operation` (`rating`/`conversion`) and `meta.key` plus
  `errors[0].field` = `Idempotency-Key` and
  `errors[0].code` = `IDEMPOTENCY_CONFLICT`. A rating
  replay also returns the stored strong `ETag` when the original applied, and a
  conversion replay returns the stored policy body and its original `ETag`. A
  legacy row with a null `request_hash` replays instead of conflicting.
- A fresh create is 201 with `Idempotent-Replayed: false`; a fresh keyed
  rating is 201, and a fresh keyed conversion that creates a policy is 201.
  Conversion also keeps the linked-policy 200 replay when the submission
  already has a policy, including for a new key, and stores that 200.
- The create request hash normalizes amounts numerically (`1000.0` and
  `1000.0000` hash the same), uppercases currencies, and defaults the initial
  status to DRAFT. The rating hash covers `policyId`, the trimmed and
  uppercased method, the numerically normalized base rate, exposure, and
  factor (factor defaults to 1), and the effective `apply` flag (false when
  absent). The conversion hash covers
  `submissionId`, the normalized premium, the trimmed and uppercased currency,
  and the null-or-date expiration. The path id in each hash stops a key from
  replaying a row from another aggregate, and the reservation uses
  `INSERT ... ON CONFLICT DO NOTHING`, so concurrent first attempts either
  replay the winner or conflict and never run the command twice.
- The header is optional for backward compatibility, even though SPEC 12.6
  requires it on transaction submission. `Idempotent-Replayed` is emitted by
  the Policy create, rating, and conversion responses; no other vertical uses
  that spelling.

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
  renewal command, the Policy mass tort profile upsert, and the Policy premium
  audit are also outside the Policy idempotency mechanism. The premium-audit
  command accepts and forwards an optional key, but the expert does not replay
  on it, so a retry applies a second audit (M-50). Policy rating and submission
  conversion also compare the optional key by canonical request hash: the key
  is scoped by tenant + operation, a first execution is 201, an identical
  request replays 200 with `Idempotent-Replayed: true`, the stored body, and
  the stored strong `ETag`, and a different request is 409
  `IDEMPOTENCY_CONFLICT` with `meta.operation`/`meta.key` and no write. A legacy
  row with a null request hash replays; conversion also keeps its linked-policy
  200 replay for an unkeyed call or a new key (M-57, M-60). The submission
  create and status
  commands also accept and forward an optional key, but the expert submission
  service has no idempotency store or replay path: a retried create makes a
  second submission with a new number and a retried real transition applies
  again with a new version (M-59). The Party status command also
  accepts and forwards an optional key, but the expert status route does not
  read it; a repeated non-no-op request applies the transition again (M-55). The
  Party child maintenance routes accept no key: a repeated real replacement
  applies again with a new version (a same-value request is the only no-op) and
  a repeated delete is 404, so neither path is a replay (M-58). The
  domain's shared mutation
  helper still emits
  `Idempotent-Replayed: false` on the renewal 201 even though no key is
  accepted, so a client must not read that header as proof that a retry is
  safe. A repeated mass tort PUT rewrites the profile and emits another event,
  so it is not retry-safe either. The header remains optional everywhere it
  exists, so a client that omits it is unaffected.

Evidence:

- `repos/eia-policy-expert/.../IdempotencyKeys.java` (trim, blank-as-absent,
  128-character cap, `INVALID_IDEMPOTENCY_KEY`, and the rating/conversion
  canonical request hash), `PolicyIdempotencyService.java` (hash compare before
  replay, tenant + operation scope, 409 with `meta.operation`/`meta.key`, legacy
  null-hash replay, stored-response completion),
  `PolicyIdempotencyRepository.java` (find, reserve with the hash, and complete
  on `policy_idempotency`), `IdempotentResponse.java`,
  `PolicyRatingController.java:47-68`, and
  `UnderwritingSubmissionController.java:100-124`;
  `repos/eia-policy-expert/src/main/resources/schema.sql:167-201` (the
  `(tenant_id, operation, idempotency_key)` unique scope and the nullable
  response/hash/policy columns); `IdempotencyKeysTest.java` (rating and
  conversion hash stability across scale/whitespace and per-input changes);
  `PolicyIdempotencyReplayIntegrationTest.java` (stored-body/ETag replay,
  rating and conversion hash conflict with `meta.operation`/`meta.key`, tenant
  and operation scope, policy/submission scoping, no-key path, 129-character
  rejection).
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
| Policy submission expert routes | `?tenantId=` query parameter or `X-EIA-Tenant` header (the domain sends both with the same value) |
| Policy submission-conversion expert route | `?tenantId=` query parameter or `X-EIA-Tenant` header; the domain sends both with the same value and an optional `Idempotency-Key` the expert ignores |
| Direct Claims expert status transition | `X-EIA-Tenant` header instead of the query parameter (`ClaimController.java:52-58`) |
| Direct Claims expert child routes | `?tenantId=` on GET, `X-EIA-Tenant` on POST/PATCH |
| Assumed Claims expert create and status | `tenantId` in the body plus `X-EIA-Tenant` sent by the domain client |
| Assumed Claims expert close, financials, audit, and second-slice routes | `X-EIA-Tenant` header |

The contracts document each route exactly. A future cleanup should make the
internal tenant a header only, and remove `tenantId` from request bodies.

## M-10 Lifecycle method inconsistency

The same conceptual operation is exposed with four shapes:

- `PATCH /{id}/status` - Policy, Contract, Direct Claims, Payment public and
  expert.
- `POST /{id}/status` - Assumed Claims, Document.
- `PUT /{id}/status` - Cession, Retrocession expert.
- `POST /{id}/transition` - Cession, Retrocession public.
- Named action POSTs - Payment public `/submit`, `/authorize`, `/approve`,
  `/issue` (the public PATCH status route is also implemented); Policy
  second-slice `/cancel`, `/reinstate`, `/erosion`; Contract `/bind`,
  `/approve`, `/execute`; Direct Claims `/close`, `/approve`, `/execute`;
  Assumed Claims `/accept`, `/resolve`, `/commute`, `/close`.

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
  DRAFT/ISSUED/APPLIED/CANCELLED/REVERSED adjustment (M-41), so the request
  surface exists, but the SPEC approval, SAP credit-memo, tax, and
  original-invoice members remain gaps. The premium-receivables
  slice adds the tenant-wide receivable queue and the dunning slice adds the
  per-installment dunning history and command (M-38), so receivables and
  dunning are no longer resource gaps. The renewal
  slice adds successor-term creation with `renewedFromPolicyId`; the reverse
  `renewed_by_policy_id` pointer, the renewal-bound source transition, the
  renewal batch, non-renewal reasons, and renewal invitations remain gaps
  (M-28). The mass tort slice adds the narrow one-per-policy DRAFT/COMPLETE
  profile (M-32); the SPEC mass tort program, the wider profile columns, and
  the SPEC trigger/status vocabularies remain gaps. The legal-entity slice adds
  the five-type catalog and the nullable issuing-entity assignment (M-43); the
  NAIC/SAP company codes, LEI, tax id, functional currency, parent, effective
  dates, organization-unit/capacity links, the entity update/retire commands,
  and the LE-01 bind-time issuer gate remain gaps.
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
  the four financial components, derived balance, DRAFT/ISSUED/SETTLED, the
  13-type line detail with bucket reconciliation, and the settled reference);
  the AGREED/DISPUTED/SUPERSEDED statuses and the `/accounts` path remain gaps
  (M-29).
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
  `dueDate`, `authority`, SAP postings, requests, batches, reconciliations, or
  escheatment. The implemented source link
  (`sourceType`/`sourceId`/`sourceReference`) is a flat denormalized reference,
  not the SPEC 11.7.4 `claim_vertical`/`claim_id`/`claim_number` projection, and
  there is no referential-integrity check that `sourceId` exists in the source
  vertical (M-24). `sourceReference` is stored on the payment so lists and
  record views can render and link the source without an N+1 lookup. The list
  also accepts a complete `sourceType` + `sourceId` pair to return the payments
  linked to one source; that filter is documented in `openapi/payment.yaml`
  1.3.0 and M-24. The generic lifecycle command is implemented at
  `PATCH /api/v1/payments/{paymentId}/status` (M-46); the projection returns
  the latest `statusReason`, but there is no status history and the `/history`
  read remains planned.
- Notifications: no `category`, `severity`, typed `subject` reference,
  `requiresAction`, `dueAt`, `actions[]`, inbox, read/acknowledge, stream,
  subscriptions, preferences, or admin surfaces. The implemented flat source
  link (`sourceType`/`sourceId`/`sourceReference`) carries the subject
  correlation, but it is not the SPEC 11.8.4 `subject_*` projection and has no
  existence check against the source vertical (M-13, M-53).
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
| Policy legal entity `code` / `name` | `legal_entity.entity_code` (varchar 16) / `legal_name` (varchar 300) |
| Policy legal entity `jurisdiction` | `legal_entity.domicile_country` (ISO 3166-1 char 3) |
| Contract `sharePct`, `signedLinePct`, `cessionPct` | percentages of 100 (`15.000000`), not the SPEC 12.2 fraction |
| Payment `sourceType` + `sourceId` + `sourceReference` | Payment `claim_vertical` + `claim_id` + `claim_number` (or the contract link) |
| Notification `sourceType` + `sourceId` + `sourceReference` | Notification `subject_vertical` + `subject_type` + `subject_id` + `subject_business_key` / `subject` EntityRef |

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
| Party | `party.party.created`, `party.party.updated`, `party.party.identifier-added`, `party.party.identifier-updated`, `party.party.identifier-deleted`, `party.party.address-added`, `party.party.address-updated`, `party.party.address-deleted` | `repos/eia-party-expert/.../PartyEvents.java` |
| Policy | `policy.policy.created`, `policy.policy.updated`, `policy.policy.version-issued`, `policy.policy.endorsed`, `policy.policy.cancelled`, `policy.policy.reinstated`, `policy.policy.renewed`, `policy.policy.premium-audited`, `policy.policy.rated`, `policy.billing-plan.created`, `policy.billing-plan.adjusted`, `policy.installment.paid`, `policy.installment.waived`, `policy.dunning.sent`, `policy.mass-tort-profile.updated`, `policy.program.created`, `policy.policy.program-assigned`, `policy.credit-note.created`, `policy.credit-note.issued`, `policy.credit-note.applied`, `policy.credit-note.cancelled`, `policy.credit-note.reversed`, `policy.legal-entity.created`, `policy.policy.legal-entity-assigned`, `policy.submission.created`, `policy.submission.status-changed`, `policy.submission.converted` | `repos/eia-policy-expert/.../PolicyEvents.java` |
| Contract | `contract.contract.created`, `contract.contract.updated`, `contract.contract.bound`, `contract.contract.commuted`, `contract.cession.recorded`, `contract.technical-account.created`, `contract.technical-account.issued`, `contract.technical-account.settled`, `contract.technical-account.line-added`, `contract.technical-account.line-removed`, `contract.bordereau.received`, `contract.bordereau.processed`, `contract.bordereau.failed`, `contract.cash-call.requested`, `contract.cash-call.issued`, `contract.cash-call.settled`, `contract.cash-call.cancelled`, `contract.security.recorded`, `contract.security.status-changed` | `repos/eia-contract-expert/.../ContractEvents.java` |
| Direct Claims | `direct.claim.registered`, `direct.claim.updated`, `direct.claim.assigned`, `direct.claim.coverage-assessed`, `direct.claim.reserve-changed`, `direct.claim.settlement-authorized`, `direct.claim.settlement-payment-linked`, `direct.claim.closed`, `direct.claim.task-created`, `direct.claim.task-completed`, `direct.claim.task-updated`, `direct.claim.note-added`, `direct.claim.allocation-created` | `repos/eia-direct-claims-expert/.../ClaimEvents.java` |
| Assumed Claims | `assumed.claim.registered`, `assumed.claim.updated`, `assumed.claim.assigned`, `assumed.claim.closed`, `assumed.claim.reopened`, `assumed.claim.loss-advice-posted`, `assumed.claim.reserve-changed`, `assumed.claim.cash-call-requested`, `assumed.claim.recovery-recorded`, `assumed.claim.commuted`, `assumed.claim.task-created`, `assumed.claim.task-completed`, `assumed.claim.task-updated`, `assumed.claim.note-added` | `repos/eia-assumed-claims-expert/.../AssumedClaimEvents.java` |
| Cession | `cession.cession.created`, `cession.cession.updated`, `cession.cession.handed-off` | `repos/eia-cession-expert/.../CessionEvents.java` |
| Retrocession | `retrocession.retrocession.created`, `retrocession.retrocession.updated`, `retrocession.retrocession.handed-off` | `repos/eia-retrocession-expert/.../RetrocessionEvents.java` |
| Document | `document.document.created`, `document.document.updated`, `document.document.status-changed`, `document.link.added`, `document.link.removed`, `document.content.uploaded`, `document.content.deleted`, `document.legal-hold.placed`, `document.legal-hold.released`, `document.document.disposed` | `repos/eia-document-expert/.../DocumentEvents.java`, `DocumentLinkEvents.java`, `DocumentContentEvents.java` |
| Payment | `payment.payment.created`, `payment.payment.updated`, `payment.payment.status-changed`, `payment.allocation.created`, `payment.allocation.reversed` | `repos/eia-payment-expert/.../PaymentEvents.java` |
| Notifications | `notifications.notification.created`, `notifications.notification.sent` | `repos/eia-notifications-expert/.../NotificationEvents.java` |

The Payment `payment.payment.created` payload now also carries the optional
`sourceType`, `sourceId`, and `sourceReference` fields in its `data` object.
They are additive: `eventVersion` stays 1, the fields are absent or null on an
unlinked payment, and `payment.payment.updated` and `.status-changed` keep their
existing identity-only payloads.

The two implemented notification facts
`notifications.notification.created` and `notifications.notification.sent` now
carry the optional notification source link (`sourceType`, `sourceId`,
`sourceReference`) in their `data` object. The expert emits each present member
and omits all three for an unlinked notification, so the payload change is
additive and `eventVersion` stays 1 (M-53).

The two allocation facts are child-aggregate events.
`PaymentEvents.allocationCreated` writes `payment.allocation.created` against
the allocation id at version 1, with the parent payment identity, the allocation
fields, and the net `totalAllocated`/`paymentAmount` totals.
`PaymentEvents.allocationReversed` writes `payment.allocation.reversed` against
the same allocation id at version 2, with the parent payment, the allocation
fields, the released amount, the required reason, and the reversal instant.
Neither bumps the payment row version, and a repeat reversal writes no event.
Both names have no SPEC 11.7.10 equivalent (M-22, M-35).

The six Party reference-data facts are child facts of the Party aggregate.
`PartyEvents.identifierAdded` and `PartyEvents.addressAdded` write one outbox
row per appended child in the same transaction as the child insert and the
Party row version bump, keyed by the party id at the bumped aggregate version,
with the child id, the normalized values, and the actor and instant in the
payload. `PartyEvents.identifierUpdated` and `PartyEvents.addressUpdated` write
one row per real replacement in the same transaction as the child update and
bump, with the ordered `changedFields` list and the `from`/`to` snapshots; a
replacement whose normalized values equal the stored values writes no row and
does not bump the Party. `PartyEvents.identifierDeleted` and
`PartyEvents.addressDeleted` write one row per hard delete in the same
transaction as the row delete and bump, with the last stored snapshot and the
original `createdBy`/`createdAt`; a repeated delete is 404 and writes nothing.
The payload `version` is the bumped Party row version and the envelope
`aggregateVersion` is that value plus one, matching the existing Party
convention. The six names have no SPEC 11.1.9 equivalent (M-22, M-54, M-58).

The Document expert's link writes append `document.link.added` or
`document.link.removed` from `DocumentLinkEvents.java` in the same transaction
as the link row. Both use the `DocumentLink` aggregate with the link id and
version 1; the three document metadata events are unchanged. A content upload
appends `document.content.uploaded` from `DocumentContentEvents.java` in the
same transaction as the revision row, keyed by the `DocumentContent` aggregate
on the document id with the content revision as the aggregate version; the
payload repeats that revision as `version` while `eventVersion` stays 1. A
content tombstone (the standalone `DELETE .../content` or a disposition of live
content) appends `document.content.deleted` from the same factory in
the same transaction as the byte clear, keyed by the `DocumentContent` aggregate
on the document id at the revision it tombstoned, with
`{documentId, documentNumber, fileName, sizeBytes, sha256, deletedAt}` and
`eventVersion` 1. A hold,
release, or disposition appends `document.legal-hold.placed`,
`document.legal-hold.released`, or `document.document.disposed` from
`DocumentEvents.java` in the same transaction as the row update, with the
`Document` aggregate at the row version + 1 and the reason plus resulting status
in the payload. A disposition of a document with live content writes both its
disposed fact and the content tombstone fact. The two legal-hold names are new;
the disposed name is the SPEC 11.6.9 name (M-22, M-44, M-47).

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

The five credit-note facts are policy-level commands:
`PolicyEvents.creditNoteCreated` writes `policy.credit-note.created` with the
policy and note identity, note number, amount, currency, status DRAFT,
`createdAt`, and, for a return-premium note, the optional `cancellationId` and
`cancellationNumber`; `PolicyEvents.creditNoteStatusChanged` picks
`policy.credit-note.issued`, `.applied`, or `.cancelled` from the new status and
builds the payload from the policy identity and number, the credit-note identity
and number, the amount as a decimal string, the currency, and the status;
`PolicyEvents.creditNoteReversed` writes `policy.credit-note.reversed` with the
note identity and number, the nullable installment that received the original
credit, the amount, the required reversal reason, and status REVERSED. Creating
the DRAFT note and every accepted transition bump the policy row version, so
every event is distinct. SPEC 11.2.13 publishes only
`policy.billing.credit-note-issued` and defines no created, applied, cancelled,
or reversed fact (M-22, M-41).

The two legal-entity facts are catalog and policy commands:
`PolicyEvents.legalEntityCreated` writes `policy.legal-entity.created` against
the `LegalEntity` aggregate at version 1, with the legal entity id as the
partition key and the full catalog row (including the nullable regulator and
license number) in the payload. `PolicyEvents.legalEntityAssigned` writes
`policy.policy.legal-entity-assigned` against the policy aggregate at the new
version, with the new and previous entity ids (either may be null) and
`changedFields: [legalEntityId]`. Both are inserted in the same transaction as
the row change; the names have no SPEC 11.2.9 equivalent (M-22, M-43).

The three underwriting-submission facts are facts of their own aggregate.
`PolicyEvents.submissionCreated` writes `policy.submission.created` against the
`UnderwritingSubmission` aggregate at version 1, with the submission id as the
partition key and the intake facts in the payload (number, applicant, product,
requested term/limit/currency, tort codes, notes, `RECEIVED` status, version 0,
and timestamps). `PolicyEvents.submissionStatusChanged` writes
`policy.submission.status-changed` at the new submission version + 1, with the
previous and new status, version, `updatedAt`, and the optional reason; the
reason is event-only because the row has no history. `PolicyEvents
.submissionConverted` writes `policy.submission.converted` at the
post-conversion submission version + 1, with exactly `submissionId`,
`submissionNumber`, `policyId`, and `policyNumber`; the same transaction also
inserts the normal `policy.policy.created` for the new policy. All three are
inserted in the same transaction as the row change, so a rejected or concurrent
transition writes nothing, and a conversion replay writes no event at all. The
names replace the SPEC 11.2.9 `policy.submission.received` and
`policy.submission.declined` pair, add a status fact SPEC does not define, and
add a conversion fact with no SPEC name (M-22, M-59, M-60).

The settlement-payment-linked fact is a claim state change:
`ClaimEvents.settlementPaymentLinked` writes
`direct.claim.settlement-payment-linked` with the claim identity and version
context, the settlement id and number, and the nullable `paymentId`/`linkedAt`;
an unlink omits both members. It is written in the same transaction as the
settlement link update and the claim version bump, while a repeated link and a
non-linkable settlement write nothing. The name has no SPEC 11.4.9 equivalent
(M-22, M-45).

The Contract expert's generic status command can additionally emit the
already-cataloged `contract.contract.signed`, `.endorsed`, `.expired`, and
`.cancelled` names when the target status matches. Those names remain published
and are not part of the implemented subset recorded in this change; the catalog
declares only the nineteen Contract events listed above. The three
technical-account lifecycle facts are child-aggregate events: the envelope uses
the account id and its lifecycle version (1 for created, 2 for issued, 3 for
settled) while the outbox partition key stays the contract id. The two line
facts are grandchild events: the envelope uses the line id and aggregate
version 1, while the partition key stays the contract id; they carry only the
contract, account, and line identity, the line type, and the amount. All five
have no SPEC 11.3.9 equivalent (M-22, M-29, M-42). The three bordereau facts are also
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
`updatedAt`. None carries `createdBy` or `updatedBy`, except the Party
identifier and address child projections, which return the stored `createdBy`
(`system` in the current slice) and no `updatedBy` (M-54). SPEC 7.10 requires
actor attribution in the audit record, which the services keep in their audit
tables and not in the resource projection. The shared `AuditFields` component therefore
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
| Party | `party.party.identifier-added` / `.identifier-updated` / `.identifier-deleted` / `party.party.address-added` / `.address-updated` / `.address-deleted`; `party.party.updated` for a status change | No SPEC 11.1.9 name for the reference-data facts: SPEC publishes the party lifecycle, role, screening, and consent facts but no fact for an added, replaced, or deleted identifier or address, so all six names are new (M-54, M-58). `created` and `updated` match SPEC. A status change reuses the generic `party.party.updated` name with `changedFields: [status]` instead of publishing SPEC 11.1.9's dedicated `party.party.status-changed`, which remains planned; `party.party.status-updated` is not an emitted name (M-55). |
| Policy | `policy.policy.created` / `.updated`; `policy.billing-plan.created` / `.adjusted`; `policy.installment.paid` / `.waived`; `policy.dunning.sent`; `policy.program.created` / `policy.policy.program-assigned`; `policy.credit-note.created` / `.issued` / `.applied` / `.cancelled` / `.reversed`; `policy.legal-entity.created` / `policy.policy.legal-entity-assigned`; `policy.policy.premium-audited`; `policy.policy.rated`; `policy.submission.created` / `policy.submission.status-changed` / `policy.submission.converted` | No SPEC name for created/updated: SPEC 11.2.9 starts at `policy.policy.quoted`. The billing plan name differs from SPEC 11.2.13 `policy.billing.plan-created`; the installment facts have no SPEC name; the positive premium adjustment fact has no SPEC 11.2.13 name either (M-51); the dunning fact differs from SPEC 11.2.13 `policy.billing.dunning-changed`; the two program facts have no SPEC name because SPEC defines no program create or policy-assignment event. SPEC 11.2.13 publishes only `policy.billing.credit-note-issued` and defines no created, applied, cancelled, or reversed fact, so all five credit-note names are new (M-41). The two legal-entity facts are new because SPEC 10.11.2/11.2.16 define the model and link but SPEC 11.2.9 names no catalog-create or assignment event (M-43). The premium-audit fact differs from SPEC 11.2.9 `policy.premium.audited`, which remains planned (M-50). The rating fact has no SPEC 11.2.9 or 11.2.14 equivalent: SPEC models rating under a submission-scoped worksheet and publishes no rating event, so the policy-scoped name is new (M-57). The three submission facts are new as well: SPEC 11.2.9 publishes `policy.submission.received` and `policy.submission.declined` but no status-change or conversion fact, and the implemented graph/conversion are separate commands rather than SPEC 11.2.14's clearance/rating/referral/quote chain (M-59, M-60). `version-issued`, `endorsed`, `cancelled`, `reinstated`, `renewed`, and `mass-tort-profile.updated` match SPEC. |
| Contract | `contract.contract.updated`; `contract.technical-account.created` / `.issued` / `.settled`; `contract.bordereau.processed` / `.failed`; `contract.security.status-changed` | No SPEC name for updated, the technical-account facts, the two terminal bordereau facts, or the security status fact: SPEC 11.3.9 lists lifecycle verbs, the contract-level `contract.account.issued` / `.agreed` facts, `contract.bordereau.posted` / `.rejected`, and only the `contract.security.recorded` / `.breached` security facts. `created`, `bound`, `commuted`, `cession.recorded`, `contract.bordereau.received`, and `contract.security.recorded` match SPEC. |
| Direct Claims | `direct.claim.task-created` / `.task-completed` / `.task-updated` / `.note-added`; `direct.claim.assigned`; `direct.claim.allocation-created`; `direct.claim.settlement-payment-linked`; `direct.claim.litigation-created` | No SPEC names: SPEC 11.4.9 defines no assignment, task, note, allocation-created, settlement-payment-link, or matter-creation event; it names the allocation fact `direct.claim.allocated`, which remains planned, and models the settlement `payment_id` only as a Payment projection (M-45). SPEC 11.4.4 also defines no litigation damages pair (M-52). `registered`, `updated`, `coverage-assessed`, `reserve-changed`, `litigation-updated`, `settlement-authorized`, and `closed` match SPEC. |
| Assumed Claims | `assumed.claim.updated`; `assumed.claim.assigned`; `assumed.claim.task-created` / `.task-completed` / `.task-updated` / `.note-added` | No SPEC names: SPEC 11.5.9 lists lifecycle verbs only and defines no assignment, task, or note event. `registered`, `closed`, `reopened`, `loss-advice-posted`, `reserve-changed`, `cash-call-requested`, `recovery-recorded`, and `commuted` match SPEC. |
| Cession | `cession.cession.created` / `.updated` / `.handed-off` | `cession.case.created`, `cession.handoff.sent`/`.acknowledged` |
| Retrocession | `retrocession.retrocession.created` / `.updated` / `.handed-off` | `retrocession.case.created`, `retrocession.handoff.sent`/`.acknowledged` |
| Document | `document.document.created` / `.updated` / `.status-changed`; `document.link.added` / `.removed`; `document.content.uploaded` / `.deleted`; `document.legal-hold.placed` / `.released` | `document.document.registered`, `document.document.associated`, plus the SPEC lifecycle verbs; no SPEC content-upload or content-tombstone fact (SPEC 11.6.8 deletes content only inside the approved disposition job, whose deletion step the disposition now performs without its approval or certificate); the SPEC hold facts are `document.document.held` / `.hold-released`. `document.document.disposed` matches SPEC and is implemented. |
| Payment | `payment.payment.updated` / `.status-changed`; `payment.allocation.created` / `.reversed` | the SPEC per-verb names such as `payment.payment.authorized`; SPEC 11.7.10 publishes no allocation fact, so both allocation names are new (M-35) |
| Notifications | `notifications.notification.created` / `.sent`; `notifications.template.created` / `.approved` / `.retired` | `notifications.notification.issued` / `.delivered`; SPEC 11.8.9 publishes no template fact, so all three template names are new (M-49) |

The catalog lists both sets and marks only the implemented ones. The names
without a SPEC equivalent are additive under EV-05: the catalog now publishes
them and records them in the implemented subset. Publishing a SPEC name in
addition to the implemented name is additive; renaming or removing an
implemented name is breaking and needs the EV-05 dual-publish window.

Evidence:

- `repos/eia-party-expert/.../PartyEvents.java:25-32,70-207` (reference-data
  names, update snapshots, delete snapshots, and aggregate version)
- `repos/eia-policy-expert/.../PolicyEvents.java:37-56,62-64,98-420` (policy,
  billing, dunning, mass tort, program, credit-note creation,
  credit-note-transition, premium-audit, rating, submission, and conversion
  names)
- `repos/eia-contract-expert/.../ContractEvents.java:41-56`
- `repos/eia-direct-claims-expert/.../ClaimEvents.java:62-74`
- `repos/eia-assumed-claims-expert/.../AssumedClaimEvents.java:52-65`
- `repos/eia-cession-expert/.../CessionEvents.java:27-29`
- `repos/eia-retrocession-expert/.../RetrocessionEvents.java:28-30`
- `repos/eia-document-expert/.../DocumentEvents.java:29-40`
- `repos/eia-document-expert/.../DocumentLinkEvents.java:26-28`
- `repos/eia-document-expert/.../DocumentContentEvents.java:26-27`
- `repos/eia-payment-expert/.../PaymentEvents.java:31-39,103-190`
- `repos/eia-notifications-expert/.../NotificationEvents.java:36-37`
- `repos/eia-notifications-expert/.../NotificationTemplateEvents.java:26-28,80-91`

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
- The generic status command (`PATCH /api/v1/payments/{paymentId}/status`,
  M-46) does not change the source link: the implemented API still has no
  command that adds or edits a source after create.

Evidence:

- `repos/eia-payment-domain/.../PaymentRules.java:110-137` and
  `repos/eia-payment-expert/.../PaymentRules.java:147-175`
  (`validateSourceLinkage`); the expert constants are at `:39-45`
  (`SOURCE_TYPES`, `SOURCE_REFERENCE_MAX_LENGTH`).
- `repos/eia-payment-expert/.../CreatePaymentRequest.java:19-21` and
  `Payment.java:27-29`; `repos/eia-payment-domain/.../PaymentDto.java:24-26`
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
| Adjust plan | `POST /api/v1/policies/{policyId}/billing/adjustment` | No API row; a premium change is a credit note or additional invoice (BIL-05) |
| Settle installment | `PATCH /api/v1/policies/{policyId}/billing/installments/{installmentId}` | No API row; billing instructions carry the status |
| Receivable queue | `GET /api/v1/billing/installments` (tenant-wide, outside `/api/v1/policies`) | No API row; SPEC 11.2.13 defines the per-policy plan, not a cross-policy receivable read |
| Dunning | `GET/POST /api/v1/billing/installments/{installmentId}/dunning` (per installment, outside `/api/v1/policies`) | No public API row; the only dunning command is the internal `POST /internal/v1/policies/{id}/dunning-status` |
| Plan event | `policy.billing-plan.created` | `policy.billing.plan-created` |
| Installment events | `policy.installment.paid`, `policy.installment.waived` | No SPEC name |
| Adjustment event | `policy.billing-plan.adjusted` | No SPEC name |
| Dunning event | `policy.dunning.sent` | `policy.billing.dunning-changed` |
| Plan status | `ACTIVE`, `COMPLETE`, `CANCELLED` | `DRAFT`, `ACTIVE`, `SUPERSEDED`, `CANCELLED` |
| Installment status | `DUE`, `OVERDUE`, `PAID`, `WAIVED`, `CREDITED` | Billing-instruction status values |
| Credit application | APPLIED credit note requires an `installmentId`; credits the note amount to a DUE/OVERDUE installment on the same tenant and policy. A partial credit raises `creditedAmount` and leaves the row open; a credit that covers the uncredited remainder sets the new terminal status `CREDITED`. A missing id is 400 `INVALID_CREDIT_NOTE_INSTALLMENT`, an unknown/foreign installment is 404 `INSTALLMENT_NOT_FOUND`, a settled or fully credited target is 409 `INSTALLMENT_NOT_CREDITABLE`, and an oversized note is 409 `CREDIT_NOTE_EXCEEDS_INSTALLMENT` | `credit_note_request` has no installment column and no APPLIED state; `BIL-06` defines only `outstanding = invoiced - paid - credited` and the non-negative rule, with no application command |
| Credit reversal | APPLIED -> REVERSED with a required 1-500 character reason. Releases the note amount from the installment recorded at application time, clamps `creditedAmount` at zero, and reopens a fully credited row as DUE or OVERDUE when it no longer covers the gross amount; a legacy APPLIED note without an installment is only marked REVERSED. Reversing a non-APPLIED or already REVERSED note is 409 `INVALID_CREDIT_NOTE_TRANSITION`; a missing or blank reason is 400 `INVALID_CREDIT_NOTE_REASON` | No reversal command or reversal fact; `BIL-06` has no unapply rule |
| Plan summary | `totalAmount`, `paidAmount`, `waivedAmount`, `creditedAmount`, net `outstandingAmount`, `overdueAmount`, `currency`, `installmentCount` | No plan summary row; `BIL-06` defines the net outstanding formula |
| Dunning level | `REMINDER`, `FIRST_NOTICE`, `SECOND_NOTICE`, `COLLECTIONS` | `billing_account.dunning_status`: `CLEAR`, `REMINDER`, `DUNNING`, `LEGAL`, `BLOCKED`; collections flow `CURRENT -> REMINDER -> DUNNING_1 -> DUNNING_2 -> NOTICE -> CANCELLATION_PENDING -> CANCELLED` |

The projection is the domain's flat public DTO, which renames the plan identity
`planId` and the installment identity `installmentId`; the expert's internal
view nests `{plan, installments, summary}` and is not part of the public
contract. Each installment carries the gross `amount`, the applied
`creditedAmount`, and the derived `outstandingAmount`; the plan `summary` adds
the paid, waived, credited, net outstanding, and overdue totals. The public
billing routes accept an absent `X-EIA-Book` for compatibility with the other
Policy proxy routes, while a supplied value must be DIRECT and another book is
hidden as 404 `BOOK_SCOPE_VIOLATION`. The domain always sends DIRECT to the
expert.

The positive premium adjustment appends an installment for the remaining gap
between the policy written premium and the plan's net premium (its total less
applied credits, floored at zero). The amount is derived, so the command body is
only `{dueDate, reason}`; a non-positive remainder is 400
`NO_PREMIUM_ADJUSTMENT`, a missing plan is 404 `BILLING_PLAN_NOT_FOUND`, a
non-ACTIVE plan and the 24-installment ceiling are 409
`BILLING_PLAN_NOT_ACTIVE`/`MAX_INSTALLMENTS_REACHED`, and a concurrent plan
change is 409 `CONCURRENT_MODIFICATION`. The domain accepts the optional
`If-Match` and `Idempotency-Key` headers and forwards them, but the expert does
not compare the tag or replay the key, so a retry appends a second installment.
The 201 `plan` member omits the schedule, so its derived `summary` is computed
from an empty list. The route, derived-delta rule, and event name are recorded
in M-51.

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
are null on every item. A partially credited installment stays in the queue; a
fully CREDITED row does not. The public projection is the domain's
`Receivable`/`ReceivableSummary`: `{installmentId, planId, planNumber,
policyId, policyNumber, insuredPartyId, installmentNumber, dueDate, amount,
creditedAmount, outstandingAmount, currency, status, daysPastDue, paidAt,
paymentId}` inside `{items, totalAmount, overdueAmount, count}`. `amount` stays
gross, `creditedAmount` is the applied credit total, and `outstandingAmount` is
`amount - creditedAmount`; `totalAmount` and `overdueAmount` sum the outstanding
amounts, matching the SPEC `premium_receivable.credited_amount`/
`outstanding_amount` netting rule (BIL-06).

The dunning slice is a separate per-installment surface at
`/api/v1/billing/installments/{installmentId}/dunning`: it records and lists
actions instead of reading a SAP-sourced level, uses its own closed level and
channel vocabularies, and its history is keyed by installment rather than by
billing account. The route, vocabulary, book rule, and event naming are
recorded in M-38.

Evidence:

- `repos/eia-policy-domain/.../PolicyBillingController.java` (public routes and
  the `requireDirectWhenPresent` guard).
- `repos/eia-policy-domain/.../BillingPlan.java`, `BillingSummary.java`,
  `Installment.java` (flat public DTO names, credited/outstanding money, net
  summary).
- `repos/eia-policy-domain/.../ReceivableController.java`,
  `ReceivableService.java`, `Receivable.java`, `ReceivableSummary.java`
  (`/api/v1/billing/installments`, status and limit normalization, outstanding
  projection).
- `repos/eia-policy-domain/.../PolicyClient.java:379-450`
  (`/internal/v1/billing/installments` call and projection remap) and
  `:800-880` (expert summary/credit mapping).
- `repos/eia-policy-expert/.../BillingController.java`,
  `BillingRules.java`, `BillingPlanSummary.java`, `PolicyEvents.java` (route,
  vocabulary, summary derivation, event names).
- `repos/eia-policy-expert/.../BillingReceivablesController.java`,
  `BillingService.java:75-102`, `BillingRepository.java:155-194`,
  `BillingRules.java:99-140`, `InstallmentReceivable.java`,
  `ReceivablesView.java` (tenant-wide query, derived status, outstanding
  totals).
- `repos/eia-policy-expert/.../CreditNoteRules.java:104-158`,
  `CreditNoteService.java:97-154`, and `BillingRepository.java:232-270`
  (installment credit application, CREDITED transition, conditional update).
- `repos/eia-policy-domain/.../BillingAdjustmentCommand.java`,
  `BillingAdjustmentResult.java`, and `PolicyBillingService.java:32-44`
  (derived-delta command and optional header forwarding).
- `repos/eia-policy-expert/.../BillingRules.java:76-174`,
  `BillingService.java:151-211`, `BillingRepository.java:124-164`, and
  `PolicyEvents.java:100-125` (ACTIVE and 24-installment gates, delta, plan
  update, appended installment, and adjusted event).
- `repos/eia-policy-expert/src/main/resources/schema.sql:388-435,503-537`
  (plan and installment status checks, `credited_amount` and its
  non-negative/bounded check).

Resolution: either amend SPEC 11.2.13 to the implemented `/billing`,
`/billing/installments/{installmentId}/dunning`, and cross-policy
`/api/v1/billing/installments` routes, flat projections, event names, and
status/level vocabularies, or add the SPEC route and names as aliases with an
EV-05 dual-publish window. The billing account, instruction, dispute, and
commission-statement routes remain unimplemented (M-12); the receivable queue
and the dunning history are implemented as above, and policy credit notes are
implemented as a separate child resource recorded in M-41. Credit application
targets an installment that is not a SPEC billing entity and defines a
CREDITED terminal state the SPEC does not name; it is the part of the credit
note slice that most closely follows BIL-06, because the persisted credited
total can never exceed the gross amount and the net outstanding amount can
never go negative. The positive premium adjustment route, derived-delta rule,
and event name are recorded in M-51.

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
| Settlement | A `SETTLED` status PATCH requires a `reference` that the expert trims, requires non-blank, and caps at 120 characters (400 `INVALID_REFERENCE`); the account projection carries the required-but-nullable `settlementReference`, null until SETTLED | The reference is free text only: there is no Payment link, cash-call link, or settlement amount/date evidence. `ISSUED` silently ignores a supplied reference rather than rejecting it. |
| Lines | `GET/POST .../{accountId}/lines` and `DELETE .../lines/{lineId}` expose the SPEC `technical_account_line` detail with the 13-type vocabulary (`PREMIUM`, `COMMISSION`, `BROKERAGE`, `PAID_LOSS`, `OUTSTANDING_LOSS`, `IBNR`, `ALAE`, `REINSTATEMENT`, `CASH_CALL`, `FUNDS_WITHHELD`, `TAX`, `ADJUSTMENT`, `OTHER`); lines are editable only in DRAFT and must reconcile by the four buckets before issue (M-42) | A line update, a per-line currency, a source-document link, and per-line approval remain gaps (M-42). The account header is still one row with `cededPremium`, `cededLosses`, `commission`, `otherCharges`, and a derived `balance`, and the cash-call/settlement linkage is absent. |
| Period | `periodStart < periodEnd`; unique exact `(tenant, contract, periodStart, periodEnd)` | There is no overlap rejection (CTR-07) and no contract-window or contract-currency equality check (CTR-08). The unique key catches only an identical period, so two overlapping but non-identical periods are accepted. |
| Book | `X-EIA-Book: ASSUMED` when present; another book is 404 `BOOK_SCOPE_VIOLATION` | The canonical contract requires the header, but the domain accepts an absent header for compatibility with the other Contract proxy routes (`requireAssumedBookWhenPresent`). The expert internal alias does not check the book at all. |
| Events | `contract.technical-account.created`, `.issued`, `.settled`, `.line-added`, `.line-removed` | SPEC 11.3.9 defines `contract.account.issued` and `contract.account.agreed`; the implemented names have no SPEC equivalent (M-22). The account envelope uses the account id and lifecycle version 1/2/3, and each line event uses the line id at version 1, while the outbox partition key stays the contract id (M-42). The settled account payload carries `settlementReference`; `created` and `issued` omit it. |
| Balance | Derived at create as `cededPremium - commission - cededLosses + otherCharges`; positive means due from the cedent to the reinsurer | The balance is not reconciled against paid losses, cash calls, or the recorded settlement reference, and there is no accounting line or payment link. |

The 2026-10-21 settlement-reference slice documents an already implemented
extension: the expert requires a trimmed, non-blank reference of at most 120
characters on SETTLED, persists it on the account, returns it as
`settlementReference`, and adds it to the settled event only. It adds no
Payment or cash-call linkage and no settlement amount or date evidence.

Evidence:

- `repos/eia-contract-domain/.../TechnicalAccountController.java:56-77`
  (the status route and the book wall, which runs only when the header is
  present) and `TechnicalAccountClient.java:84-121` (tenant and ASSUMED
  forwarding, and dropping a reference on a non-settled transition),
  `TechnicalAccount.java:12-38` (`@JsonAlias("id")` remap, the flat projection,
  and `settlementReference`), and
  `UpdateTechnicalAccountStatusCommand.java:5-22` (the optional `reference`);
  `ContractCommandRules.java:248-250` validates only the status, so the
  reference bounds stay in the expert.
- `repos/eia-contract-expert/.../technicalaccount/TechnicalAccountController.java:123-171`
  (public and internal prefixes, tenant resolution, create and status flow,
  the reference gate, and the transactional outbox).
- `repos/eia-contract-expert/.../technicalaccount/TechnicalAccountRules.java:15,83-96`
  (the 120-character settlement reference and its SETTLED-only requirement),
  `UpdateTechnicalAccountStatusRequest.java:3-18` (the settlement-reference
  contract), and `TechnicalAccountRepository.java:126-145` (compare-and-set
  status with the reference written only on SETTLED).
- `repos/eia-contract-expert/.../technicalaccount/TechnicalAccountStatus.java:11-22`
  (DRAFT/ISSUED/SETTLED only).
- `repos/eia-contract-expert/.../technicalaccount/TechnicalAccountRepository.java:49-114`
  (newest-first list and unique-period conflict).
- `repos/eia-contract-expert/src/main/resources/schema.sql:441-475`
  (unique exact period, non-negative amounts, currency pattern, status check,
  the `settlement_reference VARCHAR(120)` column, and its forward ALTER).
- `repos/eia-contract-expert/.../ContractEvents.java:69-71,225-239,480-519`
  (account fact names, child-aggregate id/version, contract partition key, and
  the settled-only `settlementReference` payload member) and
  `:72-73,247-260,521-544` (the line fact names, the add/remove factories, the
  aggregate type, version 1, and the shared line payload).
- `repos/eia-contract-expert/.../technicalaccount/TechnicalAccountLineController.java:44-129`
  (list/add/remove, tenant and book context, DRAFT guard, per-mutation outbox),
  `TechnicalAccountLineRules.java:77-151` (detailed totals, four-bucket
  roll-up, text bounds, and the bucket issue reconciliation),
  `TechnicalAccountLineRepository.java:49-103` (insertion-order reads,
  tenant/account scoping, delete, and grouped totals),
  `TechnicalAccountLineType.java:15-86` (the 13 detail types, their buckets,
  and header fields), and
  `TechnicalAccountLinesDoNotReconcileException.java:17-33` (one conflict with
  a per-bucket mismatch detail list).
- `repos/eia-contract-domain/.../TechnicalAccountLineController.java:28-79`
  (public paths, required tenant, optional ASSUMED book guard),
  `TechnicalAccountLineClient.java:109-245` (expert call, `lines` -> `items`
  normalization, `bucketTotals` preference, totals mapping),
  `TechnicalAccountLineTypes.java:19-85` (13 types and bucket mapping),
  `TechnicalAccountLine.java:23-31` (`id` -> `lineId` alias), and
  `LineSummary.java:31-92`.
- `repos/eia-contract-expert/src/main/resources/schema.sql:477-521`
  (`contract_technical_account_line`, the 13-type check, the `LOSS` migration,
  the positive amount, the account cascade, and the read index).
- Tests: `TechnicalAccountControllerTest` (settled with and without a
  reference, trimming, the 120-character boundary, and the ignored issue
  reference), `TechnicalAccountOutboxIntegrationTest`
  (`settlementReferenceIsRequiredTrimmedAndLengthChecked`),
  `TechnicalAccountClientTest` (reference forwarding and the dropped
  non-settled reference), and the domain `TechnicalAccountControllerTest`
  (the settlement projection).
- `openapi/contract.yaml` (introduced in 2.2.0, now 4.5.0),
  `asyncapi/contract.yaml` (now 1.10.0), and the README technical-account,
  technical-account-line, and settlement-reference sections record the
  implemented shape.

Resolution: the implemented slice is documented as canonical for now. Closing
the gap means adding the SPEC `/accounts` alias (or amending SPEC 11.3.10),
implementing the AGREED/DISPUTED/SUPERSEDED transitions, and enforcing period
overlap plus the contract window and currency equality. The line slice now
implements the 13-type SPEC 11.3.4 detail vocabulary and bucket reconciliation;
M-42 records the remaining correction, per-line metadata, and approval gaps. The
settlement reference is free-text evidence; linking it to a Payment record and
adding settlement amount and date evidence remains part of the gap. The
event names follow EV-05:
keep publishing the implemented names and add a SPEC name only through a
dual-publish window. Renaming the path or statuses is breaking and needs an ADR
and a `/v2` or dual-mount period.

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
| Projection | Flat `{cashCallId, callNumber, contractId, periodStart, periodEnd, amount, currency, dueDate, status, settlementReference, notes, createdAt}`; `settlementReference` is null until SETTLED and then holds the trimmed payment reference, the expert row id is remapped to `cashCallId`, and `tenantId` is not exposed | No claim link, Payment link, cash-call limit/remaining amount, contract-period relation, or settlement amount/date evidence beyond the free-text reference. |
| Status | `REQUESTED`, `ISSUED`, `SETTLED`, `CANCELLED`; only `REQUESTED -> ISSUED -> SETTLED` or `REQUESTED -> CANCELLED` | SPEC names no cash-call status vocabulary. `REQUESTED` as a target is 400 `INVALID_STATUS`; a skipped or repeated edge is 409 `INVALID_STATUS_TRANSITION`. |
| Gate | `periodStart < periodEnd`, `amount > 0`, uppercase ISO 4217 currency, required `dueDate`, notes at most 4000 characters, and a SETTLED `reference` that is trimmed, non-blank, and at most 120 characters (400 `INVALID_REFERENCE`; ISSUED and CANCELLED ignore it) | No `cash_call_allowed` or `cash_call_limit_amount` term check, no large-loss-above-cash-loss-limit authorization, and no contract-window or contract-currency equality check. |
| Events | `contract.cash-call.requested`, `.issued`, `.settled`, `.cancelled` | SPEC 11.3.9 publishes only `.issued`; the other three are new child-aggregate facts (M-22). The envelope uses the cash-call id and aggregate version 1/2/3 while the outbox partition key stays the contract id. The settled payload carries `settlementReference`; the other three omit it. |
| Book | Canonical contract requires `X-EIA-Book: ASSUMED`; another book is 404 `BOOK_SCOPE_VIOLATION` | The domain's `requireAssumedBookWhenPresent` accepts an absent header, and the expert's `/internal/v1` alias checks no book at all (M-08). |

The 2026-10-21 settlement-reference slice documents an already implemented
extension: the expert requires a trimmed, non-blank reference of at most 120
characters on SETTLED, persists it on the call, returns it as
`settlementReference`, and adds it to the settled event only. It adds no
claim/Payment linkage and no settlement amount or date evidence.

Evidence:

- `repos/eia-contract-domain/.../CashCallController.java:29-77` (public routes
  and the book wall) and `CashCallClient.java:32-118` (tenant and ASSUMED
  forwarding to the expert alias, and dropping a reference on a non-settled
  transition).
- `repos/eia-contract-domain/.../CashCall.java:23-37` (`@JsonAlias("id")` remap,
  the flat projection, and `settlementReference`),
  `UpdateCashCallStatusCommand.java:15-22` (optional `reference`), and
  `ContractCommandRules.java:299-301` (status validation; the reference bounds
  stay in the expert).
- `repos/eia-contract-expert/.../cashcall/CashCallController.java:50-160`
  (public and internal prefixes, tenant resolution, create and status flow,
  transactional outbox).
- `repos/eia-contract-expert/.../cashcall/CashCallRules.java:14-120` (period
  order, positive amount, currency, due date, notes, the 120-character
  settlement reference and its SETTLED-only requirement, status parsing, and
  the transition table), `UpdateCashCallStatusRequest.java:3-18` (the
  settlement reference contract), `CashCallStatus.java:11-37` (four statuses and
  event versions), and `CashCallRepository.java:49-118` (newest-first list,
  unique call number, compare-and-set status).
- `repos/eia-contract-expert/src/main/resources/schema.sql:524-556`
  (`contract_cash_call` columns including `settlement_reference VARCHAR(120)`,
  unique `(tenant_id, contract_id, call_number)`, period/amount/currency/status
  checks, and the forward ALTER for an existing table).
- `repos/eia-contract-expert/.../ContractEvents.java:77-80,283-309,400-402`
  (event names, child-aggregate factories, id/version, contract partition key,
  and the settled-only `settlementReference` payload member).
- `openapi/contract.yaml` (4.4.0 for this slice; now 4.5.0),
  `asyncapi/contract.yaml` (1.9.0 for this slice; now 1.10.0), and the README
  cash-call and settlement-reference sections record the implemented shape.

Resolution: the implemented slice is documented as canonical for now. Closing
the gap means adding the cash-call limit/term gate and the large-loss
authorization, enforcing the contract window and currency equality, linking the
call to the claim and the Payment settlement, and adding the SPEC route/status
names or amending SPEC 11.3.10. The three new event names need an EV-05
dual-publish window before a SPEC name is introduced; renaming the route,
statuses, or event names is breaking and needs an ADR and a `/v2` or dual-mount
period.

## M-35 Payment allocations add SPEC-less create/reverse routes and event names

SPEC 11.7.11 lists only `GET
/api/v1/payment/payments/{paymentId}/allocations`; it defines no allocation
create or reversal operation. SPEC 11.7.10 publishes no allocation event. The
2026-10-20 slice implements a standalone allocation child aggregate, and the
2026-10-22 slice adds its reversal:

| Area | Implemented | SPEC / gap |
|---|---|---|
| Routes | `GET/POST /api/v1/payments/{paymentId}/allocations` and `POST /api/v1/payments/{paymentId}/allocations/{allocationId}/reverse` (the M-01 short form) | SPEC 11.7.11 lists only the GET, under the longer `/api/v1/payment/payments` base, and defines no reverse route. |
| Projection | `PaymentAllocation` `{allocationId, paymentId, targetType, targetId, component, amount, currency, createdAt, reversedAt, reversalReason}` and `PaymentAllocationSummary` `{items, paymentAmount, totalAllocated, reversedTotal, net, unallocated, currency}`; the expert row id is remapped to `allocationId` and `tenantId` is not exposed. `reversedAt`/`reversalReason` are null until the allocation is reversed | SPEC 11.7.4 defines `claim_id`, `policy_id`, `policy_year`, `contract_id`, `layer_id`, `reserve_component`, `gl_account`, `company_code`, `cost_center`, `profit_center`, `business_area`, `tax_code`, and `allocation_pct`; the flat `targetType`/`targetId`/`component` trio replaces those columns, and neither the summary envelope nor the reversal stamp is in SPEC. |
| Command | `CreatePaymentAllocationRequest` with `targetType` DIRECT_CLAIM/ASSUMED_CLAIM/POLICY, `targetId` UUID, `component` INDEMNITY/DEFENSE_COST/ALAE/EXPENSE/COMMISSION/OTHER, and `amount` greater than zero at numeric(19,4); the currency always comes from the payment | The target record is not resolved or validated against the Direct Claims, Assumed Claims, or Policy API; there is no policy-year, layer, contract, reserve-component, allocation-percentage, or SAP GL coding input. |
| Reversal | `ReversePaymentAllocationRequest` `{reason}`: `reason` is required, trimmed, non-blank, and at most 200 characters. The accepted call stamps `reversedAt`/`reversalReason`, keeps the append-only row and its original facts, releases the amount from the active allocated total, and answers 200 with the stamped allocation | SPEC defines no allocation reversal command, no `reversedAt`/`reversalReason`, and no `ALLOCATION_ALREADY_REVERSED` conflict. A repeat, including a concurrent repeat, is 409 with no second write and no second event; an unknown or foreign payment is 404 `PAYMENT_NOT_FOUND`, and an unknown allocation or one under another payment/tenant is 404 `ALLOCATION_NOT_FOUND`. The payment lifecycle status does not gate a reversal. |
| Totals | The expert stores the active (net) allocated total and the reversed total; the domain presents the gross `totalAllocated`, `reversedTotal`, the net `net`, and the net-based `unallocated` | The SPEC 11.7.7 PAY-06 exact-sum rule has no reversal concept, and the public gross/reversed/net split is an implementation shape. |
| Status gate | 409 `PAYMENT_NOT_ALLOCATABLE` when the payment is CANCELLED, REVERSED, or FAILED | The SPEC lifecycle names the allocatable and terminal states but defines no error code. |
| Overallocation | 409 `ALLOCATION_EXCEEDS_PAYMENT` when the active allocated total plus `amount` exceeds the payment amount; zero or partial allocations are accepted, and a reversed amount is available again | SPEC 11.7.7 PAY-06 requires at least one allocation and a total equal to the payment amount within 0.01. The implemented slice does not gate issue on an allocation or require the sum to reach the payment, and the error code is an implementation name. |
| Event | `payment.allocation.created` at allocation version 1 and `payment.allocation.reversed` at version 2. The created payload is `{paymentId, paymentNumber, targetType, targetId, component, amount, currency, totalAllocated, paymentAmount}`; the reversed payload is `{paymentId, allocationId, targetType, targetId, component, amount, reason, reversedAt}` | SPEC 11.7.10 publishes no allocation event, so both names are new (M-22). The outbox partition key stays the payment id. |
| Book | Not book-scoped; `payment_allocation` has no book column and the routes require only `X-EIA-Tenant`; the events are stamped DIRECT | SPEC 3.6.1 says every payment and allocation carries the book. The implemented payment and allocation rows carry no book (M-08, M-12). |

Evidence:

- `repos/eia-payment-domain/.../PaymentController.java:73-101` (public GET/POST
  allocation routes and the reverse POST) and `PaymentService.java:122-160`
  (proxy, command normalization, and reversal forwarding).
- `repos/eia-payment-domain/.../PaymentAllocationRules.java:29-102` (target,
  component, and amount validation), `PaymentAllocation.java:20-42`,
  `PaymentAllocationSummary.java:10-39`,
  `CreatePaymentAllocationCommand.java:11-16`, and
  `ReversePaymentAllocationCommand.java:5-18` (flat public projection and the
  reversal command).
- `repos/eia-payment-domain/.../PaymentClient.java:121-229` (expert
  `/internal/v1` calls, missing-total normalization, gross/reversed/net
  conversion, reverse call, and upstream-error translation that preserves the
  404 code).
- `repos/eia-payment-expert/.../PaymentAllocationController.java:26-66` (same
  public paths plus the internal alias, tenant resolution, 201 create, and the
  reverse POST) and `PaymentAllocationService.java:44-148` (tenant wall,
  status gate, overallocation guard, allocation insert, reversal, and outbox
  writes in one transaction).
- `repos/eia-payment-expert/.../PaymentAllocationRules.java:35-96` (closed
  target and component sets, amount normalization, non-allocatable statuses,
  and the 200-character trimmed reversal reason),
  `PaymentAllocationRepository.java:46-130` (oldest-first list, active and
  reversed totals, conditional reversal update), `PaymentAllocationItem.java:15-41`,
  and `PaymentAllocationSummary.java:10-24` (public field names).
- `repos/eia-payment-expert/.../PaymentEvents.java:31-39,103-190`
  (`payment.allocation.created` at version 1 and `payment.allocation.reversed`
  at version 2, parent payment partition key) and `schema.sql:46-77`
  (`payment_allocation` columns, the positive-amount/target/component checks,
  and the additive `reversed_at`/`reversal_reason` columns).
- Tests: `PaymentAllocationControllerTest` (list totals, create, reverse,
  internal alias, `TENANT_REQUIRED`, `VALIDATION_ERROR`, 409/404),
  `PaymentAllocationIntegrationTest` (oldest-first ordering, empty summary,
  over-allocation and status guards, tenant wall, field validation, event
  payload, rollback), `PaymentAllocationReversalIntegrationTest` (reversal,
  repeat, missing/blank/over-long reason, tenant/payment/allocation wall,
  net/reversed totals, event), `PaymentAllocationRulesTest`, and the domain
  `PaymentClientTest`/`PaymentControllerTest` reversal cases.
- `openapi/payment.yaml` 1.7.0, `asyncapi/payment.yaml` 1.4.0,
  `asyncapi/event-catalog.yaml` 1.30.0, and the README payment allocation
  sections record the implemented shape.

Resolution: the implemented slice is documented as canonical for now. Closing
the gap means adding the SPEC allocation create and reverse operations and the
`payment.allocation.created`/`payment.allocation.reversed` event names (or
recording the GET-only contract), enforcing PAY-06 (at least one allocation per
payment and the exact payment-amount sum within 0.01), resolving and validating
the target against the owning claim or policy API, adding the policy-year,
layer, contract, reserve-component, allocation-percentage, and SAP GL coding
fields, and carrying the book on the payment and allocation. A new event name
needs an EV-05 dual-publish window before it can replace a SPEC name; renaming
the route or event is breaking and needs an ADR and a `/v2` or dual-mount
period. A `paymentId` outside the caller's tenant stays 404
`PAYMENT_NOT_FOUND`, and an `allocationId` outside the payment stays 404
`ALLOCATION_NOT_FOUND`.

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
- PAID, WAIVED, and fully CREDITED installments are terminal and reject dunning
  with 409 `INSTALLMENT_NOT_DUNNABLE`; the CREDITED state is reached only by
  applying credit notes and is not a SPEC billing-account state.
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
  2000-character notes, dunnable states, and CREDITED rejection),
  `BillingDunningRepository.java:62-109`
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

## M-39 Policy program catalog is a short-path, SPEC-less create, membership, and capacity surface

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
| Capacity | optional flat `capacityAmount`/`capacityCurrency` pair (both or neither, amount greater than zero, ISO 4217 alpha-3); derived `usedAmount` (sum of the assigned policies' `limit_amount`), `utilizationPct`, and `policyCount`; no capacity-share rows | `program_version`, `program_capacity`, and the LE-02 capacity-share rules |
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
  capacity-share rows, so the LE-02 share-sum check, LE-06 versioning, and the
  program detail/capacity-share/fronting views cannot be served from it. The
  optional flat capacity pair and the derived
  `usedAmount`/`utilizationPct`/`policyCount` serve a single-program capacity
  view only.
- `usedAmount` is a bare `SUM(policy.limit_amount)` over the assigned policies:
  it does not convert or verify the policies' `limitCurrency`, filter by policy
  status, or check the sum against `capacityCurrency`, so a mixed-currency or
  cancelled-policy membership is summed as-is and `utilizationPct` can exceed
  100 without a capacity breach. The projection has no remaining-capacity or
  used-currency member.
- The canonical contract documents 400 `INVALID_PROGRAM_CAPACITY` for a partial
  capacity pair, a non-positive amount, or a malformed currency. The expert's
  `ProgramRules` returns that code for the pair and for its non-positive and
  malformed backstops, but the public domain validates the same shapes first
  and returns 400 `VALIDATION_ERROR` with `CAPACITY_AMOUNT_REQUIRED`,
  `CAPACITY_CURRENCY_REQUIRED`, `MIN_VALUE`, or `INVALID_FORMAT`, so a public
  caller does not see `INVALID_PROGRAM_CAPACITY`.
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
  `Location`), `ProgramService.java:34-64` (date-range and capacity-pair
  pre-checks), `ProgramDto.java` (capacity and usage members), and
  `CreateProgramCommand.java` (name, type, capacity amount/currency
  constraints).
- `repos/eia-policy-domain/.../PolicyProgramController.java:21-47` (public
  PATCH, optional body, ETag echo) and `PolicyProgramService.java`,
  `UpdatePolicyProgramCommand.java`.
- `repos/eia-policy-domain/.../PolicyClient.java:418-494` (`/internal/v1`
  program calls and projection remap).
- `repos/eia-policy-expert/.../PolicyProgramController.java:29-85` (public and
  internal aliases, tenant query or header, 201 create, 200 assignment with
  ETag), `PolicyProgramService.java:54-112` (number generation, ACTIVE default,
  capacity persistence, usage projection, null clear, version check and 409),
  and `ProgramRules.java:17-129` (vocabulary, name cap, date order, capacity
  validation, and utilization).
- `repos/eia-policy-expert/.../PolicyProgramRepository.java:45-114`
  (tenant-scoped reads, newest-first list, number sequence, and the grouped
  usage query) and `PolicyProgram.java`, `ProgramView.java`,
  `CreateProgramRequest.java`, `AssignPolicyProgramRequest.java`.
- `repos/eia-policy-expert/.../PolicyEvents.java:50-51,94-153`
  (`policy.program.created` against Program at version 1 and
  `policy.policy.program-assigned` against Policy with both link sides) and
  `src/main/resources/schema.sql:52-99` (`policy_program`, the
  `capacity_amount`/`capacity_currency` columns and their positive,
  three-letter, and both-or-neither CHECK constraints, the nullable
  `policy.program_id` FK, and the indexes; no FK on `lead_policy_id`).
- Tests: `ProgramControllerTest`, `PolicyProgramControllerTest`,
  `ProgramClientTest`, `PolicyProgramControllerTest`,
  `PolicyProgramServiceTest`, `PolicyProgramIntegrationTest`, and
  `ProgramRulesTest`, including the capacity-pair, positive-amount,
  currency-format, and zero/negative rejection cases and the domain's
  `VALIDATION_ERROR` field codes.
- `openapi/policy.yaml` 2.12.0 records the implemented shape, including the
  capacity pair and usage members; `asyncapi/policy.yaml` 1.9.0 and
  `asyncapi/event-catalog.yaml` 1.23.0 are unchanged because capacity is not
  published on `policy.program.created`.

Resolution: either extend SPEC 10.11.3/11.2.10 with the implemented catalog,
membership command, and event names, or align the implemented paths,
vocabulary, and projection with the SPEC master data. Until then the contract
documents the short paths, the CAPTIVE/POOL/FRONTING/COINSURANCE/MASS_TORT
vocabulary, and the optional flat capacity pair. The capacity shape also needs a
decision: keep the flat pair with the unconverted `usedAmount` sum, or adopt the
SPEC `program_capacity`/`program_version` structure with the LE-02 shares; in
either case the public domain should propagate `INVALID_PROGRAM_CAPACITY`
instead of remapping the capacity request-shape failures to
`VALIDATION_ERROR`. Separately, either resolve and tenant-check `leadPolicyId`
or remove it, add an explicit close command before exposing CLOSED as a
reachable state, and decide whether the DIRECT book header is required or
optional.

## M-40 Document content keeps a current pointer plus revisions, not the SPEC versioned store

SPEC 11.6.10 defines an authorized content download (presigned) and mounts the
content history at `GET /versions` and the version-creating command at `POST
/versions`; the SPEC 11.6 model carries content, versions, hashes, page counts,
OCR status, holds, and retention. The implemented slice stores one current
content pointer per document plus immutable revision rows, serves the bytes
through a raw-byte proxy under `/content`, exposes the history under
`/content/versions`, tombstones the bytes with a standalone `DELETE
/content` that keeps the metadata, and emits content-upload and content-delete
facts that have no SPEC 11.6.9 names. The 2026-10-22 disposition slice also
applies that tombstone from `POST .../dispose`; SPEC 11.6.8's approved job
(approval and certificate) is still not implemented (M-44, M-47).

| Aspect | Implemented | SPEC 11.6.10 / 11.6 |
|---|---|---|
| Routes | `PUT|GET|DELETE /api/v1/documents/{documentId}/content`, `GET .../content/metadata`, `GET .../content/versions`, and `GET .../content/versions/{version}` | authorized content download (presigned), `GET`/`POST .../versions`, preview, text, access log |
| Upload | raw bytes; each accepted body appends an immutable revision and advances the current pointer; a later upload after a tombstone clears the pointer tombstone and appends a fresh revision | versioned content with a history |
| Size limit | 10 MiB (10,485,760 bytes); a zero-byte body is 400 `EMPTY_CONTENT`; an over-limit body is 413 `FILE_TOO_LARGE` | no implemented limit stated |
| Metadata | `DocumentContent` with `documentId`, `fileName`, `contentType`, `sizeBytes`, `sha256`, `uploadedAt`, `currentVersion`, nullable `deletedAt`, and derived `deleted`; the metadata survives a tombstone | content, hash, page count, OCR status, tags, versions |
| Download | proxied bytes with `Content-Type`, `Content-Disposition`, `X-Content-SHA256`, and `X-Content-Version`; one revision is downloadable through `/content/versions/{version}`; tombstoned current or revision bytes are 410 `CONTENT_DELETED`; no `Range`, no presigned URL | short-lived presigned URL |
| Filename | URL-encoded `X-File-Name`, reduced to its last path component; at most 255 characters | not specified |
| Versioning | append-only `document_content_version` rows; revisions start at 1 and the history is newest first; every upload appends one revision and advances `current_version`; `DELETE .../content` clears the bytes and stamps `deleted_at` on the pointer and every not-yet-deleted revision; a disposition applies the same tombstone to live content; no retention or lineage | superseded/version rows at `/versions` |
| Concurrency | a per-document pointer lock allocates the next revision, so concurrent uploads both retain their bytes; the delete locks the pointer and the `deleted_at IS NULL` predicate is the duplicate guard; a disposition locks the pointer in its own transaction and treats absent or already-tombstoned content as a no-op; the last committed upload wins the current pointer without `If-Match` or `Idempotency-Key` | not specified |
| Book | none; tenant-scoped only | SPEC 3.6 book wall |
| Event | `document.content.uploaded` and `document.content.deleted` (both new; no SPEC 11.6.9 name); the upload payload `version` is the revision and the aggregate version, the delete payload is the retained file metadata plus `deletedAt`, and both keep `eventVersion` 1. The delete fact is written by the explicit delete and by a disposition of live content | no content-upload fact; content deletion is only the disposition step |
| Missing tenant | 404 `NOT_FOUND` on the expert; 400 `TENANT_REQUIRED` on the public domain route | canonical 400 Problem |

Consequences:

- A consumer can now list and download prior revisions and read the current
  revision number, but still cannot retrieve a preview rendition, OCR text, a
  page count, tags, or an access log. Legal holds and retention disposition are
  separate surfaces, documented in M-44; they are not part of the content
  slice. The 2026-10-22 tombstone is available standalone: a caller can clear
  the bytes while keeping the metadata, and then cannot download the current or
  any revision (410 `CONTENT_DELETED`) until a new upload creates a fresh
  current revision. The 1.7.0 disposition slice also applies that tombstone
  automatically to live content in the disposition transaction.
- The history is implemented at `/content/versions`, not the SPEC `/versions`
  route, and the version-creating command is the content upload rather than
  `POST /versions`. A client generated from SPEC 11.6.10 must be adapted to the
  nested path. The tombstone is also a standalone `DELETE .../content`
  command; SPEC 11.6.8 deletes content only as a step of the approved
  disposition job, so the route and the event have no SPEC equivalent (M-47).
- The public download proxies the bytes instead of issuing a short-lived
  presigned URL, so the Document domain remains a data-path hop and the
  response has no `Range` support. A caller that expected a redirect or a
  presigned target must instead consume a binary body.
- Revision allocation is serialized per document, but the current pointer has
  no optimistic concurrency token: two concurrent uploads both retain a
  revision and the last writer wins the current read. No `If-Match` or
  `Idempotency-Key` is accepted.
- The public 413 is `application/problem+json` `FILE_TOO_LARGE`, the tombstone
  preserves the expert's `CONTENT_NOT_FOUND` 404 and
  `DOCUMENT_ON_LEGAL_HOLD`/`CONTENT_ALREADY_DELETED` 409 as
  `application/problem+json`, and tombstoned downloads preserve 410
  `CONTENT_DELETED`, but the missing-tenant 400 is still the compact
  `TENANT_REQUIRED` `ApiError` rather than the canonical Problem (M-02).
- The two event names are new and have no SPEC 11.6.9 equivalent, so a
  subscriber cannot rely on a SPEC-defined content fact. The added upload
  payload `version` is additive under EV-05 and keeps `eventVersion` 1; the
  delete payload is exactly the retained metadata plus `deletedAt` and also
  keeps `eventVersion` 1 (M-22, M-47). The `document.content.deleted` fact is
  emitted both by the explicit delete route and by a disposition that
  tombstones live content, so a subscriber keyed by event name sees the same
  payload for either trigger.
- The SPEC 11.6.9 names (`document.document.registered`, `.classified`,
  `.superseded`, `.generated`, `.signed`, `.held`, `.hold-released`,
  `.archived`, `.requested`, `.request-fulfilled`, `document.package.built`,
  and the two processing facts) remain planned. `document.document.disposed`
  is implemented by the hold/disposition slice, and the two implemented
  legal-hold facts are new names with no SPEC equivalent (M-22, M-44).

Evidence:

- `repos/eia-document-domain/.../DocumentController.java:98-161` (public
  upload, current download, content tombstone, metadata, version list, and
  version download; `X-EIA-Tenant` required), the `DocumentContentMetadata`,
  `DocumentContentVersion`, `DocumentContentDownload`, `DocumentContentPolicy`,
  `DocumentContentSizeLimitFilter`, and `DocumentContentTooLargeException`
  helpers, and `DocumentExpertClient.java:209-286` (expert calls and header
  pass-through).
- `repos/eia-document-expert/.../DocumentService.java:209-256` (the disposition
  use case and `tombstoneContentForDisposal`, which applies the same tombstone
  to live content and skips absent or already-tombstoned content).
- `repos/eia-document-expert/.../DocumentContentController.java:66-128` (raw
  upload, current download, content tombstone, metadata, newest-first version
  list, and revision download), `DocumentContentService.java:47-147` (tenant
  document lookup, revision append, pointer refresh, outbox, version reads, and
  the tombstone with its duplicate and legal-hold guards),
  `DocumentContentRepository.java:96-228` (revision allocation, pointer update,
  tombstone SQL, newest-first list, and revision read),
  `DocumentContentRules.java:46-173`
  (10 MiB, filename, MIME, SHA-256, and legal-hold delete rules),
  `DocumentContentEvents.java:42-115`
  (`document.content.uploaded` with `version` and
  `document.content.deleted` with the six retained-metadata members + `deletedAt`),
  `DocumentContentVersion.java`,
  `DocumentContentVersionMetadata.java`, `DocumentContentMetadata.java`,
  `ContentVersionNotFoundException.java`, `ContentDeletedException.java`,
  `ContentAlreadyDeletedException.java`,
  `ApiExceptionHandler.java:30-52` (`CONTENT_NOT_FOUND`,
  `CONTENT_VERSION_NOT_FOUND`, `CONTENT_DELETED`, and
  `CONTENT_ALREADY_DELETED`),
  `TenantResolver.java:28-41` (content routes hide a missing tenant as 404),
  and `DocumentContentRules`/`DocumentContentMetadata`/`DocumentContent.java`.
- `repos/eia-document-expert/src/main/resources/schema.sql:48-110`
  (`document_content` current pointer, `document_content_version` revision
  table with `UNIQUE (document_id, version)` and the newest-first index, the
  nullable bytes and `deleted_at` tombstone columns, and the version-1
  backfill).
- Tests: `DocumentContentApiTest`, `DocumentContentVersionApiTest`,
  `DocumentContentClientTest`, `DocumentContentVersionClientTest`,
  `DocumentContentIntegrationTest`, `DocumentContentDeletionIntegrationTest`,
  `DocumentDispositionContentTombstoneIntegrationTest`, and
  `DocumentContentRulesTest`.
- `openapi/document.yaml` 1.7.0, `asyncapi/document.yaml` 1.7.0, and
  `asyncapi/event-catalog.yaml` 1.29.0 record the implemented shape.

Resolution: either align the implementation with SPEC 11.6.10 (move the
history to `/versions`, add the `POST /versions` command, presigned download,
renditions, OCR text, book scope, and the SPEC lifecycle/content facts) or
amend SPEC 11.6.9 and 11.6.10 to the current-pointer plus revision proxy, the
`/content/versions` path, the upload-as-version-command, and the new
`document.content.uploaded` payload. The contract documents the implemented
shape until that decision.

## M-41 Policy credit notes use a short path, a five-state lifecycle, installment application and reversal, a cancellation link, and new event names

SPEC 11.2.13 defines the `credit_note_request` row, mounts the request at
`POST /api/v1/policy/policies/{policyId}/credit-notes`, routes the request
through a human approval step and the Payment SAP subtransaction, and publishes
`policy.billing.credit-note-issued`. The implemented slice is a narrower
tenant-scoped child resource with its own lifecycle, free-text reason, an
APPLIED transition that credits an open billing installment, an APPLIED ->
REVERSED transition that releases the credit with a required reason, an
optional link from a return-premium note to the cancellation it refunds, and
five new event names.

| Aspect | Implemented | SPEC 11.2.13 |
|---|---|---|
| Paths | `GET/POST /api/v1/policies/{policyId}/credit-notes` and `PATCH .../{creditNoteId}/status` | `POST /api/v1/policy/policies/{policyId}/credit-notes`; no public list or status action row |
| Identity | `creditNoteId` UUID; server-generated `noteNumber` `CN-{7 digits}` | `id`; optional `original_invoice_number` and `sap_credit_memo_number` |
| Status | `DRAFT`, `ISSUED`, `APPLIED`, `CANCELLED`, `REVERSED` | `REQUESTED`, `APPROVED`, `SENT_TO_SAP`, `ISSUED`, `REJECTED` |
| Transitions | DRAFT -> ISSUED -> APPLIED; CANCELLED from DRAFT or ISSUED; REVERSED from APPLIED; APPLIED, CANCELLED, and REVERSED terminal | Request, approve, send to SAP, persist the SAP reference, issue, reject |
| Cancellation link | optional `CreateCreditNoteRequest.cancellationId`. The cancellation must be on the same tenant and policy (404 `CANCELLATION_NOT_FOUND`), still be ACTIVE (409 `CANCELLATION_NOT_ACTIVE` with `meta.cancellationId`/`meta.currentStatus`), and match the note amount within one cent of `returnPremiumAmount` (400 `CREDIT_NOTE_AMOUNT_MISMATCH`) in its `premiumCurrency` (400 `CURRENCY_MISMATCH`). A cancellation funds at most one note: a duplicate is 409 `DUPLICATE_CANCELLATION_CREDIT_NOTE` with `meta.cancellationId` and, when known, `meta.creditNoteId`/`meta.noteNumber`; the unique `(tenant_id, policy_id, cancellation_id)` key arbitrates a concurrent duplicate. A linked note exposes `cancellationId` and `cancellationNumber`; both are null for a general adjustment | `credit_note_request` has no `cancellation_id` column. `BIL-05` states only that a cancellation produces a credit note or additional invoice and `BIL-08` links non-payment cancellation to a credit note; no amount/currency/one-note rule is specified |
| Cancellation number | `policy_cancellation` gains the nullable `cancellation_number` (`CX-{7 digits}`, unique per policy). New cancellations always carry one; the credit-note read and the `created` event fall back to the cancellation id for a historical row without a number. The public domain `CancellationDto` does not yet expose the member | no cancellation number column or business reference |
| Credit application | APPLIED requires an `installmentId`; the note is credited to a DUE/OVERDUE installment on the same tenant and policy. A partial credit raises the installment's `creditedAmount` and leaves it open; a credit that covers its uncredited remainder sets the new terminal installment status `CREDITED` and a zero `outstandingAmount`. A missing id is 400 `INVALID_CREDIT_NOTE_INSTALLMENT`, an unknown/foreign installment is 404 `INSTALLMENT_NOT_FOUND`, a settled/credited target is 409 `INSTALLMENT_NOT_CREDITABLE`, and an oversized note is 409 `CREDIT_NOTE_EXCEEDS_INSTALLMENT` with the note amount and available remainder | `credit_note_request` has no installment column and no APPLIED state; `BIL-06` defines only `outstanding = invoiced - paid - credited` and the non-negative rule, with no application command |
| Credit reversal | APPLIED -> REVERSED only, with a required non-blank `reason` of at most 500 characters. Releases the note amount from the installment recorded at application time, subtracts it from `creditedAmount` clamped at zero, and reopens a fully credited installment as DUE when its due date is today or later and as OVERDUE when it is past. A partial credit on an open row keeps its status, and a legacy APPLIED note without an installment is only marked REVERSED. Reversing a DRAFT/ISSUED/CANCELLED or already REVERSED note is 409 `INVALID_CREDIT_NOTE_TRANSITION`; a missing or blank reason is 400 `INVALID_CREDIT_NOTE_REASON`; a longer reason is 400 `VALIDATION_ERROR`; a concurrent installment change is 409 `CONCURRENT_MODIFICATION` | No reversal command, state, or fact; `BIL-06` defines no unapply or restore rule |
| Reason | creation reason is free text, trimmed, optional, at most 500 characters; reversal reason is free text, trimmed, required, non-blank, at most 500 characters | closed enum `CANCELLATION`, `ENDORSEMENT`, `AUDIT_RETURN`, `OVERPAYMENT`, `REFUND`, `CORRECTION` |
| Money | positive `amount` plus `currency`, which must equal the policy premium currency | `amount`, optional `tax_amount`, and `currency` |
| Approval | none | `policy.credit-note.approve` human approval with `approved_by` |
| SAP | no credit-memo number, no `payment.finance.credit-note` call, and no Payment link | SAP credit-memo request and persisted reference |
| Original invoice | not modelled | optional `original_invoice_number` |
| Projection | flat fifteen fields, including nullable `appliedInstallmentId`, `reversedAt`, `reversalReason`, `cancellationId`, and `cancellationNumber`; `tenantId` is not exposed | the full request row including tax, approval, and SAP columns; no cancellation-link columns |
| Events | `policy.credit-note.created`, `.issued`, `.applied`, `.cancelled`, `.reversed`. The `created` payload is a dedicated `PolicyCreditNoteCreatedData` with the base fields, `status: DRAFT`, `createdAt`, and the optional `cancellationId`/`cancellationNumber`; the `applied` payload adds `installmentId` and the installment's cumulative `creditedAmount`; the `reversed` payload is a dedicated `PolicyCreditNoteReversedData` with the note identity and number, the nullable released installment, the amount, the reason, and status REVERSED | only `policy.billing.credit-note-issued`; no created, applied, cancelled, or reversed fact |
| Book | the canonical contract requires `X-EIA-Book: DIRECT`; the domain and expert accept an absent header | SPEC 3.6 book wall |

Consequences:

- A consumer cannot see the approval, SAP credit-memo number, tax amount, or
  original invoice reference because none of them is modelled or returned.
- The free-text reason cannot be mapped to the SPEC six-value enum without a
  translation table; the domain test's `CANCELLATION`/`ENDORSEMENT`/... example
  is illustrative, not enforced by the expert's `CreditNoteRules`.
- The five-state lifecycle collapses the SPEC request/approval/SAP flow into
  DRAFT/ISSUED/APPLIED/CANCELLED/REVERSED, so a client cannot observe REQUESTED,
  APPROVED, SENT_TO_SAP, or REJECTED.
- Credit application goes beyond the SPEC row: a note is tied to one billing
  installment that the SPEC does not model as a credit-note target, and the
  installment gains a CREDITED state the SPEC does not name. The persisted
  `creditedAmount` is bounded by the gross amount and the derived
  `outstandingAmount` is clamped at zero, so the implementation satisfies
  BIL-06 even though the SPEC defines no application command.
- Reversal also goes beyond the SPEC row: it is a one-way release with no
  unreverse command, it keeps the application facts for audit, and it is the
  only way to make an applied credit stop counting toward the installment. The
  subtract-and-clamp rule keeps the persisted `creditedAmount` non-negative even
  when the ledger and the note disagree, and the DUE/OVERDUE reopen rule is an
  implementation choice the SPEC does not define.
- A rejected application or reversal rolls back both the note and the
  installment, so a failed reversal leaves the note APPLIED and the credit in
  place. A partial credit does not block a later settlement, so an installment
  can be PAID or WAIVED after carrying a partial credit; its `outstandingAmount`
  is then zero because the terminal status wins.
- A legacy APPLIED note that predates installment application has a null
  `appliedInstallmentId`, which is why the member is required but nullable and
  why a reversal of such a note changes no installment.
- Creating a note now bumps the policy row version and writes
  `policy.credit-note.created` in the same transaction, so the DRAFT creation
  is observable. The payload carries `createdAt` and, for a cancellation-linked
  note, the cancellation identity and number; an unlinked adjustment omits both
  link members.
- A cancellation can fund at most one note, so the create is not retry-safe in
  the duplicate direction: a retried linked request returns 409
  `DUPLICATE_CANCELLATION_CREDIT_NOTE`, and the unique
  `(tenant_id, policy_id, cancellation_id)` key arbitrates two concurrent first
  attempts. The 409 metadata names the existing note when the lookup finds it.
- Linking is stricter than the SPEC row: the note must refund the full return
  premium within one cent and in the same currency, and the cancellation must
  still be ACTIVE. A REINSTATED or VOID cancellation cannot fund a note, and a
  partial refund is not modelled because the credit-note amount is the whole
  return premium.
- The `CX-{7 digits}` cancellation number is new and per-policy unique through
  `uq_policy_cancellation_number`; the shared global sequence makes a policy's
  numbers ordered but not contiguous. Historical rows can be null, and a note
  linked to such a row reports the cancellation id in `cancellationNumber`
  instead of a `CX-` reference.
- The public domain `CancellationDto` still has no `cancellationNumber`
  component, so `/api/v1/policies/{policyId}/cancellations` and `/cancel` drop
  the field the expert returns. The domain `CreditNote` projection does carry
  `cancellationId`/`cancellationNumber`, so only the cancellation projection is
  behind; the canonical `Cancellation` schema therefore documents the member as
  nullable and optional.
- The create has no `Idempotency-Key` and no caller-supplied business key, so a
  retried unlinked request produces a second note and consumes a second
  server-assigned number; the status command accepts no `If-Match`, and a
  replay of a terminal target, including a second REVERSED, is a 409 rather
  than a no-op.
- A missing `X-EIA-Book` is accepted by both the domain and the expert even
  though the canonical contract requires DIRECT; another book is hidden as 404
  `BOOK_SCOPE_VIOLATION`.
- The five event names are new and have no SPEC equivalent other than the
  issued fact, so aligning them requires the EV-05 dual-publish window (M-22).
  The `created` payload is a new name under a dedicated message and keeps
  `eventVersion` 1; the `applied` payload additions keep `eventVersion` 1
  because they are optional and additive; the reversal has a dedicated payload
  under a new name and also keeps `eventVersion` 1.

Evidence:

- `repos/eia-policy-domain/.../PolicyCreditNoteController.java:27-76` (public
  GET/POST/PATCH, required tenant header, `requireDirectWhenPresent`, 201),
  `PolicyCreditNoteService.java` (expert delegation), `CreditNote.java`
  (nullable `appliedInstallmentId`, `reversedAt`, `reversalReason`,
  `cancellationId`, and `cancellationNumber`),
  `CreateCreditNoteCommand.java` (optional `cancellationId`),
  `UpdateCreditNoteStatusCommand.java` (optional `installmentId` and optional
  500-character `reason`), and `PolicyClient.java:773-829,1298-1316` (the
  create forwards `cancellationId` only when present; the expert `id` maps to
  `creditNoteId` and the `cancellation_id`/`cancellation_number` aliases map).
- `repos/eia-policy-domain/.../CancellationDto.java` and
  `PolicyContractController.java:175-195`: the public cancellation projection
  has no `cancellationNumber` component even though the expert
  `PolicyCancellation` returns it.
- `repos/eia-policy-expert/.../CreditNoteController.java:27-77` (public and
  internal aliases, tenant query/header, 201/200),
  `CreditNoteService.java:69-330` (policy wall, currency match, number
  consumption, cancellation resolution and ACTIVE/amount/currency gate, the
  duplicate lookup and unique-key race, the `policy.credit-note.created`
  outbox row, APPLIED installment validation and credit, REVERSED release and
  reopen, conditional transition, policy version bump),
  `CreditNoteRules.java:36-90,142-255` (five states, transition graph,
  `CANCELLATION_AMOUNT_TOLERANCE`, `CANCELLATION_NOT_ACTIVE`,
  `CREDIT_NOTE_AMOUNT_MISMATCH`, `CURRENCY_MISMATCH`,
  `DUPLICATE_CANCELLATION_CREDIT_NOTE`, required/optional 500-character
  reason, `INVALID_CREDIT_NOTE_REASON`, `INVALID_CREDIT_NOTE_INSTALLMENT`,
  `INSTALLMENT_NOT_CREDITABLE`, `CREDIT_NOTE_EXCEEDS_INSTALLMENT`, CREDITED
  transition, credited-after and status-after-reversal arithmetic),
  `CreditNoteRepository.java:21-165` (tenant/policy-scoped reads with the
  cancellation join and id fallback, `findByCancellation`, `CN-{7 digits}`
  sequence, `applied_installment_id`, conditional reversal with
  `reversed_at`/`reversal_reason`), `PolicyCreditNote.java`,
  `CreateCreditNoteRequest.java`, and `UpdateCreditNoteStatusRequest.java`.
- `repos/eia-policy-expert/.../PolicyEvents.java:49,106-169` (the
  `policy.credit-note.created` payload with the base fields, `createdAt`, and
  the optional cancellation identity/number; `issued` / `.applied` /
  `.cancelled` with policy and note identity, amount, currency, and status; the
  applied payload adds `installmentId` and `creditedAmount`;
  `creditNoteReversed` writes the six-member reversal payload),
  `CancellationRepository.java:80-140` (`nextCancellationNumber` and the
  `cancellation_number` read), `CancellationService.java:131-138` (a new
  cancellation receives its number), `PolicyCancellation.java`, and
  `src/main/resources/schema.sql:443-483,632-698` (`cancellation_number` and
  `uq_policy_cancellation_number`; `policy_credit_note.cancellation_id` and
  `uq_policy_credit_note_cancellation`; the CHECK constraints including the
  REVERSED status and `reversed_at` requirement; the number sequence,
  `applied_installment_id`, `reversed_at`, `reversal_reason`, and the
  `policy_installment.credited_amount` migration).
- `repos/eia-policy-expert/.../BillingRepository.java:232-270` (conditional
  credited-amount update, status change to CREDITED, and the reversal release)
  and `BillingRules.java:99-114` (zero outstanding for PAID, WAIVED, and
  CREDITED).
- Tests: `PolicyCreditNoteControllerTest` (linked create, null link),
  `PolicyCreditNoteServiceTest`, `PolicyCreditNoteClientTest` (cancellation
  mapping), `CreditNoteControllerTest`, `CreditNoteServiceTest` (linked create,
  duplicate, inactive, amount/currency mismatch, rollback, reversal, reason
  bounds, restore and reopen, tenant/policy wall), `CreditNoteRulesTest`
  (cancellation link, transition graph, and reversal arithmetic),
  `CancellationServiceTest` (CX number), `BillingServiceTest`,
  `BillingRulesTest`, `BillingSummaryTest`, and `BillingReceivablesServiceTest`.
- `openapi/policy.yaml` 2.14.0, `asyncapi/policy.yaml` 1.11.0, and
  `asyncapi/event-catalog.yaml` 1.26.0 record the implemented shape.

Resolution: either extend SPEC 11.2.13 with the implemented short route,
five-state lifecycle, free-text reason, installment application and reversal,
cancellation link, and five event names, or add the SPEC request/approval/SAP
lifecycle, reason enum, and `policy.billing.credit-note-issued` name behind an
EV-05 dual-publish window. The installment target, the CREDITED installment
status, and the reversal/reopen rule are the parts of the slice closest to
BIL-06, while the cancellation link is the implementation of BIL-05/BIL-08 and
can be adopted as the return-premium credit rule. Until then the contract
documents the implemented narrow surface, the `CX-{7 digits}` cancellation
reference, and the DIRECT book requirement.

## M-42 Contract technical-account lines omit correction and line-level metadata

SPEC 11.3.4 defines `technical_account_line` as the line detail of a technical
account. The 2026-10-21 slice implements the 13-type detail vocabulary and rolls
every type into one of the four account header components. The remaining gaps
are the line update/correction command, per-line currency and source metadata,
per-line approval, and duplicate detection.

| Area | Implemented | SPEC 11.3.4 / gap |
|---|---|---|
| Paths | `GET/POST /api/v1/contracts/{contractId}/technical-accounts/{accountId}/lines` and `DELETE .../lines/{lineId}`, plus the same controller under `/internal/v1` | SPEC 11.3.10 does not list a line route; the detail is nested under the implemented `/technical-accounts` path (M-29). |
| Line types | `PREMIUM`, `COMMISSION`, `BROKERAGE`, `PAID_LOSS`, `OUTSTANDING_LOSS`, `IBNR`, `ALAE`, `REINSTATEMENT`, `CASH_CALL`, `FUNDS_WITHHELD`, `TAX`, `ADJUSTMENT`, `OTHER`; each rolls into exactly one bucket: `PREMIUM` -> premium; `PAID_LOSS`, `OUTSTANDING_LOSS`, `IBNR`, `ALAE`, `REINSTATEMENT`, and `CASH_CALL` -> loss; `COMMISSION` and `BROKERAGE` -> commission; `FUNDS_WITHHELD`, `TAX`, `ADJUSTMENT`, and `OTHER` -> other | The retired aggregate `LOSS` is rejected on create (400 `INVALID_LINE_TYPE`) and stored `LOSS` rows are migrated to `PAID_LOSS`; a legacy `LOSS` total is still read into the loss bucket. |
| Read model | `items` plus `totals` with the four bucket members `premium`, `loss`, `commission`, `other` and an optional per-type `details` map; the expert also returns an authoritative `bucketTotals` map, which the domain normalizes into the public buckets | The public projection exposes only the normalized buckets and the detail map; the expert's raw `totals`/`bucketTotals` shape is not part of the public contract. |
| Projection | `lineId`, `accountId`, `lineType`, `reference`, `description`, `amount`, `createdAt`; `tenantId` is not exposed | No source-document reference, no currency per line (the account currency is implied), and no audit actor. |
| Writes | `POST` creates and `DELETE` removes; both only while the account is DRAFT (409 `ACCOUNT_NOT_EDITABLE`); `amount` must be strictly positive | No line update or amount correction. A zero or negative line cannot be recorded, so a credit line is modelled through the header amount instead. |
| Reconciliation | On DRAFT -> ISSUED, when at least one line exists, each of the four bucket totals must equal its header field (`premium` = `cededPremium`, `loss` = `cededLosses`, `commission` = `commission`, `other` = `otherCharges`); the conflict names each offending bucket and its contributing types | A header-only account (no lines) remains issuable, so the rule is opt-in by the presence of detail. There is no duplicate-line detection, line count, or per-line approval. |
| Text bounds | `reference` at most 64 characters, `description` at most 255; both optional and trimmed | The domain validates `description` at 300 characters and the expert caps it at 255, so the effective public bound is 255. |
| Events | `contract.technical-account.line-added` and `.line-removed`, each a grandchild fact keyed by the line id at aggregate version 1 with the contract id as the outbox partition key; the payload `lineType` carries the 13 detail types | The names have no SPEC 11.3.9 equivalent and the payload omits `reference` and `description` (M-22). |
| Book | The canonical contract requires `X-EIA-Book: ASSUMED`; another book is 404 `BOOK_SCOPE_VIOLATION` | The domain accepts an absent header for compatibility with the other Contract proxy routes; the expert internal alias checks no book (M-29). |

Consequences:

- A consumer that only reads the `TechnicalAccount` header does not see the
  line detail; it must call the `/lines` read model. The header and the totals
  are reconciled only at issue.
- The four buckets are the reconciliation view, so the 13 detail types preserve
  the audit distinction between paid and outstanding loss, IBNR, ALAE,
  reinstatement, cash call, brokerage, funds withheld, tax, and adjustment only
  in `totals.details` (or in the line rows themselves). A consumer that reads
  only the four buckets cannot see that distinction.
- The line events are not full audit records: they carry the type and amount
  but not the optional reference or description, so an event-only consumer
  cannot reproduce the line text.
- A line cannot be corrected in place; a mistake is removed and re-added while
  the account is DRAFT. Once ISSUED, the detail is immutable and the only path
  is a new account period.
- The domain's 300-character description check is wider than the expert's
  255-character column, so a 256-300 character description passes the domain
  and is rejected by the expert with a 400. The canonical contract documents
  the effective 255 bound.

Evidence:

- `repos/eia-contract-domain/.../TechnicalAccountLineController.java:28-79`
  (public paths, required tenant header, optional ASSUMED book guard, 200/201/
  204), `TechnicalAccountLineService.java:21-32`, and
  `TechnicalAccountLineClient.java:109-245` (expert call, `lines` -> `items`
  normalization, `bucketTotals` preference, detailed-totals and row fallback,
  error translation).
- `repos/eia-contract-domain/.../TechnicalAccountLine.java:23-31` (`id` ->
  `lineId` and `technicalAccountId` -> `accountId` aliases),
  `TechnicalAccountLineTypes.java:19-85` (13 detail types, retired `LOSS`,
  bucket mapping), `LineSummary.java:31-92` (items, four buckets, optional
  details, money serializer), and `CreateTechnicalAccountLineCommand.java:14-19`.
- `repos/eia-contract-domain/.../ContractCommandRules.java:69-70,258-272`
  (domain detail-type, positive-amount, 64-character reference, and
  300-character description validation; `INVALID_LINE_TYPE` for `LOSS`).
- `repos/eia-contract-expert/.../technicalaccount/TechnicalAccountLineController.java:44-129`
  (list/add/remove, tenant resolution, account lock, DRAFT guard, per-mutation
  outbox), `TechnicalAccountLineRules.java:77-151` (detailed totals, four-bucket
  roll-up, formatting, and the bucket reconciliation), and
  `TechnicalAccountLineRepository.java:49-103` (insertion-order reads,
  tenant/account scoping, delete, grouped totals).
- `repos/eia-contract-expert/.../technicalaccount/TechnicalAccountLineType.java:15-86`
  (the 13 types, their buckets, and the header-field mapping),
  `TechnicalAccountLinesDoNotReconcileException.java:17-33` (one conflict with
  the per-bucket mismatch list), and `TechnicalAccountLineList.java:18-23`
  (expert `lines`/`totals`/`bucketTotals` wire read model).
- `repos/eia-contract-expert/.../ContractEvents.java:72-73,247-259,512-544`
  (line event names, factories, aggregate type, version 1, and payload).
- `repos/eia-contract-expert/src/main/resources/schema.sql:477-515`
  (`contract_technical_account_line`, the 13-type check, the `LOSS` migration,
  positive amount, and account cascade).
- Tests: `TechnicalAccountLineControllerTest`,
  `TechnicalAccountLineOutboxIntegrationTest`, `TechnicalAccountLineRulesTest`,
  `TechnicalAccountLineClientTest`, `LineSummaryTest`, and
  `TechnicalAccountControllerTest` (issue reconciliation).
- `openapi/contract.yaml` 4.3.0, `asyncapi/contract.yaml` 1.8.0, and
  `asyncapi/event-catalog.yaml` 1.23.0 record the implemented shape.

Resolution: the implemented 13-type detail and bucket reconciliation are
documented as canonical for now. Closing the gap means adding a line update or
correction command, per-line currency/source metadata, per-line approval or
duplicate detection, or amending SPEC 11.3.4 to the bucket-reconciled model.
The two event names follow EV-05 and can be aligned to a SPEC name only through
a dual-publish window. The description bound should be aligned between the
domain and expert before it is treated as a stable 300.

## M-43 Policy legal entity catalog is a narrow, nullable-assignment slice

The Policy expert now owns a tenant-scoped DIRECT-book legal entity catalog and
the policy issuing-entity assignment. The implemented shape is narrower than
SPEC 10.11.2 and SPEC 11.2.16:

- The public paths are `/api/v1/legal-entities`,
  `/api/v1/legal-entities/{legalEntityId}`, and
  `PATCH /api/v1/policies/{policyId}/legal-entity`. SPEC 11.2.16 lists the
  catalog under `/api/v1/policy/legal-entities` and defines no assignment
  command (M-01).
- `LegalEntity` is `{legalEntityId, code, name, entityType, jurisdiction,
  regulator, licenseNumber, status, createdAt}`. SPEC 10.11.2 names
  `entity_code` (varchar 16), `legal_name` (varchar 300), and
  `domicile_country` (ISO 3166-1 char 3), and defines no public `jurisdiction`,
  `regulator`, or `license_number` column; the implemented code allows 32
  characters and the name 200. The implemented `jurisdiction` is a two-letter
  ISO 3166-1 alpha-2 code, not the three-letter `domicile_country`.
- `entityType` is closed to `INSURER`, `MGA`, `CAPTIVE`, `POOL`, or `FRONTER`.
  SPEC 10.11.5 seeds `HOLDING`, `INSURER`, `REINSURER`, `MGA`, `TPA`, `CAPTIVE`,
  `SYNDICATE`, and `SERVICE_COMPANY`, so `POOL` and `FRONTER` are additions and
  the other five are missing. `status` is `ACTIVE` or `INACTIVE`; SPEC 10.11.2
  also defines `LIQUIDATING`. No retirement, update, or delete command exists,
  so `INACTIVE` is reserved and never written.
- A policy's `legalEntityId` is nullable, and
  `PATCH /api/v1/policies/{policyId}/legal-entity` clears it with a null or
  absent id. SPEC 11.2.16 `LE-01` requires every policy to reference exactly one
  issuing legal entity, and the domain `PolicyClient` comment says the expert
  rejects a null member, but the expert and its integration test accept and
  persist the clear. No bind-time or lifecycle gate requires an entity before
  `ISSUED` or `IN_FORCE`.
- The create trims and upper-cases `code`, `entityType`, and `jurisdiction`, and
  trims `name`, `regulator`, and `licenseNumber`; a blank optional value becomes
  null. The code is unique per tenant after normalization, and a duplicate is
  409 `DUPLICATE_LEGAL_ENTITY_CODE`. No NAIC company code, SAP company code,
  LEI, tax id, functional currency, parent, effective dates, or
  organization-unit/capacity link is implemented. The catalog is a bare
  newest-first array with no filter, search, or page envelope (M-04).
- The expert accepts `tenantId` as a query parameter and either
  `X-EIA-Tenant` or the query; the public domain requires the tenant header.
  The domain and expert accept an absent `X-EIA-Book`, and another book is
  hidden as 404 `BOOK_SCOPE_VIOLATION`.
- The two events are new names: `policy.legal-entity.created` (the
  `LegalEntity` aggregate at version 1) and
  `policy.policy.legal-entity-assigned` (the policy aggregate at the new
  version). SPEC 11.2.9 defines neither and SPEC 11.2.16 names no event, so the
  M-22 naming difference applies.

Evidence:

- `repos/eia-policy-domain/.../LegalEntityController.java:26`,
  `LegalEntityService.java`, `LegalEntityDto.java`,
  `CreateLegalEntityCommand.java`, `PolicyLegalEntityController.java:21`,
  `PolicyLegalEntityService.java`, `UpdatePolicyLegalEntityCommand.java`,
  `PolicyDto.java:28`, `PolicyClient.java:496-581`,
  `src/test/java/com/eia/policy/domain/LegalEntityControllerTest.java`,
  `PolicyLegalEntityControllerTest.java`, and `LegalEntityClientTest.java`.
- `repos/eia-policy-expert/.../LegalEntityController.java:29`,
  `LegalEntityService.java:56-123`, `LegalEntityRules.java:17-128`,
  `LegalEntityRepository.java:43-70`, `LegalEntity.java`,
  `LegalEntityView.java`, `CreateLegalEntityRequest.java`,
  `AssignPolicyLegalEntityRequest.java`, `Policy.java:45`,
  `PolicyRepository.java:188-195`, `PolicyEvents.java:55-56,163-232`,
  `src/main/resources/schema.sql:89-125`, and the expert
  `LegalEntityControllerTest`, `LegalEntityServiceTest`,
  `LegalEntityRulesTest`, and `LegalEntityIntegrationTest`.

Resolution: either widen the catalog to the SPEC 10.11.2 columns and
vocabularies, add the SPEC path and an LE-01 assignment gate (a policy must have
an issuing entity before bind/issue), or amend SPEC 10.11.2/11.2.16 to the
implemented five-type catalog and nullable link. The two event names need the
EV-05 dual-publish treatment if they are aligned to SPEC names.

## M-44 Document legal holds and disposition are a per-document, synchronous slice

SPEC 11.6.8-11.6.10 model legal holds as a scoped hold collection with
approval and a release by hold id, and disposition as an approved asynchronous
job that produces a certificate and deletes the content. The implemented slice
stores the hold on the document row and exposes three per-document synchronous
commands; it has no hold entity, scope, approval, disposition job, or
certificate, but since the 2026-10-22 disposition-content slice it does delete
live content as part of the synchronous disposition.

| Aspect | Implemented | SPEC 11.6.8-11.6.10 |
|---|---|---|
| Hold routes | `POST /api/v1/documents/{documentId}/hold` with `{reason}` | `POST /api/v1/document/holds` (scope plus approval) |
| Release route | `POST /api/v1/documents/{documentId}/hold/release` | `POST /api/v1/document/holds/{holdId}/release` |
| Disposition route | `POST /api/v1/documents/{documentId}/dispose`, no body | `POST /api/v1/document/documents/{documentId}/dispose` in the async approval flow |
| Hold storage | flat `hold_reason`, `held_at`, `status_before_hold` columns on `document` | hold entity with scope and approval; `legal_hold_flag` on the document |
| Holdable statuses | ACTIVE, ARCHIVED, CLASSIFIED, SUPERSEDED | ACTIVE and ARCHIVED (state diagram) |
| Release result | restores `status_before_hold`; ARCHIVED when the snapshot is absent or unrecognised | ON_HOLD -> ACTIVE (and ON_HOLD -> ARCHIVED per the hold scope) |
| Disposition gates | expired `retention_until`, no ON_HOLD, status in ACTIVE/ARCHIVED/SUPERSEDED | approved disposition job, no hold/litigation/regulatory block, certificate |
| Disposition side effects | tombstone `DISPOSED` + `disposed_at`; metadata stays readable; live content is tombstoned in the same transaction (bytes cleared, `deleted_at` recorded) and `document.content.deleted` is emitted; content-free or already-tombstoned content disposes without a content fact | delete content, mark disposed, store certificate with counts and hashes |
| Hold events | `document.legal-hold.placed`, `document.legal-hold.released` (new names) | `document.document.held`, `document.document.hold-released` |
| Disposition events | `document.document.disposed` (SPEC name) and, for live content, `document.content.deleted` (new name) | `document.document.disposed` |
| Tenant scope | `X-EIA-Tenant` required; expert also accepts `?tenantId=`; another tenant is 404 | tenant wall (M-08) |

Consequences:

- A client generated from SPEC 11.6.10 must use the per-document hold and
  release paths and cannot list holds, scope a hold, or address a hold by id.
  There is no approval gate or custody record, so the command does not satisfy
  the records-manager plus legal approval rule in SPEC 10.8/11.6.
- Hold release always lands in the snapshot, or ARCHIVED when the snapshot is
  missing; CLASSIFIED and SUPERSEDED can be snapshotted even though SPEC only
  draws ACTIVE and ARCHIVED hold edges. A caller cannot force ON_HOLD back to a
  specific status.
- Disposition is immediate: there is no retention-scan job, approval step, or
  certificate. It does delete live content: the same transaction clears the
  current pointer and every not-yet-tombstoned revision, records `deletedAt`,
  and appends `document.content.deleted`. A document with no content or
  already-tombstoned content keeps its metadata/content row as a tombstone and
  writes only `document.document.disposed`; the standalone `DELETE .../content`
  command also remains available with its own 404/409 vocabulary, and neither
  path carries an approval or certificate (M-47). The
  public dispose command does not forward a
  reason, so the event reason is `RETENTION_EXPIRED`; the expert accepts an
  optional reason but the domain never sends one.
- The two legal-hold event names have no SPEC 11.6.9 equivalent. The SPEC
  `document.document.held` and `.hold-released` channels remain planned, while
  the SPEC `document.document.disposed` name is now implemented. This is a name
  difference, not a payload-version change: all three keep `eventVersion` 1
  (M-22).
- A rejected hold, release, or disposition writes no row change and no event,
  so the outbox remains consistent with the stored state.

Evidence:

- `repos/eia-document-domain/.../DocumentController.java:61-91` (public hold,
  release, and dispose), `DocumentService.java:103-126` (command
  pass-through), `HoldDocumentCommand.java`, `DocumentDto.java:11-27`, and
  `DocumentExpertClient.java:163-201` (expert calls on the public hold and
  dispose paths with `?tenantId=` and `X-EIA-Tenant`).
- `repos/eia-document-expert/.../DocumentLifecycleController.java:32-69`
  (the three routes and the tenant header/query fallback),
  `HoldDocumentRequest.java`, `DisposeDocumentRequest.java`,
  `DocumentService.java:160-256` (hold, release, dispose, and the disposition
  content tombstone),
  `DocumentRules.java:40-64,138-213` (holdable/disposable statuses, reason
  bound, restore fallback, and the seven conflict codes),
  `DocumentRepository.java:142-201` (hold, release, and dispose SQL),
  `Document.java:15-30`, and `DocumentConflictException.java`.
- `repos/eia-document-expert/.../DocumentContentRepository.java:188-228`
  (`deleted_at` tombstone SQL shared by the explicit delete and disposition) and
  `DocumentContentEvents.java:77-115` (`document.content.deleted`).
- `repos/eia-document-expert/.../DocumentEvents.java:29-40,88-117` (the two
  legal-hold names, the SPEC disposed name, and the lifecycle payload).
- `repos/eia-document-expert/src/test/java/com/eia/document/expert/DocumentLifecycleControllerTest.java`,
  `DocumentLegalHoldIntegrationTest.java`, and
  `DocumentDispositionContentTombstoneIntegrationTest.java` (the 409 codes,
  snapshot fields, events, rollback behaviour, and both disposition facts).
- `openapi/document.yaml` 1.7.0, `asyncapi/document.yaml` 1.7.0, and
  `asyncapi/event-catalog.yaml` 1.29.0 record the implemented shape.

Resolution: either implement the SPEC hold collection with scope, approval, and
release by hold id, and the approved disposition job with a certificate around
the now-coupled content deletion, or amend SPEC 11.6.8-11.6.10 to the
per-document hold columns, the snapshot restore, and the synchronous tombstone
with its content deletion. The two
legal-hold event names need the EV-05 dual-publish treatment if they are
aligned to the SPEC names.

## M-45 Direct Claims settlement payment links are a SPEC-less route and event over one stored Payment id

SPEC 11.4.4 defines a `claim_settlement.payment_id` column described as a
"Projection from Payment", and the SPEC relationship model names
`SETTLEMENT_HAS_PAYMENT` (1:N) with its inverse `PAYMENT_SETTLES` (N:1). SPEC
11.4.10 defines no payment-link operation under the settlement resource, and
SPEC 11.4.9 publishes no link event. The 2026-10-21 slice documents an already
implemented Direct Claims extension:

| Area | Implemented | SPEC / gap |
|---|---|---|
| Route | `PATCH /api/v1/claims/{claimId}/settlements/{settlementId}/payment` (the M-01 short form) and the `/internal/v1` expert alias the domain calls | SPEC 11.4.10 lists only the settlement GET, POST authorize, and execute operations; the link command is an implementation extension. |
| Command | Required body `SettlementPaymentRequest` `{paymentId}`; `paymentId` is required but nullable: a UUID links and stamps `paymentLinkedAt`, null clears both members, and repeating the current value is an idempotent no-op | SPEC models `payment_id` as a projection from Payment and does not define a command. The canonical body requires the explicit null, but neither the expert nor the domain marks the record component required, so a body that omits `paymentId` is also treated as a clear. |
| Projection | `Settlement.paymentId` and `Settlement.paymentLinkedAt` are required-but-nullable; both are null while unlinked | SPEC has `payment_id` but no link timestamp, and it does not expose the field through a documented settlement projection. |
| Linkability | Only `AUTHORIZED` or `EXECUTED` is linkable; a `PROPOSED` or `REJECTED` settlement is 409 `SETTLEMENT_NOT_LINKABLE`. A concurrent settlement change is 409 `CONFLICT`; an unknown claim or settlement, a foreign tenant, and a missing or non-DIRECT book are 404 | SPEC defines no link state machine. Its settlement status vocabulary is wider (`PROPOSED`, `NEGOTIATING`, `AUTHORIZED`, `APPROVED`, `EXECUTED`, `PAID`, `REJECTED`, `VOID`), while the implemented set is `PROPOSED`/`AUTHORIZED`/`EXECUTED`/`REJECTED`; `PAID` is not implemented. |
| Link cardinality | One nullable `paymentId` per settlement, stored by Direct Claims; no Payment service call, no existence or tenant check, and no amount or currency reconciliation | SPEC 11.4.4 and the relationship model allow many payments per settlement. The link is free of Payment-side validation, so a foreign, unknown, or cancelled Payment id is accepted. |
| Event | `direct.claim.settlement-payment-linked`; the payload carries the claim identity and version context, `claimId`, `settlementId`, `settlementNumber`, `paymentId`, and `linkedAt`, and an unlink omits `paymentId`/`linkedAt` | SPEC 11.4.9 names no settlement-payment-link fact, so the name is new (M-22). A real link or unlink bumps the claim and settlement versions; a repeat and a non-linkable settlement write nothing. |
| Error surface | The expert returns 409 `SETTLEMENT_NOT_LINKABLE`; the public domain maps every expert 409 except `EIA-DIR-4091` to 409 `CONFLICT` while preserving the detail | The canonical public contract documents `SETTLEMENT_NOT_LINKABLE`; the running domain reports `CONFLICT`, in the same way M-31 records the remapped allocation codes. |
| Book | The public and expert operations require `X-EIA-Book: DIRECT`; another book is 404 `BOOK_SCOPE_VIOLATION` | Matches the claim-vertical book wall (WALL-06); a missing header is also 404 in this vertical (M-08, M-23). |

Evidence:

- `repos/eia-direct-claims-domain/.../ClaimDetailController.java:252-267`
  (the public PATCH route, the DIRECT book guard, and the command body) and
  `ClaimDetailService.java:351-361` (pass-through to the expert), and
  `ClaimCommands.java:123-129` (the `SettlementPayment` command with the
  nullable `paymentId`).
- `repos/eia-direct-claims-domain/.../ClaimDetailDtos.java:165-187` (the
  settlement projection with `paymentId` and `paymentLinkedAt`),
  `ClaimClient.java:332-349` (the expert PATCH call with the tenant and book
  headers), and `ApiExceptionHandler.java:88-113` (the expert 400/404/409
  remap, including the `CONFLICT` collapse).
- `repos/eia-direct-claims-expert/.../SettlementController.java:79-87` (the
  public and internal PATCH mapping) and `SettlementPaymentRequest.java:5-16`
  (the nullable `paymentId` contract).
- `repos/eia-direct-claims-expert/.../SettlementService.java:142-177` (the
  AUTHORIZED/EXECUTED gate, the same-value no-op, the claim and settlement
  version bumps, and the outbox insert) and
  `SettlementNotLinkableException.java:3-11` with
  `ApiExceptionHandler.java:83-91` (the 409 `SETTLEMENT_NOT_LINKABLE` code).
- `repos/eia-direct-claims-expert/.../SettlementRepository.java:137-164` (the
  compare-and-set link update, the null clear, and the settled status
  predicate) and `Settlement.java:18-39` (the projection members).
- `repos/eia-direct-claims-expert/src/main/resources/schema.sql:208-247`
  (`claim_settlement` with nullable `payment_id` and `payment_linked_at`, the
  status check, and the additive forward ALTERs).
- `repos/eia-direct-claims-expert/.../ClaimEvents.java:51-54,67,191-205` (the
  event name, the claim partition key, and the nullable `paymentId`/`linkedAt`
  payload members).
- Tests: `SettlementServiceTest` (the AUTHORIZED link, the EXECUTED unlink, the
  PROPOSED/REJECTED refusal, the tenant scope, and the repeat no-op),
  `DirectClaimsEndpointTest` (the public and internal routes, the null clear,
  and the 409 code), `DirectClaimsOutboxIntegrationTest` (the emitted payload
  and the unlink omission), `ClaimClientTest` (the PATCH body and link parsing),
  and `ClaimDetailControllerTest` (the public route, the book wall, and the
  preserved expert errors).
- `openapi/direct-claims.yaml` (1.10.0), `asyncapi/direct-claims.yaml`
  (1.5.0), and `asyncapi/event-catalog.yaml` (1.27.0) record the implemented
  shape; the README settlement-payment-link section and the validator require
  it.

Resolution: the implemented slice is documented as canonical for now. Closing
the gap means adding the SPEC route or amending SPEC 11.4.10, deciding whether a
settlement carries one payment or many, validating the Payment id against the
Payment service (existence, tenant, status, amount, and currency), implementing
the SPEC `PAID` settlement status, and either publishing a SPEC link fact or
recording the new name under the EV-05 rule. Renaming the route or the event is
breaking and needs an ADR and a `/v2` or dual-publish period. Aligning the
public error code with the expert's `SETTLEMENT_NOT_LINKABLE` is a service fix
that does not need a contract change.

## M-46 Payment public status command is SPEC-less and its graph is wider than SPEC 11.7.6

SPEC 11.7.11 lists named payment actions (`authorize`, `issue`, `confirm`,
`void`, `stop`, `reissue`, `reverse`) and no generic status route. The
2026-10-21 contract documents the implemented public
`PATCH /api/v1/payments/{paymentId}/status`, which forwards
`{status, expectedVersion?, reason?}` to the expert. The 2026-10-22 1.6.0
contract adds the latest status reason to the payment projection.

| Aspect | Implemented | SPEC / gap |
|---|---|---|
| Route | `PATCH /api/v1/payments/{paymentId}/status` (the M-01 short form) | SPEC 11.7.11 has no status route; its named actions are partly unimplemented (`confirm`, `void`, `stop`, `reissue`, and `reverse` remain planned). |
| Body | `UpdatePaymentStatusRequest` `{status, expectedVersion?, reason?}`; `status` is a `PaymentStatus`, `expectedVersion` an optional non-negative integer, and `reason` is optional at 200 characters | SPEC defines no generic transition body; the SPEC 11.7.6 lifecycle is a mermaid graph and the named actions carry no body in the SPEC table. |
| Graph | 34 edges from `DRAFT` through `RECONCILED`, with `CANCELLED`, `STOPPED`, `REJECTED`, `VOID`, `REVERSED`, and `ESCHEATED` terminal | The SPEC mermaid omits the CANCELLED/VOID escape edges, `SUBMITTED`/`ACCEPTED` -> `FAILED`, `PROCESSING` -> `PARTIALLY_PAID`, and the `PARTIALLY_PAID` edges; it also has no `VOID` state. The contract documents the implemented graph. |
| Approval gate | `DRAFT`, `PENDING_AUTHORITY`, and `AUTHORIZED` -> an execution status is 400 `PAYMENT_NOT_APPROVED` | SPEC 11.7.7 PAY-04 and PAY-18 require approval and no active hold; the implemented gate only checks the pre-approval source status and does not evaluate authority, SoD, sanctions, duplicate, or holds. |
| Concurrency | Optional `expectedVersion`; a stale value is 409 `CONCURRENT_MODIFICATION`; omitted means unchecked | SPEC 12.6 expects a version token on writes. The named payment actions send the version the domain read; the generic route is the only Payment command that accepts a caller version. |
| Reason | Optional, trimmed, stored in `payment.status_reason` (`varchar(200)`), returned as the required-but-nullable `Payment.statusReason`, and emitted in `payment.payment.status-changed` when non-blank | The SPEC named actions carry no reason field. The contract caps it at 200 characters; the expert's `@Size(max = 200)` now answers 400 `VALIDATION_ERROR` before persistence, but the public domain still forwards without pre-validating, so the 400 comes from the expert. Each accepted change replaces the value and a change without a reason clears it; there is no status history. |
| Events | `payment.payment.updated` and `payment.payment.status-changed` at the new row version | SPEC 11.7.10 publishes per-verb names such as `payment.payment.authorized` and `payment.payment.paid`; the two generic names are recorded in M-22. |
| Book | Not book-scoped; only `X-EIA-Tenant`; the event is stamped DIRECT | SPEC 3.6.1 requires the book on every payment; the payment row carries no book (M-08, M-12). |

Evidence:

- `repos/eia-payment-domain/.../PaymentController.java:74-79` (the public PATCH
  mapping) and `PaymentService.java:122-130` (forwarding without re-deriving the
  graph), plus `UpdatePaymentStatusCommand.java:5-13` (the body record),
  `PaymentDto.java:10-27` (the returned `statusReason`), and
  `PaymentClient.java:103-120,176-202` (the expert call and the preserved
  400/404/409 translation).
- `repos/eia-payment-expert/.../PaymentController.java:45-50` (the internal
  PATCH), `UpdatePaymentStatusRequest.java:6-10` (`@Size(max = 200)` on
  `reason`), `Payment.java:13-29` (the persisted `statusReason`),
  `PaymentService.java:65-81` (transition, version check, row update, and the
  two outbox writes), `PaymentRules.java:54-78,303-323` (`TRANSITIONS`, the
  execution statuses, and `validateTransition`), and
  `PaymentRepository.java:19-43,107-123,143-145` (the `status_reason` select,
  the trimmed update with the version bump and `CONCURRENT_MODIFICATION`, and
  the blank-to-null helper), plus `schema.sql:14`
  (`status_reason VARCHAR(200)`).
- `repos/eia-payment-expert/.../PaymentEvents.java:68-89`
  (`payment.payment.updated` and `payment.payment.status-changed`, with the
  optional trimmed `reason`).
- Tests: `PaymentStatusReasonIntegrationTest` (null on create, the trimmed
  round trip, clearing without a reason, and the 200-character value) and
  `PaymentControllerTest` (the returned reason and the 201-character 400
  `VALIDATION_ERROR`).
- `openapi/payment.yaml` 1.6.0, the README payment status sections, and the
  validator checks record the implemented shape.

Resolution: either add the generic status route and the widened graph to SPEC
11.7.6/11.7.11 (or record them as an agreed extension) or restrict the contract
to the SPEC mermaid and implement the remaining named actions. The approval
gate needs the authority, SoD, sanctions, duplicate, and hold checks from
SPEC 11.7.7. The 200-character reason limit is now enforced with 400
`VALIDATION_ERROR` and the projection returns the latest `statusReason`; a
public-boundary pre-check would still avoid the expert call, and a status-history
read (the SPEC 11.7.11 `/history` read) remains planned. A future `/v2` or an
EV-05 dual-publish window applies if a route or event name is renamed.

## M-47 Document content tombstones are a SPEC-less command and event, now also applied by disposition

SPEC 11.6.8 deletes content only as step 5 of the `document.dispose` approved
asynchronous transaction, after the retention and hold gates, an approval, and
a disposition certificate; SPEC 11.6.10 lists no content `DELETE` route and
SPEC 11.6.9 publishes no content-tombstone fact. The 2026-10-22 slice documents
the implemented tombstone:
`DELETE /api/v1/documents/{documentId}/content` clears the bytes of the current
pointer and every revision and keeps the metadata, and the expert publishes
`document.content.deleted`. The 2026-10-22 disposition-content slice makes
`POST /api/v1/documents/{documentId}/dispose` apply the same tombstone to live
content in the disposition transaction, so a disposition of a document with
content now performs SPEC 11.6.8's deletion step without its approval or
certificate.

| Aspect | Implemented | SPEC / gap |
|---|---|---|
| Route | `DELETE /api/v1/documents/{documentId}/content` (the M-01 short form), no request body; `POST .../dispose` reuses the same tombstone for live content | SPEC 11.6.8 deletes content inside `document.dispose`; SPEC 11.6.10 has no content-delete route |
| Success | 204 with no body; the content metadata stays readable; a disposition that tombstones content still answers 200 with the DISPOSED document | no standalone command |
| Tenant | `X-EIA-Tenant` required; a missing document or another tenant's document is 404 `NOT_FOUND`, indistinguishable | tenant wall (M-08) |
| Missing content | 404 `CONTENT_NOT_FOUND`; a disposition of a document with no content is a no-op that writes only `document.document.disposed` | not specified |
| Legal hold | 409 `DOCUMENT_ON_LEGAL_HOLD`; the bytes, `deletedAt`, and outbox are untouched (DOC-06); disposition checks the same hold before any content work | the SPEC blocks disposition under a hold; a standalone content delete is not modeled |
| Repeat | 409 `CONTENT_ALREADY_DELETED` from the stored `deletedAt`, checked before the hold; no second event; a disposition of already-tombstoned content is a no-op that writes only `document.document.disposed` | not specified |
| Storage effect | tombstone, not a row delete: `content = NULL` and `deleted_at` on the current pointer and every not-yet-deleted revision; filename, MIME type, size, digest, upload instant, and revision retained | SPEC step 5 deletes the content object |
| Downloads | current and revision bytes answer 410 `CONTENT_DELETED` after either trigger; the metadata and history routes remain 200 | not specified |
| Re-upload | a later upload clears the pointer tombstone and appends a fresh downloadable revision; earlier revisions keep their deletion timestamps | not specified |
| Event | `document.content.deleted`, payload `{documentId, documentNumber, fileName, sizeBytes, sha256, deletedAt}`, no `contentType` or `version`; aggregate `DocumentContent`, aggregate version = tombstoned revision, `eventVersion` 1. Emitted by the explicit delete and by a disposition of live content | SPEC 11.6.9 names no content-delete fact; M-22 records the name |
| Approval, certificate, disposition coupling | no approval or certificate; `POST .../dispose` applies the tombstone to live content in the same transaction, while absent or already-tombstoned content leaves it a disposed-only no-op | SPEC requires approval, a certificate with counts and hashes, and deletion as part of disposition |

Consequences:

- A caller can still clear the bytes of a document without the retention check,
  approval, or certificate that SPEC 11.6.8 requires for disposition. The only
  state guard on the standalone route is an active legal hold (DOC-06); any
  document that is not ON_HOLD can be tombstoned, including ACTIVE, ARCHIVED,
  and DISPOSED records. The disposition route additionally enforces the
  retention and status gates before it applies the same tombstone.
- The tombstone is reversible only by a new upload: the cleared revisions are
  not recoverable and keep their `deletedAt`, while the history and the retained
  digest and size remain available for audit and correlation.
- A consumer that expected the SPEC disposition to be the only content deletion
  must tolerate a `document.content.deleted` fact and the 410 response on both
  download routes. A disposition of live content now emits that fact together
  with `document.document.disposed`; a disposition with no content or
  already-tombstoned content emits only the disposed fact.
- The 409 and 410 bodies preserve the expert problem as
  `application/problem+json`; a missing tenant is still the compact
  `TENANT_REQUIRED` 400 (M-02).

Evidence:

- `repos/eia-document-domain/.../DocumentController.java:109-121` (public
  tombstone route and 204), `DocumentService.java:149-153` (pass-through), and
  `DocumentExpertClient.java:221-234` (the expert DELETE and preserved 4xx
  vocabulary).
- `repos/eia-document-expert/.../DocumentContentController.java:79-87` (the
  DELETE mapping), `DocumentContentService.java:77-93` (locked lookup,
  already-deleted guard, legal-hold rule, tombstone, and outbox),
  `DocumentContentRules.java:46-58` (DOC-06 hold block),
  `DocumentContentRepository.java:188-208` (the nullable-bytes `deleted_at`
  writes and the duplicate guard), and `ContentDeletedException.java` /
  `ContentAlreadyDeletedException.java` with
  `ApiExceptionHandler.java:42-52` (410 `CONTENT_DELETED` and 409
  `CONTENT_ALREADY_DELETED`).
- `repos/eia-document-expert/.../DocumentContentEvents.java:77-115` (name,
  payload, aggregate version, and DIRECT book) and
  `DocumentContentMetadata.java:20-33` (the nullable `deletedAt` and derived
  `deleted`).
- `repos/eia-document-expert/src/main/resources/schema.sql` (nullable `content`
  and `deleted_at` on both content tables),
  `DocumentContentDeletionIntegrationTest` (tombstone, 410 downloads, hold
  block, repeat conflict, tenant wall, outbox payload, re-upload, rollback, and
  idempotent DDL), and `DocumentDispositionContentTombstoneIntegrationTest` /
  `DocumentLegalHoldIntegrationTest` (the disposition coupling, both facts, the
  no-content/already-tombstoned no-op, legal-hold rejection, and rollback).
- `repos/eia-document-expert/.../DocumentService.java:209-256` (the disposition
  use case and `tombstoneContentForDisposal`).
- `openapi/document.yaml` 1.7.0, `asyncapi/document.yaml` 1.7.0, and
  `asyncapi/event-catalog.yaml` 1.29.0 record the implemented shape.

Resolution: either implement the SPEC 11.6.8 approval and certificate workflow
and the remaining hold/litigation gates around the now-coupled deletion, or
amend SPEC 11.6.8/11.6.10 to the standalone-plus-disposition tombstone and add
the fact to SPEC 11.6.9. Renaming the route or event is
breaking and needs an ADR and a `/v2` or EV-05 dual-publish window.

## M-48 Notifications adds a SPEC-less `DUNNING_NOTICE` type to the closed enum

SPEC 11.8.5 v1 enumerates `NotificationType` by category and ends the Payment
category at `ESCHEATMENT_DUE`; the next member is Document's
`NEW_DOCUMENT_UPLOAD`, and no dunning or collections type is named. The
2026-10-22 notifications pass adds the implemented `DUNNING_NOTICE` member
between those two values and accepts it on both create commands.

| Aspect | Implemented | SPEC / gap |
|---|---|---|
| Type | `DUNNING_NOTICE` in the closed `NotificationType` enum, between `ESCHEATMENT_DUE` and `NEW_DOCUMENT_UPLOAD` | SPEC 11.8.5 v1 lists no dunning escalation type |
| Validation | the expert calls `NotificationType.from(...)` and rejects an unknown value with 400 `EIA-NTF-9403` `INVALID_NOTIFICATION_TYPE`; the domain enum carries the same 84 values in the same order | SPEC 11.8.5 is a closed v1 list; an addition is an additive minor change under SPEC 10.4 and a removal is breaking |
| Create and projection | both create commands and the `Notification` projection reference the one `NotificationType` schema and require `notificationType` | no SPEC shape change: the type rides the existing create and read |
| Use | the shell receivables page opens the Notifications workbench with `notificationType=DUNNING_NOTICE`; the web remote lists the value and leaves the template empty for it | SPEC 11.2.13 models dunning levels on the billing account and names no notification; the hand-off creates a draft only and Notifications owns the send |
| Version | `openapi/notifications.yaml` 1.2.0 (additive) | no SPEC version has the type |

Consequences:

- A client generated from SPEC 11.8.5 alone will not know the type; a client
  generated from the OpenAPI enum will. No path, request field, response field,
  or event changes, so existing clients are unaffected.
- The type is accepted for any channel and template; a `DUNNING_NOTICE` draft
  does not require a dedicated template, and a send still requires an approved
  template for the tenant and channel (NTF-01, NTF-14).
- The type is a notification label, not a dunning command: creating it does not
  advance `billing_account.dunning_status` or emit `policy.dunning.sent`
  (M-38).
- The expert and domain enums are hand-maintained copies; a future type must be
  added to both services, the web list, and this contract together.

Evidence:

- `repos/eia-notifications-expert/.../NotificationType.java:69`
  (`DUNNING_NOTICE`) and `NotificationService.java:48`
  (`NotificationType.from`), with `ErrorCode.java:20` (400 `EIA-NTF-9403`
  `INVALID_NOTIFICATION_TYPE`).
- `repos/eia-notifications-domain/.../NotificationType.java:69` (the same
  member on the domain copy).
- `repos/eia-notifications-expert/src/test/java/com/eia/notifications/expert/NotificationControllerTest.java:101`,
  `NotificationServiceTest.java:98`, and
  `NotificationOutboxIntegrationTest.java:98-105` (create, persist, and outbox
  round trip).
- `repos/eia-notifications-web/src/App.jsx:19` and `:137` (the type list and the
  empty template for a dunning prefill), with `README.md:51`.
- `repos/eia-frontend/shell/src/receivables.js:32-33` (the dunning
  notification-type and template constants) and `:193` (the prefill link, which
  sends the type and no template code), with `ReceivablesPage.jsx:214` (the
  draft-only hand-off label).
- `openapi/notifications.yaml` 1.2.0 records the closed enum and the member.

Resolution: add `DUNNING_NOTICE` to SPEC 11.8.5 v1 (for example a Collections
category or the Payment category after `ESCHEATMENT_DUE`) and name the dunning
hand-off in SPEC 11.2.13, or keep the implemented type and treat the OpenAPI
enum as canonical. The addition needs no `/v2`; removing the member later would
be breaking under SPEC 10.4.

## M-49 Notification template administration uses a short path, approve/retire commands, SPEC-less events, and a directory-id approver

SPEC 11.8.10 mounts the template administration surface at
`GET /api/v1/notifications/admin/templates` and names
`POST .../admin/templates/{templateId}/publish` for activation. The implemented
registry is the short `/api/v1/notifications/templates` resource: list, create
DRAFT, approve, and retire. Approval is the only path to ACTIVE (NTF-14), and
retirement is a separate command from DRAFT or ACTIVE. The three lifecycle
facts are new names with no SPEC 11.8.9 equivalent. The approver is a directory
identifier such as `a-adjuster`, while SPEC 11.8.7 types
`notification_template.approved_by` as `uuid`.

| Aspect | Implemented | SPEC / gap |
|---|---|---|
| Path | `/api/v1/notifications/templates` for the collection, `.../{id}/approve`, and `.../{id}/retire` | SPEC 11.8.10 mounts `/api/v1/notifications/admin/templates` and a publish command |
| Lifecycle | create always DRAFT; approve DRAFT -> ACTIVE with `approvedBy`/`approvedAt`; retire DRAFT or ACTIVE -> RETIRED (terminal); duplicate create 409 `TEMPLATE_ALREADY_EXISTS`, repeat approval 409 `TEMPLATE_ALREADY_ACTIVE`, other illegal transition or concurrent loss 409 `TEMPLATE_STATUS_CONFLICT` | SPEC 11.8.10 names publish, not a draft/approve/retire split; the stable conflict codes are the implementation's |
| Approver | `approvedBy` is a trimmed, non-blank 1-128-character directory identifier such as `a-adjuster`, stored in `notification_template.approved_by VARCHAR(128)`; the request requires it, the projection returns it nullable, and the approved event carries the trimmed string | SPEC 11.8.7 types `approved_by` as `uuid`; the implemented column and the canonical contract use a directory id |
| Projection | `NotificationTemplate` `{id, code, version, channel, locale, bodyTemplate, status, approvedBy, approvedAt, createdAt, updatedAt}`; tenant id and effective dates are hidden; a null channel means channel-neutral | SPEC 11.8.7 describes a template registry with effective dates and a channel; the public projection omits tenant and effective dating |
| List | bare array ordered by `createdAt` newest first, then `code`, `version` descending, and `id`; optional exact `status` and `code` filters | SPEC 11.8.10 names no list filter or ordering |
| Events | `notifications.template.created` (aggregate version 1), `.approved` (2), `.retired` (3), payload `{templateId, code, version, locale, status, approvedBy}` | SPEC 11.8.9 publishes notification lifecycle facts only; no template event |
| Version | `openapi/notifications.yaml` 1.8.0, `asyncapi/notifications.yaml` 1.6.0, `asyncapi/event-catalog.yaml` 1.39.0 (corrective/additive) | no SPEC version has this surface |

Consequences:

- A client generated from SPEC 11.8.10 alone would call the admin path and
  publish; the implemented client calls the short path and approve/retire.
- `Notification.templateCode`/`templateVersion` still resolve an approved
  ACTIVE template for the tenant and channel (NTF-01). Retirement removes a
  template from the eligible set but does not rewrite notifications that
  already reference it.
- A template that is channel-neutral (`channel` null) can serve any channel; a
  channel-specific row wins over the neutral row, matching
  `NotificationTemplateRepository.find`.
- The approver is a directory identifier, not a UUID. A client generated from
  SPEC 11.8.7 that types `approved_by` as a UUID must be regenerated to send and
  accept a directory id; a UUID string remains a valid 1-128-character value.
  Existing rows migrate forward with
  `ALTER COLUMN approved_by TYPE VARCHAR(128) USING approved_by::text`, so the
  old UUID text is preserved rather than dropped.
- The three events are additive; the catalog publishes and implements them and
  the validator requires them. Renaming one later is breaking under EV-05.

Evidence:

- `repos/eia-notifications-domain/.../NotificationTemplateController.java:32-57`
  (list, create, approve, retire), `NotificationTemplateService.java:41-50`
  (approvedBy required and forwarded), `ApproveNotificationTemplateCommand.java`
  (String approver), and `NotificationTemplateDto.java:11-23`.
- `repos/eia-notifications-expert/.../NotificationTemplateController.java:39-74`
  (the public and `/internal/v1` mappings), `NotificationTemplateService.java:78-160`
  (trim, non-blank, 128-character validation, and the ACTIVE/STATUS guards),
  `NotificationTemplateRepository.java:76-147`
  (ordering, string `markApproved`, and conditional updates),
  `ApproveNotificationTemplateRequest.java` (String `approvedBy`),
  `NotificationTemplate.java:14-27`, `NotificationTemplateDto.java:10-23`, and
  `schema.sql:6-38` (VARCHAR(128) column, unique key, status/approval checks,
  and the forward-only UUID-to-text migration).
- `repos/eia-notifications-expert/.../NotificationTemplateEvents.java:26-28,50-91`
  (names, aggregate versions, and the string approver payload).
- `repos/eia-notifications-domain/.../NotificationExpertClient.java:90-156`
  (list/create/approve/retire forwarding and problem translation).
- `repos/eia-notifications-expert/src/test/java/com/eia/notifications/expert/NotificationTemplateControllerTest.java`,
  `NotificationTemplateServiceTest.java`, and `NotificationTemplateIntegrationTest.java`
  (directory-id approval, trimming, blank and 129-character rejection, the
  128-character acceptance, and the VARCHAR(128) column assertion).
- `repos/eia-notifications-web/src/TemplatesPanel.jsx` and
  `tests/approver-directory.spec.js` (the directory-backed approver picker that
  posts the directory person id as `approvedBy`).

Resolution: either move the route and command shape to SPEC 11.8.10
(publish -> approve, admin -> short path, and add the retire command), publish
the three template facts in SPEC 11.8.9, and widen SPEC 11.8.7's `approved_by`
to a directory-id string, or keep the implemented surface and treat these
documents as canonical. No `/v2` is needed; the surface is additive over the
existing notification API and the approver field was already a JSON string.

## M-50 Policy premium audit is a SPEC-less route and event without the SPEC audit worksheet

SPEC 6.12 lists the `policy.premium-audit` transaction
(`APPLY_PREMIUM_AUDIT`, conditional approval, synchronous), and SPEC 11.2.8's
command sections define the other policy commands but not the audit steps.
SPEC 11.2.4 defines the `policy_premium_audit` table
(audit period, audit type, reported exposure, deposit/rated/additional/return
premium, minimum-premium flag, audit date, and a SCHEDULED/IN_REVIEW/FINALIZED/
DISPUTED/WAIVED status), SPEC 7.3 schedules a quarterly
`policy.premium-audit-batch` worksheet job, and SPEC 11.2.9 publishes
`policy.premium.audited`. SPEC 11.2.10 names no premium-audit route. The
2026-10-22 slice implements the command as a policy re-rating:

| Aspect | Implemented | SPEC / gap |
|---|---|---|
| Route | `POST /api/v1/policies/{policyId}/premium-audit` (and the expert's `/internal/v1` alias) | SPEC 11.2.10 lists no premium-audit route; the SPEC 6.12 transaction inventory names `policy.premium-audit` (M-01) |
| Body | `{auditedPremium, effectiveDate, reason, approvedBy?, approvalRef?}` | SPEC models an audit worksheet, not an audited-premium command |
| Subject | The policy premium itself: `auditedPremium` replaces `policy.premium_amount` | SPEC separates the worksheet (`reported_exposure`, `deposit_premium`, `rated_premium`, `additional_premium`, `return_premium`) from the policy premium |
| Eligibility | `BOUND`, `ISSUED`, `IN_FORCE`, `ENDORSED`, `REINSTATED`; another status is 409 `PREMIUM_AUDIT_NOT_ALLOWED` | SPEC defines no eligible-status set for the command; the conditional approval is keyed to financial impact |
| No-op | A zero premium movement is 400 `NO_PREMIUM_CHANGE` and writes nothing | SPEC has no no-change guard; a FINALIZED worksheet with zero movement is meaningful |
| Version and endorsement | Records a `PREMIUM_AUDIT` endorsement and an immutable `PREMIUM_AUDIT` policy version with the signed delta, description `Premium audit: old -> new (delta)`, and a bumped aggregate version; coverage and limits are untouched | SPEC 11.2.4 has the `PREMIUM_AUDIT` change type but no endorsement type; the SPEC worksheet is not a version by itself |
| Approval | `approvedBy`/`approvalRef` are optional and required only for a pre-inception or regressing effective date (428 `APPROVAL_REQUIRED`) | SPEC flags the command `Yes*` (conditional approval by financial impact); no approval is required for a normal in-term audit |
| Timeline | `effectiveDate` is resolved by `VersionTimeline`: 422 `VERSION_OUTSIDE_POLICY_TERM`, `VERSION_REGRESSION` (unjustified), or `VERSION_BACKDATE_REASON_REQUIRED`; a justified pre-inception date is clamped to policy inception on the version | SPEC names no version-timeline rule for the audit |
| Concurrency | Optional `If-Match`; a stale tag is 409 `CONCURRENT_MODIFICATION`; an optional `Idempotency-Key` is forwarded but not replayed, so the command is not retry-safe | SPEC 12.6 requires the header on transaction submission |
| Worksheet | No `policy_premium_audit` row is created; no audit period, audit type, exposure, deposit/rated/additional/return premium, minimum-premium flag, audit date, or SCHEDULED..WAIVED status is stored | SPEC 11.2.4 defines all of them; the batch job that generates the worksheets is not implemented either |
| Event | `policy.policy.premium-audited`, payload `{policyId, policyNumber, previousPremium, auditedPremium, delta, currency, effectiveDate, reason}`, emitted with `policy.policy.version-issued` in the same transaction | SPEC 11.2.9 publishes `policy.premium.audited`; the implemented name is new and the SPEC name stays planned (M-22) |
| Version | `openapi/policy.yaml` 2.15.0, `asyncapi/policy.yaml` 1.12.0, `asyncapi/event-catalog.yaml` 1.32.0 (additive) | no SPEC version has this command |

Consequences:

- A client generated from SPEC 11.2.9 alone would subscribe to
  `policy.premium.audited`; the expert emits `policy.policy.premium-audited`.
  The catalog keeps the SPEC name published and planned and adds the
  implemented name, so a later alignment can add a dual-publish window (EV-05)
  without breaking implemented consumers.
- The audit is not a worksheet lifecycle: there is no SCHEDULED/IN_REVIEW/
  FINALIZED/DISPUTED/WAIVED state, no audit period or audit type, no reported
  exposure, and no separate deposit, rated, additional, or return premium. The
  only persisted evidence is the `PREMIUM_AUDIT` endorsement and version, whose
  description carries the old premium, the new premium, and the delta.
- The approval gate protects the version timeline (a pre-inception or regressing
  date), not the premium movement; a large in-term increase or decrease is
  accepted without approval. The SPEC `Yes*` conditional approval is therefore
  not modelled.
- `auditedPremium` is the final written premium, not an additional or return
  premium. A decrease is accepted and persisted as a signed negative delta on
  the endorsement and version, and the event carries the negative `delta`.
- There is no `policy.premium-audit-batch` quarterly job and no worksheet
  generation, so an audit cannot be scheduled or reviewed before it is applied.

Evidence:

- `repos/eia-policy-domain/.../PolicyPremiumAuditController.java:25,38-63`
  (public path, tenant/book/`If-Match`/`Idempotency-Key` headers, 201/200
  publication and `ETag` fallback), `PolicyPremiumAuditService.java:21-27`
  (delegation and header validation),
  `ApplyPremiumAuditCommand.java:23-31` (shape validation and optional
  approval), `PremiumAuditResult.java`, and `PremiumAuditDto.java`.
- `repos/eia-policy-domain/.../PolicyClient.java:333-397` (`/internal/v1` call,
  tenant/DIRECT/book headers, bare-policy and envelope projection, expert
  `id`/alias handling).
- `repos/eia-policy-expert/.../PremiumAuditController.java:22-45` (public and
  internal aliases, 201, `ETag`), `PremiumAuditService.java:55-102` (guard,
  status gate, no-change gate, timeline resolution, endorsement, premium update,
  version issue, and outbox writes), `PremiumAuditRules.java:16-92` (auditable
  statuses, reasons, delta, no-change, and description),
  `PremiumAuditRequest.java:23-31`, and `VersionTimeline.java:46-88`
  (backdate, term, and regression rules).
- `repos/eia-policy-expert/.../PolicyEvents.java:42,436-455,483-496`
  (`PREMIUM_AUDITED` name, the eight-member `premiumAudited` payload, and the
  concurrent `versionIssued` fact).
- Tests: `PremiumAuditControllerTest`, `PremiumAuditServiceTest`, and
  `PremiumAuditIntegrationTest` in the expert; `PolicyPremiumAuditControllerTest`
  and `PolicyPremiumAuditServiceTest` in the domain.
- `openapi/policy.yaml` 2.15.0, `asyncapi/policy.yaml` 1.12.0, and
  `asyncapi/event-catalog.yaml` 1.32.0 record the implemented shape; the
  policy-web premium-audit modal posts the same body and `If-Match`
  (`repos/eia-policy-web/src/premiumAudit.js`,
  `App.jsx`, and `tests/premium-audit.spec.js`).

Resolution: the audited-premium command is canonical for now. Closing the gap
means persisting the SPEC `policy_premium_audit` worksheet with its audit
period, type, exposure, premium buckets, minimum-premium flag, and status
lifecycle, adding the quarterly worksheet batch job, and deciding whether the
worksheet or the immediate re-rating is the posting unit. Renaming
`policy.policy.premium-audited` to `policy.premium.audited` requires the EV-05
dual-publish window; publishing both is additive. Adding the approval gate for
a material in-term premium movement is a behaviour change and needs its own
contract version.

## M-51 Policy billing adjustment is a SPEC-less derived-delta route and event

SPEC 11.2.13 defines the installment plan as the billing surface, and BIL-05
requires a premium change to be a credit note or an additional invoice; it names
no positive premium adjustment command and no adjustment event. The 2026-10-22
slice implements the command on the billing resource:

| Aspect | Implemented | SPEC / gap |
|---|---|---|
| Route | `POST /api/v1/policies/{policyId}/billing/adjustment` (and the expert's `/internal/v1` alias) | No SPEC 11.2.10 or 11.2.13 adjustment row (M-01, M-27) |
| Body | `{dueDate, reason}` | No SPEC command; BIL-05 describes the ledger outcome, not an installment append |
| Amount | Derived, not supplied: policy written premium less the plan's net premium (total less applied credits, floored at zero). A non-positive remainder is 400 `NO_PREMIUM_ADJUSTMENT` with `meta.delta`, `meta.policyPremiumAmount`, `meta.planTotalPremium`, `meta.creditedAmount`, and `meta.netPlanPremium` | No SPEC formula; BIL-02 requires installments to sum to premium and BIL-06 defines the outstanding rule |
| Gates | Existing ACTIVE plan below the 24-installment ceiling. Missing plan 404 `BILLING_PLAN_NOT_FOUND`, non-ACTIVE 409 `BILLING_PLAN_NOT_ACTIVE`, full schedule 409 `MAX_INSTALLMENTS_REACHED` | No SPEC plan-status or installment-count gate |
| Due date and reason | `dueDate` required and not before the policy effective date (the effective date itself is accepted); `reason` required, trimmed, 1-500 characters | No SPEC fields |
| Concurrency | Optional `If-Match` and `Idempotency-Key` are validated by the domain and forwarded, but the expert neither compares the tag nor replays the key, so a retry appends a second installment | SPEC 7.6/12.6 require the headers on mutations |
| Effect | Appends one DUE installment at `plan.installmentCount + 1`, grows the gross plan total by the adjustment amount and the count by one, bumps the policy version, and writes the event in one transaction | BIL-05 says the original SAP invoice is never edited; the implemented plan total is a platform projection, not a SAP invoice |
| Event | `policy.billing-plan.adjusted`, payload `{policyId, policyNumber, planId, adjustmentAmount, newTotalPremium, installmentId, installmentNumber, dueDate, reason}`, emitted in the same transaction | No SPEC 11.2.13 name (M-22) |
| Version | `openapi/policy.yaml` 2.16.0, `asyncapi/policy.yaml` 1.13.0, `asyncapi/event-catalog.yaml` 1.33.0 (additive) | no SPEC version has this command |

Consequences:

- A positive premium movement is billed by appending an installment, while a
  negative movement remains a credit note. SPEC BIL-05 frames both directions as
  a credit note or additional invoice, so a client cannot infer the adjustment
  from the SPEC alone.
- The command bills only the gap between the policy premium and the plan's net
  premium, so it is not a generic "add installment" API: applying credits first
  shrinks the derived amount, and a fully credited plan causes the whole policy
  premium to be billed again on a gross plan total that exceeds the written
  premium (the net total still matches).
- Because the expert does not honour `If-Match` or `Idempotency-Key`, a retry
  appends a duplicate installment. The command must be treated as
  non-idempotent until M-06 and M-07 are closed for it.
- The 201 `plan` member intentionally omits the schedule; its `summary` is
  derived from an empty list, so `summary.installmentCount` and
  `summary.outstandingAmount` are zero. `plan.installmentCount`,
  `plan.totalPremium`, `adjustmentAmount`, and `newTotalPremium` are the
  authoritative totals, and a full schedule requires
  `GET /api/v1/policies/{policyId}/billing`.

Evidence:

- `repos/eia-policy-domain/.../PolicyBillingController.java:68-87` (public
  path, tenant/book headers, optional `If-Match`/`Idempotency-Key`, 201/200
  publication and `ETag`), `PolicyBillingService.java:32-44` (header
  validation and forwarding), `BillingAdjustmentCommand.java`,
  `BillingAdjustmentResult.java`, and `PolicyClient.java:460-495` and
  `:988-1009` (`/internal/v1` call and envelope projection).
- `repos/eia-policy-expert/.../BillingController.java:48-59` (POST
  `/adjustment`), `BillingService.java:151-211` (delta, plan update, appended
  installment, rollback, event), `BillingRules.java:76-174` (ACTIVE,
  24-installment, due-date, reason, and non-positive-delta rules),
  `BillingRepository.java:124-164` (conditional plan update and credited
  total), `BillingAdjustmentRequest.java`, `BillingAdjustmentView.java`, and
  `PolicyEvents.java:100-125` (adjusted payload).
- Tests: `PolicyBillingControllerTest`, `PolicyBillingAdjustmentServiceTest`,
  and `PolicyBillingAdjustmentClientTest` in the domain;
  `BillingAdjustmentServiceTest` and `BillingRulesTest` in the expert.
- `openapi/policy.yaml` 2.16.0, `asyncapi/policy.yaml` 1.13.0, and
  `asyncapi/event-catalog.yaml` 1.33.0 record the implemented shape.

Resolution: the positive adjustment command is canonical for now. Closing the
gap means deciding whether SPEC BIL-05 should recognize an installment append
for a positive premium movement, defining a SPEC event name (EV-05 dual publish
if the implemented name stays), and honouring `If-Match` and replaying
`Idempotency-Key` in the expert. The derived-delta rule and the 24-installment
ceiling are implementation choices with no SPEC counterpart; changing either is
a behaviour change and needs its own contract version.

## M-52 Direct Claims litigation damages are a SPEC-less pair and the created event has no SPEC name

SPEC 11.4.4 `claim_litigation` defines the matter number, case number, court,
jurisdiction, venue, judge, filing and trial dates, phase, status, lead and
outside counsel, MDL number, class and bellwether flags, discovery and mediation
dates, and the verdict, judgment, appeal, bond, and litigation-budget amounts.
It defines no `damages_sought` or `damages_currency` column, and SPEC 11.4.9
publishes `direct.claim.litigation-updated` with no matter-creation fact. The
2026-10-22 slice adds the optional pair and the created event:

| Aspect | Implemented | SPEC / gap |
|---|---|---|
| Columns | `claim_litigation.damages_sought NUMERIC(19,4)` and `damages_currency CHAR(3)`, with the `ck_litigation_damages` check that the pair is both-null or both-present-and-positive | No SPEC 11.4.4 column; SPEC records only verdict, judgment, appeal, bond, and budget amounts |
| Request and projection | Optional/nullable `damagesSought` and `damagesCurrency` on `LitigationRequest` and `Litigation`; both present together when damages are recorded, both null otherwise | No SPEC field or pair rule |
| Amount | Decimal string greater than zero, normalized to four fraction digits; zero or a negative amount is 400 `VALIDATION_ERROR`. The canonical schema never uses a JSON number | No SPEC field |
| Currency | Uppercase ISO 4217 alpha-3, three letters; the expert normalizes a supplied internal value to uppercase | No SPEC field |
| Pair rule | Supplying one member without the other is 400 `VALIDATION_ERROR`; a PATCH that omits both (or sends both null) keeps the stored pair | No SPEC field |
| Routes | The existing `POST /api/v1/claims/{claimId}/litigation`, `PATCH .../litigation/{litigationId}`, and the two `/internal/v1` expert aliases | SPEC 11.4.10 lists the litigation GET and POST only and has no update route |
| Events | `direct.claim.litigation-created` (new, SPEC-less) and `direct.claim.litigation-updated` (SPEC name, previously planned), both emitted in the same transaction as the matter write and the claim version bump | SPEC 11.4.9 names only the updated fact |
| Payload | `claimId`, `claimNumber`, `claimVersion` (serialized as `version`), `litigationId`, `matterType`, `jurisdiction`, `counselPartyId`, `filingDate`, `litigationStatus`, `litigationVersion`, and, when non-null, `trialDate`, `caseNumber`, `damagesSought`, and `damagesCurrency` | No SPEC payload for the created fact; the updated fact had no payload contract while planned |
| Version | `openapi/direct-claims.yaml` 1.11.0, `asyncapi/direct-claims.yaml` 1.6.0, `asyncapi/event-catalog.yaml` 1.34.0 (all additive) | No SPEC version defines the pair or the created fact |

Consequences:

- A consumer cannot discover the damages fields or the created event from SPEC
  11.4.4/11.4.9 alone. They are additive under EV-05: `damagesSought` and
  `damagesCurrency` are optional, so a client that omits both sees the previous
  matter shape, and the new event adds one published name without renaming or
  removing an existing name.
- The pair is stored and returned together. There is no way to clear recorded
  damages through the PATCH: omitting both keeps them, and supplying both
  replaces them. Clearing would need a separate command or an explicit null-pair
  convention, which the current slice does not define.
- The public domain's bean validation admits a zero amount
  (`@DecimalMin("0.00")`) and a one-sided pair; `ClaimDetailService` only
  requires a non-negative amount and a non-blank currency and forwards the
  command. The expert enforces `amount > 0` and the both-or-neither pair, so the
  public response is still 400 `VALIDATION_ERROR`, but the rejection comes from
  the expert rather than the domain. A direct `/internal/v1` caller sees the
  expert rule.
- The public `LitigationRequest` also rejects a lowercase currency with the
  `@Pattern("[A-Z]{3}")` rule before forwarding, while the expert would
  normalize it. The contract documents the uppercase public rule; an internal
  caller may send lowercase and receive the normalized uppercase value.
- `direct.claim.litigation-created` has no SPEC name. If SPEC 11.4.9 later adds
  a matter-creation fact, aligning the implemented name needs the EV-05
  dual-publish window; publishing both names is additive.

Evidence:

- `repos/eia-direct-claims-expert/.../LitigationRequest.java:8-24`,
  `LitigationMatter.java:10-32`, `LitigationService.java:51-153` (pair and
  positive-amount rules, upsert and update semantics),
  `LitigationRepository.java:17-115`, `ClaimEvents.java:308-351` (both event
  factories and the litigation payload members plus the optional damages
  pair), and `schema.sql:185-220` (columns and the `ck_litigation_damages`
  check, including the ADD COLUMN/constraint backfill).
- `repos/eia-direct-claims-domain/.../ClaimCommands.java:90-115` (nullable
  command members and `@DecimalMin`/`@Pattern`), `ClaimDetailDtos.java:148-170`
  (decimal-string projection), `ClaimDetailService.java:300-333` (domain
  pre-validation), `ClaimDetailController.java:174-205` (public POST/PATCH),
  and `ClaimClient.java:257-297` (internal calls).
- Tests: `LitigationIntegrationTest.java:48-237` (damages create/update,
  omission, unpaired and non-positive rejection, DDL check, tenant scoping, and
  the two event payloads), `LitigationServiceTest.java`, and
  `DirectClaimsEndpointTest.java:284-380` in the expert; `ClaimDetailServiceTest.java:501-575`,
  `ClaimDetailControllerTest.java:503-595`, and `ClaimClientTest.java:805-884`
  in the domain.
- `openapi/direct-claims.yaml` 1.11.0, `asyncapi/direct-claims.yaml` 1.6.0, and
  `asyncapi/event-catalog.yaml` 1.34.0 record the implemented shape.

Resolution: the optional damages pair and the created event are canonical for
now. Closing the pair gap means adding the two columns and their rule to SPEC
11.4.4; closing the event gap means adding a matter-creation fact to SPEC
11.4.9 or renaming the implemented name under EV-05. Tightening the public
domain's own validation to `> 0` and the both-or-neither rule would move the
400 to the domain without changing the wire contract, and needs no contract
version. Clearing recorded damages or accepting a null pair as a clear is a new
command and needs its own contract version.

## M-53 Notification source linkage and list filter are a flat SPEC-less triple and an exact pair rather than the SPEC subject reference

SPEC 11.8.4 `notification` defines `subject_vertical`, `subject_type`,
`subject_id`, and the optional `subject_business_key` and `subject_display`
columns; SPEC 12.5.5 renders the subject as an `EntityRef`. The 2026-10-22
Notifications source-linkage slice instead adds a flat optional
`sourceType`/`sourceId`/`sourceReference` link to the projection and both create
commands, and the two implemented notification facts carry each present member.
The source-filter slice adds an optional `sourceType` + `sourceId` query pair to
both notification list operations; the pair is exact and tenant-scoped, and the
filter is likewise SPEC-less.

| Aspect | Implemented | SPEC / gap |
|---|---|---|
| Fields | Optional nullable `sourceType`, `sourceId`, and `sourceReference` on `Notification`, `CreateNotificationRequest`, and `CreateNotificationRequestInternal` | `subject_vertical`, `subject_type`, and `subject_id` are required; the business key and display label are separate members |
| Enum | `DIRECT_CLAIM`, `ASSUMED_CLAIM`, `POLICY`, `CONTRACT`, `PAYMENT`, `CESSION`, `RETROCESSION`, `DOCUMENT`, `PARTY`, `OTHER` | `subject_vertical` is the vertical slug (`policy`, `contract`, `direct`, `assumed`, `document`, `payment`, `notifications`, ...); there is no `OTHER` and no business-object type such as a claim |
| Pair rule | `sourceType` and `sourceId` are both-or-neither; every one of the ten types requires an id; a reference-only link needs neither | SPEC requires all three subject identity members, with only the business key and display label optional |
| Reference | `sourceReference` is a trimmed, 64-character human label; a blank value is absent | `subject_business_key` is `varchar(64)` and `subject_display` is `varchar(300)`; neither is a substitute for the id |
| Validation | The expert trims/upper-cases the type and rejects an unknown type with 400 `EIA-NTF-9409` `INVALID_SOURCE_TYPE`, half a pair with 400 `EIA-NTF-9410` `INVALID_SOURCE_LINKAGE`, and an over-long reference with 400 `EIA-NTF-9411` `INVALID_SOURCE_REFERENCE`; the domain forwards the link and preserves the expert problem | No SPEC error-code assignment and no SPEC source field |
| List filter | `GET /api/v1/notifications` and `GET /internal/v1/notifications` accept an optional `sourceType` + `sourceId` query pair, normalized and matched exactly, tenant-scoped and newest-first; half a pair is 400 `EIA-NTF-9412` `INVALID_SOURCE_FILTER`, an unknown type is 400 `EIA-NTF-9409` `INVALID_SOURCE_TYPE`, and a non-UUID id is 400 `EIA-NTF-9502` (expert `INVALID_ARGUMENT`) | No SPEC list filter over the subject columns; the SPEC 11.8.10 inbox filters are a different surface |
| Existence check | None: `sourceId` is a plain UUID with no foreign key and is not resolved against the claim, policy, contract, payment, cession, retrocession, document, party, or other source vertical | SPEC 8.3.7 models notification-subject links with typed endpoints and records `NOTIFICATION_ABOUT` |
| Events | `notifications.notification.created` and `.sent` carry each present member in `data` and omit all three when unlinked; `eventVersion` stays 1 | SPEC 11.8.9 names `issued`/`delivered` and the remaining lifecycle verbs, not these implemented names, and defines no payload schema |
| Version | `openapi/notifications.yaml` 1.6.0 and `asyncapi/notifications.yaml` 1.4.0 (additive) | No SPEC version defines the flat link |

Consequences:

- A client generated from SPEC 11.8.4/12.5.5 expects a typed `subject` object;
  the implemented contract returns `sourceType`/`sourceId`/`sourceReference`.
  Both the create commands and the projection use the flat form, so a client
  that omits the link sees no required-field break and a consumer that ignores
  the event members keeps working.
- The flat type is a business-object classification, not a SPEC vertical slug:
  the ten-value set names both claims, the policy, contract, and payment
  aggregates, the two reinsurance cases, documents, parties, and the
  unclassified `OTHER`, whereas the SPEC `subject_vertical` uses the vertical
  slugs (`direct`, `assumed`, `policy`, `contract`, `cession`, `retrocession`,
  `document`, `payment`, `party`, `notifications`, ...) and has no business-object
  type such as a claim. `OTHER` is the escape hatch that still requires an id
  and stays last in the enum.
- `sourceReference` may stand alone, which has no direct SPEC counterpart: it
  records a human label without a typed subject. It never replaces `sourceId`
  for a typed source.
- The list filter is an exact-pair extension over the flat link: it cannot list
  every notification of one type, `OTHER` is filterable only with an id, and a
  blank member counts as absent (a blank type with a supplied id is the same 400
  as a missing type). Because the expert binds `sourceId` as a UUID before the
  pairing rule, a malformed id is 400 `EIA-NTF-9502` (the expert's
  `INVALID_ARGUMENT`) even when no type is supplied; the domain uses the same
  numeric code for a malformed tenant header (`INVALID_TENANT`), so the title
  and detail, not the code alone, distinguish the two causes.
- Because there is no existence check, a notification can point at a missing or
  cross-tenant source id. The tenant-scoped notification row remains the
  authority; the link is correlation metadata, not a referential constraint.
- Adding the SPEC columns later would be additive and could coexist with the
  flat link. Removing or renaming the implemented members is breaking under
  SPEC 10.4 and needs a major contract version.

Evidence:

- `repos/eia-notifications-expert/.../NotificationSourceType.java:15-41`
  (closed enum and trim/upper-case `normalize`),
  `NotificationService.java:63-93` (both-or-neither, blank-to-null, 64-character
  reference), `Notification.java:28-30`, `CreateNotificationRequest.java:25-27`,
  `NotificationEvents.java:63,80,85-100` (each present member in the created and
  sent `data` object), `ErrorCode.java:29-31`, and `schema.sql:66-80` (the three
  nullable columns, pair comment, and 64-character reference).
- `repos/eia-notifications-domain/.../CreateNotificationCommand.java:18-30`,
  `NotificationDto.java:10-30`, and `NotificationExpertClient.java:63-81,214-227`
  (the flat command/response members and the forwarded internal request).
- `repos/eia-notifications-expert/.../NotificationController.java:31-36` and
  `NotificationService.java:40-52` (the pair on the expert list and the
  normalize-before-pair order), `NotificationSourceType.java:44-60`
  (`validateFilter`), `NotificationRepository.java:66-82` (the exact
  tenant-scoped `findAllBySource` query and `created_at DESC, id` order), and
  `ErrorCode.java:32,34` (`EIA-NTF-9412` and the expert `EIA-NTF-9502`);
  `repos/eia-notifications-domain/.../NotificationController.java:32-37`,
  `NotificationService.java:34-47`, `NotificationExpertClient.java:51-76`, and
  `ErrorCode.java:21-23` (the forwarded pair, blank-to-absent rule, and the
  domain tenant codes).
- Tests: `repos/eia-notifications-expert/src/test/java/com/eia/notifications/expert/NotificationServiceTest.java:221-284`,
  `NotificationControllerTest.java:170-260`, and
  `NotificationOutboxIntegrationTest.java:100-190` (create, null fields, unknown
  type, half pair, reference cap, and the created/sent payloads);
  `NotificationSourceFilterIntegrationTest.java:47-104` and
  `NotificationControllerTest.java:47-126` (expert exact filter, tenant wall,
  half pair, unknown type, and malformed id);
  `repos/eia-notifications-domain/src/test/java/com/eia/notifications/domain/NotificationControllerTest.java:56-123`
  and `NotificationExpertClientTest.java:62-132` (domain forwarding,
  blank-to-absent, and preserved 9412/9409 problems).
- `openapi/notifications.yaml` 1.6.0 and `asyncapi/notifications.yaml` 1.4.0
  record the implemented ten-value shape; `asyncapi/event-catalog.yaml` stays
  1.35.0 because no event name changes.

Resolution: either model the SPEC `subject_*` columns (or the typed `subject`
EntityRef) on the notification and reconcile them with the flat link, or amend
SPEC 11.8.4/12.5.5 to add the optional flat source triple and the ten-value
enum. Adding the subject columns is additive; the flat link is canonical for
this release. The list filter needs the same reconciliation: if the subject
columns are modelled, the filter can move to `subject_type`/`subject_id` while
keeping the exact-pair rule.

## M-54 Party identifiers and addresses are SPEC-less child routes

Party identifiers and addresses are implemented as child facts of
the Party aggregate. The same eight operations are served on the public base and
on the `/internal/v1` expert base (the domain forwards to the expert). An add, a
real replacement, or a delete bumps the Party row version and writes the
matching child fact in the same transaction; a replacement with no normalized
change is a 200 no-op with no bump and no event (M-58).

| Aspect | Implemented | SPEC 11.1.4 / 11.1.10 |
|---|---|---|
| Public routes | `GET/POST/PATCH/DELETE /api/v1/parties/{partyId}/identifiers` and `.../identifiers/{identifierId}`, `GET/POST/PATCH/DELETE /api/v1/parties/{partyId}/addresses` and `.../addresses/{addressId}` | No route: SPEC 11.1.10 lists the party, role, relationship, screening, consent, document, lineage, match, and audit routes only |
| Expert routes | the same eight operations under `/internal/v1/parties/{partyId}/...` | No internal reference-data route in SPEC 11.1.10 |
| Identifier types | 21 values: `TAX_ID`, `REGISTRATION`, `LICENSE`, `TIN`, `EIN`, `SSN`, `ITIN`, `DUNS`, `LEI`, `PASSPORT`, `DRIVER_LICENSE`, `STATE_ID`, `MEDICARE_ID`, `MEDICAID_ID`, `NPI`, `BAR_NUMBER`, `ACORD_PARTY_ID`, `ISO_PARTY_ID`, `TRUST_CLAIM_NUMBER`, `BANKRUPTCY_CASE_NUMBER`, `OTHER` | 17 values; no `TAX_ID`, `REGISTRATION`, `LICENSE`, or `OTHER` |
| Address types | 11 values: `PRIMARY`, `LEGAL`, `PHYSICAL`, `MAILING`, `BILLING`, `CLAIM_SITE`, `EXPOSURE_SITE`, `EMPLOYER`, `PROVIDER`, `BANK`, `OTHER` | 10 values; no `PRIMARY` |
| Identifier value | plaintext `identifier_value varchar(128)` returned on the projection | `identifier_value_encrypted bytea` plus an `identifier_last4 char(4)` display projection |
| Identifier coverage | type, value, issuing authority, effective date | adds `issuing_country`, `effective_from`/`effective_to`, `verified_flag`, `verified_at`, and `verification_source` |
| Address coverage | type, line1/line2, city, stateRegion, postalCode, country (alpha-2), effective date | adds `line3`, `district`, `region`, `region_code`, latitude/longitude, `geocode_accuracy`, `effective_from`/`effective_to`, `direct_flag`, `validated_flag`, and `normalized_hash` |
| Country | two-letter ISO 3166-1 alpha-2, normalized upper-case | `char(3)` ISO 3166-1 alpha-3 |
| Identifier duplicate | 409 on the unique `(tenant, party, type, value)` key, checked on create and on a key-changing replacement | No explicit unique key in SPEC 11.1.4; the implemented key is scoped to one party and identifier type |
| Address duplicate | no uniqueness rule; a party may hold several addresses of the same type | `normalized_hash` is the SPEC dedup key |
| Update semantics | PATCH is a full replacement: every create-required member is required again and an omitted/blank optional member clears the stored value; an unchanged normalized value is a 200 no-op | SPEC defines no child update route or body; the flat clear-on-omit rule is an implementation choice (M-58) |
| Delete semantics | hard delete with 204 and no body; the row is gone, a repeat delete is 404, and the event carries the last snapshot | SPEC defines no child delete route and no child fact |
| Concurrency / idempotency | no `ETag`, `If-Match`, or `Idempotency-Key` on either maintenance route; a lost update is last-write-wins | SPEC 12.6 requires `If-Match`/`Idempotency-Key` on transaction submission |
| List shape | bare array, oldest first (`created_at`, `id`) | the SPEC list conventions are cursor-paged (M-04) |
| Events | `party.party.identifier-added`, `.identifier-updated`, `.identifier-deleted`, `party.party.address-added`, `.address-updated`, `.address-deleted` | SPEC 11.1.9 publishes none of the six child facts |
| Error envelope | expert `{code, message}`; domain `{code, message, details}`; `application/json` | canonical `Problem` with `application/problem+json` (M-02, M-17) |

Additional differences:

- The expert returns the generic `CONFLICT` code for a duplicate identifier.
  The canonical contract documents `DUPLICATE_PARTY_IDENTIFIER`, and the
  domain preserves the expert code, so a client that branches on the code sees
  `CONFLICT` today.
- The contract documents a 409 `DUPLICATE_PARTY_ADDRESS` guard for a repeat of
  the same normalized address, including on a replacement. The expert implements
  no address uniqueness check and accepts the repeat; the status is the agreed
  target, not current behaviour.
- The contract documents 409 `PARTY_IDENTIFIER_IN_USE` and
  `PARTY_ADDRESS_IN_USE` guards for a delete of a still-referenced child. The
  expert has no reference check and hard-deletes any row it finds, so both
  statuses are agreed targets, not current behaviour. The domain test doubles
  preserve such a 409 if the expert ever returns one.
- A replacement is a full replacement, not a merge: omitting or blanking
  `issuingAuthority`, `effectiveDate`, `line2`, or `stateRegion` clears the
  stored value, `createdAt`/`createdBy` are immutable, and a same-value request
  returns the unchanged projection without a version bump or event (M-58).
- A delete hard-deletes the row rather than stamping a `record_state` or
  end-dating a temporal row; the last snapshot survives only in the event.
- The public domain requires `X-EIA-Tenant` and reports its absence as 400
  `TENANT_REQUIRED`. The expert accepts `?tenantId=` or `X-EIA-Tenant`,
  requires one of them (400 `VALIDATION_ERROR`), and rejects a mismatch with
  400 `VALIDATION_ERROR`. The domain sends both with the same value.
- `createdBy` is hard-coded to `system`; there is no caller identity on any
  route, so the actor is not attributable (M-20).
- The expert README still lists five identifier types (`TAX_ID`,
  `REGISTRATION`, `LICENSE`, `PASSPORT`, `OTHER`) and four address types
  (`PRIMARY`, `MAILING`, `BILLING`, `OTHER`). The code enforces the full sets
  above; that README section is stale, and this contract follows the code and
  SPEC.

Evidence:

- `repos/eia-party-domain/.../PartyIdentifierController.java:22-79`,
  `PartyAddressController.java:22-79` (public routes, header-only tenant, 201,
  200 replacement, 204 delete)
- `repos/eia-party-domain/.../PartyIdentifierDto.java`,
  `PartyAddressDto.java` (NON_NULL projection)
- `repos/eia-party-domain/.../PartyClient.java:79-330` (tenant forwarding,
  update/delete calls, and 404/409/4xx mapping)
- `repos/eia-party-domain/.../ApiExceptionHandler.java:18-53`
- `repos/eia-party-expert/.../PartyReferenceDataController.java:26-104` (dual
  base, tenant resolution, and the eight operations)
- `repos/eia-party-expert/.../PartyReferenceDataService.java:24-289` (type
  sets, country normalization, identifier conflict, update/delete, no-op,
  version bump, outbox)
- `repos/eia-party-expert/.../UpdatePartyIdentifierRequest.java`,
  `UpdatePartyAddressRequest.java` (full-replacement bodies)
- `repos/eia-party-expert/.../PartyChildNotFoundException.java` (child-scoped
  404)
- `repos/eia-party-expert/.../PartyIdentifierRepository.java:38-127` and
  `PartyAddressRepository.java:40-102` (oldest-first reads, update, delete; the
  address table has no unique key)
- `repos/eia-party-expert/.../schema.sql:21-59` (`party_identifier` unique key,
  plaintext value, `char(2)` country)
- `repos/eia-party-expert/.../PartyEvents.java:25-32,70-207`
- `repos/eia-party-expert/src/test/java/com/eia/party/expert/PartyReferenceDataApiTest.java:101-131,190-529`
  (validation, duplicate 409, country normalization, tenant wall, update/delete,
  no-op, child 404)
- `repos/eia-party-expert/src/test/java/com/eia/party/expert/PartyReferenceDataOutboxIntegrationTest.java:61-360`
  (event per append/replacement/delete, no-op, transaction rollback, monotonic
  versions, delete snapshot)
- `repos/eia-party-domain/src/test/java/com/eia/party/domain/PartyIdentifierControllerTest.java:90-340`
  and `PartyAddressControllerTest.java:91-295` (tenant-required, 404, 409, 400,
  update body forwarding, delete 204, delete 409 preservation)
- `repos/eia-party-expert/README.md:39-68` (stale type lists)

Resolution: keep the implemented child-resource shape and widen SPEC
11.1.4/11.1.10 to it, or adopt the SPEC encrypted identifier projection, the
alpha-3 country, the address dedup key, and a SPEC route for reference data. In
either case decide the PII/encryption treatment of `identifier_value`, the
address duplicate rule, the full-replacement clear semantics, the hard delete
and its retention rule, and whether the child routes need ETag/If-Match
replay protection, and correct the expert README.

## M-55 Party status transitions are a SPEC-less command

The Party expert now owns a lifecycle status command. The public domain forwards
it to `PATCH /internal/v1/parties/{partyId}/status?tenantId=...` and returns the
updated party with `ETag: "<version>"`. The command accepts every SPEC 11.1.5
status from every current status; there is no transition graph, no status
history, and no persisted reason.

| Aspect | Implemented | SPEC 11.1.5 / 11.1.9 / 11.1.10 |
|---|---|---|
| Public route | `PATCH /api/v1/parties/{partyId}/status` | SPEC 11.1.10 lists `PATCH /api/v1/party/parties/{partyId}` for the whole party update; no `/status` subresource |
| Expert route | `PATCH /internal/v1/parties/{partyId}/status?tenantId=` | No internal status route in SPEC 11.1.10 |
| Body | `{status, reason?}`; `reason` is trimmed, capped at 500 characters, and a blank value is treated as absent | SPEC 11.1.10 does not define the update body; `reason` is not a SPEC party column |
| Status vocabulary | the full SPEC 11.1.5 eight-value `PartyStatus` set, normalized by trimming and upper-casing | matches SPEC 11.1.5 |
| Transition rules | every status accepted from every current status; a same-status request is a 200 no-op with no version bump and no event | SPEC 11.1.5 defines the enum but no party transition graph, so the flat acceptance is an implementation choice rather than a documented SPEC rule |
| Reason persistence | event-only (`party.party.updated` payload); no `status_reason` column and no history | SPEC 11.1.9's status-changed payload carries `reason`, implying a fact rather than a stored or history field |
| Event name | `party.party.updated` with `changedFields: [status]`, `version`, `from`, `to`, and the optional reason | SPEC 11.1.9 names the dedicated fact `party.party.status-changed` (`partyId`, `from`, `to`, `reason`), which remains planned |
| Event version | the payload `version` is the row version after the bump; the envelope `aggregateVersion` is that value plus one because Party rows start at 0 | the envelope follows SPEC 7.5; the plus-one is the existing Party convention (M-22) |
| Concurrency / idempotency | the public 200 sets `ETag: "<version>"`; optional `If-Match` and `Idempotency-Key` are accepted and forwarded, but the expert compares neither and replays neither, so there is no 409 | SPEC 12.6 requires `If-Match`/`Idempotency-Key` on transaction submission |
| Error envelope | domain `{code, message, details}`, expert `{code, message}`, `application/json` | canonical `Problem` with `application/problem+json` (M-02, M-17) |
| Projection | `Party.status` is the closed eight-value enum | matches SPEC 11.1.5; the previous contract described the field as a free-form string |

Additional differences:

- `party.party.status-updated` is not an event name in the implementation, the
  AsyncAPI document, or the event catalog. The implemented status-update fact is
  the generic, already-counted `party.party.updated`; no new event name was
  published or counted. SPEC 11.1.9's dedicated `party.party.status-changed`
  remains planned.
- The domain validates `status` with `@NotBlank` and `reason` with
  `@Size(max=500)` before calling the expert. An unsupported status is rejected
  by the expert with 400 `VALIDATION_ERROR`; the domain preserves that status and
  code. The public domain reports a missing tenant as 400 `TENANT_REQUIRED` and a
  malformed one as 400 `TENANT_INVALID`.
- The expert status route requires `?tenantId=` (`@RequestParam`) and does not
  read `X-EIA-Tenant`, unlike the reference-data expert routes. The domain sends
  both with the same value. A missing or malformed `tenantId` is answered by
  Spring's request-parameter binding with a plain 400, not the expert
  `{code, message}` body, because neither case has a local exception handler.
- A same-status request returns before the update, so it preserves `version`,
  `updatedAt`, the `ETag`, and the outbox and ignores a supplied reason. A
  different status on a retry applies again with a new version because the
  idempotency key is not replayed.
- `reason` is never returned by the Party projection and has no read endpoint, so
  a client cannot read back why a status changed; only an event subscriber can.
- A 404 is returned for a party in another tenant and for an unknown party, so
  the response cannot confirm that a foreign party exists. The expert also
  returns 404 for a row whose `record_state` is not `ACTIVE`, because the update
  predicate filters it out after the read.
- If-Match forwarding is best-effort: the domain omits a null or blank header and
  forwards the raw value otherwise; the expert ignores both headers entirely.

Evidence:

- `repos/eia-party-domain/.../PartyController.java:37-57` (public PATCH, ETag
  from `version`, optional header forwarding)
- `repos/eia-party-domain/.../UpdatePartyStatusCommand.java:11-14`
  (`@NotBlank status`, `@Size(max=500) reason`)
- `repos/eia-party-domain/.../PartyClient.java:80-115` (tenant on query and
  header, optional `If-Match`/`Idempotency-Key`, 4xx translation)
- `repos/eia-party-domain/.../PartyDto.java:6-15` (no status-reason member)
- `repos/eia-party-domain/.../ApiExceptionHandler.java:24-57`
  (`TENANT_REQUIRED`, `VALIDATION`, `TENANT_INVALID`)
- `repos/eia-party-expert/.../PartyController.java:37-43` (expert PATCH,
  `@RequestParam tenantId`, no header parameters)
- `repos/eia-party-expert/.../PartyService.java:20-65` (eight-value set,
  trim/upper-case, same-status early return, one bump plus outbox row)
- `repos/eia-party-expert/.../PartyRepository.java:88-104` (single `UPDATE ...
  version = version + 1` filtered by `record_state = 'ACTIVE'`)
- `repos/eia-party-expert/.../PartyEvents.java:50-64` (payload fields and
  `aggregateVersion = after.version + 1`)
- `repos/eia-party-expert/.../schema.sql:3-16` (no status-reason column)
- `repos/eia-party-expert/src/test/java/com/eia/party/expert/PartyApiTest.java:97-121`
  (ACTIVE transition, version 1, unsupported status 400)
- `repos/eia-party-expert/src/test/java/com/eia/party/expert/PartyOutboxIntegrationTest.java:97-159`
  (one `party.party.updated` row, payload fields, rollback keeps state and writes
  no event)
- `repos/eia-party-domain/src/test/java/com/eia/party/domain/PartyControllerTest.java:132-250`
  (ETag, header forwarding, expert 400/404 preservation, tenant and reason
  validation)
- `repos/eia-party-domain/src/test/java/com/eia/party/domain/PartyClientTest.java:314-420`
  (query/header forwarding, blank-header omission, empty expert body 502)
- `openapi/party.yaml`, `asyncapi/party.yaml` (this contract)

Resolution: keep the dedicated `/status` command and add a SPEC party transition
graph and status history if the business needs them, or fold the status change
into the SPEC `PATCH /api/v1/party/parties/{partyId}` update transaction. Decide
whether the reason must be stored and returned, and either implement
`If-Match`/`Idempotency-Key` on the expert status route or stop forwarding them.
If a dedicated fact is required, emit `party.party.status-changed` (or an agreed
new `party.party.status-updated`) with an EV-05 dual-publish window rather than
overloading `party.party.updated`.

## M-56 Notification delivery attempts use a SPEC-less route and simulator and keep the evidence on the notification

SPEC 11.8.4 models delivery as a `notification_delivery` row under
`notification_recipient`, with a recipient, a provider message id, requested and
responded timestamps, a retry schedule, and the `PENDING`/`SENT`/`DELIVERED`/
`BOUNCED`/`FAILED`/`SUPPRESSED` statuses. SPEC 11.8.10 surfaces tenant-wide
delivery diagnostics at `GET /api/v1/notifications/admin/deliveries` and a retry
command at `POST .../admin/deliveries/{id}/retry`. The 2026-10-22
Notifications delivery slice instead adds a tenant-scoped, per-notification
history at `GET /api/v1/notifications/{notificationId}/attempts` (and its
`/internal/v1` expert mirror), records one attempt on a successful send, keeps
the delivery evidence on the notification, and uses a local simulator provider.

| Aspect | Implemented | SPEC 11.8.4 / 11.8.10 |
|---|---|---|
| Route | `GET /api/v1/notifications/{notificationId}/attempts` and `GET /internal/v1/notifications/{notificationId}/attempts`, tenant-scoped, bare array ordered by `attemptNumber` ascending | No per-notification attempts route; the SPEC surface is the tenant-wide `/api/v1/notifications/admin/deliveries` list and a retry command |
| Projection | `NotificationDeliveryAttempt` with exactly `id`, `tenantId`, `notificationId`, `attemptNumber`, `channel`, `provider`, `providerReference`, `status`, `errorCode`, `errorMessage`, `attemptedAt` | `notification_delivery` also has `recipient_id`, `provider_message_id`, `requested_at`, `responded_at`, and `next_retry_at`; `provider` is varchar(48) and `provider_message_id` varchar(128) |
| Status | `DELIVERED` or `FAILED` only | `PENDING`, `SENT`, `DELIVERED`, `BOUNCED`, `FAILED`, `SUPPRESSED` |
| Identity and order | `attemptNumber` is sequential per notification and unique on `(notificationId, attemptNumber)`; reads order by `attemptNumber` | `attempt_number` plus the recipient determine one delivery row; the SPEC defines no tenant-local uniqueness rule |
| Delivery evidence | `Notification.deliveredAt` and `Notification.providerReference` are required-but-nullable on the notification projection and row; `deliveredAt` equals `sentAt` for a simulator delivery | `notification` has only `sent_at`; `delivered_at` belongs to `notification_recipient` and the provider reference to `notification_delivery` |
| Provider | The only implementation is the local `SIMULATOR`, selected by `eia.notifications.provider=simulator` and the default when absent; it never contacts an external system, always returns `DELIVERED`, and uses the deterministic `SIM-<notification uuid>` reference as the NTF-11 idempotency key | External email relay, SMS gateway, push, and webhook integrations; provider values `EMAIL_RELAY`, `SMS_GATEWAY`, `IN_APP`, and `WEBHOOK` |
| Failure | A provider failure aborts the send with 502 `EIA-NTF-9304` `DELIVERY_FAILED` before an attempt row, a status change, or an event is written; the `FAILED` attempt status is admitted by the schema but not produced | A failed delivery is a persisted row with `FAILED` (or `BOUNCED`), an error code and message, and a `next_retry_at` |
| Retry | None: a send records attempt 1, and a second send is rejected by the CREATED/QUEUED guard | Retry command and retry schedule (NTF-11 idempotency) |
| Events | `notifications.notification.sent` carries the optional `deliveredAt` and `providerReference` members; `notifications.notification.delivered` remains planned | SPEC 11.8.9 publishes `notifications.notification.delivered` and `notifications.delivery.failed`; neither is emitted |
| Version | `openapi/notifications.yaml` 1.7.0 and `asyncapi/notifications.yaml` 1.5.0 (additive) | No SPEC version defines the per-notification history or the notification-level evidence |

Consequences:

- A client generated from SPEC 11.8.10 has no per-notification history route;
  the implemented `GET /api/v1/notifications/{notificationId}/attempts` is a
  new, additive read. The tenant-wide diagnostics list and retry command remain
  unimplemented and are listed under `x-planned-operations`.
- A consumer of the SPEC `notification_delivery` row must not expect a
  recipient, provider message id, requested/responded timestamps, or a retry
  schedule. The implemented row is a narrow attempt record, and the delivery
  evidence is denormalized onto the notification for the web detail view.
- The simulator is a local-development provider, not an integration. In a
  deployment with a real provider the attempt shape can stay the same, but the
  provider failure path must persist a `FAILED` attempt with its error evidence
  and retry schedule instead of only returning 502.
- Because the history is tenant-scoped through the notification lookup, an
  unknown notification and a foreign-tenant notification are the same 404
  `EIA-NTF-9001`; a known unsent notification returns an empty array. The read
  never exposes another tenant's attempt rows.
- Adding the SPEC delivery columns and the admin/retry surface later is
  additive. Removing the notification-level evidence or renaming the attempt
  members is breaking under SPEC 10.4 and needs a major contract version.

Evidence:

- `repos/eia-notifications-expert/.../NotificationController.java:43-46`
  (expert attempts mapping), `NotificationService.java:66-74` (notification
  lookup is the tenant wall, then the tenant-scoped attempt read) and
  `:129-171` (send: provider call, attempt 1 insert, `markSent` with
  `deliveredAt`/`providerReference`, sent event; the failure branch throws
  `DELIVERY_FAILED` before the insert), and
  `NotificationDeliveryAttemptRepository.java:42-62` (ascending order and
  insert).
- `repos/eia-notifications-expert/.../NotificationDeliveryAttempt.java:12-33`
  (eleven-member record), `DeliveryProvider.java`, `DeliveryRequest.java`,
  `DeliveryResult.java:14-26` (two attempt statuses), and
  `SimulatedDeliveryProvider.java:15-30` (`SIMULATOR`, always delivered,
  `SIM-<notification uuid>`).
- `repos/eia-notifications-expert/.../NotificationEvents.java:68-89` (sent
  payload puts `deliveredAt` and `providerReference` when present) and
  `schema.sql:75-118` (notification `delivered_at`/`provider_reference` columns,
  attempt table, two-value status check, unique `(notification_id,
  attempt_number)`, 64/32/64/500 widths).
- `repos/eia-notifications-domain/.../NotificationController.java:51-55`
  (public attempts mapping), `NotificationService.java:77-84` (forward with the
  expert 404 preserved), `NotificationExpertClient.java:90-108` (tenant on the
  query parameter and header), `NotificationDeliveryAttemptDto.java:1-37`
  (eleven-member projection), and `NotificationDto.java:8-27`
  (`deliveredAt`/`providerReference`).
- Tests: `repos/eia-notifications-expert/src/test/java/com/eia/notifications/expert/NotificationDeliveryIntegrationTest.java:75-206`
  (default simulator, attempt 1 evidence, sent payload, tenant wall and 404,
  legacy rows, unique attempt number) and `NotificationServiceTest.java:219-239`
  (provider failure writes no attempt and no event);
  `repos/eia-notifications-domain/src/test/java/com/eia/notifications/domain/NotificationControllerTest.java:297-363`
  and `NotificationServiceTest.java:187-214` (delivery evidence on the
  projection, attempts forwarding, preserved 404, tenant and malformed-id
  problems).
- SPEC 11.8.4 `notification`/`notification_recipient`/`notification_delivery`
  tables, 11.8.9 published names, and 11.8.10 API surface; NTF-11 and NTF-15.
- `openapi/notifications.yaml` 1.7.0 and `asyncapi/notifications.yaml` 1.5.0
  record the implemented shape; `asyncapi/event-catalog.yaml` stays 1.35.0
  because no event name changes.

Resolution: either implement the SPEC `notification_delivery` row, the
tenant-wide diagnostic list, the retry command, and a real provider, or amend
SPEC 11.8.4/11.8.10 to accept the per-notification attempt history, the
notification-level evidence, and the simulator as the first delivery slice.
The per-notification history and the notification evidence are canonical for
this release; the simulator is a local provider and the admin/retry surface
remains planned.

## M-57 Policy rating worksheets are a SPEC-less policy-scoped route and event

SPEC 11.2.14 models rating under the underwriting submission: a
`rating_worksheet` row references `submission_id` and `product_version_id`,
stores `exposure_lines` and `factor_trace` JSON, `premium_amount`,
`tax_amount`, `fee_amount`, `currency`, and `calc_hash`, and moves through
`DRAFT`, `CALCULATED`, `APPROVED`, and `SUPERSEDED`. `rating_plan` defines six
methods (`RATE_TIMES_EXPOSURE`, `LOSS_COST`, `EXPERIENCE_MOD`, `SCHEDULE`,
`JUDGMENT`, `FLAT`), `rating_factor` rows supply the typed factors, and
`rating_plan.minimum_premium_amount` and `deposit_premium_flag` gate the
premium. SPEC 11.2.14 posts `POST /api/v1/policy/submissions/{submissionId}/rating`
and publishes `policy.rating.completed`; `UWR-01` and `UWR-02` require an
approved rating worksheet before bind and a reproducible one before quote
issue. The 2026-10-22 slice instead rates an existing policy directly:

| Aspect | Implemented | SPEC 11.2.14 / gap |
|---|---|---|
| Route | `POST/GET /api/v1/policies/{policyId}/rating` (and the expert's `/internal/v1` alias) | No policy-scoped rating route; the SPEC command is `POST /api/v1/policy/submissions/{submissionId}/rating` (M-01) |
| Subject | The policy: the worksheet references `policyId` and the policy premium currency; there is no submission, product version, plan, or factor row | `rating_worksheet` references `submission_id` and `product_version_id`; `rating_plan` and `rating_factor` drive the calculation |
| Body | `{ratingMethod, baseRate, exposureAmount?, factor?, apply?}` | The SPEC record is derived from a plan and factor rows; there is no caller-supplied base rate or single factor |
| Methods | `RATE_TIMES_EXPOSURE` and `FLAT` only | `RATE_TIMES_EXPOSURE`, `LOSS_COST`, `EXPERIENCE_MOD`, `SCHEDULE`, `JUDGMENT`, `FLAT` |
| Computation | `baseRate * exposureAmount * factor` or `baseRate * factor`, rounded once to scale 4 HALF_UP; no minimum-premium, deposit, tax, or fee | Plan minimum premium, deposit flag, typed factors, tax and fee amounts |
| Worksheet | `{id, tenantId, policyId, ratingMethod, baseRate, exposureAmount, factor, computedPremium, currency, calcHash, status, createdAt, createdBy}`; exposure is a single scale-4 amount and is null for FLAT | Submission and product version, `exposure_lines` (class/territory/basis/amount), `factor_trace`, separate premium/tax/fee amounts |
| Status | Always `CALCULATED`; applying is observable only through the policy premium, its version, and the event | `DRAFT`, `CALCULATED`, `APPROVED`, `SUPERSEDED`; UWR-01 requires an approved worksheet before bind |
| Rateable state | Only a `DRAFT` or `QUOTED` policy; another status is 409 `POLICY_NOT_RATEABLE` with the current and allowed statuses | Tied to submission status and underwriting referral/authority, not to the policy lifecycle |
| Apply | `apply` false (default) persists the worksheet and leaves the policy untouched; `apply` true replaces `policy.premium_amount`, bumps the aggregate version, and writes the event in the same transaction | A worksheet is underwriting evidence; SPEC defines no policy-premium re-rate command |
| Read | `GET .../rating` returns the newest worksheet for the policy, no `ETag`; a policy with no worksheet is 404 `RATING_WORKSHEET_NOT_FOUND` | No standalone worksheet read; a worksheet is addressed by submission |
| Event | `policy.policy.rated`, payload `{policyId, policyNumber, premiumAmount, currency, ratingMethod, calcHash, worksheetId}`, emitted only on apply | `policy.rating.completed` for the submission-scoped worksheet; the implemented name is new (M-22) |
| Concurrency | Optional `If-Match` is compared before any write; a stale tag is 409 `CONCURRENT_MODIFICATION` and a lost conditional premium update rolls the worksheet back | SPEC 12.6 requires the header on transaction submission |
| Idempotency | Optional `Idempotency-Key` replays the stored response in the `(tenant, operation = rating, key)` scope after comparing a canonical request hash: a first keyed calculation is 201, an identical canonical request is 200 with `Idempotent-Replayed: true`, the stored `{worksheet, policy?}` body, and the stored strong `ETag` when the original applied, and a changed request is 409 `IDEMPOTENCY_CONFLICT` with `meta.operation`/`meta.key` and no write. The hash covers `policyId` and the normalized inputs, so the key cannot replay another policy's worksheet; a blank key is absent, a 129+ key is 400 `INVALID_IDEMPOTENCY_KEY`, and a legacy null-hash row replays | SPEC 12.6 request-hash conflict (matches); the route, worksheet, and event remain SPEC-less |
| Version | `openapi/policy.yaml` 2.17.0 (2.20.0 adds keyed replay; 2.21.0 adds the canonical request hash), `asyncapi/policy.yaml` 1.14.0, `asyncapi/event-catalog.yaml` 1.36.0 (additive) | No SPEC version has this route, worksheet, or event |

Consequences:

- A client generated from SPEC 11.2.14 has no policy rating route and no
  `GET .../rating`; the implemented surface is a new, additive policy command.
  The SPEC submission-scoped command, the rating plan and factor catalog, and
  the approval/referral workflow remain unimplemented.
- The worksheet is not underwriting evidence in the SPEC sense: it carries no
  submission or product version, no exposure-line or factor-trace document, no
  tax or fee, and only the `CALCULATED` state. `calcHash` proves that the
  method, operands, result, and currency are reproducible; it does not prove
  that an approved plan produced them.
- Applying a rating is an immediate premium replacement on a DRAFT or QUOTED
  policy, not a quote or bind gate. `UWR-01` and `UWR-02` are therefore not
  enforced by this command, and an issued policy must use the endorsement or
  premium-audit commands instead because it is not rateable.
- `calcHash` is deliberately independent of the request decimal scale and of
  the worksheet identity, so two identical calculations on different policies
  produce the same hash. The hash identifies the calculation, not the
  worksheet; `worksheetId` is the row identity.
- A retry with a key and an identical canonical request replays the stored
  worksheet and, when the original applied, the stored `ETag`. The same key
  with a changed method or operand is 409 `IDEMPOTENCY_CONFLICT` with
  `meta.operation`/`meta.key` and writes no worksheet, premium, version, or
  event; a new key is needed for the new command. A retry without a key still
  appends another worksheet and, when `apply` is true, replaces the premium
  again at a new version. A legacy row with a null request hash replays. The
  pool of worksheets is append-only, so a no-key retry is visible in
  `GET .../rating` but the previous premium is not.
- Adding the SPEC submission/product/factor/approval fields later is additive;
  removing the policy-scoped route or renaming the event is breaking under SPEC
  10.4 and needs a major contract version or the EV-05 dual-publish window.

Evidence:

- `repos/eia-policy-domain/.../PolicyRatingController.java:29-74` (public path,
  tenant, optional DIRECT book, `If-Match`, `Idempotency-Key`, 201 and 200
  publication, `ETag` fallback, `Idempotent-Replayed`),
  `PolicyRatingService.java:27-38` (`If-Match` parse, key normalization,
  delegation), `RatePolicyCommand.java:26-44` (fields, defaults, and bounds),
  `RatingWorksheetDto.java:21-35`, `PolicyRatingResult.java:12-15` (nullable
  `policy` omitted from JSON), and `PolicyClient.java:423-465`
  (`/internal/v1` alias, tenant and DIRECT headers, header forwarding, envelope,
  latest read).
- `repos/eia-policy-expert/.../PolicyRatingController.java:27-69` (public and
  internal paths, tenant query/header, DIRECT book, 201, `ETag`),
  `PolicyRatingService.java:51-97` (guard, rateable gate, validation, worksheet
  insert, conditional premium update, conflict, version bump, event),
  `RatingRules.java:35-217` (two methods, DRAFT/QUOTED, default factor, HALF_UP
  rounding, numeric(19,4) cap, canonical hash, error codes),
  `PolicyRatingWorksheet.java:23-38`, `RatingWorksheetRepository.java:46-70`,
  `RatingResult.java`, and `PolicyRepository.updatePremium` (conditional
  `version = version + 1`).
- `repos/eia-policy-expert/.../PolicyEvents.java:527-545` (`RATED` name and the
  seven-member `rated` payload).
- `repos/eia-policy-expert/src/main/resources/schema.sql:761-796`
  (`policy_rating_worksheet` columns, the method/base-rate/factor/exposure/
  premium/currency/hash/status checks, and the newest-first index).
- Tests: `PolicyRatingControllerTest`, `PolicyRatingServiceTest`,
  `RatingRulesTest`, and `PolicyRatingIntegrationTest` in the expert;
  `PolicyRatingControllerTest`, `PolicyRatingServiceTest`, and
  `PolicyRatingClientTest` in the domain.
- `repos/eia-policy-expert/.../PolicyIdempotencyService.java:52-108` (rating
  hash compare, 409 conflict with `meta.operation`/`meta.key`, legacy null-hash
  replay, stored-response completion),
  `PolicyIdempotencyRepository.java:28-76` (find, reserve with the hash, and
  complete), `IdempotentResponse.java`, `IdempotencyKeys.java:25-99` (key
  bounds and the rating/conversion `requestHash` functions),
  `src/main/resources/schema.sql:167-201`, `IdempotencyKeysTest.java` (hash
  stability across scale/whitespace and per-input changes), and
  `PolicyIdempotencyReplayIntegrationTest.java`
  (`ratingReplayAcceptsAnEquivalentBodyWithDifferentScaleAndWhitespace`,
  `reusingARatingKeyWithADifferentBaseRateConflictsWithoutWriting`,
  `aRatingKeyCannotReplayAWorksheetFromAnotherPolicy`, stored body/ETag replay,
  tenant/operation scope, no-key path, 129-character rejection).
- SPEC 11.2.14 `rating_plan`, `rating_factor`, and `rating_worksheet` tables,
  RATE-02, UWR-01, and UWR-02; SPEC 11.2.9 published names.
- `openapi/policy.yaml` 2.21.0 (2.17.0 introduced the route, 2.20.0 the keyed
  replay, and 2.21.0 the canonical request hash), `asyncapi/policy.yaml`
  1.14.0, and `asyncapi/event-catalog.yaml` 1.36.0 record the implemented shape.

Resolution: the policy rating command is canonical for now. Closing the gap
means implementing the submission-scoped `rating_plan`/`rating_factor` model,
the `rating_worksheet` `exposure_lines`/`factor_trace`/tax/fee members and
DRAFT..SUPERSEDED lifecycle, the non-implemented methods, and the
`policy.rating.completed` fact, then deciding whether policy re-rating is a
separate command or a consequence of an approved worksheet. Renaming
`policy.policy.rated` to a SPEC name or adding the submission route is additive;
removing the implemented route is breaking.

## M-58 Party identifier and address maintenance adds SPEC-less PATCH/DELETE child routes

Party 1.4.0 adds full-replacement `PATCH` and hard-delete `DELETE` commands for
the identifier and address children on the public and `/internal/v1` expert
bases. Neither route exists in SPEC 11.1.10, and SPEC 11.1.9 publishes no child
fact for a replaced or deleted identifier or address. A real replacement or a
delete bumps the Party row version and writes the matching child fact in the
same transaction; a replacement with no normalized change is a 200 no-op.

| Aspect | Implemented | SPEC 11.1.4 / 11.1.10 / 12.6 |
|---|---|---|
| PATCH routes | `PATCH /api/v1/parties/{partyId}/identifiers/{identifierId}`, `PATCH /api/v1/parties/{partyId}/addresses/{addressId}`, and their `/internal/v1` mirrors | No child update route or body in SPEC 11.1.10 |
| DELETE routes | `DELETE /api/v1/parties/{partyId}/identifiers/{identifierId}`, `DELETE /api/v1/parties/{partyId}/addresses/{addressId}`, and their `/internal/v1` mirrors | No child delete route in SPEC 11.1.10 |
| Update body | `UpdatePartyIdentifierRequest` `{identifierType, identifierValue, issuingAuthority?, effectiveDate?}` and `UpdatePartyAddressRequest` `{addressType, line1, line2?, city, stateRegion?, postalCode, country, effectiveDate?}` | SPEC defines no child update representation |
| Replacement semantics | full replacement, not a merge: every create-required member is required again, an omitted or blank optional member clears the stored value, and `createdAt`/`createdBy` are immutable | No SPEC rule; the clear-on-omit behaviour is an implementation choice |
| No-op | a replacement whose normalized values equal the stored values returns the unchanged projection with 200, no Party version bump, and no event | No SPEC rule |
| Delete semantics | hard delete with 204 and no body; the event carries the last stored snapshot; a repeat delete is 404 | No SPEC rule; SPEC 11.1.4 defines no child lifecycle or tombstone |
| Identifier duplicate | 409 `DUPLICATE_PARTY_IDENTIFIER` on a replacement that would duplicate another row's normalized key; the expert returns the generic `CONFLICT` | SPEC 11.1.4 defines no explicit unique key |
| Address duplicate | canonical 409 `DUPLICATE_PARTY_ADDRESS`; not enforced because the expert has no address uniqueness rule | `normalized_hash` is the SPEC dedup key |
| Delete guards | canonical 409 `PARTY_IDENTIFIER_IN_USE` and `PARTY_ADDRESS_IN_USE`; not enforced because the expert has no reference check | No SPEC child-reference rule |
| Events | `party.party.identifier-updated` / `.identifier-deleted` and `party.party.address-updated` / `.address-deleted`, keyed by the Party aggregate at the bumped version | SPEC 11.1.9 publishes none of the four facts |
| Concurrency / idempotency | no `ETag`, `If-Match`, or `Idempotency-Key`; a real replacement retry applies again and a delete retry is 404 | SPEC 12.6 requires `If-Match`/`Idempotency-Key` on transaction submission |
| Error envelope | domain `{code, message, details}`, expert `{code, message}`, `application/json` | canonical `Problem` with `application/problem+json` (M-02, M-17) |
| Version | `openapi/party.yaml` 1.4.0 and `asyncapi/party.yaml` 1.4.0 (additive); catalog 1.37.0 | No SPEC version defines the maintenance routes or facts |

Additional differences:

- The canonical contract documents the delete guards `PARTY_IDENTIFIER_IN_USE`
  and `PARTY_ADDRESS_IN_USE`, but `PartyReferenceDataService.deleteIdentifier`
  and `deleteAddress` perform an unconditional delete after the scoped read.
  Nothing can currently produce the documented 409; the domain preserves a 409
  if one were returned, and its tests cover that mapping with a stubbed expert.
- The canonical address replacement guard is `DUPLICATE_PARTY_ADDRESS`, but
  `updateAddress` performs no uniqueness check and accepts a replacement that
  matches another address. The same gap applies to create (M-54).
- A replacement is a full replacement with clear-on-omit semantics, which is a
  different contract from a JSON Merge Patch or a partial PATCH. A client that
  sends only the field it wants to change clears the other optional members;
  the contract states this explicitly and the schema requires every
  create-required member.
- A replacement with the same normalized values returns the row read before the
  update, so it preserves `version`, `updatedAt`, and the ETag-equivalent state
  and writes no outbox row. It is the only safe retry; there is no idempotency
  key and a real replacement retry applies a second version bump and a second
  event.
- A delete is a hard delete, not a `record_state` stamp or an end-dated temporal
  row. The last snapshot exists only in the `-deleted` event, so a consumer must
  persist it if the deleted values are needed after the commit.
- The update event carries the ordered `changedFields` list, which the expert
  builds in a fixed order (`identifierType`, `identifierValue`,
  `issuingAuthority`, `effectiveDate`; `addressType`, `line1`, `line2`, `city`,
  `stateRegion`, `postalCode`, `country`, `effectiveDate`). The list never
  repeats a member and is never empty on an emitted event, but a consumer should
  treat it as a set of changed member names rather than rely on position.
- Both update payloads carry `from`/`to` snapshots rather than an entire child
  graph; both delete payloads flatten the last snapshot and add
  `createdBy`/`createdAt`. The envelope `aggregateVersion` is the bumped Party
  row version plus one because Party rows start at version 0.
- Neither maintenance route sets an `ETag` or reads `If-Match`/`Idempotency-Key`,
  so a concurrent replacement is last-write-wins and the route cannot detect a
  lost update (M-06, M-07).
- The public domain forwards the caller's body unchanged and keeps the expert
  status and code, so a duplicate identifier surfaces as the generic `CONFLICT`
  rather than `DUPLICATE_PARTY_IDENTIFIER`. A missing tenant is 400
  `TENANT_REQUIRED` and a malformed tenant is 400 `TENANT_INVALID`; the expert
  accepts `?tenantId=` or `X-EIA-Tenant` and rejects a mismatch with 400
  `VALIDATION_ERROR`.
- `createdBy` is `system` for every child route, so a replacement or delete is
  not attributable to a caller (M-20).

Consequences:

- An event subscriber that only consumes `identifier-added`/`address-added`
  misses replacements and deletions and will hold stale child data. The catalog
  now publishes and implements all six child names, so a subscriber must also
  consume the four maintenance facts to stay current.
- A consumer that treats PATCH as a partial update will clear optional members.
  The contract, the README, and the schema descriptions all state the
  full-replacement rule.
- Deleting a child does not check whether another aggregate references it, and
  there is no soft-delete or restore command. A mistaken delete is unrecoverable
  through the API except by re-creating the child.

Evidence:

- `repos/eia-party-domain/.../PartyIdentifierController.java:55-79` and
  `PartyAddressController.java:55-79` (public PATCH/DELETE, header-only tenant,
  200/204)
- `repos/eia-party-domain/.../PartyClient.java:178-330` (update/delete calls,
  tenant on query and header, body forwarding, 404/409/4xx mapping)
- `repos/eia-party-domain/src/test/java/com/eia/party/domain/PartyIdentifierControllerTest.java:182-340`
  and `PartyAddressControllerTest.java:147-295` (200/204, tenant-required,
  400/404/409 preservation, malformed id, body forwarding)
- `repos/eia-party-expert/.../PartyReferenceDataController.java:48-104` (dual
  base, `@Valid` bodies, 204 deletes)
- `repos/eia-party-expert/.../PartyReferenceDataService.java:126-289` (full
  replacement, no-op early return, duplicate check, update predicate, hard
  delete, version bump, outbox)
- `repos/eia-party-expert/.../UpdatePartyIdentifierRequest.java` and
  `UpdatePartyAddressRequest.java` (`@NotBlank` required members and optional
  clear members)
- `repos/eia-party-expert/.../PartyChildNotFoundException.java` and
  `ApiExceptionHandler.java` (child 404)
- `repos/eia-party-expert/.../PartyIdentifierRepository.java:86-127` and
  `PartyAddressRepository.java:88-102` (`existsExcluding`, update, delete with
  scoped predicates)
- `repos/eia-party-expert/.../PartyEvents.java:118-207` (changed-field
  snapshots, delete snapshots, `aggregateVersion = version + 1`)
- `repos/eia-party-expert/src/test/java/com/eia/party/expert/PartyReferenceDataApiTest.java:307-529`
  (update/delete, no-op, child 404, duplicate 409, invalid fields leave the row
  unchanged)
- `repos/eia-party-expert/src/test/java/com/eia/party/expert/PartyReferenceDataOutboxIntegrationTest.java:235-470`
  (changed fields, no event on no-op, delete snapshot, duplicate update writes
  nothing, tenant/party scoping, monotonic versions)
- `repos/eia-party-expert/src/main/resources/schema.sql:21-59` (no child
  tombstone or end-date column; hard delete)
- SPEC 11.1.4 `party_identifier`/`party_address`, SPEC 11.1.9, SPEC 11.1.10,
  SPEC 12.6.
- `openapi/party.yaml` 1.4.0 and `asyncapi/party.yaml` 1.4.0 record the
  implemented shape.

Resolution: keep the full-replacement and hard-delete shape, or move to a
partial PATCH and a tombstone/end-date model with a retention rule. In either
case implement or withdraw the address duplicate and delete in-use guards,
decide whether the child routes need `If-Match`/`Idempotency-Key`, and decide
whether the parent Party version must be bumped for a no-op.

## M-59 Policy underwriting submissions are a SPEC-less pre-policy collection

Policy 2.18.0 adds a tenant-owned underwriting submission collection at
`/api/v1/policies/submissions` with list, read, create, and status operations.
SPEC 11.2.14 defines an `underwriting_submission` aggregate and a single
`POST /api/v1/policy/submissions` create row, but no list, read, or status API;
it models the workflow as separate clearance, rating, referral, quote, bind,
and declination commands with the
`RECEIVED`/`CLEARANCE`/`RATING`/`REFERRED`/`QUOTED`/`BOUND`/`DECLINED`/
`WITHDRAWN` status set. The implemented slice is an intake record with a
one-way six-state graph and two new event names; the follow-on conversion
command and its third event are recorded in M-60.

| Aspect | Implemented | SPEC 11.2.14 / 11.2.9 |
|---|---|---|
| Routes | `GET/POST /api/v1/policies/submissions`, `GET .../{submissionId}`, `PATCH .../{submissionId}/status`, and `POST .../{submissionId}/convert` (the expert also maps `/internal/v1`; conversion is M-60) | `POST /api/v1/policy/submissions` only; no list, read, status, or conversion route |
| Projection | `PolicySubmission` `{submissionId, submissionNumber, tenantId, applicantPartyId, productCode, requestedEffectiveDate, requestedLimitAmount, requestedLimitCurrency, tortCodes, notes, status, version, createdAt, updatedAt, policyId?}` | `underwriting_submission` also carries `program_id`, `product_id` (the implementation stores a product code), `requested_limits`, `requested_coverages`, `exposures`, `owner`, and `received_at` |
| Identity | server-generated per-tenant `SUB-{YYYY}-{7 digits}` number from `underwriting_submission_number_seq`; `(tenant_id, submission_number)` unique | `submission_number varchar(32)` with no generator rule |
| Statuses | `RECEIVED`, `REFERRED`, `QUOTED`, `BOUND`, `DECLINED`, `WITHDRAWN` | adds `CLEARANCE` and `RATING` |
| Graph | `RECEIVED -> REFERRED/QUOTED/DECLINED/WITHDRAWN`, `REFERRED -> QUOTED/DECLINED/WITHDRAWN`, `QUOTED -> BOUND/DECLINED/WITHDRAWN`; `BOUND`/`DECLINED`/`WITHDRAWN` terminal | the graph is implied by the clearance, rating, referral, quote, bind, and declination commands, not a status command |
| Workflow commands | the status command and the conversion command (M-60) | clearance, rating, referral, quote, bind, declination, producer licensing/appointment, and the product/form/rating-plan slices |
| Amount | `requestedLimitAmount` is a JSON number with at most four fraction digits plus a separate currency in the HTTP projection and create body (`BigDecimal` without `@JsonFormat`), while the event payload converts the same value to a scale-4 decimal string | `requested_limits jsonb`; SPEC 10.3 requires a decimal string and never a JSON number (M-03) |
| List | bare tenant-scoped array, newest update first; no public `q`/`status` filter (the expert implements both) | SPEC 7.6 cursor pagination and the submission-list filters by producer, tort, status, age, and premium |
| Concurrency / idempotency | create, read, and transition return the submission `ETag`; `If-Match` and `Idempotency-Key` are accepted and forwarded but the expert compares neither the tag nor an `expectedVersion` body field and does not replay the key; a lost internal version race is 409 `CONCURRENT_MODIFICATION` | SPEC 12.6 requires `If-Match`/`Idempotency-Key` on transaction submission |
| Duplicate | 409 `DUPLICATE_SUBMISSION_NUMBER` on the unique tenant number; the locked allocator should prevent the collision, so the code is a database backstop | no explicit duplicate rule |
| Events | `policy.submission.created` and `policy.submission.status-changed`, keyed by the `UnderwritingSubmission` aggregate at version 1 and at version + 1 per transition; conversion adds `policy.submission.converted` (M-60) | `policy.submission.received` and `policy.submission.declined` (both planned); no status or conversion fact |
| Error envelope | canonical Policy `Problem` with `application/problem+json` | canonical `Problem` (matches) |

Additional differences:

- The public domain route does not expose the expert's list filters. The
  `q`/`status` parameters exist only on the expert's `/internal/v1` alias, while
  the public list is the bare array ordered by `updated_at DESC, id ASC`.
- Apart from conversion (M-60), the status command is the only mutation: there
  is no submission edit or delete, no clearance/rating/referral/quote/bind/
  declination command, no underwriting-authority check, and no declination
  record. A `BOUND` status edge alone does not create a policy; conversion is a
  separate command that accepts a `QUOTED` or unlinked `BOUND` submission.
- The `reason` is carried only on the event; the row stores the resulting
  status, version, and `updated_at`. There is no status-history table, so a
  consumer must persist the event to explain a transition.
- The number allocator advances in its own short transaction, so a rollback of
  the submission insert leaves a gap in the per-tenant sequence. The first
  create for a tenant can race on the counter row; the losing transaction
  retries against the committed row up to three times.
- `requestedLimitAmount` and `requestedLimitCurrency` are a flat
  amount/currency pair validated as a non-negative amount normalized to scale 4
  HALF_UP plus a three-letter currency; `tortCodes` is a PostgreSQL `text[]`
  with a 20-entry and 32-character cap, blank codes are rejected, and a missing
  list is stored as an empty array. `notes` is capped at 2000 characters and a
  blank value is stored as null.
- `submissionNumber` is formatted from the current UTC year and the per-tenant
  sequence, so the year prefix can change while the sequence continues.
- The status value is trimmed and upper-cased before the graph check, so
  `quoted` is accepted as `QUOTED`; an unknown value is 400
  `INVALID_SUBMISSION_STATUS`. The reason is trimmed, blank becomes null, and a
  value beyond 500 characters is 400 `INVALID_SUBMISSION_REASON` at the expert
  (the domain's Bean Validation rejects it first as 400 `VALIDATION_ERROR`).
- The domain's missing-tenant code is `MISSING_TENANT_HEADER` (not the
  `TENANT_REQUIRED` used by several other Policy routes) and a malformed tenant
  is `INVALID_TENANT_HEADER`; both are canonical `Problem` bodies. A supplied
  non-DIRECT `X-EIA-Book` is 404 `BOOK_SCOPE_VIOLATION` at the domain, while
  the expert's own non-DIRECT guard returns 404 `NOT_FOUND`.
- `applicantPartyId` is a plain UUID reference: the expert does not call the
  Party vertical, so an unknown applicant is accepted. `productCode` is a free
  text code with a 64-character cap, not a `product_id` foreign key, and no
  product/version or filed-form check runs.

Consequences:

- A consumer of the SPEC `policy.submission.received` name sees nothing; the
  catalog publishes and implements `policy.submission.created` instead, so a
  subscriber must consume the implemented name to observe intake.
- Because the workflow edge is a plain status command and conversion does not
  require clearance or an approved rating, the implemented workflow cannot
  express SPEC 11.2.14's clearance, rating, referral, quote, authority, and
  declination evidence. UWR-01 (no bind without clearance and rating) and
  UW-01 through UW-05 are not enforced.
- A retried create with an `Idempotency-Key` makes a second submission with a
  new number, and a retried transition applies again; clients must not treat
  the accepted key as a replay guarantee.

Evidence:

- `repos/eia-policy-domain/.../SubmissionController.java:33-113` (public
  intake routes, header-only tenant, optional book, ETag, replay marker,
  Location) and `:115-140` (the conversion route and envelope; M-60)
- `repos/eia-policy-domain/.../SubmissionService.java:22-51`,
  `SubmissionDto.java:22-51`, `CreateSubmissionCommand.java:25-34`, and
  `UpdateSubmissionStatusCommand.java:12-16` (projection and body shapes)
- `repos/eia-policy-domain/.../PolicyClient.java:773-951` (list/read/create/
  status calls, `{submission}` envelope and array/`items` list acceptance,
  tenant projection, and 400/404/409 preservation)
- `repos/eia-policy-domain/.../Problems.java:117-121` (submission codes)
- `repos/eia-policy-expert/.../UnderwritingSubmissionController.java:28-97`
  (dual base, tenant query/header, DIRECT-book gate, 201/200 and ETags) and
  `:99-122` (the bare-policy conversion response; M-60)
- `repos/eia-policy-expert/.../UnderwritingSubmissionService.java:61-195`
  (list filters, create, conditional transition, conflict and event insert)
- `repos/eia-policy-expert/.../UnderwritingSubmissionRules.java:25-229`
  (status set, transition graph, normalization and caps)
- `repos/eia-policy-expert/.../UnderwritingSubmissionRepository.java:63-140`
  (tenant reads, newest-first ordering, insert, conditional update)
- `repos/eia-policy-expert/.../UnderwritingSubmissionNumberAllocator.java`
  (locked per-tenant counter and `SUB-{YYYY}-{7 digits}` formatting)
- `repos/eia-policy-expert/.../UnderwritingSubmission.java:19-38`,
  `UnderwritingSubmissionView.java:13-44`,
  `CreateUnderwritingSubmissionRequest.java:17-26`, and
  `UpdateUnderwritingSubmissionStatusRequest.java:11-15`
- `repos/eia-policy-expert/.../PolicyEvents.java:62-64,317-400` (the three
  submission facts including conversion, aggregate type/subject, payload
  fields, and aggregate version)
- `repos/eia-policy-expert/src/main/resources/schema.sql` (`underwriting_submission`
  and `underwriting_submission_number_seq`, unique number, limit/currency/status
  checks)
- `repos/eia-policy-expert/src/test/java/com/eia/policy/expert/UnderwritingSubmissionIntegrationTest.java:78-362`
  (create/list/read/transitions, per-tenant numbering, tenant wall, both events,
  rollback, validation, and sequence gap)
- `repos/eia-policy-domain/src/test/java/com/eia/policy/domain/SubmissionControllerTest.java:71-361`
  and `SubmissionClientTest.java:44-530` (routes, headers, ETag, replay marker,
  problem preservation, and wire shapes)

Resolution: amend SPEC 11.2.14 to the implemented intake and conversion slices
and the three event names, or implement the clearance, rating, referral, quote,
bind, and producer chain with the full status set and align the amount
serialization, pagination, concurrency, and idempotency. In either case decide
whether conversion must become the SPEC quote/bind command with a required
clearance and approved rating worksheet, and whether a `BOUND` edge must require
the same (UWR-01, UW-01).

## M-60 Submission conversion is a SPEC-less command with a bare-policy expert shape

Policy 2.19.0 adds `POST /api/v1/policies/submissions/{submissionId}/convert`
and its `/internal/v1` expert alias; Policy 2.20.0 adds the tenant + operation
keyed replay with the stored policy body and original `ETag`; Policy 2.21.0
adds the canonical request hash and the 409 `IDEMPOTENCY_CONFLICT`. SPEC 11.2.14
models the submission-to-policy step as separate quote and bind commands with
the clearance and rating preconditions; it names no conversion route, no replay
rule, and no conversion event. The implemented command creates a `DRAFT` policy
directly from a `QUOTED` submission (or from a `BOUND` submission that has no
linked policy yet) and publishes a new fact.

| Aspect | Implemented | SPEC 11.2.14 / 11.2.9 |
|---|---|---|
| Routes | Public `POST /api/v1/policies/submissions/{submissionId}/convert`; expert alias `POST /internal/v1/policies/submissions/{submissionId}/convert` | Quote and bind commands; no conversion route |
| Request | `{premiumAmount, premiumCurrency, expirationDate?}`; premium is non-negative with up to four fraction digits, the currency is an ISO 4217 code, and the expiration defaults to the requested effective date plus one year and must be after it | Quote/premium and bind evidence on the quote and bind commands |
| Public response | 201 `{submission, policy}` on a fresh conversion; 200 with `Idempotent-Replayed: true` on a linked-policy or stored-key replay; strong policy `ETag` on both, with the first call's version on a stored-key replay and the submission member projected from the linked submission | No conversion response |
| Expert response | 201/200 **bare** `Policy` with `ETag` and `Idempotent-Replayed`; the expert accepts `Idempotency-Key` and replays the stored bare policy, and does not compose the public envelope | n/a |
| Convertible states | `QUOTED`, or `BOUND` with no linked policy. `RECEIVED`, `REFERRED`, `DECLINED`, and `WITHDRAWN` are 409 `SUBMISSION_NOT_CONVERTIBLE` with `meta.submissionId` and `meta.currentStatus` | Bind requires clearance and an approved rating worksheet (UWR-01, UW-01); the implemented conversion does not |
| Policy link | Nullable `Policy.submissionId`, written together with a policy version bump and unique per tenant (`(tenant_id, submission_id)`), so one submission creates at most one policy | SPEC 11.2.14 defines the linkage but no field nullability or uniqueness rule |
| Submission link | Nullable `PolicySubmission.policyId`; a `QUOTED` submission moves to `BOUND`, a `BOUND` submission keeps its status and only advances its version | SPEC has no submission projection or version rule |
| Policy created | `DRAFT` with the normal server-generated `POL-{YYYY}-{7 digits}` number and version 1 after the link; one base coverage and limit schedule when the requested limit is positive | Quote/bind policy |
| Events | `policy.submission.converted {submissionId, submissionNumber, policyId, policyNumber}` plus the normal `policy.policy.created`, in the same transaction as the policy, coverage, and link | `policy.submission.received` and `policy.submission.declined` only |
| Idempotency | The optional `Idempotency-Key` is stored and replayed in the `(tenant, operation = conversion, key)` scope after comparing a canonical request hash: a first keyed conversion stores its 201 (or linked-policy 200) bare-policy body and status, an identical canonical request returns 200 with the stored policy body and original `ETag` (the public envelope projects `submission` from the link), and a changed request is 409 `IDEMPOTENCY_CONFLICT` with `meta.operation`/`meta.key` and no write. The hash covers `submissionId` and the normalized terms; a blank key is absent, a 129+ key is 400 `INVALID_IDEMPOTENCY_KEY`, a legacy null-hash row replays, and the linked-policy 200 replay remains when no stored key exists | SPEC 12.6 request-hash conflict (matches) |
| Concurrency | The command locks the submission row (`SELECT ... FOR UPDATE`); the tenant-scoped unique `submission_id` is the second guard. No `If-Match`; a lost write is 409 `CONCURRENT_MODIFICATION` | SPEC 12.6 `If-Match` |
| Errors | 400 `VALIDATION_ERROR`/`INVALID_CONVERSION_PREMIUM`/`INVALID_CONVERSION_CURRENCY`/`INVALID_CONVERSION_EXPIRATION`; 404 `SUBMISSION_NOT_FOUND`/`BOOK_SCOPE_VIOLATION`; 409 `SUBMISSION_NOT_CONVERTIBLE`/`CONCURRENT_MODIFICATION`; 422 `PRODUCT_CODE_TOO_LONG_FOR_POLICY` | Canonical `Problem` envelope (matches) |

Additional differences:

- The public `Policy` projection does not expose `submissionId`:
  `PolicyDto` has no such member, so the domain drops the expert's field from
  policy reads and from the conversion envelope's `policy`. The expert `Policy`
  record returns it (null for a policy not created by conversion). The contract
  therefore documents `Policy.submissionId` as optional and nullable, with the
  public omission recorded here rather than claimed on the wire.
- The public domain requires an upper-case `premiumCurrency` (`@Pattern`
  `[A-Z]{3}`) and at most four `premiumAmount` fraction digits, while the expert
  trims and upper-cases the currency and rounds a longer fraction HALF_UP, so a
  lowercase code or a fifth fraction digit is accepted only on the expert alias.
  A missing or malformed public body is 400 `VALIDATION_ERROR`; the expert's own
  field codes are `INVALID_CONVERSION_PREMIUM`,
  `INVALID_CONVERSION_CURRENCY`, and `INVALID_CONVERSION_EXPIRATION`.
- The 422 `PRODUCT_CODE_TOO_LONG_FOR_POLICY` is a conversion-only rule: a
  submission accepts a product code up to 64 characters, but the policy column
  is 32, so a longer code can be created but not converted. It is a
  `category: BUSINESS_RULE` problem.
- A replay with an identical canonical request returns the stored policy (key
  replay) or the current linked policy (no matching reservation). A changed
  premium or expiration under the same stored key is 409
  `IDEMPOTENCY_CONFLICT`. A new key on an already-linked submission still
  returns the current linked policy without comparing its terms with the
  original conversion, because the command does not store the conversion
  request on the submission; the first conversion remains authoritative for
  that path.
- Conversion writes two facts: the new `policy.submission.converted` against
  the `UnderwritingSubmission` aggregate (post-conversion submission version +
  the outbox convention offset; the integration test sees aggregate version 3
  for a submission converted from `QUOTED`) and the normal `policy.policy.created`
  against the new policy. A consumer that only knows the SPEC names sees neither.
- The commit order is policy insert, base coverage/limit, `submission_id` link
  with a policy version bump, then the submission status/version update and the
  outbox rows. The replay checks the linked policy first and returns it before
  re-validating the request terms.
- The expert also maps the same conversion path under `/api/v1`; the contract
  documents `/internal/v1` as the expert surface and the public path as the
  domain surface.
- The policy link update uses the policy version it created, so the returned
  policy is version 1 for a fresh conversion. A stored-key replay returns the
  body and `ETag` captured by that first call; a linked-policy replay returns
  the linked policy at its current version, which may be higher if the policy
  was changed after conversion.

Consequences:

- A caller that expects SPEC UWR-01/UW-01 evidence (clearance and an approved
  rating worksheet) can convert a `QUOTED` submission without either; the
  command only checks the submission status.
- A retried conversion is safe by the submission link and by the stored
  `Idempotency-Key` response. A retried request with different premium terms is
  now 409 `IDEMPOTENCY_CONFLICT` when it reuses the stored key, but a new key on
  an already-linked submission still returns the current linked policy and
  ignores the new terms, so clients must treat the first successful conversion
  as authoritative (M-06, M-07).
- Public policy reads cannot navigate from the policy to its source submission
  until `submissionId` is projected; the conversion envelope and the expert read
  can.

Evidence:

- `repos/eia-policy-domain/.../SubmissionController.java:115-140` (public
  conversion route, 201/200, ETag fallback, replay marker)
- `repos/eia-policy-domain/.../ConvertSubmissionCommand.java:20-26` (request
  members and the upper-case currency pattern)
- `repos/eia-policy-domain/.../SubmissionConversionResult.java:12-15` (public
  `{submission, policy}` envelope)
- `repos/eia-policy-domain/.../SubmissionService.java:53-65` (key normalization
  and delegation)
- `repos/eia-policy-domain/.../PolicyClient.java:875-897,967-1017` (expert
  conversion call, both accepted response shapes, scoped read-back, ETag/replay
  mapping)
- `repos/eia-policy-domain/.../SubmissionDto.java:25-41` (optional `policyId`)
- `repos/eia-policy-domain/.../PolicyDto.java:12-31` (no `submissionId`, the
  public projection gap)
- `repos/eia-policy-domain/.../PolicyClient.java:1474-1502` (400/404/409/422
  problem preservation)
- `repos/eia-policy-expert/.../UnderwritingSubmissionController.java:99-122`
  (expert route and bare-policy response)
- `repos/eia-policy-expert/.../PolicyIdempotencyService.java:84-108`
  (conversion hash compare, 409 conflict with `meta.operation`/`meta.key`,
  legacy null-hash replay, stored-response completion),
  `PolicyIdempotencyRepository.java:28-76`, `IdempotencyKeys.java:83-99` (the
  conversion `requestHash`), `src/main/resources/schema.sql:167-201`,
  `IdempotencyKeysTest.java`, and
  `PolicyIdempotencyReplayIntegrationTest.java`
  (`conversionReplayAcceptsAnEquivalentBodyWithDifferentScale`,
  `reusingAConversionKeyWithADifferentPremiumConflictsWithoutWriting`,
  `reusingAConversionKeyWithADifferentExpirationConflictsWithoutWriting`,
  `aConversionKeyCannotReplayAPolicyFromAnotherSubmission`, stored body/ETag
  replay, tenant and operation scope, 129-character rejection).
- `repos/eia-policy-expert/.../ConvertSubmissionRequest.java:18-24`,
  `SubmissionConversionService.java:82-157` (eligibility, term validation,
  policy creation, coverage, link, status/version movement, event insert,
  replay)
- `repos/eia-policy-expert/.../UnderwritingSubmissionRules.java:109-174`
  (convertible statuses, premium/currency/expiration normalization,
  product-code gate)
- `repos/eia-policy-expert/.../PolicyEvents.java:360-379` (the four-member
  conversion payload and aggregate version)
- `repos/eia-policy-expert/.../Policy.java:27-51` (nullable `submissionId`),
  `PolicyRepository.java:93-126,252-265` (find by submission, bulk projection,
  conditional assign and version bump)
- `repos/eia-policy-expert/src/main/resources/schema.sql:852-861` (nullable
  `submission_id`, FK, tenant-scoped unique, index)
- `repos/eia-policy-expert/src/test/java/com/eia/policy/expert/SubmissionConversionIntegrationTest.java:66-301`
  (fresh conversion, coverage, links, versions, event payload and aggregate
  version, replay, non-convertible statuses, body validation, tenant wall,
  explicit expiration, unlinked BOUND conversion)
- `repos/eia-policy-expert/src/test/java/com/eia/policy/expert/UnderwritingSubmissionControllerTest.java:285-370`
  and `SubmissionConversionServiceTest.java` (controller shape and service
  rules)
- `repos/eia-policy-domain/src/test/java/com/eia/policy/domain/SubmissionControllerTest.java:389-510`
  and `SubmissionConversionClientTest.java:41-330` (public envelope, replay,
  ETag fallback, validation, book wall, both expert response shapes, problem
  preservation)

Resolution: amend SPEC 11.2.14 to the implemented conversion command and the
`policy.submission.converted` name, or implement the SPEC quote/bind command
chain with the clearance/rating gates and align the response shape, replay
semantics, and links. The key is now stored and request-hashed, so the remaining
replay decision is whether a new key on an already-linked submission should
compare against the original conversion terms (currently it returns the linked
policy without a comparison), and whether `Policy.submissionId` should be
public.

## Validation evidence

The repository validator was run on the working tree after the 2026-10-22
Notifications template-approver contract:

```text
$ python scripts/validate_contracts.py
EIA canonical contract validation
repository: .../repos/eia-contracts
python: 3.12.8 (standard library only)

OpenAPI 3.1 documents
  OK openapi/party.yaml  15 paths, 25 operations
  OK openapi/policy.yaml  59 paths, 77 operations
  OK openapi/contract.yaml  43 paths, 62 operations
  OK openapi/direct-claims.yaml  51 paths, 74 operations
  OK openapi/assumed-claims.yaml  41 paths, 58 operations
  OK openapi/cession.yaml  9 paths, 11 operations
  OK openapi/retrocession.yaml  9 paths, 11 operations
  OK openapi/document.yaml  18 paths, 24 operations
  OK openapi/payment.yaml  13 paths, 16 operations
  OK openapi/notifications.yaml  12 paths, 15 operations

AsyncAPI 3 documents
  OK asyncapi/party.yaml  15 event channels
  OK asyncapi/policy.yaml  39 event channels
  OK asyncapi/contract.yaml  32 event channels
  OK asyncapi/direct-claims.yaml  28 event channels
  OK asyncapi/assumed-claims.yaml  21 event channels
  OK asyncapi/cession.yaml  17 event channels
  OK asyncapi/retrocession.yaml  17 event channels
  OK asyncapi/document.yaml  24 event channels
  OK asyncapi/payment.yaml  20 event channels
  OK asyncapi/notifications.yaml  15 event channels
  OK catalog: 228 unique published events across 10 verticals

JSON Schema 2020-12 documents

JSON Reference resolution
  OK walked 22 YAML documents

Result
  PASS 17002 checks, 0 failures
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
  (exit 1); the working copy was left unchanged. The Contract
  technical-account-line pass added four more: renaming the
  `/api/v1/contracts/{contractId}/technical-accounts/{accountId}/lines` path,
  renaming the `LineSummary` schema, adding `DRAFT` to the
  `TechnicalAccountLineType` enum, and dropping
  `contract.technical-account.line-added` from the Contract catalog
  `implemented` list each fail with the specific missing-operation, schema,
  enum, or implemented-event message. All four were run on a throwaway copy and
  exited non-zero (exit 1); the working copy was left unchanged. The Policy
  legal-entity pass added four more: renaming the
  `/api/v1/legal-entities/{legalEntityId}` path, renaming the `LegalEntity`
  schema, making the nullable `Policy.legalEntityId` non-nullable, and dropping
  `policy.legal-entity.created` from the Policy catalog `implemented` list each
  fail with the specific missing-operation, schema/nullability, or
  implemented-event message. All four were run on a throwaway copy and exited
  non-zero (exit 1); the working copy was left unchanged. The expanded
  technical-account-line pass added four more: reverting the
  `TechnicalAccountLineType` enum to the four component values, removing the
  optional `details` map from `TechnicalAccountLineTotals`, deleting the
  `bucketTotals` normalization sentence from the line-list description, and
  restoring per-type reconciliation wording instead of the bucket mapping each
  fail with the specific 13-type enum, details-map, `bucketTotals`, or
  bucket-mapping message. All four were verified by mutating parsed copies in
  memory; the working copy was left unchanged. The credit-application pass
  added four more: removing the `installmentId` property from
  `UpdateCreditNoteStatusRequest`, making `CreditNote.appliedInstallmentId`
  non-nullable, removing `creditedAmount` from the applied
  `PolicyCreditNoteData` payload, and dropping `CREDITED` from
  `Installment.status` each fail with the specific optional-uuid, nullability,
  applied-payload, or status-enum message. All four were run on throwaway
  copies and exited non-zero (exit 1); the working copy was left unchanged. The
  program-capacity pass added three more: removing `capacityAmount` from the
  required `Program` keys, replacing the `CreateProgramRequest`
  `dependentRequired` mapping with an empty map, and removing
  `INVALID_PROGRAM_CAPACITY` from the create description each fail with the
  specific required-field, both-or-neither, or missing-code message. All three
  were run on a throwaway copy and exited non-zero (exit 1); the working copy
  was left unchanged. The document hold/disposition pass added four more:
  renaming the `/api/v1/documents/{documentId}/hold/release` path, removing
  `statusBeforeHold` from the required `Document` keys, dropping
  `RETENTION_NOT_EXPIRED` from the dispose 409 description, and dropping
  `document.legal-hold.placed` from the Document catalog `implemented` list
  each fail with the specific missing-operation, required-field,
  conflict-code, or implemented-event message. All four were run on a
  throwaway copy and exited non-zero (exit 1); the working copy was left
  unchanged. The credit-note reversal pass added four more: removing the
  optional `reason` property from `UpdateCreditNoteStatusRequest`, making
  `CreditNote.reversedAt` non-nullable, dropping `policy.credit-note.reversed`
  from the Policy catalog `implemented` list, and removing `REVERSED` from
  `CreditNoteStatus` each fail with the specific optional-reason, nullability,
  implemented-event, or status-enum message. All four were run on throwaway
  copies and exited non-zero (exit 1); the working copy was left unchanged. The
  cancellation-linked credit-note pass added four more: removing the required
  `cancellationId` from `CreditNote.required`, widening
  `Cancellation.cancellationNumber` from 32 to 64 characters, dropping
  `policy.credit-note.created` from the Policy catalog `implemented` list, and
  removing the optional `CreateCreditNoteRequest.cancellationId` property each
  fail with the specific required-list, nullable-string, implemented-event, or
  optional-uuid message. All four were run on a throwaway copy and exited
  non-zero (exit 1); the working copy was left unchanged. The Direct Claims
  settlement-payment-link pass added five more: renaming the public settlement
  payment-link path, renaming `Settlement.paymentId`, making
  `SettlementPaymentRequest.paymentId` non-nullable, dropping
  `direct.claim.settlement-payment-linked` from the catalog `implemented` list,
  and removing the `DirectClaimSettlementPaymentLinked` channel each fail with
  the specific missing-operation, nullable-uuid, implemented-event, or
  missing-channel message. All five were run on a throwaway copy and exited
  non-zero (exit 1); the working copy was left unchanged. The payment
  status-transition pass added five more: renaming the
  `/api/v1/payments/{paymentId}/status` path, removing one documented edge
  (`` `DRAFT` -> `CANCELLED` ``), making `expectedVersion` required in
  `UpdatePaymentStatusRequest`, widening `reason` from 200 to 400 characters,
  and re-adding the implemented status path to `x-planned-operations` each fail
  with the specific missing-operation, missing-edge, required-field, bounds, or
  planned-route message. All five were run on a throwaway copy and exited
  non-zero (exit 1); the working copy was left unchanged. The Document
  content-tombstone pass added four more: removing the DELETE operation,
  dropping `deleted` from the required `DocumentContent` keys, removing
  `document.content.deleted` from the Document catalog `implemented` list, and
  removing the 410 responses each fail with the specific missing-operation,
  required-field, implemented-event, or gone-response message. All four were run
  on a throwaway copy and exited non-zero (exit 1); the working copy was left
  unchanged. The Notifications DUNNING_NOTICE pass added three more: removing
  the enum member, moving it below `NEW_DOCUMENT_UPLOAD`, and pointing
  `CreateNotificationRequest.notificationType` at another schema each fail with
  the specific missing-member, position, or reference message. All three were
  run on a throwaway copy and exited non-zero (exit 1); the working copy was
  left unchanged. The payment allocation-reversal pass added four more:
  renaming the `/api/v1/payments/{paymentId}/allocations/{allocationId}/reverse`
  path, removing `ALLOCATION_ALREADY_REVERSED` from the reverse description,
  making `PaymentAllocation.reversedAt` non-nullable, and dropping
  `payment.allocation.reversed` from the Payment catalog `implemented` list
  each fail with the specific missing-operation, conflict-code, nullability, or
  implemented-event message. All four were run on a throwaway copy and exited
  non-zero (exit 1); the working copy was left unchanged. The Notifications
  template-management pass added five more: renaming the approve path, removing
  `TEMPLATE_ALREADY_ACTIVE` from the approve 409 description, making
  `NotificationTemplate.approvedBy` non-nullable, dropping
  `notifications.template.retired` from the catalog `implemented` list, and
  removing the `NotificationTemplateData` message from the created channel each
  fail with the specific missing-operation, conflict-code, nullability,
  implemented-event, or payload-message message. All five were run on a
  throwaway copy and exited non-zero (exit 1); the working copy was left
  unchanged. The Policy premium-audit pass added four more: renaming the
  `/api/v1/policies/{policyId}/premium-audit` path, removing `auditedPremium`
  from `ApplyPremiumAuditRequest.required`, marking the
  `policy.policy.premium-audited` channel planned, and dropping
  `policy.policy.premium-audited` from the Policy catalog `implemented` list
  each fail with the specific missing-operation, required-list,
  implemented-channel, or implemented-event message. All four were run on a
  throwaway copy and exited non-zero (exit 1); the working copy was left
  unchanged. The Policy billing-adjustment pass added four more: renaming the
  `/api/v1/policies/{policyId}/billing/adjustment` path, removing `reason` from
  `BillingAdjustmentRequest.required`, dropping `NO_PREMIUM_ADJUSTMENT` from the
  operation description, and dropping `policy.billing-plan.adjusted` from the
  Policy catalog `implemented` list each fail with the specific
  missing-operation, required-list, missing-code, or implemented-event message.
  All four were run on a throwaway copy and exited non-zero (exit 1); the working
  copy was left unchanged. The Direct Claims litigation pass added four more:
  removing `LitigationRequest.damagesSought`, breaking the request
  `dependentRequired` pair, marking the `direct.claim.litigation-created`
  channel planned, and dropping `direct.claim.litigation-created` from the
  catalog `implemented` list each fail with the specific schema, pair,
  implemented-channel, or implemented-event message. All four were run on a
  throwaway copy and exited non-zero (exit 1); the working copy was left
  unchanged. The Notifications source-linkage pass added five more: removing
  `sourceId` from the `Notification` projection, removing `CONTRACT` from the
  `NotificationSourceType` enum, deleting the sourceType-requires-sourceId
  `allOf` branch from `CreateNotificationRequest`, removing the
  `NotificationCreatedData` message reference from the created channel, and
  dropping `INVALID_SOURCE_REFERENCE` from the public create description each
  fail with the specific missing-field, enum, pairing-rule, payload-message, or
  error-documentation message. All five were run on a throwaway copy and exited
  non-zero (exit 1); the working copy was left unchanged. The Notifications
  source-filter pass added three more: removing the `sourceId` parameter from
  `GET /api/v1/notifications`, adding a `sourceReference` query parameter to the
  same operation, and removing `INVALID_SOURCE_FILTER` from the public list
  description each fail with the specific parameter, extra-filter, or
  error-documentation message. All three were run on a throwaway copy and exited
  non-zero (exit 1); the working copy was left unchanged. The Party
  reference-data pass added eight more, each run on a throwaway copy and exited
  non-zero (exit 1): renaming the public
  `/api/v1/parties/{partyId}/identifiers` path fails with the
  missing-operation message; changing a `PartyIdentifierType` member fails with
  the exact-enum message; removing `party.party.identifier-added` from both
  catalog lists fails with the published and implemented set messages; renaming
  `DUPLICATE_PARTY_ADDRESS` fails with the 409 documentation message on both
  address operations; renaming `DUPLICATE_PARTY_IDENTIFIER` fails the same way
  on both identifier operations; adding `issuingAuthority` to the required list
  of the two projections fails with the required-set message; renaming the
  `PartyIdentifierAddedData` message reference fails with the
  unresolved-reference message; and marking the identifier request body
  `required: false` fails with the required-body message. The working copy was
  left unchanged. The Party status-transition pass added five more: renaming the
  public `/api/v1/parties/{partyId}/status` path fails with the missing required
  path message; adding `UNKNOWN` to `PartyStatus` fails with the exact-enum
  message; removing the public 200 `ETag` header fails with the shared-ETag
  message; marking the SPEC `party.party.status-changed` channel implemented
  fails with the must-stay-planned message and the implemented-channel/catalog
  mismatch; and removing the `PartyStatusUpdatedData` reference from the
  `party.party.updated` channel fails with the missing payload-reference
  message. Each case backed up the mutated file, ran the validator, and restored
  the file; all five exited non-zero (exit 1) and the working copy was left
  unchanged. The Notifications source-type pass added three more, each run on a
  throwaway copy and exited non-zero (exit 1): removing `CESSION` from the
  `NotificationSourceType` enum fails five checks with the exact-enum message on
  the schema, the projection, both create requests, and the list filter; moving
  `OTHER` before `PARTY` fails three checks with the exact-enum and
  `OTHER`-last messages; and removing `DOCUMENT` from the sent payload enum
  fails one check with the `NotificationSentData` enumeration message. The
  working copy was left unchanged. The Notifications delivery-attempt pass
  added three more: renaming the public
  `/api/v1/notifications/{notificationId}/attempts` path fails with the missing
  required-path and missing delivery-attempt operation messages; removing
  `providerReference` from `Notification.required` fails with the
  required-member message; and renaming `deliveredAt` in the
  `NotificationSentData` payload fails with the missing-property and
  nullable-date-time messages. All three were run on a throwaway copy, exited
  non-zero (exit 1), and the working copy was left unchanged. The Policy
  rating-worksheet pass added five more: renaming the
  `/api/v1/policies/{policyId}/rating` path fails with the missing
  rating-operation and latest-worksheet messages; removing `baseRate` from
  `RatePolicyRequest.required` fails with the exact-required-list message;
  adding `LOSS_COST` to `RatingMethod` fails with the exact-enum message;
  marking the `policy.policy.rated` channel planned fails with the
  must-be-implemented message; and dropping `policy.policy.rated` from the
  Policy catalog `implemented` list fails with the channel/catalog-set message.
  All five were run on a throwaway copy, exited non-zero (exit 1), and the
  working copy was left unchanged. The Party maintenance pass added five more:
  renaming the public
  `/api/v1/parties/{partyId}/identifiers/{identifierId}` path fails with the
  missing required-path and missing identifier-maintenance operation messages;
  making the identifier replacement `requestBody.required: false` fails with
  the required-body message; removing the `identifierId` path parameter fails
  with the missing child-id parameter message; dropping
  `party.party.address-deleted` from both catalog lists fails with the published
  and implemented set messages; and removing `issuingAuthority` from the
  identifier update `changedFields` enum fails with the exact-enum message. All
  five were run on a throwaway copy, exited non-zero (exit 1), and the working
  copy was left unchanged. The Policy underwriting-submission pass added five
  more: renaming the `/api/v1/policies/submissions` path fails with the missing
  required-path and missing submission-operation messages; removing
  `requestedLimitAmount` from `CreatePolicySubmissionRequest.required` fails
  with the exact-required-list message; adding `CLEARANCE` to
  `PolicySubmissionStatus` fails with the exact-enum message; dropping the
  `REFERRED -> QUOTED/DECLINED/WITHDRAWN` transition bullet fails with the
  missing-edge message; and dropping `policy.submission.created` from both
  catalog lists fails with the published and implemented set messages. All five
  were run on a throwaway copy, exited non-zero (exit 1), and the working copy
  was left unchanged. The Policy submission-conversion pass added five more:
  renaming the public
  `/api/v1/policies/submissions/{submissionId}/convert` path fails with the
  missing required-path and missing conversion-operation messages; removing
  `premiumCurrency` from `ConvertPolicySubmissionRequest.required` fails with
  the exact-required-list and member-order messages; replacing the expert 201
  bare `Policy` with `ConvertPolicySubmissionResult` fails with the
  bare-Policy-response message; removing `Policy.submissionId` fails with the
  nullable-uuid message; and dropping `policy.submission.converted` from both
  catalog lists fails with the published/implemented set, not-published, and
  must-be-listed messages. All five were run on a throwaway copy, exited
  non-zero (exit 1), and the working copy was left unchanged. The Policy rating
  and conversion replay pass added five more: removing the rating `200`
  response fails with the missing replay body, header, and description
  messages; changing the shared `IdempotencyKey` maximum from 128 to 255 fails
  with the 1-128-character message; removing the conversion `200`
  `Idempotent-Replayed` header fails with the shared-header message; and
  reintroducing `does not replay` into the rating or public conversion
  description fails the stale-caveat message on the affected operation. All
  five were run on a throwaway copy, exited non-zero (exit 1), and the working
  copy was left unchanged. The Policy idempotency request-hash pass added four
  more, each run on a throwaway copy and exited non-zero (exit 1): removing
  `meta.operation` from the rating 409 description fails the missing
  conflict-meta message; removing `request hash` from the public conversion 200
  replay fails the missing replay-description message; reintroducing `does not
  compare` into the expert conversion description fails the stale-caveat
  message; and removing `legacy` from the shared `IdempotencyKey` description
  fails the missing component-term message. The Notifications
  template-approver pass added four more, each run on a throwaway copy and
  exited non-zero (exit 1): widening
  `ApproveNotificationTemplateRequest.approvedBy.maxLength` from 128 to 255
  fails the required 1-128-character directory-id message; restoring
  `format: uuid` on that property fails the not-a-uuid message; and widening
  `NotificationTemplateData.approvedBy.maxLength` from 128 to 255 fails the
  nullable directory-id payload message. Removing `server-assigned` from the
  approve description fails the missing-term message. The working copy was left
  unchanged.

## Resolution policy

1. A deviation is fixed in the service, not by weakening the contract, unless
   the Architecture owner accepts the implemented shape as canonical.
2. When a deviation is fixed, remove it from this file in the same change that
   updates the contract, and record the closure in the closed-mismatches table.
3. A new deviation must be added here with the same evidence standard: source
   path and symbol or line, and the SPEC section it violates.

