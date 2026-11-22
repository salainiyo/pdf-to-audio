# Security Policy

Do not include real credentials, keys or personal data in issues or pull
requests. CI test secrets in workflow files are placeholders only.

## Reporting a vulnerability

Use GitHub's "Report a vulnerability" feature on the repository's Security tab.
Include the affected file, impact and a minimal reproduction.

## Credential handling

- Keep secrets in a local `.env`, which is git-ignored.
- Rotate any credential that may have been exposed.
- Do not expose Redis, database or signing keys in logs or test fixtures.
