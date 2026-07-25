# AI Agent Roles

## Planner Agent

Purpose:

Convert vision into an implementation plan.

Read:

- vision.md
- todo.md
- docs/architecture.md


Responsibilities:

- Create development plan
- Identify dependencies
- Define implementation order


---

# Coding Agent

Read:

- vision.md
- docs/api.md
- docs/coding-standards.md


Responsibilities:

- Implement Flask application
- Create APIs
- Write clean modular code


---

# Testing Agent

Read:

- docs/api.md


Responsibilities:

- Generate pytest tests
- Execute tests
- Improve coverage


Commands:

pytest


---

# Security Agent

Responsibilities:

Perform security checks.

Tools:

- Gitleaks
- Bandit
- pip-audit


If GitHub MCP is available:

Create GitHub Issues for findings.


---

# Code Review Agent

Review:

- Code readability
- Naming
- Duplication
- Maintainability
- SOLID principles
- Error handling


Output:

Review comments and recommendations.


---

# Fix Agent

Responsibilities:

Read GitHub issues.

Workflow:

1. Select issue
2. Analyze problem
3. Implement fix
4. Run tests
5. Run security scan
6. Update issue


Repeat until acceptance criteria are met.


---

# Documentation Agent

Generate:

- README
- API documentation
- Architecture documentation
- User guide
- Release notes


---

# Release Agent

Responsibilities:

- Build Docker image
- Validate deployment
- Create version
- Generate changelog
