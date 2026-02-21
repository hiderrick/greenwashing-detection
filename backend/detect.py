from backend.db import get_conn
from backend.embed import embed_text


def search_similar_greenwash(text: str, k: int = 5) -> list[tuple[str, float]]:
    """Return top-k greenwash examples most similar to the query text."""
    emb = embed_text(text)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT content, 1 - (embedding <=> %s::vector) AS similarity
        FROM greenwash_examples
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (str(emb), str(emb), k),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def search_company_esg(company: str, k: int = 8) -> list[tuple[str, str, str, str | None, str | None, str | None, str | None]]:
    """Return the company's own ESG document chunks."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT content, sector, doc_type, source_url, source_title, source_publisher, published_at
        FROM esg_documents
        WHERE LOWER(company) = LOWER(%s)
        ORDER BY id DESC
        LIMIT %s
        """,
        (company, k),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def search_peer_esg(company: str, sector: str, text: str, k: int = 5) -> list[tuple[str, str, float]]:
    """Return ESG docs from same-sector peers, ranked by similarity to the query text."""
    emb = embed_text(text)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT content, company, 1 - (embedding <=> %s::vector) AS similarity
        FROM esg_documents
        WHERE LOWER(sector) = LOWER(%s)
          AND LOWER(company) != LOWER(%s)
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (str(emb), sector, company, str(emb), k),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def risk_score(similarities: list[tuple[str, float]]) -> float:
    """Compute a 0–100 greenwashing risk score from similarity matches."""
    if not similarities:
        return 0.0
    avg_sim = sum(s for _, s in similarities) / len(similarities)
    return round(max(0.0, min(100.0, avg_sim * 100)), 2)
