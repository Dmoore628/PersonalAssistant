# Contributing Guide

Thank you for your interest in contributing to the Archi AI Digital Twin System! This project enforces a strict branching, testing, and validation workflow to ensure reliability, rollbackability, and reproducibility.

## 🚀 Getting Started

### Prerequisites
- Windows 10/11 with Docker Desktop
- Python 3.11+
- Git with PowerShell 5.1+
- Visual Studio Code (recommended)

### Development Setup
1. Fork and clone: `git clone https://github.com/yourusername/PersonalAssistant.git`
2. Environment setup: `Copy-Item .env.example .env` and configure
3. Install dependencies: `pip install -e libs/archi_core`
4. Start services: `.\scripts\up.ps1 -Build`
5. Verify setup: `.\scripts\test.ps1`

## 🔄 Branching Strategy (Trunk + Release + Hotfix)

**Protected Branches:**
- **main:** Always deployable; protected; version tags only
- **develop:** Integration branch; feature PRs merge here first

**Working Branches:**
- **release/x.y:** Stabilization for a version; only fixes, docs
- **hotfix/x.y.z:** Urgent fixes branched from main; merge back to main and develop
- **feature/\<area>/\<short-desc>:** New work. Example: `feature/ai/focus-scorer`
- **fix/\<scope>/\<issue-id>-\<desc>:** Bug fix referencing an issue
- **chore/\<scope>/\<desc>:** Tooling, config, docs, infra

**Naming Rules:**
- Use lowercase with hyphens; max 60 chars after prefix
- Rebase on latest `develop` before opening a PR
- One owner per feature branch to reduce merge conflicts

**Examples:**
```
feature/voice-processing/wake-word-detection
feature/cua/office-integration
fix/memory-agent/neo4j-timeout-issue-42
chore/ci/update-dependencies
```

## 📝 Commit Convention (Conventional Commits)

**Format:** `type(scope): subject`

**Types:** feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

**Examples:**
```
feat(memory): add neo4j upsert for task nodes
fix(security-agent): resolve audit log performance issue
docs(adr): add decision record for Neo4j selection
test(execution-agent): add CUA action validation tests
```

## 🔀 Pull Request Protocol

### Requirements
- Use the PR template with: scope, problem, solution, tests, risks, rollback plan
- Must pass: lint (ruff), format (black), types (mypy), tests (pytest), container build
- At least one approval by a code reviewer
- Include validation log in `docs/validation/logs/`

### PR Checklist
- [ ] Rebased on latest `develop`
- [ ] Follows conventional commit format
- [ ] All CI checks passing
- [ ] Tests added/updated with 70%+ coverage
- [ ] Documentation updated
- [ ] Validation log completed
- [ ] No merge conflicts

## 🧪 Testing Strategy

### Test Types & Coverage
- **Unit tests:** Fast, isolated; 70%+ coverage target per package
- **Integration tests:** Service-to-service via docker compose
- **Contract tests:** FastAPI schemas/models and message formats
- **E2E tests:** Smoke flows across core agents (optional for alpha)

### Test Organization
- Tests live next to code or under `tests/` with mirrors by module
- Use descriptive test names: `test_<function>_<scenario>`
- Comprehensive fixtures in `conftest.py`

### Running Tests
```powershell
# All tests with coverage
pytest --cov=libs --cov=services --cov-report=html

# Specific agent tests
pytest tests/test_planning_agent.py -v

# Integration tests  
docker-compose up -d && pytest tests/integration/
```

## 📋 Validation Protocol

### Required for Every PR
1. **Plan** → Implement → Verify → Record → Review
2. Add validation log to `docs/validation/logs/` using template
3. Record: environment, versions, commands, notable decisions
4. Steps: build, lint, format, type check, tests, containers

### Validation Template
Use `docs/validation/TEMPLATE.md` for consistent validation reporting.

## 🏗️ Architecture Guidelines

### Agent Implementation
- All agents implement `/health` endpoint with consistent schema
- Use async/await for I/O operations
- Comprehensive error handling with proper HTTP status codes
- Structured logging with correlation IDs
- Input validation using Pydantic schemas

### Inter-Agent Communication
- RabbitMQ message bus for async communication
- Clear message schemas in `archi_core.schemas`
- Idempotent message handlers
- Correlation IDs for request tracing

## 🔒 Security & Best Practices

### Security Requirements
- Never commit secrets or API keys
- Use Windows Credential Manager for local secrets
- Implement comprehensive input validation
- Follow principle of least privilege
- Use secure communication channels

### Code Quality
- Follow established patterns in existing codebase
- Use type hints for better maintainability
- Write descriptive docstrings
- Handle edge cases and error conditions
- Optimize for readability over cleverness

## 🎯 Areas for Contribution

### High-Priority
- **Voice Processing:** Wake-word detection, speech recognition
- **Computer Vision:** Screen capture, object detection
- **HUD Interface:** Windows overlay system
- **Integrations:** Office, browsers, trading platforms
- **Performance:** Optimization and scaling

### Good First Issues
Look for `good first issue` label:
- Documentation improvements
- Unit test additions
- Code style improvements
- Configuration enhancements

## 🏷️ Issue Guidelines

### Issue Types
Use appropriate templates:
- 🐛 **Bug Report:** Something isn't working
- ✨ **Feature Request:** New functionality
- 🤖 **Agent Enhancement:** AI agent improvements
- 🔗 **Integration Request:** New app integrations
- ⚡ **Performance Issue:** Performance problems

### Security Issues
- Use [GitHub Security Advisories](https://github.com/Dmoore628/PersonalAssistant/security/advisories)
- Never create public issues for vulnerabilities
- Provide detailed reproduction steps

## 🔧 Tooling

### Development Tools
- **Pre-commit hooks:** Lint/format before push
- **PowerShell scripts:** `scripts/` for local Windows dev
- **Docker Compose:** Service orchestration and testing
- **VS Code:** Recommended with Python extension

### Quality Gates
```powershell
# Lint and format
.\scripts\lint.ps1

# Run all tests
.\scripts\test.ps1

# Start full stack
.\scripts\up.ps1 -Build

# Stop services
.\scripts\down.ps1
```

## 📦 Releasing

### Release Process
1. Create `release/x.y` branch from `develop`
2. Stabilization: bug fixes, documentation updates
3. Merge to `main` with version tag `vX.Y.Z`
4. GitHub Release triggers CI build with artifacts

### Versioning
- Follow [Semantic Versioning](https://semver.org/)
- Major.Minor.Patch (e.g., 1.2.3)
- Breaking changes increment major version

## 📞 Getting Help

### Communication
- **GitHub Discussions:** Questions and community interaction
- **Issues:** Bug reports and feature requests
- **Pull Requests:** Code review and collaboration

### Resources
- [Technical Requirements](archi-technicalrequirement.md)
- [Implementation Roadmap](ImplementationRoadmap.md)
- [Architecture Decisions](docs/adr/)
- [API Docs](http://localhost:8011/docs) (local)

---

**Questions?** Open a [GitHub Discussion](https://github.com/Dmoore628/PersonalAssistant/discussions) or create an issue. We appreciate your contributions!
