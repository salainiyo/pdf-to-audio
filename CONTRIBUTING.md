# Contributing

Contributions are welcome.

## Getting started

1. Fork the repository and branch from `main`.
2. Start dependencies with `docker compose up --build`, or work in `backend/`.
3. Keep any local `.env` file untracked.

## Before opening a pull request

- Run `cd backend && pytest -q`.
- Cover new endpoints or worker behavior with tests under `backend/tests/`.
- Do not include real credentials or personal data.
- Update the README and CHANGELOG when behavior changes.
