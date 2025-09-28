# Contributing Guide

This project enforces a strict branching, testing, and validation workflow to ensure reliability, rollbackability, and reproducibility.

## Branching Strategy (Trunk + Release + Hotfix)
- main: Always deployable; protected; version tags only.
- develop: Integration branch; feature PRs merge here first.
- release/x.y: Stabilization for a version; only fixes, docs.
- hotfix/x.y.z: Urgent fixes branched from main; merge back to main and develop.
- feature/<area>/<short-desc>: New work. Example: `feature/ai/focus-scorer`.
- fix/<scope>/<issue-id>-<desc>: Bug fix referencing an issue.
- chore/<scope>/<desc>: Tooling, config, docs, infra.

Naming rules:
- Use lowercase with hyphens; max 60 chars after prefix.
- Rebase on latest `develop` before opening a PR.
- One owner per feature branch to reduce merge conflicts.

## Commit Convention (Conventional Commits)
- Format: `type(scope): subject`
- Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
- Example: `feat(memory): add neo4j upsert for task nodes`

## Pull Request Protocol
- Use the PR template. Include: scope, problem, solution, tests, risks, rollback plan.
- Must pass: lint (ruff), format (black), types (mypy), tests (pytest), container build where applicable.
- At least one approval by a code reviewer.

## Testing Strategy
- Unit tests: fast, isolated; 70%+ coverage target per package.
- Integration tests: service-to-service via docker compose.
- Contract tests: FastAPI schemas/models and message formats.
- E2E (alpha optional): smoke flows across core agents.
- Tests live next to code or under `tests/` with mirrors by module.

## Validation Protocol
- For every PR, add a new entry to `docs/validation/logs/` using the log template.
- Steps: Plan → Implement → Verify (build, lint, tests) → Record → Review.
- Record environment, versions, commands, and notable decisions.

## Releasing
- Tag `vX.Y.Z` on `main` via GitHub Release; CI builds and attaches artifacts.

## Tooling
- Use pre-commit for lint/format before push.
- Windows scripts are under `scripts/` for local dev.
