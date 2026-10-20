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
)

BILLING_INSTALLMENT_FIELDS = (
    "installmentId",
    "installmentNumber",
    "dueDate",
    "amount",
    "status",
    "paidAt",
    "paymentId",
)

BILLING_INSTALLMENT_REQUIRED_FIELDS = (
    "installmentId",
    "installmentNumber",
    "dueDate",
    "amount",
    "status",
)

BILLING_FREQUENCIES = ("MONTHLY", "QUARTERLY", "SEMI_ANNUAL", "ANNUAL")
BILLING_PLAN_STATUSES = ("ACTIVE", "COMPLETE", "CANCELLED")
BILLING_INSTALLMENT_STATUSES = ("DUE", "OVERDUE", "PAID", "WAIVED")
BILLING_SETTLE_STATUSES = ("PAID", "WAIVED")
BILLING_MIN_INSTALLMENTS = 1
BILLING_MAX_INSTALLMENTS = 24

# The three billing event names implemented by the Policy expert. The plan
# name differs from the SPEC 11.2.13 `policy.billing.plan-created` spelling and
# the installment facts have no SPEC name; MISMATCHES.md M-22 and M-27 record
# the deviation.
POLICY_BILLING_EVENTS = (
    "policy.billing-plan.created",
    "policy.installment.paid",
    "policy.installment.waived",
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
    "currency",
    "status",
    "daysPastDue",
)

RECEIVABLE_STATUSES = ("DUE", "OVERDUE")
RECEIVABLE_SUMMARY_FIELDS = ("items", "totalAmount", "overdueAmount", "count")
RECEIVABLE_DEFAULT_LIMIT = 20
RECEIVABLE_MIN_LIMIT = 1
RECEIVABLE_MAX_LIMIT = 200


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
        "policy.billing-plan.created",
        "policy.installment.paid",
        "policy.installment.waived",
        "policy.mass-tort-profile.updated",
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
        "contract.bordereau.received",
        "contract.bordereau.processed",
        "contract.bordereau.failed",
    ],
    "direct-claims": [
        "direct.claim.registered",
        "direct.claim.updated",
        "direct.claim.assigned",
        "direct.claim.coverage-assessed",
        "direct.claim.reserve-changed",
        "direct.claim.settlement-authorized",
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
    ],
    "payment": [
        "payment.payment.created",
        "payment.payment.updated",
        "payment.payment.status-changed",
    ],
    "notifications": [
        "notifications.notification.created",
        "notifications.notification.sent",
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
    contracts.check(
        str((installment_properties.get("amount") or {}).get("$ref", "")).endswith(
            "/schemas/MoneyAmount"
        ),
        f"{relative}: Installment.amount must reference MoneyAmount",
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
    count = summary_properties.get("count") or {}
    contracts.check(
        (count.get("type"), count.get("minimum")) == ("integer", 0),
        f"{relative}: ReceivableSummary.count must be an integer >= 0",
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

    planned = document.get("x-planned-operations") or []
    contracts.check(
        not any(
            isinstance(entry, dict)
            and entry.get("path") == "/api/v1/claims/{claimId}/allocations"
            for entry in planned
        ),
        f"{relative}: x-planned-operations must not list the implemented allocations path",
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
        if vertical == "document":
            check_document_links_openapi(contracts, document, relative)
        if vertical == "policy":
            check_policy_billing_openapi(contracts, document, relative)
            check_policy_receivables_openapi(contracts, document, relative)
            check_policy_renewal_openapi(contracts, document, relative)
            check_policy_mass_tort_profile_openapi(contracts, document, relative)
        if vertical == "contract":
            check_contract_technical_accounts(contracts, document, relative)
            check_contract_bordereaux(contracts, document, relative)
        if vertical == "direct-claims":
            check_direct_claim_allocations(contracts, document, relative)
        contracts.check_openapi_schemas(document, relative)
        if verbose:
            print(f"  OK {relative}  paths={len(paths)} operations={operation_count}")
        else:
            print(f"  OK {relative}  {len(paths)} paths, {operation_count} operations")
    contracts.check_openapi_schemas(components, Path("openapi/components.yaml"))



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
