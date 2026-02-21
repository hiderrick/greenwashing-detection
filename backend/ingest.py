"""
Ingestion script for ESG documents and greenwashing examples.

ESG doc filename convention:  CompanyName_Sector_DocType.txt
Greenwash case files:         any .txt file in data/greenwash_cases/
"""

import os
import pathlib
from hashlib import sha256
from backend.embed import embed_text
from backend.db import get_conn, init_db

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"


def _hash_content(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def ingest_esg_doc(
    company: str,
    sector: str,
    doc_type: str,
    text: str,
    metadata: dict | None = None,
) -> bool:
    metadata = metadata or {}
    content_hash = metadata.get("content_hash") or _hash_content(text)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT 1
        FROM esg_documents
        WHERE content_hash = %s
        LIMIT 1
        """,
        (content_hash,),
    )
    if cur.fetchone():
        cur.close()
        conn.close()
        return False

    emb = embed_text(text)
    cur.execute(
        """
        INSERT INTO esg_documents (
            company, sector, doc_type, content, embedding,
            source_url, source_title, source_publisher,
            published_at, retrieved_at, source_type, retrieval_method, content_hash
        )
        VALUES (
            %s, %s, %s, %s, %s::vector,
            %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        """,
        (
            company,
            sector,
            doc_type,
            text,
            str(emb),
            metadata.get("source_url"),
            metadata.get("source_title"),
            metadata.get("source_publisher"),
            metadata.get("published_at"),
            metadata.get("retrieved_at"),
            metadata.get("source_type", "uploaded"),
            metadata.get("retrieval_method", "manual_upload"),
            content_hash,
        ),
    )
    conn.commit()
    cur.close()
    conn.close()
    return True


def ingest_greenwash_example(text: str):
    emb = embed_text(text)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO greenwash_examples (content, embedding)
        VALUES (%s, %s::vector)
        """,
        (text, str(emb)),
    )
    conn.commit()
    cur.close()
    conn.close()


def ingest_all():
    init_db()

    esg_dir = DATA_DIR / "esg_docs"
    greenwash_dir = DATA_DIR / "greenwash_cases"

    for filepath in sorted(esg_dir.glob("*.txt")):
        parts = filepath.stem.split("_", maxsplit=2)
        if len(parts) < 3:
            print(f"Skipping {filepath.name} — expected CompanyName_Sector_DocType.txt")
            continue
        company, sector, doc_type = parts
        text = filepath.read_text(encoding="utf-8").strip()
        if not text:
            continue
        print(f"Ingesting ESG doc: {company} / {sector} / {doc_type}")
        ingest_esg_doc(company, sector, doc_type, text)

    for filepath in sorted(greenwash_dir.glob("*.txt")):
        text = filepath.read_text(encoding="utf-8").strip()
        if not text:
            continue
        print(f"Ingesting greenwash case: {filepath.name}")
        ingest_greenwash_example(text)

    print("Ingestion complete.")


if __name__ == "__main__":
    ingest_all()
