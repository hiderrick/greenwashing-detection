# Greenwashing Risk Detector

This project helps verify (or expose) sustainability claims for companies.

It combines:
- Live source discovery (AI Search workflow web search)
- Vector similarity search against ESG docs and known greenwashing examples
- RAG-based explanation generation with citations

## Objective

Given a company, estimate greenwashing risk by comparing its claims with:
- Known greenwashing patterns
- Same-sector peer disclosures
- Newly discovered external sources (reports/news)

## Architecture

- Frontend: Single-page app (`frontend/index.html`) for analyze/upload flows
- API: FastAPI service (`backend/main.py`)
- Retrieval + scoring: vector search and risk logic (`backend/detect.py`)
- Discovery: OpenAI live search + source ingestion (`backend/discovery.py`)
- LLM reasoning: report generation (`backend/rag.py`)
- Embeddings: OpenAI `text-embedding-3-large` with deterministic fallback (`backend/embed.py`)
- Database: Actian VectorAI DB over PostgreSQL wire protocol (`backend/db.py`)

VectorAI DB GitHub:
https://github.com/hackmamba-io/actian-vectorAI-db-beta

### Architecture Flow (Mermaid.js)

```will add PNG later
```

## Workflow

### 1. AI Search + Discovery Workflow

```will add PNG later
```

### 2. RAG Analysis Workflow

```will add PNG later
```

## API Endpoints

- `POST /discover/{company}`: Live discovery and ingestion
- `GET /analyze/{company}`: Risk score + RAG explanation + citations
- `POST /upload` or `POST /upload/esg`: Upload `.txt`/`.pdf` ESG document
- `GET /sources/{company}`: List ingested discovered sources
- `GET /health`: Health check

## Quick Start

1. Create env file and set credentials:

```bash
cp .env.example .env
```

Required vars (example):

```bash
OPENAI_API_KEY=<KEY_GOES_HERE>
VECTORAI_HOST=localhost
VECTORAI_PORT=5433
VECTORAI_DB=vectordb
VECTORAI_USER=admin
VECTORAI_PASSWORD=admin
```

2. Start VectorAI DB:

```bash
docker-compose up -d
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Ingest local seed data:

```bash
python -m backend.ingest
```

5. Run API:

```bash
uvicorn backend.main:app --reload
```

6. Open app:

- `http://localhost:8000/`

## Discovery Controls

Optional environment variables:

```bash
LIVE_DISCOVERY_ENABLED=true
DISCOVERY_MODEL=gpt-4o-mini
DISCOVERY_TIME_BUDGET_SEC=35
DISCOVERY_SOURCE_TIMEOUT_SEC=8
DISCOVERY_OPENAI_TIMEOUT_SEC=12
DISCOVERY_OPENAI_MAX_ATTEMPTS=2
```

These controls prevent discovery from hanging and ensure bounded response time.
