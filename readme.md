# Greenwashing Risk Detector

AI-powered ESG risk analysis tool that uses semantic vector search to compare a company's sustainability claims against peer disclosures and verified greenwashing cases. A retrieval-augmented generation (RAG) layer produces evidence-backed explanations to help investors make trustworthy sustainable investment decisions.

## Tech Stack

- **Backend:** Python, FastAPI
- **Frontend:** Three.js + vanilla HTML/CSS/JS (served by FastAPI)
- **Embeddings:** OpenAI `text-embedding-3-large`
- **Vector DB:** Actian VectorAI DB (Docker)
- **LLM:** OpenAI GPT-4o-mini (configurable)

## Prerequisites

- Docker & Docker Compose
- Python 3.11+
- OpenAI API key

## Quick Start

### 1. Environment Setup

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-key
```

### 2. Start the Vector Database

```bash
docker-compose up -d
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Ingest Sample Data

```bash
python -m backend.ingest
```

This reads files from `data/esg_docs/` and `data/greenwash_cases/`, embeds them via OpenAI, and stores them in VectorAI DB.

### 5. Start the Backend

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`. Check health at `http://localhost:8000/health`.

### 6. Open the Frontend

The frontend is served by FastAPI at the root URL:

```
http://localhost:8000/
```

Open it in your browser, enter a company name (e.g., `GreenCorp`, `PetroGlobal`), and click **Analyze**.

## How It Works

1. User enters a company name
2. Backend retrieves the company's ESG document chunks from VectorAI DB
3. Semantic vector search finds the most similar known greenwashing cases
4. Peer ESG disclosures from the same sector are retrieved for comparison
5. A greenwashing risk score (0–100) is computed from similarity to known cases
6. GPT-4o-mini generates an evidence-backed risk assessment with citations
7. Frontend displays the score, explanation, and matched cases

## API

### `GET /analyze/{company}`

Returns a JSON response:

```json
{
  "company": "GreenCorp",
  "risk_score": 42.5,
  "explanation": "...",
  "citations": [
    {"content": "...", "similarity": 0.65}
  ],
  "source_citations": [
    {"title": "...", "url": "https://...", "publisher": "...", "published_at": "..."}
  ]
}
```

### `GET /health`

Returns `{"status": "ok"}`.

### `POST /discover/{company}`

Searches online sources (reports/news), extracts text, and ingests discovered documents into ESG retrieval.

Query params:
- `sector` (optional, default `Unknown`)
- `max_results` (optional, `1-20`, default `8`)

Example:

```bash
curl -X POST "http://localhost:8000/discover/Amazon?sector=ConsumerDiscretionary&max_results=8"
```

### `GET /sources/{company}`

Returns discovered-source metadata already ingested for a company.

Example:

```bash
curl "http://localhost:8000/sources/Amazon?limit=20"
```

## Discovery Configuration

Optional `.env` settings:

```bash
LIVE_DISCOVERY_ENABLED=true
DISCOVERY_MODEL=gpt-4o-mini
```

Notes:
- Discovery relies on OpenAI web-search-capable tooling availability and account quota.
- If discovery cannot run (rate limit/quota/tooling unavailable), it returns `discovered: 0` with an `errors` array.

## Project Structure

```
greenwashing-detection-/
├── backend/
│   ├── main.py          # FastAPI app and API endpoints
│   ├── db.py            # Database connection and table init
│   ├── embed.py         # OpenAI embedding helper
│   ├── ingest.py        # Data ingestion CLI
│   ├── detect.py        # Vector search and risk scoring
│   ├── discovery.py     # Online source discovery and ingestion
│   └── rag.py           # RAG explanation generation
├── frontend/
│   └── index.html       # Self-contained Tailwind frontend
├── data/
│   ├── esg_docs/        # ESG report text files
│   ├── greenwash_cases/ # Known greenwashing case files
│   └── news/            # News coverage (placeholder)
├── .env.example
├── docker-compose.yml
├── requirements.txt
└── readme.md
```

## Adding Your Own Data

**ESG documents:** Place `.txt` files in `data/esg_docs/` with the naming convention `CompanyName_Sector_DocType.txt` (e.g., `Tesla_Automotive_AnnualReport.txt`).

**Greenwashing cases:** Place any `.txt` file in `data/greenwash_cases/` describing a known greenwashing pattern or case.

Then re-run `python -m backend.ingest` to embed and store the new data.
