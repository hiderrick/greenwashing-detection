import json
import os
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from html import unescape
from io import BytesIO
from typing import Any

from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError
from pypdf import PdfReader

from backend.ingest import ingest_esg_doc


@dataclass
class SourceCandidate:
    title: str
    url: str
    snippet: str
    publisher: str
    published_at: str | None
    doc_type: str
    source_type: str
    relevance: float


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _safe_json_array(text: str) -> list[dict]:
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return []
    try:
        parsed = json.loads(text[start : end + 1])
    except Exception:
        return []
    return parsed if isinstance(parsed, list) else []


def _clean_text(value: str) -> str:
    no_script = re.sub(r"(?is)<(script|style).*?>.*?</\\1>", " ", value)
    no_tags = re.sub(r"(?s)<[^>]+>", " ", no_script)
    no_entities = unescape(no_tags)
    return re.sub(r"\s+", " ", no_entities).strip()


def _extract_pdf_text(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    pages = []
    for page in reader.pages:
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(text)
    return "\n\n".join(pages).strip()


def _fetch_source_text(url: str, timeout_sec: int = 20) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "greenwashing-detector/1.0 (+research; contact: local-app)",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout_sec) as res:
        raw = res.read()
        ctype = (res.headers.get("Content-Type") or "").lower()

    if "pdf" in ctype or url.lower().endswith(".pdf"):
        try:
            return _extract_pdf_text(raw)
        except Exception:
            return ""

    text = raw.decode("utf-8", errors="ignore")
    return _clean_text(text)


def _build_queries(company: str) -> list[str]:
    return [
        f"{company} sustainability report pdf",
        f"{company} ESG report",
        f"{company} climate report",
        f"{company} environmental controversy news",
        f"{company} emissions investigation",
    ]


def _float_env(name: str, default: float) -> float:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def _int_env(name: str, default: int) -> int:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _domain_from_url(url: str) -> str:
    try:
        host = urllib.parse.urlsplit(url).netloc.lower()
    except Exception:
        return "Unknown"
    return host or "Unknown"


def _extract_urls_from_text(text: str) -> list[str]:
    matches = re.findall(r"https?://[^\s<>()\"']+", text or "")
    cleaned = [m.rstrip(".,);:!?") for m in matches]
    out: list[str] = []
    seen: set[str] = set()
    for url in cleaned:
        if url in seen:
            continue
        seen.add(url)
        out.append(url)
    return out


def _collect_urls_recursive(value: Any, out: list[str]) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            if k in {"url", "href", "source_url"} and isinstance(v, str) and v.startswith(("http://", "https://")):
                out.append(v)
            _collect_urls_recursive(v, out)
        return
    if isinstance(value, list):
        for item in value:
            _collect_urls_recursive(item, out)
        return
    if isinstance(value, str):
        out.extend(_extract_urls_from_text(value))


def _urls_to_candidates(urls: list[str], company: str) -> list[SourceCandidate]:
    out: list[SourceCandidate] = []
    for idx, url in enumerate(urls):
        domain = _domain_from_url(url)
        out.append(
            SourceCandidate(
                title=f"{company} source {idx + 1}",
                url=url,
                snippet="Discovered via OpenAI web search.",
                publisher=domain,
                published_at=None,
                doc_type="Other",
                source_type="third_party",
                relevance=max(0.0, 0.8 - idx * 0.02),
            )
        )
    return out


def _search_with_openai(
    company: str,
    queries: list[str],
    max_results: int,
    request_timeout_sec: float = 12.0,
    max_attempts: int = 2,
) -> list[SourceCandidate]:
    timeout_sec = max(1.0, request_timeout_sec)
    attempts = max(1, min(max_attempts, 3))
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=timeout_sec,
        max_retries=0,
    )
    model = os.getenv("DISCOVERY_MODEL", "gpt-4o-mini")
    prompt = f"""
Find recent, high-quality sources for ESG and greenwashing analysis for company: {company}.
Include official reports, reputable news, and third-party assessments.
Use these search intents:
{chr(10).join(f"- {q}" for q in queries)}

Return only valid JSON as an array of up to {max_results} objects with keys:
title, url, snippet, publisher, published_at, doc_type, source_type, relevance

doc_type must be one of: ESGReport, AnnualReport, SustainabilityReport, ClimateReport, NewsArticle, Other
source_type must be one of: company_site, news, regulatory, third_party
relevance must be a number from 0 to 1.
"""

    response = None
    last_err: Exception | None = None
    for attempt in range(attempts):
        try:
            response = client.responses.create(
                model=model,
                tools=[{"type": "web_search_preview"}],
                input=prompt,
                temperature=0.0,
                timeout=timeout_sec,
            )
            break
        except (RateLimitError, APITimeoutError, APIConnectionError) as exc:
            last_err = exc
            if attempt == attempts - 1:
                raise
            time.sleep(min(2.0, 0.75 * (attempt + 1)))
    if response is None and last_err is not None:
        raise last_err
    if response is None:
        return []

    rows = _safe_json_array(response.output_text or "")
    out: list[SourceCandidate] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        url = str(row.get("url") or "").strip()
        if not url.startswith(("http://", "https://")):
            continue
        out.append(
            SourceCandidate(
                title=str(row.get("title") or "Untitled").strip(),
                url=url,
                snippet=str(row.get("snippet") or "").strip(),
                publisher=str(row.get("publisher") or "Unknown").strip(),
                published_at=(str(row.get("published_at")).strip() or None) if row.get("published_at") else None,
                doc_type=str(row.get("doc_type") or "Other").strip(),
                source_type=str(row.get("source_type") or "third_party").strip(),
                relevance=float(row.get("relevance") or 0.0),
            )
        )
    if out:
        return out

    # Fallback: if model returns prose/citations instead of JSON, collect URLs directly.
    discovered_urls = _extract_urls_from_text(response.output_text or "")
    try:
        dump = response.model_dump()
        _collect_urls_recursive(dump, discovered_urls)
    except Exception:
        pass
    deduped_urls: list[str] = []
    seen: set[str] = set()
    for url in discovered_urls:
        if url in seen or not url.startswith(("http://", "https://")):
            continue
        seen.add(url)
        deduped_urls.append(url)
    return _urls_to_candidates(deduped_urls[:max_results], company=company)


def _normalize_doc_type(value: str) -> str:
    allowed = {
        "ESGReport",
        "AnnualReport",
        "SustainabilityReport",
        "ClimateReport",
        "NewsArticle",
        "Other",
    }
    return value if value in allowed else "Other"


def _dedupe_candidates(candidates: list[SourceCandidate]) -> list[SourceCandidate]:
    seen: set[str] = set()
    deduped: list[SourceCandidate] = []
    for c in sorted(candidates, key=lambda x: x.relevance, reverse=True):
        norm = urllib.parse.urlsplit(c.url)._replace(fragment="").geturl().rstrip("/")
        if norm in seen:
            continue
        seen.add(norm)
        deduped.append(c)
    return deduped


def discover_and_ingest(
    company: str,
    sector: str = "Unknown",
    max_results: int = 8,
) -> dict:
    started = time.monotonic()
    time_budget_sec = _float_env("DISCOVERY_TIME_BUDGET_SEC", 35.0)
    per_source_timeout_sec = _int_env("DISCOVERY_SOURCE_TIMEOUT_SEC", 8)
    openai_timeout_sec = _float_env("DISCOVERY_OPENAI_TIMEOUT_SEC", 12.0)
    openai_max_attempts = _int_env("DISCOVERY_OPENAI_MAX_ATTEMPTS", 2)

    if os.getenv("LIVE_DISCOVERY_ENABLED", "true").lower() != "true":
        return {
            "status": "disabled",
            "company": company,
            "discovered": 0,
            "ingested": 0,
            "errors": ["LIVE_DISCOVERY_ENABLED is false."],
            "sources": [],
        }

    queries = _build_queries(company)
    raw_candidates: list[SourceCandidate] = []
    errors: list[str] = []

    # Primary: OpenAI web search via gpt-4o-mini + web_search_preview tool.
    try:
        elapsed = time.monotonic() - started
        remaining_budget = max(1.0, time_budget_sec - elapsed)
        if remaining_budget <= 2.0:
            errors.append("Discovery time budget too low to run OpenAI live search.")
        else:
            search_timeout_sec = min(max(3.0, remaining_budget - 2.0), max(3.0, openai_timeout_sec))
            raw_candidates.extend(
                _search_with_openai(
                    company,
                    queries=queries,
                    max_results=max_results * 2,
                    request_timeout_sec=search_timeout_sec,
                    max_attempts=openai_max_attempts,
                )
            )
    except Exception as exc:
        details = str(exc).strip()
        if details:
            errors.append(f"OpenAI discovery unavailable: {type(exc).__name__} - {details}")
        else:
            errors.append(f"OpenAI discovery unavailable: {type(exc).__name__}")

    # Keep candidate set tight so discovery finishes quickly.
    candidates = _dedupe_candidates(raw_candidates)[: max_results]
    ingested = 0
    sources: list[dict] = []

    for candidate in candidates:
        if (time.monotonic() - started) > time_budget_sec:
            errors.append(f"Discovery time budget reached ({time_budget_sec:.0f}s).")
            break
        try:
            extracted = _fetch_source_text(candidate.url, timeout_sec=per_source_timeout_sec)
        except Exception:
            continue
        if len(extracted) < 240:
            continue

        trimmed = extracted[:15000]
        body = f"{candidate.title}\n\n{candidate.snippet}\n\n{trimmed}".strip()
        inserted = ingest_esg_doc(
            company=company,
            sector=sector,
            doc_type=_normalize_doc_type(candidate.doc_type),
            text=body,
            metadata={
                "source_url": candidate.url,
                "source_title": candidate.title,
                "source_publisher": candidate.publisher,
                "published_at": candidate.published_at,
                "retrieved_at": _now_iso(),
                "source_type": candidate.source_type,
                "retrieval_method": "live_discovery",
            },
        )
        if inserted:
            ingested += 1
        sources.append(
            {
                "title": candidate.title,
                "url": candidate.url,
                "publisher": candidate.publisher,
                "published_at": candidate.published_at,
                "doc_type": _normalize_doc_type(candidate.doc_type),
                "source_type": candidate.source_type,
                "relevance": round(candidate.relevance, 3),
                "inserted": inserted,
            }
        )

    return {
        "status": "ok",
        "company": company,
        "discovered": len(candidates),
        "ingested": ingested,
        "errors": errors,
        "sources": sources,
        "queries": queries,
        "duration_sec": round(time.monotonic() - started, 2),
    }
