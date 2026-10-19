# eia-contracts

- GitHub organization: `eia-open-insurance`
- Repository URL: https://github.com/eia-open-insurance/eia-contracts
- Type: Contracts
- Deployable: No
- Owner: Architecture
- Runtime: YAML and JSON Schema
- Data store: Not applicable
- Depends on: None

## Purpose

Canonical OpenAPI, AsyncAPI, JSON Schema, and external mapping contracts.

## Responsibilities

- Keep this repository focused on one deployable component or one platform concern.
- Follow the repository standard in `../CONVENTIONS.md` and the specification in `../../SPEC.md`.
- Publish and consume contracts through `eia-contracts`.
- Maintain README, CODEOWNERS, SECURITY, CHANGELOG, tests, and local verification.
- Contain no business logic in shared libraries or front-end remotes.

## Verification

- Lint and format
- Unit tests with 100% business-logic coverage where applicable
- Contract tests
- Integration or Playwright tests where applicable
- Security scan and SBOM
- Build and publish

## Notes

Contract-first source of truth for all services and events.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
