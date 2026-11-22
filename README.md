# PDF-to-Audio Async API

[![PDF-TO-AUDIO BACKEND CI](https://github.com/salainiyo/pdf-to-audio/actions/workflows/ci.yaml/badge.svg)](https://github.com/salainiyo/pdf-to-audio/actions/workflows/ci.yaml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An asynchronous REST API that converts PDF documents into audio files. Built
to master background task processing, message brokering and async Python.

## Architecture

```text
client ──► FastAPI (upload) ──► Redis ──► Celery worker
   │             │                            │
   │             └──► task id / status        ├──► pypdf text extraction
   │                                          └──► gTTS audio synthesis
   └──────────── poll /result ◄──────────── audio file
```

- **API:** FastAPI (`backend/main.py`, `backend/api/`)
- **Task queue:** Celery (`backend/api/worker.py`)
- **Broker / result backend:** Redis
- **Storage:** SQLModel/SQLAlchemy database with Alembic migrations
- **Containerization:** Docker Compose

## Quick start

```bash
docker compose up --build
```

API docs: `http://localhost:8000/docs`.

Local development:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## API overview

- `POST /` — upload a PDF and receive a task id.
- `GET /status/{task_id}` — poll Celery task state.
- `GET /result/{task_id}` — download the generated audio.
- Authentication and rate limiting live in `backend/api/auth.py` and
  `backend/core/rate_limiting.py`.

## Configuration

Runtime settings are read from environment variables and `.env` (git-ignored).
Never commit real secrets or API keys. See the workflow file for the CI-only
test values; they are placeholders, not production credentials.

## Tests

```bash
cd backend && pytest -q
```

CI runs the same suite on every push and pull request to `main`.

## Roadmap

- Add structured API response schemas.
- Add end-to-end tests for the full upload → poll → download flow.
- Expand language and voice options for synthesis.

See [CHANGELOG.md](CHANGELOG.md), [CONTRIBUTING.md](CONTRIBUTING.md) and
[SECURITY.md](SECURITY.md).
