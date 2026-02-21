from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from backend.db import init_db
from backend.detect import search_company_esg, search_similar_greenwash, search_peer_esg, risk_score
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
