from contextlib import asynccontextmanager
import pathlib
import re
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from backend.db import init_db
from backend.detect import search_company_esg, search_similar_greenwash, search_peer_esg, risk_score
from backend.ingest import ingest_esg_doc
from backend.rag import generate_report


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Greenwashing Risk Detector",
    description="AI-powered ESG greenwashing risk analysis",
    lifespan=lifespan,
)

DATA_ESG_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "esg_docs"


def _safe_token(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9]+", "", value.strip())
    return sanitized or "Unknown"


@app.post("/upload/esg")
async def upload_esg(
    company: str = Form(...),
    sector: str = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required.")
    if not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported.")

    content_bytes = await file.read()
    text = content_bytes.decode("utf-8", errors="ignore").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    clean_company = _safe_token(company)
    clean_sector = _safe_token(sector)
    clean_doc_type = _safe_token(doc_type)

    DATA_ESG_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_ESG_DIR / f"{clean_company}_{clean_sector}_{clean_doc_type}.txt"
    out_path.write_text(text, encoding="utf-8")

    ingest_esg_doc(company=company.strip(), sector=sector.strip(), doc_type=doc_type.strip(), text=text)

    return {
        "status": "ok",
        "message": "File uploaded and ingested successfully.",
        "saved_as": out_path.name,
        "company": company.strip(),
        "sector": sector.strip(),
        "doc_type": doc_type.strip(),
        "chars": len(text),
    }


@app.get("/analyze/{company}")
def analyze(company: str):
    company_docs = search_company_esg(company)

    if not company_docs:
        raise HTTPException(
            status_code=404,
            detail=f"No ESG documents found for '{company}'. Ingest data first.",
        )

    combined_claims = " ".join(content for content, _, _ in company_docs)

    greenwash_matches = search_similar_greenwash(combined_claims, k=5)
    score = risk_score(greenwash_matches)

    sector = company_docs[0][1]
    peer_docs = search_peer_esg(company, sector, combined_claims, k=5)

    explanation = generate_report(
        company=company,
        company_claims=company_docs,
        greenwash_matches=greenwash_matches,
        peer_comparisons=peer_docs,
        score=score,
    )

    citations = [
        {"content": content[:300], "similarity": round(sim, 3)}
        for content, sim in greenwash_matches
    ]

    return {
        "company": company,
        "risk_score": score,
        "explanation": explanation,
        "citations": citations,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
