# Contributing

Thank you for your interest in contributing! This document explains how to file issues, propose changes, and submit pull requests.

## Table of contents
- <a>Code of Conduct</a>
- <a>Getting started</a>
- <a>How to contribute</a>
- <a>Development setup</a>
- <a>Tests and CI</a>
- <a>Branching and PR process</a>
- <a>Commit messages</a>
- <a>Review checklist</a>
- <a>Contact</a>

## Code of Conduct
Please follow the project's Code of Conduct. Be kind and respectful in all interactions.

## Getting started
1. Fork the repository.
2. Clone your fork:
```bash
git clone git@github.com:<your-username>/<repo>.git
cd <repo>
```
3. Create a branch for your work:
```bash
git checkout -b feat/my-feature
```

## How to contribute
- For bug reports or feature requests, open an issue with a clear title and description.
- If you want to propose a change, open a draft PR or link the issue from your PR.
- Small fixes (typos, docs) can be opened as direct PRs against the default branch unless otherwise noted.

## Development setup
We use Python for development. Example steps:
```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```
If the project has additional setup steps (pre-commit hooks, environment variables), document them in README or in this file.

## Tests and CI
Run tests locally before opening a PR:
```bash
pytest
```
The repository uses CI to run linting and tests on PRs. Fix any failing checks before requesting a review.

## Formatting and linting
We use:
- Black for formatting: `black .`
- Flake8 for lint: `flake8`
Run them before committing.

## Branching and Pull Request process
- Branch names: `feat/...`, `fix/...`, `chore/...`
- Open a PR against the main branch (or the currently used default).
- Link related issues in your PR description.
- Add screenshots or logs if relevant.
- One reviewer approval is required (adjust to project policy).

## Commit messages
Use conventional-style commit messages:
```
type(scope): short summary

Longer description (optional)
```
Example:
```
feat(ui): add dark mode toggle
```

## Review checklist (for PR authors)
- [ ] Tests added or updated
- [ ] Linting passes locally
- [ ] Documentation updated where needed
- [ ] PR description is clear and references related issues

## Contact
If you have any questions, open an issue or reach out to the maintainers via GitHub.

Thank you for contributing!
