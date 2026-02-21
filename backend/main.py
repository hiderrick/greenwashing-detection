from contextlib import asynccontextmanager
from io import BytesIO
import pathlib
import re
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader
from backend.db import get_conn
from backend.db import init_db
from backend.detect import search_company_esg, search_similar_greenwash, search_peer_esg, risk_score
from backend.discovery import discover_and_ingest
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
FRONTEND_DIR = pathlib.Path(__file__).resolve().parent.parent / "frontend"
MAX_UPLOAD_BYTES = 15 * 1024 * 1024
DEFAULT_SECTOR = "Unknown"
DEFAULT_DOC_TYPE = "ESGReport"


def _safe_token(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9]+", "", value.strip())
    return sanitized or "Unknown"


def _clean_or_default(value: str | None, default: str) -> str:
    cleaned = (value or "").strip()
    return cleaned or default


def _extract_text_from_pdf(content_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content_bytes))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid PDF file.")

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            raise HTTPException(status_code=400, detail="Encrypted PDF files are not supported.")

    pages: list[str] = []
    for page in reader.pages:
        page_text = (page.extract_text() or "").strip()
        if page_text:
            pages.append(page_text)

    text = "\n\n".join(pages).strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail=(
                "No extractable text found in PDF. "
                "Please upload a text-based PDF (not image-only/scanned)."
            ),
        )
    return text


def _extract_uploaded_text(filename: str, content_bytes: bytes) -> tuple[str, str]:
    lower_name = filename.lower()
    if lower_name.endswith(".txt"):
        text = content_bytes.decode("utf-8", errors="ignore").strip()
        source_type = "txt"
    elif lower_name.endswith(".pdf"):
        text = _extract_text_from_pdf(content_bytes)
        source_type = "pdf"
    else:
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported.")

    if not text:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    return text, source_type


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


# Keep both routes for compatibility with older/newer frontend versions.
@app.post("/upload")
@app.post("/upload/esg")
async def upload_esg(
    company: str = Form(...),
    sector: str | None = Form(None),
    doc_type: str | None = Form(None),
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required.")
    company_clean = company.strip()
    if not company_clean:
        raise HTTPException(status_code=400, detail="Company is required.")

    content_bytes = await file.read()
    if len(content_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Max size is 15 MB.")

    text, source_type = _extract_uploaded_text(file.filename, content_bytes)
    sector_clean = _clean_or_default(sector, DEFAULT_SECTOR)
    doc_type_clean = _clean_or_default(doc_type, DEFAULT_DOC_TYPE)

    clean_company = _safe_token(company_clean)
    clean_sector = _safe_token(sector_clean)
    clean_doc_type = _safe_token(doc_type_clean)

    DATA_ESG_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_ESG_DIR / f"{clean_company}_{clean_sector}_{clean_doc_type}.txt"
    out_path.write_text(text, encoding="utf-8")

    ingest_esg_doc(company=company_clean, sector=sector_clean, doc_type=doc_type_clean, text=text)

    return {
        "status": "ok",
        "message": "File uploaded and ingested successfully.",
        "saved_as": out_path.name,
        "company": company_clean,
        "sector": sector_clean,
        "doc_type": doc_type_clean,
        "source_type": source_type,
        "chars": len(text),
    }


@app.get("/analyze/{company}")
def analyze(company: str):
    company_docs = search_company_esg(company)

    if not company_docs:
        return {
            "company": company,
            "status": "no_data",
            "risk_score": 0.0,
            "explanation": (
                f"No ESG documents are available for '{company}' yet. "
                "Try enabling live discovery again or upload a report manually."
            ),
            "citations": [],
            "source_citations": [],
        }

    combined_claims = " ".join(content for content, *_ in company_docs)

    greenwash_matches = search_similar_greenwash(combined_claims, k=5)
    score = risk_score(greenwash_matches)

    sector = company_docs[0][1]
    peer_docs = search_peer_esg(company, sector, combined_claims, k=5)

    company_claims_for_report = [(content, sector, doc_type) for content, sector, doc_type, *_ in company_docs]

    explanation = generate_report(
        company=company,
        company_claims=company_claims_for_report,
        greenwash_matches=greenwash_matches,
        peer_comparisons=peer_docs,
        score=score,
    )

    citations = [
        {"content": content[:300], "similarity": round(sim, 3)}
        for content, sim in greenwash_matches
    ]

    discovered_sources = []
    seen_urls: set[str] = set()
    for _content, _sector, _doc_type, source_url, source_title, source_publisher, published_at in company_docs:
        if not source_url or source_url in seen_urls:
            continue
        seen_urls.add(source_url)
        discovered_sources.append(
            {
                "title": source_title or "Untitled source",
                "url": source_url,
                "publisher": source_publisher,
                "published_at": published_at,
            }
        )

    return {
        "company": company,
        "risk_score": score,
        "explanation": explanation,
        "citations": citations,
        "source_citations": discovered_sources,
    }


@app.post("/discover/{company}")
def discover_company(
    company: str,
    sector: str = Query(DEFAULT_SECTOR),
    max_results: int = Query(8, ge=1, le=20),
):
    company_clean = company.strip()
    if not company_clean:
        raise HTTPException(status_code=400, detail="Company is required.")
    result = discover_and_ingest(company=company_clean, sector=sector.strip() or DEFAULT_SECTOR, max_results=max_results)
    if result.get("status") == "disabled":
        raise HTTPException(status_code=503, detail="Live discovery is disabled. Set LIVE_DISCOVERY_ENABLED=true.")
    return result


@app.get("/sources/{company}")
def company_sources(company: str, limit: int = Query(20, ge=1, le=100)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT source_title, source_url, source_publisher, published_at, doc_type, source_type, retrieval_method
        FROM esg_documents
        WHERE LOWER(company) = LOWER(%s)
          AND source_url IS NOT NULL
        ORDER BY id DESC
        LIMIT %s
        """,
        (company.strip(), limit),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {
        "company": company,
        "sources": [
            {
                "title": title,
                "url": url,
                "publisher": publisher,
                "published_at": published_at,
                "doc_type": doc_type,
                "source_type": source_type,
                "retrieval_method": retrieval_method,
            }
            for title, url, publisher, published_at, doc_type, source_type, retrieval_method in rows
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok"}
