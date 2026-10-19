# Changelog

All notable changes to this repository are documented here.

The format is based on Keep a Changelog and the project uses Semantic Versioning.

## [Unreleased]

### Added

- OpenAPI 3.1 contracts for the party, policy, contract, direct-claims,
  assumed-claims, cession, retrocession, document, payment, and notifications
  verticals, covering the implemented public domain API and internal expert API.
- `openapi/components.yaml` with the canonical Problem error envelope, money,
  cursor pagination, audit fields, entity references, and tenant/book headers.
- AsyncAPI 3 event catalog and ten vertical event documents for the 151 domain
  events declared in SPEC 11.
- JSON Schema 2020-12 documents for the error envelope, money, and event
  envelope.
- `scripts/validate_contracts.py`, a standard-library-only validator for YAML
  parsing, required paths, event catalog consistency, schema members, and JSON
  References.
- `MISMATCHES.md`, the contract-to-implementation audit with source evidence.
- README sections for versioning, compatibility, validation, and the deviation
  policy.

### Changed

- README expanded from the repository baseline into the contract repository
  guide.

### Notes

- No runtime dependency, CI workflow, Maven build, or hosted pipeline was
  added. Validation is local and deterministic.
