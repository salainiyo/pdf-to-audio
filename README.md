# PDF-to-Audio Async API

An asynchronous REST API that converts PDF documents into audio files. Built to master background task processing, message brokering, and async Python.

## Architecture
- **API:** FastAPI
- **Task Queue:** Celery
- **Message Broker:** Redis
- **Containerization:** Docker & Docker Compose

## Key Features
- **Asynchronous processing:** Upload a PDF and receive a task ID immediately without blocking the main thread.
- **Status polling:** Check task status and retrieve the final audio file once processing is complete.
- **Fully containerized:** One-command setup (`docker-compose up`) for local development and deployment.
