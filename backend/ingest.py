"""
Ingestion script for ESG documents and greenwashing examples.

ESG doc filename convention:  CompanyName_Sector_DocType.txt
Greenwash case files:         any .txt file in data/greenwash_cases/
"""

import os
import pathlib
from backend.embed import embed_text
from backend.db import get_conn, init_db

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"


def ingest_esg_doc(company: str, sector: str, doc_type: str, text: str):
    emb = embed_text(text)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO esg_documents (company, sector, doc_type, content, embedding)
        VALUES (%s, %s, %s, %s, %s::vector)
        """,
        (company, sector, doc_type, text, str(emb)),
    )
    conn.commit()
    cur.close()
    conn.close()


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
