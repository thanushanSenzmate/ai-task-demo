# GitHub Integration Guide

## Purpose

This document defines how AI agents should interact with GitHub during the software delivery lifecycle.

GitHub acts as the central collaboration platform for:

- Source code management
- Issue tracking
- Pull requests
- Code reviews
- CI/CD automation
- Release management

AI agents should use GitHub as the system of record for tracking development progress, issues, reviews, and releases.

> **Scope:** This file is a topic reference, not a root instruction file. Load it only when the current task involves GitHub (issues, PRs, CI, releases). Session startup rules live in `agents.md`, not here.
>
> **Keep this updated when:** the branch strategy, CI pipeline, severity classification, or approval requirements change. Stale workflow docs are worse than none — an agent will follow them literally.

---

## MCP Configuration

### Location

The GitHub MCP Server configuration is maintained in `opencode.json`. The AI agent **must check this file** before performing any GitHub-related operation.

### Expected Project Structure

```
project-root/
├── opencode.json
├── vision.md
├── agents.md
├── todo.md
├── README.md
└── docs/
    └── github.md
```

### What GitHub MCP Provides

GitHub MCP allows AI agents to interact with GitHub using standardized MCP tools instead of manually calling GitHub APIs. Agents can:

- Read repositories
- Create and update issues
- Create and review pull requests
- Monitor workflows
- Manage releases

### Authentication

Authentication is provided through the `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable, configured in `opencode.json`.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "github": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
      "enabled": true,
      "environment": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

### Agent Checklist Before GitHub Operations

1. Check `opencode.json`
2. Verify the GitHub MCP connection
3. Use GitHub MCP tools if available
4. Follow repository workflow rules
5. Avoid destructive operations without approval

### Fallback if MCP Is Unavailable

If the GitHub MCP server is not configured, fails to connect, or the token is missing/invalid:

1. **Do not** attempt to call GitHub's REST/GraphQL API directly as a workaround.
2. Check whether the `gh` CLI is available and authenticated as a fallback for read-only operations (browsing issues, PR status).
3. If no fallback is available, **stop and report the gap to the user** rather than skipping the GitHub step silently or guessing at repository state.

---

## GitHub MCP Capabilities

### Repository Management

Agents can:

- Read repository details
- Browse source code and read files
- Check branches and commits
- Inspect pull requests
- Check CI/CD status

### Issue Management

GitHub Issues are used to track:

- Bugs
- Security findings
- Code quality improvements
- Technical debt
- Feature requests

**Example issue:**

| Field | Value |
|---|---|
| Title | Hardcoded Secret Found |
| Labels | `security`, `high-priority` |
| Description | A sensitive credential was detected in the source code. |
| Recommended action | Remove the secret and use environment variables. |

### Issue Severity Classification

| Severity | Examples |
|---|---|
| **Critical** | Exposed credentials, remote code execution, authentication bypass |
| **High** | SQL injection, missing authorization checks, vulnerable dependencies |
| **Medium** | Code duplication, poor error handling, missing validation |
| **Low** | Refactoring suggestions, documentation improvements |

---

## Agent Workflows

### Security Agent Workflow

**Recommended tools (in order):** Gitleaks → Bandit → pip-audit → Dependency Scanner

1. Scan repository
2. Analyze finding
3. Create GitHub issue
4. Assign severity
5. Notify Fix Agent

### Fix Agent Workflow

1. Read open issues
2. Select highest-priority issue
3. Analyze root cause
4. Implement fix
5. Run tests
6. Run security scan
7. Commit changes
8. Update issue
9. Repeat from step 1

**Stop the loop when:**

- All critical issues are resolved
- Tests pass
- Security scans pass
- No high-severity issues remain

### Pull Request Workflow

1. Feature requirement identified
2. Create feature branch
3. Implement changes
4. Run tests
5. Create pull request
6. AI code review
7. Human approval
8. Merge

### Branch Strategy

| Branch | Purpose | Example |
|---|---|---|
| `main` | Production-ready code | — |
| `develop` | Integration branch | — |
| `feature/<feature-name>` | New feature work | `feature/task-api` |
| `bugfix/<issue-name>` | Bug fixes | `bugfix/login-validation` |

### Code Review Agent

The Code Review Agent should review:

**Code Quality**
- Readability
- Naming conventions
- Function complexity
- Duplicate code

**Design**
- Separation of concerns
- SOLID principles
- Maintainability

**Security**
- Input validation
- Authentication handling
- Secret management

**Testing**
- Test coverage
- Missing edge cases
- Regression risks

The agent should provide: review comments, suggested improvements, and possible fixes.

---

## GitHub Actions Integration

CI/CD workflows are located at:

```
.github/
└── workflows/
    └── ci.yml
```

### CI Pipeline

Every push and pull request triggers:

1. Code push triggers GitHub Actions
2. Runs in parallel: unit tests, code quality check, security scan, Docker build
3. Report status back to the PR/commit

### Recommended CI Checks

| Category | Tools |
|---|---|
| Testing | `pytest` |
| Code Quality | `ruff`, `flake8` |
| Security | `gitleaks`, `bandit`, `pip-audit` |
| Container Validation | `docker build .` |

---

## Release Workflow

The Release Agent is responsible for:

1. Verify CI status
2. Generate version number
3. Generate changelog
4. Create GitHub release
5. Update documentation

**Example release:**

```
Version: v1.0.0

Changes:
- Added authentication API
- Added task management API
- Added Docker support
- Added automated testing
```

---

## Human Approval Requirements

AI agents should **not** automatically:

- Merge production code
- Modify architecture
- Remove security checks
- Change deployment configuration
- Create production releases

**Human approval is required for:**

- Major refactoring
- Database changes
- Authentication changes
- Production deployment

---

## Source of Truth Files

| Information | Location |
|---|---|
| Project vision | `vision.md` |
| Agent responsibilities | `agents.md` |
| Current work items | `todo.md` |
| API specification | `docs/api.md` |
| Architecture | `docs/architecture.md` |
| Docker instructions | `docs/docker.md` |
| GitHub MCP configuration | `opencode.json` |
| GitHub workflow rules | `docs/github.md` |

---

## Agent Reminder

Session startup requirements (reading `vision.md`, `agents.md`, `todo.md`, etc.) are defined once in `agents.md` — do not duplicate them here. This file only adds: once GitHub work begins, keep issues, PRs, and releases updated as the record of progress.

GitHub should remain the single source of truth for code changes, issues, reviews, and releases.
