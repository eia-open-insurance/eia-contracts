#!/usr/bin/env python3
"""Validate the EIA canonical API contracts.

Runs with the Python standard library only. It deliberately does not depend on
PyYAML, jsonschema, openapi-spec-validator, Node.js, or any other tool that a
contributor would have to install. The script provides:

1. A strict parser for the YAML subset used by this repository (block
   mappings, block sequences, quoted and plain scalars, flow lists and maps,
   folded and literal block scalars, comments). Constructs outside that subset
   are rejected with a line number instead of being guessed.
2. Structural checks for every OpenAPI 3.1 and AsyncAPI 3 document: the
   required paths and methods, operation metadata, response presence, and the
   ten global-search operations with their shared SearchResponse envelope.
3. Cross-document checks: every JSON Reference resolves, the AsyncAPI catalog
   and the per-vertical event documents name the same events, and the JSON
   Schemas contain the canonical required members and validate their own
   examples.
4. A non-zero exit code and a printed failure list when any check fails.

Usage:
    python scripts/validate_contracts.py
    python scripts/validate_contracts.py --verbose

Exit codes:
    0  every check passed
    1  one or more checks failed
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPENAPI_DIR = ROOT / "openapi"
ASYNCAPI_DIR = ROOT / "asyncapi"
SCHEMA_DIR = ROOT / "schemas"

VERTICAL_FILES = [
    "party",
    "policy",
    "contract",
    "direct-claims",
    "assumed-claims",
    "cession",
    "retrocession",
    "document",
    "payment",
    "notifications",
]

HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")

REQUIRED_OPENAPI_PATHS = {
    "party": [
        ("/api/v1/parties", "get"),
        ("/api/v1/parties", "post"),
        ("/api/v1/parties/{partyId}", "get"),
        ("/internal/v1/parties", "get"),
        ("/internal/v1/parties", "post"),
        ("/internal/v1/parties/{partyId}", "get"),
    ],
    "policy": [
        ("/api/v1/policies", "get"),
        ("/api/v1/policies", "post"),
        ("/api/v1/policies/{policyId}", "get"),
        ("/api/v1/policies/{policyId}/status", "patch"),
        ("/internal/v1/policies", "get"),
        ("/internal/v1/policies", "post"),
        ("/internal/v1/policies/{policyId}", "get"),
        ("/internal/v1/policies/{policyId}/status", "patch"),
    ],
    "contract": [
        ("/api/v1/contracts", "get"),
        ("/api/v1/contracts", "post"),
        ("/api/v1/contracts/{contractId}", "get"),
        ("/api/v1/contracts/{contractId}/status", "patch"),
        ("/internal/v1/contracts", "get"),
        ("/internal/v1/contracts", "post"),
        ("/internal/v1/contracts/{contractId}", "get"),
        ("/internal/v1/contracts/{contractId}/status", "patch"),
    ],
    "direct-claims": [
        ("/api/v1/claims", "get"),
        ("/api/v1/claims", "post"),
        ("/api/v1/claims/{claimId}", "get"),
        ("/api/v1/claims/{claimId}/status", "patch"),
        ("/internal/v1/claims", "get"),
        ("/internal/v1/claims", "post"),
        ("/internal/v1/claims/{claimId}", "get"),
        ("/internal/v1/claims/{claimId}/status", "patch"),
    ],
    "assumed-claims": [
        ("/api/v1/assumed-claims", "get"),
        ("/api/v1/assumed-claims", "post"),
        ("/api/v1/assumed-claims/{assumedClaimId}", "get"),
        ("/api/v1/assumed-claims/{assumedClaimId}/status", "post"),
        ("/api/v1/assumed-claims/claims", "get"),
        ("/api/v1/assumed-claims/claims", "post"),
        ("/api/v1/assumed-claims/claims/{assumedClaimId}", "get"),
        ("/api/v1/assumed-claims/claims/{assumedClaimId}/status", "post"),
        ("/internal/v1/assumed-claims", "get"),
        ("/internal/v1/assumed-claims", "post"),
        ("/internal/v1/assumed-claims/{assumedClaimId}", "get"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/status", "post"),
    ],
    "cession": [
        ("/api/v1/cessions", "get"),
        ("/api/v1/cessions", "post"),
        ("/api/v1/cessions/{cessionId}", "get"),
        ("/api/v1/cessions/{cessionId}/transition", "post"),
        ("/internal/v1/cessions", "get"),
        ("/internal/v1/cessions", "post"),
        ("/internal/v1/cessions/{cessionId}", "get"),
        ("/internal/v1/cessions/{cessionId}/status", "put"),
    ],
    "retrocession": [
        ("/api/v1/retrocessions", "get"),
        ("/api/v1/retrocessions", "post"),
        ("/api/v1/retrocessions/{retrocessionId}", "get"),
        ("/api/v1/retrocessions/{retrocessionId}/transition", "post"),
        ("/internal/v1/retrocessions", "get"),
        ("/internal/v1/retrocessions", "post"),
        ("/internal/v1/retrocessions/{retrocessionId}", "get"),
        ("/internal/v1/retrocessions/{retrocessionId}/status", "put"),
    ],
    "document": [
        ("/api/v1/documents", "get"),
        ("/api/v1/documents", "post"),
        ("/api/v1/documents/{documentId}", "get"),
        ("/api/v1/documents/{documentId}/status", "post"),
        ("/api/v1/documents/{documentId}/hold", "post"),
        ("/api/v1/documents/{documentId}/hold/release", "post"),
        ("/api/v1/documents/{documentId}/dispose", "post"),
        ("/internal/v1/documents", "get"),
        ("/internal/v1/documents", "post"),
        ("/internal/v1/documents/{documentId}", "get"),
        ("/internal/v1/documents/{documentId}/status", "post"),
    ],
    "payment": [
        ("/api/v1/payments", "get"),
        ("/api/v1/payments", "post"),
        ("/api/v1/payments/{paymentId}", "get"),
        ("/api/v1/payments/{paymentId}/submit", "post"),
        ("/api/v1/payments/{paymentId}/authorize", "post"),
        ("/api/v1/payments/{paymentId}/approve", "post"),
        ("/api/v1/payments/{paymentId}/issue", "post"),
        ("/api/v1/payments/{paymentId}/status", "patch"),
        ("/internal/v1/payments", "get"),
        ("/internal/v1/payments", "post"),
        ("/internal/v1/payments/{paymentId}", "get"),
        ("/internal/v1/payments/{paymentId}/status", "patch"),
    ],
    "notifications": [
        ("/api/v1/notifications", "get"),
        ("/api/v1/notifications", "post"),
        ("/api/v1/notifications/{notificationId}", "get"),
        ("/api/v1/notifications/{notificationId}/send", "post"),
        ("/internal/v1/notifications", "get"),
        ("/internal/v1/notifications", "post"),
        ("/internal/v1/notifications/{notificationId}", "get"),
        ("/internal/v1/notifications/{notificationId}/send", "post"),
    ],
}

# Round 5 second-slice routes. They are listed separately so the table above
# keeps its Round 2 meaning; every entry is still checked as mandatory.
ROUND5_OPENAPI_PATHS = {
    "policy": [
        ("/api/v1/policies/{policyId}/versions", "get"),
        ("/api/v1/policies/{policyId}/versions/current", "get"),
        ("/api/v1/policies/{policyId}/versions/{versionId}", "get"),
        ("/api/v1/policies/{policyId}/coverages", "get"),
        ("/api/v1/policies/{policyId}/coverages", "post"),
        ("/api/v1/policies/{policyId}/limits", "get"),
        ("/api/v1/policies/{policyId}/aggregate-state", "get"),
        ("/api/v1/policies/{policyId}/erosion", "post"),
        ("/api/v1/policies/{policyId}/endorsements", "get"),
        ("/api/v1/policies/{policyId}/endorsements", "post"),
        ("/api/v1/policies/{policyId}/endorsements/{endorsementId}", "get"),
        ("/api/v1/policies/{policyId}/insureds", "get"),
        ("/api/v1/policies/{policyId}/insureds", "post"),
        ("/api/v1/policies/{policyId}/locations", "get"),
        ("/api/v1/policies/{policyId}/locations", "post"),
        ("/api/v1/policies/{policyId}/cancellations", "get"),
        ("/api/v1/policies/{policyId}/cancel", "post"),
        ("/api/v1/policies/{policyId}/reinstatements", "get"),
        ("/api/v1/policies/{policyId}/reinstate", "post"),
        ("/internal/v1/policies/{policyId}/versions/current", "get"),
        ("/internal/v1/policies/{policyId}/coverages", "post"),
        ("/internal/v1/policies/{policyId}/erosion", "post"),
        ("/internal/v1/policies/{policyId}/endorsements", "post"),
        ("/internal/v1/policies/{policyId}/insureds", "post"),
        ("/internal/v1/policies/{policyId}/locations", "post"),
        ("/internal/v1/policies/{policyId}/cancel", "post"),
        ("/internal/v1/policies/{policyId}/reinstate", "post"),
    ],
    "contract": [
        ("/api/v1/contracts/{contractId}/layers", "get"),
        ("/api/v1/contracts/{contractId}/layers", "post"),
        ("/api/v1/contracts/{contractId}/layers/summary", "get"),
        ("/api/v1/contracts/{contractId}/participants", "get"),
        ("/api/v1/contracts/{contractId}/participants", "post"),
        ("/api/v1/contracts/{contractId}/terms", "get"),
        ("/api/v1/contracts/{contractId}/terms", "post"),
        ("/api/v1/contracts/{contractId}/terms/requirements", "get"),
        ("/api/v1/contracts/{contractId}/security", "get"),
        ("/api/v1/contracts/{contractId}/security", "post"),
        ("/api/v1/contracts/{contractId}/cessions", "get"),
        ("/api/v1/contracts/{contractId}/cessions", "post"),
        ("/api/v1/contracts/{contractId}/bordereaux", "get"),
        ("/api/v1/contracts/{contractId}/bordereaux", "post"),
        ("/api/v1/contracts/{contractId}/bordereaux/{bordereauId}/status", "patch"),
        ("/api/v1/contracts/{contractId}/commutations", "get"),
        ("/api/v1/contracts/{contractId}/commutations", "post"),
        ("/api/v1/contracts/{contractId}/commutations/{commutationId}/approve", "post"),
        ("/api/v1/contracts/{contractId}/commutations/{commutationId}/execute", "post"),
        ("/api/v1/contracts/{contractId}/bind-eligibility", "get"),
        ("/api/v1/contracts/{contractId}/bind", "post"),
        ("/internal/v1/contracts/{contractId}/layers", "post"),
        ("/internal/v1/contracts/{contractId}/participants", "post"),
        ("/internal/v1/contracts/{contractId}/terms/requirements", "get"),
        ("/internal/v1/contracts/{contractId}/security", "post"),
        ("/internal/v1/contracts/{contractId}/cessions", "post"),
        ("/internal/v1/contracts/{contractId}/bordereaux/{bordereauId}", "get"),
        ("/internal/v1/contracts/{contractId}/commutations/{commutationId}/execute", "post"),
        ("/internal/v1/contracts/{contractId}/bind-eligibility", "get"),
        ("/internal/v1/contracts/{contractId}/bind", "post"),
    ],
    "direct-claims": [
        ("/api/v1/claims/{claimId}/close", "post"),
        ("/api/v1/claims/{claimId}/injuries", "get"),
        ("/api/v1/claims/{claimId}/injuries", "post"),
        ("/api/v1/claims/{claimId}/injuries/{injuryId}", "patch"),
        ("/api/v1/claims/{claimId}/exposures", "get"),
        ("/api/v1/claims/{claimId}/exposures", "post"),
        ("/api/v1/claims/{claimId}/exposures/{exposureId}", "patch"),
        ("/api/v1/claims/{claimId}/reserves", "get"),
        ("/api/v1/claims/{claimId}/reserves", "post"),
        ("/api/v1/claims/{claimId}/coverage", "get"),
        ("/api/v1/claims/{claimId}/coverage", "post"),
        ("/api/v1/claims/{claimId}/litigation", "get"),
        ("/api/v1/claims/{claimId}/litigation", "post"),
        ("/api/v1/claims/{claimId}/litigation/{litigationId}", "patch"),
        ("/api/v1/claims/{claimId}/settlements", "get"),
        ("/api/v1/claims/{claimId}/settlements", "post"),
        ("/api/v1/claims/{claimId}/settlements/{settlementId}/approve", "post"),
        ("/api/v1/claims/{claimId}/settlements/{settlementId}/execute", "post"),
        ("/api/v1/claims/{claimId}/settlements/{settlementId}/payment", "patch"),
        ("/api/v1/claims/{claimId}/recoveries", "get"),
        ("/api/v1/claims/{claimId}/recoveries", "post"),
        ("/api/v1/claims/{claimId}/recoveries/{recoveryId}", "patch"),
        ("/api/v1/claims/{claimId}/liens", "get"),
        ("/api/v1/claims/{claimId}/liens", "post"),
        ("/api/v1/claims/{claimId}/liens/{lienId}", "patch"),
        ("/api/v1/claims/{claimId}/tasks", "get"),
        ("/api/v1/claims/{claimId}/tasks", "post"),
        ("/api/v1/claims/{claimId}/tasks/{taskId}", "patch"),
        ("/api/v1/claims/{claimId}/notes", "get"),
        ("/api/v1/claims/{claimId}/notes", "post"),
        ("/internal/v1/claims/{claimId}/close", "post"),
        ("/internal/v1/claims/{claimId}/injuries", "post"),
        ("/internal/v1/claims/{claimId}/exposures", "post"),
        ("/internal/v1/claims/{claimId}/reserves", "get"),
        ("/internal/v1/claims/{claimId}/coverage", "post"),
        ("/internal/v1/claims/{claimId}/litigation", "post"),
        ("/internal/v1/claims/{claimId}/settlements/{settlementId}/execute", "post"),
        ("/internal/v1/claims/{claimId}/settlements/{settlementId}/payment", "patch"),
        ("/internal/v1/claims/{claimId}/recoveries", "post"),
        ("/internal/v1/claims/{claimId}/liens", "post"),
        ("/internal/v1/claims/{claimId}/tasks", "get"),
        ("/internal/v1/claims/{claimId}/tasks", "post"),
        ("/internal/v1/claims/{claimId}/tasks/{taskId}", "patch"),
        ("/internal/v1/claims/{claimId}/notes", "get"),
        ("/internal/v1/claims/{claimId}/notes", "post"),
    ],
    "assumed-claims": [
        ("/api/v1/assumed-claims/{assumedClaimId}/close", "post"),
        ("/api/v1/assumed-claims/{assumedClaimId}/financials", "get"),
        ("/api/v1/assumed-claims/{assumedClaimId}/audit", "get"),
        ("/api/v1/assumed-claims/{assumedClaimId}/advices", "get"),
        ("/api/v1/assumed-claims/{assumedClaimId}/advices", "post"),
        ("/api/v1/assumed-claims/{assumedClaimId}/advices/{adviceId}/accept", "post"),
        ("/api/v1/assumed-claims/{assumedClaimId}/bordereaux", "get"),
        ("/api/v1/assumed-claims/{assumedClaimId}/bordereaux", "post"),
        ("/api/v1/assumed-claims/{assumedClaimId}/reserves", "get"),
        ("/api/v1/assumed-claims/{assumedClaimId}/reserves", "post"),
        ("/api/v1/assumed-claims/{assumedClaimId}/cash-calls", "get"),
        ("/api/v1/assumed-claims/{assumedClaimId}/cash-calls", "post"),
        ("/api/v1/assumed-claims/{assumedClaimId}/recoveries", "get"),
        ("/api/v1/assumed-claims/{assumedClaimId}/recoveries", "post"),
        ("/api/v1/assumed-claims/{assumedClaimId}/commutation", "get"),
        ("/api/v1/assumed-claims/{assumedClaimId}/commute", "post"),
        ("/api/v1/assumed-claims/{assumedClaimId}/disputes", "get"),
        ("/api/v1/assumed-claims/{assumedClaimId}/disputes", "post"),
        ("/api/v1/assumed-claims/{assumedClaimId}/disputes/{disputeId}/resolve", "post"),
        ("/api/v1/assumed-claims/claims/{claimId}/tasks", "get"),
        ("/api/v1/assumed-claims/claims/{claimId}/tasks", "post"),
        ("/api/v1/assumed-claims/claims/{claimId}/tasks/{taskId}", "patch"),
        ("/api/v1/assumed-claims/claims/{claimId}/notes", "get"),
        ("/api/v1/assumed-claims/claims/{claimId}/notes", "post"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/close", "post"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/financials", "get"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/audit", "get"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/advices", "post"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/advices/{adviceId}/accept", "post"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/bordereaux", "post"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/reserves", "post"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/cash-calls", "post"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/recoveries", "post"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/commutation", "get"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/commute", "post"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/disputes", "post"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/disputes/{disputeId}/resolve", "post"),
    ],
}

# Response codes the Round 5 contract relies on, keyed by vertical. Each tuple
# is (path, method, required response codes).
ROUND5_REQUIRED_RESPONSES = {
    "policy": [
        ("/api/v1/policies/{policyId}/coverages", "post", ("201", "422", "409")),
        ("/api/v1/policies/{policyId}/endorsements", "post", ("201", "422", "428")),
        ("/api/v1/policies/{policyId}/cancel", "post", ("201", "422", "428")),
        ("/api/v1/policies/{policyId}/reinstate", "post", ("201", "422", "428")),
        ("/api/v1/policies/{policyId}/erosion", "post", ("201", "422")),
    ],
    "contract": [
        ("/api/v1/contracts/{contractId}/bind", "post", ("200", "409")),
        ("/api/v1/contracts/{contractId}/status", "patch", ("200", "409")),
    ],
    "direct-claims": [
        ("/api/v1/claims/{claimId}/close", "post", ("200", "409")),
    ],
    "assumed-claims": [
        ("/api/v1/assumed-claims/{assumedClaimId}/cash-calls", "post", ("201", "422", "428")),
        ("/api/v1/assumed-claims/{assumedClaimId}/commute", "post", ("201", "422", "428")),
        ("/api/v1/assumed-claims/{assumedClaimId}/close", "post", ("200", "422")),
    ],
}


# Global-search routes added by the 2026-10-20 contract. Each tuple is
# (path, required book-header component or None, SearchItem.type value). Every
# entry is mandatory; the operation must use the shared SearchResponse schema.
SEARCH_OPENAPI_PATHS = {
    "party": ("/api/v1/parties/search", None, "PARTY"),
    "policy": ("/api/v1/policies/search", "BookHeaderDirect", "POLICY"),
    "contract": ("/api/v1/contracts/search", "BookHeaderAssumed", "CONTRACT"),
    "direct-claims": ("/api/v1/claims/search", "BookHeaderDirect", "DIRECT_CLAIM"),
    "assumed-claims": ("/api/v1/assumed-claims/search", "BookHeaderAssumed", "ASSUMED_CLAIM"),
    "cession": ("/api/v1/cessions/search", "BookHeaderDirect", "CESSION"),
    "retrocession": ("/api/v1/retrocessions/search", "BookHeaderAssumed", "RETROCESSION"),
    "document": ("/api/v1/documents/search", None, "DOCUMENT"),
    "payment": ("/api/v1/payments/search", None, "PAYMENT"),
    "notifications": ("/api/v1/notifications/search", None, "NOTIFICATION"),
}

SEARCH_RESPONSE_KEYS = ("query", "limit", "items")
SEARCH_ITEM_KEYS = ("id", "type", "label", "secondary", "status", "href")


# Contract technical accounts. Each tuple is
# (method, path, success status, success schema, request schema or None). All
# three public operations must document the tenant header, the ASSUMED book
# header, the path parameters, and the 400/404 problem responses; the two
# mutations also document 409.
CONTRACT_TECHNICAL_ACCOUNT_PATHS = [
    (
        "get",
        "/api/v1/contracts/{contractId}/technical-accounts",
        "200",
        "TechnicalAccount",
        None,
    ),
    (
        "post",
        "/api/v1/contracts/{contractId}/technical-accounts",
        "201",
        "TechnicalAccount",
        "CreateTechnicalAccountRequest",
    ),
    (
        "patch",
        "/api/v1/contracts/{contractId}/technical-accounts/{accountId}/status",
        "200",
        "TechnicalAccount",
        "UpdateTechnicalAccountStatusRequest",
    ),
]

CONTRACT_TECHNICAL_ACCOUNT_FIELDS = (
    "accountId",
    "accountNumber",
    "contractId",
    "periodStart",
    "periodEnd",
    "currency",
    "cededPremium",
    "cededLosses",
    "commission",
    "otherCharges",
    "balance",
    "status",
    "settlementReference",
    "createdAt",
)

CONTRACT_TECHNICAL_ACCOUNT_MONEY_FIELDS = (
    "cededPremium",
    "cededLosses",
    "commission",
    "otherCharges",
    "balance",
)

CONTRACT_TECHNICAL_ACCOUNT_CREATE_FIELDS = (
    "periodStart",
    "periodEnd",
    "currency",
    "cededPremium",
    "cededLosses",
    "commission",
    "otherCharges",
)

CONTRACT_TECHNICAL_ACCOUNT_STATUSES = ("DRAFT", "ISSUED", "SETTLED")
CONTRACT_TECHNICAL_ACCOUNT_REQUEST_STATUSES = ("ISSUED", "SETTLED")
CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_MAX_LENGTH = 120
CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_FIELD = "settlementReference"
CONTRACT_TECHNICAL_ACCOUNT_STATUS_REFERENCE_FIELD = "reference"
CONTRACT_TECHNICAL_ACCOUNT_INVALID_REFERENCE = "INVALID_REFERENCE"
CONTRACT_TECHNICAL_ACCOUNT_EVENTS = (
    "contract.technical-account.created",
    "contract.technical-account.issued",
    "contract.technical-account.settled",
)
CONTRACT_TECHNICAL_ACCOUNT_EVENT_FIELDS = (
    "contractId",
    "accountId",
    "accountNumber",
    "periodStart",
    "periodEnd",
    "currency",
    "balance",
    "status",
)
CONTRACT_TECHNICAL_ACCOUNT_EVENT_MESSAGE = "ContractTechnicalAccountData"
CONTRACT_TECHNICAL_ACCOUNT_EVENT_IMPLEMENTED_BY = "ContractEvents.java"

# Contract technical-account lines (SPEC 11.3.4 technical_account_line). Each
# tuple is (method, path, success status, success schema, request schema or
# None). The collection GET/POST and the item DELETE are mandatory; all three
# operations document the tenant and ASSUMED book headers, the contract and
# account path parameters, and 400/404, with 409 on both mutations. The line is
# editable only in DRAFT (ACCOUNT_NOT_EDITABLE) and issue-time reconciliation
# is documented on the account status PATCH.
CONTRACT_TECHNICAL_ACCOUNT_LINE_PATHS = [
    (
        "get",
        "/api/v1/contracts/{contractId}/technical-accounts/{accountId}/lines",
        "200",
        "LineSummary",
        None,
    ),
    (
        "post",
        "/api/v1/contracts/{contractId}/technical-accounts/{accountId}/lines",
        "201",
        "TechnicalAccountLine",
        "CreateTechnicalAccountLineRequest",
    ),
    (
        "delete",
        "/api/v1/contracts/{contractId}/technical-accounts/{accountId}/lines/{lineId}",
        "204",
        None,
        None,
    ),
]

CONTRACT_TECHNICAL_ACCOUNT_LINE_FIELDS = (
    "lineId",
    "accountId",
    "lineType",
    "reference",
    "description",
    "amount",
    "createdAt",
)

CONTRACT_TECHNICAL_ACCOUNT_LINE_TYPES = (
    "PREMIUM",
    "COMMISSION",
    "BROKERAGE",
    "PAID_LOSS",
    "OUTSTANDING_LOSS",
    "IBNR",
    "ALAE",
    "REINSTATEMENT",
    "CASH_CALL",
    "FUNDS_WITHHELD",
    "TAX",
    "ADJUSTMENT",
    "OTHER",
)
# The first slice's aggregate loss type. It is still understood when reading an
# older expert projection but is rejected on create and must not be enumerated.
CONTRACT_TECHNICAL_ACCOUNT_LINE_RETIRED_TYPES = ("LOSS",)
CONTRACT_TECHNICAL_ACCOUNT_LINE_SUMMARY_FIELDS = ("items", "totals")
CONTRACT_TECHNICAL_ACCOUNT_LINE_TOTAL_FIELDS = (
    "premium",
    "loss",
    "commission",
    "other",
)
# Detail line type -> the single reconciliation bucket it rolls into. The
# buckets are also the four header components; the coverage check below proves
# every one of the 13 types is mapped exactly once.
CONTRACT_TECHNICAL_ACCOUNT_LINE_BUCKET_TYPES = {
    "premium": ("PREMIUM",),
    "loss": (
        "PAID_LOSS",
        "OUTSTANDING_LOSS",
        "IBNR",
        "ALAE",
        "REINSTATEMENT",
        "CASH_CALL",
    ),
    "commission": ("COMMISSION", "BROKERAGE"),
    "other": ("FUNDS_WITHHELD", "TAX", "ADJUSTMENT", "OTHER"),
}
CONTRACT_TECHNICAL_ACCOUNT_LINE_BUCKET_HEADER_FIELDS = {
    "premium": "cededPremium",
    "loss": "cededLosses",
    "commission": "commission",
    "other": "otherCharges",
}
CONTRACT_TECHNICAL_ACCOUNT_LINE_REFERENCE_MAX_LENGTH = 64
CONTRACT_TECHNICAL_ACCOUNT_LINE_DESCRIPTION_MAX_LENGTH = 255
CONTRACT_TECHNICAL_ACCOUNT_LINE_NOT_EDITABLE = "ACCOUNT_NOT_EDITABLE"
CONTRACT_TECHNICAL_ACCOUNT_LINE_RECONCILE = "ACCOUNT_LINES_DO_NOT_RECONCILE"
CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENTS = (
    "contract.technical-account.line-added",
    "contract.technical-account.line-removed",
)
CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_FIELDS = (
    "contractId",
    "accountId",
    "lineId",
    "lineType",
    "amount",
)
CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_MESSAGE = "ContractTechnicalAccountLineData"
CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_IMPLEMENTED_BY = "ContractEvents.java"


# Contract period bordereaux. Each tuple is
# (method, path, success status, success schema, request schema or None). All
# three public operations must document the tenant header, the ASSUMED book
# header, the path parameters, and the 400/404 problem responses; the two
# mutations also document 409.
CONTRACT_BORDEREAU_PATHS = [
    (
        "get",
        "/api/v1/contracts/{contractId}/bordereaux",
        "200",
        "Bordereau",
        None,
    ),
    (
        "post",
        "/api/v1/contracts/{contractId}/bordereaux",
        "201",
        "Bordereau",
        "CreateBordereauRequest",
    ),
    (
        "patch",
        "/api/v1/contracts/{contractId}/bordereaux/{bordereauId}/status",
        "200",
        "Bordereau",
        "UpdateBordereauStatusRequest",
    ),
]

CONTRACT_BORDEREAU_FIELDS = (
    "bordereauId",
    "bordereauNumber",
    "contractId",
    "periodStart",
    "periodEnd",
    "receivedDate",
    "currency",
    "premiumAmount",
    "lossAmount",
    "commissionAmount",
    "otherChargesAmount",
    "lineCount",
    "notes",
    "status",
    "technicalAccountId",
    "createdAt",
)

CONTRACT_BORDEREAU_MONEY_FIELDS = (
    "premiumAmount",
    "lossAmount",
    "commissionAmount",
    "otherChargesAmount",
)

CONTRACT_BORDEREAU_CREATE_FIELDS = (
    "periodStart",
    "periodEnd",
    "receivedDate",
    "currency",
    "premiumAmount",
    "lossAmount",
    "commissionAmount",
    "otherChargesAmount",
    "lineCount",
)

CONTRACT_BORDEREAU_STATUSES = ("RECEIVED", "PROCESSED", "FAILED")
CONTRACT_BORDEREAU_REQUEST_STATUSES = ("PROCESSED", "FAILED")
CONTRACT_BORDEREAU_NOTES_MAX_LENGTH = 4000


# Contract cash calls. Each tuple is
# (method, path, success status, success schema, request schema or None). All
# three public operations must document the tenant header, the ASSUMED book
# header, the path parameters, and the 400/404 problem responses; the two
# mutations also document 409.
CONTRACT_CASH_CALL_PATHS = [
    (
        "get",
        "/api/v1/contracts/{contractId}/cash-calls",
        "200",
        "CashCall",
        None,
    ),
    (
        "post",
        "/api/v1/contracts/{contractId}/cash-calls",
        "201",
        "CashCall",
        "CreateCashCallRequest",
    ),
    (
        "patch",
        "/api/v1/contracts/{contractId}/cash-calls/{cashCallId}/status",
        "200",
        "CashCall",
        "UpdateCashCallStatusRequest",
    ),
]

CONTRACT_CASH_CALL_FIELDS = (
    "cashCallId",
    "callNumber",
    "contractId",
    "periodStart",
    "periodEnd",
    "amount",
    "currency",
    "dueDate",
    "status",
    "settlementReference",
    "notes",
    "createdAt",
)

CONTRACT_CASH_CALL_CREATE_FIELDS = (
    "periodStart",
    "periodEnd",
    "amount",
    "currency",
    "dueDate",
)

CONTRACT_CASH_CALL_STATUSES = ("REQUESTED", "ISSUED", "SETTLED", "CANCELLED")
CONTRACT_CASH_CALL_REQUEST_STATUSES = ("ISSUED", "SETTLED", "CANCELLED")
CONTRACT_CASH_CALL_NOTES_MAX_LENGTH = 4000
CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_MAX_LENGTH = 120
CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_FIELD = "settlementReference"
CONTRACT_CASH_CALL_STATUS_REFERENCE_FIELD = "reference"
CONTRACT_CASH_CALL_INVALID_REFERENCE = "INVALID_REFERENCE"
CONTRACT_CASH_CALL_EVENTS = (
    "contract.cash-call.requested",
    "contract.cash-call.issued",
    "contract.cash-call.settled",
    "contract.cash-call.cancelled",
)
CONTRACT_CASH_CALL_EVENT_FIELDS = (
    "contractId",
    "cashCallId",
    "callNumber",
    "periodStart",
    "periodEnd",
    "amount",
    "currency",
    "dueDate",
    "status",
)


# Contract security/collateral. The public domain and expert expose the same
# path; the public projection is the ten-field SecurityRecord, the create body
# is CreateContractSecurityRequest, and the internal expert keeps the wider
# Security row and CreateSecurityRequest body. The public create derives ACTIVE
# or EXPIRED and never accepts a caller status; the list can also return the
# internal bind-slice statuses (OUTSTANDING and the rest), which is why the
# response enum carries the full database vocabulary.
CONTRACT_SECURITY_PATHS = [
    (
        "get",
        "/api/v1/contracts/{contractId}/security",
        "200",
        "SecurityRecord",
        None,
    ),
    (
        "post",
        "/api/v1/contracts/{contractId}/security",
        "201",
        "SecurityRecord",
        "CreateContractSecurityRequest",
    ),
]

CONTRACT_SECURITY_FIELDS = (
    "id",
    "securityType",
    "requiredAmount",
    "heldAmount",
    "currency",
    "providerPartyId",
    "expiryDate",
    "approvalRef",
    "status",
    "createdAt",
)

CONTRACT_SECURITY_CREATE_REQUIRED = ("securityType", "requiredAmount", "currency")
CONTRACT_SECURITY_CREATE_OPTIONAL = (
    "heldAmount",
    "providerPartyId",
    "expiryDate",
    "approvalRef",
    "approvedAt",
)
CONTRACT_SECURITY_STATUSES = (
    "ACTIVE",
    "REQUIRED",
    "OUTSTANDING",
    "PARTIAL",
    "RELEASED",
    "EXPIRED",
    "BREACH",
)
CONTRACT_SECURITY_TYPES = (
    "LETTER_OF_CREDIT",
    "TRUST_FUND",
    "FUNDS_WITHHELD",
    "CASH_ADVANCE",
    "PARENT_GUARANTEE",
    "BANK_GUARANTEE",
    "SECURITIES",
)
CONTRACT_SECURITY_CONFLICT_CODES = (
    "COLLATERAL_EXCEEDS_OBLIGATION",
    "COLLATERAL_APPROVAL_INCOMPLETE",
    "SECURITY_CURRENCY_MISMATCH",
    "CONTRACT_LOCKED",
)
CONTRACT_SECURITY_EVENT = "contract.security.recorded"
CONTRACT_SECURITY_EVENT_FIELDS = (
    "contractId",
    "securityId",
    "securityType",
    "requiredAmount",
    "heldAmount",
    "currency",
    "status",
)

# Contract security status action. One PATCH on the public security path moves
# a live record to RELEASED or EXPIRED and an EXPIRED record to RELEASED;
# RELEASED is terminal and BREACH cannot be moved. The request only accepts the
# two terminal outcomes, and the implementation writes
# contract.security.status-changed in the same transaction as the row update.
CONTRACT_SECURITY_STATUS_PATH = (
    "/api/v1/contracts/{contractId}/security/{securityId}/status"
)
CONTRACT_SECURITY_STATUS_REQUEST = "UpdateContractSecurityStatusRequest"
CONTRACT_SECURITY_STATUS_REQUEST_STATUSES = ("RELEASED", "EXPIRED")
CONTRACT_SECURITY_STATUS_PREVIOUS = (
    "ACTIVE",
    "OUTSTANDING",
    "PARTIAL",
    "REQUIRED",
    "EXPIRED",
)
CONTRACT_SECURITY_STATUS_CODES = ("INVALID_STATUS", "INVALID_STATUS_TRANSITION")
CONTRACT_SECURITY_STATUS_EVENT = "contract.security.status-changed"
CONTRACT_SECURITY_STATUS_EVENT_FIELDS = (
    "contractId",
    "securityId",
    "securityType",
    "previousStatus",
    "status",
)


# Direct Claims and Assumed Claims task and note schemas. The public projection
# and command shapes are the ones the domains serialize, so the names are
# mandatory alongside the five public routes above.
TASK_NOTE_REQUIRED_SCHEMAS = {
    "direct-claims": [
        "Task",
        "TaskCreate",
        "TaskStatusChange",
        "Note",
        "NoteCreate",
    ],
    "assumed-claims": [
        "Task",
        "TaskCreate",
        "TaskStatusChange",
        "Note",
        "NoteCreate",
    ],
}


# Idempotent task and note creation. Every listed operation must declare the
# shared 1-64 character header parameter, a 201 response with the
# `Idempotent-Replay` header, and the vertical's 409 idempotency-reuse code.
# Each tuple is (path, method). The value is (409 code, operations).
TASK_NOTE_IDEMPOTENCY_POSTS = {
    "direct-claims": (
        "EIA-DIR-4091",
        [
            ("/api/v1/claims/{claimId}/tasks", "post"),
            ("/api/v1/claims/{claimId}/notes", "post"),
            ("/internal/v1/claims/{claimId}/tasks", "post"),
            ("/internal/v1/claims/{claimId}/notes", "post"),
        ],
    ),
    "assumed-claims": (
        "EIA-RNS-4091",
        [
            ("/api/v1/assumed-claims/claims/{claimId}/tasks", "post"),
            ("/api/v1/assumed-claims/claims/{claimId}/notes", "post"),
        ],
    ),
}


# Claim assignment. Each tuple is
# (path, method, claim schema name, book header component). The public and the
# internal expert routes are both mandatory because the domain calls the expert
# alias. Every operation must document the tenant and book headers, the optional
# shared ActorHeader, an AssignClaimRequest body, the updated claim on 200, and
# a problem+json 400/404/409.
ASSIGNMENT_OPENAPI_PATHS = {
    "direct-claims": [
        ("/api/v1/claims/{claimId}/assignment", "patch", "Claim", "BookHeaderDirect"),
        ("/internal/v1/claims/{claimId}/assignment", "patch", "Claim", "BookHeaderDirect"),
    ],
    "assumed-claims": [
        (
            "/api/v1/assumed-claims/claims/{claimId}/assignment",
            "patch",
            "AssumedClaim",
            "BookHeaderAssumed",
        ),
        (
            "/internal/v1/assumed-claims/{claimId}/assignment",
            "patch",
            "AssumedClaim",
            "BookHeaderAssumed",
        ),
    ],
}

ASSIGNMENT_REQUIRED_SCHEMAS = {
    "direct-claims": "Claim",
    "assumed-claims": "AssumedClaim",
}

# Field -> maxLength for the nullable assignment fields on the claim projection.
ASSIGNMENT_CLAIM_FIELDS = {
    "assignedAdjuster": 128,
    "assignedTeam": 64,
    "assignedAt": None,
}

ASSIGNMENT_MAX_ADJUSTER = 128
ASSIGNMENT_MAX_TEAM = 64


# Direct Claims policy-year allocations. Each tuple is
# (method, path, success status, success schema, request schema or None). The
# two public operations are mandatory. The expert shares the public path and
# also exposes an /internal/v1 alias that the domain calls; the domain remaps
# the expert's id/tenantId projection to the public allocationId, so the alias
# is deliberately not part of the public contract (README, Policy billing
# precedent).
ALLOCATION_OPENAPI_PATHS = [
    (
        "get",
        "/api/v1/claims/{claimId}/allocations",
        "200",
        "AllocationSummary",
        None,
    ),
    (
        "post",
        "/api/v1/claims/{claimId}/allocations",
        "201",
        "Allocation",
        "CreateClaimAllocationRequest",
    ),
]

ALLOCATION_PROJECTION_FIELDS = (
    "allocationId",
    "claimId",
    "policyId",
    "policyYear",
    "layer",
    "allocationPct",
    "allocatedAmount",
    "createdAt",
)

ALLOCATION_REQUEST_FIELDS = (
    "policyId",
    "policyYear",
    "layer",
    "allocationPct",
    "allocatedAmount",
)

ALLOCATION_MIN_POLICY_YEAR = 1900
ALLOCATION_MAX_POLICY_YEAR = 2200
ALLOCATION_MAX_LAYER = 32

# The public create also consumes the Policy mass tort coverage block. A year
# outside the block of a COMPLETE profile is a stable 400 code, alongside the
# expert POLICY_MISMATCH code and the generic VALIDATION_ERROR.
ALLOCATION_MASS_TORT_CODE = "MASS_TORT_YEAR_OUTSIDE_BLOCK"

# Allocation policy erosion. The projection carries the optional limit, the
# posting state, and the posting evidence. The public command is a bodyless
# orchestration retry that reposts the stored limit; the posted state is
# terminal and a retry that would change it is a conflict.
ALLOCATION_EROSION_PATH = (
    "/api/v1/claims/{claimId}/allocations/{allocationId}/erosion"
)
ALLOCATION_EROSION_PROJECTION_FIELDS = (
    "limitId",
    "erosionStatus",
    "erosionMessage",
    "erosionPostedAt",
)
ALLOCATION_EROSION_STATUSES = ("NOT_POSTED", "POSTED", "FAILED")
ALLOCATION_EROSION_MESSAGE_MAX_LENGTH = 4000
ALLOCATION_EROSION_CONFLICT_CODE = "CONFLICT"


# Direct Claims settlement payment link. The public and expert PATCH routes set
# or clear the Payment aggregate linked to a settlement. Only an AUTHORIZED or
# EXECUTED settlement is linkable; a PROPOSED or REJECTED settlement is 409
# SETTLEMENT_NOT_LINKABLE and nothing is written. A real link or unlink bumps
# the claim and settlement versions and emits
# direct.claim.settlement-payment-linked in the same transaction; repeating the
# current value is an idempotent no-op that writes no version and no event.
SETTLEMENT_PAYMENT_OPENAPI_PATHS = (
    (
        "/api/v1/claims/{claimId}/settlements/{settlementId}/payment",
        "linkClaimSettlementPayment",
    ),
    (
        "/internal/v1/claims/{claimId}/settlements/{settlementId}/payment",
        "expertLinkClaimSettlementPayment",
    ),
)
SETTLEMENT_PAYMENT_SCHEMA = "SettlementPaymentRequest"
SETTLEMENT_PAYMENT_EVENT = "direct.claim.settlement-payment-linked"
SETTLEMENT_PAYMENT_EVENT_FIELDS = (
    "claimId",
    "settlementId",
    "settlementNumber",
    "paymentId",
    "linkedAt",
)
SETTLEMENT_PAYMENT_LINKABLE_STATUSES = ("AUTHORIZED", "EXECUTED")
SETTLEMENT_PAYMENT_UNLINKABLE_STATUSES = ("PROPOSED", "REJECTED")
SETTLEMENT_PAYMENT_CONFLICT_CODE = "SETTLEMENT_NOT_LINKABLE"


# Policy billing (SPEC 11.2.13). The public domain routes proxy the expert's
# billing service; the expert's /internal/v1 alias is an implementation detail
# and is not part of the public contract. Every operation requires the tenant
# header and accepts an optional X-EIA-Book that must be DIRECT when present.
# Each tuple is (method, path, response schema, request schema or None).
BILLING_OPENAPI_PATHS = [
    ("get", "/api/v1/policies/{policyId}/billing", "BillingPlan", None),
    (
        "post",
        "/api/v1/policies/{policyId}/billing",
        "BillingPlan",
        "CreateBillingPlanRequest",
    ),
    (
        "patch",
        "/api/v1/policies/{policyId}/billing/installments/{installmentId}",
        "Installment",
        "UpdateInstallmentRequest",
    ),
    (
        "post",
        "/api/v1/policies/{policyId}/billing/adjustment",
        "BillingAdjustmentResult",
        "BillingAdjustmentRequest",
    ),
]

BILLING_PLAN_FIELDS = (
    "planId",
    "planNumber",
    "policyId",
    "totalPremium",
    "currency",
    "installmentCount",
    "frequency",
    "firstDueDate",
    "status",
    "installments",
    "summary",
)

BILLING_INSTALLMENT_FIELDS = (
    "installmentId",
    "installmentNumber",
    "dueDate",
    "amount",
    "creditedAmount",
    "outstandingAmount",
    "status",
    "paidAt",
    "paymentId",
)

BILLING_INSTALLMENT_REQUIRED_FIELDS = (
    "installmentId",
    "installmentNumber",
    "dueDate",
    "amount",
    "creditedAmount",
    "outstandingAmount",
    "status",
)

BILLING_INSTALLMENT_MONEY_FIELDS = (
    "amount",
    "creditedAmount",
    "outstandingAmount",
)

# The plan money summary returned with the billing read. `outstandingAmount`
# is net of the paid, waived, and credited portions (SPEC BIL-06).
BILLING_SUMMARY_FIELDS = (
    "totalAmount",
    "paidAmount",
    "waivedAmount",
    "creditedAmount",
    "outstandingAmount",
    "overdueAmount",
    "currency",
    "installmentCount",
)

BILLING_SUMMARY_MONEY_FIELDS = (
    "totalAmount",
    "paidAmount",
    "waivedAmount",
    "creditedAmount",
    "outstandingAmount",
    "overdueAmount",
)

BILLING_FREQUENCIES = ("MONTHLY", "QUARTERLY", "SEMI_ANNUAL", "ANNUAL")
BILLING_PLAN_STATUSES = ("ACTIVE", "COMPLETE", "CANCELLED")
BILLING_INSTALLMENT_STATUSES = ("DUE", "OVERDUE", "PAID", "WAIVED", "CREDITED")
BILLING_SETTLE_STATUSES = ("PAID", "WAIVED")
BILLING_MIN_INSTALLMENTS = 1
BILLING_MAX_INSTALLMENTS = 24

# The four billing event names implemented by the Policy expert. The plan
# name differs from the SPEC 11.2.13 `policy.billing.plan-created` spelling, the
# installment facts have no SPEC name, and the positive premium adjustment fact
# has no SPEC 11.2.13 name either; MISMATCHES.md M-22, M-27, and M-51 record the
# deviations.
POLICY_BILLING_EVENTS = (
    "policy.billing-plan.created",
    "policy.billing-plan.adjusted",
    "policy.installment.paid",
    "policy.installment.waived",
)

# Positive premium billing adjustment (SPEC 11.2.13). The amount is derived
# from the policy written premium less the plan's net premium, so a zero or
# negative remainder is a 400. The plan must exist, be ACTIVE, and be below the
# 24-installment ceiling. The domain accepts the optional If-Match and
# Idempotency-Key headers and forwards them, but the expert does not compare or
# replay them in this slice (M-06, M-07).
BILLING_ADJUSTMENT_PATH = "/api/v1/policies/{policyId}/billing/adjustment"
BILLING_ADJUSTMENT_REQUEST = "BillingAdjustmentRequest"
BILLING_ADJUSTMENT_RESULT = "BillingAdjustmentResult"
BILLING_ADJUSTMENT_REQUEST_FIELDS = ("dueDate", "reason")
BILLING_ADJUSTMENT_RESULT_FIELDS = (
    "plan",
    "installment",
    "adjustmentAmount",
    "newTotalPremium",
)
BILLING_ADJUSTMENT_REASON_MAX_LENGTH = 500
BILLING_ADJUSTMENT_EVENT = "policy.billing-plan.adjusted"
BILLING_ADJUSTMENT_EVENT_MESSAGE = "PolicyBillingPlanAdjustedData"
BILLING_ADJUSTMENT_EVENT_FIELDS = (
    "policyId",
    "policyNumber",
    "planId",
    "adjustmentAmount",
    "newTotalPremium",
    "installmentId",
    "installmentNumber",
    "dueDate",
    "reason",
)
BILLING_ADJUSTMENT_CODES = (
    "NO_PREMIUM_ADJUSTMENT",
    "BILLING_PLAN_NOT_FOUND",
    "BILLING_PLAN_NOT_ACTIVE",
    "MAX_INSTALLMENTS_REACHED",
    "CONCURRENT_MODIFICATION",
)


# Policy premium receivables (SPEC 11.2.13). The cross-policy queue is served by
# the domain over the expert's billing read and deliberately sits outside
# /api/v1/policies because it is not scoped to one policy. The expert's
# /internal/v1 alias is an implementation detail and is not part of the public
# contract. Each tuple is (method, path, response schema).
RECEIVABLE_OPENAPI_PATHS = [
    ("get", "/api/v1/billing/installments", "ReceivableSummary"),
]

RECEIVABLE_FIELDS = (
    "installmentId",
    "planId",
    "planNumber",
    "policyId",
    "policyNumber",
    "insuredPartyId",
    "installmentNumber",
    "dueDate",
    "amount",
    "creditedAmount",
    "outstandingAmount",
    "currency",
    "status",
    "daysPastDue",
    "paidAt",
    "paymentId",
)

# paidAt and paymentId are nullable and stay optional because the queue only
# returns unsettled installments; every other member is always present.
RECEIVABLE_REQUIRED_FIELDS = (
    "installmentId",
    "planId",
    "planNumber",
    "policyId",
    "policyNumber",
    "insuredPartyId",
    "installmentNumber",
    "dueDate",
    "amount",
    "creditedAmount",
    "outstandingAmount",
    "currency",
    "status",
    "daysPastDue",
)

RECEIVABLE_STATUSES = ("DUE", "OVERDUE")
RECEIVABLE_SUMMARY_FIELDS = ("items", "totalAmount", "overdueAmount", "count")
RECEIVABLE_DEFAULT_LIMIT = 20
RECEIVABLE_MIN_LIMIT = 1
RECEIVABLE_MAX_LIMIT = 200


# Policy installment dunning (SPEC 11.2.13 collections and dunning). The public
# surface is a per-installment history and command under /api/v1/billing. The
# canonical contract requires the DIRECT book; the domain accepts an absent
# header for compatibility, which MISMATCHES.md M-38 records. A dunning action
# is per escalation level: the unique (tenant, installment, level) constraint is
# the retry guard, and the level/channel vocabularies and statuses are closed.
DUNNING_PATH = "/api/v1/billing/installments/{installmentId}/dunning"
DUNNING_FIELDS = (
    "dunningId",
    "installmentId",
    "planId",
    "policyId",
    "level",
    "channel",
    "notes",
    "status",
    "sentAt",
)
DUNNING_REQUIRED_FIELDS = (
    "dunningId",
    "installmentId",
    "planId",
    "policyId",
    "level",
    "channel",
    "status",
    "sentAt",
)
DUNNING_REQUEST_FIELDS = ("level", "channel", "notes")
DUNNING_REQUEST_REQUIRED_FIELDS = ("level", "channel")
DUNNING_LEVELS = ("REMINDER", "FIRST_NOTICE", "SECOND_NOTICE", "COLLECTIONS")
DUNNING_CHANNELS = ("EMAIL", "LETTER", "PORTAL")
DUNNING_STATUSES = ("SENT", "CANCELLED")
DUNNING_NOTES_MAX_LENGTH = 2000
DUNNING_CONFLICT_CODES = ("INSTALLMENT_NOT_DUNNABLE", "DUNNING_ALREADY_SENT")
DUNNING_EVENT = "policy.dunning.sent"
DUNNING_EVENT_FIELDS = (
    "policyId",
    "policyNumber",
    "installmentId",
    "level",
    "channel",
    "sentAt",
    "status",
)


# Policy renewal (SPEC 11.2.4 renewal lineage, SPEC 11.2.10 renew). The public
# route creates a successor DRAFT term, leaves the source policy unchanged, and
# returns the successor with its own ETag. The request body carries the two term
# dates as required fields and premium/limit overrides as optional fields.
POLICY_RENEWAL_PATH = "/api/v1/policies/{policyId}/renew"
POLICY_RENEWAL_REQUIRED_FIELDS = ("effectiveDate", "expirationDate")
POLICY_RENEWAL_OPTIONAL_FIELDS = (
    "premiumAmount",
    "premiumCurrency",
    "limitAmount",
    "limitCurrency",
)
POLICY_RENEWAL_ALLOWED_STATUSES = ("ISSUED", "IN_FORCE", "ENDORSED", "REINSTATED")
POLICY_RENEWAL_EVENT = "policy.policy.renewed"


# Policy mass tort profile (SPEC 11.2.4 `policy_mass_tort_profile`, SPEC
# 11.2.11). The public domain exposes the short /api/v1/policies route; GET
# reads the one-per-policy profile and PUT is an upsert returning 201 on create
# and 200 on replace. Tenant is required and a supplied book must be DIRECT.
MASS_TORT_PROFILE_PATH = "/api/v1/policies/{policyId}/mass-tort-profile"
MASS_TORT_PROFILE_SCHEMAS = (
    "MassTortProfile",
    "UpdateMassTortProfileRequest",
    "MassTortTortType",
    "MassTortTriggerType",
    "MassTortAllocationMethod",
    "MassTortProfileStatus",
)
MASS_TORT_PROFILE_FIELDS = (
    "profileId",
    "policyId",
    "tortType",
    "triggerType",
    "allocationMethod",
    "allocationNotes",
    "coverageBlockStart",
    "coverageBlockEnd",
    "status",
    "updatedAt",
)
MASS_TORT_UPDATE_REQUIRED_FIELDS = (
    "tortType",
    "triggerType",
    "allocationMethod",
    "status",
)
MASS_TORT_UPDATE_OPTIONAL_FIELDS = (
    "allocationNotes",
    "coverageBlockStart",
    "coverageBlockEnd",
)
MASS_TORT_TORT_TYPES = (
    "ASBESTOS",
    "SILICA",
    "TALC",
    "PFAS",
    "OPIOIDS",
    "PRODUCT_LIABILITY",
    "ENVIRONMENTAL",
    "OTHER",
)
MASS_TORT_TRIGGER_TYPES = ("EXPOSURE", "MANIFESTATION", "INJURY", "REVISIONIST")
MASS_TORT_ALLOCATION_METHODS = (
    "ALL_SUMS",
    "PRO_RATA_TIME_ON_RISK",
    "PRO_RATA_PREMIUM",
    "EQUAL_SHARES",
    "STACKED_LIMITS",
    "CUSTOM_MATRIX",
)
MASS_TORT_PROFILE_STATUSES = ("DRAFT", "COMPLETE")
MASS_TORT_NOTES_MAX_LENGTH = 2000
MASS_TORT_EVENT = "policy.mass-tort-profile.updated"
MASS_TORT_EVENT_FIELDS = (
    "policyId",
    "policyNumber",
    "status",
    "tortType",
    "triggerType",
    "allocationMethod",
    "coverageBlockStart",
    "coverageBlockEnd",
)


# Policy commercial programs (SPEC 10.11.3 `program`, SPEC 11.2.16). The public
# domain exposes the short /api/v1/programs catalog and the policy membership
# command; the expert serves the same public paths plus an /internal/v1 alias
# that the domain calls and that stays an implementation detail. Every operation
# requires the tenant and the DIRECT book. Each tuple is
# (method, path, success status, success schema, request schema or None,
# required error response codes).
POLICY_PROGRAM_OPENAPI_PATHS = [
    ("get", "/api/v1/programs", "200", "Program", None, ("400", "404")),
    (
        "post",
        "/api/v1/programs",
        "201",
        "Program",
        "CreateProgramRequest",
        ("400", "404"),
    ),
    (
        "get",
        "/api/v1/programs/{programId}",
        "200",
        "Program",
        None,
        ("400", "404"),
    ),
    (
        "patch",
        "/api/v1/policies/{policyId}/program",
        "200",
        "Policy",
        "UpdatePolicyProgramRequest",
        ("400", "404", "409"),
    ),
]

POLICY_PROGRAM_FIELDS = (
    "programId",
    "programNumber",
    "name",
    "programType",
    "effectiveFrom",
    "effectiveTo",
    "status",
    "capacityAmount",
    "capacityCurrency",
    "leadPolicyId",
    "createdAt",
    "usedAmount",
    "utilizationPct",
    "policyCount",
)

POLICY_PROGRAM_CREATE_REQUIRED_FIELDS = (
    "name",
    "programType",
    "effectiveFrom",
    "effectiveTo",
)

POLICY_PROGRAM_CREATE_OPTIONAL_FIELDS = ("leadPolicyId",)

POLICY_PROGRAM_TYPES = ("CAPTIVE", "POOL", "FRONTING", "COINSURANCE", "MASS_TORT")
POLICY_PROGRAM_STATUSES = ("ACTIVE", "CLOSED")
POLICY_PROGRAM_NAME_MAX_LENGTH = 200
POLICY_PROGRAM_NUMBER_MAX_LENGTH = 32
POLICY_PROGRAM_CAPACITY_CODE = "INVALID_PROGRAM_CAPACITY"
POLICY_PROGRAM_CAPACITY_PATTERN = (
    r"^(?!0(?:\.0{1,4})?$)(?:0|[1-9][0-9]{0,14})(?:\.[0-9]{1,4})?$"
)
POLICY_PROGRAM_USED_AMOUNT_PATTERN = (
    r"^(?:0|[1-9][0-9]{0,14})(?:\.[0-9]{1,4})?$"
)
POLICY_PROGRAM_UTILIZATION_PATTERN = r"^[0-9]{1,21}\.[0-9]{2}$"
POLICY_PROGRAM_CURRENCY_PATTERN = "^[A-Z]{3}$"
POLICY_PROGRAM_CAPACITY_DEPENDENCIES = {
    "capacityAmount": ["capacityCurrency"],
    "capacityCurrency": ["capacityAmount"],
}
POLICY_PROGRAM_CREATED_FIELDS = (
    "programId",
    "programNumber",
    "name",
    "programType",
    "effectiveFrom",
    "effectiveTo",
    "status",
    "leadPolicyId",
    "createdAt",
)
POLICY_PROGRAM_ASSIGNED_FIELDS = (
    "policyId",
    "policyNumber",
    "status",
    "version",
    "effectiveDate",
    "expirationDate",
    "premiumAmount",
    "premiumCurrency",
    "limitAmount",
    "limitCurrency",
    "programId",
    "previousProgramId",
    "changedFields",
)


# Policy credit notes (SPEC 11.2.13 billing adjustments). The public domain
# exposes the short /api/v1/policies/{policyId}/credit-notes resource; the
# expert's /internal/v1 alias is an implementation detail. Every operation
# requires the tenant header and the canonical DIRECT book. A note is created
# DRAFT and advances once through DRAFT -> ISSUED -> APPLIED, with CANCELLED
# reachable from DRAFT or ISSUED. APPLIED and CANCELLED are terminal. Creation
# bumps the policy version and writes policy.credit-note.created in the same
# transaction; each accepted transition writes one credit-note event. A create
# may name an ACTIVE cancellation of the same tenant and policy whose return
# premium the note refunds, and a cancellation funds at most one note.
POLICY_CREDIT_NOTE_PATHS = [
    (
        "get",
        "/api/v1/policies/{policyId}/credit-notes",
        "200",
        "CreditNote",
        None,
    ),
    (
        "post",
        "/api/v1/policies/{policyId}/credit-notes",
        "201",
        "CreditNote",
        "CreateCreditNoteRequest",
    ),
    (
        "patch",
        "/api/v1/policies/{policyId}/credit-notes/{creditNoteId}/status",
        "200",
        "CreditNote",
        "UpdateCreditNoteStatusRequest",
    ),
]

POLICY_CREDIT_NOTE_FIELDS = (
    "creditNoteId",
    "noteNumber",
    "policyId",
    "amount",
    "currency",
    "reason",
    "status",
    "issuedAt",
    "appliedAt",
    "appliedInstallmentId",
    "createdAt",
    "reversedAt",
    "reversalReason",
    "cancellationId",
    "cancellationNumber",
)

POLICY_CREDIT_NOTE_STATUSES = ("DRAFT", "ISSUED", "APPLIED", "CANCELLED", "REVERSED")
POLICY_CREDIT_NOTE_REQUEST_STATUSES = ("ISSUED", "APPLIED", "CANCELLED", "REVERSED")
POLICY_CREDIT_NOTE_EVENT_STATUSES = ("ISSUED", "APPLIED", "CANCELLED")
POLICY_CREDIT_NOTE_REASON_MAX_LENGTH = 500
POLICY_CREDIT_NOTE_CANCELLATION_NUMBER_MAX_LENGTH = 32
POLICY_CREDIT_NOTE_AMOUNT_PATTERN = (
    r"^(?!0(?:\.0{1,4})?$)(?:0|[1-9][0-9]{0,14})(?:\.[0-9]{1,4})?$"
)
POLICY_CREDIT_NOTE_EVENTS = (
    "policy.credit-note.created",
    "policy.credit-note.issued",
    "policy.credit-note.applied",
    "policy.credit-note.cancelled",
    "policy.credit-note.reversed",
)
# The created event is a dedicated DRAFT payload; the other four facts are
# transitions. The status command only ever writes the transition events.
POLICY_CREDIT_NOTE_TRANSITION_EVENTS = (
    "policy.credit-note.issued",
    "policy.credit-note.applied",
    "policy.credit-note.cancelled",
    "policy.credit-note.reversed",
)
POLICY_CREDIT_NOTE_EVENT_FIELDS = (
    "policyId",
    "policyNumber",
    "creditNoteId",
    "noteNumber",
    "amount",
    "currency",
    "status",
)
# The created payload adds the creation instant and the optional cancellation
# link; an unlinked billing adjustment omits both link members.
POLICY_CREDIT_NOTE_CREATED_EVENT_FIELDS = POLICY_CREDIT_NOTE_EVENT_FIELDS + (
    "createdAt",
)
POLICY_CREDIT_NOTE_LINK_FIELDS = ("cancellationId", "cancellationNumber")
# The applied event additionally names the credited installment and its
# cumulative credited amount; ISSUED and CANCELLED omit both members.
POLICY_CREDIT_NOTE_APPLIED_EVENT_FIELDS = ("installmentId", "creditedAmount")
POLICY_CREDIT_NOTE_EVENT_MESSAGE = "PolicyCreditNoteData"
POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE = "PolicyCreditNoteCreatedData"
# The reversal payload is a dedicated message: it has no policy identity members
# and names the released installment, the amount, the required reason, and the
# terminal status.
POLICY_CREDIT_NOTE_REVERSED_EVENT_FIELDS = (
    "creditNoteId",
    "noteNumber",
    "installmentId",
    "amount",
    "reason",
    "status",
)
POLICY_CREDIT_NOTE_REVERSED_EVENT_MESSAGE = "PolicyCreditNoteReversedData"
POLICY_CREDIT_NOTE_EVENT_IMPLEMENTED_BY = "PolicyEvents.java"


# Policy legal entity catalog and issuing-entity assignment. Each tuple is
# (method, path, success status, success schema, request schema or None,
# required error codes). The catalog list is a bare newest-first array; the
# create returns 201 with a Location, the detail 200, and the assignment 200
# with the updated Policy and the shared ETag. Every operation requires the
# tenant header and accepts the optional DIRECT book parameter. A duplicate code
# is 409 DUPLICATE_LEGAL_ENTITY_CODE and a concurrent policy change is 409
# CONCURRENT_MODIFICATION.
POLICY_LEGAL_ENTITY_OPENAPI_PATHS = [
    (
        "get",
        "/api/v1/legal-entities",
        "200",
        "LegalEntity",
        None,
        ("400", "404"),
    ),
    (
        "post",
        "/api/v1/legal-entities",
        "201",
        "LegalEntity",
        "CreateLegalEntityRequest",
        ("400", "404", "409"),
    ),
    (
        "get",
        "/api/v1/legal-entities/{legalEntityId}",
        "200",
        "LegalEntity",
        None,
        ("400", "404"),
    ),
    (
        "patch",
        "/api/v1/policies/{policyId}/legal-entity",
        "200",
        "Policy",
        "UpdatePolicyLegalEntityRequest",
        ("400", "404", "409"),
    ),
]

POLICY_LEGAL_ENTITY_FIELDS = (
    "legalEntityId",
    "code",
    "name",
    "entityType",
    "jurisdiction",
    "regulator",
    "licenseNumber",
    "status",
    "createdAt",
)

POLICY_LEGAL_ENTITY_NULLABLE_FIELDS = ("regulator", "licenseNumber")
POLICY_LEGAL_ENTITY_TYPES = ("INSURER", "MGA", "CAPTIVE", "POOL", "FRONTER")
POLICY_LEGAL_ENTITY_STATUSES = ("ACTIVE", "INACTIVE")
POLICY_LEGAL_ENTITY_CODE_MAX_LENGTH = 32
POLICY_LEGAL_ENTITY_NAME_MAX_LENGTH = 200
POLICY_LEGAL_ENTITY_REGULATOR_MAX_LENGTH = 120
POLICY_LEGAL_ENTITY_LICENSE_MAX_LENGTH = 80
POLICY_LEGAL_ENTITY_JURISDICTION_PATTERN = "^[A-Z]{2}$"
POLICY_LEGAL_ENTITY_CREATE_REQUIRED_FIELDS = (
    "code",
    "name",
    "entityType",
    "jurisdiction",
)
POLICY_LEGAL_ENTITY_CREATE_OPTIONAL_FIELDS = ("regulator", "licenseNumber")

POLICY_LEGAL_ENTITY_EVENTS = (
    "policy.legal-entity.created",
    "policy.policy.legal-entity-assigned",
)
POLICY_LEGAL_ENTITY_CREATED_EVENT_FIELDS = (
    "legalEntityId",
    "code",
    "name",
    "entityType",
    "jurisdiction",
    "regulator",
    "licenseNumber",
    "status",
    "createdAt",
)
POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_FIELDS = (
    "policyId",
    "policyNumber",
    "status",
    "version",
    "effectiveDate",
    "expirationDate",
    "premiumAmount",
    "premiumCurrency",
    "limitAmount",
    "limitCurrency",
    "legalEntityId",
    "previousLegalEntityId",
    "changedFields",
)
POLICY_LEGAL_ENTITY_CREATED_EVENT_MESSAGE = "PolicyLegalEntityCreatedData"
POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_MESSAGE = "PolicyPolicyLegalEntityAssignedData"
POLICY_LEGAL_ENTITY_EVENT_IMPLEMENTED_BY = "PolicyEvents.java"


# Policy premium audit (SPEC 6.12 policy.premium-audit, SPEC 11.2.10). The
# public command re-rates the written premium with a PREMIUM_AUDIT endorsement
# and version. The audited premium must be non-negative and must change the
# current premium; the eligible statuses, the version-timeline 422/428 rules,
# and the If-Match conflict are the expert's. The implemented event name differs
# from the SPEC 11.2.9 `policy.premium.audited`, which stays planned.
POLICY_PREMIUM_AUDIT_PATH = "/api/v1/policies/{policyId}/premium-audit"
POLICY_PREMIUM_AUDIT_REQUEST = "ApplyPremiumAuditRequest"
POLICY_PREMIUM_AUDIT_REQUIRED_FIELDS = (
    "auditedPremium",
    "effectiveDate",
    "reason",
)
POLICY_PREMIUM_AUDIT_OPTIONAL_FIELDS = ("approvedBy", "approvalRef")
POLICY_PREMIUM_AUDIT_ALLOWED_STATUSES = (
    "BOUND",
    "ISSUED",
    "IN_FORCE",
    "ENDORSED",
    "REINSTATED",
)
POLICY_PREMIUM_AUDIT_AMOUNT_PATTERN = (
    r"^(?:0|[1-9][0-9]{0,14})(?:\.[0-9]{1,4})?$"
)
POLICY_PREMIUM_AUDIT_REASON_MAX_LENGTH = 500
POLICY_PREMIUM_AUDIT_CHANGE_TYPE = "PREMIUM_AUDIT"
POLICY_PREMIUM_AUDIT_EVENT = "policy.policy.premium-audited"
POLICY_PREMIUM_AUDIT_SPEC_EVENT = "policy.premium.audited"
POLICY_PREMIUM_AUDIT_EVENT_FIELDS = (
    "policyId",
    "policyNumber",
    "previousPremium",
    "auditedPremium",
    "delta",
    "currency",
    "effectiveDate",
    "reason",
)
POLICY_PREMIUM_AUDIT_EVENT_MESSAGE = "PolicyPremiumAuditedData"
POLICY_PREMIUM_AUDIT_EVENT_IMPLEMENTED_BY = "PolicyEvents.java"


# Event names the transactional-outbox rollout actually emits. The catalog must
# list each one as published and implemented, and the vertical document must
# expose a channel for it. Round 5 covered the first six verticals; the rollout
# was completed for Policy, Contract, Direct Claims, and Assumed Claims on
# 2026-10-20.
IMPLEMENTED_EVENTS = {
    "party": [
        "party.party.created",
        "party.party.updated",
    ],
    "policy": [
        "policy.policy.created",
        "policy.policy.updated",
        "policy.policy.version-issued",
        "policy.policy.endorsed",
        "policy.policy.cancelled",
        "policy.policy.reinstated",
        "policy.policy.renewed",
        "policy.policy.premium-audited",
        "policy.billing-plan.created",
        "policy.billing-plan.adjusted",
        "policy.installment.paid",
        "policy.installment.waived",
        "policy.dunning.sent",
        "policy.mass-tort-profile.updated",
        "policy.program.created",
        "policy.policy.program-assigned",
        "policy.credit-note.created",
        "policy.credit-note.issued",
        "policy.credit-note.applied",
        "policy.credit-note.cancelled",
        "policy.credit-note.reversed",
        "policy.legal-entity.created",
        "policy.policy.legal-entity-assigned",
    ],
    "contract": [
        "contract.contract.created",
        "contract.contract.updated",
        "contract.contract.bound",
        "contract.contract.commuted",
        "contract.cession.recorded",
        "contract.technical-account.created",
        "contract.technical-account.issued",
        "contract.technical-account.settled",
        "contract.technical-account.line-added",
        "contract.technical-account.line-removed",
        "contract.bordereau.received",
        "contract.bordereau.processed",
        "contract.bordereau.failed",
        "contract.cash-call.requested",
        "contract.cash-call.issued",
        "contract.cash-call.settled",
        "contract.cash-call.cancelled",
        "contract.security.recorded",
        "contract.security.status-changed",
    ],
    "direct-claims": [
        "direct.claim.registered",
        "direct.claim.updated",
        "direct.claim.assigned",
        "direct.claim.coverage-assessed",
        "direct.claim.reserve-changed",
        "direct.claim.settlement-authorized",
        "direct.claim.settlement-payment-linked",
        "direct.claim.closed",
        "direct.claim.task-created",
        "direct.claim.task-completed",
        "direct.claim.task-updated",
        "direct.claim.note-added",
        "direct.claim.allocation-created",
    ],
    "assumed-claims": [
        "assumed.claim.registered",
        "assumed.claim.updated",
        "assumed.claim.assigned",
        "assumed.claim.closed",
        "assumed.claim.reopened",
        "assumed.claim.loss-advice-posted",
        "assumed.claim.reserve-changed",
        "assumed.claim.cash-call-requested",
        "assumed.claim.recovery-recorded",
        "assumed.claim.commuted",
        "assumed.claim.task-created",
        "assumed.claim.task-completed",
        "assumed.claim.task-updated",
        "assumed.claim.note-added",
    ],
    "cession": [
        "cession.cession.created",
        "cession.cession.updated",
        "cession.cession.handed-off",
    ],
    "retrocession": [
        "retrocession.retrocession.created",
        "retrocession.retrocession.updated",
        "retrocession.retrocession.handed-off",
    ],
    "document": [
        "document.document.created",
        "document.document.updated",
        "document.document.status-changed",
        "document.link.added",
        "document.link.removed",
        "document.content.uploaded",
        "document.content.deleted",
        "document.legal-hold.placed",
        "document.legal-hold.released",
        "document.document.disposed",
    ],
    "payment": [
        "payment.payment.created",
        "payment.payment.updated",
        "payment.payment.status-changed",
        "payment.allocation.created",
        "payment.allocation.reversed",
    ],
    "notifications": [
        "notifications.notification.created",
        "notifications.notification.sent",
        "notifications.template.created",
        "notifications.template.approved",
        "notifications.template.retired",
    ],
}

REQUIRED_COMPONENTS = {
    "schemas": [
        "Problem",
        "ProblemFieldError",
        "Money",
        "MoneyAmount",
        "CurrencyCode",
        "Percent",
        "AuditFields",
        "Page",
        "PageMeta",
        "PageLinks",
        "Link",
        "EntityRef",
        "VerticalId",
        "SearchResponse",
        "SearchItem",
        "SearchType",
    ],
    "parameters": [
        "TenantHeader",
        "BookHeaderDirect",
        "BookHeaderAssumed",
        "TenantIdQuery",
        "PageParam",
        "PageSizeParam",
        "SearchQuery",
        "SearchLimit",
        "CorrelationId",
        "IdempotencyKey",
        "ClaimIdempotencyKey",
        "IfMatch",
        "BookHeaderDirectOptional",
    ],
    "headers": [
        "ETag",
        "IdempotentReplayed",
        "IdempotentReplay",
    ],
    "responses": [
        "BadRequest",
        "NotFound",
        "Conflict",
        "UnprocessableContent",
        "PreconditionRequired",
        "BadGateway",
        "ServiceUnavailable",
        "Problem",
    ],
}

REQUIRED_SCHEMA_FILES = [
    "error-envelope.schema.json",
    "money.schema.json",
    "event-envelope.schema.json",
]

# Payment source linkage. The three classified types identify a UUID source;
# OTHER is the reference-only escape hatch. All three fields are optional on the
# wire so an unlinked payment and a pre-linkage payment stay valid.
PAYMENT_SOURCE_FIELDS = ("sourceType", "sourceId", "sourceReference")
PAYMENT_SOURCE_TYPES = ("DIRECT_CLAIM", "ASSUMED_CLAIM", "POLICY", "OTHER")
PAYMENT_CLASSIFIED_SOURCE_TYPES = ("DIRECT_CLAIM", "ASSUMED_CLAIM", "POLICY")
PAYMENT_SOURCE_REFERENCE_MAX_LENGTH = 64

# Payment list source filter. The two optional query parameters form a pair:
# the expert requires both or neither, normalizes the type, and rejects an
# unknown type with INVALID_SOURCE_TYPE and a partial pair with
# INVALID_SOURCE_FILTER.
PAYMENT_SOURCE_FILTER_PARAMETERS = ("sourceType", "sourceId")
PAYMENT_SOURCE_FILTER_ERRORS = ("INVALID_SOURCE_TYPE", "INVALID_SOURCE_FILTER")


# Payment lifecycle (SPEC 11.7.6). The public domain exposes PATCH
# /api/v1/payments/{paymentId}/status; the expert serves the same command under
# /internal/v1. The expert owns the graph, the approval gate, and the optional
# optimistic version check. The implemented graph is wider than the SPEC 11.7.6
# mermaid: it adds the CANCELLED/VOID escape edges, SUBMITTED/ACCEPTED ->
# FAILED, PROCESSING -> PARTIALLY_PAID, and the PARTIALLY_PAID edges (M-46).
PAYMENT_STATUS_OPENAPI_PATH = "/api/v1/payments/{paymentId}/status"
PAYMENT_STATUS_REQUEST_SCHEMA = "UpdatePaymentStatusRequest"
PAYMENT_STATUS_REQUEST_INTERNAL_SCHEMA = "UpdatePaymentStatusRequestInternal"
PAYMENT_STATUSES = (
    "DRAFT",
    "PENDING_AUTHORITY",
    "AUTHORIZED",
    "APPROVED",
    "SCHEDULED",
    "SUBMITTED",
    "ACCEPTED",
    "PROCESSING",
    "PAID",
    "PARTIALLY_PAID",
    "FAILED",
    "REJECTED",
    "CANCELLED",
    "STOPPED",
    "RETURNED",
    "REVERSED",
    "RECONCILED",
    "ESCHEATED",
    "VOID",
)
PAYMENT_STATUS_TRANSITIONS = {
    "DRAFT": ("PENDING_AUTHORITY", "CANCELLED", "VOID"),
    "PENDING_AUTHORITY": ("AUTHORIZED", "REJECTED", "CANCELLED", "VOID"),
    "AUTHORIZED": ("APPROVED", "CANCELLED", "VOID"),
    "APPROVED": ("SCHEDULED", "STOPPED", "VOID"),
    "SCHEDULED": ("SUBMITTED", "CANCELLED", "VOID"),
    "SUBMITTED": ("ACCEPTED", "FAILED"),
    "ACCEPTED": ("PROCESSING", "FAILED"),
    "PROCESSING": ("PAID", "PARTIALLY_PAID", "FAILED"),
    "PARTIALLY_PAID": ("PAID", "RETURNED", "REVERSED"),
    "PAID": ("RECONCILED", "RETURNED", "REVERSED"),
    "RETURNED": ("SCHEDULED", "CANCELLED"),
    "FAILED": ("SCHEDULED", "CANCELLED"),
    "RECONCILED": ("ESCHEATED",),
    "REVERSED": (),
    "ESCHEATED": (),
    "CANCELLED": (),
    "STOPPED": (),
    "REJECTED": (),
    "VOID": (),
}
PAYMENT_TERMINAL_STATUSES = (
    "CANCELLED",
    "STOPPED",
    "REJECTED",
    "VOID",
    "REVERSED",
    "ESCHEATED",
)
PAYMENT_PRE_APPROVAL_STATUSES = ("DRAFT", "PENDING_AUTHORITY", "AUTHORIZED")
PAYMENT_EXECUTION_STATUSES = (
    "SUBMITTED",
    "ACCEPTED",
    "PROCESSING",
    "PAID",
    "PARTIALLY_PAID",
    "RECONCILED",
    "ESCHEATED",
)
PAYMENT_STATUS_REASON_MAX_LENGTH = 200
PAYMENT_STATUS_ERROR_CODES = (
    "VALIDATION_ERROR",
    "INVALID_STATUS",
    "INVALID_STATUS_TRANSITION",
    "PAYMENT_NOT_APPROVED",
    "CONCURRENT_MODIFICATION",
    "PAYMENT_NOT_FOUND",
    "MISSING_TENANT_HEADER",
    "INVALID_PARAMETER",
)
PAYMENT_STATUS_EVENTS = (
    "payment.payment.updated",
    "payment.payment.status-changed",
)


# Payment allocations (SPEC 11.7.11). The public domain exposes GET/POST
# /api/v1/payments/{paymentId}/allocations plus the allocation reversal under
# .../{allocationId}/reverse; the expert serves the same paths and an
# /internal/v1 alias that the domain calls, but the alias is an implementation
# detail and is not part of the public contract. An allocation is append-only,
# always uses the payment currency, and may not take the payment's active
# allocated total above the payment amount. A reversal stamps the row, releases
# the amount, and reports the gross/reversed/net summary totals.
PAYMENT_ALLOCATION_OPENAPI_PATHS = [
    (
        "get",
        "/api/v1/payments/{paymentId}/allocations",
        "200",
        "PaymentAllocationSummary",
        None,
    ),
    (
        "post",
        "/api/v1/payments/{paymentId}/allocations",
        "201",
        "PaymentAllocation",
        "CreatePaymentAllocationRequest",
    ),
]

PAYMENT_ALLOCATION_REVERSE_OPENAPI_PATH = (
    "/api/v1/payments/{paymentId}/allocations/{allocationId}/reverse"
)

PAYMENT_ALLOCATION_FIELDS = (
    "allocationId",
    "paymentId",
    "targetType",
    "targetId",
    "component",
    "amount",
    "currency",
    "createdAt",
    "reversedAt",
    "reversalReason",
)

PAYMENT_ALLOCATION_SUMMARY_FIELDS = (
    "items",
    "paymentAmount",
    "totalAllocated",
    "reversedTotal",
    "net",
    "unallocated",
    "currency",
)

PAYMENT_ALLOCATION_REQUEST_FIELDS = (
    "targetType",
    "targetId",
    "component",
    "amount",
)

PAYMENT_ALLOCATION_REVERSE_REQUEST_FIELDS = ("reason",)
PAYMENT_ALLOCATION_REVERSAL_REASON_MAX_LENGTH = 200

PAYMENT_ALLOCATION_TARGET_TYPES = ("DIRECT_CLAIM", "ASSUMED_CLAIM", "POLICY")
PAYMENT_ALLOCATION_COMPONENTS = (
    "INDEMNITY",
    "DEFENSE_COST",
    "ALAE",
    "EXPENSE",
    "COMMISSION",
    "OTHER",
)
PAYMENT_ALLOCATION_CONFLICT_CODES = (
    "ALLOCATION_EXCEEDS_PAYMENT",
    "PAYMENT_NOT_ALLOCATABLE",
)
PAYMENT_ALLOCATION_REVERSE_CONFLICT_CODES = ("ALLOCATION_ALREADY_REVERSED",)
PAYMENT_ALLOCATION_NOT_FOUND_CODES = ("PAYMENT_NOT_FOUND", "ALLOCATION_NOT_FOUND")
PAYMENT_ALLOCATION_EVENT = "payment.allocation.created"
PAYMENT_ALLOCATION_EVENT_FIELDS = (
    "paymentId",
    "paymentNumber",
    "targetType",
    "targetId",
    "component",
    "amount",
    "currency",
    "totalAllocated",
    "paymentAmount",
)
PAYMENT_ALLOCATION_REVERSE_EVENT = "payment.allocation.reversed"
PAYMENT_ALLOCATION_REVERSE_EVENT_FIELDS = (
    "paymentId",
    "allocationId",
    "targetType",
    "targetId",
    "component",
    "amount",
    "reason",
    "reversedAt",
)

# Document association links. The three public routes are mirrored on the
# expert's /internal/v1 base; both surfaces are mandatory. The link vocabulary
# is the closed set the expert enforces, and linkedReference is an optional
# display snapshot rather than a resolved target.
DOCUMENT_LINK_OPENAPI_PATHS = [
    ("/api/v1/documents/{documentId}/links", "get"),
    ("/api/v1/documents/{documentId}/links", "post"),
    ("/api/v1/documents/{documentId}/links/{linkId}", "delete"),
    ("/internal/v1/documents/{documentId}/links", "get"),
    ("/internal/v1/documents/{documentId}/links", "post"),
    ("/internal/v1/documents/{documentId}/links/{linkId}", "delete"),
]

DOCUMENT_LINKED_TYPES = (
    "DIRECT_CLAIM",
    "ASSUMED_CLAIM",
    "POLICY",
    "CONTRACT",
    "PARTY",
    "PAYMENT",
    "OTHER",
)

DOCUMENT_LINK_REFERENCE_MAX_LENGTH = 64

# Document content. One document owns one current content pointer and an
# append-only revision history; every upload appends a revision and advances
# the pointer. The public surface is six routes from 1.6.0, including the
# content tombstone. The metadata projection is named DocumentContent because
# the bytes are not part of it, and the history projection is
# DocumentContentVersion.
DOCUMENT_CONTENT_PATH = "/api/v1/documents/{documentId}/content"
DOCUMENT_CONTENT_METADATA_PATH = "/api/v1/documents/{documentId}/content/metadata"
DOCUMENT_CONTENT_VERSIONS_PATH = "/api/v1/documents/{documentId}/content/versions"
DOCUMENT_CONTENT_VERSION_PATH = (
    "/api/v1/documents/{documentId}/content/versions/{version}"
)
DOCUMENT_CONTENT_FIELDS = (
    "documentId",
    "fileName",
    "contentType",
    "sizeBytes",
    "sha256",
    "uploadedAt",
    "deletedAt",
    "deleted",
)
DOCUMENT_CONTENT_VERSION_FIELDS = (
    "documentId",
    "version",
    "fileName",
    "contentType",
    "sizeBytes",
    "sha256",
    "uploadedAt",
)
DOCUMENT_CONTENT_MAX_BYTES = 10 * 1024 * 1024
DOCUMENT_CONTENT_FILE_NAME_MAX_LENGTH = 255
DOCUMENT_CONTENT_TYPE_MAX_LENGTH = 128
DOCUMENT_CONTENT_ERRORS = ("EMPTY_CONTENT", "FILE_TOO_LARGE")
DOCUMENT_CONTENT_EVENT = "document.content.uploaded"
DOCUMENT_CONTENT_DELETED_EVENT = "document.content.deleted"
DOCUMENT_CONTENT_DELETED_EVENT_FIELDS = (
    "documentId",
    "documentNumber",
    "fileName",
    "sizeBytes",
    "sha256",
    "deletedAt",
)
DOCUMENT_CONTENT_DELETE_CODES = (
    "CONTENT_NOT_FOUND",
    "DOCUMENT_ON_LEGAL_HOLD",
    "CONTENT_ALREADY_DELETED",
)

# Document legal holds and disposition. The implemented hold surface is
# per-document and synchronous, not the SPEC 11.6.10 hold collection. A hold may
# be placed only from ACTIVE, ARCHIVED, CLASSIFIED, or SUPERSEDED; release
# restores the snapshotted status (ARCHIVED when absent); disposition requires
# an expired retention date and no active hold. The seven conflict codes are the
# complete state vocabulary the expert returns on 409.
DOCUMENT_HOLD_PATH = "/api/v1/documents/{documentId}/hold"
DOCUMENT_HOLD_RELEASE_PATH = "/api/v1/documents/{documentId}/hold/release"
DOCUMENT_DISPOSAL_PATH = "/api/v1/documents/{documentId}/dispose"
DOCUMENT_HOLD_FIELDS = (
    "holdReason",
    "heldAt",
    "statusBeforeHold",
    "disposedAt",
)
DOCUMENT_HOLD_REASON_MAX_LENGTH = 500
DOCUMENT_STATUSES = (
    "PENDING_UPLOAD",
    "RECEIVED",
    "SCANNING",
    "PROCESSING",
    "CLASSIFIED",
    "ACTIVE",
    "SUPERSEDED",
    "ON_HOLD",
    "ARCHIVED",
    "DISPOSED",
    "REJECTED",
    "FAILED",
)
DOCUMENT_HOLD_CODES = ("HOLD_STATUS_NOT_ALLOWED", "DOCUMENT_ALREADY_ON_HOLD")
DOCUMENT_HOLD_RELEASE_CODES = ("DOCUMENT_NOT_ON_HOLD",)
DOCUMENT_DISPOSAL_CODES = (
    "DOCUMENT_ON_LEGAL_HOLD",
    "DISPOSAL_STATUS_NOT_ALLOWED",
    "RETENTION_DATE_REQUIRED",
    "RETENTION_NOT_EXPIRED",
)
# A successful disposition tombstones live content in the same transaction and
# emits document.content.deleted alongside document.document.disposed. Its
# description must name both facts and state that a document with no stored
# content or already-tombstoned content still disposes normally.
DOCUMENT_DISPOSAL_DESCRIPTION_TERMS = (
    "document.document.disposed",
    "document.content.deleted",
    "no stored content",
    "already tombstoned",
    "same transaction",
)
# The two content reads and the explicit tombstone must point at a disposition
# as the other producer of a content tombstone, so the shared 410 and deletedAt
# behaviour is not documented as a DELETE-only effect.
DOCUMENT_CONTENT_DISPOSITION_TERMS = ("disposition",)
DOCUMENT_LIFECYCLE_CODES = (
    DOCUMENT_HOLD_CODES
    + DOCUMENT_HOLD_RELEASE_CODES
    + DOCUMENT_DISPOSAL_CODES
)
DOCUMENT_LIFECYCLE_EVENTS = (
    "document.legal-hold.placed",
    "document.legal-hold.released",
    "document.document.disposed",
)
DOCUMENT_LIFECYCLE_DATA = "DocumentLifecycleData"
DOCUMENT_LIFECYCLE_EVENT_FIELDS = (
    "documentId",
    "documentNumber",
    "reason",
    "status",
)


# Notifications. SPEC 11.8.5 v1 does not name a dunning escalation type; the
# implemented expert and domain add DUNNING_NOTICE to the closed NotificationType
# set between ESCHEATMENT_DUE and NEW_DOCUMENT_UPLOAD. The Notification
# projection and both create commands reference the one NotificationType schema,
# so the contract must enumerate the type once and keep all three references, or
# a create would accept a value the read cannot return (or the reverse).
NOTIFICATION_TYPE_SCHEMA = "NotificationType"
NOTIFICATION_DUNNING_TYPE = "DUNNING_NOTICE"
NOTIFICATION_TYPE_PREDECESSOR = "ESCHEATMENT_DUE"
NOTIFICATION_TYPE_SUCCESSOR = "NEW_DOCUMENT_UPLOAD"
NOTIFICATION_TYPE_REFERENCES = (
    ("Notification", "notificationType"),
    ("CreateNotificationRequest", "notificationType"),
    ("CreateNotificationRequestInternal", "notificationType"),
)

# Notification template administration (SPEC 11.8.10, NTF-14). The implemented
# public surface is the short /api/v1/notifications/templates resource rather
# than the SPEC admin path: list with optional status/code filters, create DRAFT,
# approve with an approver, and retire. A template is created DRAFT, approval is
# the only path to ACTIVE, and RETIRED is terminal. The unique key is
# (tenant, templateCode, templateVersion, locale), so a duplicate create is 409
# TEMPLATE_ALREADY_EXISTS; a repeated approval of an ACTIVE template is 409
# TEMPLATE_ALREADY_ACTIVE; any other illegal transition or concurrent loss is
# 409 TEMPLATE_STATUS_CONFLICT. Every accepted write emits one template event.
NOTIFICATION_TEMPLATE_OPENAPI_PATHS = [
    (
        "get",
        "/api/v1/notifications/templates",
        "200",
        "NotificationTemplate",
        None,
        ("400",),
    ),
    (
        "post",
        "/api/v1/notifications/templates",
        "201",
        "NotificationTemplate",
        "CreateNotificationTemplateRequest",
        ("400", "409"),
    ),
    (
        "post",
        "/api/v1/notifications/templates/{id}/approve",
        "200",
        "NotificationTemplate",
        "ApproveNotificationTemplateRequest",
        ("400", "404", "409"),
    ),
    (
        "post",
        "/api/v1/notifications/templates/{id}/retire",
        "200",
        "NotificationTemplate",
        None,
        ("400", "404", "409"),
    ),
]

NOTIFICATION_TEMPLATE_FIELDS = (
    "id",
    "code",
    "version",
    "channel",
    "locale",
    "bodyTemplate",
    "status",
    "approvedBy",
    "approvedAt",
    "createdAt",
    "updatedAt",
)
NOTIFICATION_TEMPLATE_STATUSES = ("DRAFT", "ACTIVE", "RETIRED")
NOTIFICATION_TEMPLATE_CREATE_PROPERTIES = (
    "templateCode",
    "templateVersion",
    "channel",
    "locale",
    "bodyTemplate",
)
NOTIFICATION_TEMPLATE_CREATE_REQUIRED = (
    "templateCode",
    "templateVersion",
    "locale",
    "bodyTemplate",
)
NOTIFICATION_TEMPLATE_CODE_MAX_LENGTH = 64
NOTIFICATION_TEMPLATE_LOCALE_MAX_LENGTH = 16
NOTIFICATION_TEMPLATE_CONFLICT_CODES = (
    "TEMPLATE_ALREADY_EXISTS",
    "TEMPLATE_ALREADY_ACTIVE",
    "TEMPLATE_STATUS_CONFLICT",
)
NOTIFICATION_TEMPLATE_EVENTS = (
    "notifications.template.created",
    "notifications.template.approved",
    "notifications.template.retired",
)
NOTIFICATION_TEMPLATE_EVENT_FIELDS = (
    "templateId",
    "code",
    "version",
    "locale",
    "status",
    "approvedBy",
)
NOTIFICATION_TEMPLATE_EVENT_MESSAGE = "NotificationTemplateData"
NOTIFICATION_TEMPLATE_EVENT_IMPLEMENTED_BY = "NotificationTemplateEvents.java"

EVENT_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")
VALID_JSON_TYPES = {"null", "boolean", "object", "array", "number", "string", "integer"}


# ---------------------------------------------------------------------------
# Minimal YAML parser for the repository's YAML subset
# ---------------------------------------------------------------------------


class YamlError(ValueError):
    def __init__(self, source: Path, line: int, message: str):
        super().__init__(f"{source}:{line}: {message}")
        self.source = source
        self.line = line
        self.message = message


class _YamlParser:
    """Parse the YAML subset used by this repository.

    Supported: block mappings and sequences, plain and quoted scalars, flow
    lists and flow maps, literal and folded block scalars, full-line comments,
    and trailing comments on scalars. Anchors, aliases, tags, multiple
    documents, complex keys, and explicit indentation indicators are rejected.
    """

    def __init__(self, text: str, source: Path):
        self.lines = text.splitlines()
        self.source = source
        self.i = 0

    # -- helpers ---------------------------------------------------------

    def _error(self, line_index: int, message: str) -> YamlError:
        return YamlError(self.source, line_index + 1, message)

    def _indent_of(self, raw: str, line_index: int) -> int:
        stripped = raw.lstrip(" ")
        indent = len(raw) - len(stripped)
        if stripped.startswith("\t") or raw[:indent].find("\t") != -1:
            raise self._error(line_index, "tab character in indentation")
        return indent

    def _peek(self):
        """Return (indent, content, line_index) of the next content line."""
        while self.i < len(self.lines):
            raw = self.lines[self.i]
            stripped = raw.strip()
            if stripped == "" or stripped.startswith("#"):
                self.i += 1
                continue
            if stripped in ("---", "..."):
                self.i += 1
                continue
            indent = self._indent_of(raw, self.i)
            return indent, raw[indent:], self.i
        return None

    # -- public ----------------------------------------------------------

    def parse(self):
        node = self._parse_node(0)
        extra = self._peek()
        if extra is not None:
            raise self._error(extra[2], "unexpected content after the document root")
        return node

    # -- structure -------------------------------------------------------

    def _parse_node(self, indent: int):
        peeked = self._peek()
        if peeked is None:
            return None
        current, content, line_index = peeked
        if current != indent:
            raise self._error(line_index, f"expected indentation {indent}, found {current}")
        if content == "-" or content.startswith("- "):
            return self._parse_sequence(indent)
        return self._parse_mapping(indent)

    def _parse_mapping(self, indent: int):
        result = {}
        while True:
            peeked = self._peek()
            if peeked is None:
                break
            current, content, line_index = peeked
            if current < indent:
                break
            if current > indent:
                raise self._error(line_index, f"unexpected indentation {current} inside a mapping")
            if content == "-" or content.startswith("- "):
                raise self._error(line_index, "sequence item where a mapping key was expected")
            key, rest = self._split_key(content, line_index)
            if key in result:
                raise self._error(line_index, f"duplicate key '{key}'")
            self.i = line_index + 1
            result[key] = self._parse_value(rest, indent, line_index)
        return result

    def _parse_sequence(self, indent: int):
        result = []
        while True:
            peeked = self._peek()
            if peeked is None:
                break
            current, content, line_index = peeked
            if current < indent:
                break
            if current > indent:
                raise self._error(line_index, f"unexpected indentation {current} inside a sequence")
            if not (content == "-" or content.startswith("- ")):
                break
            rest = content[1:]
            if rest.startswith(" "):
                rest = rest[1:]
            self.i = line_index + 1
            if rest.strip() == "":
                peeked_inner = self._peek()
                if peeked_inner is None or peeked_inner[0] <= indent:
                    result.append(None)
                else:
                    result.append(self._parse_node(peeked_inner[0]))
                continue
            key_split = self._try_split_key(rest)
            if key_split is not None:
                item = self._parse_inline_mapping_item(rest, indent, line_index)
                result.append(item)
            else:
                result.append(self._parse_scalar(rest, line_index))
        return result

    def _parse_inline_mapping_item(self, first_content: str, dash_indent: int, line_index: int):
        """Parse a sequence item that starts with a mapping entry on the dash line."""
        first_key, first_rest = self._split_key(first_content, line_index)
        # The mapping's indentation is the column of the first key.
        prefix = len(first_content) - len(first_content.lstrip(" "))
        item_indent = dash_indent + 2 + prefix
        item = {first_key: self._parse_value(first_rest, item_indent, line_index)}
        while True:
            peeked = self._peek()
            if peeked is None:
                break
            current, content, next_line = peeked
            if current < item_indent:
                break
            if current > item_indent:
                raise self._error(next_line, f"unexpected indentation {current} in a sequence item")
            if content == "-" or content.startswith("- "):
                break
            key, rest = self._split_key(content, next_line)
            if key in item:
                raise self._error(next_line, f"duplicate key '{key}' in a sequence item")
            self.i = next_line + 1
            item[key] = self._parse_value(rest, item_indent, next_line)
        return item

    def _parse_value(self, rest: str, parent_indent: int, line_index: int):
        text = rest.strip()
        if text == "":
            peeked = self._peek()
            if peeked is None or peeked[0] <= parent_indent:
                return None
            return self._parse_node(peeked[0])
        if text[0] in ("|", ">"):
            style = text[0]
            chomp = text[1:]
            if chomp not in ("", "-", "+"):
                raise self._error(line_index, f"unsupported block scalar header '{text}'")
            return self._read_block_scalar(parent_indent, style, chomp, line_index)
        return self._parse_scalar(text, line_index)

    # -- scalars ---------------------------------------------------------

    def _read_block_scalar(self, parent_indent: int, style: str, chomp: str, line_index: int) -> str:
        block = []
        block_indent = None
        while self.i < len(self.lines):
            raw = self.lines[self.i]
            if raw.strip() == "":
                block.append("")
                self.i += 1
                continue
            indent = self._indent_of(raw, self.i)
            if indent <= parent_indent:
                break
            if block_indent is None:
                block_indent = indent
            if indent < block_indent:
                break
            block.append(raw[block_indent:])
            self.i += 1
        if style == "|":
            text = "\n".join(block)
        else:
            parts = []
            previous_blank = False
            for line in block:
                if line == "":
                    parts.append("\n")
                    previous_blank = True
                else:
                    if parts and not previous_blank:
                        parts.append(" ")
                    parts.append(line)
                    previous_blank = False
            text = "".join(parts)
        if chomp == "-":
            return text.rstrip("\n")
        if chomp == "+":
            return text + "\n"
        return text.rstrip("\n") + "\n"

    def _parse_scalar(self, text: str, line_index: int):
        value = _strip_trailing_comment(text).strip()
        if value == "":
            return ""
        if value[0] == "'":
            return _parse_single_quoted(value, self.source, line_index)
        if value[0] == '"':
            return _parse_double_quoted(value, self.source, line_index)
        if value[0] == "[":
            return _parse_flow_sequence(value, self.source, line_index)
        if value[0] == "{":
            return _parse_flow_map(value, self.source, line_index)
        if value in ("null", "Null", "NULL", "~"):
            return None
        if value in ("true", "True", "TRUE"):
            return True
        if value in ("false", "False", "FALSE"):
            return False
        if re.fullmatch(r"[+-]?[0-9]+", value):
            return int(value)
        if value[0] in ("&", "*", "!", "@", "`"):
            raise YamlError(self.source, line_index + 1, f"unsupported YAML construct '{value[0]}'")
        return value

    # -- keys ------------------------------------------------------------

    def _try_split_key(self, content: str):
        try:
            return _split_key_text(content, self.source, 0)
        except YamlError:
            return None

    def _split_key(self, content: str, line_index: int):
        return _split_key_text(content, self.source, line_index)


def _strip_trailing_comment(text: str) -> str:
    quote = None
    depth = 0
    i = 0
    while i < len(text):
        char = text[i]
        if quote == "'":
            if char == "'":
                if i + 1 < len(text) and text[i + 1] == "'":
                    i += 2
                    continue
                quote = None
        elif quote == '"':
            if char == "\\":
                i += 2
                continue
            if char == '"':
                quote = None
        else:
            if char in ("'", '"'):
                quote = char
            elif char in "[{":
                depth += 1
            elif char in "]}":
                depth -= 1
            elif char == "#" and depth == 0 and (i == 0 or text[i - 1] in " \t"):
                return text[:i]
        i += 1
    return text


def _split_key_text(content: str, source: Path, line_index: int):
    quote = None
    depth = 0
    i = 0
    while i < len(content):
        char = content[i]
        if quote == "'":
            if char == "'":
                if i + 1 < len(content) and content[i + 1] == "'":
                    i += 2
                    continue
                quote = None
        elif quote == '"':
            if char == "\\":
                i += 2
                continue
            if char == '"':
                quote = None
        else:
            if char in ("'", '"'):
                quote = char
            elif char in "[{":
                depth += 1
            elif char in "]}":
                depth -= 1
            elif char == ":" and depth == 0:
                next_char = content[i + 1] if i + 1 < len(content) else ""
                if next_char in ("", " ", "\t"):
                    raw_key = content[:i].strip()
                    if raw_key == "":
                        raise YamlError(source, line_index + 1, "empty mapping key")
                    key = _unquote_key(raw_key, source, line_index)
                    return key, content[i + 1:]
        i += 1
    raise YamlError(source, line_index + 1, f"expected 'key: value', found '{content.strip()}'")


def _unquote_key(raw: str, source: Path, line_index: int) -> str:
    if raw[0] == "'":
        return _parse_single_quoted(raw, source, line_index)
    if raw[0] == '"':
        return _parse_double_quoted(raw, source, line_index)
    return raw


def _require_consumed(text: str, position: int, source: Path, line_index: int):
    if text[position:].strip() != "":
        raise YamlError(source, line_index + 1, f"unexpected trailing text '{text[position:].strip()}'")


def _parse_single_quoted(text: str, source: Path, line_index: int) -> str:
    result = []
    i = 1
    while i < len(text):
        if text[i] == "'":
            if i + 1 < len(text) and text[i + 1] == "'":
                result.append("'")
                i += 2
                continue
            _require_consumed(text, i + 1, source, line_index)
            return "".join(result)
        result.append(text[i])
        i += 1
    raise YamlError(source, line_index + 1, "unterminated single-quoted scalar")


def _parse_double_quoted(text: str, source: Path, line_index: int) -> str:
    escapes = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "0": "\0"}
    result = []
    i = 1
    while i < len(text):
        char = text[i]
        if char == "\\":
            if i + 1 >= len(text):
                raise YamlError(source, line_index + 1, "dangling escape in double-quoted scalar")
            escape = text[i + 1]
            result.append(escapes.get(escape, escape))
            i += 2
            continue
        if char == '"':
            _require_consumed(text, i + 1, source, line_index)
            return "".join(result)
        result.append(char)
        i += 1
    raise YamlError(source, line_index + 1, "unterminated double-quoted scalar")


def _split_flow_items(inner: str) -> list[str]:
    items = []
    start = 0
    depth = 0
    quote = None
    i = 0
    while i < len(inner):
        char = inner[i]
        if quote == "'":
            if char == "'":
                if i + 1 < len(inner) and inner[i + 1] == "'":
                    i += 2
                    continue
                quote = None
        elif quote == '"':
            if char == "\\":
                i += 2
                continue
            if char == '"':
                quote = None
        else:
            if char in ("'", '"'):
                quote = char
            elif char in "[{":
                depth += 1
            elif char in "]}":
                depth -= 1
            elif char == "," and depth == 0:
                items.append(inner[start:i])
                start = i + 1
        i += 1
    items.append(inner[start:])
    return [item for item in items if item.strip() != ""]


def _parse_flow_sequence(text: str, source: Path, line_index: int):
    close = _matching_flow(text, 0, "[", "]", source, line_index)
    inner = text[1:close]
    _require_consumed(text, close + 1, source, line_index)
    if inner.strip() == "":
        return []
    result = []
    for item in _split_flow_items(inner):
        value = _strip_trailing_comment(item).strip()
        if value[:1] == "'":
            result.append(_parse_single_quoted(value, source, line_index))
        elif value[:1] == '"':
            result.append(_parse_double_quoted(value, source, line_index))
        elif value[:1] == "[":
            result.append(_parse_flow_sequence(value, source, line_index))
        elif value[:1] == "{":
            result.append(_parse_flow_map(value, source, line_index))
        elif value in ("true", "false"):
            result.append(value == "true")
        elif value in ("null", "~"):
            result.append(None)
        elif re.fullmatch(r"[+-]?[0-9]+", value):
            result.append(int(value))
        else:
            result.append(value)
    return result


def _parse_flow_map(text: str, source: Path, line_index: int):
    close = _matching_flow(text, 0, "{", "}", source, line_index)
    inner = text[1:close]
    _require_consumed(text, close + 1, source, line_index)
    if inner.strip() == "":
        return {}
    result = {}
    for item in _split_flow_items(inner):
        key, rest = _split_key_text(item.strip(), source, line_index)
        value = rest.strip()
        if value[:1] == "'":
            result[key] = _parse_single_quoted(value, source, line_index)
        elif value[:1] == '"':
            result[key] = _parse_double_quoted(value, source, line_index)
        elif value == "":
            result[key] = None
        else:
            result[key] = value
    return result


def _matching_flow(text: str, start: int, open_char: str, close_char: str, source: Path, line_index: int) -> int:
    depth = 0
    quote = None
    i = start
    while i < len(text):
        char = text[i]
        if quote == "'":
            if char == "'":
                if i + 1 < len(text) and text[i + 1] == "'":
                    i += 2
                    continue
                quote = None
        elif quote == '"':
            if char == "\\":
                i += 2
                continue
            if char == '"':
                quote = None
        else:
            if char in ("'", '"'):
                quote = char
            elif char == open_char:
                depth += 1
            elif char == close_char:
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    raise YamlError(source, line_index + 1, f"unterminated flow collection starting with '{open_char}'")


def parse_yaml(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise SystemExit(f"cannot read {path}: {error}")
    return _YamlParser(text, path).parse()


# ---------------------------------------------------------------------------
# JSON Reference resolution
# ---------------------------------------------------------------------------


class ContractSet:
    def __init__(self):
        self.cache = {}
        self.failures = []
        self.checks = 0

    def fail(self, message: str):
        self.failures.append(message)

    def check(self, condition: bool, message: str):
        self.checks += 1
        if not condition:
            self.fail(message)
        return condition

    def load(self, path: Path):
        path = path.resolve()
        if path in self.cache:
            return self.cache[path]
        if not str(path).startswith(str(ROOT)):
            raise SystemExit(f"reference escapes the repository: {path}")
        if path.suffix.lower() == ".json":
            with path.open(encoding="utf-8") as handle:
                value = json.load(handle)
        else:
            value = parse_yaml(path)
        self.cache[path] = value
        return value

    def resolve(self, document, reference: str):
        if reference.startswith("#"):
            file_part = ""
            pointer = reference[2:] if reference.startswith("#/") else reference[1:]
            target = document
            target_path = None
        else:
            file_part, _, pointer = reference.partition("#")
            pointer = pointer[1:] if pointer.startswith("/") else pointer
            target_path = (self.current_file.parent / file_part).resolve()
            if not target_path.exists():
                raise KeyError(f"missing referenced file {file_part}")
            target = self.load(target_path)
        value = target
        if pointer:
            for raw_token in pointer.split("/"):
                token = raw_token.replace("~1", "/").replace("~0", "~")
                if isinstance(value, list):
                    value = value[int(token)]
                elif isinstance(value, dict):
                    value = value[token]
                else:
                    raise KeyError(f"cannot descend into {type(value).__name__} at '{token}'")
        return value, target_path

    def walk_refs(self, node, document_path: Path, trail: str):
        self.current_file = document_path
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "$ref" and isinstance(value, str):
                    try:
                        target, target_path = self.resolve(self.load(document_path), value)
                    except (KeyError, IndexError, ValueError, json.JSONDecodeError, YamlError) as error:
                        self.fail(f"{document_path.relative_to(ROOT).as_posix()} {trail}: unresolved $ref '{value}': {error}")
                        continue
                    if target is None:
                        self.fail(f"{document_path.relative_to(ROOT).as_posix()} {trail}: $ref '{value}' resolves to null")
                else:
                    self.walk_refs(value, document_path, f"{trail}/{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                self.walk_refs(value, document_path, f"{trail}/{index}")

    def check_schema_object(self, schema, relative, trail: str = "$"):
        """Check schema hygiene on an already-parsed schema object."""
        if not isinstance(schema, dict):
            return
        declared = schema.get("type")
        if declared is not None:
            values = declared if isinstance(declared, list) else [declared]
            self.check(
                all(value in VALID_JSON_TYPES for value in values),
                f"{relative} {trail}: invalid schema type {declared}",
            )
        if "required" in schema:
            required = schema["required"]
            self.check(isinstance(required, list), f"{relative} {trail}: required must be a list")
            properties = schema.get("properties")
            if isinstance(required, list) and isinstance(properties, dict):
                for field in required:
                    self.check(
                        field in properties,
                        f"{relative} {trail}: required '{field}' has no property definition",
                    )
        if "properties" in schema:
            self.check(isinstance(schema["properties"], dict), f"{relative} {trail}: properties must be a mapping")
            for name, sub in (schema["properties"] or {}).items():
                self.check_schema_object(sub, relative, f"{trail}.properties.{name}")
        if "enum" in schema:
            self.check(
                isinstance(schema["enum"], list) and bool(schema["enum"]),
                f"{relative} {trail}: enum must be a non-empty list",
            )
        for keyword in ("allOf", "oneOf", "anyOf"):
            for index, sub in enumerate(schema.get(keyword) or []):
                self.check_schema_object(sub, relative, f"{trail}.{keyword}[{index}]")
        if isinstance(schema.get("items"), dict):
            self.check_schema_object(schema["items"], relative, f"{trail}.items")
        for keyword in ("$defs", "definitions"):
            for name, sub in (schema.get(keyword) or {}).items():
                self.check_schema_object(sub, relative, f"{trail}.{keyword}.{name}")

    def check_openapi_schemas(self, document, relative):
        schemas = (document.get("components") or {}).get("schemas") or {}
        for name, schema in schemas.items():
            self.check_schema_object(schema, str(relative), f"components.schemas.{name}")



# ---------------------------------------------------------------------------
# Payment source-linkage checks
# ---------------------------------------------------------------------------


def _payment_source_type_values(property_schema, document):
    """Return the sourceType enum values from a plain, oneOf, or $ref property."""
    if not isinstance(property_schema, dict):
        return set()
    if isinstance(property_schema.get("enum"), list):
        return set(property_schema["enum"])
    for branch in property_schema.get("oneOf") or []:
        if not isinstance(branch, dict):
            continue
        if isinstance(branch.get("enum"), list):
            return set(branch["enum"])
        reference = branch.get("$ref")
        if isinstance(reference, str):
            target = _local_ref(document, reference)
            if isinstance(target, dict) and isinstance(target.get("enum"), list):
                return set(target["enum"])
    return set()


def _payment_create_rules(schema):
    """Return (classified requires sourceId, sourceId requires sourceType)."""
    classified_rule = False
    pairing_rule = False
    for branch in schema.get("allOf") or []:
        if not isinstance(branch, dict):
            continue
        condition = branch.get("if") or {}
        consequence = branch.get("then") or {}
        if not isinstance(condition, dict) or not isinstance(consequence, dict):
            continue
        condition_required = set(condition.get("required") or [])
        then_required = set(consequence.get("required") or [])
        condition_properties = condition.get("properties") or {}
        source_type = condition_properties.get("sourceType") or {}
        source_id = condition_properties.get("sourceId") or {}
        if (
            "sourceType" in condition_required
            and set(source_type.get("enum") or []) == set(PAYMENT_CLASSIFIED_SOURCE_TYPES)
            and "sourceId" in then_required
        ):
            classified_rule = True
        if (
            "sourceId" in condition_required
            and source_id.get("type") == "string"
            and "sourceType" in then_required
        ):
            pairing_rule = True
    return classified_rule, pairing_rule


def check_payment_openapi_sources(contracts: ContractSet, document, relative: str):
    """Require the optional source fields and create rules in openapi/payment.yaml."""
    schemas = (document.get("components") or {}).get("schemas") or {}
    payment = schemas.get("Payment") or {}
    payment_properties = payment.get("properties") or {}
    for field in PAYMENT_SOURCE_FIELDS:
        contracts.check(
            field in payment_properties,
            f"{relative}: Payment.properties.{field} is required",
        )
    contracts.check(
        _payment_source_type_values(payment_properties.get("sourceType"), document)
        == set(PAYMENT_SOURCE_TYPES),
        f"{relative}: Payment.sourceType must enumerate {list(PAYMENT_SOURCE_TYPES)}",
    )
    contracts.check(
        (payment_properties.get("sourceId") or {}).get("format") == "uuid",
        f"{relative}: Payment.sourceId must be a uuid",
    )
    contracts.check(
        (payment_properties.get("sourceReference") or {}).get("maxLength")
        == PAYMENT_SOURCE_REFERENCE_MAX_LENGTH,
        f"{relative}: Payment.sourceReference maxLength must be {PAYMENT_SOURCE_REFERENCE_MAX_LENGTH}",
    )

    for schema_name in ("CreatePaymentRequest", "CreatePaymentRequestInternal"):
        schema = schemas.get(schema_name) or {}
        properties = schema.get("properties") or {}
        required = set(schema.get("required") or [])
        for field in PAYMENT_SOURCE_FIELDS:
            contracts.check(
                field in properties,
                f"{relative}: {schema_name}.properties.{field} is required",
            )
            contracts.check(
                field not in required,
                f"{relative}: {schema_name}.{field} must stay optional",
            )
        contracts.check(
            _payment_source_type_values(properties.get("sourceType"), document)
            == set(PAYMENT_SOURCE_TYPES),
            f"{relative}: {schema_name}.sourceType must enumerate {list(PAYMENT_SOURCE_TYPES)}",
        )
        contracts.check(
            (properties.get("sourceId") or {}).get("format") == "uuid",
            f"{relative}: {schema_name}.sourceId must be a uuid",
        )
        contracts.check(
            (properties.get("sourceReference") or {}).get("maxLength")
            == PAYMENT_SOURCE_REFERENCE_MAX_LENGTH,
            f"{relative}: {schema_name}.sourceReference maxLength must be "
            f"{PAYMENT_SOURCE_REFERENCE_MAX_LENGTH}",
        )
        classified_rule, pairing_rule = _payment_create_rules(schema)
        contracts.check(
            classified_rule,
            f"{relative}: {schema_name} must require sourceId for "
            f"{list(PAYMENT_CLASSIFIED_SOURCE_TYPES)}",
        )
        contracts.check(
            pairing_rule,
            f"{relative}: {schema_name} must require sourceType when sourceId is supplied",
        )


def _payment_filter_parameter(operation, name):
    """Return the inline query parameter named ``name`` from an operation."""
    for parameter in operation.get("parameters") or []:
        if isinstance(parameter, dict) and parameter.get("name") == name:
            return parameter
    return None


def check_payment_source_filter(contracts: ContractSet, document, relative: str):
    """Require the optional sourceType + sourceId list filter and its 400s.

    Both the public domain list and the expert list accept the pair. The
    operation must document the tenant scope, both optional query parameters,
    the closed source-type enum, the UUID source id, the 400 response, and the
    two filter error codes.
    """
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}
    source_type = schemas.get("PaymentSourceType") or {}
    contracts.check(
        source_type.get("type") == "string",
        f"{relative}: PaymentSourceType must be a string enum",
    )
    contracts.check(
        set(source_type.get("enum") or []) == set(PAYMENT_SOURCE_TYPES),
        f"{relative}: PaymentSourceType must enumerate {list(PAYMENT_SOURCE_TYPES)}",
    )

    for list_path, tenant_parameter in (
        ("/api/v1/payments", "TenantHeader"),
        ("/internal/v1/payments", "TenantIdQuery"),
    ):
        path_item = paths.get(list_path) if isinstance(paths, dict) else None
        operation = path_item.get("get") if isinstance(path_item, dict) else None
        where = f"{relative}: GET {list_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required list operation is missing",
        )
        if not isinstance(operation, dict):
            continue

        parameter_refs = []
        for parameter in operation.get("parameters") or []:
            if isinstance(parameter, dict) and isinstance(parameter.get("$ref"), str):
                parameter_refs.append(parameter["$ref"].rsplit("/", 1)[-1])
        contracts.check(
            tenant_parameter in parameter_refs,
            f"{where}: must document the shared {tenant_parameter} parameter",
        )

        for name in PAYMENT_SOURCE_FILTER_PARAMETERS:
            parameter = _payment_filter_parameter(operation, name)
            contracts.check(
                parameter is not None,
                f"{where}: must declare the optional {name} filter parameter",
            )
            if parameter is None:
                continue
            contracts.check(
                parameter.get("in") == "query",
                f"{where}: {name} must be a query parameter",
            )
            contracts.check(
                parameter.get("required") is False,
                f"{where}: {name} must stay optional",
            )

        source_type_parameter = _payment_filter_parameter(operation, "sourceType") or {}
        contracts.check(
            str((source_type_parameter.get("schema") or {}).get("$ref", "")).endswith(
                "/schemas/PaymentSourceType"
            ),
            f"{where}: sourceType must reference PaymentSourceType",
        )
        source_id_parameter = _payment_filter_parameter(operation, "sourceId") or {}
        source_id_schema = source_id_parameter.get("schema") or {}
        contracts.check(
            source_id_schema.get("type") == "string"
            and source_id_schema.get("format") == "uuid",
            f"{where}: sourceId must be a uuid string",
        )

        description = str(operation.get("description") or "")
        for code in PAYMENT_SOURCE_FILTER_ERRORS:
            contracts.check(
                code in description,
                f"{where}: description must document 400 {code}",
            )
        contracts.check(
            "400" in (operation.get("responses") or {}),
            f"{where}: must document the 400 response",
        )


def check_payment_asyncapi_sources(contracts: ContractSet, document, relative: str):
    """Require the optional source fields on the created event payload."""
    channels = document.get("channels") or {}
    created = channels.get("PaymentPaymentCreated") or {}
    created_messages = created.get("messages") or {}
    contracts.check(
        (created_messages.get("PaymentPaymentCreatedData") or {}).get("$ref")
        == "#/components/messages/PaymentPaymentCreatedData",
        f"{relative}: PaymentPaymentCreated must reference PaymentPaymentCreatedData",
    )
    messages = (document.get("components") or {}).get("messages") or {}
    message = messages.get("PaymentPaymentCreatedData") or {}
    payload = message.get("payload") or {}
    properties = payload.get("properties") or {}
    required = set(payload.get("required") or [])
    for field in PAYMENT_SOURCE_FIELDS:
        contracts.check(
            field in properties,
            f"{relative}: PaymentPaymentCreatedData.payload.properties.{field} is required",
        )
        contracts.check(
            field not in required,
            f"{relative}: PaymentPaymentCreatedData.payload.{field} must stay optional",
        )
    contracts.check(
        _payment_source_type_values(properties.get("sourceType"), document)
        == set(PAYMENT_SOURCE_TYPES),
        f"{relative}: PaymentPaymentCreatedData.sourceType must enumerate "
        f"{list(PAYMENT_SOURCE_TYPES)}",
    )
    contracts.check(
        (properties.get("sourceId") or {}).get("format") == "uuid",
        f"{relative}: PaymentPaymentCreatedData.sourceId must be a uuid",
    )
    contracts.check(
        (properties.get("sourceReference") or {}).get("maxLength")
        == PAYMENT_SOURCE_REFERENCE_MAX_LENGTH,
        f"{relative}: PaymentPaymentCreatedData.sourceReference maxLength must be "
        f"{PAYMENT_SOURCE_REFERENCE_MAX_LENGTH}",
    )


# ---------------------------------------------------------------------------
# Payment allocation checks
# ---------------------------------------------------------------------------


def check_payment_allocations(contracts: ContractSet, document, relative: str):
    """Require the payment allocation routes, schemas, and conflict codes.

    The public GET/POST routes are mandatory. GET returns the
    ``PaymentAllocationSummary`` read model; POST returns the created
    ``PaymentAllocation`` and documents the two stable 409 guard codes. Both
    operations are tenant-scoped and not book-scoped, and the implemented path
    must not remain in ``x-planned-operations``.
    """
    schemas = (document.get("components") or {}).get("schemas") or {}

    allocation = schemas.get("PaymentAllocation") or {}
    allocation_properties = allocation.get("properties") or {}
    allocation_required = allocation.get("required") or []
    contracts.check(
        isinstance(allocation, dict) and allocation.get("type") == "object",
        f"{relative}: PaymentAllocation must be an object schema",
    )
    for field in PAYMENT_ALLOCATION_FIELDS:
        contracts.check(
            isinstance(allocation_properties.get(field), dict),
            f"{relative}: PaymentAllocation.{field} is required",
        )
        contracts.check(
            field in allocation_required,
            f"{relative}: PaymentAllocation.required must list {field}",
        )
    for field in ("allocationId", "paymentId", "targetId"):
        contracts.check(
            (allocation_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: PaymentAllocation.{field} must be a uuid",
        )
    contracts.check(
        str((allocation_properties.get("targetType") or {}).get("$ref", "")).endswith(
            "/schemas/PaymentAllocationTargetType"
        ),
        f"{relative}: PaymentAllocation.targetType must reference "
        "PaymentAllocationTargetType",
    )
    contracts.check(
        str((allocation_properties.get("component") or {}).get("$ref", "")).endswith(
            "/schemas/PaymentAllocationComponent"
        ),
        f"{relative}: PaymentAllocation.component must reference "
        "PaymentAllocationComponent",
    )
    contracts.check(
        str((allocation_properties.get("amount") or {}).get("$ref", "")).endswith(
            "/schemas/MoneyAmount"
        ),
        f"{relative}: PaymentAllocation.amount must use the shared MoneyAmount schema",
    )
    contracts.check(
        str((allocation_properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: PaymentAllocation.currency must use the shared CurrencyCode schema",
    )
    contracts.check(
        (allocation_properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: PaymentAllocation.createdAt must be a date-time",
    )
    reversed_at = allocation_properties.get("reversedAt") or {}
    contracts.check(
        _schema_types(reversed_at) == {"string", "null"}
        and reversed_at.get("format") == "date-time",
        f"{relative}: PaymentAllocation.reversedAt must be a nullable date-time",
    )
    reversal_reason = allocation_properties.get("reversalReason") or {}
    contracts.check(
        _schema_types(reversal_reason) == {"string", "null"}
        and reversal_reason.get("maxLength")
        == PAYMENT_ALLOCATION_REVERSAL_REASON_MAX_LENGTH,
        f"{relative}: PaymentAllocation.reversalReason must be a nullable string of "
        f"at most {PAYMENT_ALLOCATION_REVERSAL_REASON_MAX_LENGTH} characters",
    )

    for schema_name, expected in (
        ("PaymentAllocationTargetType", PAYMENT_ALLOCATION_TARGET_TYPES),
        ("PaymentAllocationComponent", PAYMENT_ALLOCATION_COMPONENTS),
    ):
        enum_schema = schemas.get(schema_name) or {}
        contracts.check(
            enum_schema.get("type") == "string",
            f"{relative}: {schema_name} must be a string enum",
        )
        contracts.check(
            set(enum_schema.get("enum") or []) == set(expected),
            f"{relative}: {schema_name} must enumerate {list(expected)}",
        )

    summary = schemas.get("PaymentAllocationSummary") or {}
    summary_properties = summary.get("properties") or {}
    summary_required = summary.get("required") or []
    contracts.check(
        isinstance(summary, dict) and summary.get("type") == "object",
        f"{relative}: PaymentAllocationSummary must be an object schema",
    )
    for field in PAYMENT_ALLOCATION_SUMMARY_FIELDS:
        contracts.check(
            isinstance(summary_properties.get(field), dict),
            f"{relative}: PaymentAllocationSummary.{field} is required",
        )
        contracts.check(
            field in summary_required,
            f"{relative}: PaymentAllocationSummary.required must list {field}",
        )
    summary_items = summary_properties.get("items") or {}
    contracts.check(
        summary_items.get("type") == "array"
        and str((summary_items.get("items") or {}).get("$ref", "")).endswith(
            "/schemas/PaymentAllocation"
        ),
        f"{relative}: PaymentAllocationSummary.items must be an array of PaymentAllocation",
    )
    for field in ("paymentAmount", "totalAllocated", "reversedTotal", "net", "unallocated"):
        contracts.check(
            str((summary_properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: PaymentAllocationSummary.{field} must use the shared "
            "MoneyAmount schema",
        )
    contracts.check(
        str((summary_properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: PaymentAllocationSummary.currency must use the shared "
        "CurrencyCode schema",
    )
    summary_description = str(summary.get("description") or "")
    contracts.check(
        "gross" in summary_description,
        f"{relative}: PaymentAllocationSummary must document the gross "
        "totalAllocated",
    )
    contracts.check(
        "net" in summary_description,
        f"{relative}: PaymentAllocationSummary must document the net allocated "
        "and unallocated figures",
    )
    contracts.check(
        "gross" in str((summary_properties.get("totalAllocated") or {}).get(
            "description", ""
        )).lower(),
        f"{relative}: PaymentAllocationSummary.totalAllocated must document the "
        "gross sum",
    )
    contracts.check(
        "net" in str((summary_properties.get("unallocated") or {}).get(
            "description", ""
        )).lower(),
        f"{relative}: PaymentAllocationSummary.unallocated must document the net "
        "basis",
    )

    request = schemas.get("CreatePaymentAllocationRequest") or {}
    request_properties = request.get("properties") or {}
    request_required = request.get("required") or []
    contracts.check(
        isinstance(request, dict) and request.get("type") == "object",
        f"{relative}: CreatePaymentAllocationRequest must be an object schema",
    )
    for field in PAYMENT_ALLOCATION_REQUEST_FIELDS:
        contracts.check(
            isinstance(request_properties.get(field), dict),
            f"{relative}: CreatePaymentAllocationRequest.{field} is required",
        )
        contracts.check(
            field in request_required,
            f"{relative}: CreatePaymentAllocationRequest.required must list {field}",
        )
    contracts.check(
        str((request_properties.get("targetType") or {}).get("$ref", "")).endswith(
            "/schemas/PaymentAllocationTargetType"
        ),
        f"{relative}: CreatePaymentAllocationRequest.targetType must reference "
        "PaymentAllocationTargetType",
    )
    contracts.check(
        (request_properties.get("targetId") or {}).get("format") == "uuid",
        f"{relative}: CreatePaymentAllocationRequest.targetId must be a uuid",
    )
    contracts.check(
        str((request_properties.get("component") or {}).get("$ref", "")).endswith(
            "/schemas/PaymentAllocationComponent"
        ),
        f"{relative}: CreatePaymentAllocationRequest.component must reference "
        "PaymentAllocationComponent",
    )
    request_amount = request_properties.get("amount") or {}
    contracts.check(
        str(request_amount.get("$ref", "")).endswith("/schemas/MoneyAmount"),
        f"{relative}: CreatePaymentAllocationRequest.amount must use the shared "
        "MoneyAmount schema",
    )
    contracts.check(
        "greater than zero" in str(request_amount.get("description") or "").lower(),
        f"{relative}: CreatePaymentAllocationRequest.amount must document the "
        "greater-than-zero rule",
    )

    paths = document.get("paths") or {}
    for method, path, success_status, success_schema, request_schema in (
        PAYMENT_ALLOCATION_OPENAPI_PATHS
    ):
        path_item = paths.get(path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required payment allocation operation is missing",
        )
        if not isinstance(operation, dict):
            continue
        parameter_refs, inline_names = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must document the shared TenantHeader parameter",
        )
        contracts.check(
            "paymentId" in inline_names,
            f"{where}: must declare the paymentId path parameter",
        )
        contracts.check(
            not ({"BookHeaderDirect", "BookHeaderAssumed"} & set(parameter_refs)),
            f"{where}: payment allocations are not book-scoped and must not "
            "declare a book header",
        )
        description = str(operation.get("description") or "")
        contracts.check(
            "PAYMENT_NOT_FOUND" in description,
            f"{where}: description must document 404 PAYMENT_NOT_FOUND",
        )
        contracts.check(
            "MISSING_TENANT_HEADER" in description,
            f"{where}: description must document 400 MISSING_TENANT_HEADER",
        )
        if request_schema:
            request_body = operation.get("requestBody") or {}
            body_schema = (
                ((request_body.get("content") or {}).get("application/json") or {})
                .get("schema")
                if isinstance(request_body, dict)
                else None
            )
            contracts.check(
                isinstance(request_body, dict)
                and request_body.get("required") is True,
                f"{where}: requestBody must be required",
            )
            contracts.check(
                isinstance(body_schema, dict)
                and str(body_schema.get("$ref", "")).endswith(
                    f"/schemas/{request_schema}"
                ),
                f"{where}: request body must use the {request_schema} schema",
            )
            contracts.check(
                "VALIDATION_ERROR" in description,
                f"{where}: description must document 400 VALIDATION_ERROR",
            )
            for code in PAYMENT_ALLOCATION_CONFLICT_CODES:
                contracts.check(
                    code in description,
                    f"{where}: description must document 409 {code}",
                )
            contracts.check(
                PAYMENT_ALLOCATION_EVENT in description,
                f"{where}: description must document the "
                f"{PAYMENT_ALLOCATION_EVENT} event",
            )
        responses = operation.get("responses") or {}
        success_body = _response_schema(operation, success_status)
        contracts.check(
            isinstance(success_body, dict)
            and str(success_body.get("$ref", "")).endswith(f"/schemas/{success_schema}"),
            f"{where}: {success_status} must return the {success_schema} schema",
        )
        for code, suffix in (
            ("400", "/responses/BadRequest"),
            ("404", "/responses/NotFound"),
        ):
            response = responses.get(code) if isinstance(responses, dict) else None
            contracts.check(
                isinstance(response, dict)
                and str(response.get("$ref", "")).endswith(suffix),
                f"{where}: {code} must reference the shared {suffix.rsplit('/', 1)[-1]} "
                "response",
            )
        if request_schema:
            conflict = responses.get("409") if isinstance(responses, dict) else None
            contracts.check(
                isinstance(conflict, dict)
                and str(conflict.get("$ref", "")).endswith("/responses/Conflict"),
                f"{where}: 409 must reference the shared Conflict response",
            )

    planned = document.get("x-planned-operations") or []
    contracts.check(
        not any(
            isinstance(entry, dict)
            and entry.get("path") == "/api/v1/payments/{paymentId}/allocations"
            for entry in planned
        ),
        f"{relative}: x-planned-operations must not list the implemented payment "
        "allocations path",
    )


def check_payment_allocation_reversal(contracts: ContractSet, document, relative: str):
    """Require the public allocation-reversal route, request, and error codes.

    The reversal is a stamp on the append-only allocation. The operation must
    document the required 200-character reason, the 200 ``PaymentAllocation``
    response, both tenant-scoped 404 codes, the 400 validation and tenant
    errors, the ``ALLOCATION_ALREADY_REVERSED`` conflict, and the
    ``payment.allocation.reversed`` event. The implemented path must not remain
    in ``x-planned-operations``.
    """
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}
    path = PAYMENT_ALLOCATION_REVERSE_OPENAPI_PATH
    path_item = paths.get(path) if isinstance(paths, dict) else None
    operation = path_item.get("post") if isinstance(path_item, dict) else None
    where = f"{relative}: POST {path}"
    contracts.check(
        isinstance(operation, dict),
        f"{where}: required payment allocation reversal operation is missing",
    )
    if not isinstance(operation, dict):
        return
    parameter_refs, inline_names = _parameter_names(operation)
    contracts.check(
        "TenantHeader" in parameter_refs,
        f"{where}: must document the shared TenantHeader parameter",
    )
    for name in ("paymentId", "allocationId"):
        contracts.check(
            name in inline_names,
            f"{where}: must declare the {name} path parameter",
        )
    contracts.check(
        not ({"BookHeaderDirect", "BookHeaderAssumed"} & set(parameter_refs)),
        f"{where}: payment allocations are not book-scoped and must not "
        "declare a book header",
    )
    description = str(operation.get("description") or "")
    for code in PAYMENT_ALLOCATION_NOT_FOUND_CODES:
        contracts.check(
            code in description,
            f"{where}: description must document 404 {code}",
        )
    for code in ("VALIDATION_ERROR", "MISSING_TENANT_HEADER"):
        contracts.check(
            code in description,
            f"{where}: description must document 400 {code}",
        )
    for code in PAYMENT_ALLOCATION_REVERSE_CONFLICT_CODES:
        contracts.check(
            code in description,
            f"{where}: description must document 409 {code}",
        )
    contracts.check(
        PAYMENT_ALLOCATION_REVERSE_EVENT in description,
        f"{where}: description must document the "
        f"{PAYMENT_ALLOCATION_REVERSE_EVENT} event",
    )
    contracts.check(
        "trim" in description.lower(),
        f"{where}: description must document the trimmed reversal reason",
    )

    request_body = operation.get("requestBody") or {}
    body_schema = (
        ((request_body.get("content") or {}).get("application/json") or {}).get(
            "schema"
        )
        if isinstance(request_body, dict)
        else None
    )
    contracts.check(
        isinstance(request_body, dict) and request_body.get("required") is True,
        f"{where}: requestBody must be required",
    )
    contracts.check(
        isinstance(body_schema, dict)
        and str(body_schema.get("$ref", "")).endswith(
            "/schemas/ReversePaymentAllocationRequest"
        ),
        f"{where}: request body must use the ReversePaymentAllocationRequest "
        "schema",
    )

    request = schemas.get("ReversePaymentAllocationRequest") or {}
    request_properties = request.get("properties") or {}
    request_required = request.get("required") or []
    contracts.check(
        isinstance(request, dict) and request.get("type") == "object",
        f"{relative}: ReversePaymentAllocationRequest must be an object schema",
    )
    for field in PAYMENT_ALLOCATION_REVERSE_REQUEST_FIELDS:
        contracts.check(
            isinstance(request_properties.get(field), dict),
            f"{relative}: ReversePaymentAllocationRequest.{field} is required",
        )
        contracts.check(
            field in request_required,
            f"{relative}: ReversePaymentAllocationRequest.required must list {field}",
        )
    reason = request_properties.get("reason") or {}
    contracts.check(
        reason.get("type") == "string",
        f"{relative}: ReversePaymentAllocationRequest.reason must be a string",
    )
    contracts.check(
        reason.get("maxLength") == PAYMENT_ALLOCATION_REVERSAL_REASON_MAX_LENGTH,
        f"{relative}: ReversePaymentAllocationRequest.reason maxLength must be "
        f"{PAYMENT_ALLOCATION_REVERSAL_REASON_MAX_LENGTH}",
    )
    contracts.check(
        reason.get("minLength") == 1,
        f"{relative}: ReversePaymentAllocationRequest.reason must be non-empty",
    )
    contracts.check(
        "trim" in str(reason.get("description") or "").lower(),
        f"{relative}: ReversePaymentAllocationRequest.reason must document the "
        "trim rule",
    )

    success_body = _response_schema(operation, "200")
    contracts.check(
        isinstance(success_body, dict)
        and str(success_body.get("$ref", "")).endswith("/schemas/PaymentAllocation"),
        f"{where}: 200 must return the PaymentAllocation schema",
    )
    responses = operation.get("responses") or {}
    for code, suffix in (
        ("400", "/responses/BadRequest"),
        ("404", "/responses/NotFound"),
        ("409", "/responses/Conflict"),
    ):
        response = responses.get(code) if isinstance(responses, dict) else None
        contracts.check(
            isinstance(response, dict)
            and str(response.get("$ref", "")).endswith(suffix),
            f"{where}: {code} must reference the shared "
            f"{suffix.rsplit('/', 1)[-1]} response",
        )

    planned = document.get("x-planned-operations") or []
    contracts.check(
        not any(
            isinstance(entry, dict) and entry.get("path") == path
            for entry in planned
        ),
        f"{relative}: x-planned-operations must not list the implemented payment "
        "allocation reversal path",
    )


def check_payment_status(contracts: ContractSet, document, relative: str):
    """Require the public payment status route, request schema, and graph.

    The public PATCH operation is mandatory and returns the updated ``Payment``.
    The contract must document every edge of the implemented expert graph, all
    terminal statuses, the approval gate, and the optional ``expectedVersion``
    and ``reason`` semantics. The public request and the internal command must
    describe the same wire shape because the domain forwards the public body
    unchanged.
    """
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    status_schema = schemas.get("PaymentStatus") or {}
    contracts.check(
        status_schema.get("type") == "string",
        f"{relative}: PaymentStatus must be a string enum",
    )
    contracts.check(
        set(status_schema.get("enum") or []) == set(PAYMENT_STATUSES),
        f"{relative}: PaymentStatus must enumerate {list(PAYMENT_STATUSES)}",
    )
    status_description = str(status_schema.get("description") or "")
    contracts.check(
        "terminal" in status_description,
        f"{relative}: PaymentStatus must document the terminal statuses",
    )
    for terminal in PAYMENT_TERMINAL_STATUSES:
        contracts.check(
            terminal in status_description,
            f"{relative}: PaymentStatus must name the terminal {terminal} status",
        )

    # The status reason is part of the Payment projection: it is always
    # serialized, null when the latest change carried no reason, and capped at
    # the payment.status_reason column width.
    payment_schema = schemas.get("Payment") or {}
    payment_properties = payment_schema.get("properties") or {}
    payment_required = set(payment_schema.get("required") or [])
    contracts.check(
        isinstance(payment_properties.get("statusReason"), dict),
        f"{relative}: Payment.statusReason is required",
    )
    contracts.check(
        "statusReason" in payment_required,
        f"{relative}: Payment.required must list statusReason",
    )
    payment_status_reason = payment_properties.get("statusReason") or {}
    contracts.check(
        _schema_types(payment_status_reason) == {"string", "null"}
        and payment_status_reason.get("maxLength")
        == PAYMENT_STATUS_REASON_MAX_LENGTH,
        f"{relative}: Payment.statusReason must be a required-but-nullable "
        f"string capped at {PAYMENT_STATUS_REASON_MAX_LENGTH} characters",
    )
    payment_status_reason_description = str(
        payment_status_reason.get("description") or ""
    ).lower()
    for term in ("latest", "trimmed", "clears"):
        contracts.check(
            term in payment_status_reason_description,
            f"{relative}: Payment.statusReason description must document {term}",
        )

    # The transition table is the machine-checkable form of the graph: a
    # terminal status has no outgoing edge and every other status has at least
    # one.
    contracts.check(
        set(PAYMENT_STATUS_TRANSITIONS) == set(PAYMENT_STATUSES),
        f"{relative}: the transition table must cover every PaymentStatus",
    )
    contracts.check(
        set(PAYMENT_PRE_APPROVAL_STATUSES) <= set(PAYMENT_STATUSES)
        and set(PAYMENT_EXECUTION_STATUSES) <= set(PAYMENT_STATUSES),
        f"{relative}: the approval-gate status sets must be PaymentStatus values",
    )
    for status, targets in PAYMENT_STATUS_TRANSITIONS.items():
        edge_where = f"{relative}: PaymentStatus transition"
        contracts.check(
            status in PAYMENT_STATUSES,
            f"{edge_where} source {status} is not a PaymentStatus",
        )
        for target in targets:
            contracts.check(
                target in PAYMENT_STATUSES,
                f"{edge_where} target {target} is not a PaymentStatus",
            )
    for source in PAYMENT_PRE_APPROVAL_STATUSES:
        contracts.check(
            not (
                set(PAYMENT_STATUS_TRANSITIONS[source])
                & set(PAYMENT_EXECUTION_STATUSES)
            ),
            f"{relative}: a pre-approval status must not have a direct execution "
            "edge",
        )
    contracts.check(
        {
            status
            for status, targets in PAYMENT_STATUS_TRANSITIONS.items()
            if not targets
        }
        == set(PAYMENT_TERMINAL_STATUSES),
        f"{relative}: terminal statuses must match the statuses without an "
        "outgoing transition",
    )

    path_item = (
        paths.get(PAYMENT_STATUS_OPENAPI_PATH) if isinstance(paths, dict) else None
    )
    operation = path_item.get("patch") if isinstance(path_item, dict) else None
    where = f"{relative}: PATCH {PAYMENT_STATUS_OPENAPI_PATH}"
    contracts.check(
        isinstance(operation, dict),
        f"{where}: required payment status operation is missing",
    )
    if not isinstance(operation, dict):
        return

    parameter_refs, inline_names = _parameter_names(operation)
    contracts.check(
        "TenantHeader" in parameter_refs,
        f"{where}: must document the shared TenantHeader parameter",
    )
    contracts.check(
        "paymentId" in inline_names,
        f"{where}: must declare the paymentId path parameter",
    )
    contracts.check(
        not ({"BookHeaderDirect", "BookHeaderAssumed"} & set(parameter_refs)),
        f"{where}: payments are not book-scoped and must not declare a book header",
    )

    request_body = operation.get("requestBody") or {}
    body_schema = (
        ((request_body.get("content") or {}).get("application/json") or {}).get(
            "schema"
        )
        if isinstance(request_body, dict)
        else None
    )
    contracts.check(
        isinstance(request_body, dict) and request_body.get("required") is True,
        f"{where}: requestBody must be required",
    )
    contracts.check(
        isinstance(body_schema, dict)
        and str(body_schema.get("$ref", "")).endswith(
            f"/schemas/{PAYMENT_STATUS_REQUEST_SCHEMA}"
        ),
        f"{where}: request body must use the {PAYMENT_STATUS_REQUEST_SCHEMA} schema",
    )

    success_body = _response_schema(operation, "200")
    contracts.check(
        isinstance(success_body, dict)
        and str(success_body.get("$ref", "")).endswith("/schemas/Payment"),
        f"{where}: 200 must return the Payment schema",
    )
    responses = operation.get("responses") or {}
    for code, suffix in (
        ("400", "/responses/BadRequest"),
        ("404", "/responses/NotFound"),
        ("409", "/responses/Conflict"),
    ):
        response = responses.get(code) if isinstance(responses, dict) else None
        contracts.check(
            isinstance(response, dict)
            and str(response.get("$ref", "")).endswith(suffix),
            f"{where}: {code} must reference the shared {suffix.rsplit('/', 1)[-1]} "
            "response",
        )

    description = str(operation.get("description") or "")
    for source, targets in PAYMENT_STATUS_TRANSITIONS.items():
        for target in targets:
            edge = f"`{source}` -> `{target}`"
            contracts.check(
                edge in description,
                f"{where}: description must document the {edge} transition",
            )
    contracts.check(
        "are terminal" in description,
        f"{where}: description must state which statuses are terminal",
    )
    contracts.check(
        "is not terminal" in description,
        f"{where}: description must state that PARTIALLY_PAID is not terminal",
    )
    for code in PAYMENT_STATUS_ERROR_CODES:
        contracts.check(
            code in description,
            f"{where}: description must document the {code} error code",
        )
    for event in PAYMENT_STATUS_EVENTS:
        contracts.check(
            event in description,
            f"{where}: description must document the {event} event",
        )
    for term in ("expectedVersion", "reason", "approval gate"):
        contracts.check(
            term in description,
            f"{where}: description must document {term}",
        )
    contracts.check(
        "statusReason" in description,
        f"{where}: description must document the returned statusReason",
    )
    contracts.check(
        "not returned" not in description,
        f"{where}: description must not claim the status reason is not returned",
    )

    # The public request and the internal command must describe the same wire
    # shape: only status is required, status is the shared PaymentStatus enum,
    # expectedVersion is a non-negative integer, and reason is capped at 200.
    for schema_name in (
        PAYMENT_STATUS_REQUEST_SCHEMA,
        PAYMENT_STATUS_REQUEST_INTERNAL_SCHEMA,
    ):
        request = schemas.get(schema_name) or {}
        properties = request.get("properties") or {}
        request_required = set(request.get("required") or [])
        contracts.check(
            isinstance(request, dict) and request.get("type") == "object",
            f"{relative}: {schema_name} must be an object schema",
        )
        contracts.check(
            request_required == {"status"},
            f"{relative}: {schema_name} must require only status",
        )
        status = properties.get("status") or {}
        contracts.check(
            str(status.get("$ref", "")).endswith("/schemas/PaymentStatus"),
            f"{relative}: {schema_name}.status must reference PaymentStatus",
        )
        expected_version = properties.get("expectedVersion") or {}
        contracts.check(
            expected_version.get("type") == "integer"
            and expected_version.get("minimum") == 0,
            f"{relative}: {schema_name}.expectedVersion must be an integer with "
            "minimum 0",
        )
        reason = properties.get("reason") or {}
        contracts.check(
            reason.get("type") == "string"
            and reason.get("maxLength") == PAYMENT_STATUS_REASON_MAX_LENGTH,
            f"{relative}: {schema_name}.reason must be a string capped at "
            f"{PAYMENT_STATUS_REASON_MAX_LENGTH} characters",
        )
        contracts.check(
            "expectedVersion" not in request_required,
            f"{relative}: {schema_name}.expectedVersion must stay optional",
        )
        contracts.check(
            "reason" not in request_required,
            f"{relative}: {schema_name}.reason must stay optional",
        )

    planned = document.get("x-planned-operations") or []
    contracts.check(
        not any(
            isinstance(entry, dict)
            and entry.get("path") == PAYMENT_STATUS_OPENAPI_PATH
            for entry in planned
        ),
        f"{relative}: x-planned-operations must not list the implemented payment "
        "status path",
    )


def check_payment_allocation_asyncapi(contracts: ContractSet, document, relative: str):
    """Require the implemented payment.allocation.created channel and payload."""
    channels = document.get("channels") or {}
    channel = channels.get("PaymentAllocationCreated") or {}
    contracts.check(
        channel.get("address") == PAYMENT_ALLOCATION_EVENT,
        f"{relative}: payment allocation channel must address "
        f"{PAYMENT_ALLOCATION_EVENT}",
    )
    contracts.check(
        channel.get("x-status") == "implemented",
        f"{relative}: {PAYMENT_ALLOCATION_EVENT} channel must be implemented",
    )
    contracts.check(
        bool(channel.get("x-implemented-by")),
        f"{relative}: {PAYMENT_ALLOCATION_EVENT} must name the emitting source",
    )
    messages = channel.get("messages") or {}
    contracts.check(
        (messages.get("PaymentAllocationCreatedData") or {}).get("$ref")
        == "#/components/messages/PaymentAllocationCreatedData",
        f"{relative}: {PAYMENT_ALLOCATION_EVENT} must reference "
        "PaymentAllocationCreatedData",
    )
    send_events = {
        operation.get("x-event-type")
        for operation in (document.get("operations") or {}).values()
        if isinstance(operation, dict) and operation.get("action") == "send"
    }
    contracts.check(
        PAYMENT_ALLOCATION_EVENT in send_events,
        f"{relative}: {PAYMENT_ALLOCATION_EVENT} must have a send operation",
    )
    message = (
        ((document.get("components") or {}).get("messages") or {}).get(
            "PaymentAllocationCreatedData"
        )
        or {}
    )
    payload = message.get("payload") or {}
    properties = payload.get("properties") or {}
    required = set(payload.get("required") or [])
    for field in PAYMENT_ALLOCATION_EVENT_FIELDS:
        contracts.check(
            field in properties,
            f"{relative}: PaymentAllocationCreatedData.properties.{field} "
            "is required",
        )
        contracts.check(
            field in required,
            f"{relative}: PaymentAllocationCreatedData.required must list {field}",
        )
    contracts.check(
        set((properties.get("targetType") or {}).get("enum") or [])
        == set(PAYMENT_ALLOCATION_TARGET_TYPES),
        f"{relative}: PaymentAllocationCreatedData.targetType must enumerate "
        f"{list(PAYMENT_ALLOCATION_TARGET_TYPES)}",
    )
    contracts.check(
        set((properties.get("component") or {}).get("enum") or [])
        == set(PAYMENT_ALLOCATION_COMPONENTS),
        f"{relative}: PaymentAllocationCreatedData.component must enumerate "
        f"{list(PAYMENT_ALLOCATION_COMPONENTS)}",
    )
    contracts.check(
        (properties.get("currency") or {}).get("pattern") == "^[A-Z]{3}$",
        f"{relative}: PaymentAllocationCreatedData.currency must be an ISO 4217 code",
    )


def check_payment_allocation_reversed_asyncapi(
    contracts: ContractSet, document, relative: str
):
    """Require the implemented payment.allocation.reversed channel and payload."""
    channels = document.get("channels") or {}
    channel = channels.get("PaymentAllocationReversed") or {}
    contracts.check(
        channel.get("address") == PAYMENT_ALLOCATION_REVERSE_EVENT,
        f"{relative}: payment allocation reversal channel must address "
        f"{PAYMENT_ALLOCATION_REVERSE_EVENT}",
    )
    contracts.check(
        channel.get("x-status") == "implemented",
        f"{relative}: {PAYMENT_ALLOCATION_REVERSE_EVENT} channel must be "
        "implemented",
    )
    contracts.check(
        bool(channel.get("x-implemented-by")),
        f"{relative}: {PAYMENT_ALLOCATION_REVERSE_EVENT} must name the emitting "
        "source",
    )
    messages = channel.get("messages") or {}
    contracts.check(
        (messages.get("PaymentAllocationReversedData") or {}).get("$ref")
        == "#/components/messages/PaymentAllocationReversedData",
        f"{relative}: {PAYMENT_ALLOCATION_REVERSE_EVENT} must reference "
        "PaymentAllocationReversedData",
    )
    send_events = {
        operation.get("x-event-type")
        for operation in (document.get("operations") or {}).values()
        if isinstance(operation, dict) and operation.get("action") == "send"
    }
    contracts.check(
        PAYMENT_ALLOCATION_REVERSE_EVENT in send_events,
        f"{relative}: {PAYMENT_ALLOCATION_REVERSE_EVENT} must have a send "
        "operation",
    )
    message = (
        ((document.get("components") or {}).get("messages") or {}).get(
            "PaymentAllocationReversedData"
        )
        or {}
    )
    payload = message.get("payload") or {}
    properties = payload.get("properties") or {}
    required = set(payload.get("required") or [])
    for field in PAYMENT_ALLOCATION_REVERSE_EVENT_FIELDS:
        contracts.check(
            field in properties,
            f"{relative}: PaymentAllocationReversedData.properties.{field} "
            "is required",
        )
        contracts.check(
            field in required,
            f"{relative}: PaymentAllocationReversedData.required must list {field}",
        )
    contracts.check(
        set((properties.get("targetType") or {}).get("enum") or [])
        == set(PAYMENT_ALLOCATION_TARGET_TYPES),
        f"{relative}: PaymentAllocationReversedData.targetType must enumerate "
        f"{list(PAYMENT_ALLOCATION_TARGET_TYPES)}",
    )
    contracts.check(
        set((properties.get("component") or {}).get("enum") or [])
        == set(PAYMENT_ALLOCATION_COMPONENTS),
        f"{relative}: PaymentAllocationReversedData.component must enumerate "
        f"{list(PAYMENT_ALLOCATION_COMPONENTS)}",
    )
    reason = properties.get("reason") or {}
    contracts.check(
        reason.get("maxLength") == PAYMENT_ALLOCATION_REVERSAL_REASON_MAX_LENGTH,
        f"{relative}: PaymentAllocationReversedData.reason maxLength must be "
        f"{PAYMENT_ALLOCATION_REVERSAL_REASON_MAX_LENGTH}",
    )
    contracts.check(
        (properties.get("reversedAt") or {}).get("format") == "date-time",
        f"{relative}: PaymentAllocationReversedData.reversedAt must be a "
        "date-time",
    )


# ---------------------------------------------------------------------------
# Document association-link checks
# ---------------------------------------------------------------------------


def _link_parameters(operation):
    """Return (referenced parameter names, inline parameter names)."""
    references = []
    names = []
    for parameter in operation.get("parameters") or []:
        if not isinstance(parameter, dict):
            continue
        reference = parameter.get("$ref")
        if isinstance(reference, str):
            references.append(reference.rsplit("/", 1)[-1])
        if isinstance(parameter.get("name"), str):
            names.append(parameter["name"])
    return references, names


def _link_parameter_schema(operation, name):
    for parameter in operation.get("parameters") or []:
        if isinstance(parameter, dict) and parameter.get("name") == name:
            return parameter.get("schema") or {}
    return {}


def _link_response_schema(operation, status, media_type):
    response = (operation.get("responses") or {}).get(status)
    if not isinstance(response, dict):
        return None
    return ((response.get("content") or {}).get(media_type) or {}).get("schema")


def check_document_links_openapi(contracts: ContractSet, document, relative: str):
    """Require the document association-link operations, schemas, and filters."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    for link_path, link_method in DOCUMENT_LINK_OPENAPI_PATHS:
        path_item = paths.get(link_path) if isinstance(paths, dict) else None
        operation = path_item.get(link_method) if isinstance(path_item, dict) else None
        where = f"{relative}: {link_method.upper()} {link_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required document-link operation is missing",
        )
        if not isinstance(operation, dict):
            continue
        parameter_refs, inline_names = _link_parameters(operation)
        tenant_parameter = (
            "TenantHeader" if link_path.startswith("/api/v1/") else "TenantIdQuery"
        )
        contracts.check(
            tenant_parameter in parameter_refs,
            f"{where}: must document the shared {tenant_parameter} parameter",
        )
        contracts.check(
            "documentId" in inline_names,
            f"{where}: must declare the documentId path parameter",
        )
        if link_path.endswith("/{linkId}"):
            contracts.check(
                "linkId" in inline_names,
                f"{where}: must declare the linkId path parameter",
            )

        responses = operation.get("responses") or {}
        contracts.check("400" in responses, f"{where}: must document the 400 response")
        contracts.check("404" in responses, f"{where}: must document the 404 response")
        if link_method == "get":
            ok_schema = _link_response_schema(operation, "200", "application/json")
            contracts.check(
                isinstance(ok_schema, dict)
                and ok_schema.get("type") == "array"
                and str((ok_schema.get("items") or {}).get("$ref", "")).endswith(
                    "/schemas/DocumentLink"
                ),
                f"{where}: 200 must return an array of DocumentLink",
            )
        elif link_method == "post":
            request_schema = (
                ((operation.get("requestBody") or {}).get("content") or {})
                .get("application/json", {})
                .get("schema")
            )
            contracts.check(
                isinstance(request_schema, dict)
                and str(request_schema.get("$ref", "")).endswith(
                    "/schemas/CreateDocumentLinkRequest"
                ),
                f"{where}: request body must use the CreateDocumentLinkRequest schema",
            )
            created_schema = _link_response_schema(operation, "201", "application/json")
            contracts.check(
                isinstance(created_schema, dict)
                and str(created_schema.get("$ref", "")).endswith("/schemas/DocumentLink"),
                f"{where}: 201 must return the DocumentLink schema",
            )
            conflict = responses.get("409")
            conflict_text = (
                str(conflict.get("description") or "") if isinstance(conflict, dict) else ""
            )
            contracts.check(
                "DUPLICATE_LINK" in conflict_text,
                f"{where}: 409 must document DUPLICATE_LINK",
            )
            conflict_schema = _link_response_schema(
                operation, "409", "application/problem+json"
            )
            contracts.check(
                isinstance(conflict_schema, dict)
                and str(conflict_schema.get("$ref", "")).endswith("/schemas/Problem"),
                f"{where}: 409 must document the shared Problem schema",
            )
        else:
            contracts.check(
                "204" in responses,
                f"{where}: must document the 204 no-content response",
            )

    linked_type = schemas.get("DocumentLinkedType") or {}
    contracts.check(
        linked_type.get("type") == "string",
        f"{relative}: DocumentLinkedType must be a string enum",
    )
    contracts.check(
        set(linked_type.get("enum") or []) == set(DOCUMENT_LINKED_TYPES),
        f"{relative}: DocumentLinkedType must enumerate {list(DOCUMENT_LINKED_TYPES)}",
    )

    link = schemas.get("DocumentLink") or {}
    link_properties = link.get("properties") or {}
    link_required = set(link.get("required") or [])
    for field in (
        "id",
        "documentId",
        "linkedType",
        "linkedId",
        "linkedReference",
        "linkedLabel",
        "createdAt",
    ):
        contracts.check(
            field in link_properties,
            f"{relative}: DocumentLink.properties.{field} is required",
        )
    for field in ("id", "documentId", "linkedType", "linkedId", "linkedLabel", "createdAt"):
        contracts.check(
            field in link_required,
            f"{relative}: DocumentLink.required must list {field}",
        )
    contracts.check(
        "linkedReference" not in link_required,
        f"{relative}: DocumentLink.linkedReference must stay optional",
    )
    contracts.check(
        str((link_properties.get("linkedType") or {}).get("$ref", "")).endswith(
            "/schemas/DocumentLinkedType"
        ),
        f"{relative}: DocumentLink.linkedType must reference DocumentLinkedType",
    )
    for field in ("id", "documentId", "linkedId"):
        contracts.check(
            (link_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: DocumentLink.{field} must be a uuid",
        )
    reference = link_properties.get("linkedReference") or {}
    contracts.check(
        _schema_types(reference) == {"string", "null"}
        and reference.get("maxLength") == DOCUMENT_LINK_REFERENCE_MAX_LENGTH,
        f"{relative}: DocumentLink.linkedReference must be a nullable string of at most "
        f"{DOCUMENT_LINK_REFERENCE_MAX_LENGTH} characters",
    )
    contracts.check(
        (link_properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: DocumentLink.createdAt must be a date-time",
    )

    request = schemas.get("CreateDocumentLinkRequest") or {}
    request_properties = request.get("properties") or {}
    request_required = set(request.get("required") or [])
    contracts.check(
        {"linkedType", "linkedId"} <= request_required,
        f"{relative}: CreateDocumentLinkRequest must require linkedType and linkedId",
    )
    contracts.check(
        "linkedReference" not in request_required,
        f"{relative}: CreateDocumentLinkRequest.linkedReference must stay optional",
    )
    for field in ("linkedType", "linkedId", "linkedReference"):
        contracts.check(
            field in request_properties,
            f"{relative}: CreateDocumentLinkRequest.properties.{field} is required",
        )
    contracts.check(
        str((request_properties.get("linkedType") or {}).get("$ref", "")).endswith(
            "/schemas/DocumentLinkedType"
        ),
        f"{relative}: CreateDocumentLinkRequest.linkedType must reference DocumentLinkedType",
    )
    contracts.check(
        (request_properties.get("linkedId") or {}).get("format") == "uuid",
        f"{relative}: CreateDocumentLinkRequest.linkedId must be a uuid",
    )
    contracts.check(
        (request_properties.get("linkedReference") or {}).get("maxLength")
        == DOCUMENT_LINK_REFERENCE_MAX_LENGTH,
        f"{relative}: CreateDocumentLinkRequest.linkedReference maxLength must be "
        f"{DOCUMENT_LINK_REFERENCE_MAX_LENGTH}",
    )

    # The document list takes the optional linkedType + linkedId pair, the
    # expert list takes the same pair plus q, and the public search documents
    # that q matches a link's linkedReference.
    list_path_item = paths.get("/api/v1/documents") if isinstance(paths, dict) else None
    list_operation = list_path_item.get("get") if isinstance(list_path_item, dict) else None
    _, list_names = _link_parameters(list_operation or {})
    contracts.check(
        "linkedType" in list_names and "linkedId" in list_names,
        f"{relative}: GET /api/v1/documents must declare the linkedType and linkedId filter parameters",
    )
    contracts.check(
        str(_link_parameter_schema(list_operation or {}, "linkedType").get("$ref", "")).endswith(
            "/schemas/DocumentLinkedType"
        ),
        f"{relative}: GET /api/v1/documents linkedType must reference DocumentLinkedType",
    )
    contracts.check(
        _link_parameter_schema(list_operation or {}, "linkedId").get("format") == "uuid",
        f"{relative}: GET /api/v1/documents linkedId must be a uuid",
    )

    expert_list_path_item = (
        paths.get("/internal/v1/documents") if isinstance(paths, dict) else None
    )
    expert_list = (
        expert_list_path_item.get("get")
        if isinstance(expert_list_path_item, dict)
        else None
    )
    _, expert_list_names = _link_parameters(expert_list or {})
    contracts.check(
        {"linkedType", "linkedId", "q"} <= set(expert_list_names),
        f"{relative}: the expert document list must declare linkedType, linkedId, and q",
    )

    search_path_item = (
        paths.get("/api/v1/documents/search") if isinstance(paths, dict) else None
    )
    search_operation = (
        search_path_item.get("get") if isinstance(search_path_item, dict) else None
    )
    contracts.check(
        "linkedReference" in str((search_operation or {}).get("description") or ""),
        f"{relative}: GET /api/v1/documents/search must document that q matches linkedReference",
    )


# ---------------------------------------------------------------------------
# Document content checks
# ---------------------------------------------------------------------------


def check_document_content_openapi(contracts: ContractSet, document, relative: str):
    """Require the document content operations, headers, schema, and errors."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    for method, content_path, operation_id in (
        ("put", DOCUMENT_CONTENT_PATH, "uploadDocumentContent"),
        ("get", DOCUMENT_CONTENT_PATH, "downloadDocumentContent"),
        ("delete", DOCUMENT_CONTENT_PATH, "deleteDocumentContent"),
        ("get", DOCUMENT_CONTENT_METADATA_PATH, "getDocumentContentMetadata"),
        ("get", DOCUMENT_CONTENT_VERSIONS_PATH, "listDocumentContentVersions"),
        ("get", DOCUMENT_CONTENT_VERSION_PATH, "downloadDocumentContentVersion"),
    ):
        path_item = paths.get(content_path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {content_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required content operation is missing",
        )
        if not isinstance(operation, dict):
            continue
        contracts.check(
            operation.get("operationId") == operation_id,
            f"{where}: operationId must be {operation_id}",
        )
        parameter_refs, inline_names = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must require the shared TenantHeader",
        )
        contracts.check(
            "documentId" in inline_names,
            f"{where}: must declare the documentId path parameter",
        )
        responses = operation.get("responses") or {}
        contracts.check("400" in responses, f"{where}: must document the 400 response")
        contracts.check("404" in responses, f"{where}: must document the 404 response")

        if method == "put":
            contracts.check(
                operation.get("x-raw-body") is True,
                f"{where}: must be marked x-raw-body: true",
            )
            request_body = operation.get("requestBody") or {}
            contracts.check(
                request_body.get("required") is True,
                f"{where}: request body must be required",
            )
            request_content = request_body.get("content") or {}
            binary_schema = None
            for media_type, media_object in request_content.items():
                if media_type in ("*/*", "application/octet-stream") and isinstance(
                    media_object, dict
                ):
                    binary_schema = media_object.get("schema")
            contracts.check(
                isinstance(binary_schema, dict)
                and binary_schema.get("type") == "string"
                and binary_schema.get("format") == "binary",
                f"{where}: requestBody must declare a binary string body",
            )
            content_type_parameter = _inline_parameter(operation, "Content-Type")
            contracts.check(
                isinstance(content_type_parameter, dict)
                and content_type_parameter.get("in") == "header",
                f"{where}: must document the Content-Type header parameter",
            )
            if isinstance(content_type_parameter, dict):
                contracts.check(
                    content_type_parameter.get("required") is False,
                    f"{where}: Content-Type must stay optional and default to "
                    "application/octet-stream",
                )
                contracts.check(
                    (content_type_parameter.get("schema") or {}).get("default")
                    == "application/octet-stream",
                    f"{where}: Content-Type must default to application/octet-stream",
                )
            file_name_parameter = _inline_parameter(operation, "X-File-Name")
            contracts.check(
                isinstance(file_name_parameter, dict)
                and file_name_parameter.get("in") == "header",
                f"{where}: must document the X-File-Name header parameter",
            )
            if isinstance(file_name_parameter, dict):
                contracts.check(
                    file_name_parameter.get("required") is True,
                    f"{where}: X-File-Name must be required",
                )
                contracts.check(
                    (file_name_parameter.get("schema") or {}).get("type") == "string",
                    f"{where}: X-File-Name schema must be a string",
                )
            ok_schema = _response_schema(operation, "200")
            contracts.check(
                isinstance(ok_schema, dict)
                and str(ok_schema.get("$ref", "")).endswith(
                    "/schemas/DocumentContent"
                ),
                f"{where}: 200 must return the DocumentContent schema",
            )
            bad_request = responses.get("400")
            bad_request_text = (
                str(bad_request.get("description") or "")
                if isinstance(bad_request, dict)
                else ""
            )
            contracts.check(
                "EMPTY_CONTENT" in bad_request_text,
                f"{where}: 400 must document EMPTY_CONTENT",
            )
            too_large = responses.get("413")
            too_large_text = (
                str(too_large.get("description") or "")
                if isinstance(too_large, dict)
                else ""
            )
            contracts.check(
                "FILE_TOO_LARGE" in too_large_text,
                f"{where}: 413 must document FILE_TOO_LARGE",
            )
            too_large_schema = _response_schema(
                operation, "413", "application/problem+json"
            )
            contracts.check(
                isinstance(too_large_schema, dict)
                and str(too_large_schema.get("$ref", "")).endswith("/schemas/Problem"),
                f"{where}: 413 must use the shared Problem schema",
            )
        elif method == "delete":
            contracts.check(
                "204" in responses,
                f"{where}: must document the 204 no-content response",
            )
            no_content = responses.get("204")
            contracts.check(
                isinstance(no_content, dict) and "content" not in no_content,
                f"{where}: 204 must not declare a response body",
            )
            contracts.check(
                "requestBody" not in operation,
                f"{where}: the content tombstone must not declare a request body",
            )
            not_found = responses.get("404")
            not_found_text = (
                str(not_found.get("description") or "")
                if isinstance(not_found, dict)
                else ""
            )
            contracts.check(
                "CONTENT_NOT_FOUND" in not_found_text,
                f"{where}: 404 must document CONTENT_NOT_FOUND",
            )
            conflict = responses.get("409")
            conflict_text = (
                str(conflict.get("description") or "")
                if isinstance(conflict, dict)
                else ""
            )
            for code in DOCUMENT_CONTENT_DELETE_CODES[1:]:
                contracts.check(
                    code in conflict_text,
                    f"{where}: 409 must document {code}",
                )
            conflict_schema = _response_schema(
                operation, "409", "application/problem+json"
            )
            contracts.check(
                isinstance(conflict_schema, dict)
                and str(conflict_schema.get("$ref", "")).endswith("/schemas/Problem"),
                f"{where}: 409 must use the shared Problem schema",
            )
            description = str(operation.get("description") or "")
            for term in ("document.content.deleted", "deletedAt", "204"):
                contracts.check(
                    term in description,
                    f"{where}: description must document {term}",
                )
            for term in DOCUMENT_CONTENT_DISPOSITION_TERMS:
                contracts.check(
                    term in description,
                    f"{where}: description must document the shared disposition "
                    f"tombstone ({term})",
                )
        elif content_path == DOCUMENT_CONTENT_PATH:
            ok_response = responses.get("200")
            ok_content = (
                ok_response.get("content") if isinstance(ok_response, dict) else {}
            ) or {}
            binary_schema = None
            for media_type, media_object in ok_content.items():
                if media_type in ("*/*", "application/octet-stream") and isinstance(
                    media_object, dict
                ):
                    binary_schema = media_object.get("schema")
            contracts.check(
                isinstance(binary_schema, dict)
                and binary_schema.get("type") == "string"
                and binary_schema.get("format") == "binary",
                f"{where}: 200 must return a binary string body",
            )
            headers = (
                ok_response.get("headers") if isinstance(ok_response, dict) else {}
            ) or {}
            for header_name in (
                "Content-Type",
                "Content-Disposition",
                "X-Content-SHA256",
                "X-Content-Version",
            ):
                contracts.check(
                    header_name in headers,
                    f"{where}: 200 must document the {header_name} header",
                )
            sha256_schema = (headers.get("X-Content-SHA256") or {}).get("schema") or {}
            contracts.check(
                sha256_schema.get("pattern") == "^[a-f0-9]{64}$",
                f"{where}: X-Content-SHA256 must be a lowercase 64-character digest",
            )
            version_header_schema = (
                (headers.get("X-Content-Version") or {}).get("schema") or {}
            )
            contracts.check(
                version_header_schema.get("type") == "integer"
                and version_header_schema.get("minimum") == 1,
                f"{where}: X-Content-Version must be a positive integer",
            )
            gone = responses.get("410")
            gone_text = (
                str(gone.get("description") or "") if isinstance(gone, dict) else ""
            )
            contracts.check(
                "CONTENT_DELETED" in gone_text,
                f"{where}: 410 must document CONTENT_DELETED",
            )
            gone_schema = _response_schema(
                operation, "410", "application/problem+json"
            )
            contracts.check(
                isinstance(gone_schema, dict)
                and str(gone_schema.get("$ref", "")).endswith("/schemas/Problem"),
                f"{where}: 410 must use the shared Problem schema",
            )
            description = str(operation.get("description") or "")
            for term in DOCUMENT_CONTENT_DISPOSITION_TERMS:
                contracts.check(
                    term in description,
                    f"{where}: description must document a disposition tombstone "
                    "as a 410 source",
                )
        elif content_path == DOCUMENT_CONTENT_VERSIONS_PATH:
            ok_schema = _response_schema(operation, "200")
            contracts.check(
                isinstance(ok_schema, dict)
                and ok_schema.get("type") == "array"
                and str((ok_schema.get("items") or {}).get("$ref", "")).endswith(
                    "/schemas/DocumentContentVersion"
                ),
                f"{where}: 200 must return an array of DocumentContentVersion",
            )
        elif content_path == DOCUMENT_CONTENT_VERSION_PATH:
            version_parameter = _inline_parameter(operation, "version")
            contracts.check(
                isinstance(version_parameter, dict)
                and version_parameter.get("in") == "path"
                and version_parameter.get("required") is True,
                f"{where}: must declare the required version path parameter",
            )
            version_schema = (
                (version_parameter or {}).get("schema")
                if isinstance(version_parameter, dict)
                else None
            ) or {}
            contracts.check(
                version_schema.get("type") == "integer"
                and version_schema.get("minimum") == 1,
                f"{where}: version path parameter must be a positive integer",
            )
            ok_response = responses.get("200")
            ok_content = (
                ok_response.get("content") if isinstance(ok_response, dict) else {}
            ) or {}
            binary_schema = None
            for media_type, media_object in ok_content.items():
                if media_type in ("*/*", "application/octet-stream") and isinstance(
                    media_object, dict
                ):
                    binary_schema = media_object.get("schema")
            contracts.check(
                isinstance(binary_schema, dict)
                and binary_schema.get("type") == "string"
                and binary_schema.get("format") == "binary",
                f"{where}: 200 must return a binary string body",
            )
            headers = (
                ok_response.get("headers") if isinstance(ok_response, dict) else {}
            ) or {}
            for header_name in (
                "Content-Type",
                "Content-Disposition",
                "X-Content-SHA256",
                "X-Content-Version",
            ):
                contracts.check(
                    header_name in headers,
                    f"{where}: 200 must document the {header_name} header",
                )
            version_header_schema = (
                (headers.get("X-Content-Version") or {}).get("schema") or {}
            )
            contracts.check(
                version_header_schema.get("type") == "integer"
                and version_header_schema.get("minimum") == 1,
                f"{where}: X-Content-Version must be a positive integer",
            )
            gone = responses.get("410")
            gone_text = (
                str(gone.get("description") or "") if isinstance(gone, dict) else ""
            )
            contracts.check(
                "CONTENT_DELETED" in gone_text,
                f"{where}: 410 must document CONTENT_DELETED",
            )
            gone_schema = _response_schema(
                operation, "410", "application/problem+json"
            )
            contracts.check(
                isinstance(gone_schema, dict)
                and str(gone_schema.get("$ref", "")).endswith("/schemas/Problem"),
                f"{where}: 410 must use the shared Problem schema",
            )
            description = str(operation.get("description") or "")
            contracts.check(
                "CONTENT_VERSION_NOT_FOUND" in description,
                f"{where}: description must document 404 CONTENT_VERSION_NOT_FOUND",
            )
            contracts.check(
                "INVALID_PARAMETER" in description,
                f"{where}: description must document 400 INVALID_PARAMETER for a "
                "non-numeric version",
            )
            for term in DOCUMENT_CONTENT_DISPOSITION_TERMS:
                contracts.check(
                    term in description,
                    f"{where}: description must document a disposition tombstone "
                    "as a 410 source",
                )
        else:
            ok_schema = _response_schema(operation, "200")
            contracts.check(
                isinstance(ok_schema, dict)
                and str(ok_schema.get("$ref", "")).endswith(
                    "/schemas/DocumentContent"
                ),
                f"{where}: 200 must return the DocumentContent schema",
            )
            description = str(operation.get("description") or "")
            for term in DOCUMENT_CONTENT_DISPOSITION_TERMS:
                contracts.check(
                    term in description,
                    f"{where}: description must document the disposition tombstone",
                )

    content_schema = schemas.get("DocumentContent") or {}
    content_properties = content_schema.get("properties") or {}
    content_required = set(content_schema.get("required") or [])
    contracts.check(
        content_schema.get("type") == "object",
        f"{relative}: DocumentContent must be an object schema",
    )
    for field in DOCUMENT_CONTENT_FIELDS:
        contracts.check(
            field in content_properties,
            f"{relative}: DocumentContent.properties.{field} is required",
        )
        contracts.check(
            field in content_required,
            f"{relative}: DocumentContent.required must list {field}",
        )
    contracts.check(
        (content_properties.get("documentId") or {}).get("format") == "uuid",
        f"{relative}: DocumentContent.documentId must be a uuid",
    )
    contracts.check(
        (content_properties.get("fileName") or {}).get("maxLength")
        == DOCUMENT_CONTENT_FILE_NAME_MAX_LENGTH,
        f"{relative}: DocumentContent.fileName maxLength must be "
        f"{DOCUMENT_CONTENT_FILE_NAME_MAX_LENGTH}",
    )
    contracts.check(
        (content_properties.get("contentType") or {}).get("maxLength")
        == DOCUMENT_CONTENT_TYPE_MAX_LENGTH,
        f"{relative}: DocumentContent.contentType maxLength must be "
        f"{DOCUMENT_CONTENT_TYPE_MAX_LENGTH}",
    )
    size_schema = content_properties.get("sizeBytes") or {}
    contracts.check(
        (
            size_schema.get("type"),
            size_schema.get("format"),
            size_schema.get("minimum"),
            size_schema.get("maximum"),
        )
        == ("integer", "int64", 0, DOCUMENT_CONTENT_MAX_BYTES),
        f"{relative}: DocumentContent.sizeBytes must be an int64 from 0 to "
        f"{DOCUMENT_CONTENT_MAX_BYTES}",
    )
    contracts.check(
        (content_properties.get("sha256") or {}).get("pattern")
        == "^[a-f0-9]{64}$",
        f"{relative}: DocumentContent.sha256 must be a lowercase 64-character digest",
    )
    contracts.check(
        (content_properties.get("uploadedAt") or {}).get("format") == "date-time",
        f"{relative}: DocumentContent.uploadedAt must be a date-time",
    )
    current_version = content_properties.get("currentVersion") or {}
    contracts.check(
        current_version.get("type") == "integer"
        and current_version.get("minimum") == 1,
        f"{relative}: DocumentContent.currentVersion must be a positive integer",
    )
    contracts.check(
        "currentVersion" in content_required,
        f"{relative}: DocumentContent.required must list currentVersion",
    )
    deleted_at = content_properties.get("deletedAt") or {}
    contracts.check(
        _schema_types(deleted_at) == {"string", "null"}
        and deleted_at.get("format") == "date-time",
        f"{relative}: DocumentContent.deletedAt must be a nullable date-time",
    )
    deleted_at_description = str(deleted_at.get("description") or "")
    for term in DOCUMENT_CONTENT_DISPOSITION_TERMS:
        contracts.check(
            term in deleted_at_description,
            f"{relative}: DocumentContent.deletedAt description must document "
            "the disposition tombstone",
        )
    deleted = content_properties.get("deleted") or {}
    contracts.check(
        deleted.get("type") == "boolean",
        f"{relative}: DocumentContent.deleted must be a boolean",
    )

    version_schema = schemas.get("DocumentContentVersion") or {}
    version_properties = version_schema.get("properties") or {}
    version_required = set(version_schema.get("required") or [])
    contracts.check(
        version_schema.get("type") == "object",
        f"{relative}: DocumentContentVersion must be an object schema",
    )
    for field in DOCUMENT_CONTENT_VERSION_FIELDS:
        contracts.check(
            field in version_properties,
            f"{relative}: DocumentContentVersion.properties.{field} is required",
        )
        contracts.check(
            field in version_required,
            f"{relative}: DocumentContentVersion.required must list {field}",
        )
    contracts.check(
        (version_properties.get("documentId") or {}).get("format") == "uuid",
        f"{relative}: DocumentContentVersion.documentId must be a uuid",
    )
    revision = version_properties.get("version") or {}
    contracts.check(
        revision.get("type") == "integer" and revision.get("minimum") == 1,
        f"{relative}: DocumentContentVersion.version must be a positive integer",
    )
    contracts.check(
        (version_properties.get("fileName") or {}).get("maxLength")
        == DOCUMENT_CONTENT_FILE_NAME_MAX_LENGTH,
        f"{relative}: DocumentContentVersion.fileName maxLength must be "
        f"{DOCUMENT_CONTENT_FILE_NAME_MAX_LENGTH}",
    )
    contracts.check(
        (version_properties.get("contentType") or {}).get("maxLength")
        == DOCUMENT_CONTENT_TYPE_MAX_LENGTH,
        f"{relative}: DocumentContentVersion.contentType maxLength must be "
        f"{DOCUMENT_CONTENT_TYPE_MAX_LENGTH}",
    )
    version_size = version_properties.get("sizeBytes") or {}
    contracts.check(
        (
            version_size.get("type"),
            version_size.get("format"),
            version_size.get("minimum"),
            version_size.get("maximum"),
        )
        == ("integer", "int64", 0, DOCUMENT_CONTENT_MAX_BYTES),
        f"{relative}: DocumentContentVersion.sizeBytes must be an int64 from 0 to "
        f"{DOCUMENT_CONTENT_MAX_BYTES}",
    )
    contracts.check(
        (version_properties.get("sha256") or {}).get("pattern")
        == "^[a-f0-9]{64}$",
        f"{relative}: DocumentContentVersion.sha256 must be a lowercase "
        "64-character digest",
    )
    contracts.check(
        (version_properties.get("uploadedAt") or {}).get("format") == "date-time",
        f"{relative}: DocumentContentVersion.uploadedAt must be a date-time",
    )

    planned = document.get("x-planned-operations") or []
    for implemented_path in (
        DOCUMENT_CONTENT_PATH,
        DOCUMENT_CONTENT_METADATA_PATH,
        DOCUMENT_CONTENT_VERSIONS_PATH,
        DOCUMENT_CONTENT_VERSION_PATH,
    ):
        contracts.check(
            not any(
                isinstance(entry, dict) and entry.get("path") == implemented_path
                for entry in planned
            ),
            f"{relative}: {implemented_path} must not remain in x-planned-operations",
        )


# ---------------------------------------------------------------------------
# Document legal-hold and disposition checks
# ---------------------------------------------------------------------------


def check_document_holds_openapi(contracts: ContractSet, document, relative: str):
    """Require the legal-hold and disposition operations, schemas, and codes."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    info_description = str((document.get("info") or {}).get("description") or "")
    for term in ("disposition-content slice", "document.content.deleted"):
        contracts.check(
            term in info_description,
            f"{relative}: info.description must document {term}",
        )

    lifecycle_operations = (
        (DOCUMENT_HOLD_PATH, "placeDocumentHold", DOCUMENT_HOLD_CODES),
        (DOCUMENT_HOLD_RELEASE_PATH, "releaseDocumentHold", DOCUMENT_HOLD_RELEASE_CODES),
        (DOCUMENT_DISPOSAL_PATH, "disposeDocument", DOCUMENT_DISPOSAL_CODES),
    )
    documented_conflicts = []
    for lifecycle_path, operation_id, conflict_codes in lifecycle_operations:
        path_item = paths.get(lifecycle_path) if isinstance(paths, dict) else None
        operation = path_item.get("post") if isinstance(path_item, dict) else None
        where = f"{relative}: POST {lifecycle_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required hold/disposition operation is missing",
        )
        if not isinstance(operation, dict):
            continue
        contracts.check(
            operation.get("operationId") == operation_id,
            f"{where}: operationId must be {operation_id}",
        )
        parameter_refs, inline_names = _link_parameters(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must document the shared TenantHeader parameter",
        )
        contracts.check(
            "documentId" in inline_names,
            f"{where}: must declare the documentId path parameter",
        )

        responses = operation.get("responses") or {}
        for status in ("200", "400", "404", "409"):
            contracts.check(
                status in responses,
                f"{where}: must document the {status} response",
            )
        ok_schema = _link_response_schema(operation, "200", "application/json")
        contracts.check(
            isinstance(ok_schema, dict)
            and str(ok_schema.get("$ref", "")).endswith("/schemas/Document"),
            f"{where}: 200 must return the Document schema",
        )
        conflict = responses.get("409")
        conflict_text = (
            str(conflict.get("description") or "") if isinstance(conflict, dict) else ""
        )
        documented_conflicts.append(conflict_text)
        for code in conflict_codes:
            contracts.check(
                code in conflict_text,
                f"{where}: 409 must document {code}",
            )
        conflict_schema = _link_response_schema(
            operation, "409", "application/problem+json"
        )
        contracts.check(
            isinstance(conflict_schema, dict)
            and str(conflict_schema.get("$ref", "")).endswith("/schemas/Problem"),
            f"{where}: 409 must document the shared Problem schema",
        )

        if lifecycle_path == DOCUMENT_HOLD_PATH:
            request_schema = (
                ((operation.get("requestBody") or {}).get("content") or {})
                .get("application/json", {})
                .get("schema")
            )
            contracts.check(
                isinstance(request_schema, dict)
                and str(request_schema.get("$ref", "")).endswith(
                    "/schemas/HoldDocumentRequest"
                ),
                f"{where}: request body must use the HoldDocumentRequest schema",
            )
        else:
            contracts.check(
                "requestBody" not in operation,
                f"{where}: the command must not declare a request body",
            )

        if lifecycle_path == DOCUMENT_DISPOSAL_PATH:
            description = str(operation.get("description") or "")
            for term in DOCUMENT_DISPOSAL_DESCRIPTION_TERMS:
                contracts.check(
                    term in description,
                    f"{where}: description must document {term}",
                )
            # A document with no content or already-tombstoned content still
            # disposes; the explicit delete's 404/409 vocabulary must not leak
            # into the disposition conflicts.
            contracts.check(
                "CONTENT_NOT_FOUND" not in conflict_text
                and "CONTENT_ALREADY_DELETED" not in conflict_text,
                f"{where}: absent or already-tombstoned content must not be a "
                "disposition 404/409 conflict",
            )

    # Every conflict code of the slice must be documented somewhere, and no
    # implemented lifecycle path may hide under the planned list.
    planned = document.get("x-planned-operations") or []
    for implemented_path in (
        DOCUMENT_HOLD_PATH,
        DOCUMENT_HOLD_RELEASE_PATH,
        DOCUMENT_DISPOSAL_PATH,
    ):
        contracts.check(
            not any(
                isinstance(entry, dict) and entry.get("path") == implemented_path
                for entry in planned
            ),
            f"{relative}: {implemented_path} must not remain in x-planned-operations",
        )
    documented = " ".join(documented_conflicts)
    for code in DOCUMENT_LIFECYCLE_CODES:
        contracts.check(
            code in documented,
            f"{relative}: hold/disposition 409 responses must document {code}",
        )

    # The Document projection carries the four nullable lifecycle members.
    document_schema = schemas.get("Document") or {}
    document_properties = document_schema.get("properties") or {}
    document_required = set(document_schema.get("required") or [])
    for field in DOCUMENT_HOLD_FIELDS:
        contracts.check(
            field in document_properties,
            f"{relative}: Document.properties.{field} is required",
        )
        contracts.check(
            field in document_required,
            f"{relative}: Document.required must list {field}",
        )
    hold_reason = document_properties.get("holdReason") or {}
    contracts.check(
        _schema_types(hold_reason) == {"string", "null"}
        and hold_reason.get("maxLength") == DOCUMENT_HOLD_REASON_MAX_LENGTH,
        f"{relative}: Document.holdReason must be a nullable string of at most "
        f"{DOCUMENT_HOLD_REASON_MAX_LENGTH} characters",
    )
    for field in ("heldAt", "disposedAt"):
        member = document_properties.get(field) or {}
        contracts.check(
            _schema_types(member) == {"string", "null"}
            and member.get("format") == "date-time",
            f"{relative}: Document.{field} must be a nullable date-time",
        )
    status_before_hold = document_properties.get("statusBeforeHold") or {}
    status_branches = [
        branch
        for branch in (status_before_hold.get("oneOf") or [])
        if isinstance(branch, dict)
    ]
    contracts.check(
        any(
            str(branch.get("$ref", "")).endswith("/schemas/DocumentStatus")
            for branch in status_branches
        )
        and any(branch.get("type") == "null" for branch in status_branches),
        f"{relative}: Document.statusBeforeHold must be a nullable DocumentStatus",
    )

    hold_request = schemas.get("HoldDocumentRequest") or {}
    hold_properties = hold_request.get("properties") or {}
    hold_required = set(hold_request.get("required") or [])
    contracts.check(
        hold_request.get("type") == "object" and hold_required == {"reason"},
        f"{relative}: HoldDocumentRequest must be an object requiring only reason",
    )
    reason = hold_properties.get("reason") or {}
    contracts.check(
        reason.get("type") == "string"
        and reason.get("minLength") == 1
        and reason.get("maxLength") == DOCUMENT_HOLD_REASON_MAX_LENGTH,
        f"{relative}: HoldDocumentRequest.reason must be a string of 1 to "
        f"{DOCUMENT_HOLD_REASON_MAX_LENGTH} characters",
    )


def check_document_holds_asyncapi(contracts: ContractSet, document, relative: str):
    """Require the implemented hold and disposition channels and payload."""
    channels = document.get("channels") or {}
    operations = document.get("operations") or {}
    messages = (document.get("components") or {}).get("messages") or {}

    addresses = {
        channel.get("address")
        for channel in channels.values()
        if isinstance(channel, dict)
    }
    implemented_addresses = {
        channel.get("address")
        for channel in channels.values()
        if isinstance(channel, dict) and channel.get("x-status") == "implemented"
    }
    send_events = {
        operation.get("x-event-type")
        for operation in operations.values()
        if isinstance(operation, dict) and operation.get("action") == "send"
    }

    for event in DOCUMENT_LIFECYCLE_EVENTS:
        contracts.check(
            event in addresses,
            f"{relative}: required hold/disposition event channel '{event}' is missing",
        )
        contracts.check(
            event in implemented_addresses,
            f"{relative}: hold/disposition event channel '{event}' must be implemented",
        )
        contracts.check(
            event in send_events,
            f"{relative}: hold/disposition event '{event}' must have a send operation",
        )
        channel = next(
            (
                channel
                for channel in channels.values()
                if isinstance(channel, dict) and channel.get("address") == event
            ),
            None,
        )
        contracts.check(
            isinstance(channel, dict)
            and str(channel.get("x-implemented-by", "")).endswith(
                "DocumentEvents.java"
            ),
            f"{relative}: {event} must name DocumentEvents.java in x-implemented-by",
        )
        channel_messages = (
            channel.get("messages") if isinstance(channel, dict) else None
        ) or {}
        contracts.check(
            DOCUMENT_LIFECYCLE_DATA in channel_messages,
            f"{relative}: {event} must reference {DOCUMENT_LIFECYCLE_DATA}",
        )
        if event == "document.document.disposed":
            description = (
                str(channel.get("description") or "")
                if isinstance(channel, dict)
                else ""
            )
            for term in (
                "document.content.deleted",
                "live stored content",
                "no content",
                "already-tombstoned",
            ):
                contracts.check(
                    term in description,
                    f"{relative}: {event} description must document {term}",
                )

    # The SPEC 11.6.9 held/hold-released names stay planned; the implemented
    # names are the two legal-hold facts above.
    for spec_event in (
        "document.document.held",
        "document.document.hold-released",
    ):
        contracts.check(
            spec_event not in implemented_addresses,
            f"{relative}: {spec_event} must stay planned; the implemented hold "
            "names are document.legal-hold.placed/.released",
        )

    message = messages.get(DOCUMENT_LIFECYCLE_DATA) or {}
    payload = message.get("payload") or {}
    properties = payload.get("properties") or {}
    required = set(payload.get("required") or [])
    for field in DOCUMENT_LIFECYCLE_EVENT_FIELDS:
        contracts.check(
            field in properties,
            f"{relative}: {DOCUMENT_LIFECYCLE_DATA}.properties.{field} is required",
        )
        contracts.check(
            field in required,
            f"{relative}: {DOCUMENT_LIFECYCLE_DATA}.required must list {field}",
        )
    contracts.check(
        (properties.get("documentId") or {}).get("format") == "uuid",
        f"{relative}: {DOCUMENT_LIFECYCLE_DATA}.documentId must be a uuid",
    )
    contracts.check(
        (properties.get("reason") or {}).get("maxLength")
        == DOCUMENT_HOLD_REASON_MAX_LENGTH,
        f"{relative}: {DOCUMENT_LIFECYCLE_DATA}.reason maxLength must be "
        f"{DOCUMENT_HOLD_REASON_MAX_LENGTH}",
    )
    contracts.check(
        set((properties.get("status") or {}).get("enum") or [])
        == set(DOCUMENT_STATUSES),
        f"{relative}: {DOCUMENT_LIFECYCLE_DATA}.status must enumerate "
        f"{list(DOCUMENT_STATUSES)}",
    )


# ---------------------------------------------------------------------------
# Policy billing checks
# ---------------------------------------------------------------------------


def _response_schema(operation, status, media_type="application/json"):
    response = (operation.get("responses") or {}).get(status)
    if not isinstance(response, dict):
        return None
    return ((response.get("content") or {}).get(media_type) or {}).get("schema")


def _parameter_names(operation):
    """Return (referenced parameter component names, inline parameter names)."""
    references = []
    names = []
    for parameter in operation.get("parameters") or []:
        if not isinstance(parameter, dict):
            continue
        reference = parameter.get("$ref")
        if isinstance(reference, str):
            references.append(reference.rsplit("/", 1)[-1])
        if isinstance(parameter.get("name"), str):
            names.append(parameter["name"])
    return references, names


def _inline_parameter(operation, name):
    """Return the inline query/path parameter called name, or None."""
    for parameter in operation.get("parameters") or []:
        if isinstance(parameter, dict) and parameter.get("name") == name:
            return parameter
    return None


def check_policy_billing_openapi(contracts: ContractSet, document, relative: str):
    """Require the Policy billing operations, schemas, and field rules."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    for method, billing_path, response_schema_name, request_schema_name in (
        BILLING_OPENAPI_PATHS
    ):
        path_item = paths.get(billing_path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {billing_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required billing operation is missing",
        )
        if not isinstance(operation, dict):
            continue

        parameter_refs, inline_names = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must require the shared TenantHeader",
        )
        contracts.check(
            "BookHeaderDirectOptional" in parameter_refs,
            f"{where}: must document the shared BookHeaderDirectOptional parameter",
        )
        contracts.check(
            "policyId" in inline_names,
            f"{where}: must declare the policyId path parameter",
        )
        if method == "patch":
            contracts.check(
                "installmentId" in inline_names,
                f"{where}: must declare the installmentId path parameter",
            )

        responses = operation.get("responses") or {}
        contracts.check(
            "400" in responses,
            f"{where}: must document the 400 response",
        )
        contracts.check(
            "404" in responses,
            f"{where}: must document the 404 response",
        )
        if method in ("post", "patch"):
            contracts.check(
                "409" in responses,
                f"{where}: must document the 409 response",
            )

        if method == "get":
            ok_schema = _response_schema(operation, "200")
            contracts.check(
                isinstance(ok_schema, dict)
                and str(ok_schema.get("$ref", "")).endswith(
                    f"/schemas/{response_schema_name}"
                ),
                f"{where}: 200 must return the {response_schema_name} schema",
            )
        else:
            request_body = operation.get("requestBody") or {}
            contracts.check(
                request_body.get("required") is True,
                f"{where}: request body must be required",
            )
            request_schema = (
                ((request_body.get("content") or {}).get("application/json") or {})
                .get("schema")
                if isinstance(request_body, dict)
                else None
            )
            contracts.check(
                isinstance(request_schema, dict)
                and str(request_schema.get("$ref", "")).endswith(
                    f"/schemas/{request_schema_name}"
                ),
                f"{where}: request body must use the {request_schema_name} schema",
            )
            success_status = "201" if method == "post" else "200"
            success_schema = _response_schema(operation, success_status)
            contracts.check(
                isinstance(success_schema, dict)
                and str(success_schema.get("$ref", "")).endswith(
                    f"/schemas/{response_schema_name}"
                ),
                f"{where}: {success_status} must return the {response_schema_name} schema",
            )

    plan = schemas.get("BillingPlan") or {}
    plan_properties = plan.get("properties") or {}
    plan_required = set(plan.get("required") or [])
    contracts.check(
        isinstance(plan, dict) and plan.get("type") == "object",
        f"{relative}: BillingPlan must be an object schema",
    )
    for field in BILLING_PLAN_FIELDS:
        contracts.check(
            field in plan_properties,
            f"{relative}: BillingPlan.properties.{field} is required",
        )
    for field in BILLING_PLAN_FIELDS:
        contracts.check(
            field in plan_required,
            f"{relative}: BillingPlan.required must list {field}",
        )
    for field in ("planId", "policyId"):
        contracts.check(
            (plan_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: BillingPlan.{field} must be a uuid",
        )
    contracts.check(
        str((plan_properties.get("totalPremium") or {}).get("$ref", "")).endswith(
            "/schemas/MoneyAmount"
        ),
        f"{relative}: BillingPlan.totalPremium must reference MoneyAmount",
    )
    contracts.check(
        str((plan_properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: BillingPlan.currency must reference CurrencyCode",
    )
    plan_count = plan_properties.get("installmentCount") or {}
    contracts.check(
        (
            plan_count.get("type"),
            plan_count.get("minimum"),
            plan_count.get("maximum"),
        ) == ("integer", BILLING_MIN_INSTALLMENTS, BILLING_MAX_INSTALLMENTS),
        f"{relative}: BillingPlan.installmentCount must be an integer between "
        f"{BILLING_MIN_INSTALLMENTS} and {BILLING_MAX_INSTALLMENTS}",
    )
    contracts.check(
        set((plan_properties.get("frequency") or {}).get("enum") or [])
        == set(BILLING_FREQUENCIES),
        f"{relative}: BillingPlan.frequency must enumerate {list(BILLING_FREQUENCIES)}",
    )
    contracts.check(
        (plan_properties.get("firstDueDate") or {}).get("format") == "date",
        f"{relative}: BillingPlan.firstDueDate must be a date",
    )
    contracts.check(
        set((plan_properties.get("status") or {}).get("enum") or [])
        == set(BILLING_PLAN_STATUSES),
        f"{relative}: BillingPlan.status must enumerate {list(BILLING_PLAN_STATUSES)}",
    )
    plan_installments = plan_properties.get("installments") or {}
    contracts.check(
        plan_installments.get("type") == "array"
        and str((plan_installments.get("items") or {}).get("$ref", "")).endswith(
            "/schemas/Installment"
        ),
        f"{relative}: BillingPlan.installments must be an array of Installment",
    )
    contracts.check(
        str((plan_properties.get("summary") or {}).get("$ref", "")).endswith(
            "/schemas/BillingSummary"
        ),
        f"{relative}: BillingPlan.summary must reference BillingSummary",
    )

    get_billing = paths.get("/api/v1/policies/{policyId}/billing") or {}
    get_operation = get_billing.get("get") if isinstance(get_billing, dict) else None
    get_text = str((get_operation or {}).get("description") or "")
    for term in ("creditedAmount", "outstandingAmount", "summary", "CREDITED"):
        contracts.check(
            term in get_text,
            f"{relative}: GET billing must document {term}",
        )

    installment = schemas.get("Installment") or {}
    installment_properties = installment.get("properties") or {}
    installment_required = set(installment.get("required") or [])
    contracts.check(
        isinstance(installment, dict) and installment.get("type") == "object",
        f"{relative}: Installment must be an object schema",
    )
    for field in BILLING_INSTALLMENT_FIELDS:
        contracts.check(
            field in installment_properties,
            f"{relative}: Installment.properties.{field} is required",
        )
    for field in BILLING_INSTALLMENT_REQUIRED_FIELDS:
        contracts.check(
            field in installment_required,
            f"{relative}: Installment.required must list {field}",
        )
    contracts.check(
        (installment_properties.get("installmentId") or {}).get("format") == "uuid",
        f"{relative}: Installment.installmentId must be a uuid",
    )
    installment_number = installment_properties.get("installmentNumber") or {}
    contracts.check(
        (
            installment_number.get("type"),
            installment_number.get("minimum"),
        ) == ("integer", 1),
        f"{relative}: Installment.installmentNumber must be an integer >= 1",
    )
    contracts.check(
        (installment_properties.get("dueDate") or {}).get("format") == "date",
        f"{relative}: Installment.dueDate must be a date",
    )
    for field in BILLING_INSTALLMENT_MONEY_FIELDS:
        contracts.check(
            str((installment_properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: Installment.{field} must reference MoneyAmount",
        )
    contracts.check(
        set((installment_properties.get("status") or {}).get("enum") or [])
        == set(BILLING_INSTALLMENT_STATUSES),
        f"{relative}: Installment.status must enumerate "
        f"{list(BILLING_INSTALLMENT_STATUSES)}",
    )
    paid_at = installment_properties.get("paidAt") or {}
    contracts.check(
        _schema_types(paid_at) == {"string", "null"}
        and paid_at.get("format") == "date-time",
        f"{relative}: Installment.paidAt must be a nullable date-time",
    )
    payment_id = installment_properties.get("paymentId") or {}
    contracts.check(
        _schema_types(payment_id) == {"string", "null"}
        and payment_id.get("format") == "uuid",
        f"{relative}: Installment.paymentId must be a nullable uuid",
    )

    summary = schemas.get("BillingSummary") or {}
    summary_properties = summary.get("properties") or {}
    summary_required = set(summary.get("required") or [])
    contracts.check(
        isinstance(summary, dict) and summary.get("type") == "object",
        f"{relative}: BillingSummary must be an object schema",
    )
    for field in BILLING_SUMMARY_FIELDS:
        contracts.check(
            field in summary_properties,
            f"{relative}: BillingSummary.properties.{field} is required",
        )
        contracts.check(
            field in summary_required,
            f"{relative}: BillingSummary.required must list {field}",
        )
    for field in BILLING_SUMMARY_MONEY_FIELDS:
        contracts.check(
            str((summary_properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: BillingSummary.{field} must reference MoneyAmount",
        )
    contracts.check(
        str((summary_properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: BillingSummary.currency must reference CurrencyCode",
    )
    summary_count = summary_properties.get("installmentCount") or {}
    contracts.check(
        (summary_count.get("type"), summary_count.get("minimum")) == ("integer", 0),
        f"{relative}: BillingSummary.installmentCount must be an integer >= 0",
    )

    patch_billing = paths.get(
        "/api/v1/policies/{policyId}/billing/installments/{installmentId}"
    ) or {}
    patch_operation = (
        patch_billing.get("patch") if isinstance(patch_billing, dict) else None
    )
    patch_text = str((patch_operation or {}).get("description") or "")
    for term in ("CREDITED", "INSTALLMENT_ALREADY_SETTLED", "outstandingAmount"):
        contracts.check(
            term in patch_text,
            f"{relative}: PATCH billing installment must document {term}",
        )

    create = schemas.get("CreateBillingPlanRequest") or {}
    create_properties = create.get("properties") or {}
    create_required = set(create.get("required") or [])
    contracts.check(
        isinstance(create, dict) and create.get("type") == "object",
        f"{relative}: CreateBillingPlanRequest must be an object schema",
    )
    contracts.check(
        {"installmentCount", "frequency", "firstDueDate"} <= create_required,
        f"{relative}: CreateBillingPlanRequest must require installmentCount, "
        f"frequency, and firstDueDate",
    )
    create_count = create_properties.get("installmentCount") or {}
    contracts.check(
        (
            create_count.get("type"),
            create_count.get("minimum"),
            create_count.get("maximum"),
        ) == ("integer", BILLING_MIN_INSTALLMENTS, BILLING_MAX_INSTALLMENTS),
        f"{relative}: CreateBillingPlanRequest.installmentCount must be an integer "
        f"between {BILLING_MIN_INSTALLMENTS} and {BILLING_MAX_INSTALLMENTS}",
    )
    contracts.check(
        set((create_properties.get("frequency") or {}).get("enum") or [])
        == set(BILLING_FREQUENCIES),
        f"{relative}: CreateBillingPlanRequest.frequency must enumerate "
        f"{list(BILLING_FREQUENCIES)}",
    )
    contracts.check(
        (create_properties.get("firstDueDate") or {}).get("format") == "date",
        f"{relative}: CreateBillingPlanRequest.firstDueDate must be a date",
    )

    update = schemas.get("UpdateInstallmentRequest") or {}
    update_properties = update.get("properties") or {}
    update_required = set(update.get("required") or [])
    contracts.check(
        isinstance(update, dict) and update.get("type") == "object",
        f"{relative}: UpdateInstallmentRequest must be an object schema",
    )
    contracts.check(
        "status" in update_required,
        f"{relative}: UpdateInstallmentRequest must require status",
    )
    contracts.check(
        set((update_properties.get("status") or {}).get("enum") or [])
        == set(BILLING_SETTLE_STATUSES),
        f"{relative}: UpdateInstallmentRequest.status must enumerate "
        f"{list(BILLING_SETTLE_STATUSES)}",
    )
    contracts.check(
        "paymentId" in update_properties,
        f"{relative}: UpdateInstallmentRequest.properties.paymentId is required",
    )
    contracts.check(
        "paymentId" not in update_required,
        f"{relative}: UpdateInstallmentRequest.paymentId must stay optional",
    )
    contracts.check(
        _schema_types(update_properties.get("paymentId")) == {"string", "null"}
        and (update_properties.get("paymentId") or {}).get("format") == "uuid",
        f"{relative}: UpdateInstallmentRequest.paymentId must be a nullable uuid",
    )

    check_policy_billing_adjustment_openapi(contracts, document, relative)


def check_policy_billing_adjustment_openapi(
    contracts: ContractSet, document, relative: str
):
    """Require the positive premium adjustment operation, schemas, and errors."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    path_item = paths.get(BILLING_ADJUSTMENT_PATH) if isinstance(paths, dict) else None
    operation = path_item.get("post") if isinstance(path_item, dict) else None
    where = f"{relative}: POST {BILLING_ADJUSTMENT_PATH}"
    contracts.check(
        isinstance(operation, dict),
        f"{where}: required billing-adjustment operation is missing",
    )
    if not isinstance(operation, dict):
        return

    parameter_refs, inline_names = _parameter_names(operation)
    for parameter in (
        "TenantHeader",
        "BookHeaderDirectOptional",
        "IfMatch",
        "IdempotencyKey",
    ):
        contracts.check(
            parameter in parameter_refs,
            f"{where}: must document the shared {parameter} parameter",
        )
    contracts.check(
        "policyId" in inline_names,
        f"{where}: must declare the policyId path parameter",
    )

    created = (operation.get("responses") or {}).get("201")
    created_headers = created.get("headers") if isinstance(created, dict) else None
    for header, reference in (
        ("ETag", "ETag"),
        ("Idempotent-Replayed", "IdempotentReplayed"),
    ):
        entry = created_headers.get(header) if isinstance(created_headers, dict) else None
        contracts.check(
            isinstance(entry, dict)
            and str(entry.get("$ref", "")).endswith(f"/headers/{reference}"),
            f"{where}: 201 must declare the shared {header} header",
        )

    description = str(operation.get("description") or "")
    for term in (
        "adjustmentAmount",
        "newTotalPremium",
        "creditedAmount",
        *BILLING_ADJUSTMENT_CODES,
        "INVALID_ADJUSTMENT_DUE_DATE",
        "INVALID_ADJUSTMENT_REASON",
        BILLING_ADJUSTMENT_EVENT,
        "same transaction",
        "ETag",
    ):
        contracts.check(
            term in description,
            f"{where}: description must document {term}",
        )

    planned_operations = document.get("x-planned-operations") or []
    planned_pairs = {
        (str(entry.get("method", "")).lower(), entry.get("path"))
        for entry in planned_operations
        if isinstance(entry, dict)
    }
    contracts.check(
        ("post", BILLING_ADJUSTMENT_PATH) not in planned_pairs,
        f"{relative}: implemented billing-adjustment operation must not reappear "
        "under x-planned-operations",
    )

    request = schemas.get(BILLING_ADJUSTMENT_REQUEST) or {}
    request_properties = request.get("properties") or {}
    request_required = set(request.get("required") or [])
    contracts.check(
        isinstance(request, dict) and request.get("type") == "object",
        f"{relative}: {BILLING_ADJUSTMENT_REQUEST} must be an object schema",
    )
    contracts.check(
        request_required == set(BILLING_ADJUSTMENT_REQUEST_FIELDS),
        f"{relative}: {BILLING_ADJUSTMENT_REQUEST} must require exactly "
        f"{list(BILLING_ADJUSTMENT_REQUEST_FIELDS)}",
    )
    for field in BILLING_ADJUSTMENT_REQUEST_FIELDS:
        contracts.check(
            field in request_properties,
            f"{relative}: {BILLING_ADJUSTMENT_REQUEST}.properties.{field} is "
            "required",
        )
    contracts.check(
        (request_properties.get("dueDate") or {}).get("format") == "date",
        f"{relative}: {BILLING_ADJUSTMENT_REQUEST}.dueDate must be a date",
    )
    reason = request_properties.get("reason") or {}
    contracts.check(
        reason.get("type") == "string"
        and reason.get("minLength") == 1
        and reason.get("maxLength") == BILLING_ADJUSTMENT_REASON_MAX_LENGTH,
        f"{relative}: {BILLING_ADJUSTMENT_REQUEST}.reason must be a non-blank "
        f"string of at most {BILLING_ADJUSTMENT_REASON_MAX_LENGTH} characters",
    )

    result = schemas.get(BILLING_ADJUSTMENT_RESULT) or {}
    result_properties = result.get("properties") or {}
    result_required = set(result.get("required") or [])
    contracts.check(
        isinstance(result, dict) and result.get("type") == "object",
        f"{relative}: {BILLING_ADJUSTMENT_RESULT} must be an object schema",
    )
    contracts.check(
        result_required == set(BILLING_ADJUSTMENT_RESULT_FIELDS),
        f"{relative}: {BILLING_ADJUSTMENT_RESULT} must require exactly "
        f"{list(BILLING_ADJUSTMENT_RESULT_FIELDS)}",
    )
    for field in BILLING_ADJUSTMENT_RESULT_FIELDS:
        contracts.check(
            field in result_properties,
            f"{relative}: {BILLING_ADJUSTMENT_RESULT}.properties.{field} is "
            "required",
        )
    for field, schema_name in (
        ("plan", "BillingPlan"),
        ("installment", "Installment"),
    ):
        contracts.check(
            str((result_properties.get(field) or {}).get("$ref", "")).endswith(
                f"/schemas/{schema_name}"
            ),
            f"{relative}: {BILLING_ADJUSTMENT_RESULT}.{field} must reference "
            f"{schema_name}",
        )
    for field in ("adjustmentAmount", "newTotalPremium"):
        contracts.check(
            str((result_properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: {BILLING_ADJUSTMENT_RESULT}.{field} must reference "
            "MoneyAmount",
        )


# ---------------------------------------------------------------------------
# Policy premium-receivables checks
# ---------------------------------------------------------------------------


def check_policy_receivables_openapi(contracts: ContractSet, document, relative: str):
    """Require the cross-policy receivables queue, schemas, and query rules."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    for method, receivable_path, response_schema_name in RECEIVABLE_OPENAPI_PATHS:
        path_item = paths.get(receivable_path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {receivable_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required receivable operation is missing",
        )
        if not isinstance(operation, dict):
            continue

        parameter_refs, _ = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must require the shared TenantHeader",
        )
        contracts.check(
            "BookHeaderDirectOptional" in parameter_refs,
            f"{where}: must document the shared BookHeaderDirectOptional parameter",
        )
        contracts.check(
            not any(
                isinstance(parameter, dict) and parameter.get("in") == "path"
                for parameter in operation.get("parameters") or []
            ),
            f"{where}: is a cross-policy read and must not declare a path parameter",
        )

        description = str(operation.get("description") or "")
        contracts.check(
            "outside" in description.lower() and "/api/v1/policies" in description,
            f"{where}: description must note that the route is outside /api/v1/policies",
        )
        contracts.check(
            "BOOK_SCOPE_VIOLATION" in description,
            f"{where}: description must document the 404 BOOK_SCOPE_VIOLATION book wall",
        )
        contracts.check(
            "INVALID_INSTALLMENT_STATUS" in description,
            f"{where}: description must document INVALID_INSTALLMENT_STATUS",
        )
        contracts.check(
            "VALIDATION_ERROR" in description,
            f"{where}: description must document the limit VALIDATION_ERROR",
        )
        for term in ("creditedAmount", "outstandingAmount"):
            contracts.check(
                term in description,
                f"{where}: description must document {term}",
            )

        status_parameter = _inline_parameter(operation, "status")
        contracts.check(
            isinstance(status_parameter, dict)
            and status_parameter.get("in") == "query"
            and status_parameter.get("required") is False,
            f"{where}: must declare an optional query parameter status",
        )
        contracts.check(
            set(((status_parameter or {}).get("schema") or {}).get("enum") or [])
            == set(RECEIVABLE_STATUSES),
            f"{where}: status must enumerate {list(RECEIVABLE_STATUSES)}",
        )

        due_before = _inline_parameter(operation, "dueBefore")
        contracts.check(
            isinstance(due_before, dict)
            and due_before.get("in") == "query"
            and due_before.get("required") is False
            and (due_before.get("schema") or {}).get("format") == "date",
            f"{where}: must declare an optional date query parameter dueBefore",
        )

        limit_parameter = _inline_parameter(operation, "limit")
        limit_schema = (limit_parameter or {}).get("schema") or {}
        contracts.check(
            isinstance(limit_parameter, dict)
            and limit_parameter.get("in") == "query"
            and limit_parameter.get("required") is False,
            f"{where}: must declare an optional query parameter limit",
        )
        contracts.check(
            (
                limit_schema.get("type"),
                limit_schema.get("minimum"),
                limit_schema.get("maximum"),
                limit_schema.get("default"),
            )
            == (
                "integer",
                RECEIVABLE_MIN_LIMIT,
                RECEIVABLE_MAX_LIMIT,
                RECEIVABLE_DEFAULT_LIMIT,
            ),
            f"{where}: limit must be an integer {RECEIVABLE_MIN_LIMIT}.."
            f"{RECEIVABLE_MAX_LIMIT} defaulting to {RECEIVABLE_DEFAULT_LIMIT}",
        )

        responses = operation.get("responses") or {}
        contracts.check(
            "400" in responses,
            f"{where}: must document the 400 response",
        )
        contracts.check(
            "404" in responses,
            f"{where}: must document the 404 response",
        )
        bad_request = responses.get("400")
        contracts.check(
            isinstance(bad_request, dict)
            and str(bad_request.get("$ref", "")).endswith("/responses/BadRequest"),
            f"{where}: 400 must reference the shared BadRequest",
        )
        not_found = responses.get("404")
        contracts.check(
            isinstance(not_found, dict)
            and str(not_found.get("$ref", "")).endswith("/responses/NotFound"),
            f"{where}: 404 must reference the shared NotFound",
        )
        ok_schema = _response_schema(operation, "200")
        contracts.check(
            isinstance(ok_schema, dict)
            and str(ok_schema.get("$ref", "")).endswith(
                f"/schemas/{response_schema_name}"
            ),
            f"{where}: 200 must return the {response_schema_name} schema",
        )

    receivable = schemas.get("Receivable") or {}
    receivable_properties = receivable.get("properties") or {}
    receivable_required = set(receivable.get("required") or [])
    contracts.check(
        isinstance(receivable, dict) and receivable.get("type") == "object",
        f"{relative}: Receivable must be an object schema",
    )
    for field in RECEIVABLE_FIELDS:
        contracts.check(
            field in receivable_properties,
            f"{relative}: Receivable.properties.{field} is required",
        )
    contracts.check(
        set(RECEIVABLE_REQUIRED_FIELDS) == receivable_required,
        f"{relative}: Receivable.required must list the non-nullable receivable fields",
    )
    for field in ("installmentId", "planId", "policyId", "insuredPartyId"):
        contracts.check(
            (receivable_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: Receivable.{field} must be a uuid",
        )
    for field in ("planNumber", "policyNumber"):
        contracts.check(
            (
                (receivable_properties.get(field) or {}).get("type"),
                (receivable_properties.get(field) or {}).get("maxLength"),
            )
            == ("string", 32),
            f"{relative}: Receivable.{field} must be a string of at most 32 characters",
        )
    installment_number = receivable_properties.get("installmentNumber") or {}
    contracts.check(
        (installment_number.get("type"), installment_number.get("minimum"))
        == ("integer", 1),
        f"{relative}: Receivable.installmentNumber must be an integer >= 1",
    )
    contracts.check(
        (receivable_properties.get("dueDate") or {}).get("format") == "date",
        f"{relative}: Receivable.dueDate must be a date",
    )
    contracts.check(
        str((receivable_properties.get("amount") or {}).get("$ref", "")).endswith(
            "/schemas/MoneyAmount"
        ),
        f"{relative}: Receivable.amount must reference MoneyAmount",
    )
    for field in ("creditedAmount", "outstandingAmount"):
        contracts.check(
            str((receivable_properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: Receivable.{field} must reference MoneyAmount",
        )
    contracts.check(
        str((receivable_properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: Receivable.currency must reference CurrencyCode",
    )
    contracts.check(
        set((receivable_properties.get("status") or {}).get("enum") or [])
        == set(RECEIVABLE_STATUSES),
        f"{relative}: Receivable.status must enumerate {list(RECEIVABLE_STATUSES)}",
    )
    days_past_due = receivable_properties.get("daysPastDue") or {}
    contracts.check(
        (days_past_due.get("type"), days_past_due.get("minimum")) == ("integer", 0),
        f"{relative}: Receivable.daysPastDue must be an integer >= 0",
    )
    paid_at = receivable_properties.get("paidAt") or {}
    contracts.check(
        _schema_types(paid_at) == {"string", "null"}
        and paid_at.get("format") == "date-time",
        f"{relative}: Receivable.paidAt must be a nullable date-time",
    )
    payment_id = receivable_properties.get("paymentId") or {}
    contracts.check(
        _schema_types(payment_id) == {"string", "null"}
        and payment_id.get("format") == "uuid",
        f"{relative}: Receivable.paymentId must be a nullable uuid",
    )

    summary = schemas.get("ReceivableSummary") or {}
    summary_properties = summary.get("properties") or {}
    summary_required = set(summary.get("required") or [])
    contracts.check(
        isinstance(summary, dict) and summary.get("type") == "object",
        f"{relative}: ReceivableSummary must be an object schema",
    )
    for field in RECEIVABLE_SUMMARY_FIELDS:
        contracts.check(
            field in summary_properties,
            f"{relative}: ReceivableSummary.properties.{field} is required",
        )
        contracts.check(
            field in summary_required,
            f"{relative}: ReceivableSummary.required must list {field}",
        )
    items = summary_properties.get("items") or {}
    contracts.check(
        items.get("type") == "array"
        and str((items.get("items") or {}).get("$ref", "")).endswith(
            "/schemas/Receivable"
        ),
        f"{relative}: ReceivableSummary.items must be an array of Receivable",
    )
    for field in ("totalAmount", "overdueAmount"):
        contracts.check(
            str((summary_properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: ReceivableSummary.{field} must reference MoneyAmount",
        )
    summary_text = str(summary.get("description") or "")
    contracts.check(
        "outstanding" in summary_text,
        f"{relative}: ReceivableSummary must document outstanding-based totals",
    )
    count = summary_properties.get("count") or {}
    contracts.check(
        (count.get("type"), count.get("minimum")) == ("integer", 0),
        f"{relative}: ReceivableSummary.count must be an integer >= 0",
    )


# ---------------------------------------------------------------------------
# Policy installment-dunning checks
# ---------------------------------------------------------------------------


def check_policy_dunning_openapi(contracts: ContractSet, document, relative: str):
    """Require the installment dunning operations, schemas, and field rules."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    for method in ("get", "post"):
        path_item = paths.get(DUNNING_PATH) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {DUNNING_PATH}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required dunning operation is missing",
        )
        if not isinstance(operation, dict):
            continue

        parameter_refs, inline_names = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must require the shared TenantHeader",
        )
        contracts.check(
            "BookHeaderDirect" in parameter_refs,
            f"{where}: must require the shared BookHeaderDirect parameter",
        )
        contracts.check(
            "installmentId" in inline_names,
            f"{where}: must declare the installmentId path parameter",
        )
        installment_parameter = _inline_parameter(operation, "installmentId")
        contracts.check(
            isinstance(installment_parameter, dict)
            and installment_parameter.get("in") == "path"
            and installment_parameter.get("required") is True
            and (installment_parameter.get("schema") or {}).get("format") == "uuid",
            f"{where}: installmentId must be a required uuid path parameter",
        )

        responses = operation.get("responses") or {}
        contracts.check("400" in responses, f"{where}: must document the 400 response")
        contracts.check("404" in responses, f"{where}: must document the 404 response")
        for code, component in (("400", "BadRequest"), ("404", "NotFound")):
            response = responses.get(code)
            contracts.check(
                isinstance(response, dict)
                and str(response.get("$ref", "")).endswith(
                    f"/responses/{component}"
                ),
                f"{where}: {code} must reference the shared {component}",
            )

        description = str(operation.get("description") or "")
        contracts.check(
            "INSTALLMENT_NOT_FOUND" in description,
            f"{where}: description must document INSTALLMENT_NOT_FOUND",
        )
        contracts.check(
            "BOOK_SCOPE_VIOLATION" in description,
            f"{where}: description must document the 404 BOOK_SCOPE_VIOLATION "
            "book wall",
        )

        if method == "get":
            ok_schema = _response_schema(operation, "200")
            contracts.check(
                isinstance(ok_schema, dict)
                and ok_schema.get("type") == "array"
                and str((ok_schema.get("items") or {}).get("$ref", "")).endswith(
                    "/schemas/DunningAction"
                ),
                f"{where}: 200 must return an array of DunningAction",
            )
        else:
            contracts.check("409" in responses, f"{where}: must document the 409 response")
            conflict = responses.get("409")
            contracts.check(
                isinstance(conflict, dict)
                and str(conflict.get("$ref", "")).endswith("/responses/Conflict"),
                f"{where}: 409 must reference the shared Conflict",
            )
            for code in DUNNING_CONFLICT_CODES:
                contracts.check(
                    code in description,
                    f"{where}: description must document the 409 {code}",
                )
            contracts.check(
                "CREDITED" in description,
                f"{where}: description must document CREDITED as a terminal, "
                "non-dunnable installment status",
            )

            request_body = operation.get("requestBody") or {}
            contracts.check(
                request_body.get("required") is True,
                f"{where}: request body must be required",
            )
            request_schema = (
                ((request_body.get("content") or {}).get("application/json") or {})
                .get("schema")
                if isinstance(request_body, dict)
                else None
            )
            contracts.check(
                isinstance(request_schema, dict)
                and str(request_schema.get("$ref", "")).endswith(
                    "/schemas/CreateDunningRequest"
                ),
                f"{where}: request body must use the CreateDunningRequest schema",
            )
            success_schema = _response_schema(operation, "201")
            contracts.check(
                isinstance(success_schema, dict)
                and str(success_schema.get("$ref", "")).endswith(
                    "/schemas/DunningAction"
                ),
                f"{where}: 201 must return the DunningAction schema",
            )

    dunning = schemas.get("DunningAction") or {}
    dunning_properties = dunning.get("properties") or {}
    dunning_required = set(dunning.get("required") or [])
    contracts.check(
        isinstance(dunning, dict) and dunning.get("type") == "object",
        f"{relative}: DunningAction must be an object schema",
    )
    for field in DUNNING_FIELDS:
        contracts.check(
            field in dunning_properties,
            f"{relative}: DunningAction.properties.{field} is required",
        )
    contracts.check(
        dunning_required == set(DUNNING_REQUIRED_FIELDS),
        f"{relative}: DunningAction.required must list the non-nullable action fields",
    )
    for field in ("dunningId", "installmentId", "planId", "policyId"):
        contracts.check(
            (dunning_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: DunningAction.{field} must be a uuid",
        )
    contracts.check(
        tuple((dunning_properties.get("level") or {}).get("enum") or [])
        == DUNNING_LEVELS,
        f"{relative}: DunningAction.level must enumerate {list(DUNNING_LEVELS)}",
    )
    contracts.check(
        tuple((dunning_properties.get("channel") or {}).get("enum") or [])
        == DUNNING_CHANNELS,
        f"{relative}: DunningAction.channel must enumerate {list(DUNNING_CHANNELS)}",
    )
    dunning_notes = dunning_properties.get("notes") or {}
    contracts.check(
        _schema_types(dunning_notes) == {"string", "null"}
        and dunning_notes.get("maxLength") == DUNNING_NOTES_MAX_LENGTH,
        f"{relative}: DunningAction.notes must be a nullable string of at most "
        f"{DUNNING_NOTES_MAX_LENGTH} characters",
    )
    contracts.check(
        "notes" not in dunning_required,
        f"{relative}: DunningAction.notes must stay optional",
    )
    contracts.check(
        tuple((dunning_properties.get("status") or {}).get("enum") or [])
        == DUNNING_STATUSES,
        f"{relative}: DunningAction.status must enumerate {list(DUNNING_STATUSES)}",
    )
    contracts.check(
        (dunning_properties.get("sentAt") or {}).get("format") == "date-time",
        f"{relative}: DunningAction.sentAt must be a date-time",
    )

    create = schemas.get("CreateDunningRequest") or {}
    create_properties = create.get("properties") or {}
    create_required = set(create.get("required") or [])
    contracts.check(
        isinstance(create, dict) and create.get("type") == "object",
        f"{relative}: CreateDunningRequest must be an object schema",
    )
    for field in DUNNING_REQUEST_FIELDS:
        contracts.check(
            field in create_properties,
            f"{relative}: CreateDunningRequest.properties.{field} is required",
        )
    contracts.check(
        create_required == set(DUNNING_REQUEST_REQUIRED_FIELDS),
        f"{relative}: CreateDunningRequest.required must list level and channel",
    )
    contracts.check(
        tuple((create_properties.get("level") or {}).get("enum") or [])
        == DUNNING_LEVELS,
        f"{relative}: CreateDunningRequest.level must enumerate "
        f"{list(DUNNING_LEVELS)}",
    )
    contracts.check(
        tuple((create_properties.get("channel") or {}).get("enum") or [])
        == DUNNING_CHANNELS,
        f"{relative}: CreateDunningRequest.channel must enumerate "
        f"{list(DUNNING_CHANNELS)}",
    )
    create_notes = create_properties.get("notes") or {}
    contracts.check(
        _schema_types(create_notes) == {"string", "null"}
        and create_notes.get("maxLength") == DUNNING_NOTES_MAX_LENGTH,
        f"{relative}: CreateDunningRequest.notes must be a nullable string of at "
        f"most {DUNNING_NOTES_MAX_LENGTH} characters",
    )
    contracts.check(
        "notes" not in create_required,
        f"{relative}: CreateDunningRequest.notes must stay optional",
    )
    contracts.check(
        set(create_properties) == set(DUNNING_REQUEST_FIELDS),
        f"{relative}: CreateDunningRequest must not accept server-owned fields "
        f"beyond {list(DUNNING_REQUEST_FIELDS)}",
    )

    receivable = schemas.get("Receivable") or {}
    receivable_properties = receivable.get("properties") or {}
    receivable_required = set(receivable.get("required") or [])
    last_level = receivable_properties.get("lastDunningLevel") or {}
    contracts.check(
        _schema_types(last_level) == {"string", "null"}
        and last_level.get("maxLength") == 16,
        f"{relative}: Receivable.lastDunningLevel must be a nullable string of at "
        "most 16 characters",
    )
    last_at = receivable_properties.get("lastDunningAt") or {}
    contracts.check(
        _schema_types(last_at) == {"string", "null"}
        and last_at.get("format") == "date-time",
        f"{relative}: Receivable.lastDunningAt must be a nullable date-time",
    )
    for field in ("lastDunningLevel", "lastDunningAt"):
        contracts.check(
            field not in receivable_required,
            f"{relative}: Receivable.{field} must stay optional",
        )


# ---------------------------------------------------------------------------
# Policy renewal checks
# ---------------------------------------------------------------------------


def check_policy_renewal_openapi(contracts: ContractSet, document, relative: str):
    """Require the renewal operation, its schemas, responses, and lineage field."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    path_item = paths.get(POLICY_RENEWAL_PATH) if isinstance(paths, dict) else None
    operation = path_item.get("post") if isinstance(path_item, dict) else None
    where = f"{relative}: POST {POLICY_RENEWAL_PATH}"
    contracts.check(
        isinstance(operation, dict),
        f"{where}: required renewal operation is missing",
    )
    if isinstance(operation, dict):
        parameter_refs, inline_names = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must require the shared TenantHeader",
        )
        contracts.check(
            "BookHeaderDirect" in parameter_refs,
            f"{where}: must require the shared BookHeaderDirect parameter",
        )
        contracts.check(
            "policyId" in inline_names,
            f"{where}: must declare the policyId path parameter",
        )

        request_body = operation.get("requestBody") or {}
        contracts.check(
            request_body.get("required") is True,
            f"{where}: request body must be required",
        )
        request_schema = (
            ((request_body.get("content") or {}).get("application/json") or {}).get("schema")
            if isinstance(request_body, dict)
            else None
        )
        contracts.check(
            isinstance(request_schema, dict)
            and str(request_schema.get("$ref", "")).endswith("/schemas/RenewPolicyRequest"),
            f"{where}: request body must use the RenewPolicyRequest schema",
        )

        created = (operation.get("responses") or {}).get("201")
        created_headers = created.get("headers") if isinstance(created, dict) else None
        tag = created_headers.get("ETag") if isinstance(created_headers, dict) else None
        contracts.check(
            isinstance(tag, dict)
            and str(tag.get("$ref", "")).endswith("/headers/ETag"),
            f"{where}: 201 must declare the shared ETag header",
        )
        created_schema = _response_schema(operation, "201")
        contracts.check(
            isinstance(created_schema, dict)
            and str(created_schema.get("$ref", "")).endswith("/schemas/Policy"),
            f"{where}: 201 must return the successor Policy schema",
        )

        responses = operation.get("responses") or {}
        for code, suffix in (("400", "BadRequest"), ("404", "NotFound")):
            response = responses.get(code) if isinstance(responses, dict) else None
            contracts.check(
                isinstance(response, dict)
                and str(response.get("$ref", "")).endswith(f"/responses/{suffix}"),
                f"{where}: {code} must reference the shared {suffix} response",
            )
        conflict = responses.get("409") if isinstance(responses, dict) else None
        conflict_text = (
            str(conflict.get("description") or "") if isinstance(conflict, dict) else ""
        )
        contracts.check(
            "RENEWAL_NOT_ALLOWED" in conflict_text,
            f"{where}: 409 must document RENEWAL_NOT_ALLOWED",
        )
        conflict_schema = _response_schema(operation, "409", "application/problem+json")
        contracts.check(
            isinstance(conflict_schema, dict)
            and str(conflict_schema.get("$ref", "")).endswith("/schemas/Problem"),
            f"{where}: 409 must document the shared Problem schema",
        )

        description = str(operation.get("description") or "")
        for status in POLICY_RENEWAL_ALLOWED_STATUSES:
            contracts.check(
                status in description,
                f"{where}: description must name the renewable source status {status}",
            )
        contracts.check(
            POLICY_RENEWAL_EVENT in description,
            f"{where}: description must name {POLICY_RENEWAL_EVENT}",
        )

    request = schemas.get("RenewPolicyRequest") or {}
    request_properties = request.get("properties") or {}
    request_required = set(request.get("required") or [])
    contracts.check(
        isinstance(request, dict) and request.get("type") == "object",
        f"{relative}: RenewPolicyRequest must be an object schema",
    )
    for field in POLICY_RENEWAL_REQUIRED_FIELDS:
        contracts.check(
            field in request_properties,
            f"{relative}: RenewPolicyRequest.properties.{field} is required",
        )
        contracts.check(
            field in request_required,
            f"{relative}: RenewPolicyRequest.required must list {field}",
        )
        contracts.check(
            (request_properties.get(field) or {}).get("format") == "date",
            f"{relative}: RenewPolicyRequest.{field} must be a date",
        )
    for field in POLICY_RENEWAL_OPTIONAL_FIELDS:
        contracts.check(
            field in request_properties,
            f"{relative}: RenewPolicyRequest.properties.{field} is required",
        )
        contracts.check(
            field not in request_required,
            f"{relative}: RenewPolicyRequest.{field} must stay optional",
        )
    for field in ("premiumAmount", "limitAmount"):
        contracts.check(
            str((request_properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: RenewPolicyRequest.{field} must reference MoneyAmount",
        )
    for field in ("premiumCurrency", "limitCurrency"):
        contracts.check(
            str((request_properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/CurrencyCode"
            ),
            f"{relative}: RenewPolicyRequest.{field} must reference CurrencyCode",
        )

    policy = schemas.get("Policy") or {}
    policy_properties = policy.get("properties") or {}
    policy_required = set(policy.get("required") or [])
    lineage = policy_properties.get("renewedFromPolicyId")
    contracts.check(
        isinstance(lineage, dict),
        f"{relative}: Policy.renewedFromPolicyId is required",
    )
    if isinstance(lineage, dict):
        contracts.check(
            _schema_types(lineage) == {"string", "null"},
            f"{relative}: Policy.renewedFromPolicyId must be a nullable string",
        )
        contracts.check(
            lineage.get("format") == "uuid",
            f"{relative}: Policy.renewedFromPolicyId must be a uuid",
        )
    contracts.check(
        "renewedFromPolicyId" not in policy_required,
        f"{relative}: Policy.renewedFromPolicyId must stay optional",
    )


# ---------------------------------------------------------------------------
# Policy mass tort profile checks
# ---------------------------------------------------------------------------


def check_policy_mass_tort_profile_openapi(contracts: ContractSet, document, relative: str):
    """Require the mass tort profile operations, schemas, enums, and event."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    path_item = paths.get(MASS_TORT_PROFILE_PATH) if isinstance(paths, dict) else None
    get_operation = path_item.get("get") if isinstance(path_item, dict) else None
    put_operation = path_item.get("put") if isinstance(path_item, dict) else None
    where_get = f"{relative}: GET {MASS_TORT_PROFILE_PATH}"
    where_put = f"{relative}: PUT {MASS_TORT_PROFILE_PATH}"
    contracts.check(
        isinstance(get_operation, dict),
        f"{where_get}: required mass tort profile operation is missing",
    )
    contracts.check(
        isinstance(put_operation, dict),
        f"{where_put}: required mass tort profile upsert operation is missing",
    )

    for operation, where in ((get_operation, where_get), (put_operation, where_put)):
        if not isinstance(operation, dict):
            continue
        parameter_refs, inline_names = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must require the shared TenantHeader",
        )
        contracts.check(
            "BookHeaderDirectOptional" in parameter_refs,
            f"{where}: must document the shared BookHeaderDirectOptional parameter",
        )
        contracts.check(
            "policyId" in inline_names,
            f"{where}: must declare the policyId path parameter",
        )
        responses = operation.get("responses") or {}
        for code, suffix in (("400", "BadRequest"), ("404", "NotFound")):
            response = responses.get(code) if isinstance(responses, dict) else None
            contracts.check(
                isinstance(response, dict)
                and str(response.get("$ref", "")).endswith(f"/responses/{suffix}"),
                f"{where}: {code} must reference the shared {suffix} response",
            )

    if isinstance(get_operation, dict):
        contracts.check(
            "requestBody" not in get_operation,
            f"{where_get}: the read operation must not declare a request body",
        )
        get_schema = _response_schema(get_operation, "200")
        contracts.check(
            isinstance(get_schema, dict)
            and str(get_schema.get("$ref", "")).endswith("/schemas/MassTortProfile"),
            f"{where_get}: 200 must return the MassTortProfile schema",
        )
        get_description = str(get_operation.get("description") or "")
        contracts.check(
            "MASS_TORT_PROFILE_NOT_FOUND" in get_description,
            f"{where_get}: description must document MASS_TORT_PROFILE_NOT_FOUND",
        )
        contracts.check(
            "DIRECT" in get_description,
            f"{where_get}: description must document the DIRECT book rule",
        )

    if isinstance(put_operation, dict):
        request_body = put_operation.get("requestBody") or {}
        contracts.check(
            request_body.get("required") is True,
            f"{where_put}: request body must be required",
        )
        request_schema = (
            ((request_body.get("content") or {}).get("application/json") or {}).get("schema")
            if isinstance(request_body, dict)
            else None
        )
        contracts.check(
            isinstance(request_schema, dict)
            and str(request_schema.get("$ref", "")).endswith(
                "/schemas/UpdateMassTortProfileRequest"
            ),
            f"{where_put}: request body must use the UpdateMassTortProfileRequest schema",
        )
        for code in ("200", "201"):
            success_schema = _response_schema(put_operation, code)
            contracts.check(
                isinstance(success_schema, dict)
                and str(success_schema.get("$ref", "")).endswith("/schemas/MassTortProfile"),
                f"{where_put}: {code} must return the MassTortProfile schema",
            )
        responses = put_operation.get("responses") or {}
        conflict = responses.get("409") if isinstance(responses, dict) else None
        contracts.check(
            isinstance(conflict, dict)
            and str(conflict.get("$ref", "")).endswith("/responses/Conflict"),
            f"{where_put}: 409 must reference the shared Conflict response",
        )
        put_description = str(put_operation.get("description") or "")
        contracts.check(
            "MASS_TORT_PROFILE_ALREADY_EXISTS" in put_description,
            f"{where_put}: description must document MASS_TORT_PROFILE_ALREADY_EXISTS",
        )
        contracts.check(
            MASS_TORT_EVENT in put_description,
            f"{where_put}: description must name {MASS_TORT_EVENT}",
        )

    for schema_name in MASS_TORT_PROFILE_SCHEMAS:
        contracts.check(
            schema_name in schemas,
            f"{relative}: required mass tort schema {schema_name} is missing",
        )

    profile = schemas.get("MassTortProfile") or {}
    profile_properties = profile.get("properties") or {}
    profile_required = set(profile.get("required") or [])
    contracts.check(
        isinstance(profile, dict) and profile.get("type") == "object",
        f"{relative}: MassTortProfile must be an object schema",
    )
    for field in MASS_TORT_PROFILE_FIELDS:
        contracts.check(
            field in profile_properties,
            f"{relative}: MassTortProfile.properties.{field} is required",
        )
        contracts.check(
            field in profile_required,
            f"{relative}: MassTortProfile.required must list {field}",
        )
    for field in ("profileId", "policyId"):
        contracts.check(
            (profile_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: MassTortProfile.{field} must be a uuid",
        )
    for field, enum_name in (
        ("tortType", "MassTortTortType"),
        ("triggerType", "MassTortTriggerType"),
        ("allocationMethod", "MassTortAllocationMethod"),
        ("status", "MassTortProfileStatus"),
    ):
        contracts.check(
            str((profile_properties.get(field) or {}).get("$ref", "")).endswith(
                f"/schemas/{enum_name}"
            ),
            f"{relative}: MassTortProfile.{field} must reference {enum_name}",
        )
    notes = profile_properties.get("allocationNotes") or {}
    contracts.check(
        _schema_types(notes) == {"string", "null"},
        f"{relative}: MassTortProfile.allocationNotes must be a nullable string",
    )
    contracts.check(
        notes.get("maxLength") == MASS_TORT_NOTES_MAX_LENGTH,
        f"{relative}: MassTortProfile.allocationNotes maxLength must be "
        f"{MASS_TORT_NOTES_MAX_LENGTH}",
    )
    for field in ("coverageBlockStart", "coverageBlockEnd"):
        field_schema = profile_properties.get(field) or {}
        contracts.check(
            _schema_types(field_schema) == {"string", "null"},
            f"{relative}: MassTortProfile.{field} must be a nullable string",
        )
        contracts.check(
            field_schema.get("format") == "date",
            f"{relative}: MassTortProfile.{field} must be a date",
        )
    updated_at = profile_properties.get("updatedAt") or {}
    contracts.check(
        _schema_types(updated_at) == {"string"}
        and updated_at.get("format") == "date-time",
        f"{relative}: MassTortProfile.updatedAt must be a date-time",
    )

    for name, expected in (
        ("MassTortTortType", MASS_TORT_TORT_TYPES),
        ("MassTortTriggerType", MASS_TORT_TRIGGER_TYPES),
        ("MassTortAllocationMethod", MASS_TORT_ALLOCATION_METHODS),
        ("MassTortProfileStatus", MASS_TORT_PROFILE_STATUSES),
    ):
        schema = schemas.get(name) or {}
        contracts.check(
            isinstance(schema, dict) and schema.get("type") == "string",
            f"{relative}: {name} must be a string schema",
        )
        contracts.check(
            set(schema.get("enum") or []) == set(expected),
            f"{relative}: {name}.enum must be {list(expected)}",
        )

    request = schemas.get("UpdateMassTortProfileRequest") or {}
    request_properties = request.get("properties") or {}
    request_required = set(request.get("required") or [])
    contracts.check(
        isinstance(request, dict) and request.get("type") == "object",
        f"{relative}: UpdateMassTortProfileRequest must be an object schema",
    )
    for field in MASS_TORT_UPDATE_REQUIRED_FIELDS:
        contracts.check(
            field in request_properties,
            f"{relative}: UpdateMassTortProfileRequest.properties.{field} is required",
        )
        contracts.check(
            field in request_required,
            f"{relative}: UpdateMassTortProfileRequest.required must list {field}",
        )
    for field in MASS_TORT_UPDATE_OPTIONAL_FIELDS:
        contracts.check(
            field in request_properties,
            f"{relative}: UpdateMassTortProfileRequest.properties.{field} is required",
        )
        contracts.check(
            field not in request_required,
            f"{relative}: UpdateMassTortProfileRequest.{field} must stay optional",
        )
    for field, enum_name in (
        ("tortType", "MassTortTortType"),
        ("triggerType", "MassTortTriggerType"),
        ("allocationMethod", "MassTortAllocationMethod"),
        ("status", "MassTortProfileStatus"),
    ):
        contracts.check(
            str((request_properties.get(field) or {}).get("$ref", "")).endswith(
                f"/schemas/{enum_name}"
            ),
            f"{relative}: UpdateMassTortProfileRequest.{field} must reference {enum_name}",
        )
    request_notes = request_properties.get("allocationNotes") or {}
    contracts.check(
        _schema_types(request_notes) == {"string", "null"},
        f"{relative}: UpdateMassTortProfileRequest.allocationNotes must be a nullable string",
    )
    contracts.check(
        request_notes.get("maxLength") == MASS_TORT_NOTES_MAX_LENGTH,
        f"{relative}: UpdateMassTortProfileRequest.allocationNotes maxLength must be "
        f"{MASS_TORT_NOTES_MAX_LENGTH}",
    )
    for field in ("coverageBlockStart", "coverageBlockEnd"):
        contracts.check(
            (request_properties.get(field) or {}).get("format") == "date",
            f"{relative}: UpdateMassTortProfileRequest.{field} must be a date",
        )

    planned = document.get("x-planned-operations") or []
    contracts.check(
        not any(
            isinstance(entry, dict) and entry.get("path") == MASS_TORT_PROFILE_PATH
            for entry in planned
        ),
        f"{relative}: {MASS_TORT_PROFILE_PATH} must not remain in x-planned-operations",
    )


# ---------------------------------------------------------------------------
# Policy program checks
# ---------------------------------------------------------------------------


def check_policy_programs(contracts: ContractSet, document, relative: str):
    """Require the program catalog routes, schemas, and membership command.

    The four public operations are mandatory and tenant/DIRECT scoped. The
    projection carries the fourteen fields, including the optional capacity
    pair and the derived ``usedAmount``/``utilizationPct``/``policyCount``; the
    create body is ``CreateProgramRequest`` with the both-or-neither capacity
    pair, and the PATCH body is ``UpdatePolicyProgramRequest`` with a nullable
    ``programId``. ``Policy.programId`` must stay nullable and optional so a
    policy outside a program remains valid, and the implemented catalog paths
    must not remain in ``x-planned-operations``.
    """
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    program = schemas.get("Program") or {}
    properties = program.get("properties") or {}
    required = set(program.get("required") or [])
    contracts.check(
        isinstance(program, dict) and program.get("type") == "object",
        f"{relative}: Program must be an object schema",
    )
    for field in POLICY_PROGRAM_FIELDS:
        contracts.check(
            isinstance(properties.get(field), dict),
            f"{relative}: Program.{field} is required",
        )
        contracts.check(
            field in required,
            f"{relative}: Program.required must list {field}",
        )
    contracts.check(
        _schema_types(properties.get("programId")) == {"string"}
        and (properties.get("programId") or {}).get("format") == "uuid",
        f"{relative}: Program.programId must be a uuid",
    )
    contracts.check(
        _schema_types(properties.get("leadPolicyId")) == {"string", "null"}
        and (properties.get("leadPolicyId") or {}).get("format") == "uuid",
        f"{relative}: Program.leadPolicyId must be a nullable uuid",
    )
    contracts.check(
        (
            (properties.get("programNumber") or {}).get("type"),
            (properties.get("programNumber") or {}).get("maxLength"),
        )
        == ("string", POLICY_PROGRAM_NUMBER_MAX_LENGTH),
        f"{relative}: Program.programNumber must be a string of at most "
        f"{POLICY_PROGRAM_NUMBER_MAX_LENGTH} characters",
    )
    contracts.check(
        (
            (properties.get("name") or {}).get("type"),
            (properties.get("name") or {}).get("maxLength"),
        )
        == ("string", POLICY_PROGRAM_NAME_MAX_LENGTH),
        f"{relative}: Program.name must be a string of at most "
        f"{POLICY_PROGRAM_NAME_MAX_LENGTH} characters",
    )
    for field in ("effectiveFrom", "effectiveTo"):
        contracts.check(
            (properties.get(field) or {}).get("format") == "date",
            f"{relative}: Program.{field} must be a date",
        )
    contracts.check(
        (properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: Program.createdAt must be a date-time",
    )
    contracts.check(
        str((properties.get("programType") or {}).get("$ref", "")).endswith(
            "/schemas/ProgramType"
        ),
        f"{relative}: Program.programType must reference ProgramType",
    )
    contracts.check(
        str((properties.get("status") or {}).get("$ref", "")).endswith(
            "/schemas/ProgramStatus"
        ),
        f"{relative}: Program.status must reference ProgramStatus",
    )
    contracts.check(
        _schema_types(properties.get("capacityAmount")) == {"string", "null"}
        and (properties.get("capacityAmount") or {}).get("pattern")
        == POLICY_PROGRAM_CAPACITY_PATTERN,
        f"{relative}: Program.capacityAmount must be a nullable positive money "
        "string",
    )
    contracts.check(
        _schema_types(properties.get("capacityCurrency")) == {"string", "null"}
        and (properties.get("capacityCurrency") or {}).get("pattern")
        == POLICY_PROGRAM_CURRENCY_PATTERN,
        f"{relative}: Program.capacityCurrency must be a nullable three-letter "
        "currency code",
    )
    contracts.check(
        _schema_types(properties.get("usedAmount")) == {"string"}
        and (properties.get("usedAmount") or {}).get("pattern")
        == POLICY_PROGRAM_USED_AMOUNT_PATTERN,
        f"{relative}: Program.usedAmount must be a non-null non-negative money "
        "string",
    )
    contracts.check(
        _schema_types(properties.get("utilizationPct")) == {"string", "null"}
        and (properties.get("utilizationPct") or {}).get("pattern")
        == POLICY_PROGRAM_UTILIZATION_PATTERN,
        f"{relative}: Program.utilizationPct must be a nullable two-decimal "
        "percentage string",
    )
    policy_count = properties.get("policyCount") or {}
    contracts.check(
        _schema_types(policy_count) == {"integer"}
        and policy_count.get("minimum") == 0,
        f"{relative}: Program.policyCount must be an integer >= 0",
    )
    program_description = str(program.get("description") or "")
    for token in ("limitAmount", "usedAmount", "utilizationPct", "policyCount"):
        contracts.check(
            token in program_description,
            f"{relative}: Program description must document {token}",
        )

    for schema_name, expected in (
        ("ProgramType", POLICY_PROGRAM_TYPES),
        ("ProgramStatus", POLICY_PROGRAM_STATUSES),
    ):
        enum_schema = schemas.get(schema_name) or {}
        contracts.check(
            enum_schema.get("type") == "string",
            f"{relative}: {schema_name} must be a string enum",
        )
        contracts.check(
            set(enum_schema.get("enum") or []) == set(expected),
            f"{relative}: {schema_name} must enumerate {list(expected)}",
        )

    create = schemas.get("CreateProgramRequest") or {}
    create_properties = create.get("properties") or {}
    create_required = set(create.get("required") or [])
    contracts.check(
        isinstance(create, dict) and create.get("type") == "object",
        f"{relative}: CreateProgramRequest must be an object schema",
    )
    for field in POLICY_PROGRAM_CREATE_REQUIRED_FIELDS:
        contracts.check(
            isinstance(create_properties.get(field), dict),
            f"{relative}: CreateProgramRequest.{field} is required",
        )
        contracts.check(
            field in create_required,
            f"{relative}: CreateProgramRequest.required must list {field}",
        )
    for field in POLICY_PROGRAM_CREATE_OPTIONAL_FIELDS:
        contracts.check(
            isinstance(create_properties.get(field), dict),
            f"{relative}: CreateProgramRequest.{field} is required",
        )
        contracts.check(
            field not in create_required,
            f"{relative}: CreateProgramRequest.{field} must stay optional",
        )
        contracts.check(
            _schema_types(create_properties.get(field)) == {"string", "null"},
            f"{relative}: CreateProgramRequest.{field} must be a nullable string",
        )
        contracts.check(
            (create_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: CreateProgramRequest.{field} must be a uuid",
        )
    contracts.check(
        str((create_properties.get("programType") or {}).get("$ref", "")).endswith(
            "/schemas/ProgramType"
        ),
        f"{relative}: CreateProgramRequest.programType must reference ProgramType",
    )
    for field in ("effectiveFrom", "effectiveTo"):
        contracts.check(
            (create_properties.get(field) or {}).get("format") == "date",
            f"{relative}: CreateProgramRequest.{field} must be a date",
        )
    for field in ("capacityAmount", "capacityCurrency"):
        contracts.check(
            isinstance(create_properties.get(field), dict),
            f"{relative}: CreateProgramRequest.{field} must be documented",
        )
        contracts.check(
            field not in create_required,
            f"{relative}: CreateProgramRequest.{field} must stay optional",
        )
    capacity_amount = create_properties.get("capacityAmount") or {}
    contracts.check(
        _schema_types(capacity_amount) == {"string"}
        and capacity_amount.get("pattern") == POLICY_PROGRAM_CAPACITY_PATTERN,
        f"{relative}: CreateProgramRequest.capacityAmount must be a positive "
        "money string",
    )
    capacity_currency = create_properties.get("capacityCurrency") or {}
    contracts.check(
        (
            _schema_types(capacity_currency) == {"string"}
            and capacity_currency.get("pattern") == POLICY_PROGRAM_CURRENCY_PATTERN
        )
        or str(capacity_currency.get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: CreateProgramRequest.capacityCurrency must be a "
        "three-letter currency code",
    )
    contracts.check(
        create.get("dependentRequired") == POLICY_PROGRAM_CAPACITY_DEPENDENCIES,
        f"{relative}: CreateProgramRequest must require capacityAmount and "
        "capacityCurrency as a pair",
    )

    update = schemas.get("UpdatePolicyProgramRequest") or {}
    update_properties = update.get("properties") or {}
    contracts.check(
        isinstance(update, dict) and update.get("type") == "object",
        f"{relative}: UpdatePolicyProgramRequest must be an object schema",
    )
    contracts.check(
        "programId" in update_properties,
        f"{relative}: UpdatePolicyProgramRequest.programId is required",
    )
    contracts.check(
        "programId" in set(update.get("required") or []),
        f"{relative}: UpdatePolicyProgramRequest.required must list programId",
    )
    contracts.check(
        _schema_types(update_properties.get("programId")) == {"string", "null"},
        f"{relative}: UpdatePolicyProgramRequest.programId must be a nullable string",
    )
    contracts.check(
        (update_properties.get("programId") or {}).get("format") == "uuid",
        f"{relative}: UpdatePolicyProgramRequest.programId must be a uuid",
    )

    policy = schemas.get("Policy") or {}
    policy_properties = policy.get("properties") or {}
    policy_required = set(policy.get("required") or [])
    contracts.check(
        "programId" in policy_properties,
        f"{relative}: Policy.programId is required",
    )
    contracts.check(
        _schema_types(policy_properties.get("programId")) == {"string", "null"}
        and (policy_properties.get("programId") or {}).get("format") == "uuid",
        f"{relative}: Policy.programId must be a nullable uuid",
    )
    contracts.check(
        "programId" not in policy_required,
        f"{relative}: Policy.programId must stay optional",
    )

    for (
        method,
        program_path,
        success_status,
        success_schema,
        request_schema,
        error_codes,
    ) in POLICY_PROGRAM_OPENAPI_PATHS:
        path_item = paths.get(program_path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {program_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required program operation is missing",
        )
        if not isinstance(operation, dict):
            continue

        parameter_refs, inline_names = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must require the shared TenantHeader",
        )
        contracts.check(
            "BookHeaderDirect" in parameter_refs,
            f"{where}: must require the shared BookHeaderDirect",
        )
        if program_path.endswith("/{programId}"):
            contracts.check(
                "programId" in inline_names,
                f"{where}: must declare the programId path parameter",
            )
        if program_path.endswith("/program"):
            contracts.check(
                "policyId" in inline_names,
                f"{where}: must declare the policyId path parameter",
            )

        description = str(operation.get("description") or "")
        contracts.check(
            "MISSING_TENANT_HEADER" in description,
            f"{where}: description must document 400 MISSING_TENANT_HEADER",
        )
        contracts.check(
            "BOOK_SCOPE_VIOLATION" in description,
            f"{where}: description must document 404 BOOK_SCOPE_VIOLATION",
        )

        responses = operation.get("responses") or {}
        for code in error_codes:
            contracts.check(
                code in responses,
                f"{where}: must document response {code}",
            )
        success_body = _response_schema(operation, success_status)
        success_reference = str((success_body or {}).get("$ref", ""))
        success_items_reference = str(
            ((success_body or {}).get("items") or {}).get("$ref", "")
        )
        contracts.check(
            isinstance(success_body, dict)
            and (
                success_reference.endswith(f"/schemas/{success_schema}")
                or (
                    success_body.get("type") == "array"
                    and success_items_reference.endswith(f"/schemas/{success_schema}")
                )
            ),
            f"{where}: {success_status} must return the {success_schema} schema",
        )
        for code, suffix in (("400", "BadRequest"), ("404", "NotFound")):
            response = responses.get(code) if isinstance(responses, dict) else None
            contracts.check(
                isinstance(response, dict)
                and str(response.get("$ref", "")).endswith(f"/responses/{suffix}"),
                f"{where}: {code} must reference the shared {suffix} response",
            )
        if "409" in error_codes:
            conflict = responses.get("409") if isinstance(responses, dict) else None
            contracts.check(
                isinstance(conflict, dict)
                and str(conflict.get("$ref", "")).endswith("/responses/Conflict"),
                f"{where}: 409 must reference the shared Conflict response",
            )

        if request_schema:
            request_body = operation.get("requestBody") or {}
            body_schema = (
                ((request_body.get("content") or {}).get("application/json") or {})
                .get("schema")
                if isinstance(request_body, dict)
                else None
            )
            contracts.check(
                isinstance(request_body, dict) and request_body.get("required") is True,
                f"{where}: requestBody must be required",
            )
            contracts.check(
                isinstance(body_schema, dict)
                and str(body_schema.get("$ref", "")).endswith(f"/schemas/{request_schema}"),
                f"{where}: request body must use the {request_schema} schema",
            )
        else:
            contracts.check(
                operation.get("requestBody") is None,
                f"{where}: read operations must not declare a requestBody",
            )

        if method == "post":
            for code in (
                "INVALID_PROGRAM_NAME",
                "INVALID_PROGRAM_TYPE",
                "INVALID_PROGRAM_DATES",
                POLICY_PROGRAM_CAPACITY_CODE,
            ):
                contracts.check(
                    code in description,
                    f"{where}: description must document 400 {code}",
                )
            contracts.check(
                "policy.program.created" in description,
                f"{where}: description must document the policy.program.created event",
            )
            created = responses.get("201") if isinstance(responses, dict) else None
            headers = created.get("headers") if isinstance(created, dict) else None
            contracts.check(
                isinstance(headers, dict) and "Location" in headers,
                f"{where}: 201 must declare the Location header",
            )
        if program_path.endswith("/{programId}"):
            contracts.check(
                "PROGRAM_NOT_FOUND" in description,
                f"{where}: description must document 404 PROGRAM_NOT_FOUND",
            )
        if method == "patch":
            for code in (
                "POLICY_NOT_FOUND",
                "PROGRAM_NOT_FOUND",
                "CONCURRENT_MODIFICATION",
            ):
                contracts.check(
                    code in description,
                    f"{where}: description must document {code}",
                )
            contracts.check(
                "policy.policy.program-assigned" in description,
                f"{where}: description must document the "
                "policy.policy.program-assigned event",
            )
            ok = responses.get("200") if isinstance(responses, dict) else None
            headers = ok.get("headers") if isinstance(ok, dict) else None
            etag = headers.get("ETag") if isinstance(headers, dict) else None
            contracts.check(
                isinstance(etag, dict)
                and str(etag.get("$ref", "")).endswith("/headers/ETag"),
                f"{where}: 200 must declare the shared ETag header",
            )

    planned = document.get("x-planned-operations") or []
    for implemented_path in sorted({entry[1] for entry in POLICY_PROGRAM_OPENAPI_PATHS}):
        contracts.check(
            not any(
                isinstance(entry, dict) and entry.get("path") == implemented_path
                for entry in planned
            ),
            f"{relative}: {implemented_path} must not remain in x-planned-operations",
        )


def check_policy_programs_asyncapi(contracts: ContractSet, document, relative: str):
    """Require the two implemented program event channels and payloads."""
    channels = document.get("channels") or {}
    operations = document.get("operations") or {}
    messages = (document.get("components") or {}).get("messages") or {}
    send_events = {
        operation.get("x-event-type")
        for operation in operations.values()
        if isinstance(operation, dict) and operation.get("action") == "send"
    }
    for channel_key, event, message_name, fields in (
        (
            "PolicyProgramCreated",
            "policy.program.created",
            "PolicyProgramCreatedData",
            POLICY_PROGRAM_CREATED_FIELDS,
        ),
        (
            "PolicyPolicyProgramAssigned",
            "policy.policy.program-assigned",
            "PolicyPolicyProgramAssignedData",
            POLICY_PROGRAM_ASSIGNED_FIELDS,
        ),
    ):
        channel = channels.get(channel_key) or {}
        contracts.check(
            channel.get("address") == event,
            f"{relative}: {channel_key} channel must address {event}",
        )
        contracts.check(
            channel.get("x-status") == "implemented",
            f"{relative}: {event} channel must be implemented",
        )
        contracts.check(
            bool(channel.get("x-implemented-by")),
            f"{relative}: {event} must name the emitting source",
        )
        channel_messages = channel.get("messages") or {}
        contracts.check(
            (channel_messages.get(message_name) or {}).get("$ref")
            == f"#/components/messages/{message_name}",
            f"{relative}: {event} must reference {message_name}",
        )
        contracts.check(
            event in send_events,
            f"{relative}: {event} must have a send operation",
        )
        message = messages.get(message_name) or {}
        payload = message.get("payload") or {}
        payload_properties = payload.get("properties") or {}
        payload_required = set(payload.get("required") or [])
        for field in fields:
            contracts.check(
                field in payload_properties,
                f"{relative}: {message_name}.properties.{field} is required",
            )
            contracts.check(
                field in payload_required,
                f"{relative}: {message_name}.required must list {field}",
            )

    created = (
        (messages.get("PolicyProgramCreatedData") or {}).get("payload") or {}
    )
    created_properties = created.get("properties") or {}
    contracts.check(
        set((created_properties.get("programType") or {}).get("enum") or [])
        == set(POLICY_PROGRAM_TYPES),
        f"{relative}: PolicyProgramCreatedData.programType must enumerate "
        f"{list(POLICY_PROGRAM_TYPES)}",
    )
    contracts.check(
        set((created_properties.get("status") or {}).get("enum") or [])
        == set(POLICY_PROGRAM_STATUSES),
        f"{relative}: PolicyProgramCreatedData.status must enumerate "
        f"{list(POLICY_PROGRAM_STATUSES)}",
    )
    contracts.check(
        _schema_types(created_properties.get("leadPolicyId")) == {"string", "null"},
        f"{relative}: PolicyProgramCreatedData.leadPolicyId must be a nullable string",
    )
    contracts.check(
        (created_properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: PolicyProgramCreatedData.createdAt must be a date-time",
    )

    assigned = (
        (messages.get("PolicyPolicyProgramAssignedData") or {}).get("payload") or {}
    )
    assigned_properties = assigned.get("properties") or {}
    for field in ("programId", "previousProgramId"):
        contracts.check(
            _schema_types(assigned_properties.get(field)) == {"string", "null"}
            and (assigned_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: PolicyPolicyProgramAssignedData.{field} must be a "
            "nullable uuid",
        )
    changed_fields = assigned_properties.get("changedFields") or {}
    contracts.check(
        changed_fields.get("type") == "array"
        and (changed_fields.get("items") or {}).get("type") == "string",
        f"{relative}: PolicyPolicyProgramAssignedData.changedFields must be a "
        "string array",
    )
    contracts.check(
        (assigned_properties.get("version") or {}).get("type") == "integer",
        f"{relative}: PolicyPolicyProgramAssignedData.version must be an integer",
    )


# ---------------------------------------------------------------------------
# Policy credit-note checks
# ---------------------------------------------------------------------------


def check_policy_credit_notes_openapi(contracts: ContractSet, document, relative: str):
    """Require the public credit-note operations, schemas, and lifecycle rules."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    for (
        method,
        note_path,
        success_status,
        response_schema_name,
        request_schema_name,
    ) in POLICY_CREDIT_NOTE_PATHS:
        path_item = paths.get(note_path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {note_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required credit-note operation is missing",
        )
        if not isinstance(operation, dict):
            continue

        parameter_refs, inline_names = _parameter_names(operation)
        for parameter in ("TenantHeader", "BookHeaderDirect"):
            contracts.check(
                parameter in parameter_refs,
                f"{where}: must document the shared {parameter} parameter",
            )
        contracts.check(
            "policyId" in inline_names,
            f"{where}: must declare the policyId path parameter",
        )
        if method == "patch":
            contracts.check(
                "creditNoteId" in inline_names,
                f"{where}: must declare the creditNoteId path parameter",
            )

        responses = operation.get("responses") or {}
        for code in ("400", "404"):
            contracts.check(
                code in responses,
                f"{where}: must document the {code} response",
            )
        if method == "get":
            ok_schema = _response_schema(operation, "200")
            contracts.check(
                isinstance(ok_schema, dict)
                and ok_schema.get("type") == "array"
                and str((ok_schema.get("items") or {}).get("$ref", "")).endswith(
                    f"/schemas/{response_schema_name}"
                ),
                f"{where}: 200 must return an array of {response_schema_name}",
            )
        else:
            contracts.check(
                "409" in responses,
                f"{where}: must document the 409 response",
            )
            request_body = operation.get("requestBody") or {}
            contracts.check(
                isinstance(request_body, dict)
                and request_body.get("required") is True,
                f"{where}: request body must be required",
            )
            request_schema = (
                ((request_body.get("content") or {}).get("application/json") or {})
                .get("schema")
                if isinstance(request_body, dict)
                else None
            )
            contracts.check(
                isinstance(request_schema, dict)
                and str(request_schema.get("$ref", "")).endswith(
                    f"/schemas/{request_schema_name}"
                ),
                f"{where}: request body must use the {request_schema_name} schema",
            )
            success_schema = _response_schema(operation, success_status)
            contracts.check(
                isinstance(success_schema, dict)
                and str(success_schema.get("$ref", "")).endswith(
                    f"/schemas/{response_schema_name}"
                ),
                f"{where}: {success_status} must return the "
                f"{response_schema_name} schema",
            )

    list_item = paths.get("/api/v1/policies/{policyId}/credit-notes")
    list_operation = (
        list_item.get("get") if isinstance(list_item, dict) else None
    )
    list_text = str(
        (list_operation or {}).get("description") or ""
    )
    contracts.check(
        "newest-first" in list_text.lower(),
        f"{relative}: GET credit notes must document the newest-first order",
    )

    create_item = paths.get("/api/v1/policies/{policyId}/credit-notes")
    create_operation = (
        create_item.get("post") if isinstance(create_item, dict) else None
    )
    create_text = str((create_operation or {}).get("description") or "")
    for code in (
        "INVALID_CREDIT_NOTE_AMOUNT",
        "CURRENCY_MISMATCH",
        "INVALID_CREDIT_NOTE_REASON",
        "VALIDATION_ERROR",
        "CONCURRENT_MODIFICATION",
        "CANCELLATION_NOT_FOUND",
        "CANCELLATION_NOT_ACTIVE",
        "CREDIT_NOTE_AMOUNT_MISMATCH",
        "DUPLICATE_CANCELLATION_CREDIT_NOTE",
    ):
        contracts.check(
            code in create_text,
            f"{relative}: POST credit notes must document {code}",
        )
    for term in (
        "cancellationId",
        "cancellationNumber",
        "ACTIVE",
        "one cent",
        "policy.credit-note.created",
        "same transaction",
    ):
        contracts.check(
            term in create_text,
            f"{relative}: POST credit notes must document {term}",
        )
    contracts.check(
        "no lifecycle" not in create_text.lower()
        and "emits no" not in create_text.lower(),
        f"{relative}: POST credit notes must not claim that creation emits no event",
    )

    status_path = (
        "/api/v1/policies/{policyId}/credit-notes/{creditNoteId}/status"
    )
    status_item = paths.get(status_path) if isinstance(paths, dict) else None
    status_operation = (
        status_item.get("patch") if isinstance(status_item, dict) else None
    )
    status_text = str((status_operation or {}).get("description") or "")
    for status in POLICY_CREDIT_NOTE_STATUSES:
        contracts.check(
            status in status_text,
            f"{relative}: PATCH credit-note status must document {status}",
        )
    for code in (
        "INVALID_CREDIT_NOTE_STATUS",
        "INVALID_CREDIT_NOTE_TRANSITION",
        "INVALID_CREDIT_NOTE_INSTALLMENT",
        "INVALID_CREDIT_NOTE_REASON",
        "INSTALLMENT_NOT_FOUND",
        "INSTALLMENT_NOT_CREDITABLE",
        "CREDIT_NOTE_EXCEEDS_INSTALLMENT",
        "CONCURRENT_MODIFICATION",
    ):
        contracts.check(
            code in status_text,
            f"{relative}: PATCH credit-note status must document {code}",
        )
    for term in (
        "installmentId",
        "creditedAmount",
        "CREDITED",
        "partial credit",
        "outstandingAmount",
        "APPLIED -> REVERSED",
        "reversedAt",
        "reversalReason",
        "REVERSED",
    ):
        contracts.check(
            term in status_text,
            f"{relative}: PATCH credit-note status must document {term}",
        )
    for event in POLICY_CREDIT_NOTE_TRANSITION_EVENTS:
        contracts.check(
            event in status_text,
            f"{relative}: PATCH credit-note status must document {event}",
        )

    planned_operations = document.get("x-planned-operations") or []
    planned_pairs = {
        (str(entry.get("method", "")).lower(), entry.get("path"))
        for entry in planned_operations
        if isinstance(entry, dict)
    }
    for method, note_path, _, _, _ in POLICY_CREDIT_NOTE_PATHS:
        contracts.check(
            (method, note_path) not in planned_pairs,
            f"{relative}: implemented credit-note operation {method.upper()} "
            f"{note_path} must not reappear under x-planned-operations",
        )

    credit_note = schemas.get("CreditNote") or {}
    properties = credit_note.get("properties") or {}
    required = set(credit_note.get("required") or [])
    contracts.check(
        isinstance(credit_note, dict) and credit_note.get("type") == "object",
        f"{relative}: CreditNote must be an object schema",
    )
    contracts.check(
        required == set(POLICY_CREDIT_NOTE_FIELDS),
        f"{relative}: CreditNote must require exactly "
        f"{list(POLICY_CREDIT_NOTE_FIELDS)}",
    )
    for field in POLICY_CREDIT_NOTE_FIELDS:
        contracts.check(
            field in properties,
            f"{relative}: CreditNote.properties.{field} is required",
        )
    for field in ("creditNoteId", "policyId"):
        contracts.check(
            (properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: CreditNote.{field} must be a uuid",
        )
    contracts.check(
        (properties.get("noteNumber") or {}).get("type") == "string"
        and (properties.get("noteNumber") or {}).get("maxLength") == 32,
        f"{relative}: CreditNote.noteNumber must be a string of at most 32 characters",
    )
    contracts.check(
        str((properties.get("amount") or {}).get("$ref", "")).endswith(
            "/schemas/MoneyAmount"
        ),
        f"{relative}: CreditNote.amount must reference MoneyAmount",
    )
    contracts.check(
        str((properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: CreditNote.currency must reference CurrencyCode",
    )
    reason = properties.get("reason") or {}
    contracts.check(
        _schema_types(reason) == {"string", "null"}
        and reason.get("maxLength") == POLICY_CREDIT_NOTE_REASON_MAX_LENGTH,
        f"{relative}: CreditNote.reason must be a nullable string of at most "
        f"{POLICY_CREDIT_NOTE_REASON_MAX_LENGTH} characters",
    )
    contracts.check(
        str((properties.get("status") or {}).get("$ref", "")).endswith(
            "/schemas/CreditNoteStatus"
        ),
        f"{relative}: CreditNote.status must reference CreditNoteStatus",
    )
    for field in ("issuedAt", "appliedAt"):
        contracts.check(
            _schema_types(properties.get(field)) == {"string", "null"}
            and (properties.get(field) or {}).get("format") == "date-time",
            f"{relative}: CreditNote.{field} must be a nullable date-time",
        )
    applied_installment = properties.get("appliedInstallmentId") or {}
    contracts.check(
        _schema_types(applied_installment) == {"string", "null"}
        and applied_installment.get("format") == "uuid",
        f"{relative}: CreditNote.appliedInstallmentId must be a nullable uuid",
    )
    cancellation_id = properties.get("cancellationId") or {}
    contracts.check(
        _schema_types(cancellation_id) == {"string", "null"}
        and cancellation_id.get("format") == "uuid",
        f"{relative}: CreditNote.cancellationId must be a nullable uuid",
    )
    cancellation_number = properties.get("cancellationNumber") or {}
    contracts.check(
        _schema_types(cancellation_number) == {"string", "null"}
        and cancellation_number.get("maxLength")
        == POLICY_CREDIT_NOTE_CANCELLATION_NUMBER_MAX_LENGTH,
        f"{relative}: CreditNote.cancellationNumber must be a nullable string of "
        f"at most {POLICY_CREDIT_NOTE_CANCELLATION_NUMBER_MAX_LENGTH} characters",
    )
    contracts.check(
        (properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: CreditNote.createdAt must be a date-time",
    )
    reversed_at = properties.get("reversedAt") or {}
    contracts.check(
        _schema_types(reversed_at) == {"string", "null"}
        and reversed_at.get("format") == "date-time",
        f"{relative}: CreditNote.reversedAt must be a nullable date-time",
    )
    reversal_reason = properties.get("reversalReason") or {}
    contracts.check(
        _schema_types(reversal_reason) == {"string", "null"}
        and reversal_reason.get("maxLength") == POLICY_CREDIT_NOTE_REASON_MAX_LENGTH,
        f"{relative}: CreditNote.reversalReason must be a nullable string of at "
        f"most {POLICY_CREDIT_NOTE_REASON_MAX_LENGTH} characters",
    )

    status_schema = schemas.get("CreditNoteStatus") or {}
    contracts.check(
        status_schema.get("type") == "string",
        f"{relative}: CreditNoteStatus must be a string enum",
    )
    contracts.check(
        tuple(status_schema.get("enum") or []) == POLICY_CREDIT_NOTE_STATUSES,
        f"{relative}: CreditNoteStatus must enumerate "
        f"{list(POLICY_CREDIT_NOTE_STATUSES)}",
    )

    create = schemas.get("CreateCreditNoteRequest") or {}
    create_properties = create.get("properties") or {}
    create_required = set(create.get("required") or [])
    contracts.check(
        isinstance(create, dict) and create.get("type") == "object",
        f"{relative}: CreateCreditNoteRequest must be an object schema",
    )
    contracts.check(
        create_required == {"amount", "currency"},
        f"{relative}: CreateCreditNoteRequest must require amount and currency",
    )
    contracts.check(
        "reason" in create_properties and "reason" not in create_required,
        f"{relative}: CreateCreditNoteRequest.reason must stay optional",
    )
    contracts.check(
        "status" not in create_properties,
        f"{relative}: CreateCreditNoteRequest must not accept a caller status",
    )
    amount = create_properties.get("amount") or {}
    contracts.check(
        amount.get("type") == "string"
        and amount.get("pattern") == POLICY_CREDIT_NOTE_AMOUNT_PATTERN,
        f"{relative}: CreateCreditNoteRequest.amount must be a positive money "
        "decimal string",
    )
    contracts.check(
        str((create_properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: CreateCreditNoteRequest.currency must reference CurrencyCode",
    )
    create_reason = create_properties.get("reason") or {}
    contracts.check(
        _schema_types(create_reason) == {"string", "null"}
        and create_reason.get("maxLength")
        == POLICY_CREDIT_NOTE_REASON_MAX_LENGTH,
        f"{relative}: CreateCreditNoteRequest.reason must be a nullable string "
        f"of at most {POLICY_CREDIT_NOTE_REASON_MAX_LENGTH} characters",
    )
    create_cancellation = create_properties.get("cancellationId") or {}
    contracts.check(
        "cancellationId" in create_properties
        and "cancellationId" not in create_required,
        f"{relative}: CreateCreditNoteRequest.cancellationId must stay optional",
    )
    contracts.check(
        _schema_types(create_cancellation) == {"string", "null"}
        and create_cancellation.get("format") == "uuid",
        f"{relative}: CreateCreditNoteRequest.cancellationId must be a nullable "
        "uuid",
    )

    cancellation = schemas.get("Cancellation") or {}
    cancellation_properties = cancellation.get("properties") or {}
    cancellation_required = set(cancellation.get("required") or [])
    cancellation_number = cancellation_properties.get("cancellationNumber") or {}
    contracts.check(
        "cancellationNumber" in cancellation_properties
        and "cancellationNumber" not in cancellation_required,
        f"{relative}: Cancellation.cancellationNumber must stay optional so the "
        "historical and public-domain projections remain valid",
    )
    contracts.check(
        _schema_types(cancellation_number) == {"string", "null"}
        and cancellation_number.get("maxLength")
        == POLICY_CREDIT_NOTE_CANCELLATION_NUMBER_MAX_LENGTH
        and "CX-" in str(cancellation_number.get("description") or ""),
        f"{relative}: Cancellation.cancellationNumber must be a nullable "
        f"`CX-` reference of at most "
        f"{POLICY_CREDIT_NOTE_CANCELLATION_NUMBER_MAX_LENGTH} characters",
    )

    request = schemas.get("UpdateCreditNoteStatusRequest") or {}
    request_properties = request.get("properties") or {}
    contracts.check(
        isinstance(request, dict) and request.get("type") == "object",
        f"{relative}: UpdateCreditNoteStatusRequest must be an object schema",
    )
    contracts.check(
        set(request.get("required") or []) == {"status"},
        f"{relative}: UpdateCreditNoteStatusRequest must require only status",
    )
    request_status = request_properties.get("status") or {}
    contracts.check(
        (request_status.get("type"), tuple(request_status.get("enum") or []))
        == ("string", POLICY_CREDIT_NOTE_REQUEST_STATUSES),
        f"{relative}: UpdateCreditNoteStatusRequest.status must enumerate "
        f"{list(POLICY_CREDIT_NOTE_REQUEST_STATUSES)}",
    )
    request_installment = request_properties.get("installmentId") or {}
    contracts.check(
        "installmentId" in request_properties
        and "installmentId" not in set(request.get("required") or []),
        f"{relative}: UpdateCreditNoteStatusRequest.installmentId must be optional",
    )
    contracts.check(
        _schema_types(request_installment) == {"string", "null"}
        and request_installment.get("format") == "uuid",
        f"{relative}: UpdateCreditNoteStatusRequest.installmentId must be a "
        "nullable uuid",
    )
    request_reason = request_properties.get("reason") or {}
    contracts.check(
        "reason" in request_properties
        and "reason" not in set(request.get("required") or []),
        f"{relative}: UpdateCreditNoteStatusRequest.reason must be optional",
    )
    contracts.check(
        _schema_types(request_reason) == {"string", "null"}
        and request_reason.get("maxLength") == POLICY_CREDIT_NOTE_REASON_MAX_LENGTH,
        f"{relative}: UpdateCreditNoteStatusRequest.reason must be a nullable "
        f"string of at most {POLICY_CREDIT_NOTE_REASON_MAX_LENGTH} characters",
    )
    applied_condition = next(
        (
            entry
            for entry in request.get("allOf") or []
            if isinstance(entry, dict)
            and ((entry.get("if") or {}).get("properties") or {})
            .get("status", {})
            .get("const")
            == "APPLIED"
        ),
        None,
    )
    contracts.check(
        isinstance(applied_condition, dict),
        f"{relative}: UpdateCreditNoteStatusRequest must conditionally require "
        "installmentId for APPLIED",
    )
    contracts.check(
        set(((applied_condition or {}).get("then") or {}).get("required") or [])
        == {"installmentId"},
        f"{relative}: UpdateCreditNoteStatusRequest must require installmentId "
        "when status is APPLIED",
    )
    reversed_condition = next(
        (
            entry
            for entry in request.get("allOf") or []
            if isinstance(entry, dict)
            and ((entry.get("if") or {}).get("properties") or {})
            .get("status", {})
            .get("const")
            == "REVERSED"
        ),
        None,
    )
    contracts.check(
        isinstance(reversed_condition, dict),
        f"{relative}: UpdateCreditNoteStatusRequest must conditionally require "
        "reason for REVERSED",
    )
    contracts.check(
        set(((reversed_condition or {}).get("then") or {}).get("required") or [])
        == {"reason"},
        f"{relative}: UpdateCreditNoteStatusRequest must require reason when "
        "status is REVERSED",
    )
    reversed_reason = (
        ((reversed_condition or {}).get("then") or {}).get("properties") or {}
    ).get("reason") or {}
    contracts.check(
        reversed_reason.get("type") == "string"
        and reversed_reason.get("minLength") == 1
        and reversed_reason.get("maxLength") == POLICY_CREDIT_NOTE_REASON_MAX_LENGTH,
        f"{relative}: UpdateCreditNoteStatusRequest must require a non-blank "
        f"reason of at most {POLICY_CREDIT_NOTE_REASON_MAX_LENGTH} characters "
        "when status is REVERSED",
    )


def check_policy_credit_notes_asyncapi(contracts: ContractSet, document, relative: str):
    """Require the five implemented credit-note channels and their payloads."""
    channels = document.get("channels") or {}
    operations = document.get("operations") or {}
    messages = (
        (document.get("components") or {}).get("messages") or {}
    )
    send_events = {
        operation.get("x-event-type")
        for operation in operations.values()
        if isinstance(operation, dict)
        and operation.get("action") == "send"
    }

    for event in POLICY_CREDIT_NOTE_EVENTS:
        channel = next(
            (
                candidate
                for candidate in channels.values()
                if isinstance(candidate, dict)
                and candidate.get("address") == event
            ),
            None,
        )
        contracts.check(
            isinstance(channel, dict),
            f"{relative}: required credit-note event channel '{event}' is missing",
        )
        if not isinstance(channel, dict):
            continue
        contracts.check(
            channel.get("x-status") == "implemented",
            f"{relative}: credit-note event channel '{event}' must be implemented",
        )
        contracts.check(
            str(channel.get("x-implemented-by", "")).endswith(
                POLICY_CREDIT_NOTE_EVENT_IMPLEMENTED_BY
            ),
            f"{relative}: credit-note event channel '{event}' must name "
            f"{POLICY_CREDIT_NOTE_EVENT_IMPLEMENTED_BY} in x-implemented-by",
        )
        contracts.check(
            event in send_events,
            f"{relative}: credit-note event '{event}' must have a send operation",
        )
        is_created = event == "policy.credit-note.created"
        is_reversed = event == "policy.credit-note.reversed"
        if is_created:
            expected_message = POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE
        elif is_reversed:
            expected_message = POLICY_CREDIT_NOTE_REVERSED_EVENT_MESSAGE
        else:
            expected_message = POLICY_CREDIT_NOTE_EVENT_MESSAGE
        channel_messages = channel.get("messages") or {}
        contracts.check(
            (channel_messages.get(expected_message) or {}).get("$ref")
            == f"#/components/messages/{expected_message}",
            f"{relative}: {event} must reference {expected_message}",
        )
        if is_created:
            created_text = str(channel.get("description") or "")
            for field in POLICY_CREDIT_NOTE_LINK_FIELDS:
                contracts.check(
                    field in created_text,
                    f"{relative}: {event} description must document {field}",
                )
            contracts.check(
                "DRAFT" in created_text,
                f"{relative}: {event} description must document DRAFT",
            )
        if event == "policy.credit-note.applied":
            applied_text = str(channel.get("description") or "")
            for field in POLICY_CREDIT_NOTE_APPLIED_EVENT_FIELDS:
                contracts.check(
                    field in applied_text,
                    f"{relative}: {event} description must document {field}",
                )
        if is_reversed:
            reversed_text = str(channel.get("description") or "")
            for field in ("installmentId", "reason", "REVERSED"):
                contracts.check(
                    field in reversed_text,
                    f"{relative}: {event} description must document {field}",
                )

    message = messages.get(POLICY_CREDIT_NOTE_EVENT_MESSAGE) or {}
    payload = message.get("payload") or {}
    payload_properties = payload.get("properties") or {}
    payload_required = set(payload.get("required") or [])
    contracts.check(
        payload_required == set(POLICY_CREDIT_NOTE_EVENT_FIELDS),
        f"{relative}: {POLICY_CREDIT_NOTE_EVENT_MESSAGE} must require exactly "
        f"{list(POLICY_CREDIT_NOTE_EVENT_FIELDS)}",
    )
    for field in POLICY_CREDIT_NOTE_EVENT_FIELDS:
        contracts.check(
            field in payload_properties,
            f"{relative}: {POLICY_CREDIT_NOTE_EVENT_MESSAGE}.properties.{field} "
            "is required",
        )
    for field in ("policyId", "creditNoteId"):
        contracts.check(
            (payload_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: {POLICY_CREDIT_NOTE_EVENT_MESSAGE}.{field} must be a uuid",
        )
    contracts.check(
        (payload_properties.get("noteNumber") or {}).get("maxLength") == 32,
        f"{relative}: {POLICY_CREDIT_NOTE_EVENT_MESSAGE}.noteNumber must be at "
        "most 32 characters",
    )
    contracts.check(
        (payload_properties.get("amount") or {}).get("type") == "string",
        f"{relative}: {POLICY_CREDIT_NOTE_EVENT_MESSAGE}.amount must be a "
        "decimal string",
    )
    contracts.check(
        (payload_properties.get("currency") or {}).get("pattern")
        == "^[A-Z]{3}$",
        f"{relative}: {POLICY_CREDIT_NOTE_EVENT_MESSAGE}.currency must be an "
        "uppercase ISO code",
    )
    contracts.check(
        set((payload_properties.get("status") or {}).get("enum") or [])
        == set(POLICY_CREDIT_NOTE_EVENT_STATUSES),
        f"{relative}: {POLICY_CREDIT_NOTE_EVENT_MESSAGE}.status must enumerate "
        f"{list(POLICY_CREDIT_NOTE_EVENT_STATUSES)}",
    )
    for field in POLICY_CREDIT_NOTE_APPLIED_EVENT_FIELDS:
        contracts.check(
            field in payload_properties,
            f"{relative}: {POLICY_CREDIT_NOTE_EVENT_MESSAGE}.properties.{field} "
            "is required for the applied event",
        )
        contracts.check(
            field not in payload_required,
            f"{relative}: {POLICY_CREDIT_NOTE_EVENT_MESSAGE}.{field} must stay "
            "optional because ISSUED and CANCELLED omit it",
        )
    contracts.check(
        (payload_properties.get("installmentId") or {}).get("format") == "uuid",
        f"{relative}: {POLICY_CREDIT_NOTE_EVENT_MESSAGE}.installmentId must be "
        "a uuid",
    )
    contracts.check(
        (payload_properties.get("creditedAmount") or {}).get("type") == "string",
        f"{relative}: {POLICY_CREDIT_NOTE_EVENT_MESSAGE}.creditedAmount must be "
        "a decimal string",
    )

    created_message = messages.get(POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE) or {}
    created_payload = created_message.get("payload") or {}
    created_properties = created_payload.get("properties") or {}
    created_required = set(created_payload.get("required") or [])
    contracts.check(
        created_required == set(POLICY_CREDIT_NOTE_CREATED_EVENT_FIELDS),
        f"{relative}: {POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE} must require "
        f"exactly {list(POLICY_CREDIT_NOTE_CREATED_EVENT_FIELDS)}",
    )
    for field in POLICY_CREDIT_NOTE_CREATED_EVENT_FIELDS:
        contracts.check(
            field in created_properties,
            f"{relative}: {POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE}."
            f"properties.{field} is required",
        )
    for field in ("policyId", "creditNoteId"):
        contracts.check(
            (created_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: {POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE}.{field} "
            "must be a uuid",
        )
    contracts.check(
        (created_properties.get("noteNumber") or {}).get("maxLength") == 32,
        f"{relative}: {POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE}.noteNumber must "
        "be at most 32 characters",
    )
    contracts.check(
        (created_properties.get("amount") or {}).get("type") == "string",
        f"{relative}: {POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE}.amount must be "
        "a decimal string",
    )
    contracts.check(
        (created_properties.get("currency") or {}).get("pattern") == "^[A-Z]{3}$",
        f"{relative}: {POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE}.currency must be "
        "an uppercase ISO code",
    )
    contracts.check(
        tuple((created_properties.get("status") or {}).get("enum") or [])
        == ("DRAFT",),
        f"{relative}: {POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE}.status must "
        "enumerate DRAFT only",
    )
    contracts.check(
        (created_properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: {POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE}.createdAt must be "
        "a date-time",
    )
    for field in POLICY_CREDIT_NOTE_LINK_FIELDS:
        contracts.check(
            field in created_properties,
            f"{relative}: {POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE}."
            f"properties.{field} is required for a linked note",
        )
        contracts.check(
            field not in created_required,
            f"{relative}: {POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE}.{field} must "
            "stay optional because an unlinked billing adjustment omits it",
        )
    contracts.check(
        (created_properties.get("cancellationId") or {}).get("format") == "uuid",
        f"{relative}: {POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE}.cancellationId "
        "must be a uuid",
    )
    created_cancellation_number = (
        created_properties.get("cancellationNumber") or {}
    )
    contracts.check(
        _schema_types(created_cancellation_number) == {"string", "null"}
        and created_cancellation_number.get("maxLength")
        == POLICY_CREDIT_NOTE_CANCELLATION_NUMBER_MAX_LENGTH,
        f"{relative}: {POLICY_CREDIT_NOTE_CREATED_EVENT_MESSAGE}."
        "cancellationNumber must be a nullable string of at most "
        f"{POLICY_CREDIT_NOTE_CANCELLATION_NUMBER_MAX_LENGTH} characters",
    )

    reversed_message = messages.get(POLICY_CREDIT_NOTE_REVERSED_EVENT_MESSAGE) or {}
    reversed_payload = reversed_message.get("payload") or {}
    reversed_properties = reversed_payload.get("properties") or {}
    reversed_required = set(reversed_payload.get("required") or [])
    contracts.check(
        reversed_required == set(POLICY_CREDIT_NOTE_REVERSED_EVENT_FIELDS),
        f"{relative}: {POLICY_CREDIT_NOTE_REVERSED_EVENT_MESSAGE} must require "
        f"exactly {list(POLICY_CREDIT_NOTE_REVERSED_EVENT_FIELDS)}",
    )
    for field in POLICY_CREDIT_NOTE_REVERSED_EVENT_FIELDS:
        contracts.check(
            field in reversed_properties,
            f"{relative}: {POLICY_CREDIT_NOTE_REVERSED_EVENT_MESSAGE}."
            f"properties.{field} is required",
        )
    contracts.check(
        (reversed_properties.get("creditNoteId") or {}).get("format") == "uuid",
        f"{relative}: {POLICY_CREDIT_NOTE_REVERSED_EVENT_MESSAGE}.creditNoteId "
        "must be a uuid",
    )
    contracts.check(
        (reversed_properties.get("noteNumber") or {}).get("maxLength") == 32,
        f"{relative}: {POLICY_CREDIT_NOTE_REVERSED_EVENT_MESSAGE}.noteNumber "
        "must be at most 32 characters",
    )
    reversed_installment = reversed_properties.get("installmentId") or {}
    contracts.check(
        _schema_types(reversed_installment) == {"string", "null"}
        and reversed_installment.get("format") == "uuid",
        f"{relative}: {POLICY_CREDIT_NOTE_REVERSED_EVENT_MESSAGE}.installmentId "
        "must be a nullable uuid",
    )
    contracts.check(
        (reversed_properties.get("amount") or {}).get("type") == "string",
        f"{relative}: {POLICY_CREDIT_NOTE_REVERSED_EVENT_MESSAGE}.amount must be "
        "a decimal string",
    )
    reversed_reason = reversed_properties.get("reason") or {}
    contracts.check(
        reversed_reason.get("type") == "string"
        and reversed_reason.get("maxLength") == POLICY_CREDIT_NOTE_REASON_MAX_LENGTH,
        f"{relative}: {POLICY_CREDIT_NOTE_REVERSED_EVENT_MESSAGE}.reason must be "
        f"a string of at most {POLICY_CREDIT_NOTE_REASON_MAX_LENGTH} characters",
    )
    contracts.check(
        tuple((reversed_properties.get("status") or {}).get("enum") or [])
        == ("REVERSED",),
        f"{relative}: {POLICY_CREDIT_NOTE_REVERSED_EVENT_MESSAGE}.status must "
        "enumerate REVERSED only",
    )


# ---------------------------------------------------------------------------
# Policy legal entity checks
# ---------------------------------------------------------------------------


def check_policy_legal_entities_openapi(contracts: ContractSet, document, relative: str):
    """Require the legal-entity catalog and assignment operations and schemas."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    legal_entity = schemas.get("LegalEntity") or {}
    legal_entity_properties = legal_entity.get("properties") or {}
    legal_entity_required = set(legal_entity.get("required") or [])
    contracts.check(
        legal_entity.get("type") == "object",
        f"{relative}: LegalEntity must be an object schema",
    )
    for field in POLICY_LEGAL_ENTITY_FIELDS:
        contracts.check(
            field in legal_entity_properties,
            f"{relative}: LegalEntity.properties.{field} is required",
        )
        contracts.check(
            field in legal_entity_required,
            f"{relative}: LegalEntity.required must list {field}",
        )
    contracts.check(
        (legal_entity_properties.get("legalEntityId") or {}).get("format") == "uuid",
        f"{relative}: LegalEntity.legalEntityId must be a uuid",
    )
    contracts.check(
        (legal_entity_properties.get("code") or {}).get("maxLength")
        == POLICY_LEGAL_ENTITY_CODE_MAX_LENGTH,
        f"{relative}: LegalEntity.code maxLength must be "
        f"{POLICY_LEGAL_ENTITY_CODE_MAX_LENGTH}",
    )
    contracts.check(
        (legal_entity_properties.get("name") or {}).get("maxLength")
        == POLICY_LEGAL_ENTITY_NAME_MAX_LENGTH,
        f"{relative}: LegalEntity.name maxLength must be "
        f"{POLICY_LEGAL_ENTITY_NAME_MAX_LENGTH}",
    )
    contracts.check(
        (legal_entity_properties.get("entityType") or {}).get("$ref")
        == "#/components/schemas/LegalEntityType",
        f"{relative}: LegalEntity.entityType must reference LegalEntityType",
    )
    jurisdiction = legal_entity_properties.get("jurisdiction") or {}
    contracts.check(
        (
            jurisdiction.get("type"),
            jurisdiction.get("minLength"),
            jurisdiction.get("maxLength"),
            jurisdiction.get("pattern"),
        )
        == (
            "string",
            2,
            2,
            POLICY_LEGAL_ENTITY_JURISDICTION_PATTERN,
        ),
        f"{relative}: LegalEntity.jurisdiction must be a two-letter uppercase code",
    )
    for field, maximum in (
        ("regulator", POLICY_LEGAL_ENTITY_REGULATOR_MAX_LENGTH),
        ("licenseNumber", POLICY_LEGAL_ENTITY_LICENSE_MAX_LENGTH),
    ):
        field_schema = legal_entity_properties.get(field) or {}
        contracts.check(
            _schema_types(field_schema) == {"string", "null"},
            f"{relative}: LegalEntity.{field} must be a nullable string",
        )
        contracts.check(
            field_schema.get("maxLength") == maximum,
            f"{relative}: LegalEntity.{field} maxLength must be {maximum}",
        )
    contracts.check(
        (legal_entity_properties.get("status") or {}).get("$ref")
        == "#/components/schemas/LegalEntityStatus",
        f"{relative}: LegalEntity.status must reference LegalEntityStatus",
    )
    contracts.check(
        (legal_entity_properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: LegalEntity.createdAt must be a date-time",
    )

    entity_type = schemas.get("LegalEntityType") or {}
    contracts.check(
        entity_type.get("type") == "string"
        and tuple(entity_type.get("enum") or []) == POLICY_LEGAL_ENTITY_TYPES,
        f"{relative}: LegalEntityType.enum must be "
        f"{list(POLICY_LEGAL_ENTITY_TYPES)}",
    )
    status = schemas.get("LegalEntityStatus") or {}
    contracts.check(
        status.get("type") == "string"
        and tuple(status.get("enum") or []) == POLICY_LEGAL_ENTITY_STATUSES,
        f"{relative}: LegalEntityStatus.enum must be "
        f"{list(POLICY_LEGAL_ENTITY_STATUSES)}",
    )

    create = schemas.get("CreateLegalEntityRequest") or {}
    create_properties = create.get("properties") or {}
    create_required = set(create.get("required") or [])
    contracts.check(
        create.get("type") == "object",
        f"{relative}: CreateLegalEntityRequest must be an object schema",
    )
    for field in POLICY_LEGAL_ENTITY_CREATE_REQUIRED_FIELDS:
        contracts.check(
            field in create_properties,
            f"{relative}: CreateLegalEntityRequest.properties.{field} is required",
        )
        contracts.check(
            field in create_required,
            f"{relative}: CreateLegalEntityRequest.required must list {field}",
        )
    for field in POLICY_LEGAL_ENTITY_CREATE_OPTIONAL_FIELDS:
        contracts.check(
            field in create_properties,
            f"{relative}: CreateLegalEntityRequest.properties.{field} is required",
        )
        contracts.check(
            field not in create_required,
            f"{relative}: CreateLegalEntityRequest.{field} must stay optional",
        )
    contracts.check(
        (create_properties.get("code") or {}).get("maxLength")
        == POLICY_LEGAL_ENTITY_CODE_MAX_LENGTH,
        f"{relative}: CreateLegalEntityRequest.code maxLength must be "
        f"{POLICY_LEGAL_ENTITY_CODE_MAX_LENGTH}",
    )
    contracts.check(
        (create_properties.get("name") or {}).get("maxLength")
        == POLICY_LEGAL_ENTITY_NAME_MAX_LENGTH,
        f"{relative}: CreateLegalEntityRequest.name maxLength must be "
        f"{POLICY_LEGAL_ENTITY_NAME_MAX_LENGTH}",
    )
    contracts.check(
        (create_properties.get("entityType") or {}).get("$ref")
        == "#/components/schemas/LegalEntityType",
        f"{relative}: CreateLegalEntityRequest.entityType must reference "
        "LegalEntityType",
    )
    create_jurisdiction = create_properties.get("jurisdiction") or {}
    contracts.check(
        (
            create_jurisdiction.get("minLength"),
            create_jurisdiction.get("maxLength"),
            create_jurisdiction.get("pattern"),
        )
        == (2, 2, POLICY_LEGAL_ENTITY_JURISDICTION_PATTERN),
        f"{relative}: CreateLegalEntityRequest.jurisdiction must be a "
        "two-letter uppercase code",
    )
    for field, maximum in (
        ("regulator", POLICY_LEGAL_ENTITY_REGULATOR_MAX_LENGTH),
        ("licenseNumber", POLICY_LEGAL_ENTITY_LICENSE_MAX_LENGTH),
    ):
        field_schema = create_properties.get(field) or {}
        contracts.check(
            _schema_types(field_schema) == {"string", "null"},
            f"{relative}: CreateLegalEntityRequest.{field} must be a nullable "
            "string",
        )
        contracts.check(
            field_schema.get("maxLength") == maximum,
            f"{relative}: CreateLegalEntityRequest.{field} maxLength must be "
            f"{maximum}",
        )

    update = schemas.get("UpdatePolicyLegalEntityRequest") or {}
    update_properties = update.get("properties") or {}
    contracts.check(
        update.get("type") == "object",
        f"{relative}: UpdatePolicyLegalEntityRequest must be an object schema",
    )
    update_legal_entity = update_properties.get("legalEntityId") or {}
    contracts.check(
        _schema_types(update_legal_entity) == {"string", "null"}
        and update_legal_entity.get("format") == "uuid",
        f"{relative}: UpdatePolicyLegalEntityRequest.legalEntityId must be a "
        "nullable uuid",
    )
    contracts.check(
        "legalEntityId" not in set(update.get("required") or []),
        f"{relative}: UpdatePolicyLegalEntityRequest.legalEntityId must stay "
        "optional so an empty object clears the link",
    )

    policy = schemas.get("Policy") or {}
    policy_properties = policy.get("properties") or {}
    policy_required = set(policy.get("required") or [])
    policy_legal_entity = policy_properties.get("legalEntityId") or {}
    contracts.check(
        _schema_types(policy_legal_entity) == {"string", "null"}
        and policy_legal_entity.get("format") == "uuid",
        f"{relative}: Policy.legalEntityId must be a nullable uuid",
    )
    contracts.check(
        "legalEntityId" not in policy_required,
        f"{relative}: Policy.legalEntityId must stay optional",
    )

    for (
        method,
        legal_entity_path,
        success_status,
        response_schema_name,
        request_schema_name,
        error_codes,
    ) in POLICY_LEGAL_ENTITY_OPENAPI_PATHS:
        path_item = paths.get(legal_entity_path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {legal_entity_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required legal-entity operation is missing",
        )
        if not isinstance(operation, dict):
            continue
        parameter_refs, _ = _parameter_names(operation)
        for required_parameter in ("TenantHeader", "BookHeaderDirectOptional"):
            contracts.check(
                required_parameter in parameter_refs,
                f"{where}: must document the shared {required_parameter} parameter",
            )
        path_parameter_name = None
        if "{policyId}" in legal_entity_path:
            path_parameter_name = "policyId"
        elif "{legalEntityId}" in legal_entity_path:
            path_parameter_name = "legalEntityId"
        if path_parameter_name:
            path_parameter = _inline_parameter(operation, path_parameter_name)
            contracts.check(
                isinstance(path_parameter, dict),
                f"{where}: must declare the {path_parameter_name} path parameter",
            )
            if isinstance(path_parameter, dict):
                contracts.check(
                    path_parameter.get("in") == "path"
                    and path_parameter.get("required") is True
                    and (path_parameter.get("schema") or {}).get("format") == "uuid",
                    f"{where}: {path_parameter_name} must be a required uuid path "
                    "parameter",
                )
        responses = operation.get("responses") or {}
        contracts.check(
            success_status in responses,
            f"{where}: must document response {success_status}",
        )
        success_schema = _response_schema(operation, success_status)
        success_ref = (
            str(success_schema.get("$ref", ""))
            if isinstance(success_schema, dict)
            else ""
        )
        array_item_ref = (
            str((success_schema.get("items") or {}).get("$ref", ""))
            if isinstance(success_schema, dict)
            and success_schema.get("type") == "array"
            else ""
        )
        contracts.check(
            success_ref.endswith(f"/schemas/{response_schema_name}")
            or array_item_ref.endswith(f"/schemas/{response_schema_name}"),
            f"{where}: {success_status} must return the {response_schema_name} "
            "schema",
        )
        if success_status == "201":
            created = responses.get("201") if isinstance(responses, dict) else None
            headers = created.get("headers") if isinstance(created, dict) else None
            contracts.check(
                isinstance(headers, dict) and "Location" in headers,
                f"{where}: 201 must declare the Location header",
            )
        if method == "patch":
            ok = responses.get("200") if isinstance(responses, dict) else None
            headers = ok.get("headers") if isinstance(ok, dict) else None
            contracts.check(
                isinstance(headers, dict) and "ETag" in headers,
                f"{where}: 200 must declare the shared ETag header",
            )
            contracts.check(
                not ({"IfMatch", "IdempotencyKey"} & set(parameter_refs)),
                f"{where}: must not accept If-Match or Idempotency-Key in this "
                "slice",
            )
        for code in error_codes:
            contracts.check(
                code in responses,
                f"{where}: must document response {code}",
            )
        if request_schema_name:
            request_body = operation.get("requestBody") or {}
            request_schema = (
                ((request_body.get("content") or {}).get("application/json") or {})
                .get("schema")
                if isinstance(request_body, dict)
                else None
            )
            contracts.check(
                isinstance(request_schema, dict)
                and str(request_schema.get("$ref", "")).endswith(
                    f"/schemas/{request_schema_name}"
                ),
                f"{where}: request body must use the {request_schema_name} schema",
            )

    implemented_paths = sorted(
        {entry[1] for entry in POLICY_LEGAL_ENTITY_OPENAPI_PATHS}
    )
    for entry in document.get("x-planned-operations") or []:
        if isinstance(entry, dict) and entry.get("path") in implemented_paths:
            contracts.check(
                False,
                f"{relative}: {entry.get('path')} must not remain in "
                "x-planned-operations",
            )


def check_policy_legal_entities_asyncapi(contracts: ContractSet, document, relative: str):
    """Require the two implemented legal-entity channels and payloads."""
    channels = document.get("channels") or {}
    operations = document.get("operations") or {}
    messages = (document.get("components") or {}).get("messages") or {}
    channel_by_address = {}
    implemented_addresses = set()
    for channel in channels.values():
        if not isinstance(channel, dict):
            continue
        address = channel.get("address")
        if address:
            channel_by_address[address] = channel
            if channel.get("x-status") == "implemented":
                implemented_addresses.add(address)
    send_events = {
        operation.get("x-event-type")
        for operation in operations.values()
        if isinstance(operation, dict) and operation.get("action") == "send"
    }

    for event in POLICY_LEGAL_ENTITY_EVENTS:
        contracts.check(
            event in channel_by_address,
            f"{relative}: required legal-entity event channel '{event}' is "
            "missing",
        )
        contracts.check(
            event in implemented_addresses,
            f"{relative}: legal-entity event channel '{event}' must be "
            "implemented",
        )
        contracts.check(
            event in send_events,
            f"{relative}: legal-entity event '{event}' must have a send "
            "operation",
        )
        channel = channel_by_address.get(event) or {}
        channel_messages = channel.get("messages") or {}
        contracts.check(
            str(channel.get("x-implemented-by", "")).endswith(
                POLICY_LEGAL_ENTITY_EVENT_IMPLEMENTED_BY
            ),
            f"{relative}: {event} must name "
            f"{POLICY_LEGAL_ENTITY_EVENT_IMPLEMENTED_BY} in x-implemented-by",
        )
        if event == "policy.legal-entity.created":
            contracts.check(
                POLICY_LEGAL_ENTITY_CREATED_EVENT_MESSAGE in channel_messages,
                f"{relative}: {event} must reference "
                f"{POLICY_LEGAL_ENTITY_CREATED_EVENT_MESSAGE}",
            )
        else:
            contracts.check(
                POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_MESSAGE in channel_messages,
                f"{relative}: {event} must reference "
                f"{POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_MESSAGE}",
            )

    created_message = messages.get(POLICY_LEGAL_ENTITY_CREATED_EVENT_MESSAGE) or {}
    created_payload = created_message.get("payload") or {}
    created_properties = created_payload.get("properties") or {}
    created_required = set(created_payload.get("required") or [])
    for field in POLICY_LEGAL_ENTITY_CREATED_EVENT_FIELDS:
        contracts.check(
            field in created_properties,
            f"{relative}: {POLICY_LEGAL_ENTITY_CREATED_EVENT_MESSAGE}."
            f"properties.{field} is required",
        )
        contracts.check(
            field in created_required,
            f"{relative}: {POLICY_LEGAL_ENTITY_CREATED_EVENT_MESSAGE}.required "
            f"must list {field}",
        )
    contracts.check(
        (created_properties.get("legalEntityId") or {}).get("format") == "uuid",
        f"{relative}: {POLICY_LEGAL_ENTITY_CREATED_EVENT_MESSAGE}.legalEntityId "
        "must be a uuid",
    )
    contracts.check(
        tuple((created_properties.get("entityType") or {}).get("enum") or [])
        == POLICY_LEGAL_ENTITY_TYPES,
        f"{relative}: {POLICY_LEGAL_ENTITY_CREATED_EVENT_MESSAGE}.entityType "
        f"must enumerate {list(POLICY_LEGAL_ENTITY_TYPES)}",
    )
    contracts.check(
        tuple((created_properties.get("status") or {}).get("enum") or [])
        == POLICY_LEGAL_ENTITY_STATUSES,
        f"{relative}: {POLICY_LEGAL_ENTITY_CREATED_EVENT_MESSAGE}.status must "
        f"enumerate {list(POLICY_LEGAL_ENTITY_STATUSES)}",
    )
    contracts.check(
        (created_properties.get("jurisdiction") or {}).get("pattern")
        == POLICY_LEGAL_ENTITY_JURISDICTION_PATTERN,
        f"{relative}: {POLICY_LEGAL_ENTITY_CREATED_EVENT_MESSAGE}.jurisdiction "
        "must be a two-letter uppercase code",
    )
    for field in POLICY_LEGAL_ENTITY_NULLABLE_FIELDS:
        contracts.check(
            _schema_types(created_properties.get(field)) == {"string", "null"},
            f"{relative}: {POLICY_LEGAL_ENTITY_CREATED_EVENT_MESSAGE}.{field} "
            "must be a nullable string",
        )
    contracts.check(
        (created_properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: {POLICY_LEGAL_ENTITY_CREATED_EVENT_MESSAGE}.createdAt "
        "must be a date-time",
    )

    assigned_message = messages.get(POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_MESSAGE) or {}
    assigned_payload = assigned_message.get("payload") or {}
    assigned_properties = assigned_payload.get("properties") or {}
    assigned_required = set(assigned_payload.get("required") or [])
    for field in POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_FIELDS:
        contracts.check(
            field in assigned_properties,
            f"{relative}: {POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_MESSAGE}."
            f"properties.{field} is required",
        )
        contracts.check(
            field in assigned_required,
            f"{relative}: {POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_MESSAGE}.required "
            f"must list {field}",
        )
    contracts.check(
        (assigned_properties.get("policyId") or {}).get("format") == "uuid",
        f"{relative}: {POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_MESSAGE}.policyId "
        "must be a uuid",
    )
    for field in ("legalEntityId", "previousLegalEntityId"):
        field_schema = assigned_properties.get(field) or {}
        contracts.check(
            _schema_types(field_schema) == {"string", "null"}
            and field_schema.get("format") == "uuid",
            f"{relative}: {POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_MESSAGE}.{field} "
            "must be a nullable uuid",
        )
    changed_fields = assigned_properties.get("changedFields") or {}
    contracts.check(
        changed_fields.get("type") == "array"
        and (changed_fields.get("items") or {}).get("type") == "string"
        and "legalEntityId" in str(changed_fields.get("description") or ""),
        f"{relative}: {POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_MESSAGE}.changedFields "
        "must be a string array naming legalEntityId",
    )
    contracts.check(
        (assigned_properties.get("version") or {}).get("type") == "integer",
        f"{relative}: {POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_MESSAGE}.version must "
        "be an integer",
    )
    for field in ("premiumAmount", "limitAmount"):
        contracts.check(
            (assigned_properties.get(field) or {}).get("type") == "string",
            f"{relative}: {POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_MESSAGE}.{field} "
            "must be a decimal string",
        )
    for field in ("premiumCurrency", "limitCurrency"):
        contracts.check(
            (assigned_properties.get(field) or {}).get("pattern") == "^[A-Z]{3}$",
            f"{relative}: {POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_MESSAGE}.{field} "
            "must be a three-letter uppercase currency",
        )
    for field in ("effectiveDate", "expirationDate"):
        contracts.check(
            (assigned_properties.get(field) or {}).get("format") == "date",
            f"{relative}: {POLICY_LEGAL_ENTITY_ASSIGNED_EVENT_MESSAGE}.{field} "
            "must be a date",
        )


# ---------------------------------------------------------------------------
# Policy premium-audit checks
# ---------------------------------------------------------------------------


def check_policy_premium_audit_openapi(contracts: ContractSet, document, relative: str):
    """Require the audited-premium command, its schema, and its error rules."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    path_item = paths.get(POLICY_PREMIUM_AUDIT_PATH) if isinstance(paths, dict) else None
    operation = path_item.get("post") if isinstance(path_item, dict) else None
    where = f"{relative}: POST {POLICY_PREMIUM_AUDIT_PATH}"
    contracts.check(
        isinstance(operation, dict),
        f"{where}: required premium-audit operation is missing",
    )
    if isinstance(operation, dict):
        parameter_refs, inline_names = _parameter_names(operation)
        for parameter in ("TenantHeader", "BookHeaderDirectOptional", "IfMatch"):
            contracts.check(
                parameter in parameter_refs,
                f"{where}: must document the shared {parameter} parameter",
            )
        contracts.check(
            "policyId" in inline_names,
            f"{where}: must declare the policyId path parameter",
        )

        request_body = operation.get("requestBody") or {}
        contracts.check(
            request_body.get("required") is True,
            f"{where}: request body must be required",
        )
        request_schema = (
            ((request_body.get("content") or {}).get("application/json") or {}).get("schema")
            if isinstance(request_body, dict)
            else None
        )
        contracts.check(
            isinstance(request_schema, dict)
            and str(request_schema.get("$ref", "")).endswith(
                f"/schemas/{POLICY_PREMIUM_AUDIT_REQUEST}"
            ),
            f"{where}: request body must use the {POLICY_PREMIUM_AUDIT_REQUEST} schema",
        )

        created = (operation.get("responses") or {}).get("201")
        created_headers = created.get("headers") if isinstance(created, dict) else None
        tag = created_headers.get("ETag") if isinstance(created_headers, dict) else None
        contracts.check(
            isinstance(tag, dict)
            and str(tag.get("$ref", "")).endswith("/headers/ETag"),
            f"{where}: 201 must declare the shared ETag header",
        )
        created_schema = _response_schema(operation, "201")
        contracts.check(
            isinstance(created_schema, dict)
            and str(created_schema.get("$ref", "")).endswith("/schemas/Policy"),
            f"{where}: 201 must return the updated Policy schema",
        )

        responses = operation.get("responses") or {}
        for code, suffix in (
            ("400", "BadRequest"),
            ("404", "NotFound"),
            ("422", "UnprocessableContent"),
            ("428", "PreconditionRequired"),
        ):
            response = responses.get(code) if isinstance(responses, dict) else None
            contracts.check(
                isinstance(response, dict)
                and str(response.get("$ref", "")).endswith(f"/responses/{suffix}"),
                f"{where}: {code} must reference the shared {suffix} response",
            )
        conflict = responses.get("409") if isinstance(responses, dict) else None
        conflict_text = (
            str(conflict.get("description") or "") if isinstance(conflict, dict) else ""
        )
        for code in ("PREMIUM_AUDIT_NOT_ALLOWED", "CONCURRENT_MODIFICATION"):
            contracts.check(
                code in conflict_text,
                f"{where}: 409 must document {code}",
            )
        conflict_schema = _response_schema(operation, "409", "application/problem+json")
        contracts.check(
            isinstance(conflict_schema, dict)
            and str(conflict_schema.get("$ref", "")).endswith("/schemas/Problem"),
            f"{where}: 409 must document the shared Problem schema",
        )

        description = str(operation.get("description") or "")
        for status in POLICY_PREMIUM_AUDIT_ALLOWED_STATUSES:
            contracts.check(
                status in description,
                f"{where}: description must name the auditable status {status}",
            )
        for term in (
            POLICY_PREMIUM_AUDIT_CHANGE_TYPE,
            "NO_PREMIUM_CHANGE",
            "PREMIUM_AUDIT_NOT_ALLOWED",
            "CONCURRENT_MODIFICATION",
            "VERSION_OUTSIDE_POLICY_TERM",
            "VERSION_REGRESSION",
            "VERSION_BACKDATE_REASON_REQUIRED",
            "APPROVAL_REQUIRED",
            POLICY_PREMIUM_AUDIT_EVENT,
            POLICY_PREMIUM_AUDIT_SPEC_EVENT,
            "same transaction",
            "ETag",
        ):
            contracts.check(
                term in description,
                f"{where}: description must document {term}",
            )

    planned_operations = document.get("x-planned-operations") or []
    planned_pairs = {
        (str(entry.get("method", "")).lower(), entry.get("path"))
        for entry in planned_operations
        if isinstance(entry, dict)
    }
    contracts.check(
        ("post", POLICY_PREMIUM_AUDIT_PATH) not in planned_pairs,
        f"{relative}: implemented premium-audit operation must not reappear under "
        "x-planned-operations",
    )

    request = schemas.get(POLICY_PREMIUM_AUDIT_REQUEST) or {}
    request_properties = request.get("properties") or {}
    request_required = set(request.get("required") or [])
    contracts.check(
        isinstance(request, dict) and request.get("type") == "object",
        f"{relative}: {POLICY_PREMIUM_AUDIT_REQUEST} must be an object schema",
    )
    contracts.check(
        request_required == set(POLICY_PREMIUM_AUDIT_REQUIRED_FIELDS),
        f"{relative}: {POLICY_PREMIUM_AUDIT_REQUEST} must require exactly "
        f"{list(POLICY_PREMIUM_AUDIT_REQUIRED_FIELDS)}",
    )
    for field in POLICY_PREMIUM_AUDIT_REQUIRED_FIELDS:
        contracts.check(
            field in request_properties,
            f"{relative}: {POLICY_PREMIUM_AUDIT_REQUEST}.properties.{field} "
            "is required",
        )
    for field in POLICY_PREMIUM_AUDIT_OPTIONAL_FIELDS:
        contracts.check(
            field in request_properties,
            f"{relative}: {POLICY_PREMIUM_AUDIT_REQUEST}.properties.{field} "
            "is required as an optional member",
        )
        contracts.check(
            field not in request_required,
            f"{relative}: {POLICY_PREMIUM_AUDIT_REQUEST}.{field} must stay optional",
        )
        contracts.check(
            (request_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: {POLICY_PREMIUM_AUDIT_REQUEST}.{field} must be a uuid",
        )
    audited = request_properties.get("auditedPremium") or {}
    contracts.check(
        audited.get("type") == "string"
        and audited.get("pattern") == POLICY_PREMIUM_AUDIT_AMOUNT_PATTERN,
        f"{relative}: {POLICY_PREMIUM_AUDIT_REQUEST}.auditedPremium must be a "
        "non-negative money decimal string",
    )
    contracts.check(
        (request_properties.get("effectiveDate") or {}).get("format") == "date",
        f"{relative}: {POLICY_PREMIUM_AUDIT_REQUEST}.effectiveDate must be a date",
    )
    reason = request_properties.get("reason") or {}
    contracts.check(
        reason.get("type") == "string"
        and reason.get("minLength") == 1
        and reason.get("maxLength") == POLICY_PREMIUM_AUDIT_REASON_MAX_LENGTH,
        f"{relative}: {POLICY_PREMIUM_AUDIT_REQUEST}.reason must be a non-blank "
        f"string of at most {POLICY_PREMIUM_AUDIT_REASON_MAX_LENGTH} characters",
    )


def check_policy_premium_audit_asyncapi(contracts: ContractSet, document, relative: str):
    """Require the implemented premium-audited channel and its eight-member payload."""
    channels = document.get("channels") or {}
    operations = document.get("operations") or {}
    messages = (document.get("components") or {}).get("messages") or {}
    send_events = {
        operation.get("x-event-type")
        for operation in operations.values()
        if isinstance(operation, dict) and operation.get("action") == "send"
    }

    channel = next(
        (
            candidate
            for candidate in channels.values()
            if isinstance(candidate, dict)
            and candidate.get("address") == POLICY_PREMIUM_AUDIT_EVENT
        ),
        None,
    )
    contracts.check(
        isinstance(channel, dict),
        f"{relative}: required premium-audited channel "
        f"'{POLICY_PREMIUM_AUDIT_EVENT}' is missing",
    )
    if not isinstance(channel, dict):
        return
    contracts.check(
        channel.get("x-status") == "implemented",
        f"{relative}: {POLICY_PREMIUM_AUDIT_EVENT} channel must be implemented",
    )
    contracts.check(
        channel.get("x-event-version") == 1,
        f"{relative}: {POLICY_PREMIUM_AUDIT_EVENT} channel must stay at "
        "x-event-version 1",
    )
    contracts.check(
        str(channel.get("x-implemented-by", "")).endswith(
            POLICY_PREMIUM_AUDIT_EVENT_IMPLEMENTED_BY
        ),
        f"{relative}: {POLICY_PREMIUM_AUDIT_EVENT} must name "
        f"{POLICY_PREMIUM_AUDIT_EVENT_IMPLEMENTED_BY} in x-implemented-by",
    )
    contracts.check(
        POLICY_PREMIUM_AUDIT_EVENT in send_events,
        f"{relative}: {POLICY_PREMIUM_AUDIT_EVENT} must have a send operation",
    )
    channel_messages = channel.get("messages") or {}
    contracts.check(
        (channel_messages.get(POLICY_PREMIUM_AUDIT_EVENT_MESSAGE) or {}).get("$ref")
        == f"#/components/messages/{POLICY_PREMIUM_AUDIT_EVENT_MESSAGE}",
        f"{relative}: {POLICY_PREMIUM_AUDIT_EVENT} must reference "
        f"{POLICY_PREMIUM_AUDIT_EVENT_MESSAGE}",
    )

    message = messages.get(POLICY_PREMIUM_AUDIT_EVENT_MESSAGE) or {}
    payload = message.get("payload") or {}
    properties = payload.get("properties") or {}
    required = set(payload.get("required") or [])
    contracts.check(
        required == set(POLICY_PREMIUM_AUDIT_EVENT_FIELDS),
        f"{relative}: {POLICY_PREMIUM_AUDIT_EVENT_MESSAGE} must require exactly "
        f"{list(POLICY_PREMIUM_AUDIT_EVENT_FIELDS)}",
    )
    for field in POLICY_PREMIUM_AUDIT_EVENT_FIELDS:
        contracts.check(
            field in properties,
            f"{relative}: {POLICY_PREMIUM_AUDIT_EVENT_MESSAGE}.properties.{field} "
            "is required",
        )
    contracts.check(
        (properties.get("policyId") or {}).get("format") == "uuid",
        f"{relative}: {POLICY_PREMIUM_AUDIT_EVENT_MESSAGE}.policyId must be a uuid",
    )
    for field in ("previousPremium", "auditedPremium", "delta"):
        contracts.check(
            (properties.get(field) or {}).get("type") == "string",
            f"{relative}: {POLICY_PREMIUM_AUDIT_EVENT_MESSAGE}.{field} must be a "
            "decimal string",
        )
    contracts.check(
        (properties.get("currency") or {}).get("pattern") == "^[A-Z]{3}$",
        f"{relative}: {POLICY_PREMIUM_AUDIT_EVENT_MESSAGE}.currency must be an "
        "uppercase ISO code",
    )
    contracts.check(
        (properties.get("effectiveDate") or {}).get("format") == "date",
        f"{relative}: {POLICY_PREMIUM_AUDIT_EVENT_MESSAGE}.effectiveDate must be "
        "a date",
    )
    contracts.check(
        (properties.get("reason") or {}).get("maxLength")
        == POLICY_PREMIUM_AUDIT_REASON_MAX_LENGTH,
        f"{relative}: {POLICY_PREMIUM_AUDIT_EVENT_MESSAGE}.reason must be at most "
        f"{POLICY_PREMIUM_AUDIT_REASON_MAX_LENGTH} characters",
    )


def check_policy_billing_adjustment_asyncapi(
    contracts: ContractSet, document, relative: str
):
    """Require the implemented positive-adjustment channel and nine-member payload."""
    channels = document.get("channels") or {}
    operations = document.get("operations") or {}
    messages = (document.get("components") or {}).get("messages") or {}
    send_events = {
        operation.get("x-event-type")
        for operation in operations.values()
        if isinstance(operation, dict) and operation.get("action") == "send"
    }

    channel = next(
        (
            candidate
            for candidate in channels.values()
            if isinstance(candidate, dict)
            and candidate.get("address") == BILLING_ADJUSTMENT_EVENT
        ),
        None,
    )
    contracts.check(
        isinstance(channel, dict),
        f"{relative}: required billing-adjustment channel "
        f"'{BILLING_ADJUSTMENT_EVENT}' is missing",
    )
    if not isinstance(channel, dict):
        return
    contracts.check(
        channel.get("x-status") == "implemented",
        f"{relative}: {BILLING_ADJUSTMENT_EVENT} channel must be implemented",
    )
    contracts.check(
        channel.get("x-event-version") == 1,
        f"{relative}: {BILLING_ADJUSTMENT_EVENT} channel must stay at "
        "x-event-version 1",
    )
    contracts.check(
        str(channel.get("x-implemented-by", "")).endswith("PolicyEvents.java"),
        f"{relative}: {BILLING_ADJUSTMENT_EVENT} must name PolicyEvents.java in "
        "x-implemented-by",
    )
    contracts.check(
        BILLING_ADJUSTMENT_EVENT in send_events,
        f"{relative}: {BILLING_ADJUSTMENT_EVENT} must have a send operation",
    )
    channel_messages = channel.get("messages") or {}
    contracts.check(
        (
            channel_messages.get(BILLING_ADJUSTMENT_EVENT_MESSAGE) or {}
        ).get("$ref")
        == f"#/components/messages/{BILLING_ADJUSTMENT_EVENT_MESSAGE}",
        f"{relative}: {BILLING_ADJUSTMENT_EVENT} must reference "
        f"{BILLING_ADJUSTMENT_EVENT_MESSAGE}",
    )

    message = messages.get(BILLING_ADJUSTMENT_EVENT_MESSAGE) or {}
    payload = message.get("payload") or {}
    properties = payload.get("properties") or {}
    required = set(payload.get("required") or [])
    contracts.check(
        required == set(BILLING_ADJUSTMENT_EVENT_FIELDS),
        f"{relative}: {BILLING_ADJUSTMENT_EVENT_MESSAGE} must require exactly "
        f"{list(BILLING_ADJUSTMENT_EVENT_FIELDS)}",
    )
    for field in BILLING_ADJUSTMENT_EVENT_FIELDS:
        contracts.check(
            field in properties,
            f"{relative}: {BILLING_ADJUSTMENT_EVENT_MESSAGE}.properties.{field} "
            "is required",
        )
    for field in ("policyId", "planId", "installmentId"):
        contracts.check(
            (properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: {BILLING_ADJUSTMENT_EVENT_MESSAGE}.{field} must be a uuid",
        )
    for field in ("adjustmentAmount", "newTotalPremium"):
        contracts.check(
            (properties.get(field) or {}).get("type") == "string",
            f"{relative}: {BILLING_ADJUSTMENT_EVENT_MESSAGE}.{field} must be a "
            "decimal string",
        )
    installment_number = properties.get("installmentNumber") or {}
    contracts.check(
        (
            installment_number.get("type"),
            installment_number.get("minimum"),
        )
        == ("integer", 1),
        f"{relative}: {BILLING_ADJUSTMENT_EVENT_MESSAGE}.installmentNumber must "
        "be an integer >= 1",
    )
    contracts.check(
        (properties.get("dueDate") or {}).get("format") == "date",
        f"{relative}: {BILLING_ADJUSTMENT_EVENT_MESSAGE}.dueDate must be a date",
    )
    reason = properties.get("reason") or {}
    contracts.check(
        reason.get("type") == "string"
        and reason.get("maxLength") == BILLING_ADJUSTMENT_REASON_MAX_LENGTH,
        f"{relative}: {BILLING_ADJUSTMENT_EVENT_MESSAGE}.reason must be a string "
        f"of at most {BILLING_ADJUSTMENT_REASON_MAX_LENGTH} characters",
    )


# ---------------------------------------------------------------------------
# Contract technical-account checks
# ---------------------------------------------------------------------------


def check_contract_technical_accounts(contracts: ContractSet, document, relative: str):
    """Require the technical-account operations, schemas, and field rules."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    for method, account_path, success_status, response_schema_name, request_schema_name in (
        CONTRACT_TECHNICAL_ACCOUNT_PATHS
    ):
        path_item = paths.get(account_path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {account_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required technical-account operation is missing",
        )
        if not isinstance(operation, dict):
            continue

        parameter_refs, inline_names = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must document the shared TenantHeader parameter",
        )
        contracts.check(
            "BookHeaderAssumed" in parameter_refs,
            f"{where}: must document the shared BookHeaderAssumed parameter",
        )
        contracts.check(
            "contractId" in inline_names,
            f"{where}: must declare the contractId path parameter",
        )
        if method == "patch":
            contracts.check(
                "accountId" in inline_names,
                f"{where}: must declare the accountId path parameter",
            )

        responses = operation.get("responses") or {}
        for code in ("400", "404"):
            contracts.check(
                code in responses,
                f"{where}: must document the {code} response",
            )
        if method in ("post", "patch"):
            contracts.check(
                "409" in responses,
                f"{where}: must document the 409 response",
            )
        if method == "patch":
            description = str(operation.get("description") or "")
            contracts.check(
                CONTRACT_TECHNICAL_ACCOUNT_STATUS_REFERENCE_FIELD in description
                and CONTRACT_TECHNICAL_ACCOUNT_INVALID_REFERENCE in description,
                f"{where}: must document the settlement reference and "
                f"{CONTRACT_TECHNICAL_ACCOUNT_INVALID_REFERENCE}",
            )
            bad_request = responses.get("400") or {}
            bad_request_description = (
                bad_request.get("description")
                if isinstance(bad_request, dict)
                else ""
            ) or ""
            contracts.check(
                CONTRACT_TECHNICAL_ACCOUNT_INVALID_REFERENCE
                in str(bad_request_description),
                f"{where}: 400 must document "
                f"{CONTRACT_TECHNICAL_ACCOUNT_INVALID_REFERENCE}",
            )

        if method == "get":
            ok_schema = _response_schema(operation, "200")
            contracts.check(
                isinstance(ok_schema, dict)
                and ok_schema.get("type") == "array"
                and str((ok_schema.get("items") or {}).get("$ref", "")).endswith(
                    "/schemas/TechnicalAccount"
                ),
                f"{where}: 200 must return an array of TechnicalAccount",
            )
        else:
            request_body = operation.get("requestBody") or {}
            contracts.check(
                request_body.get("required") is True,
                f"{where}: request body must be required",
            )
            request_schema = (
                ((request_body.get("content") or {}).get("application/json") or {})
                .get("schema")
                if isinstance(request_body, dict)
                else None
            )
            contracts.check(
                isinstance(request_schema, dict)
                and str(request_schema.get("$ref", "")).endswith(
                    f"/schemas/{request_schema_name}"
                ),
                f"{where}: request body must use the {request_schema_name} schema",
            )
            success_schema = _response_schema(operation, success_status)
            contracts.check(
                isinstance(success_schema, dict)
                and str(success_schema.get("$ref", "")).endswith(
                    f"/schemas/{response_schema_name}"
                ),
                f"{where}: {success_status} must return the {response_schema_name} schema",
            )

    account = schemas.get("TechnicalAccount") or {}
    account_properties = account.get("properties") or {}
    account_required = set(account.get("required") or [])
    contracts.check(
        isinstance(account, dict) and account.get("type") == "object",
        f"{relative}: TechnicalAccount must be an object schema",
    )
    for field in CONTRACT_TECHNICAL_ACCOUNT_FIELDS:
        contracts.check(
            field in account_properties,
            f"{relative}: TechnicalAccount.properties.{field} is required",
        )
        contracts.check(
            field in account_required,
            f"{relative}: TechnicalAccount.required must list {field}",
        )
    for field in ("accountId", "contractId"):
        contracts.check(
            (account_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: TechnicalAccount.{field} must be a uuid",
        )
    for field in ("periodStart", "periodEnd"):
        contracts.check(
            (account_properties.get(field) or {}).get("format") == "date",
            f"{relative}: TechnicalAccount.{field} must be a date",
        )
    contracts.check(
        str((account_properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: TechnicalAccount.currency must reference CurrencyCode",
    )
    for field in CONTRACT_TECHNICAL_ACCOUNT_MONEY_FIELDS:
        contracts.check(
            str((account_properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: TechnicalAccount.{field} must reference MoneyAmount",
        )
    contracts.check(
        str((account_properties.get("status") or {}).get("$ref", "")).endswith(
            "/schemas/TechnicalAccountStatus"
        ),
        f"{relative}: TechnicalAccount.status must reference TechnicalAccountStatus",
    )
    contracts.check(
        (account_properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: TechnicalAccount.createdAt must be a date-time",
    )
    settlement_reference = (
        account_properties.get(CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_FIELD)
        or {}
    )
    contracts.check(
        _schema_types(settlement_reference) == {"string", "null"}
        and settlement_reference.get("maxLength")
        == CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_MAX_LENGTH,
        f"{relative}: TechnicalAccount.settlementReference must be a nullable "
        f"string of at most "
        f"{CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_MAX_LENGTH} characters",
    )

    account_status = schemas.get("TechnicalAccountStatus") or {}
    contracts.check(
        account_status.get("type") == "string",
        f"{relative}: TechnicalAccountStatus must be a string enum",
    )
    contracts.check(
        set(account_status.get("enum") or []) == set(CONTRACT_TECHNICAL_ACCOUNT_STATUSES),
        f"{relative}: TechnicalAccountStatus must enumerate "
        f"{list(CONTRACT_TECHNICAL_ACCOUNT_STATUSES)}",
    )

    create = schemas.get("CreateTechnicalAccountRequest") or {}
    create_properties = create.get("properties") or {}
    create_required = set(create.get("required") or [])
    contracts.check(
        isinstance(create, dict) and create.get("type") == "object",
        f"{relative}: CreateTechnicalAccountRequest must be an object schema",
    )
    contracts.check(
        create_required == set(CONTRACT_TECHNICAL_ACCOUNT_CREATE_FIELDS),
        f"{relative}: CreateTechnicalAccountRequest must require "
        f"{list(CONTRACT_TECHNICAL_ACCOUNT_CREATE_FIELDS)}",
    )
    for field in ("periodStart", "periodEnd"):
        contracts.check(
            (create_properties.get(field) or {}).get("format") == "date",
            f"{relative}: CreateTechnicalAccountRequest.{field} must be a date",
        )
    contracts.check(
        str((create_properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: CreateTechnicalAccountRequest.currency must reference CurrencyCode",
    )
    for field in ("cededPremium", "cededLosses", "commission", "otherCharges"):
        contracts.check(
            str((create_properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: CreateTechnicalAccountRequest.{field} must reference MoneyAmount",
        )

    update = schemas.get("UpdateTechnicalAccountStatusRequest") or {}
    update_properties = update.get("properties") or {}
    update_required = set(update.get("required") or [])
    contracts.check(
        isinstance(update, dict) and update.get("type") == "object",
        f"{relative}: UpdateTechnicalAccountStatusRequest must be an object schema",
    )
    contracts.check(
        update_required == {"status"},
        f"{relative}: UpdateTechnicalAccountStatusRequest must require only status",
    )
    contracts.check(
        set((update_properties.get("status") or {}).get("enum") or [])
        == set(CONTRACT_TECHNICAL_ACCOUNT_REQUEST_STATUSES),
        f"{relative}: UpdateTechnicalAccountStatusRequest.status must enumerate "
        f"{list(CONTRACT_TECHNICAL_ACCOUNT_REQUEST_STATUSES)}",
    )
    status_reference = update_properties.get(
        CONTRACT_TECHNICAL_ACCOUNT_STATUS_REFERENCE_FIELD
    ) or {}
    contracts.check(
        CONTRACT_TECHNICAL_ACCOUNT_STATUS_REFERENCE_FIELD in update_properties
        and CONTRACT_TECHNICAL_ACCOUNT_STATUS_REFERENCE_FIELD not in update_required,
        f"{relative}: UpdateTechnicalAccountStatusRequest.reference must be "
        "optional",
    )
    contracts.check(
        _schema_types(status_reference) == {"string", "null"}
        and status_reference.get("maxLength")
        == CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_MAX_LENGTH,
        f"{relative}: UpdateTechnicalAccountStatusRequest.reference must be a "
        f"nullable string of at most "
        f"{CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_MAX_LENGTH} characters",
    )
    settled_condition = next(
        (
            entry
            for entry in update.get("allOf") or []
            if isinstance(entry, dict)
            and ((entry.get("if") or {}).get("properties") or {})
            .get("status", {})
            .get("const")
            == "SETTLED"
        ),
        None,
    )
    contracts.check(
        isinstance(settled_condition, dict),
        f"{relative}: UpdateTechnicalAccountStatusRequest must conditionally "
        "require reference for SETTLED",
    )
    settled_then = (settled_condition or {}).get("then") or {}
    contracts.check(
        set(settled_then.get("required") or [])
        == {CONTRACT_TECHNICAL_ACCOUNT_STATUS_REFERENCE_FIELD},
        f"{relative}: UpdateTechnicalAccountStatusRequest must require reference "
        "when status is SETTLED",
    )
    settled_reference = (
        (settled_then.get("properties") or {}).get(
            CONTRACT_TECHNICAL_ACCOUNT_STATUS_REFERENCE_FIELD
        )
        or {}
    )
    contracts.check(
        settled_reference.get("type") == "string"
        and settled_reference.get("minLength") == 1
        and settled_reference.get("maxLength")
        == CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_MAX_LENGTH
        and "\\S" in str(settled_reference.get("pattern") or ""),
        f"{relative}: a SETTLED reference must be a non-blank string of at most "
        f"{CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_MAX_LENGTH} characters",
    )


# ---------------------------------------------------------------------------
# Contract technical-account line checks
# ---------------------------------------------------------------------------


def check_contract_technical_account_lines(
    contracts: ContractSet, document, relative: str
):
    """Require the technical-account line operations, schemas, and rules."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    for (
        method,
        line_path,
        success_status,
        response_schema_name,
        request_schema_name,
    ) in CONTRACT_TECHNICAL_ACCOUNT_LINE_PATHS:
        path_item = paths.get(line_path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {line_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required technical-account line operation is missing",
        )
        if not isinstance(operation, dict):
            continue

        parameter_refs, inline_names = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must document the shared TenantHeader parameter",
        )
        contracts.check(
            "BookHeaderAssumed" in parameter_refs,
            f"{where}: must document the shared BookHeaderAssumed parameter",
        )
        for path_parameter in ("contractId", "accountId"):
            contracts.check(
                path_parameter in inline_names,
                f"{where}: must declare the {path_parameter} path parameter",
            )
        if method == "delete":
            contracts.check(
                "lineId" in inline_names,
                f"{where}: must declare the lineId path parameter",
            )

        responses = operation.get("responses") or {}
        for code in ("400", "404"):
            contracts.check(
                code in responses,
                f"{where}: must document the {code} response",
            )
        if method in ("post", "delete"):
            contracts.check(
                "409" in responses,
                f"{where}: must document the 409 response",
            )
            conflict = responses.get("409") if isinstance(responses, dict) else None
            conflict_text = (
                str(conflict.get("description") or "")
                if isinstance(conflict, dict)
                else ""
            )
            contracts.check(
                CONTRACT_TECHNICAL_ACCOUNT_LINE_NOT_EDITABLE in conflict_text,
                f"{where}: 409 must document "
                f"{CONTRACT_TECHNICAL_ACCOUNT_LINE_NOT_EDITABLE}",
            )

        description = str(operation.get("description") or "")
        if method in ("post", "delete"):
            contracts.check(
                CONTRACT_TECHNICAL_ACCOUNT_LINE_NOT_EDITABLE in description,
                f"{where}: description must document "
                f"{CONTRACT_TECHNICAL_ACCOUNT_LINE_NOT_EDITABLE}",
            )

        if method == "get":
            contracts.check(
                "requestBody" not in operation,
                f"{where}: the read operation must not declare a request body",
            )
            ok_schema = _response_schema(operation, success_status)
            contracts.check(
                isinstance(ok_schema, dict)
                and str(ok_schema.get("$ref", "")).endswith(
                    f"/schemas/{response_schema_name}"
                ),
                f"{where}: {success_status} must return the "
                f"{response_schema_name} schema",
            )
        elif method == "post":
            request_body = operation.get("requestBody") or {}
            contracts.check(
                request_body.get("required") is True,
                f"{where}: request body must be required",
            )
            request_schema = (
                ((request_body.get("content") or {}).get("application/json") or {})
                .get("schema")
                if isinstance(request_body, dict)
                else None
            )
            contracts.check(
                isinstance(request_schema, dict)
                and str(request_schema.get("$ref", "")).endswith(
                    f"/schemas/{request_schema_name}"
                ),
                f"{where}: request body must use the {request_schema_name} schema",
            )
            success_schema = _response_schema(operation, success_status)
            contracts.check(
                isinstance(success_schema, dict)
                and str(success_schema.get("$ref", "")).endswith(
                    f"/schemas/{response_schema_name}"
                ),
                f"{where}: {success_status} must return the "
                f"{response_schema_name} schema",
            )
        else:
            contracts.check(
                success_status in responses,
                f"{where}: must document the {success_status} response",
            )
            contracts.check(
                _response_schema(operation, success_status) is None,
                f"{where}: {success_status} must not return a body",
            )

    line = schemas.get("TechnicalAccountLine") or {}
    line_properties = line.get("properties") or {}
    line_required = set(line.get("required") or [])
    contracts.check(
        isinstance(line, dict) and line.get("type") == "object",
        f"{relative}: TechnicalAccountLine must be an object schema",
    )
    contracts.check(
        line_required == set(CONTRACT_TECHNICAL_ACCOUNT_LINE_FIELDS),
        f"{relative}: TechnicalAccountLine must require exactly "
        f"{list(CONTRACT_TECHNICAL_ACCOUNT_LINE_FIELDS)}",
    )
    for field in CONTRACT_TECHNICAL_ACCOUNT_LINE_FIELDS:
        contracts.check(
            field in line_properties,
            f"{relative}: TechnicalAccountLine.properties.{field} is required",
        )
    for field in ("lineId", "accountId"):
        contracts.check(
            (line_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: TechnicalAccountLine.{field} must be a uuid",
        )
    contracts.check(
        str((line_properties.get("lineType") or {}).get("$ref", "")).endswith(
            "/schemas/TechnicalAccountLineType"
        ),
        f"{relative}: TechnicalAccountLine.lineType must reference "
        "TechnicalAccountLineType",
    )
    for field, max_length in (
        ("reference", CONTRACT_TECHNICAL_ACCOUNT_LINE_REFERENCE_MAX_LENGTH),
        ("description", CONTRACT_TECHNICAL_ACCOUNT_LINE_DESCRIPTION_MAX_LENGTH),
    ):
        property_schema = line_properties.get(field) or {}
        contracts.check(
            _schema_types(property_schema) == {"string", "null"}
            and property_schema.get("maxLength") == max_length,
            f"{relative}: TechnicalAccountLine.{field} must be a nullable string "
            f"of at most {max_length} characters",
        )
    contracts.check(
        str((line_properties.get("amount") or {}).get("$ref", "")).endswith(
            "/schemas/MoneyAmount"
        ),
        f"{relative}: TechnicalAccountLine.amount must reference MoneyAmount",
    )
    contracts.check(
        (line_properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: TechnicalAccountLine.createdAt must be a date-time",
    )

    line_type = schemas.get("TechnicalAccountLineType") or {}
    line_type_enum = line_type.get("enum") or []
    contracts.check(
        line_type.get("type") == "string",
        f"{relative}: TechnicalAccountLineType must be a string enum",
    )
    contracts.check(
        line_type_enum == list(CONTRACT_TECHNICAL_ACCOUNT_LINE_TYPES),
        f"{relative}: TechnicalAccountLineType must enumerate exactly the 13 "
        f"detail types {list(CONTRACT_TECHNICAL_ACCOUNT_LINE_TYPES)}",
    )
    contracts.check(
        not (
            set(CONTRACT_TECHNICAL_ACCOUNT_LINE_RETIRED_TYPES)
            & set(line_type_enum)
        ),
        f"{relative}: TechnicalAccountLineType must not enumerate the retired "
        f"type(s) {list(CONTRACT_TECHNICAL_ACCOUNT_LINE_RETIRED_TYPES)}",
    )

    mapped_types = [
        line_type_name
        for bucket_types in CONTRACT_TECHNICAL_ACCOUNT_LINE_BUCKET_TYPES.values()
        for line_type_name in bucket_types
    ]
    contracts.check(
        sorted(mapped_types) == sorted(CONTRACT_TECHNICAL_ACCOUNT_LINE_TYPES),
        f"{relative}: the bucket map must cover each of the 13 line types "
        "exactly once",
    )
    contracts.check(
        set(CONTRACT_TECHNICAL_ACCOUNT_LINE_BUCKET_TYPES)
        == set(CONTRACT_TECHNICAL_ACCOUNT_LINE_TOTAL_FIELDS),
        f"{relative}: the bucket map keys must be the four bucket totals "
        f"{list(CONTRACT_TECHNICAL_ACCOUNT_LINE_TOTAL_FIELDS)}",
    )

    totals = schemas.get("TechnicalAccountLineTotals") or {}
    totals_properties = totals.get("properties") or {}
    totals_required = set(totals.get("required") or [])
    contracts.check(
        isinstance(totals, dict) and totals.get("type") == "object",
        f"{relative}: TechnicalAccountLineTotals must be an object schema",
    )
    contracts.check(
        totals_required == set(CONTRACT_TECHNICAL_ACCOUNT_LINE_TOTAL_FIELDS),
        f"{relative}: TechnicalAccountLineTotals must require exactly "
        f"{list(CONTRACT_TECHNICAL_ACCOUNT_LINE_TOTAL_FIELDS)}",
    )
    for field in CONTRACT_TECHNICAL_ACCOUNT_LINE_TOTAL_FIELDS:
        contracts.check(
            str((totals_properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: TechnicalAccountLineTotals.{field} must reference "
            "MoneyAmount",
        )
    details = totals_properties.get("details") or {}
    contracts.check(
        "details" not in totals_required,
        f"{relative}: TechnicalAccountLineTotals.details must be optional",
    )
    contracts.check(
        isinstance(details, dict) and details.get("type") == "object",
        f"{relative}: TechnicalAccountLineTotals.details must be an object map",
    )
    contracts.check(
        str((details.get("additionalProperties") or {}).get("$ref", "")).endswith(
            "/schemas/MoneyAmount"
        ),
        f"{relative}: TechnicalAccountLineTotals.details values must reference "
        "MoneyAmount",
    )
    details_keys = (
        (details.get("propertyNames") or {}).get("enum") or []
        if isinstance(details, dict)
        else []
    )
    contracts.check(
        details_keys == list(CONTRACT_TECHNICAL_ACCOUNT_LINE_TYPES),
        f"{relative}: TechnicalAccountLineTotals.details.propertyNames.enum "
        f"must enumerate the 13 line types "
        f"{list(CONTRACT_TECHNICAL_ACCOUNT_LINE_TYPES)}",
    )
    contracts.check(
        not (
            set(CONTRACT_TECHNICAL_ACCOUNT_LINE_RETIRED_TYPES)
            & set(details_keys)
        ),
        f"{relative}: TechnicalAccountLineTotals.details must not allow the "
        f"retired type(s) {list(CONTRACT_TECHNICAL_ACCOUNT_LINE_RETIRED_TYPES)}",
    )

    summary = schemas.get("LineSummary") or {}
    summary_properties = summary.get("properties") or {}
    summary_required = set(summary.get("required") or [])
    contracts.check(
        isinstance(summary, dict) and summary.get("type") == "object",
        f"{relative}: LineSummary must be an object schema",
    )
    contracts.check(
        summary_required == set(CONTRACT_TECHNICAL_ACCOUNT_LINE_SUMMARY_FIELDS),
        f"{relative}: LineSummary must require exactly "
        f"{list(CONTRACT_TECHNICAL_ACCOUNT_LINE_SUMMARY_FIELDS)}",
    )
    items = summary_properties.get("items") or {}
    contracts.check(
        items.get("type") == "array"
        and str((items.get("items") or {}).get("$ref", "")).endswith(
            "/schemas/TechnicalAccountLine"
        ),
        f"{relative}: LineSummary.items must be an array of "
        "TechnicalAccountLine",
    )
    contracts.check(
        str((summary_properties.get("totals") or {}).get("$ref", "")).endswith(
            "/schemas/TechnicalAccountLineTotals"
        ),
        f"{relative}: LineSummary.totals must reference "
        "TechnicalAccountLineTotals",
    )

    lines_path = CONTRACT_TECHNICAL_ACCOUNT_LINE_PATHS[0][1]
    lines_get = (paths.get(lines_path) or {}).get("get") or {}
    lines_get_description = str(lines_get.get("description") or "")
    contracts.check(
        "bucketTotals" in lines_get_description,
        f"{relative}: GET {lines_path} description must document that the "
        "expert bucketTotals map is normalized into the public buckets",
    )
    contracts.check(
        all(
            token in lines_get_description
            for token in ("details", *CONTRACT_TECHNICAL_ACCOUNT_LINE_TOTAL_FIELDS)
        ),
        f"{relative}: GET {lines_path} description must document the four "
        "bucket totals and the optional details map",
    )
    for line_type_name in CONTRACT_TECHNICAL_ACCOUNT_LINE_TYPES:
        contracts.check(
            line_type_name in lines_get_description,
            f"{relative}: GET {lines_path} description must document the "
            f"{line_type_name} bucket mapping",
        )

    create = schemas.get("CreateTechnicalAccountLineRequest") or {}
    create_properties = create.get("properties") or {}
    create_required = set(create.get("required") or [])
    contracts.check(
        isinstance(create, dict) and create.get("type") == "object",
        f"{relative}: CreateTechnicalAccountLineRequest must be an object schema",
    )
    contracts.check(
        create_required == {"lineType", "amount"},
        f"{relative}: CreateTechnicalAccountLineRequest must require exactly "
        "lineType and amount",
    )
    contracts.check(
        str((create_properties.get("lineType") or {}).get("$ref", "")).endswith(
            "/schemas/TechnicalAccountLineType"
        ),
        f"{relative}: CreateTechnicalAccountLineRequest.lineType must reference "
        "TechnicalAccountLineType",
    )
    contracts.check(
        str((create_properties.get("amount") or {}).get("$ref", "")).endswith(
            "/schemas/MoneyAmount"
        ),
        f"{relative}: CreateTechnicalAccountLineRequest.amount must reference "
        "MoneyAmount",
    )
    for field, max_length in (
        ("reference", CONTRACT_TECHNICAL_ACCOUNT_LINE_REFERENCE_MAX_LENGTH),
        ("description", CONTRACT_TECHNICAL_ACCOUNT_LINE_DESCRIPTION_MAX_LENGTH),
    ):
        property_schema = create_properties.get(field) or {}
        contracts.check(
            _schema_types(property_schema) == {"string", "null"}
            and property_schema.get("maxLength") == max_length,
            f"{relative}: CreateTechnicalAccountLineRequest.{field} must be an "
            f"optional nullable string of at most {max_length} characters",
        )

    status_path = (
        "/api/v1/contracts/{contractId}/technical-accounts/{accountId}/status"
    )
    status_item = paths.get(status_path) if isinstance(paths, dict) else None
    status_operation = status_item.get("patch") if isinstance(status_item, dict) else None
    contracts.check(
        isinstance(status_operation, dict),
        f"{relative}: PATCH {status_path} is required to document line "
        "reconciliation",
    )
    if isinstance(status_operation, dict):
        status_description = str(status_operation.get("description") or "")
        status_conflict = (
            (status_operation.get("responses") or {}).get("409") or {}
        )
        status_conflict_text = str(status_conflict.get("description") or "")
        contracts.check(
            CONTRACT_TECHNICAL_ACCOUNT_LINE_RECONCILE in status_description,
            f"{relative}: PATCH {status_path} description must document "
            f"{CONTRACT_TECHNICAL_ACCOUNT_LINE_RECONCILE}",
        )
        contracts.check(
            CONTRACT_TECHNICAL_ACCOUNT_LINE_RECONCILE in status_conflict_text,
            f"{relative}: PATCH {status_path} 409 must document "
            f"{CONTRACT_TECHNICAL_ACCOUNT_LINE_RECONCILE}",
        )
        contracts.check(
            "DRAFT" in status_description and "ISSUED" in status_description,
            f"{relative}: PATCH {status_path} description must document the "
            "DRAFT -> ISSUED reconciliation point",
        )
        for bucket, bucket_types in (
            CONTRACT_TECHNICAL_ACCOUNT_LINE_BUCKET_TYPES.items()
        ):
            contracts.check(
                bucket in status_description,
                f"{relative}: PATCH {status_path} description must document "
                f"the {bucket} bucket",
            )
            contracts.check(
                CONTRACT_TECHNICAL_ACCOUNT_LINE_BUCKET_HEADER_FIELDS[bucket]
                in status_description,
                f"{relative}: PATCH {status_path} description must document "
                f"the {bucket} -> "
                f"{CONTRACT_TECHNICAL_ACCOUNT_LINE_BUCKET_HEADER_FIELDS[bucket]} "
                "header mapping",
            )
            for line_type_name in bucket_types:
                contracts.check(
                    line_type_name in status_description,
                    f"{relative}: PATCH {status_path} description must document "
                    f"that {line_type_name} rolls into {bucket}",
                )
        contracts.check(
            "bucket" in status_description,
            f"{relative}: PATCH {status_path} description must describe the "
            "bucket reconciliation",
        )

    planned = {
        (entry.get("method", "").lower(), entry.get("path"))
        for entry in document.get("x-planned-operations") or []
        if isinstance(entry, dict)
    }
    for method, line_path, *_ in CONTRACT_TECHNICAL_ACCOUNT_LINE_PATHS:
        contracts.check(
            (method, line_path) not in planned,
            f"{relative}: implemented line operation {method.upper()} "
            f"{line_path} must not reappear under x-planned-operations",
        )


def check_contract_technical_accounts_asyncapi(
    contracts: ContractSet, document, relative: str
):
    """Require the three implemented account channels and their shared payload."""
    channels = document.get("channels") or {}
    operations = document.get("operations") or {}
    messages = (document.get("components") or {}).get("messages") or {}
    send_events = {
        operation.get("x-event-type")
        for operation in operations.values()
        if isinstance(operation, dict) and operation.get("action") == "send"
    }

    for event in CONTRACT_TECHNICAL_ACCOUNT_EVENTS:
        channel = next(
            (
                candidate
                for candidate in channels.values()
                if isinstance(candidate, dict)
                and candidate.get("address") == event
            ),
            None,
        )
        contracts.check(
            isinstance(channel, dict),
            f"{relative}: required technical-account event channel '{event}' is "
            "missing",
        )
        if not isinstance(channel, dict):
            continue
        contracts.check(
            channel.get("x-status") == "implemented",
            f"{relative}: technical-account event channel '{event}' must be "
            "implemented",
        )
        contracts.check(
            str(channel.get("x-implemented-by", "")).endswith(
                CONTRACT_TECHNICAL_ACCOUNT_EVENT_IMPLEMENTED_BY
            ),
            f"{relative}: technical-account event channel '{event}' must name "
            f"{CONTRACT_TECHNICAL_ACCOUNT_EVENT_IMPLEMENTED_BY} in "
            "x-implemented-by",
        )
        contracts.check(
            event in send_events,
            f"{relative}: technical-account event '{event}' must have a send "
            "operation",
        )
        channel_messages = channel.get("messages") or {}
        contracts.check(
            (
                channel_messages.get(CONTRACT_TECHNICAL_ACCOUNT_EVENT_MESSAGE)
                or {}
            ).get("$ref")
            == f"#/components/messages/{CONTRACT_TECHNICAL_ACCOUNT_EVENT_MESSAGE}",
            f"{relative}: {event} must reference "
            f"{CONTRACT_TECHNICAL_ACCOUNT_EVENT_MESSAGE}",
        )

    message = messages.get(CONTRACT_TECHNICAL_ACCOUNT_EVENT_MESSAGE) or {}
    payload = message.get("payload") or {}
    payload_properties = payload.get("properties") or {}
    payload_required = set(payload.get("required") or [])
    contracts.check(
        payload_required == set(CONTRACT_TECHNICAL_ACCOUNT_EVENT_FIELDS),
        f"{relative}: {CONTRACT_TECHNICAL_ACCOUNT_EVENT_MESSAGE} must require "
        f"exactly {list(CONTRACT_TECHNICAL_ACCOUNT_EVENT_FIELDS)}",
    )
    for field in CONTRACT_TECHNICAL_ACCOUNT_EVENT_FIELDS:
        contracts.check(
            field in payload_properties,
            f"{relative}: {CONTRACT_TECHNICAL_ACCOUNT_EVENT_MESSAGE}."
            f"properties.{field} is required",
        )
    contracts.check(
        set((payload_properties.get("status") or {}).get("enum") or [])
        == set(CONTRACT_TECHNICAL_ACCOUNT_STATUSES),
        f"{relative}: {CONTRACT_TECHNICAL_ACCOUNT_EVENT_MESSAGE}.status must "
        f"enumerate {list(CONTRACT_TECHNICAL_ACCOUNT_STATUSES)}",
    )
    settlement_reference = payload_properties.get(
        CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_FIELD
    ) or {}
    contracts.check(
        CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_FIELD
        in payload_properties,
        f"{relative}: {CONTRACT_TECHNICAL_ACCOUNT_EVENT_MESSAGE}.properties."
        "settlementReference is required for the settled event",
    )
    contracts.check(
        CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_FIELD
        not in payload_required,
        f"{relative}: {CONTRACT_TECHNICAL_ACCOUNT_EVENT_MESSAGE}."
        "settlementReference must stay optional because created and issued omit "
        "it",
    )
    contracts.check(
        settlement_reference.get("type") == "string"
        and settlement_reference.get("maxLength")
        == CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_MAX_LENGTH,
        f"{relative}: {CONTRACT_TECHNICAL_ACCOUNT_EVENT_MESSAGE}."
        "settlementReference must be a string of at most "
        f"{CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_MAX_LENGTH} characters",
    )
    settled_channel = next(
        (
            channel
            for channel in channels.values()
            if isinstance(channel, dict)
            and channel.get("address") == "contract.technical-account.settled"
        ),
        None,
    )
    contracts.check(
        CONTRACT_TECHNICAL_ACCOUNT_SETTLEMENT_REFERENCE_FIELD
        in str((settled_channel or {}).get("description") or ""),
        f"{relative}: contract.technical-account.settled must document "
        "settlementReference",
    )


def check_contract_technical_account_lines_asyncapi(
    contracts: ContractSet, document, relative: str
):
    """Require the two implemented line channels and their shared payload."""
    channels = document.get("channels") or {}
    operations = document.get("operations") or {}
    messages = (document.get("components") or {}).get("messages") or {}
    send_events = {
        operation.get("x-event-type")
        for operation in operations.values()
        if isinstance(operation, dict) and operation.get("action") == "send"
    }

    for event in CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENTS:
        channel = next(
            (
                candidate
                for candidate in channels.values()
                if isinstance(candidate, dict)
                and candidate.get("address") == event
            ),
            None,
        )
        contracts.check(
            isinstance(channel, dict),
            f"{relative}: required technical-account line event channel "
            f"'{event}' is missing",
        )
        if not isinstance(channel, dict):
            continue
        contracts.check(
            channel.get("x-status") == "implemented",
            f"{relative}: line event channel '{event}' must be implemented",
        )
        contracts.check(
            str(channel.get("x-implemented-by", "")).endswith(
                CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_IMPLEMENTED_BY
            ),
            f"{relative}: line event channel '{event}' must name "
            f"{CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_IMPLEMENTED_BY} in "
            "x-implemented-by",
        )
        contracts.check(
            event in send_events,
            f"{relative}: line event '{event}' must have a send operation",
        )
        channel_messages = channel.get("messages") or {}
        contracts.check(
            (
                channel_messages.get(CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_MESSAGE)
                or {}
            ).get("$ref")
            == f"#/components/messages/{CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_MESSAGE}",
            f"{relative}: {event} must reference "
            f"{CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_MESSAGE}",
        )

    message = messages.get(CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_MESSAGE) or {}
    payload = message.get("payload") or {}
    payload_properties = payload.get("properties") or {}
    payload_required = set(payload.get("required") or [])
    contracts.check(
        payload_required == set(CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_FIELDS),
        f"{relative}: {CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_MESSAGE} must "
        f"require exactly {list(CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_FIELDS)}",
    )
    for field in CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_FIELDS:
        contracts.check(
            field in payload_properties,
            f"{relative}: {CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_MESSAGE}."
            f"properties.{field} is required",
        )
    for field in ("contractId", "accountId", "lineId"):
        contracts.check(
            (payload_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: {CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_MESSAGE}."
            f"{field} must be a uuid",
        )
    line_type_values = (
        (payload_properties.get("lineType") or {}).get("enum") or []
    )
    contracts.check(
        line_type_values == list(CONTRACT_TECHNICAL_ACCOUNT_LINE_TYPES),
        f"{relative}: {CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_MESSAGE}.lineType "
        f"must enumerate exactly the 13 detail types "
        f"{list(CONTRACT_TECHNICAL_ACCOUNT_LINE_TYPES)}",
    )
    contracts.check(
        not (
            set(CONTRACT_TECHNICAL_ACCOUNT_LINE_RETIRED_TYPES)
            & set(line_type_values)
        ),
        f"{relative}: {CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_MESSAGE}.lineType "
        f"must not enumerate the retired type(s) "
        f"{list(CONTRACT_TECHNICAL_ACCOUNT_LINE_RETIRED_TYPES)}",
    )
    amount = payload_properties.get("amount") or {}
    contracts.check(
        amount.get("type") == "string"
        and amount.get("pattern")
        == "^-?(?:0|[1-9][0-9]{0,14})(?:\\.[0-9]{1,4})?$",
        f"{relative}: {CONTRACT_TECHNICAL_ACCOUNT_LINE_EVENT_MESSAGE}.amount "
        "must be a decimal string",
    )


# ---------------------------------------------------------------------------
# Contract period-bordereau checks
# ---------------------------------------------------------------------------


def check_contract_bordereaux(contracts: ContractSet, document, relative: str):
    """Require the period-bordereau operations, schemas, and field rules."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    for method, bordereau_path, success_status, response_schema_name, request_schema_name in (
        CONTRACT_BORDEREAU_PATHS
    ):
        path_item = paths.get(bordereau_path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {bordereau_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required period-bordereau operation is missing",
        )
        if not isinstance(operation, dict):
            continue

        parameter_refs, inline_names = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must document the shared TenantHeader parameter",
        )
        contracts.check(
            "BookHeaderAssumed" in parameter_refs,
            f"{where}: must document the shared BookHeaderAssumed parameter",
        )
        contracts.check(
            "contractId" in inline_names,
            f"{where}: must declare the contractId path parameter",
        )
        if method == "patch":
            contracts.check(
                "bordereauId" in inline_names,
                f"{where}: must declare the bordereauId path parameter",
            )

        responses = operation.get("responses") or {}
        for code in ("400", "404"):
            contracts.check(
                code in responses,
                f"{where}: must document the {code} response",
            )
        if method in ("post", "patch"):
            contracts.check(
                "409" in responses,
                f"{where}: must document the 409 response",
            )

        if method == "get":
            ok_schema = _response_schema(operation, "200")
            contracts.check(
                isinstance(ok_schema, dict)
                and ok_schema.get("type") == "array"
                and str((ok_schema.get("items") or {}).get("$ref", "")).endswith(
                    "/schemas/Bordereau"
                ),
                f"{where}: 200 must return an array of Bordereau",
            )
        else:
            request_body = operation.get("requestBody") or {}
            contracts.check(
                isinstance(request_body, dict) and request_body.get("required") is True,
                f"{where}: request body must be required",
            )
            request_schema = (
                ((request_body.get("content") or {}).get("application/json") or {})
                .get("schema")
                if isinstance(request_body, dict)
                else None
            )
            contracts.check(
                isinstance(request_schema, dict)
                and str(request_schema.get("$ref", "")).endswith(
                    f"/schemas/{request_schema_name}"
                ),
                f"{where}: request body must use the {request_schema_name} schema",
            )
            success_schema = _response_schema(operation, success_status)
            contracts.check(
                isinstance(success_schema, dict)
                and str(success_schema.get("$ref", "")).endswith(
                    f"/schemas/{response_schema_name}"
                ),
                f"{where}: {success_status} must return the {response_schema_name} schema",
            )

    bordereau = schemas.get("Bordereau") or {}
    properties = bordereau.get("properties") or {}
    required = set(bordereau.get("required") or [])
    contracts.check(
        isinstance(bordereau, dict) and bordereau.get("type") == "object",
        f"{relative}: Bordereau must be an object schema",
    )
    for field in CONTRACT_BORDEREAU_FIELDS:
        contracts.check(
            field in properties,
            f"{relative}: Bordereau.properties.{field} is required",
        )
        contracts.check(
            field in required,
            f"{relative}: Bordereau.required must list {field}",
        )
    for field in ("bordereauId", "contractId"):
        contracts.check(
            (properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: Bordereau.{field} must be a uuid",
        )
    for field in ("periodStart", "periodEnd", "receivedDate"):
        contracts.check(
            (properties.get(field) or {}).get("format") == "date",
            f"{relative}: Bordereau.{field} must be a date",
        )
    contracts.check(
        str((properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: Bordereau.currency must reference CurrencyCode",
    )
    for field in CONTRACT_BORDEREAU_MONEY_FIELDS:
        contracts.check(
            str((properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: Bordereau.{field} must reference MoneyAmount",
        )
    contracts.check(
        (properties.get("lineCount") or {}).get("type") == "integer"
        and (properties.get("lineCount") or {}).get("minimum") == 0
        and (properties.get("lineCount") or {}).get("maximum") == 10_000_000,
        f"{relative}: Bordereau.lineCount must be an integer between 0 and 10000000",
    )
    notes = properties.get("notes") or {}
    contracts.check(
        _schema_types(notes) == {"string", "null"}
        and notes.get("maxLength") == CONTRACT_BORDEREAU_NOTES_MAX_LENGTH,
        f"{relative}: Bordereau.notes must be a nullable string of at most "
        f"{CONTRACT_BORDEREAU_NOTES_MAX_LENGTH} characters",
    )
    contracts.check(
        str((properties.get("status") or {}).get("$ref", "")).endswith(
            "/schemas/BordereauStatus"
        ),
        f"{relative}: Bordereau.status must reference BordereauStatus",
    )
    account_id = properties.get("technicalAccountId") or {}
    contracts.check(
        _schema_types(account_id) == {"string", "null"}
        and account_id.get("format") == "uuid",
        f"{relative}: Bordereau.technicalAccountId must be a nullable uuid",
    )
    contracts.check(
        (properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: Bordereau.createdAt must be a date-time",
    )

    bordereau_status = schemas.get("BordereauStatus") or {}
    contracts.check(
        bordereau_status.get("type") == "string",
        f"{relative}: BordereauStatus must be a string enum",
    )
    contracts.check(
        set(bordereau_status.get("enum") or []) == set(CONTRACT_BORDEREAU_STATUSES),
        f"{relative}: BordereauStatus must enumerate "
        f"{list(CONTRACT_BORDEREAU_STATUSES)}",
    )

    create = schemas.get("CreateBordereauRequest") or {}
    create_properties = create.get("properties") or {}
    create_required = set(create.get("required") or [])
    contracts.check(
        isinstance(create, dict) and create.get("type") == "object",
        f"{relative}: CreateBordereauRequest must be an object schema",
    )
    contracts.check(
        create_required == set(CONTRACT_BORDEREAU_CREATE_FIELDS),
        f"{relative}: CreateBordereauRequest must require "
        f"{list(CONTRACT_BORDEREAU_CREATE_FIELDS)}",
    )
    for field in ("periodStart", "periodEnd", "receivedDate"):
        contracts.check(
            (create_properties.get(field) or {}).get("format") == "date",
            f"{relative}: CreateBordereauRequest.{field} must be a date",
        )
    contracts.check(
        str((create_properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: CreateBordereauRequest.currency must reference CurrencyCode",
    )
    for field in CONTRACT_BORDEREAU_MONEY_FIELDS:
        contracts.check(
            str((create_properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: CreateBordereauRequest.{field} must reference MoneyAmount",
        )
    create_line_count = create_properties.get("lineCount") or {}
    contracts.check(
        create_line_count.get("type") == "integer"
        and create_line_count.get("minimum") == 0
        and create_line_count.get("maximum") == 10_000_000,
        f"{relative}: CreateBordereauRequest.lineCount must be an integer between 0 and 10000000",
    )
    create_notes = create_properties.get("notes") or {}
    contracts.check(
        _schema_types(create_notes) == {"string", "null"}
        and create_notes.get("maxLength") == CONTRACT_BORDEREAU_NOTES_MAX_LENGTH,
        f"{relative}: CreateBordereauRequest.notes must be an optional nullable string of at most "
        f"{CONTRACT_BORDEREAU_NOTES_MAX_LENGTH} characters",
    )

    update = schemas.get("UpdateBordereauStatusRequest") or {}
    update_properties = update.get("properties") or {}
    update_required = set(update.get("required") or [])
    contracts.check(
        isinstance(update, dict) and update.get("type") == "object",
        f"{relative}: UpdateBordereauStatusRequest must be an object schema",
    )
    contracts.check(
        update_required == {"status"},
        f"{relative}: UpdateBordereauStatusRequest must require only status",
    )
    contracts.check(
        set((update_properties.get("status") or {}).get("enum") or [])
        == set(CONTRACT_BORDEREAU_REQUEST_STATUSES),
        f"{relative}: UpdateBordereauStatusRequest.status must enumerate "
        f"{list(CONTRACT_BORDEREAU_REQUEST_STATUSES)}",
    )
    update_notes = update_properties.get("notes") or {}
    contracts.check(
        _schema_types(update_notes) == {"string", "null"}
        and update_notes.get("maxLength") == CONTRACT_BORDEREAU_NOTES_MAX_LENGTH,
        f"{relative}: UpdateBordereauStatusRequest.notes must be an optional nullable string of at most "
        f"{CONTRACT_BORDEREAU_NOTES_MAX_LENGTH} characters",
    )


# ---------------------------------------------------------------------------
# Contract cash-call checks
# ---------------------------------------------------------------------------


def check_contract_cash_calls(contracts: ContractSet, document, relative: str):
    """Require the cash-call operations, schemas, and field rules."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    for method, cash_call_path, success_status, response_schema_name, request_schema_name in (
        CONTRACT_CASH_CALL_PATHS
    ):
        path_item = paths.get(cash_call_path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {cash_call_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required cash-call operation is missing",
        )
        if not isinstance(operation, dict):
            continue

        parameter_refs, inline_names = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must document the shared TenantHeader parameter",
        )
        contracts.check(
            "BookHeaderAssumed" in parameter_refs,
            f"{where}: must document the shared BookHeaderAssumed parameter",
        )
        contracts.check(
            "contractId" in inline_names,
            f"{where}: must declare the contractId path parameter",
        )
        if method == "patch":
            contracts.check(
                "cashCallId" in inline_names,
                f"{where}: must declare the cashCallId path parameter",
            )

        responses = operation.get("responses") or {}
        for code in ("400", "404"):
            contracts.check(
                code in responses,
                f"{where}: must document the {code} response",
            )
        if method in ("post", "patch"):
            contracts.check(
                "409" in responses,
                f"{where}: must document the 409 response",
            )
        if method == "patch":
            description = str(operation.get("description") or "")
            contracts.check(
                CONTRACT_CASH_CALL_STATUS_REFERENCE_FIELD in description
                and CONTRACT_CASH_CALL_INVALID_REFERENCE in description,
                f"{where}: must document the settlement reference and "
                f"{CONTRACT_CASH_CALL_INVALID_REFERENCE}",
            )
            bad_request = responses.get("400") or {}
            bad_request_description = (
                bad_request.get("description")
                if isinstance(bad_request, dict)
                else ""
            ) or ""
            contracts.check(
                CONTRACT_CASH_CALL_INVALID_REFERENCE
                in str(bad_request_description),
                f"{where}: 400 must document "
                f"{CONTRACT_CASH_CALL_INVALID_REFERENCE}",
            )

        if method == "get":
            ok_schema = _response_schema(operation, "200")
            contracts.check(
                isinstance(ok_schema, dict)
                and ok_schema.get("type") == "array"
                and str((ok_schema.get("items") or {}).get("$ref", "")).endswith(
                    "/schemas/CashCall"
                ),
                f"{where}: 200 must return an array of CashCall",
            )
        else:
            request_body = operation.get("requestBody") or {}
            contracts.check(
                isinstance(request_body, dict) and request_body.get("required") is True,
                f"{where}: request body must be required",
            )
            request_schema = (
                ((request_body.get("content") or {}).get("application/json") or {})
                .get("schema")
                if isinstance(request_body, dict)
                else None
            )
            contracts.check(
                isinstance(request_schema, dict)
                and str(request_schema.get("$ref", "")).endswith(
                    f"/schemas/{request_schema_name}"
                ),
                f"{where}: request body must use the {request_schema_name} schema",
            )
            success_schema = _response_schema(operation, success_status)
            contracts.check(
                isinstance(success_schema, dict)
                and str(success_schema.get("$ref", "")).endswith(
                    f"/schemas/{response_schema_name}"
                ),
                f"{where}: {success_status} must return the {response_schema_name} schema",
            )

    cash_call = schemas.get("CashCall") or {}
    properties = cash_call.get("properties") or {}
    required = set(cash_call.get("required") or [])
    contracts.check(
        isinstance(cash_call, dict) and cash_call.get("type") == "object",
        f"{relative}: CashCall must be an object schema",
    )
    for field in CONTRACT_CASH_CALL_FIELDS:
        contracts.check(
            field in properties,
            f"{relative}: CashCall.properties.{field} is required",
        )
        contracts.check(
            field in required,
            f"{relative}: CashCall.required must list {field}",
        )
    for field in ("cashCallId", "contractId"):
        contracts.check(
            (properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: CashCall.{field} must be a uuid",
        )
    for field in ("periodStart", "periodEnd", "dueDate"):
        contracts.check(
            (properties.get(field) or {}).get("format") == "date",
            f"{relative}: CashCall.{field} must be a date",
        )
    contracts.check(
        str((properties.get("amount") or {}).get("$ref", "")).endswith(
            "/schemas/MoneyAmount"
        ),
        f"{relative}: CashCall.amount must reference MoneyAmount",
    )
    contracts.check(
        str((properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: CashCall.currency must reference CurrencyCode",
    )
    contracts.check(
        str((properties.get("status") or {}).get("$ref", "")).endswith(
            "/schemas/CashCallStatus"
        ),
        f"{relative}: CashCall.status must reference CashCallStatus",
    )
    notes = properties.get("notes") or {}
    contracts.check(
        _schema_types(notes) == {"string", "null"}
        and notes.get("maxLength") == CONTRACT_CASH_CALL_NOTES_MAX_LENGTH,
        f"{relative}: CashCall.notes must be a nullable string of at most "
        f"{CONTRACT_CASH_CALL_NOTES_MAX_LENGTH} characters",
    )
    settlement_reference = properties.get(
        CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_FIELD
    ) or {}
    contracts.check(
        _schema_types(settlement_reference) == {"string", "null"}
        and settlement_reference.get("maxLength")
        == CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_MAX_LENGTH,
        f"{relative}: CashCall.settlementReference must be a nullable string of "
        f"at most {CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_MAX_LENGTH} "
        "characters",
    )
    contracts.check(
        (properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: CashCall.createdAt must be a date-time",
    )

    cash_call_status = schemas.get("CashCallStatus") or {}
    contracts.check(
        cash_call_status.get("type") == "string",
        f"{relative}: CashCallStatus must be a string enum",
    )
    contracts.check(
        set(cash_call_status.get("enum") or []) == set(CONTRACT_CASH_CALL_STATUSES),
        f"{relative}: CashCallStatus must enumerate "
        f"{list(CONTRACT_CASH_CALL_STATUSES)}",
    )

    create = schemas.get("CreateCashCallRequest") or {}
    create_properties = create.get("properties") or {}
    create_required = set(create.get("required") or [])
    contracts.check(
        isinstance(create, dict) and create.get("type") == "object",
        f"{relative}: CreateCashCallRequest must be an object schema",
    )
    contracts.check(
        create_required == set(CONTRACT_CASH_CALL_CREATE_FIELDS),
        f"{relative}: CreateCashCallRequest must require "
        f"{list(CONTRACT_CASH_CALL_CREATE_FIELDS)}",
    )
    for field in ("periodStart", "periodEnd", "dueDate"):
        contracts.check(
            (create_properties.get(field) or {}).get("format") == "date",
            f"{relative}: CreateCashCallRequest.{field} must be a date",
        )
    contracts.check(
        str((create_properties.get("amount") or {}).get("$ref", "")).endswith(
            "/schemas/MoneyAmount"
        ),
        f"{relative}: CreateCashCallRequest.amount must reference MoneyAmount",
    )
    contracts.check(
        str((create_properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: CreateCashCallRequest.currency must reference CurrencyCode",
    )
    create_notes = create_properties.get("notes") or {}
    contracts.check(
        _schema_types(create_notes) == {"string", "null"}
        and create_notes.get("maxLength") == CONTRACT_CASH_CALL_NOTES_MAX_LENGTH,
        f"{relative}: CreateCashCallRequest.notes must be an optional nullable string "
        f"of at most {CONTRACT_CASH_CALL_NOTES_MAX_LENGTH} characters",
    )

    update = schemas.get("UpdateCashCallStatusRequest") or {}
    update_properties = update.get("properties") or {}
    update_required = set(update.get("required") or [])
    contracts.check(
        isinstance(update, dict) and update.get("type") == "object",
        f"{relative}: UpdateCashCallStatusRequest must be an object schema",
    )
    contracts.check(
        update_required == {"status"},
        f"{relative}: UpdateCashCallStatusRequest must require only status",
    )
    contracts.check(
        set((update_properties.get("status") or {}).get("enum") or [])
        == set(CONTRACT_CASH_CALL_REQUEST_STATUSES),
        f"{relative}: UpdateCashCallStatusRequest.status must enumerate "
        f"{list(CONTRACT_CASH_CALL_REQUEST_STATUSES)}",
    )
    status_reference = update_properties.get(
        CONTRACT_CASH_CALL_STATUS_REFERENCE_FIELD
    ) or {}
    contracts.check(
        CONTRACT_CASH_CALL_STATUS_REFERENCE_FIELD in update_properties
        and CONTRACT_CASH_CALL_STATUS_REFERENCE_FIELD not in update_required,
        f"{relative}: UpdateCashCallStatusRequest.reference must be optional",
    )
    contracts.check(
        _schema_types(status_reference) == {"string", "null"}
        and status_reference.get("maxLength")
        == CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_MAX_LENGTH,
        f"{relative}: UpdateCashCallStatusRequest.reference must be a nullable "
        f"string of at most {CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_MAX_LENGTH} "
        "characters",
    )
    settled_condition = next(
        (
            entry
            for entry in update.get("allOf") or []
            if isinstance(entry, dict)
            and ((entry.get("if") or {}).get("properties") or {})
            .get("status", {})
            .get("const")
            == "SETTLED"
        ),
        None,
    )
    contracts.check(
        isinstance(settled_condition, dict),
        f"{relative}: UpdateCashCallStatusRequest must conditionally require "
        "reference for SETTLED",
    )
    settled_then = (settled_condition or {}).get("then") or {}
    contracts.check(
        set(settled_then.get("required") or [])
        == {CONTRACT_CASH_CALL_STATUS_REFERENCE_FIELD},
        f"{relative}: UpdateCashCallStatusRequest must require reference when "
        "status is SETTLED",
    )
    settled_reference = (
        (settled_then.get("properties") or {}).get(
            CONTRACT_CASH_CALL_STATUS_REFERENCE_FIELD
        )
        or {}
    )
    contracts.check(
        settled_reference.get("type") == "string"
        and settled_reference.get("minLength") == 1
        and settled_reference.get("maxLength")
        == CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_MAX_LENGTH
        and "\\S" in str(settled_reference.get("pattern") or ""),
        f"{relative}: a SETTLED reference must be a non-blank string of at most "
        f"{CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_MAX_LENGTH} characters",
    )


# ---------------------------------------------------------------------------
# Contract security/collateral checks
# ---------------------------------------------------------------------------


def check_contract_security(contracts: ContractSet, document, relative: str):
    """Require the public security operations, projection, and command rules."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    for method, security_path, success_status, response_schema_name, request_schema_name in (
        CONTRACT_SECURITY_PATHS
    ):
        path_item = paths.get(security_path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {security_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required security operation is missing",
        )
        if not isinstance(operation, dict):
            continue

        parameter_refs, inline_names = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must document the shared TenantHeader parameter",
        )
        contracts.check(
            "BookHeaderAssumed" in parameter_refs,
            f"{where}: must document the shared BookHeaderAssumed parameter",
        )
        contracts.check(
            "contractId" in inline_names,
            f"{where}: must declare the contractId path parameter",
        )

        responses = operation.get("responses") or {}
        for code in ("400", "404"):
            contracts.check(
                code in responses,
                f"{where}: must document the {code} response",
            )

        if method == "get":
            ok_schema = _response_schema(operation, "200")
            contracts.check(
                isinstance(ok_schema, dict)
                and ok_schema.get("type") == "array"
                and str((ok_schema.get("items") or {}).get("$ref", "")).endswith(
                    f"/schemas/{response_schema_name}"
                ),
                f"{where}: 200 must return an array of {response_schema_name}",
            )
        else:
            contracts.check(
                "409" in responses,
                f"{where}: must document the 409 response",
            )
            request_body = operation.get("requestBody") or {}
            contracts.check(
                isinstance(request_body, dict) and request_body.get("required") is True,
                f"{where}: request body must be required",
            )
            request_schema = (
                ((request_body.get("content") or {}).get("application/json") or {})
                .get("schema")
                if isinstance(request_body, dict)
                else None
            )
            contracts.check(
                isinstance(request_schema, dict)
                and str(request_schema.get("$ref", "")).endswith(
                    f"/schemas/{request_schema_name}"
                ),
                f"{where}: request body must use the {request_schema_name} schema",
            )
            success_schema = _response_schema(operation, success_status)
            contracts.check(
                isinstance(success_schema, dict)
                and str(success_schema.get("$ref", "")).endswith(
                    f"/schemas/{response_schema_name}"
                ),
                f"{where}: {success_status} must return the {response_schema_name} schema",
            )
            description = operation.get("description") or ""
            for code in CONTRACT_SECURITY_CONFLICT_CODES:
                contracts.check(
                    code in description,
                    f"{where}: description must document 409 {code}",
                )

    record = schemas.get("SecurityRecord") or {}
    properties = record.get("properties") or {}
    required = set(record.get("required") or [])
    contracts.check(
        isinstance(record, dict) and record.get("type") == "object",
        f"{relative}: SecurityRecord must be an object schema",
    )
    contracts.check(
        required == set(CONTRACT_SECURITY_FIELDS),
        f"{relative}: SecurityRecord must require exactly "
        f"{list(CONTRACT_SECURITY_FIELDS)}",
    )
    for field in CONTRACT_SECURITY_FIELDS:
        contracts.check(
            field in properties,
            f"{relative}: SecurityRecord.properties.{field} is required",
        )
    contracts.check(
        (properties.get("id") or {}).get("format") == "uuid",
        f"{relative}: SecurityRecord.id must be a uuid",
    )
    contracts.check(
        str((properties.get("securityType") or {}).get("$ref", "")).endswith(
            "/schemas/SecurityType"
        ),
        f"{relative}: SecurityRecord.securityType must reference SecurityType",
    )
    for field in ("requiredAmount", "heldAmount"):
        contracts.check(
            str((properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: SecurityRecord.{field} must reference MoneyAmount",
        )
    contracts.check(
        str((properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: SecurityRecord.currency must reference CurrencyCode",
    )
    contracts.check(
        _schema_types(properties.get("providerPartyId")) == {"string", "null"}
        and (properties.get("providerPartyId") or {}).get("format") == "uuid",
        f"{relative}: SecurityRecord.providerPartyId must be a nullable uuid",
    )
    contracts.check(
        _schema_types(properties.get("expiryDate")) == {"string", "null"}
        and (properties.get("expiryDate") or {}).get("format") == "date",
        f"{relative}: SecurityRecord.expiryDate must be a nullable date",
    )
    approval_ref = properties.get("approvalRef") or {}
    contracts.check(
        _schema_types(approval_ref) == {"string", "null"}
        and approval_ref.get("maxLength") == 64,
        f"{relative}: SecurityRecord.approvalRef must be a nullable string of at most 64 characters",
    )
    contracts.check(
        str((properties.get("status") or {}).get("$ref", "")).endswith(
            "/schemas/SecurityStatus"
        ),
        f"{relative}: SecurityRecord.status must reference SecurityStatus",
    )
    contracts.check(
        (properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: SecurityRecord.createdAt must be a date-time",
    )

    security_type = schemas.get("SecurityType") or {}
    contracts.check(
        security_type.get("type") == "string",
        f"{relative}: SecurityType must be a string enum",
    )
    contracts.check(
        set(security_type.get("enum") or []) == set(CONTRACT_SECURITY_TYPES),
        f"{relative}: SecurityType must enumerate {list(CONTRACT_SECURITY_TYPES)}",
    )

    status = schemas.get("SecurityStatus") or {}
    contracts.check(
        status.get("type") == "string",
        f"{relative}: SecurityStatus must be a string enum",
    )
    contracts.check(
        set(status.get("enum") or []) == set(CONTRACT_SECURITY_STATUSES),
        f"{relative}: SecurityStatus must enumerate "
        f"{list(CONTRACT_SECURITY_STATUSES)} including ACTIVE and OUTSTANDING",
    )

    create = schemas.get("CreateContractSecurityRequest") or {}
    create_properties = create.get("properties") or {}
    create_required = set(create.get("required") or [])
    contracts.check(
        isinstance(create, dict) and create.get("type") == "object",
        f"{relative}: CreateContractSecurityRequest must be an object schema",
    )
    contracts.check(
        create_required == set(CONTRACT_SECURITY_CREATE_REQUIRED),
        f"{relative}: CreateContractSecurityRequest must require "
        f"{list(CONTRACT_SECURITY_CREATE_REQUIRED)}",
    )
    for field in CONTRACT_SECURITY_CREATE_OPTIONAL:
        contracts.check(
            field in create_properties,
            f"{relative}: CreateContractSecurityRequest.properties.{field} is required",
        )
        contracts.check(
            field not in create_required,
            f"{relative}: CreateContractSecurityRequest.{field} must stay optional",
        )
    contracts.check(
        "status" not in create_properties,
        f"{relative}: CreateContractSecurityRequest must not accept a caller status",
    )
    contracts.check(
        str((create_properties.get("securityType") or {}).get("$ref", "")).endswith(
            "/schemas/SecurityType"
        ),
        f"{relative}: CreateContractSecurityRequest.securityType must reference SecurityType",
    )
    for field in ("requiredAmount", "heldAmount"):
        contracts.check(
            str((create_properties.get(field) or {}).get("$ref", "")).endswith(
                "/schemas/MoneyAmount"
            ),
            f"{relative}: CreateContractSecurityRequest.{field} must reference MoneyAmount",
        )
    contracts.check(
        str((create_properties.get("currency") or {}).get("$ref", "")).endswith(
            "/schemas/CurrencyCode"
        ),
        f"{relative}: CreateContractSecurityRequest.currency must reference CurrencyCode",
    )
    contracts.check(
        _schema_types(create_properties.get("providerPartyId")) == {"string", "null"}
        and (create_properties.get("providerPartyId") or {}).get("format") == "uuid",
        f"{relative}: CreateContractSecurityRequest.providerPartyId must be a nullable uuid",
    )
    contracts.check(
        _schema_types(create_properties.get("expiryDate")) == {"string", "null"}
        and (create_properties.get("expiryDate") or {}).get("format") == "date",
        f"{relative}: CreateContractSecurityRequest.expiryDate must be a nullable date",
    )
    create_approval = create_properties.get("approvalRef") or {}
    contracts.check(
        _schema_types(create_approval) == {"string", "null"}
        and create_approval.get("maxLength") == 64,
        f"{relative}: CreateContractSecurityRequest.approvalRef must be a nullable "
        "string of at most 64 characters",
    )
    contracts.check(
        _schema_types(create_properties.get("approvedAt")) == {"string", "null"}
        and (create_properties.get("approvedAt") or {}).get("format") == "date-time",
        f"{relative}: CreateContractSecurityRequest.approvedAt must be a nullable date-time",
    )


def check_contract_security_status(contracts: ContractSet, document, relative: str):
    """Require the security status action, its request schema, and its rules."""
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}
    path_item = paths.get(CONTRACT_SECURITY_STATUS_PATH) if isinstance(paths, dict) else None
    operation = path_item.get("patch") if isinstance(path_item, dict) else None
    where = f"{relative}: PATCH {CONTRACT_SECURITY_STATUS_PATH}"
    contracts.check(
        isinstance(operation, dict),
        f"{where}: required security status operation is missing",
    )
    if not isinstance(operation, dict):
        return

    parameter_refs, inline_names = _parameter_names(operation)
    contracts.check(
        "TenantHeader" in parameter_refs,
        f"{where}: must document the shared TenantHeader parameter",
    )
    contracts.check(
        "BookHeaderAssumed" in parameter_refs,
        f"{where}: must document the shared BookHeaderAssumed parameter",
    )
    contracts.check(
        "contractId" in inline_names,
        f"{where}: must declare the contractId path parameter",
    )
    contracts.check(
        "securityId" in inline_names,
        f"{where}: must declare the securityId path parameter",
    )

    responses = operation.get("responses") or {}
    for code in ("200", "400", "404", "409"):
        contracts.check(code in responses, f"{where}: must document the {code} response")
    ok_schema = _response_schema(operation, "200")
    contracts.check(
        isinstance(ok_schema, dict)
        and str(ok_schema.get("$ref", "")).endswith("/schemas/SecurityRecord"),
        f"{where}: 200 must return the SecurityRecord schema",
    )

    request_body = operation.get("requestBody") or {}
    contracts.check(
        isinstance(request_body, dict) and request_body.get("required") is True,
        f"{where}: request body must be required",
    )
    request_schema = (
        ((request_body.get("content") or {}).get("application/json") or {}).get("schema")
        if isinstance(request_body, dict)
        else None
    )
    contracts.check(
        isinstance(request_schema, dict)
        and str(request_schema.get("$ref", "")).endswith(
            f"/schemas/{CONTRACT_SECURITY_STATUS_REQUEST}"
        ),
        f"{where}: request body must use the {CONTRACT_SECURITY_STATUS_REQUEST} schema",
    )

    description = operation.get("description") or ""
    for status in (
        "ACTIVE",
        "OUTSTANDING",
        "PARTIAL",
        "REQUIRED",
        "RELEASED",
        "EXPIRED",
        "BREACH",
    ):
        contracts.check(
            status in description,
            f"{where}: description must document the {status} transition rule",
        )
    for code in CONTRACT_SECURITY_STATUS_CODES:
        contracts.check(
            code in description,
            f"{where}: description must document the {code} error code",
        )
    contracts.check(
        "RELEASED` is terminal" in description,
        f"{where}: description must state that RELEASED is terminal",
    )
    contracts.check(
        "ASSUMED" in description,
        f"{where}: description must document the ASSUMED book",
    )

    request = schemas.get(CONTRACT_SECURITY_STATUS_REQUEST) or {}
    request_properties = request.get("properties") or {}
    contracts.check(
        isinstance(request, dict) and request.get("type") == "object",
        f"{relative}: {CONTRACT_SECURITY_STATUS_REQUEST} must be an object schema",
    )
    contracts.check(
        set(request.get("required") or []) == {"status"},
        f"{relative}: {CONTRACT_SECURITY_STATUS_REQUEST} must require only status",
    )
    status = request_properties.get("status") or {}
    contracts.check(
        (status.get("type"), tuple(status.get("enum") or []))
        == ("string", CONTRACT_SECURITY_STATUS_REQUEST_STATUSES),
        f"{relative}: {CONTRACT_SECURITY_STATUS_REQUEST}.status must enumerate "
        f"{list(CONTRACT_SECURITY_STATUS_REQUEST_STATUSES)}",
    )


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def _schema_types(schema) -> set:
    """Return the declared JSON types of a schema, flattening a type list."""
    if not isinstance(schema, dict):
        return set()
    declared = schema.get("type")
    if isinstance(declared, str):
        return {declared}
    if isinstance(declared, list):
        return {value for value in declared if isinstance(value, str)}
    return set()


# ---------------------------------------------------------------------------
# Direct Claims policy-year allocation checks
# ---------------------------------------------------------------------------


def check_direct_claim_allocations(contracts: ContractSet, document, relative: str):
    schemas = (document.get("components") or {}).get("schemas") or {}

    allocation = schemas.get("Allocation") or {}
    allocation_properties = allocation.get("properties") or {}
    allocation_required = allocation.get("required") or []
    contracts.check(
        isinstance(allocation, dict) and allocation.get("type") == "object",
        f"{relative}: Allocation must be an object schema",
    )
    for field in ALLOCATION_PROJECTION_FIELDS:
        contracts.check(
            isinstance(allocation_properties.get(field), dict),
            f"{relative}: Allocation.{field} is required",
        )
        contracts.check(
            field in allocation_required,
            f"{relative}: Allocation.required must list {field}",
        )
    for field in ("allocationId", "claimId", "policyId"):
        contracts.check(
            (allocation_properties.get(field) or {}).get("format") == "uuid",
            f"{relative}: Allocation.{field} must be a uuid",
        )
    policy_year = allocation_properties.get("policyYear") or {}
    contracts.check(
        (
            policy_year.get("type"),
            policy_year.get("minimum"),
            policy_year.get("maximum"),
        )
        == ("integer", ALLOCATION_MIN_POLICY_YEAR, ALLOCATION_MAX_POLICY_YEAR),
        f"{relative}: Allocation.policyYear must be an integer in "
        f"{ALLOCATION_MIN_POLICY_YEAR}-{ALLOCATION_MAX_POLICY_YEAR}",
    )
    layer = allocation_properties.get("layer") or {}
    contracts.check(
        (layer.get("type"), layer.get("maxLength"))
        == ("string", ALLOCATION_MAX_LAYER),
        f"{relative}: Allocation.layer must be a string of at most "
        f"{ALLOCATION_MAX_LAYER} characters",
    )
    contracts.check(
        str((allocation_properties.get("allocationPct") or {}).get("$ref", "")).endswith(
            "/schemas/Percent"
        ),
        f"{relative}: Allocation.allocationPct must use the shared Percent schema",
    )
    contracts.check(
        str((allocation_properties.get("allocatedAmount") or {}).get("$ref", "")).endswith(
            "/schemas/MoneyAmount"
        ),
        f"{relative}: Allocation.allocatedAmount must use the shared MoneyAmount schema",
    )
    contracts.check(
        (allocation_properties.get("createdAt") or {}).get("format") == "date-time",
        f"{relative}: Allocation.createdAt must be a date-time",
    )

    for field in ALLOCATION_EROSION_PROJECTION_FIELDS:
        contracts.check(
            isinstance(allocation_properties.get(field), dict),
            f"{relative}: Allocation.{field} is required",
        )
    contracts.check(
        "erosionStatus" in allocation_required,
        f"{relative}: Allocation.required must list erosionStatus",
    )
    for field in ("limitId", "erosionMessage", "erosionPostedAt"):
        contracts.check(
            field not in allocation_required,
            f"{relative}: Allocation.{field} must stay optional because it is nullable",
        )
    allocation_limit = allocation_properties.get("limitId") or {}
    contracts.check(
        _schema_types(allocation_limit) == {"string", "null"}
        and allocation_limit.get("format") == "uuid",
        f"{relative}: Allocation.limitId must be a nullable uuid",
    )
    contracts.check(
        str((allocation_properties.get("erosionStatus") or {}).get("$ref", "")).endswith(
            "/schemas/AllocationErosionStatus"
        ),
        f"{relative}: Allocation.erosionStatus must use the AllocationErosionStatus schema",
    )
    allocation_message = allocation_properties.get("erosionMessage") or {}
    contracts.check(
        _schema_types(allocation_message) == {"string", "null"}
        and allocation_message.get("maxLength") == ALLOCATION_EROSION_MESSAGE_MAX_LENGTH,
        f"{relative}: Allocation.erosionMessage must be a nullable string of at most "
        f"{ALLOCATION_EROSION_MESSAGE_MAX_LENGTH} characters",
    )
    allocation_posted_at = allocation_properties.get("erosionPostedAt") or {}
    contracts.check(
        _schema_types(allocation_posted_at) == {"string", "null"}
        and allocation_posted_at.get("format") == "date-time",
        f"{relative}: Allocation.erosionPostedAt must be a nullable date-time",
    )

    erosion_status = schemas.get("AllocationErosionStatus") or {}
    contracts.check(
        erosion_status.get("type") == "string"
        and tuple(erosion_status.get("enum") or ()) == ALLOCATION_EROSION_STATUSES,
        f"{relative}: AllocationErosionStatus must enumerate "
        f"{list(ALLOCATION_EROSION_STATUSES)}",
    )

    summary = schemas.get("AllocationSummary") or {}
    summary_properties = summary.get("properties") or {}
    summary_required = summary.get("required") or []
    contracts.check(
        isinstance(summary, dict) and summary.get("type") == "object",
        f"{relative}: AllocationSummary must be an object schema",
    )
    for field in ("items", "totalPct", "totalAmount"):
        contracts.check(
            isinstance(summary_properties.get(field), dict),
            f"{relative}: AllocationSummary.{field} is required",
        )
        contracts.check(
            field in summary_required,
            f"{relative}: AllocationSummary.required must list {field}",
        )
    summary_items = summary_properties.get("items") or {}
    contracts.check(
        summary_items.get("type") == "array"
        and str((summary_items.get("items") or {}).get("$ref", "")).endswith(
            "/schemas/Allocation"
        ),
        f"{relative}: AllocationSummary.items must be an array of Allocation",
    )
    contracts.check(
        str((summary_properties.get("totalPct") or {}).get("$ref", "")).endswith(
            "/schemas/Percent"
        ),
        f"{relative}: AllocationSummary.totalPct must use the shared Percent schema",
    )
    contracts.check(
        str((summary_properties.get("totalAmount") or {}).get("$ref", "")).endswith(
            "/schemas/MoneyAmount"
        ),
        f"{relative}: AllocationSummary.totalAmount must use the shared MoneyAmount schema",
    )

    request = schemas.get("CreateClaimAllocationRequest") or {}
    request_properties = request.get("properties") or {}
    request_required = request.get("required") or []
    contracts.check(
        isinstance(request, dict) and request.get("type") == "object",
        f"{relative}: CreateClaimAllocationRequest must be an object schema",
    )
    for field in ALLOCATION_REQUEST_FIELDS:
        contracts.check(
            isinstance(request_properties.get(field), dict),
            f"{relative}: CreateClaimAllocationRequest.{field} is required",
        )
        contracts.check(
            field in request_required,
            f"{relative}: CreateClaimAllocationRequest.required must list {field}",
        )
    request_year = request_properties.get("policyYear") or {}
    contracts.check(
        (
            request_year.get("type"),
            request_year.get("minimum"),
            request_year.get("maximum"),
        )
        == ("integer", ALLOCATION_MIN_POLICY_YEAR, ALLOCATION_MAX_POLICY_YEAR),
        f"{relative}: CreateClaimAllocationRequest.policyYear must be an integer in "
        f"{ALLOCATION_MIN_POLICY_YEAR}-{ALLOCATION_MAX_POLICY_YEAR}",
    )
    request_layer = request_properties.get("layer") or {}
    contracts.check(
        (request_layer.get("type"), request_layer.get("maxLength"))
        == ("string", ALLOCATION_MAX_LAYER),
        f"{relative}: CreateClaimAllocationRequest.layer must be a string of at most "
        f"{ALLOCATION_MAX_LAYER} characters",
    )
    request_pct = request_properties.get("allocationPct") or {}
    contracts.check(
        (
            request_pct.get("type"),
            request_pct.get("exclusiveMinimum"),
            request_pct.get("maximum"),
        )
        == ("number", 0, 1),
        f"{relative}: CreateClaimAllocationRequest.allocationPct must be a number "
        "greater than 0 and at most 1",
    )
    contracts.check(
        str((request_properties.get("allocatedAmount") or {}).get("$ref", "")).endswith(
            "/schemas/MoneyAmount"
        ),
        f"{relative}: CreateClaimAllocationRequest.allocatedAmount must use the shared "
        "MoneyAmount schema",
    )
    request_limit = request_properties.get("limitId") or {}
    contracts.check(
        isinstance(request_limit, dict),
        f"{relative}: CreateClaimAllocationRequest.limitId is required",
    )
    contracts.check(
        _schema_types(request_limit) == {"string"}
        and request_limit.get("format") == "uuid",
        f"{relative}: CreateClaimAllocationRequest.limitId must be an optional uuid",
    )
    contracts.check(
        "limitId" not in request_required,
        f"{relative}: CreateClaimAllocationRequest.limitId must stay optional",
    )
    contracts.check(
        "AllocationErosionRequest" not in schemas,
        f"{relative}: the public erosion retry has no request body; "
        "AllocationErosionRequest must not be a public schema",
    )

    paths = document.get("paths") or {}
    for method, path, success_status, success_schema, request_schema in (
        ALLOCATION_OPENAPI_PATHS
    ):
        path_item = paths.get(path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required allocation operation is missing",
        )
        if not isinstance(operation, dict):
            continue
        parameter_refs = []
        inline_names = []
        for parameter in operation.get("parameters") or []:
            if not isinstance(parameter, dict):
                continue
            reference = parameter.get("$ref")
            if isinstance(reference, str):
                parameter_refs.append(reference.rsplit("/", 1)[-1])
            if isinstance(parameter.get("name"), str):
                inline_names.append(parameter["name"])
        for required_parameter in ("TenantHeader", "BookHeaderDirect"):
            contracts.check(
                required_parameter in parameter_refs,
                f"{where}: must document the shared {required_parameter} parameter",
            )
        contracts.check(
            "claimId" in inline_names,
            f"{where}: must declare the claimId path parameter",
        )
        if request_schema:
            request_body = operation.get("requestBody") or {}
            body_schema = (
                ((request_body.get("content") or {}).get("application/json") or {})
                .get("schema")
                if isinstance(request_body, dict)
                else None
            )
            contracts.check(
                isinstance(request_body, dict)
                and request_body.get("required") is True,
                f"{where}: requestBody must be required",
            )
            contracts.check(
                isinstance(body_schema, dict)
                and str(body_schema.get("$ref", "")).endswith(
                    f"/schemas/{request_schema}"
                ),
                f"{where}: request body must use the {request_schema} schema",
            )
        responses = operation.get("responses") or {}
        success = responses.get(success_status) if isinstance(responses, dict) else None
        success_body = (
            ((success.get("content") or {}).get("application/json") or {}).get("schema")
            if isinstance(success, dict)
            else None
        )
        contracts.check(
            isinstance(success_body, dict)
            and str(success_body.get("$ref", "")).endswith(f"/schemas/{success_schema}"),
            f"{where}: {success_status} must return the {success_schema} schema",
        )
        for code in ("400", "404"):
            contracts.check(
                isinstance(responses, dict) and code in responses,
                f"{where}: must document response {code}",
            )
        bad_request = responses.get("400") if isinstance(responses, dict) else None
        bad_request_text = (
            str(bad_request.get("description") or "")
            if isinstance(bad_request, dict)
            else ""
        )
        if request_schema:
            contracts.check(
                "POLICY_MISMATCH" in bad_request_text,
                f"{where}: 400 must document POLICY_MISMATCH",
            )
            contracts.check(
                ALLOCATION_MASS_TORT_CODE in bad_request_text,
                f"{where}: 400 must document {ALLOCATION_MASS_TORT_CODE}",
            )
            conflict = responses.get("409") if isinstance(responses, dict) else None
            conflict_text = (
                str(conflict.get("description") or "")
                if isinstance(conflict, dict)
                else ""
            )
            contracts.check(
                "ALLOCATION_EXCEEDS_100" in conflict_text,
                f"{where}: 409 must document ALLOCATION_EXCEEDS_100",
            )

    erosion_path_item = (
        paths.get(ALLOCATION_EROSION_PATH) if isinstance(paths, dict) else None
    )
    erosion_operation = (
        erosion_path_item.get("post") if isinstance(erosion_path_item, dict) else None
    )
    erosion_where = f"{relative}: POST {ALLOCATION_EROSION_PATH}"
    contracts.check(
        isinstance(erosion_operation, dict),
        f"{erosion_where}: required allocation erosion operation is missing",
    )
    if isinstance(erosion_operation, dict):
        erosion_parameter_refs = []
        erosion_inline_names = []
        for parameter in erosion_operation.get("parameters") or []:
            if not isinstance(parameter, dict):
                continue
            reference = parameter.get("$ref")
            if isinstance(reference, str):
                erosion_parameter_refs.append(reference.rsplit("/", 1)[-1])
            if isinstance(parameter.get("name"), str):
                erosion_inline_names.append(parameter["name"])
        for required_parameter in ("TenantHeader", "BookHeaderDirect"):
            contracts.check(
                required_parameter in erosion_parameter_refs,
                f"{erosion_where}: must document the shared {required_parameter} parameter",
            )
        for path_parameter in ("claimId", "allocationId"):
            contracts.check(
                path_parameter in erosion_inline_names,
                f"{erosion_where}: must declare the {path_parameter} path parameter",
            )
        contracts.check(
            "requestBody" not in erosion_operation,
            f"{erosion_where}: the orchestration retry must not declare a request body",
        )
        erosion_responses = erosion_operation.get("responses") or {}
        erosion_success = (
            erosion_responses.get("200") if isinstance(erosion_responses, dict) else None
        )
        erosion_success_body = (
            ((erosion_success.get("content") or {}).get("application/json") or {})
            .get("schema")
            if isinstance(erosion_success, dict)
            else None
        )
        contracts.check(
            isinstance(erosion_success_body, dict)
            and str(erosion_success_body.get("$ref", "")).endswith("/schemas/Allocation"),
            f"{erosion_where}: 200 must return the Allocation schema",
        )
        for code in ("400", "404", "409"):
            contracts.check(
                isinstance(erosion_responses, dict) and code in erosion_responses,
                f"{erosion_where}: must document response {code}",
            )
        erosion_bad_request = (
            erosion_responses.get("400") if isinstance(erosion_responses, dict) else None
        )
        erosion_bad_text = (
            str(erosion_bad_request.get("description") or "")
            if isinstance(erosion_bad_request, dict)
            else ""
        )
        contracts.check(
            "VALIDATION_ERROR" in erosion_bad_text,
            f"{erosion_where}: 400 must document VALIDATION_ERROR",
        )
        contracts.check(
            "limitId" in erosion_bad_text,
            f"{erosion_where}: 400 must document the missing stored limitId guard",
        )
        erosion_conflict = (
            erosion_responses.get("409") if isinstance(erosion_responses, dict) else None
        )
        erosion_conflict_text = (
            str(erosion_conflict.get("description") or "")
            if isinstance(erosion_conflict, dict)
            else ""
        )
        contracts.check(
            f"`{ALLOCATION_EROSION_CONFLICT_CODE}`" in erosion_conflict_text,
            f"{erosion_where}: 409 must document `{ALLOCATION_EROSION_CONFLICT_CODE}`",
        )

    planned = document.get("x-planned-operations") or []
    implemented_allocation_paths = {
        "/api/v1/claims/{claimId}/allocations",
        ALLOCATION_EROSION_PATH,
    }
    contracts.check(
        not any(
            isinstance(entry, dict)
            and entry.get("path") in implemented_allocation_paths
            for entry in planned
        ),
        f"{relative}: x-planned-operations must not list an implemented allocations path",
    )


# ---------------------------------------------------------------------------
# Direct Claims settlement payment-link checks
# ---------------------------------------------------------------------------


def check_direct_claim_settlement_payment(contracts: ContractSet, document, relative: str):
    """Require the settlement payment-link route, projection, and conflict code.

    The public domain route and the expert ``/internal/v1`` alias both set or
    clear the Payment link on an AUTHORIZED or EXECUTED settlement. The body is
    the required ``SettlementPaymentRequest`` whose ``paymentId`` is required
    but nullable; the response is the updated ``Settlement`` with the two
    required-but-nullable link members. A PROPOSED or REJECTED settlement is
    409 ``SETTLEMENT_NOT_LINKABLE``. The operation documents the idempotent
    repeat and the event written in the same transaction.
    """
    schemas = (document.get("components") or {}).get("schemas") or {}

    settlement = schemas.get("Settlement") or {}
    settlement_properties = settlement.get("properties") or {}
    settlement_required = settlement.get("required") or []
    contracts.check(
        isinstance(settlement, dict) and settlement.get("type") == "object",
        f"{relative}: Settlement must be an object schema",
    )
    settlement_payment_id = settlement_properties.get("paymentId") or {}
    contracts.check(
        isinstance(settlement_payment_id, dict),
        f"{relative}: Settlement.paymentId is required",
    )
    contracts.check(
        "paymentId" in settlement_required,
        f"{relative}: Settlement.required must list paymentId",
    )
    contracts.check(
        _schema_types(settlement_payment_id) == {"string", "null"}
        and settlement_payment_id.get("format") == "uuid",
        f"{relative}: Settlement.paymentId must be a nullable uuid",
    )
    settlement_linked_at = settlement_properties.get("paymentLinkedAt") or {}
    contracts.check(
        isinstance(settlement_linked_at, dict),
        f"{relative}: Settlement.paymentLinkedAt is required",
    )
    contracts.check(
        "paymentLinkedAt" in settlement_required,
        f"{relative}: Settlement.required must list paymentLinkedAt",
    )
    contracts.check(
        _schema_types(settlement_linked_at) == {"string", "null"}
        and settlement_linked_at.get("format") == "date-time",
        f"{relative}: Settlement.paymentLinkedAt must be a nullable date-time",
    )

    request = schemas.get(SETTLEMENT_PAYMENT_SCHEMA) or {}
    request_properties = request.get("properties") or {}
    request_required = request.get("required") or []
    contracts.check(
        isinstance(request, dict) and request.get("type") == "object",
        f"{relative}: {SETTLEMENT_PAYMENT_SCHEMA} must be an object schema",
    )
    request_payment_id = request_properties.get("paymentId") or {}
    contracts.check(
        isinstance(request_payment_id, dict),
        f"{relative}: {SETTLEMENT_PAYMENT_SCHEMA}.paymentId is required",
    )
    contracts.check(
        "paymentId" in request_required,
        f"{relative}: {SETTLEMENT_PAYMENT_SCHEMA}.required must list paymentId",
    )
    contracts.check(
        _schema_types(request_payment_id) == {"string", "null"}
        and request_payment_id.get("format") == "uuid",
        f"{relative}: {SETTLEMENT_PAYMENT_SCHEMA}.paymentId must be a nullable uuid",
    )

    paths = document.get("paths") or {}
    for path, operation_id in SETTLEMENT_PAYMENT_OPENAPI_PATHS:
        path_item = paths.get(path) if isinstance(paths, dict) else None
        operation = path_item.get("patch") if isinstance(path_item, dict) else None
        where = f"{relative}: PATCH {path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required settlement payment-link operation is missing",
        )
        if not isinstance(operation, dict):
            continue
        contracts.check(
            operation.get("operationId") == operation_id,
            f"{where}: operationId must be {operation_id}",
        )
        parameter_refs = []
        inline_names = []
        for parameter in operation.get("parameters") or []:
            if not isinstance(parameter, dict):
                continue
            reference = parameter.get("$ref")
            if isinstance(reference, str):
                parameter_refs.append(reference.rsplit("/", 1)[-1])
            if isinstance(parameter.get("name"), str):
                inline_names.append(parameter["name"])
        for required_parameter in ("TenantHeader", "BookHeaderDirect"):
            contracts.check(
                required_parameter in parameter_refs,
                f"{where}: must document the shared {required_parameter} parameter",
            )
        for path_parameter in ("claimId", "settlementId"):
            contracts.check(
                path_parameter in inline_names,
                f"{where}: must declare the {path_parameter} path parameter",
            )
        request_body = operation.get("requestBody") or {}
        body_schema = (
            ((request_body.get("content") or {}).get("application/json") or {})
            .get("schema")
            if isinstance(request_body, dict)
            else None
        )
        contracts.check(
            isinstance(request_body, dict) and request_body.get("required") is True,
            f"{where}: requestBody must be required",
        )
        contracts.check(
            isinstance(body_schema, dict)
            and str(body_schema.get("$ref", "")).endswith(
                f"/schemas/{SETTLEMENT_PAYMENT_SCHEMA}"
            ),
            f"{where}: request body must use the {SETTLEMENT_PAYMENT_SCHEMA} schema",
        )
        responses = operation.get("responses") or {}
        success = responses.get("200") if isinstance(responses, dict) else None
        success_schema = (
            ((success.get("content") or {}).get("application/json") or {}).get("schema")
            if isinstance(success, dict)
            else None
        )
        contracts.check(
            isinstance(success_schema, dict)
            and str(success_schema.get("$ref", "")).endswith("/schemas/Settlement"),
            f"{where}: 200 must return the Settlement schema",
        )
        for code in ("400", "404", "409"):
            contracts.check(
                isinstance(responses, dict) and code in responses,
                f"{where}: must document response {code}",
            )
        conflict = responses.get("409") if isinstance(responses, dict) else None
        conflict_text = (
            str(conflict.get("description") or "")
            if isinstance(conflict, dict)
            else ""
        )
        contracts.check(
            f"`{SETTLEMENT_PAYMENT_CONFLICT_CODE}`" in conflict_text,
            f"{where}: 409 must document `{SETTLEMENT_PAYMENT_CONFLICT_CODE}`",
        )
        contracts.check(
            "CONFLICT" in conflict_text,
            f"{where}: 409 must document the concurrent-change CONFLICT code",
        )
        description = str(operation.get("description") or "")
        for status in SETTLEMENT_PAYMENT_LINKABLE_STATUSES:
            contracts.check(
                status in description,
                f"{where}: description must document the linkable {status} status",
            )
        for status in SETTLEMENT_PAYMENT_UNLINKABLE_STATUSES:
            contracts.check(
                status in description,
                f"{where}: description must document the rejected {status} status",
            )
        contracts.check(
            "idempotent no-op" in description,
            f"{where}: description must document the idempotent repeat",
        )
        contracts.check(
            SETTLEMENT_PAYMENT_EVENT in description,
            f"{where}: description must document {SETTLEMENT_PAYMENT_EVENT}",
        )

    planned = document.get("x-planned-operations") or []
    implemented_payment_paths = {
        path for path, _ in SETTLEMENT_PAYMENT_OPENAPI_PATHS
    }
    contracts.check(
        not any(
            isinstance(entry, dict) and entry.get("path") in implemented_payment_paths
            for entry in planned
        ),
        f"{relative}: x-planned-operations must not list an implemented "
        "settlement payment-link path",
    )


def check_direct_claim_settlement_payment_asyncapi(
    contracts: ContractSet, document, relative: str
):
    """Require the implemented settlement-payment-linked channel and payload.

    The event name is new in this contract and has no SPEC 11.4.9 equivalent.
    The channel is implemented, names its emitter, and documents the five
    payload members plus the unlink that omits ``paymentId`` and ``linkedAt``.
    """
    channels = document.get("channels") or {}
    operations = document.get("operations") or {}
    channel = None
    for candidate in channels.values():
        if (
            isinstance(candidate, dict)
            and candidate.get("address") == SETTLEMENT_PAYMENT_EVENT
        ):
            channel = candidate
            break
    contracts.check(
        channel is not None,
        f"{relative}: required {SETTLEMENT_PAYMENT_EVENT} channel is missing",
    )
    if not isinstance(channel, dict):
        return
    contracts.check(
        channel.get("x-event-type") == SETTLEMENT_PAYMENT_EVENT,
        f"{relative}: {SETTLEMENT_PAYMENT_EVENT} x-event-type must equal the address",
    )
    contracts.check(
        channel.get("x-status") == "implemented",
        f"{relative}: {SETTLEMENT_PAYMENT_EVENT} must be implemented",
    )
    contracts.check(
        bool(channel.get("x-implemented-by")),
        f"{relative}: {SETTLEMENT_PAYMENT_EVENT} must name the emitting source",
    )
    description = str(channel.get("description") or "")
    for field in SETTLEMENT_PAYMENT_EVENT_FIELDS:
        contracts.check(
            f"`{field}`" in description,
            f"{relative}: {SETTLEMENT_PAYMENT_EVENT} description must document "
            f"payload member {field}",
        )
    for status in SETTLEMENT_PAYMENT_LINKABLE_STATUSES:
        contracts.check(
            status in description,
            f"{relative}: {SETTLEMENT_PAYMENT_EVENT} description must document "
            f"the linkable {status} status",
        )
    contracts.check(
        "omitted on an unlink" in description,
        f"{relative}: {SETTLEMENT_PAYMENT_EVENT} description must document that "
        "paymentId and linkedAt are omitted on an unlink",
    )
    send_operations = [
        operation
        for operation in operations.values()
        if isinstance(operation, dict)
        and operation.get("action") == "send"
        and operation.get("x-event-type") == SETTLEMENT_PAYMENT_EVENT
    ]
    contracts.check(
        bool(send_operations),
        f"{relative}: {SETTLEMENT_PAYMENT_EVENT} must have a send operation",
    )
    if not send_operations:
        return
    operation = send_operations[0]
    contracts.check(
        operation.get("x-status") == "implemented",
        f"{relative}: the {SETTLEMENT_PAYMENT_EVENT} send operation must be implemented",
    )
    channel_ref = (operation.get("channel") or {}).get("$ref")
    contracts.check(
        isinstance(channel_ref, str) and channel_ref.startswith("#/channels/"),
        f"{relative}: the {SETTLEMENT_PAYMENT_EVENT} send operation must "
        "reference the local channel",
    )


# ---------------------------------------------------------------------------
# Direct Claims claim-list filter checks
# ---------------------------------------------------------------------------


DIRECT_CLAIM_LIST_FILTER_PARAM = "claimantPartyId"


def check_direct_claim_list_filter(contracts: ContractSet, document, relative: str):
    """Require the optional claimant filter on both claim list operations.

    The public and expert lists accept ``status`` and ``claimantPartyId`` as
    independent optional filters. The public list requires the tenant header;
    the expert uses the tenantId query parameter. Both require the DIRECT book
    header and return the bare Claim array.
    """
    paths = document.get("paths") or {}
    for path, tenant_parameter in (
        ("/api/v1/claims", "TenantHeader"),
        ("/internal/v1/claims", "TenantIdQuery"),
    ):
        path_item = paths.get(path) if isinstance(paths, dict) else None
        operation = path_item.get("get") if isinstance(path_item, dict) else None
        where = f"{relative}: GET {path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required claim list operation is missing",
        )
        if not isinstance(operation, dict):
            continue
        parameter_refs, _ = _parameter_names(operation)
        contracts.check(
            tenant_parameter in parameter_refs,
            f"{where}: must document the shared {tenant_parameter} parameter",
        )
        contracts.check(
            "BookHeaderDirect" in parameter_refs,
            f"{where}: must require the shared BookHeaderDirect parameter",
        )
        contracts.check(
            "DirectClaimStatusFilter" in parameter_refs,
            f"{where}: must keep the shared DirectClaimStatusFilter parameter",
        )
        claimant = _inline_parameter(operation, DIRECT_CLAIM_LIST_FILTER_PARAM)
        contracts.check(
            isinstance(claimant, dict),
            f"{where}: must declare the optional claimantPartyId query parameter",
        )
        if isinstance(claimant, dict):
            contracts.check(
                claimant.get("in") == "query",
                f"{where}: claimantPartyId must be a query parameter",
            )
            contracts.check(
                claimant.get("required") is False,
                f"{where}: claimantPartyId must stay optional",
            )
            claimant_schema = claimant.get("schema") or {}
            contracts.check(
                (claimant_schema.get("type"), claimant_schema.get("format"))
                == ("string", "uuid"),
                f"{where}: claimantPartyId must be a UUID string",
            )
        description = str(operation.get("description") or "")
        contracts.check(
            DIRECT_CLAIM_LIST_FILTER_PARAM in description,
            f"{where}: description must document the claimantPartyId filter",
        )
        contracts.check(
            "DIRECT" in description,
            f"{where}: description must document the DIRECT book scope",
        )
        ok_schema = _response_schema(operation, "200")
        contracts.check(
            isinstance(ok_schema, dict)
            and ok_schema.get("type") == "array"
            and str((ok_schema.get("items") or {}).get("$ref", "")).endswith(
                "/schemas/Claim"
            ),
            f"{where}: 200 must be a bare array of Claim",
        )


# ---------------------------------------------------------------------------
# Notifications NotificationType checks
# ---------------------------------------------------------------------------


def check_notifications_openapi(contracts: ContractSet, document, relative: str):
    """Require the implemented DUNNING_NOTICE type on the closed enum.

    The SPEC 11.8.5 v1 list has no dunning escalation type; the expert and the
    domain accept DUNNING_NOTICE between ESCHEATMENT_DUE and NEW_DOCUMENT_UPLOAD.
    Both create commands and the projection reference the one NotificationType
    schema, so the enum must carry the member and all three references must point
    at it.
    """
    schemas = (document.get("components") or {}).get("schemas") or {}
    notification_type = schemas.get(NOTIFICATION_TYPE_SCHEMA) or {}
    enum = notification_type.get("enum")

    contracts.check(
        notification_type.get("type") == "string",
        f"{relative}: {NOTIFICATION_TYPE_SCHEMA}.type must be string",
    )
    contracts.check(
        isinstance(enum, list) and NOTIFICATION_DUNNING_TYPE in enum,
        f"{relative}: {NOTIFICATION_TYPE_SCHEMA}.enum must include "
        f"{NOTIFICATION_DUNNING_TYPE}",
    )
    if isinstance(enum, list):
        contracts.check(
            len(enum) == len({str(value) for value in enum}),
            f"{relative}: {NOTIFICATION_TYPE_SCHEMA}.enum must not repeat a value",
        )
        contracts.check(
            enum.count(NOTIFICATION_DUNNING_TYPE) == 1,
            f"{relative}: {NOTIFICATION_TYPE_SCHEMA}.enum must name "
            f"{NOTIFICATION_DUNNING_TYPE} exactly once",
        )
        index = (
            enum.index(NOTIFICATION_DUNNING_TYPE)
            if NOTIFICATION_DUNNING_TYPE in enum
            else None
        )
        contracts.check(
            index is not None
            and 0 < index < len(enum) - 1
            and enum[index - 1] == NOTIFICATION_TYPE_PREDECESSOR
            and enum[index + 1] == NOTIFICATION_TYPE_SUCCESSOR,
            f"{relative}: {NOTIFICATION_TYPE_SCHEMA}.enum must place "
            f"{NOTIFICATION_DUNNING_TYPE} between "
            f"{NOTIFICATION_TYPE_PREDECESSOR} and {NOTIFICATION_TYPE_SUCCESSOR}",
        )

    for schema_name, property_name in NOTIFICATION_TYPE_REFERENCES:
        schema = schemas.get(schema_name) or {}
        properties = schema.get("properties") or {}
        property_schema = properties.get(property_name) or {}
        where = f"{relative}: {schema_name}.{property_name}"
        contracts.check(
            property_schema.get("$ref")
            == f"#/components/schemas/{NOTIFICATION_TYPE_SCHEMA}",
            f"{where} must reference {NOTIFICATION_TYPE_SCHEMA}",
        )
        contracts.check(
            property_name in (schema.get("required") or []),
            f"{where} must stay required",
        )


def _notification_template_channel(schema) -> bool:
    """A template channel is either a NotificationChannel or null."""
    options = [option for option in (schema.get("oneOf") or []) if isinstance(option, dict)]
    return (
        any(
            option.get("$ref") == "#/components/schemas/NotificationChannel"
            for option in options
        )
        and any(option.get("type") == "null" for option in options)
    )


def check_notification_templates_openapi(contracts: ContractSet, document, relative: str):
    """Require the implemented notification-template administration surface.

    The short `/api/v1/notifications/templates` resource is the implemented
    registry: list with exact status/code filters, create DRAFT, approve, and
    retire. The lifecycle is closed (DRAFT -> ACTIVE, DRAFT|ACTIVE -> RETIRED),
    the create body never carries a status, and the three conflicts name the
    stable TEMPLATE_* codes.
    """
    paths = document.get("paths") or {}
    schemas = (document.get("components") or {}).get("schemas") or {}

    template = schemas.get("NotificationTemplate") or {}
    properties = template.get("properties") or {}
    required = template.get("required") or []
    contracts.check(
        template.get("type") == "object",
        f"{relative}: NotificationTemplate must be an object schema",
    )
    contracts.check(
        set(properties) == set(NOTIFICATION_TEMPLATE_FIELDS),
        f"{relative}: NotificationTemplate must declare exactly "
        f"{list(NOTIFICATION_TEMPLATE_FIELDS)}",
    )
    for field in NOTIFICATION_TEMPLATE_FIELDS:
        contracts.check(
            field in required,
            f"{relative}: NotificationTemplate.required must list {field}",
        )
    contracts.check(
        (properties.get("id") or {}).get("format") == "uuid",
        f"{relative}: NotificationTemplate.id must be a uuid",
    )
    code_schema = properties.get("code") or {}
    contracts.check(
        (code_schema.get("type"), code_schema.get("maxLength"))
        == ("string", NOTIFICATION_TEMPLATE_CODE_MAX_LENGTH),
        f"{relative}: NotificationTemplate.code must be a string of at most "
        f"{NOTIFICATION_TEMPLATE_CODE_MAX_LENGTH} characters",
    )
    version_schema = properties.get("version") or {}
    contracts.check(
        (version_schema.get("type"), version_schema.get("minimum")) == ("integer", 1),
        f"{relative}: NotificationTemplate.version must be a positive integer",
    )
    contracts.check(
        _notification_template_channel(properties.get("channel")),
        f"{relative}: NotificationTemplate.channel must be NotificationChannel or null",
    )
    locale_schema = properties.get("locale") or {}
    contracts.check(
        (locale_schema.get("type"), locale_schema.get("maxLength"))
        == ("string", NOTIFICATION_TEMPLATE_LOCALE_MAX_LENGTH),
        f"{relative}: NotificationTemplate.locale must be a string of at most "
        f"{NOTIFICATION_TEMPLATE_LOCALE_MAX_LENGTH} characters",
    )
    body_schema = properties.get("bodyTemplate") or {}
    contracts.check(
        body_schema.get("type") == "string" and body_schema.get("minLength") == 1,
        f"{relative}: NotificationTemplate.bodyTemplate must be a non-empty string",
    )
    contracts.check(
        (properties.get("status") or {}).get("$ref")
        == "#/components/schemas/NotificationTemplateStatus",
        f"{relative}: NotificationTemplate.status must reference "
        "NotificationTemplateStatus",
    )
    approved_by = properties.get("approvedBy") or {}
    contracts.check(
        _schema_types(approved_by) == {"string", "null"}
        and approved_by.get("format") == "uuid",
        f"{relative}: NotificationTemplate.approvedBy must be a nullable uuid",
    )
    approved_at = properties.get("approvedAt") or {}
    contracts.check(
        _schema_types(approved_at) == {"string", "null"}
        and approved_at.get("format") == "date-time",
        f"{relative}: NotificationTemplate.approvedAt must be a nullable date-time",
    )
    for field in ("createdAt", "updatedAt"):
        field_schema = properties.get(field) or {}
        contracts.check(
            field_schema.get("type") == "string"
            and field_schema.get("format") == "date-time",
            f"{relative}: NotificationTemplate.{field} must be a date-time",
        )

    status_schema = schemas.get("NotificationTemplateStatus") or {}
    contracts.check(
        status_schema.get("type") == "string",
        f"{relative}: NotificationTemplateStatus.type must be string",
    )
    contracts.check(
        tuple(status_schema.get("enum") or []) == NOTIFICATION_TEMPLATE_STATUSES,
        f"{relative}: NotificationTemplateStatus.enum must be "
        f"{list(NOTIFICATION_TEMPLATE_STATUSES)}",
    )

    create = schemas.get("CreateNotificationTemplateRequest") or {}
    create_properties = create.get("properties") or {}
    create_required = create.get("required") or []
    contracts.check(
        create.get("type") == "object",
        f"{relative}: CreateNotificationTemplateRequest must be an object schema",
    )
    contracts.check(
        set(create_properties) == set(NOTIFICATION_TEMPLATE_CREATE_PROPERTIES),
        f"{relative}: CreateNotificationTemplateRequest must declare exactly "
        f"{list(NOTIFICATION_TEMPLATE_CREATE_PROPERTIES)}",
    )
    for field in NOTIFICATION_TEMPLATE_CREATE_REQUIRED:
        contracts.check(
            field in create_required,
            f"{relative}: CreateNotificationTemplateRequest.required must list {field}",
        )
    contracts.check(
        "status" not in create_properties,
        f"{relative}: CreateNotificationTemplateRequest must not accept a status",
    )
    create_code = create_properties.get("templateCode") or {}
    contracts.check(
        (create_code.get("type"), create_code.get("minLength"), create_code.get("maxLength"))
        == ("string", 1, NOTIFICATION_TEMPLATE_CODE_MAX_LENGTH),
        f"{relative}: CreateNotificationTemplateRequest.templateCode must be a "
        f"1-{NOTIFICATION_TEMPLATE_CODE_MAX_LENGTH} character string",
    )
    create_version = create_properties.get("templateVersion") or {}
    contracts.check(
        (create_version.get("type"), create_version.get("minimum")) == ("integer", 1),
        f"{relative}: CreateNotificationTemplateRequest.templateVersion must be a "
        "positive integer",
    )
    contracts.check(
        _notification_template_channel(create_properties.get("channel")),
        f"{relative}: CreateNotificationTemplateRequest.channel must be "
        "NotificationChannel or null",
    )
    create_locale = create_properties.get("locale") or {}
    contracts.check(
        (
            create_locale.get("type"),
            create_locale.get("minLength"),
            create_locale.get("maxLength"),
        )
        == ("string", 1, NOTIFICATION_TEMPLATE_LOCALE_MAX_LENGTH),
        f"{relative}: CreateNotificationTemplateRequest.locale must be a "
        f"1-{NOTIFICATION_TEMPLATE_LOCALE_MAX_LENGTH} character string",
    )
    create_body = create_properties.get("bodyTemplate") or {}
    contracts.check(
        create_body.get("type") == "string" and create_body.get("minLength") == 1,
        f"{relative}: CreateNotificationTemplateRequest.bodyTemplate must be a "
        "non-empty string",
    )

    approve = schemas.get("ApproveNotificationTemplateRequest") or {}
    approve_properties = approve.get("properties") or {}
    contracts.check(
        approve.get("type") == "object" and "approvedBy" in (approve.get("required") or []),
        f"{relative}: ApproveNotificationTemplateRequest must require approvedBy",
    )
    contracts.check(
        (approve_properties.get("approvedBy") or {}).get("format") == "uuid",
        f"{relative}: ApproveNotificationTemplateRequest.approvedBy must be a uuid",
    )

    planned = {
        (str(entry.get("method") or "").lower(), entry.get("path"))
        for entry in document.get("x-planned-operations") or []
        if isinstance(entry, dict)
    }
    for method, template_path, success, response_schema, request_schema, errors in (
        NOTIFICATION_TEMPLATE_OPENAPI_PATHS
    ):
        path_item = paths.get(template_path) if isinstance(paths, dict) else None
        operation = path_item.get(method) if isinstance(path_item, dict) else None
        where = f"{relative}: {method.upper()} {template_path}"
        contracts.check(
            isinstance(operation, dict),
            f"{where}: required template operation is missing",
        )
        if not isinstance(operation, dict):
            continue
        contracts.check(
            (method, template_path) not in planned,
            f"{where}: implemented template operation must not be listed in "
            "x-planned-operations",
        )
        parameter_refs, inline_names = _parameter_names(operation)
        contracts.check(
            "TenantHeader" in parameter_refs,
            f"{where}: must require the shared TenantHeader",
        )
        if "{id}" in template_path:
            contracts.check(
                "id" in inline_names,
                f"{where}: must declare the id path parameter",
            )
        response_schema_object = _response_schema(operation, success)
        if method != "get":
            contracts.check(
                isinstance(response_schema_object, dict)
                and str(response_schema_object.get("$ref", "")).endswith(
                    f"/schemas/{response_schema}"
                ),
                f"{where}: {success} must return the {response_schema} schema",
            )
        responses = operation.get("responses") or {}
        for code in errors:
            contracts.check(code in responses, f"{where}: must document the {code} response")
        if method == "get":
            array_schema = _response_schema(operation, success) or {}
            items = array_schema.get("items") or {}
            contracts.check(
                array_schema.get("type") == "array"
                and str(items.get("$ref", "")).endswith("/schemas/NotificationTemplate"),
                f"{where}: 200 must be an array of NotificationTemplate",
            )
            status_parameter = _inline_parameter(operation, "status") or {}
            contracts.check(
                (status_parameter.get("schema") or {}).get("$ref")
                == "#/components/schemas/NotificationTemplateStatus",
                f"{where}: status must reference NotificationTemplateStatus",
            )
            code_parameter = _inline_parameter(operation, "code") or {}
            contracts.check(
                (code_parameter.get("schema") or {}).get("maxLength")
                == NOTIFICATION_TEMPLATE_CODE_MAX_LENGTH,
                f"{where}: code must be capped at "
                f"{NOTIFICATION_TEMPLATE_CODE_MAX_LENGTH} characters",
            )
        if request_schema:
            request_body = operation.get("requestBody") or {}
            request_object = (
                ((request_body.get("content") or {}).get("application/json") or {})
                .get("schema")
                if isinstance(request_body, dict)
                else None
            )
            contracts.check(
                isinstance(request_object, dict)
                and str(request_object.get("$ref", "")).endswith(
                    f"/schemas/{request_schema}"
                ),
                f"{where}: request body must use the {request_schema} schema",
            )
        else:
            contracts.check(
                "requestBody" not in operation,
                f"{where}: retire must not declare a request body",
            )
        if "409" in errors:
            conflict = responses.get("409") or {}
            conflict_text = str(conflict.get("description") or "")
            problem_schema = (((conflict.get("content") or {}).get(
                "application/problem+json"
            ) or {}).get("schema")) if isinstance(conflict, dict) else None
            contracts.check(
                isinstance(problem_schema, dict)
                and str(problem_schema.get("$ref", "")).endswith("/schemas/Problem"),
                f"{where}: 409 must document the shared Problem schema",
            )
            if method == "post" and request_schema is None:
                expected_codes = (NOTIFICATION_TEMPLATE_CONFLICT_CODES[2],)
                expected_event = NOTIFICATION_TEMPLATE_EVENTS[2]
            elif request_schema == "ApproveNotificationTemplateRequest":
                expected_codes = NOTIFICATION_TEMPLATE_CONFLICT_CODES[1:]
                expected_event = NOTIFICATION_TEMPLATE_EVENTS[1]
            else:
                expected_codes = (NOTIFICATION_TEMPLATE_CONFLICT_CODES[0],)
                expected_event = NOTIFICATION_TEMPLATE_EVENTS[0]
            for conflict_code in expected_codes:
                contracts.check(
                    conflict_code in conflict_text,
                    f"{where}: 409 must document {conflict_code}",
                )
            contracts.check(
                expected_event in str(operation.get("description") or ""),
                f"{where}: description must name the emitted {expected_event} event",
            )
        if request_schema == "CreateNotificationTemplateRequest":
            contracts.check(
                "DRAFT" in str(operation.get("summary") or ""),
                f"{where}: create must document the DRAFT initial status",
            )
            contracts.check(
                "notifications.template.created"
                in str(operation.get("description") or ""),
                f"{where}: create must document notifications.template.created",
            )

    compatibility = document.get("x-compatibility") or {}
    contracts.check(
        isinstance(compatibility, dict) and compatibility.get("contractVersion") == (
            (document.get("info") or {}).get("version")
        ),
        f"{relative}: x-compatibility must name the current contract version",
    )
    implementation = document.get("x-implementation") or {}
    verified = [
        str(entry) for entry in implementation.get("verifiedAgainst") or []
    ]
    contracts.check(
        any(entry.endswith("NotificationTemplateController.java") for entry in verified),
        f"{relative}: x-implementation.verifiedAgainst must name the template "
        "controller",
    )


def check_openapi(contracts: ContractSet, verbose: bool):
    print("\nOpenAPI 3.1 documents")
    expected = {"components"} | set(VERTICAL_FILES)
    present = {path.stem for path in OPENAPI_DIR.glob("*.yaml")}
    contracts.check(
        present == expected,
        f"openapi/ must contain exactly {sorted(expected)}; found {sorted(present)}",
    )

    components = contracts.load(OPENAPI_DIR / "components.yaml")
    contracts.check(components.get("openapi") == "3.1.0", "components.yaml: openapi must be 3.1.0")
    info = components.get("info") or {}
    contracts.check(bool(info.get("title")), "components.yaml: info.title is required")
    contracts.check(bool(info.get("version")), "components.yaml: info.version is required")
    contracts.check(
        components.get("jsonSchemaDialect") == "https://json-schema.org/draft/2020-12/schema",
        "components.yaml: jsonSchemaDialect must be the JSON Schema 2020-12 dialect",
    )
    component_sections = components.get("components") or {}
    for section, names in REQUIRED_COMPONENTS.items():
        actual = component_sections.get(section) or {}
        for name in names:
            contracts.check(name in actual, f"components.yaml: missing components.{section}.{name}")

    # Shared global-search contract: every search operation references these
    # schemas, so their keys and parameter bounds are checked once here.
    search_schemas = component_sections.get("schemas") or {}
    search_response = search_schemas.get("SearchResponse") or {}
    search_properties = search_response.get("properties") or {}
    search_required = search_response.get("required") or []
    contracts.check(search_response.get("type") == "object", "components.yaml: SearchResponse.type must be object")
    for key in SEARCH_RESPONSE_KEYS:
        contracts.check(key in search_properties, f"components.yaml: SearchResponse.properties.{key} is required")
        contracts.check(key in search_required, f"components.yaml: SearchResponse.required must list {key}")
    search_items = search_properties.get("items") or {}
    contracts.check(search_items.get("type") == "array", "components.yaml: SearchResponse.items.type must be array")
    contracts.check(
        (search_items.get("items") or {}).get("$ref") == "#/components/schemas/SearchItem",
        "components.yaml: SearchResponse.items must reference SearchItem",
    )
    search_item = search_schemas.get("SearchItem") or {}
    search_item_properties = search_item.get("properties") or {}
    search_item_required = search_item.get("required") or []
    contracts.check(search_item.get("type") == "object", "components.yaml: SearchItem.type must be object")
    for key in SEARCH_ITEM_KEYS:
        contracts.check(key in search_item_properties, f"components.yaml: SearchItem.properties.{key} is required")
        contracts.check(key in search_item_required, f"components.yaml: SearchItem.required must list {key}")
    contracts.check(
        (search_item_properties.get("id") or {}).get("format") == "uuid",
        "components.yaml: SearchItem.id must be a uuid",
    )
    contracts.check(
        (search_item_properties.get("type") or {}).get("$ref") == "#/components/schemas/SearchType",
        "components.yaml: SearchItem.type must reference SearchType",
    )
    search_limit = (component_sections.get("parameters") or {}).get("SearchLimit") or {}
    search_limit_schema = search_limit.get("schema") or {}
    contracts.check(search_limit.get("name") == "limit", "components.yaml: SearchLimit.name must be limit")
    contracts.check(search_limit.get("in") == "query", "components.yaml: SearchLimit.in must be query")
    contracts.check(
        (search_limit_schema.get("type"), search_limit_schema.get("minimum"),
         search_limit_schema.get("maximum"), search_limit_schema.get("default")) == ("integer", 1, 25, 10),
        "components.yaml: SearchLimit must be an integer defaulting to 10 with minimum 1 and maximum 25",
    )
    search_query = (component_sections.get("parameters") or {}).get("SearchQuery") or {}
    contracts.check(search_query.get("name") == "q", "components.yaml: SearchQuery.name must be q")
    contracts.check(search_query.get("in") == "query", "components.yaml: SearchQuery.in must be query")
    contracts.check(
        (search_query.get("schema") or {}).get("type") == "string",
        "components.yaml: SearchQuery.schema.type must be string",
    )
    search_types = set(((search_schemas.get("SearchType") or {}).get("enum") or []))
    expected_search_types = {entry[2] for entry in SEARCH_OPENAPI_PATHS.values()}
    contracts.check(
        expected_search_types <= search_types,
        f"components.yaml: SearchType.enum is missing {sorted(expected_search_types - search_types)}",
    )

    # Claim task and note idempotency: the shared parameter, response header,
    # and 400/409 descriptions that both claim documents reference.
    claim_key = (component_sections.get("parameters") or {}).get("ClaimIdempotencyKey") or {}
    claim_key_schema = claim_key.get("schema") or {}
    contracts.check(
        claim_key.get("name") == "Idempotency-Key",
        "components.yaml: ClaimIdempotencyKey.name must be Idempotency-Key",
    )
    contracts.check(
        claim_key.get("in") == "header",
        "components.yaml: ClaimIdempotencyKey.in must be header",
    )
    contracts.check(
        claim_key.get("required") is False,
        "components.yaml: ClaimIdempotencyKey must stay optional",
    )
    contracts.check(
        (
            claim_key_schema.get("type"),
            claim_key_schema.get("minLength"),
            claim_key_schema.get("maxLength"),
        ) == ("string", 1, 64),
        "components.yaml: ClaimIdempotencyKey must be a 1-64 character string",
    )
    actor_header = (component_sections.get("parameters") or {}).get("ActorHeader") or {}
    actor_header_schema = actor_header.get("schema") or {}
    contracts.check(
        actor_header.get("name") == "X-EIA-Actor",
        "components.yaml: ActorHeader.name must be X-EIA-Actor",
    )
    contracts.check(
        actor_header.get("in") == "header",
        "components.yaml: ActorHeader.in must be header",
    )
    contracts.check(
        actor_header.get("required") is False,
        "components.yaml: ActorHeader must stay optional",
    )
    contracts.check(
        (
            actor_header_schema.get("type"),
            actor_header_schema.get("maxLength"),
        ) == ("string", ASSIGNMENT_MAX_ADJUSTER),
        "components.yaml: ActorHeader must be a string of at most 128 characters",
    )
    optional_direct_book = (
        component_sections.get("parameters") or {}
    ).get("BookHeaderDirectOptional") or {}
    optional_direct_book_schema = optional_direct_book.get("schema") or {}
    contracts.check(
        optional_direct_book.get("name") == "X-EIA-Book",
        "components.yaml: BookHeaderDirectOptional.name must be X-EIA-Book",
    )
    contracts.check(
        optional_direct_book.get("in") == "header",
        "components.yaml: BookHeaderDirectOptional.in must be header",
    )
    contracts.check(
        optional_direct_book.get("required") is False,
        "components.yaml: BookHeaderDirectOptional must stay optional",
    )
    contracts.check(
        set(optional_direct_book_schema.get("enum") or []) == {"DIRECT"},
        "components.yaml: BookHeaderDirectOptional must enumerate DIRECT",
    )
    replay_header = (component_sections.get("headers") or {}).get("IdempotentReplay") or {}
    replay_schema = replay_header.get("schema") or {}
    contracts.check(
        replay_schema.get("type") == "string"
        and set(replay_schema.get("enum") or []) == {"true", "false"},
        "components.yaml: IdempotentReplay must be a string enum of true and false",
    )
    contracts.check(
        "Idempotent-Replay" in str(replay_header.get("description") or ""),
        "components.yaml: IdempotentReplay must name the Idempotent-Replay header",
    )
    shared_bad_request = (component_sections.get("responses") or {}).get("BadRequest") or {}
    bad_request_text = str(shared_bad_request.get("description") or "")
    contracts.check(
        "INVALID_IDEMPOTENCY_KEY" in bad_request_text and "Idempotency-Key" in bad_request_text,
        "components.yaml: BadRequest must document the invalid Idempotency-Key 400",
    )
    shared_conflict = (component_sections.get("responses") or {}).get("Conflict") or {}
    conflict_text = str(shared_conflict.get("description") or "")
    for code in ("EIA-DIR-4091", "EIA-RNS-4091"):
        contracts.check(
            code in conflict_text,
            f"components.yaml: Conflict must document {code}",
        )

    operation_ids = {}
    for vertical in VERTICAL_FILES:
        path = OPENAPI_DIR / f"{vertical}.yaml"
        if not path.exists():
            contracts.check(False, f"missing openapi/{vertical}.yaml")
            continue
        document = contracts.load(path)
        relative = path.relative_to(ROOT).as_posix()
        contracts.check(document.get("openapi") == "3.1.0", f"{relative}: openapi must be 3.1.0")
        doc_info = document.get("info") or {}
        contracts.check(bool(doc_info.get("title")), f"{relative}: info.title is required")
        contracts.check(
            isinstance(doc_info.get("version"), str) and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", doc_info["version"]),
            f"{relative}: info.version must be SemVer",
        )
        contracts.check(
            document.get("jsonSchemaDialect") == "https://json-schema.org/draft/2020-12/schema",
            f"{relative}: jsonSchemaDialect must be the JSON Schema 2020-12 dialect",
        )
        contracts.check(
            (document.get("x-vertical") == vertical),
            f"{relative}: x-vertical must be '{vertical}'",
        )
        contracts.check(
            isinstance(document.get("security"), list) and bool(document.get("security")),
            f"{relative}: a document-level security requirement is required",
        )
        security_schemes = (document.get("components") or {}).get("securitySchemes") or {}
        contracts.check(
            "sessionCookie" in security_schemes,
            f"{relative}: components.securitySchemes.sessionCookie is required",
        )

        paths = document.get("paths") or {}
        contracts.check(isinstance(paths, dict) and bool(paths), f"{relative}: paths must be a non-empty mapping")
        local_operation_ids = set()
        operation_count = 0
        for path_key, path_item in paths.items():
            contracts.check(
                path_key.startswith("/api/v1/") or path_key.startswith("/internal/v1/"),
                f"{relative}: path '{path_key}' must start with /api/v1/ or /internal/v1/",
            )
            contracts.check(isinstance(path_item, dict), f"{relative}: path '{path_key}' must be a mapping")
            if not isinstance(path_item, dict):
                continue
            is_internal = path_key.startswith("/internal/v1/")
            for method, operation in path_item.items():
                if method not in HTTP_METHODS:
                    continue
                operation_count += 1
                where = f"{relative}: {method.upper()} {path_key}"
                contracts.check(isinstance(operation, dict), f"{where}: operation must be a mapping")
                if not isinstance(operation, dict):
                    continue
                operation_id = operation.get("operationId")
                contracts.check(bool(operation_id), f"{where}: operationId is required")
                if operation_id:
                    contracts.check(operation_id not in local_operation_ids, f"{where}: duplicate operationId '{operation_id}'")
                    contracts.check(
                        operation_id not in operation_ids,
                        f"{where}: operationId '{operation_id}' is already used in {operation_ids.get(operation_id)}",
                    )
                    local_operation_ids.add(operation_id)
                    operation_ids[operation_id] = relative
                contracts.check(bool(operation.get("summary")), f"{where}: summary is required")
                contracts.check(bool(operation.get("tags")), f"{where}: tags are required")
                if is_internal:
                    contracts.check(operation.get("security") == [], f"{where}: internal operations must declare security: []")
                    contracts.check(operation.get("x-internal-api") is True, f"{where}: internal operations must be marked x-internal-api: true")
                responses = operation.get("responses")
                contracts.check(isinstance(responses, dict) and bool(responses), f"{where}: responses are required")
                if isinstance(responses, dict):
                    success = [code for code in responses if str(code).startswith("2")]
                    contracts.check(bool(success), f"{where}: a 2xx response is required")
                    for code, response in responses.items():
                        if isinstance(response, dict) and "$ref" not in response:
                            contracts.check(bool(response.get("description")), f"{where}: response {code} needs a description")
                request_body = operation.get("requestBody")
                if request_body is not None:
                    contracts.check(isinstance(request_body, dict), f"{where}: requestBody must be a mapping")
                    content = (request_body or {}).get("content") or {}
                    if operation.get("x-raw-body") is True:
                        contracts.check(
                            isinstance(content, dict) and bool(content),
                            f"{where}: raw requestBody must declare a content media range",
                        )
                        for media_type, media_object in (content or {}).items():
                            schema = (
                                media_object.get("schema")
                                if isinstance(media_object, dict)
                                else None
                            )
                            contracts.check(
                                isinstance(schema, dict),
                                f"{where}: raw requestBody {media_type} schema is required",
                            )
                            contracts.check(
                                isinstance(schema, dict)
                                and schema.get("type") == "string"
                                and schema.get("format") == "binary",
                                f"{where}: raw requestBody {media_type} schema must be a binary string",
                            )
                    else:
                        contracts.check("application/json" in content, f"{where}: requestBody must declare application/json")
                        if "application/json" in content:
                            schema = (content["application/json"] or {}).get("schema")
                            contracts.check(isinstance(schema, dict), f"{where}: requestBody schema is required")

        for required_path, required_method in REQUIRED_OPENAPI_PATHS[vertical]:
            path_item = paths.get(required_path) if isinstance(paths, dict) else None
            contracts.check(
                isinstance(path_item, dict) and required_method in path_item,
                f"{relative}: required operation {required_method.upper()} {required_path} is missing",
            )
        for required_path, required_method in ROUND5_OPENAPI_PATHS.get(vertical, []):
            path_item = paths.get(required_path) if isinstance(paths, dict) else None
            contracts.check(
                isinstance(path_item, dict) and required_method in path_item,
                f"{relative}: required Round 5 operation {required_method.upper()} {required_path} is missing",
            )
        document_schemas = (document.get("components") or {}).get("schemas") or {}
        for schema_name in TASK_NOTE_REQUIRED_SCHEMAS.get(vertical, []):
            contracts.check(
                schema_name in document_schemas,
                f"{relative}: required task/note schema {schema_name} is missing",
            )
        idempotency_entry = TASK_NOTE_IDEMPOTENCY_POSTS.get(vertical)
        if idempotency_entry:
            reuse_code, idempotency_posts = idempotency_entry
            for post_path, post_method in idempotency_posts:
                path_item = paths.get(post_path) if isinstance(paths, dict) else None
                operation = path_item.get(post_method) if isinstance(path_item, dict) else None
                where = f"{relative}: {post_method.upper()} {post_path}"
                contracts.check(
                    isinstance(operation, dict),
                    f"{where}: idempotent task/note create operation is missing",
                )
                if not isinstance(operation, dict):
                    continue
                parameter_refs = [
                    str(parameter.get("$ref")).rsplit("/", 1)[-1]
                    for parameter in operation.get("parameters") or []
                    if isinstance(parameter, dict) and parameter.get("$ref")
                ]
                contracts.check(
                    "ClaimIdempotencyKey" in parameter_refs,
                    f"{where}: must document the shared ClaimIdempotencyKey header parameter",
                )
                responses = operation.get("responses") or {}
                created = responses.get("201") if isinstance(responses, dict) else None
                created_headers = created.get("headers") if isinstance(created, dict) else None
                replay = (
                    created_headers.get("Idempotent-Replay")
                    if isinstance(created_headers, dict)
                    else None
                )
                contracts.check(
                    isinstance(replay, dict)
                    and str(replay.get("$ref", "")).endswith("/headers/IdempotentReplay"),
                    f"{where}: 201 must declare the shared Idempotent-Replay header",
                )
                conflict = responses.get("409") if isinstance(responses, dict) else None
                conflict_text = (
                    str(conflict.get("description") or "")
                    if isinstance(conflict, dict)
                    else ""
                )
                contracts.check(
                    bool(conflict_text),
                    f"{where}: 409 must be documented with a description",
                )
                contracts.check(
                    reuse_code in conflict_text,
                    f"{where}: 409 must document {reuse_code}",
                )
                contracts.check(
                    "IDEMPOTENCY_KEY_REUSED" in conflict_text,
                    f"{where}: 409 must document IDEMPOTENCY_KEY_REUSED",
                )
                conflict_content = conflict.get("content") if isinstance(conflict, dict) else None
                problem_schema = (
                    ((conflict_content or {}).get("application/problem+json") or {}).get("schema")
                    if isinstance(conflict_content, dict)
                    else None
                )
                contracts.check(
                    isinstance(problem_schema, dict)
                    and str(problem_schema.get("$ref", "")).endswith("/schemas/Problem"),
                    f"{where}: 409 must document the shared Problem schema",
                )
        # Claim assignment: the public and expert operations, the command
        # schema, the nullable ownership fields, and the actor header.
        assignment_schema_name = ASSIGNMENT_REQUIRED_SCHEMAS.get(vertical)
        if assignment_schema_name:
            assignment_request = document_schemas.get("AssignClaimRequest") or {}
            assignment_properties = assignment_request.get("properties") or {}
            assignment_required = assignment_request.get("required") or []
            contracts.check(
                isinstance(assignment_request, dict) and assignment_request.get("type") == "object",
                f"{relative}: AssignClaimRequest must be an object schema",
            )
            contracts.check(
                "assignedAdjuster" in assignment_required
                and "expectedVersion" in assignment_required,
                f"{relative}: AssignClaimRequest must require assignedAdjuster and expectedVersion",
            )
            contracts.check(
                "assignedTeam" not in assignment_required,
                f"{relative}: AssignClaimRequest.assignedTeam must stay optional",
            )
            adjuster_schema = assignment_properties.get("assignedAdjuster") or {}
            contracts.check(
                (
                    adjuster_schema.get("type"),
                    adjuster_schema.get("maxLength"),
                ) == ("string", ASSIGNMENT_MAX_ADJUSTER),
                f"{relative}: AssignClaimRequest.assignedAdjuster must be a string of at most "
                f"{ASSIGNMENT_MAX_ADJUSTER} characters",
            )
            team_schema = assignment_properties.get("assignedTeam") or {}
            contracts.check(
                _schema_types(team_schema) == {"string", "null"}
                and team_schema.get("maxLength") == ASSIGNMENT_MAX_TEAM,
                f"{relative}: AssignClaimRequest.assignedTeam must be a nullable string of at most "
                f"{ASSIGNMENT_MAX_TEAM} characters",
            )
            expected_schema = assignment_properties.get("expectedVersion") or {}
            contracts.check(
                (
                    expected_schema.get("type"),
                    expected_schema.get("minimum"),
                ) == ("integer", 0),
                f"{relative}: AssignClaimRequest.expectedVersion must be an integer >= 0",
            )

            claim_schema = document_schemas.get(assignment_schema_name) or {}
            claim_properties = claim_schema.get("properties") or {}
            for field, maximum in ASSIGNMENT_CLAIM_FIELDS.items():
                field_schema = claim_properties.get(field)
                contracts.check(
                    isinstance(field_schema, dict),
                    f"{relative}: {assignment_schema_name}.{field} is required",
                )
                if not isinstance(field_schema, dict):
                    continue
                contracts.check(
                    _schema_types(field_schema) == {"string", "null"},
                    f"{relative}: {assignment_schema_name}.{field} must be a nullable string",
                )
                if maximum is None:
                    contracts.check(
                        field_schema.get("format") == "date-time",
                        f"{relative}: {assignment_schema_name}.{field} must be a date-time",
                    )
                else:
                    contracts.check(
                        field_schema.get("maxLength") == maximum,
                        f"{relative}: {assignment_schema_name}.{field} maxLength must be {maximum}",
                    )

            for assignment_path, assignment_method, claim_schema, book_parameter in (
                ASSIGNMENT_OPENAPI_PATHS.get(vertical, [])
            ):
                path_item = paths.get(assignment_path) if isinstance(paths, dict) else None
                operation = (
                    path_item.get(assignment_method)
                    if isinstance(path_item, dict)
                    else None
                )
                where = f"{relative}: {assignment_method.upper()} {assignment_path}"
                contracts.check(
                    isinstance(operation, dict),
                    f"{where}: required assignment operation is missing",
                )
                if not isinstance(operation, dict):
                    continue
                parameter_refs = []
                inline_names = []
                for parameter in operation.get("parameters") or []:
                    if not isinstance(parameter, dict):
                        continue
                    reference = parameter.get("$ref")
                    if isinstance(reference, str):
                        parameter_refs.append(reference.rsplit("/", 1)[-1])
                    if isinstance(parameter.get("name"), str):
                        inline_names.append(parameter["name"])
                for required_parameter in (
                    "TenantHeader",
                    book_parameter,
                    "ActorHeader",
                ):
                    contracts.check(
                        required_parameter in parameter_refs,
                        f"{where}: must document the shared {required_parameter} parameter",
                    )
                contracts.check(
                    "claimId" in inline_names,
                    f"{where}: must declare the claimId path parameter",
                )
                request_body = operation.get("requestBody") or {}
                request_schema = (
                    ((request_body.get("content") or {}).get("application/json") or {})
                    .get("schema")
                    if isinstance(request_body, dict)
                    else None
                )
                contracts.check(
                    isinstance(request_schema, dict)
                    and str(request_schema.get("$ref", "")).endswith(
                        "/schemas/AssignClaimRequest"
                    ),
                    f"{where}: request body must use the AssignClaimRequest schema",
                )
                responses = operation.get("responses") or {}
                ok_response = responses.get("200") if isinstance(responses, dict) else None
                ok_schema = (
                    ((ok_response.get("content") or {}).get("application/json") or {})
                    .get("schema")
                    if isinstance(ok_response, dict)
                    else None
                )
                contracts.check(
                    isinstance(ok_schema, dict)
                    and str(ok_schema.get("$ref", "")).endswith(
                        f"/schemas/{claim_schema}"
                    ),
                    f"{where}: 200 must return the {claim_schema} schema",
                )
                for code, suffix in (
                    ("400", "/responses/BadRequest"),
                    ("404", "/responses/NotFound"),
                    ("409", "/responses/Conflict"),
                ):
                    response = responses.get(code) if isinstance(responses, dict) else None
                    contracts.check(
                        isinstance(response, dict)
                        and str(response.get("$ref", "")).endswith(suffix),
                        f"{where}: {code} must reference the shared {suffix.rsplit('/', 1)[-1]} response",
                    )
        for required_path, required_method, required_codes in ROUND5_REQUIRED_RESPONSES.get(vertical, []):
            path_item = paths.get(required_path) if isinstance(paths, dict) else None
            operation = path_item.get(required_method) if isinstance(path_item, dict) else None
            responses = operation.get("responses") if isinstance(operation, dict) else None
            for code in required_codes:
                contracts.check(
                    isinstance(responses, dict) and code in responses,
                    f"{relative}: {required_method.upper()} {required_path} must document response {code}",
                )

        search_path, search_book, search_type = SEARCH_OPENAPI_PATHS[vertical]
        search_path_item = paths.get(search_path) if isinstance(paths, dict) else None
        search_operation = search_path_item.get("get") if isinstance(search_path_item, dict) else None
        contracts.check(
            isinstance(search_operation, dict),
            f"{relative}: required search operation GET {search_path} is missing",
        )
        if isinstance(search_operation, dict):
            parameter_refs = []
            for parameter in search_operation.get("parameters") or []:
                reference = parameter.get("$ref") if isinstance(parameter, dict) else None
                if isinstance(reference, str):
                    parameter_refs.append(reference.rsplit("/", 1)[-1])
            contracts.check(
                "TenantHeader" in parameter_refs,
                f"{relative}: GET {search_path} must require the shared TenantHeader",
            )
            if search_book:
                contracts.check(
                    search_book in parameter_refs,
                    f"{relative}: GET {search_path} must require the shared {search_book}",
                )
            else:
                contracts.check(
                    not ({"BookHeaderDirect", "BookHeaderAssumed"} & set(parameter_refs)),
                    f"{relative}: GET {search_path} is not book-scoped and must not declare a book header",
                )
            contracts.check(
                "SearchQuery" in parameter_refs,
                f"{relative}: GET {search_path} must document the shared SearchQuery parameter",
            )
            contracts.check(
                "SearchLimit" in parameter_refs,
                f"{relative}: GET {search_path} must document the shared SearchLimit parameter",
            )
            contracts.check(
                search_operation.get("x-search-type") == search_type,
                f"{relative}: GET {search_path} must declare x-search-type: {search_type}",
            )
            list_path, list_method = REQUIRED_OPENAPI_PATHS[vertical][0]
            list_path_item = paths.get(list_path) if isinstance(paths, dict) else None
            list_operation = list_path_item.get(list_method) if isinstance(list_path_item, dict) else None
            contracts.check(
                isinstance(list_operation, dict)
                and search_operation.get("security") == list_operation.get("security"),
                f"{relative}: GET {search_path} security must match GET {list_path}",
            )
            search_responses = search_operation.get("responses") or {}
            ok_response = search_responses.get("200") if isinstance(search_responses, dict) else None
            ok_schema = None
            if isinstance(ok_response, dict):
                ok_schema = (((ok_response.get("content") or {}).get("application/json") or {})
                             .get("schema"))
            contracts.check(
                isinstance(ok_schema, dict)
                and ok_schema.get("$ref") == "./components.yaml#/components/schemas/SearchResponse",
                f"{relative}: GET {search_path} 200 must use the shared SearchResponse schema",
            )
            bad_request = search_responses.get("400") if isinstance(search_responses, dict) else None
            contracts.check(
                isinstance(bad_request, dict)
                and str(bad_request.get("$ref", "")).endswith("/responses/BadRequest"),
                f"{relative}: GET {search_path} must document the shared problem+json BadRequest",
            )
            if search_book:
                contracts.check(
                    "404" in search_responses,
                    f"{relative}: GET {search_path} must document the 404 book-scope response",
                )

        compatibility = document.get("x-compatibility") or {}
        if isinstance(compatibility, dict) and compatibility.get("contractVersion"):
            contracts.check(
                compatibility.get("contractVersion") == doc_info.get("version"),
                f"{relative}: x-compatibility.contractVersion must equal info.version",
            )
        if vertical == "payment":
            check_payment_openapi_sources(contracts, document, relative)
            check_payment_source_filter(contracts, document, relative)
            check_payment_allocations(contracts, document, relative)
            check_payment_allocation_reversal(contracts, document, relative)
            check_payment_status(contracts, document, relative)
        if vertical == "document":
            check_document_links_openapi(contracts, document, relative)
            check_document_content_openapi(contracts, document, relative)
            check_document_holds_openapi(contracts, document, relative)
        if vertical == "policy":
            check_policy_billing_openapi(contracts, document, relative)
            check_policy_receivables_openapi(contracts, document, relative)
            check_policy_dunning_openapi(contracts, document, relative)
            check_policy_renewal_openapi(contracts, document, relative)
            check_policy_mass_tort_profile_openapi(contracts, document, relative)
            check_policy_programs(contracts, document, relative)
            check_policy_credit_notes_openapi(contracts, document, relative)
            check_policy_legal_entities_openapi(contracts, document, relative)
            check_policy_premium_audit_openapi(contracts, document, relative)
        if vertical == "contract":
            check_contract_security(contracts, document, relative)
            check_contract_security_status(contracts, document, relative)
            check_contract_technical_accounts(contracts, document, relative)
            check_contract_technical_account_lines(contracts, document, relative)
            check_contract_bordereaux(contracts, document, relative)
            check_contract_cash_calls(contracts, document, relative)
        if vertical == "direct-claims":
            check_direct_claim_allocations(contracts, document, relative)
            check_direct_claim_list_filter(contracts, document, relative)
            check_direct_claim_settlement_payment(contracts, document, relative)
        if vertical == "notifications":
            check_notifications_openapi(contracts, document, relative)
            check_notification_templates_openapi(contracts, document, relative)
        contracts.check_openapi_schemas(document, relative)
        if verbose:
            print(f"  OK {relative}  paths={len(paths)} operations={operation_count}")
        else:
            print(f"  OK {relative}  {len(paths)} paths, {operation_count} operations")
    contracts.check_openapi_schemas(components, Path("openapi/components.yaml"))



def check_notification_templates_asyncapi(contracts: ContractSet, document, relative: str):
    """Require the three implemented template lifecycle channels.

    Each channel carries the shared DomainEvent envelope and the dedicated
    NotificationTemplateData payload with the six-member data object. The
    template version is the identity version from the row, not the aggregate
    version (1 create, 2 approve, 3 retire).
    """
    channels = document.get("channels") or {}
    operations = document.get("operations") or {}
    messages = (document.get("components") or {}).get("messages") or {}

    message = messages.get(NOTIFICATION_TEMPLATE_EVENT_MESSAGE) or {}
    payload = message.get("payload") or {}
    properties = payload.get("properties") or {}
    required = set(payload.get("required") or [])
    contracts.check(
        isinstance(message, dict) and message.get("contentType") == "application/json",
        f"{relative}: {NOTIFICATION_TEMPLATE_EVENT_MESSAGE} must declare "
        "application/json",
    )
    contracts.check(
        set(properties) == set(NOTIFICATION_TEMPLATE_EVENT_FIELDS),
        f"{relative}: {NOTIFICATION_TEMPLATE_EVENT_MESSAGE} must declare exactly "
        f"{list(NOTIFICATION_TEMPLATE_EVENT_FIELDS)}",
    )
    for field in NOTIFICATION_TEMPLATE_EVENT_FIELDS:
        contracts.check(
            field in required,
            f"{relative}: {NOTIFICATION_TEMPLATE_EVENT_MESSAGE}.required must list "
            f"{field}",
        )
    contracts.check(
        (properties.get("templateId") or {}).get("format") == "uuid",
        f"{relative}: {NOTIFICATION_TEMPLATE_EVENT_MESSAGE}.templateId must be a uuid",
    )
    payload_code = properties.get("code") or {}
    contracts.check(
        (payload_code.get("type"), payload_code.get("maxLength"))
        == ("string", NOTIFICATION_TEMPLATE_CODE_MAX_LENGTH),
        f"{relative}: {NOTIFICATION_TEMPLATE_EVENT_MESSAGE}.code must be a string of "
        f"at most {NOTIFICATION_TEMPLATE_CODE_MAX_LENGTH} characters",
    )
    payload_version = properties.get("version") or {}
    contracts.check(
        (payload_version.get("type"), payload_version.get("minimum")) == ("integer", 1),
        f"{relative}: {NOTIFICATION_TEMPLATE_EVENT_MESSAGE}.version must be a "
        "positive integer",
    )
    payload_locale = properties.get("locale") or {}
    contracts.check(
        (payload_locale.get("type"), payload_locale.get("maxLength"))
        == ("string", NOTIFICATION_TEMPLATE_LOCALE_MAX_LENGTH),
        f"{relative}: {NOTIFICATION_TEMPLATE_EVENT_MESSAGE}.locale must be a string "
        f"of at most {NOTIFICATION_TEMPLATE_LOCALE_MAX_LENGTH} characters",
    )
    contracts.check(
        tuple((properties.get("status") or {}).get("enum") or [])
        == NOTIFICATION_TEMPLATE_STATUSES,
        f"{relative}: {NOTIFICATION_TEMPLATE_EVENT_MESSAGE}.status must enumerate "
        f"{list(NOTIFICATION_TEMPLATE_STATUSES)}",
    )
    payload_approver = properties.get("approvedBy") or {}
    contracts.check(
        _schema_types(payload_approver) == {"string", "null"}
        and payload_approver.get("format") == "uuid",
        f"{relative}: {NOTIFICATION_TEMPLATE_EVENT_MESSAGE}.approvedBy must be a "
        "nullable uuid",
    )

    send_events = {
        operation.get("x-event-type")
        for operation in operations.values()
        if isinstance(operation, dict) and operation.get("action") == "send"
    }
    template_addresses = {
        channel.get("address")
        for channel in channels.values()
        if isinstance(channel, dict)
        and str(channel.get("address") or "").startswith("notifications.template.")
    }
    contracts.check(
        template_addresses == set(NOTIFICATION_TEMPLATE_EVENTS),
        f"{relative}: the notifications.template.* channels must be exactly "
        f"{list(NOTIFICATION_TEMPLATE_EVENTS)}",
    )
    for event in NOTIFICATION_TEMPLATE_EVENTS:
        channel = next(
            (
                channel
                for channel in channels.values()
                if isinstance(channel, dict) and channel.get("address") == event
            ),
            None,
        )
        where = f"{relative}: {event}"
        contracts.check(isinstance(channel, dict), f"{where} channel is missing")
        if not isinstance(channel, dict):
            continue
        contracts.check(
            channel.get("x-status") == "implemented",
            f"{where} channel must be implemented",
        )
        contracts.check(
            channel.get("x-event-version") == 1,
            f"{where} channel must stay at x-event-version 1",
        )
        contracts.check(
            str(channel.get("x-implemented-by", "")).endswith(
                NOTIFICATION_TEMPLATE_EVENT_IMPLEMENTED_BY
            ),
            f"{where} must name {NOTIFICATION_TEMPLATE_EVENT_IMPLEMENTED_BY} in "
            "x-implemented-by",
        )
        channel_messages = channel.get("messages") or {}
        contracts.check(
            NOTIFICATION_TEMPLATE_EVENT_MESSAGE in channel_messages,
            f"{where} must reference {NOTIFICATION_TEMPLATE_EVENT_MESSAGE}",
        )
        contracts.check(
            event in send_events,
            f"{where} must have an implemented send operation",
        )


def check_asyncapi(contracts: ContractSet, verbose: bool):
    print("\nAsyncAPI 3 documents")
    expected = {"event-catalog"} | set(VERTICAL_FILES)
    present = {path.stem for path in ASYNCAPI_DIR.glob("*.yaml")}
    contracts.check(
        present == expected,
        f"asyncapi/ must contain exactly {sorted(expected)}; found {sorted(present)}",
    )

    catalog_path = ASYNCAPI_DIR / "event-catalog.yaml"
    catalog = contracts.load(catalog_path)
    contracts.check(catalog.get("asyncapi") == "3.0.0", "event-catalog.yaml: asyncapi must be 3.0.0")
    contracts.check(bool((catalog.get("info") or {}).get("version")), "event-catalog.yaml: info.version is required")
    catalog_entries = catalog.get("x-event-catalog") or {}
    contracts.check(isinstance(catalog_entries, dict), "event-catalog.yaml: x-event-catalog must be a mapping")
    contracts.check(
        set(catalog_entries) == set(VERTICAL_FILES),
        f"event-catalog.yaml: x-event-catalog must list exactly {sorted(VERTICAL_FILES)}",
    )

    published_by_vertical = {}
    for vertical in VERTICAL_FILES:
        path = ASYNCAPI_DIR / f"{vertical}.yaml"
        if not path.exists():
            contracts.check(False, f"missing asyncapi/{vertical}.yaml")
            continue
        document = contracts.load(path)
        relative = path.relative_to(ROOT).as_posix()
        contracts.check(document.get("asyncapi") == "3.0.0", f"{relative}: asyncapi must be 3.0.0")
        contracts.check(bool((document.get("info") or {}).get("version")), f"{relative}: info.version is required")
        channels = document.get("channels") or {}
        operations = document.get("operations") or {}
        contracts.check(isinstance(channels, dict) and bool(channels), f"{relative}: channels must be non-empty")
        contracts.check(isinstance(operations, dict) and bool(operations), f"{relative}: operations must be non-empty")

        addresses = set()
        implemented_addresses = set()
        for channel_key, channel in channels.items():
            where = f"{relative}: channel {channel_key}"
            contracts.check(isinstance(channel, dict), f"{where} must be a mapping")
            if not isinstance(channel, dict):
                continue
            address = channel.get("address")
            contracts.check(bool(address), f"{where} needs an address")
            if address:
                addresses.add(address)
                contracts.check(bool(EVENT_NAME_RE.fullmatch(address)), f"{where} address '{address}' is not a valid event name")
                contracts.check(channel.get("x-event-type") == address, f"{where} x-event-type must equal the address")
                status = channel.get("x-status")
                contracts.check(
                    status in ("planned", "implemented"),
                    f"{where} must be marked x-status: planned or x-status: implemented",
                )
                if status == "implemented":
                    implemented_addresses.add(address)
                    contracts.check(
                        bool(channel.get("x-implemented-by")),
                        f"{where} is implemented and must name the emitting source in x-implemented-by",
                    )
            messages = channel.get("messages") or {}
            contracts.check("DomainEvent" in messages, f"{where} must reference the DomainEvent message")

        for operation_key, operation in operations.items():
            where = f"{relative}: operation {operation_key}"
            contracts.check(isinstance(operation, dict), f"{where} must be a mapping")
            if not isinstance(operation, dict):
                continue
            contracts.check(operation.get("action") == "send", f"{where} action must be send for a publisher document")
            channel_ref = (operation.get("channel") or {}).get("$ref")
            contracts.check(
                isinstance(channel_ref, str) and channel_ref.startswith("#/channels/"),
                f"{where} must reference a local channel",
            )
            if isinstance(channel_ref, str) and channel_ref.startswith("#/channels/"):
                key = channel_ref.split("/")[-1].replace("~1", "/")
                contracts.check(key in channels, f"{where} references unknown channel '{key}'")
            contracts.check(
                operation.get("x-status") in ("planned", "implemented"),
                f"{where} must be marked x-status: planned or x-status: implemented",
            )

        if vertical == "direct-claims":
            check_direct_claim_settlement_payment_asyncapi(
                contracts, document, relative
            )

        if vertical == "policy":
            send_events = {
                operation.get("x-event-type")
                for operation in operations.values()
                if isinstance(operation, dict) and operation.get("action") == "send"
            }
            for event in POLICY_BILLING_EVENTS:
                contracts.check(
                    event in addresses,
                    f"{relative}: required billing event channel '{event}' is missing",
                )
                contracts.check(
                    event in implemented_addresses,
                    f"{relative}: billing event channel '{event}' must be implemented",
                )
                contracts.check(
                    event in send_events,
                    f"{relative}: billing event '{event}' must have a send operation",
                )

            contracts.check(
                MASS_TORT_EVENT in addresses,
                f"{relative}: required mass tort event channel '{MASS_TORT_EVENT}' is missing",
            )
            contracts.check(
                MASS_TORT_EVENT in implemented_addresses,
                f"{relative}: mass tort event channel '{MASS_TORT_EVENT}' must be implemented",
            )
            contracts.check(
                MASS_TORT_EVENT in send_events,
                f"{relative}: mass tort event '{MASS_TORT_EVENT}' must have a send operation",
            )
            mass_tort_channel = next(
                (
                    channel
                    for channel in channels.values()
                    if isinstance(channel, dict)
                    and channel.get("address") == MASS_TORT_EVENT
                ),
                None,
            )
            mass_tort_messages = (
                mass_tort_channel.get("messages")
                if isinstance(mass_tort_channel, dict)
                else None
            ) or {}
            contracts.check(
                "PolicyMassTortProfileUpdatedData" in mass_tort_messages,
                f"{relative}: {MASS_TORT_EVENT} must reference "
                "PolicyMassTortProfileUpdatedData",
            )
            mass_tort_message = (
                ((document.get("components") or {}).get("messages") or {}).get(
                    "PolicyMassTortProfileUpdatedData"
                )
                or {}
            )
            payload = mass_tort_message.get("payload") or {}
            payload_properties = payload.get("properties") or {}
            payload_required = set(payload.get("required") or [])
            for field in MASS_TORT_EVENT_FIELDS:
                contracts.check(
                    field in payload_properties,
                    f"{relative}: PolicyMassTortProfileUpdatedData.properties.{field} "
                    "is required",
                )
                contracts.check(
                    field in payload_required,
                    f"{relative}: PolicyMassTortProfileUpdatedData.required must list {field}",
                )
            contracts.check(
                (payload_properties.get("status") or {}).get("enum")
                == list(MASS_TORT_PROFILE_STATUSES),
                f"{relative}: PolicyMassTortProfileUpdatedData.status must enumerate "
                f"{list(MASS_TORT_PROFILE_STATUSES)}",
            )
            for field, expected in (
                ("tortType", MASS_TORT_TORT_TYPES),
                ("triggerType", MASS_TORT_TRIGGER_TYPES),
                ("allocationMethod", MASS_TORT_ALLOCATION_METHODS),
            ):
                contracts.check(
                    set((payload_properties.get(field) or {}).get("enum") or [])
                    == set(expected),
                    f"{relative}: PolicyMassTortProfileUpdatedData.{field} must enumerate "
                    f"{list(expected)}",
                )
            for field in ("coverageBlockStart", "coverageBlockEnd"):
                contracts.check(
                    _schema_types(payload_properties.get(field)) == {"string", "null"},
                    f"{relative}: PolicyMassTortProfileUpdatedData.{field} must be a "
                    "nullable string",
                )

            contracts.check(
                DUNNING_EVENT in addresses,
                f"{relative}: required dunning event channel '{DUNNING_EVENT}' is "
                "missing",
            )
            contracts.check(
                DUNNING_EVENT in implemented_addresses,
                f"{relative}: dunning event channel '{DUNNING_EVENT}' must be "
                "implemented",
            )
            contracts.check(
                DUNNING_EVENT in send_events,
                f"{relative}: dunning event '{DUNNING_EVENT}' must have a send "
                "operation",
            )
            dunning_channel = next(
                (
                    channel
                    for channel in channels.values()
                    if isinstance(channel, dict)
                    and channel.get("address") == DUNNING_EVENT
                ),
                None,
            )
            dunning_messages = (
                dunning_channel.get("messages")
                if isinstance(dunning_channel, dict)
                else None
            ) or {}
            contracts.check(
                "PolicyDunningSentData" in dunning_messages,
                f"{relative}: {DUNNING_EVENT} must reference PolicyDunningSentData",
            )
            dunning_message = (
                ((document.get("components") or {}).get("messages") or {}).get(
                    "PolicyDunningSentData"
                )
                or {}
            )
            dunning_payload = dunning_message.get("payload") or {}
            dunning_properties = dunning_payload.get("properties") or {}
            dunning_required = set(dunning_payload.get("required") or [])
            for field in DUNNING_EVENT_FIELDS:
                contracts.check(
                    field in dunning_properties,
                    f"{relative}: PolicyDunningSentData.properties.{field} is "
                    "required",
                )
                contracts.check(
                    field in dunning_required,
                    f"{relative}: PolicyDunningSentData.required must list {field}",
                )
            contracts.check(
                tuple((dunning_properties.get("level") or {}).get("enum") or [])
                == DUNNING_LEVELS,
                f"{relative}: PolicyDunningSentData.level must enumerate "
                f"{list(DUNNING_LEVELS)}",
            )
            contracts.check(
                tuple((dunning_properties.get("channel") or {}).get("enum") or [])
                == DUNNING_CHANNELS,
                f"{relative}: PolicyDunningSentData.channel must enumerate "
                f"{list(DUNNING_CHANNELS)}",
            )
            contracts.check(
                tuple((dunning_properties.get("status") or {}).get("enum") or [])
                == DUNNING_STATUSES,
                f"{relative}: PolicyDunningSentData.status must enumerate "
                f"{list(DUNNING_STATUSES)}",
            )
            contracts.check(
                (dunning_properties.get("sentAt") or {}).get("format") == "date-time",
                f"{relative}: PolicyDunningSentData.sentAt must be a date-time",
            )
            for field in ("policyId", "installmentId"):
                contracts.check(
                    (dunning_properties.get(field) or {}).get("format") == "uuid",
                    f"{relative}: PolicyDunningSentData.{field} must be a uuid",
                )
            check_policy_programs_asyncapi(contracts, document, relative)
            check_policy_credit_notes_asyncapi(contracts, document, relative)
            check_policy_legal_entities_asyncapi(contracts, document, relative)
            check_policy_premium_audit_asyncapi(contracts, document, relative)
            check_policy_billing_adjustment_asyncapi(contracts, document, relative)

        if vertical == "contract":
            check_contract_technical_accounts_asyncapi(
                contracts, document, relative
            )
            check_contract_technical_account_lines_asyncapi(
                contracts, document, relative
            )
            contract_send_events = {
                operation.get("x-event-type")
                for operation in operations.values()
                if isinstance(operation, dict)
                and operation.get("action") == "send"
            }
            for event in CONTRACT_CASH_CALL_EVENTS:
                contracts.check(
                    event in addresses,
                    f"{relative}: required cash-call event channel '{event}' is missing",
                )
                contracts.check(
                    event in implemented_addresses,
                    f"{relative}: cash-call event channel '{event}' must be implemented",
                )
                contracts.check(
                    event in contract_send_events,
                    f"{relative}: cash-call event '{event}' must have a send operation",
                )
                cash_call_channel = next(
                    (
                        channel
                        for channel in channels.values()
                        if isinstance(channel, dict) and channel.get("address") == event
                    ),
                    None,
                )
                cash_call_messages = (
                    cash_call_channel.get("messages")
                    if isinstance(cash_call_channel, dict)
                    else None
                ) or {}
                contracts.check(
                    "ContractCashCallData" in cash_call_messages,
                    f"{relative}: {event} must reference ContractCashCallData",
                )
            cash_call_message = (
                ((document.get("components") or {}).get("messages") or {}).get(
                    "ContractCashCallData"
                )
                or {}
            )
            payload = cash_call_message.get("payload") or {}
            payload_properties = payload.get("properties") or {}
            payload_required = set(payload.get("required") or [])
            for field in CONTRACT_CASH_CALL_EVENT_FIELDS:
                contracts.check(
                    field in payload_properties,
                    f"{relative}: ContractCashCallData.properties.{field} is required",
                )
                contracts.check(
                    field in payload_required,
                    f"{relative}: ContractCashCallData.required must list {field}",
                )
            contracts.check(
                set((payload_properties.get("status") or {}).get("enum") or [])
                == set(CONTRACT_CASH_CALL_STATUSES),
                f"{relative}: ContractCashCallData.status must enumerate "
                f"{list(CONTRACT_CASH_CALL_STATUSES)}",
            )
            settlement_reference = payload_properties.get(
                CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_FIELD
            ) or {}
            contracts.check(
                CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_FIELD
                in payload_properties,
                f"{relative}: ContractCashCallData.properties."
                "settlementReference is required for the settled event",
            )
            contracts.check(
                CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_FIELD
                not in payload_required,
                f"{relative}: ContractCashCallData.settlementReference must stay "
                "optional because requested, issued, and cancelled omit it",
            )
            contracts.check(
                settlement_reference.get("type") == "string"
                and settlement_reference.get("maxLength")
                == CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_MAX_LENGTH,
                f"{relative}: ContractCashCallData.settlementReference must be a "
                f"string of at most "
                f"{CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_MAX_LENGTH} characters",
            )
            settled_channel = next(
                (
                    channel
                    for channel in channels.values()
                    if isinstance(channel, dict)
                    and channel.get("address") == "contract.cash-call.settled"
                ),
                None,
            )
            contracts.check(
                CONTRACT_CASH_CALL_SETTLEMENT_REFERENCE_FIELD
                in str((settled_channel or {}).get("description") or ""),
                f"{relative}: contract.cash-call.settled must document "
                "settlementReference",
            )

            contracts.check(
                CONTRACT_SECURITY_EVENT in addresses,
                f"{relative}: required security event channel "
                f"'{CONTRACT_SECURITY_EVENT}' is missing",
            )
            contracts.check(
                CONTRACT_SECURITY_EVENT in implemented_addresses,
                f"{relative}: security event channel '{CONTRACT_SECURITY_EVENT}' "
                "must be implemented",
            )
            contracts.check(
                CONTRACT_SECURITY_EVENT in contract_send_events,
                f"{relative}: security event '{CONTRACT_SECURITY_EVENT}' must "
                "have a send operation",
            )
            security_channel = next(
                (
                    channel
                    for channel in channels.values()
                    if isinstance(channel, dict)
                    and channel.get("address") == CONTRACT_SECURITY_EVENT
                ),
                None,
            )
            security_messages = (
                security_channel.get("messages")
                if isinstance(security_channel, dict)
                else None
            ) or {}
            contracts.check(
                "ContractSecurityData" in security_messages,
                f"{relative}: {CONTRACT_SECURITY_EVENT} must reference "
                "ContractSecurityData",
            )
            security_message = (
                ((document.get("components") or {}).get("messages") or {}).get(
                    "ContractSecurityData"
                )
                or {}
            )
            security_payload = security_message.get("payload") or {}
            security_properties = security_payload.get("properties") or {}
            security_required = set(security_payload.get("required") or [])
            for field in CONTRACT_SECURITY_EVENT_FIELDS:
                contracts.check(
                    field in security_properties,
                    f"{relative}: ContractSecurityData.properties.{field} is required",
                )
                contracts.check(
                    field in security_required,
                    f"{relative}: ContractSecurityData.required must list {field}",
                )
            contracts.check(
                set((security_properties.get("status") or {}).get("enum") or [])
                == set(CONTRACT_SECURITY_STATUSES),
                f"{relative}: ContractSecurityData.status must enumerate "
                f"{list(CONTRACT_SECURITY_STATUSES)}",
            )
            contracts.check(
                set((security_properties.get("securityType") or {}).get("enum") or [])
                == set(CONTRACT_SECURITY_TYPES),
                f"{relative}: ContractSecurityData.securityType must enumerate "
                f"{list(CONTRACT_SECURITY_TYPES)}",
            )

            contracts.check(
                CONTRACT_SECURITY_STATUS_EVENT in addresses,
                f"{relative}: required security status event channel "
                f"'{CONTRACT_SECURITY_STATUS_EVENT}' is missing",
            )
            contracts.check(
                CONTRACT_SECURITY_STATUS_EVENT in implemented_addresses,
                f"{relative}: security status event channel "
                f"'{CONTRACT_SECURITY_STATUS_EVENT}' must be implemented",
            )
            contracts.check(
                CONTRACT_SECURITY_STATUS_EVENT in contract_send_events,
                f"{relative}: security status event "
                f"'{CONTRACT_SECURITY_STATUS_EVENT}' must have a send operation",
            )
            status_channel = next(
                (
                    channel
                    for channel in channels.values()
                    if isinstance(channel, dict)
                    and channel.get("address") == CONTRACT_SECURITY_STATUS_EVENT
                ),
                None,
            )
            status_messages = (
                status_channel.get("messages")
                if isinstance(status_channel, dict)
                else None
            ) or {}
            contracts.check(
                "ContractSecurityStatusChangedData" in status_messages,
                f"{relative}: {CONTRACT_SECURITY_STATUS_EVENT} must reference "
                "ContractSecurityStatusChangedData",
            )
            status_message = (
                ((document.get("components") or {}).get("messages") or {}).get(
                    "ContractSecurityStatusChangedData"
                )
                or {}
            )
            status_payload = status_message.get("payload") or {}
            status_properties = status_payload.get("properties") or {}
            status_required = set(status_payload.get("required") or [])
            for field in CONTRACT_SECURITY_STATUS_EVENT_FIELDS:
                contracts.check(
                    field in status_properties,
                    f"{relative}: ContractSecurityStatusChangedData.properties.{field} "
                    "is required",
                )
                contracts.check(
                    field in status_required,
                    f"{relative}: ContractSecurityStatusChangedData.required must list "
                    f"{field}",
                )
            contracts.check(
                set((status_properties.get("previousStatus") or {}).get("enum") or [])
                == set(CONTRACT_SECURITY_STATUS_PREVIOUS),
                f"{relative}: ContractSecurityStatusChangedData.previousStatus must "
                f"enumerate {list(CONTRACT_SECURITY_STATUS_PREVIOUS)}",
            )
            contracts.check(
                set((status_properties.get("status") or {}).get("enum") or [])
                == set(CONTRACT_SECURITY_STATUS_REQUEST_STATUSES),
                f"{relative}: ContractSecurityStatusChangedData.status must enumerate "
                f"{list(CONTRACT_SECURITY_STATUS_REQUEST_STATUSES)}",
            )
            contracts.check(
                set((status_properties.get("securityType") or {}).get("enum") or [])
                == set(CONTRACT_SECURITY_TYPES),
                f"{relative}: ContractSecurityStatusChangedData.securityType must "
                f"enumerate {list(CONTRACT_SECURITY_TYPES)}",
            )

        if vertical == "document":
            check_document_holds_asyncapi(contracts, document, relative)
            document_send_events = {
                operation.get("x-event-type")
                for operation in operations.values()
                if isinstance(operation, dict)
                and operation.get("action") == "send"
            }
            content_event_names = {
                address
                for address in addresses
                if isinstance(address, str) and address.startswith("document.content.")
            }
            contracts.check(
                content_event_names
                == {DOCUMENT_CONTENT_EVENT, DOCUMENT_CONTENT_DELETED_EVENT},
                f"{relative}: the document.content.* event names must be exactly "
                f"{[DOCUMENT_CONTENT_EVENT, DOCUMENT_CONTENT_DELETED_EVENT]}",
            )
            contracts.check(
                DOCUMENT_CONTENT_EVENT in addresses,
                f"{relative}: required content event channel "
                f"'{DOCUMENT_CONTENT_EVENT}' is missing",
            )
            contracts.check(
                DOCUMENT_CONTENT_EVENT in implemented_addresses,
                f"{relative}: content event channel '{DOCUMENT_CONTENT_EVENT}' "
                "must be implemented",
            )
            contracts.check(
                DOCUMENT_CONTENT_EVENT in document_send_events,
                f"{relative}: content event '{DOCUMENT_CONTENT_EVENT}' must "
                "have a send operation",
            )
            content_channel = next(
                (
                    channel
                    for channel in channels.values()
                    if isinstance(channel, dict)
                    and channel.get("address") == DOCUMENT_CONTENT_EVENT
                ),
                None,
            )
            contracts.check(
                isinstance(content_channel, dict)
                and str(content_channel.get("x-implemented-by", "")).endswith(
                    "DocumentContentEvents.java"
                ),
                f"{relative}: {DOCUMENT_CONTENT_EVENT} must name "
                "DocumentContentEvents.java in x-implemented-by",
            )
            content_messages = (
                content_channel.get("messages")
                if isinstance(content_channel, dict)
                else None
            ) or {}
            contracts.check(
                "DocumentContentUploadedData" in content_messages,
                f"{relative}: {DOCUMENT_CONTENT_EVENT} must reference "
                "DocumentContentUploadedData",
            )
            content_message = (
                ((document.get("components") or {}).get("messages") or {}).get(
                    "DocumentContentUploadedData"
                )
                or {}
            )
            content_payload = content_message.get("payload") or {}
            content_properties = content_payload.get("properties") or {}
            content_required = set(content_payload.get("required") or [])
            for field in (
                "documentId",
                "documentNumber",
                "version",
                "fileName",
                "contentType",
                "sizeBytes",
                "sha256",
            ):
                contracts.check(
                    field in content_properties,
                    f"{relative}: DocumentContentUploadedData.properties.{field} "
                    "is required",
                )
                contracts.check(
                    field in content_required,
                    f"{relative}: DocumentContentUploadedData.required must "
                    f"list {field}",
                )
            contracts.check(
                (content_properties.get("documentId") or {}).get("format") == "uuid",
                f"{relative}: DocumentContentUploadedData.documentId must be a uuid",
            )
            content_revision = content_properties.get("version") or {}
            contracts.check(
                content_revision.get("type") == "integer"
                and content_revision.get("minimum") == 1,
                f"{relative}: DocumentContentUploadedData.version must be a "
                "positive integer",
            )
            content_size = content_properties.get("sizeBytes") or {}
            contracts.check(
                (content_size.get("type"), content_size.get("maximum"))
                == ("integer", DOCUMENT_CONTENT_MAX_BYTES),
                f"{relative}: DocumentContentUploadedData.sizeBytes must be an "
                f"integer capped at {DOCUMENT_CONTENT_MAX_BYTES}",
            )
            contracts.check(
                (content_properties.get("sha256") or {}).get("pattern")
                == "^[a-f0-9]{64}$",
                f"{relative}: DocumentContentUploadedData.sha256 must be a "
                "lowercase 64-character digest",
            )

            contracts.check(
                DOCUMENT_CONTENT_DELETED_EVENT in addresses,
                f"{relative}: required content event channel "
                f"'{DOCUMENT_CONTENT_DELETED_EVENT}' is missing",
            )
            contracts.check(
                DOCUMENT_CONTENT_DELETED_EVENT in implemented_addresses,
                f"{relative}: content event channel "
                f"'{DOCUMENT_CONTENT_DELETED_EVENT}' must be implemented",
            )
            contracts.check(
                DOCUMENT_CONTENT_DELETED_EVENT in document_send_events,
                f"{relative}: content event '{DOCUMENT_CONTENT_DELETED_EVENT}' "
                "must have a send operation",
            )
            deleted_channel = next(
                (
                    channel
                    for channel in channels.values()
                    if isinstance(channel, dict)
                    and channel.get("address") == DOCUMENT_CONTENT_DELETED_EVENT
                ),
                None,
            )
            contracts.check(
                isinstance(deleted_channel, dict)
                and str(deleted_channel.get("x-implemented-by", "")).endswith(
                    "DocumentContentEvents.java"
                ),
                f"{relative}: {DOCUMENT_CONTENT_DELETED_EVENT} must name "
                "DocumentContentEvents.java in x-implemented-by",
            )
            deleted_messages = (
                deleted_channel.get("messages")
                if isinstance(deleted_channel, dict)
                else None
            ) or {}
            contracts.check(
                "DocumentContentDeletedData" in deleted_messages,
                f"{relative}: {DOCUMENT_CONTENT_DELETED_EVENT} must reference "
                "DocumentContentDeletedData",
            )
            deleted_description = (
                str(deleted_channel.get("description") or "")
                if isinstance(deleted_channel, dict)
                else ""
            )
            for term in ("dispose", "document.document.disposed"):
                contracts.check(
                    term in deleted_description,
                    f"{relative}: {DOCUMENT_CONTENT_DELETED_EVENT} description "
                    f"must document the {term} trigger",
                )
            deleted_message = (
                ((document.get("components") or {}).get("messages") or {}).get(
                    "DocumentContentDeletedData"
                )
                or {}
            )
            deleted_payload = deleted_message.get("payload") or {}
            deleted_properties = deleted_payload.get("properties") or {}
            deleted_required = set(deleted_payload.get("required") or [])
            contracts.check(
                set(deleted_properties) == set(DOCUMENT_CONTENT_DELETED_EVENT_FIELDS),
                f"{relative}: DocumentContentDeletedData must declare exactly "
                f"{list(DOCUMENT_CONTENT_DELETED_EVENT_FIELDS)}",
            )
            for field in DOCUMENT_CONTENT_DELETED_EVENT_FIELDS:
                contracts.check(
                    field in deleted_properties,
                    f"{relative}: DocumentContentDeletedData.properties.{field} "
                    "is required",
                )
                contracts.check(
                    field in deleted_required,
                    f"{relative}: DocumentContentDeletedData.required must list "
                    f"{field}",
                )
            contracts.check(
                (deleted_properties.get("documentId") or {}).get("format") == "uuid",
                f"{relative}: DocumentContentDeletedData.documentId must be a uuid",
            )
            deleted_size = deleted_properties.get("sizeBytes") or {}
            contracts.check(
                (deleted_size.get("type"), deleted_size.get("maximum"))
                == ("integer", DOCUMENT_CONTENT_MAX_BYTES),
                f"{relative}: DocumentContentDeletedData.sizeBytes must be an "
                f"integer capped at {DOCUMENT_CONTENT_MAX_BYTES}",
            )
            contracts.check(
                (deleted_properties.get("sha256") or {}).get("pattern")
                == "^[a-f0-9]{64}$",
                f"{relative}: DocumentContentDeletedData.sha256 must be a "
                "lowercase 64-character digest",
            )
            contracts.check(
                (deleted_properties.get("deletedAt") or {}).get("format")
                == "date-time",
                f"{relative}: DocumentContentDeletedData.deletedAt must be a "
                "date-time",
            )

        if vertical == "notifications":
            check_notification_templates_asyncapi(contracts, document, relative)

        entry = catalog_entries.get(vertical) or {}
        published = entry.get("published") or []
        contracts.check(isinstance(published, list) and bool(published), f"event-catalog.yaml: {vertical}.published must be non-empty")
        contracts.check(
            len(published) == len(set(published)),
            f"event-catalog.yaml: {vertical}.published contains duplicate event names",
        )
        contracts.check(
            set(published) == addresses,
            f"{relative}: channels {sorted(addresses)} do not match catalog published {sorted(published)}",
        )
        implemented = entry.get("implemented")
        contracts.check(
            isinstance(implemented, list),
            f"event-catalog.yaml: {vertical}.implemented must be a list (use [] when none is emitted)",
        )
        implemented = implemented or []
        contracts.check(
            len(implemented) == len(set(implemented)),
            f"event-catalog.yaml: {vertical}.implemented contains duplicate event names",
        )
        contracts.check(
            set(implemented) <= set(published),
            f"event-catalog.yaml: {vertical}.implemented must be a subset of published",
        )
        contracts.check(
            set(implemented) == implemented_addresses,
            f"{relative}: implemented channels {sorted(implemented_addresses)} do not match catalog implemented {sorted(implemented)}",
        )
        for event in published:
            contracts.check(bool(EVENT_NAME_RE.fullmatch(event)), f"event-catalog.yaml: {event} is not a valid event name")
        if vertical == "payment":
            check_payment_asyncapi_sources(contracts, document, relative)
            check_payment_allocation_asyncapi(contracts, document, relative)
            check_payment_allocation_reversed_asyncapi(
                contracts, document, relative
            )
        published_by_vertical[vertical] = set(published)
        if verbose:
            print(f"  OK {relative}  channels={len(channels)} operations={len(operations)}")
        else:
            print(f"  OK {relative}  {len(channels)} event channels")

    all_events = set()
    for names in published_by_vertical.values():
        overlap = all_events & names
        contracts.check(not overlap, f"event names published by more than one vertical: {sorted(overlap)}")
        all_events |= names

    for vertical, expected_events in IMPLEMENTED_EVENTS.items():
        entry = catalog_entries.get(vertical) or {}
        implemented = set(entry.get("implemented") or [])
        for event in expected_events:
            contracts.check(
                event in all_events,
                f"event-catalog.yaml: implemented event '{event}' is not published by any vertical",
            )
            contracts.check(
                event in implemented,
                f"event-catalog.yaml: implemented event '{event}' must be listed in {vertical}.implemented",
            )

    for vertical, entry in catalog_entries.items():
        if not isinstance(entry, dict):
            contracts.check(False, f"event-catalog.yaml: {vertical} entry must be a mapping")
            continue
        consumed = entry.get("consumed") or []
        contracts.check(isinstance(consumed, list), f"event-catalog.yaml: {vertical}.consumed must be a list")
        for event in consumed:
            contracts.check(
                event in all_events,
                f"event-catalog.yaml: {vertical} consumes '{event}' but no vertical publishes it",
            )
    print(f"  OK catalog: {len(all_events)} unique published events across {len(published_by_vertical)} verticals")


def check_json_schemas(contracts: ContractSet, verbose: bool):
    print("\nJSON Schema 2020-12 documents")
    present = {path.name for path in SCHEMA_DIR.glob("*.schema.json")}
    for name in REQUIRED_SCHEMA_FILES:
        contracts.check(name in present, f"schemas/: missing {name}")

    schemas = {}
    for name in REQUIRED_SCHEMA_FILES:
        path = SCHEMA_DIR / name
        if not path.exists():
            continue
        try:
            document = contracts.load(path)
        except json.JSONDecodeError as error:
            contracts.check(False, f"schemas/{name}: invalid JSON: {error}")
            continue
        relative = path.relative_to(ROOT).as_posix()
        contracts.check(isinstance(document, dict), f"{relative}: root must be an object")
        contracts.check(
            document.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
            f"{relative}: $schema must be the 2020-12 dialect",
        )
        contracts.check(bool(document.get("$id")), f"{relative}: $id is required")
        contracts.check_schema_object(document, str(relative))
        schemas[name] = document
        if verbose:
            print(f"  OK {relative}")

    error_schema = schemas.get("error-envelope.schema.json")
    if error_schema:
        required = set(error_schema.get("required") or [])
        for field in ("type", "title", "status", "detail", "instance", "code", "category", "retryable"):
            contracts.check(field in required, f"schemas/error-envelope.schema.json: '{field}' must be required")
        properties = error_schema.get("properties") or {}
        contracts.check(
            (properties.get("code") or {}).get("pattern") == "^EIA-[A-Z]{3}-[0-9]{4}$",
            "schemas/error-envelope.schema.json: code must use the EIA-XXX-NNNN pattern",
        )
        categories = set((properties.get("category") or {}).get("enum") or [])
        contracts.check(len(categories) >= 10, "schemas/error-envelope.schema.json: category enum is incomplete")
        for index, example in enumerate(error_schema.get("examples") or []):
            problems = _validate_instance(example, error_schema, error_schema)
            contracts.check(not problems, f"schemas/error-envelope.schema.json: example {index} invalid: {problems}")

    money_schema = schemas.get("money.schema.json")
    if money_schema:
        required = set(money_schema.get("required") or [])
        contracts.check({"amount", "currency"} <= required, "schemas/money.schema.json: amount and currency must be required")
        definitions = money_schema.get("$defs") or {}
        amount = definitions.get("MoneyAmount") or {}
        contracts.check(amount.get("type") == "string", "schemas/money.schema.json: MoneyAmount.type must be string")
        contracts.check(bool(amount.get("pattern")), "schemas/money.schema.json: MoneyAmount.pattern is required")
        currency = definitions.get("CurrencyCode") or {}
        contracts.check(currency.get("pattern") == "^[A-Z]{3}$", "schemas/money.schema.json: CurrencyCode.pattern must be ^[A-Z]{3}$")
        for index, example in enumerate(money_schema.get("examples") or []):
            problems = _validate_instance(example, money_schema, money_schema)
            contracts.check(not problems, f"schemas/money.schema.json: example {index} invalid: {problems}")

    event_schema = schemas.get("event-envelope.schema.json")
    if event_schema:
        required = set(event_schema.get("required") or [])
        for field in ("eventId", "eventType", "eventVersion", "occurredAt", "recordedAt", "tenantId", "vertical", "aggregateType", "aggregateId", "aggregateVersion", "subject", "data"):
            contracts.check(field in required, f"schemas/event-envelope.schema.json: '{field}' must be required")
        properties = event_schema.get("properties") or {}
        contracts.check(
            (properties.get("book") or {}).get("enum") == ["DIRECT", "ASSUMED"],
            "schemas/event-envelope.schema.json: book must be the DIRECT/ASSUMED enum",
        )
        verticals = set((properties.get("vertical") or {}).get("enum") or [])
        contracts.check(len(verticals) == 10, "schemas/event-envelope.schema.json: vertical must enumerate the ten verticals")


def _validate_instance(instance, schema, root, path="$"):
    """Validate a small subset of JSON Schema for the schema's own examples."""
    problems = []
    if "$ref" in schema:
        target = _local_ref(root, schema["$ref"])
        if target is None:
            return [f"{path}: unresolved $ref {schema['$ref']}"]
        return _validate_instance(instance, target, root, path)
    declared = schema.get("type")
    if declared is not None:
        types = declared if isinstance(declared, list) else [declared]
        if not any(_matches_type(instance, item) for item in types):
            problems.append(f"{path}: expected type {types}, found {type(instance).__name__}")
    enum = schema.get("enum")
    if enum is not None and instance not in enum:
        problems.append(f"{path}: value {instance!r} is not in enum")
    if isinstance(instance, str):
        pattern = schema.get("pattern")
        if pattern and re.fullmatch(pattern, instance) is None:
            problems.append(f"{path}: '{instance}' does not match {pattern}")
        minimum = schema.get("minLength")
        if minimum is not None and len(instance) < minimum:
            problems.append(f"{path}: shorter than minLength")
        maximum = schema.get("maxLength")
        if maximum is not None and len(instance) > maximum:
            problems.append(f"{path}: longer than maxLength")
    if isinstance(instance, int):
        minimum = schema.get("minimum")
        if minimum is not None and instance < minimum:
            problems.append(f"{path}: below minimum")
        maximum = schema.get("maximum")
        if maximum is not None and instance > maximum:
            problems.append(f"{path}: above maximum")
    if isinstance(instance, dict):
        for field in schema.get("required") or []:
            if field not in instance:
                problems.append(f"{path}: missing required '{field}'")
        properties = schema.get("properties") or {}
        for field, value in instance.items():
            if field in properties:
                problems.extend(_validate_instance(value, properties[field], root, f"{path}.{field}"))
            elif schema.get("additionalProperties") is False:
                problems.append(f"{path}: unexpected '{field}'")
    if isinstance(instance, list):
        items = schema.get("items")
        if isinstance(items, dict):
            for index, value in enumerate(instance):
                problems.extend(_validate_instance(value, items, root, f"{path}[{index}]"))
    return problems


def _matches_type(value, declared_type):
    if declared_type == "null":
        return value is None
    if declared_type == "string":
        return isinstance(value, str)
    if declared_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if declared_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if declared_type == "boolean":
        return isinstance(value, bool)
    if declared_type == "object":
        return isinstance(value, dict)
    if declared_type == "array":
        return isinstance(value, list)
    return True


def _local_ref(root, reference):
    if not reference.startswith("#/"):
        return None
    value = root
    for token in reference[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or token not in value:
            return None
        value = value[token]
    return value


def check_references(contracts: ContractSet):
    print("\nJSON Reference resolution")
    documents = []
    for directory in (OPENAPI_DIR, ASYNCAPI_DIR):
        documents.extend(sorted(directory.glob("*.yaml")))
    for path in documents:
        contracts.current_file = path
        contracts.walk_refs(contracts.load(path), path, "")
    print(f"  OK walked {len(documents)} YAML documents")


def main(argv: list[str]) -> int:
    verbose = "--verbose" in argv[1:]
    unknown = [arg for arg in argv[1:] if arg not in ("--verbose",)]
    if unknown:
        print(f"unknown arguments: {unknown}")
        return 2
    for directory in (OPENAPI_DIR, ASYNCAPI_DIR, SCHEMA_DIR):
        if not directory.is_dir():
            print(f"missing directory: {directory}")
            return 2

    print("EIA canonical contract validation")
    print(f"repository: {ROOT}")
    print(f"python: {sys.version.split()[0]} (standard library only)")

    contracts = ContractSet()
    sections = [
        ("OpenAPI 3.1 documents", lambda: check_openapi(contracts, verbose)),
        ("AsyncAPI 3 documents", lambda: check_asyncapi(contracts, verbose)),
        ("JSON Schema 2020-12 documents", lambda: check_json_schemas(contracts, verbose)),
        ("JSON Reference resolution", lambda: check_references(contracts)),
    ]
    for label, section in sections:
        try:
            section()
        except YamlError as error:
            contracts.check(False, f"{label}: YAML parse error: {error}")
        except json.JSONDecodeError as error:
            contracts.check(False, f"{label}: JSON parse error: {error}")

    print("\nResult")
    if contracts.failures:
        print(f"  FAIL {len(contracts.failures)} of {contracts.checks} checks failed")
        for failure in contracts.failures:
            print(f"   - {failure}")
        return 1
    print(f"  PASS {contracts.checks} checks, 0 failures")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
