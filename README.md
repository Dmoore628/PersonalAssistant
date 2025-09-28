# Archi AI Digital Twin - Monorepo

This repository contains the initial scaffolding for the Archi AI Digital Twin system per the TRD and Implementation Roadmap.

## Structure
- `services/` — Python microservices for agents and APIs
- `libs/` — Shared Python libraries (config, logging, schemas, messaging)
- `infra/` — Docker Compose, database configs, and local infra
- `scripts/` — PowerShell utilities for Windows developer workflows
- `.github/workflows/` — CI pipelines (lint, test, build)

## Getting Started
1. Ensure Docker Desktop is installed and running on Windows 10/11.
2. Copy `.env.example` to `.env` and adjust as needed.
3. Use scripts in `scripts/` to start the stack.

## Quality Gates
- Formatting: black
- Linting: ruff
- Types: mypy
- Tests: pytest + coverage

## Security
- Do not commit secrets. Use Windows Credential Manager for host-only secrets.
- Services load configuration from environment variables and `.env` files for local dev only.

## Workflow: Branching, Testing, Validation

1) Branching (protected):
- main (production), develop (integration), release/x.y, hotfix/x.y.z, feature/<area>/<desc>, fix/<scope>/<id>-<desc>, chore/<scope>/<desc>
- PRs must target `develop` (except hotfix to `main`).

2) Testing:
- Unit tests under `tests/` or alongside modules. Target 70%+ coverage.
- Integration tests run via docker compose (agents + infra).
- CI runs ruff, black --check, mypy, pytest.

3) Validation Protocol:
- For each PR, complete the PR checklist and add a log under `docs/validation/logs/` using `TEMPLATE.md`.
- Record environment, steps, and results of lint/type/test/container checks.

## Application Setup and Usage

### Prerequisites
- Docker and Docker Compose installed.
- Python 3.11 installed.

### Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/Dmoore628/PersonalAssistant.git
   cd PersonalAssistant
   ```

2. Build and start the services:
   ```bash
   docker-compose -f infra/docker-compose.yml up --build
   ```

3. Verify service health endpoints:
   - `learning-agent`: [http://localhost:8016/health](http://localhost:8016/health)
   - `memory-agent`: [http://localhost:8013/health](http://localhost:8013/health)
   - `planning-agent`: [http://localhost:8011/health](http://localhost:8011/health)
   - `security-agent`: [http://localhost:8014/health](http://localhost:8014/health)
   - `tool-creation-agent`: [http://localhost:8015/health](http://localhost:8015/health)
   - `execution-agent`: [http://localhost:8012/health](http://localhost:8012/health)

### RabbitMQ
- Default credentials:
  - User: `archi`
  - Password: `archi_secret`
- Management UI: [http://localhost:15672](http://localhost:15672)

### Neo4j
- Default credentials:
  - User: `neo4j`
  - Password: `neo4j_secret`
- Browser UI: [http://localhost:7474](http://localhost:7474)

### Testing
- Run unit tests:
  ```bash
  pytest tests/
  ```

### Notes
- Ensure all environment variables are correctly set in `docker-compose.yml`.
- For troubleshooting, check container logs:
  ```bash
  docker-compose -f infra/docker-compose.yml logs
  ```

### Quick commands (PowerShell)
- Lint/format/typecheck: `./scripts/lint.ps1`
- Run tests: `./scripts/test.ps1`
- Start stack: `./scripts/up.ps1 -Build`
- Stop stack: `./scripts/down.ps1`
