# AGENTS.md

This repository supports AI contributions.  
All AI agents must also follow the [CONTRIBUTING.md](CONTRIBUTING.md) guidelines.

## Codex

### Branching
- All Codex-generated changes must target the `codex` branch.
- Codex PRs should never target `develop` or `main` directly.
- After review, Codex changes are merged into `develop`.

### Development Flow
- The promotion path is: `codex → develop → main`.
- The `issues` branch is reserved for hotfixes.

### Standards
- Respect all rules in [CONTRIBUTING.md](CONTRIBUTING.md).
- Use Python 3.11+.
- Follow PEP8 formatting.
- Commit messages should be in imperative mood (e.g., "Add helper function", not "Added helper function").

### Testing
- Run `pytest` before submitting PRs.
- No failing tests or lint errors allowed.
- Prefer test-driven updates when modifying critical functions.
