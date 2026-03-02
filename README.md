#  3 Service Word Analysis System

A distributed 3 service system built with FastAPI that accepts text, splits it into chunks, and analyses each chunk in parallel. Built as a learning project on Day 13 of a backend development internship.

## Architecture

```
User → Gateway (8000) → Processor (8001) → Worker (8002)
         gives job_id    splits into chunks   analyses each chunk
```

- **Gateway** — front door. Accepts text from the user, returns a `job_id` instantly, processes work in the background
- **Processor** — coordinator. Receives full text, splits into 50-word chunks, calls Worker for each chunk in parallel using `asyncio.gather`
- **Worker** — does one unit of work. Receives a single chunk, returns word count and most common word
- **shared/logger.py** — structured JSON logger shared across all 3 services

## Project Structure

```
D-13_3-SERVICE/
├── Gateway/
│   ├── main.py
│   ├── .env
│   ├── dockerfile
│   └── requirements.txt
├── Processor/
│   ├── main.py
│   ├── .env
│   ├── dockerfile
│   └── requirements.txt
├── Worker/
│   ├── main.py
│   ├── dockerfile
│   └── requirements.txt
├── shared/
│   └── logger.py
├── docker-compose.yml
└── requirements.txt
```

## Features

- **Background tasks** — Gateway returns `job_id` instantly, work happens in the background
- **Job tracking** — poll `/status/{job_id}` to check progress (queued → processing → completed)
- **Parallel processing** — Processor calls Worker for all chunks simultaneously using `asyncio.gather`
- **Structured JSON logging** — every service logs in JSON format with service name injected automatically
- **Error handling** — distinguishes between unreachable services (503), bad responses (502), and unexpected errors (500)
- **Docker** — all 3 services containerised and orchestrated with Docker Compose

## API

### Gateway — port 8000

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Submit text for analysis. Returns `job_id` instantly |
| GET | `/status/{job_id}` | Check job status and results |
| GET | `/status` | View all jobs |
| GET | `/health` | Health check |

**POST /upload — request body:**
```json
{
  "text": "your text here"
}
```

**POST /upload — response:**
```json
{
  "job_id": "uuid-here",
  "check_status_at": "/status/uuid-here"
}
```

**GET /status/{job_id} — response when completed:**
```json
{
  "status": "completed",
  "Total_Chunks": 6,
  "result": {
    "total Chunks": 6,
    "results": [
      {
        "chunk_index": 0,
        "word_count": 50,
        "most_common_word": "the"
      }
    ]
  }
}
```

## Running with Docker

```bash
docker-compose up --build
```

Then call the API at `http://localhost:8000`

## Running Locally

Run each service in a separate terminal:

```bash
uvicorn Gateway.main:app --port 8000 --reload
uvicorn Processor.main:app --port 8001 --reload
uvicorn Worker.main:app --port 8002 --reload
```

Make sure your `.env` files use `localhost` URLs when running locally:

```
# Gateway/.env
PROCESSOR_URL=http://localhost:8001/process

# Processor/.env
WORKER_URL=http://localhost:8002/work
```

Docker Compose overrides these with internal service name URLs automatically.

## Environment Variables

| Service | Variable | Local | Docker |
|---------|----------|-------|--------|
| Gateway | `PROCESSOR_URL` | `http://localhost:8001/process` | `http://processor:8001/process` |
| Processor | `WORKER_URL` | `http://localhost:8002/work` | `http://worker:8002/work` |
| All | `LOG_ENV` | `local` | `docker` |

When `LOG_ENV=local`, logs are written to a `.log` file. In Docker, logs go to stdout only.

## Tech Stack

- Python 3.11
- FastAPI
- httpx (async HTTP between services)
- Pydantic (request validation)
- python-json-logger (structured logging)
- Docker + Docker Compose