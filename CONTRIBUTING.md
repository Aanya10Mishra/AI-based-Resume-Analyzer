# Contributing

Thanks for your interest in contributing to AI-Based Resume Analyzer! This project is intentionally lightweight and rule-based — contributions that improve parsing accuracy, testing, documentation, or developer ergonomics are very welcome.

This document explains how to get started, the preferred workflow, coding guidelines, and the checklist we use for pull requests.

---

## Table of contents
- How to contribute
- Reporting issues
- Branching & pull request workflow
- Code style & quality
- Tests
- Adding or updating keyword lists (skills / roles / education)
- Adding features or larger design changes
- Security & sensitive data
- Code of Conduct
- License

---

## How to contribute
You can contribute by:
- Opening an issue to report a bug or request a feature.
- Submitting a pull request with bug fixes, improvements, tests, or documentation updates.
- Improving the keyword lists in `scripts/parse_resumes.py` or moving them to a configurable file.
- Adding tests, CI, or automation.

If you are new here, a good first PR is to:
- Add a few unit tests for `parse_resumes.parse_resumes_df` and `match_resumes.compute_similarity`.
- Improve README examples (how to run, example input/output).
- Add a small improvement to the UI or the example JDs.

---

## Reporting issues
- Use the GitHub Issues tab.
- When filing a bug, include:
  - A short descriptive title
  - Steps to reproduce
  - Minimal sample input (example resume text or CSV snippet)
  - Expected vs actual behavior
  - Any error logs / stack traces
- For feature requests, describe the use case and a suggested implementation if possible.

---

## Branching & pull request workflow
- Fork the repository and create a branch for your change:
  - `git checkout -b feature/short-description` or `fix/short-description`
- Keep changes small and focused.
- Rebase or merge the latest `main` (or default branch) before opening a PR.
- In your PR description:
  - Explain what you changed and why
  - Reference any related issue (e.g. `Fixes #123`)
  - Include screenshots or example outputs for UI/UX changes
- PRs should have at least one approving review before merge.

---

## Commit messages
Use clear, imperative commit messages. Example:
- `feat: add rapidfuzz-based fuzzy matching option`
- `fix: handle missing resume_text column in parse_resumes`
- `chore: add requirements.txt and pre-commit`

If you want to follow a conventional format, use Conventional Commits (optional).

---

## Code style & quality
- Language: Python 3.8+
- Formatting: Please format Python code with `black` (recommended).
- Linting: `flake8` or similar is encouraged.
- Keep functions small and focused; add docstrings for non-trivial functions.
- Do not commit large data files — keep sample inputs small and synthetic if needed.

Suggested tools (optional):
- black
- isort
- flake8
- pre-commit hooks (recommended)

---

## Tests
- Use `pytest` for unit tests.
- Add tests for parsing, matching logic, and any new modules you add.
- Place tests in `tests/` and keep them small and deterministic.
- CI: If you add GitHub Actions or other CI, please make sure tests run on Python 3.8+.

Example commands:
```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
pip install pytest
pytest
```

---

## Adding or updating keyword lists
The project uses small in-code lists by default:
- `scripts/parse_resumes.py` contains `skills_list`, `education_list`, `roles_list`.

If you update or expand these lists:
- Prefer extracting them to a configurable JSON/YAML file (e.g., `config/keywords.json`) rather than editing code directly.
- Add a loader and a unit test that demonstrates the loader works.
- Consider adding a small script to normalize and deduplicate terms (e.g., title-casing, trimming).

When adding new skills/roles, try to avoid overly generic tokens that cause false positives (for example, short words like "Lead" can be noisy).

---

## Adding features or larger design changes
For larger work (semantic matching, model-backed NER, persistent stores, etc.):
- Open an issue describing the design and tradeoffs before starting work.
- Prefer adding features behind a configuration flag or new endpoint so the lightweight behavior remains the default.
- If adding heavy dependencies (transformers, sentence-transformers), add clear docs explaining the added requirements and optional install extras (e.g., `pip install .[embeddings]`).

Example: if you add an embeddings-based matcher, make it an optional module with fallback to the existing rule-based matcher.

---

## Security & sensitive data
- Treat resume data as sensitive. Do not publish real resumes or personally identifiable information (PII) in commits or issues.
- If you discover a security issue, report it privately (open an issue marked security or contact the maintainers directly if possible). Do not include sensitive details in public issues.
- Uploaded files are temporarily stored — if you change that behavior, update the privacy section in the docs.

---

## Code of Conduct
This project follows a Code of Conduct. Be respectful and constructive. Contributors who violate the Code of Conduct may be removed from the project.

(If your repo does not already contain one, consider adding `CODE_OF_CONDUCT.md` with your preferred policy and contact info.)

---

## License
By contributing, you agree that your contributions will be licensed under the project's license (see LICENSE). If the project uses MIT or Apache-2.0, make sure your contributions are compatible.

---

## Maintainers
- Repo owner / maintainers will review PRs and issues in a reasonable timeframe. If you want to be added as a contributor with more permissions, open an issue to request it.

---

## Quick PR checklist
- [ ] Branch created from latest default branch
- [ ] Descriptive PR title and body
- [ ] Tests added/updated
- [ ] Code formatted with `black`
- [ ] Linting passes
- [ ] No PII or large dataset files committed
- [ ] Documentation / README updated if behavior changes

---

Thank you — your contributions help make this tool more useful for everyone!
