# Contributing Guidelines

These rules apply to **all contributions**, human or AI.

## Branching & PRs
- AI agents submit PRs into their dedicated branches (e.g., `codex`, `ai-security`).
- Human contributors submit PRs directly into `develop`.
- No contributions go directly into `main`.
- Promotion path:
  - AI branches → develop
  - Human PRs → develop
  - develop → main

## Code Standards
- Use Python 3.11+.
- Follow PEP8 formatting.
- Write clean, maintainable, and well-commented code.
- **No emojis are allowed in code, commit messages, or PR descriptions.**
- Use descriptive names for variables, functions, and branches.

## Commits
- Commit messages should be imperative (e.g., "Add new validator" not "Added new validator").
- Keep commits scoped and focused.

## Testing
- Run `pytest` locally before submitting a PR.
- No failing tests or linting errors.
- Add or update tests when introducing new functionality or fixing bugs.
