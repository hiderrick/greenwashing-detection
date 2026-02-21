import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_conn():
    return psycopg2.connect(
        host=os.getenv("VECTORAI_HOST", "localhost"),
        port=int(os.getenv("VECTORAI_PORT", "5432")),
        database=os.getenv("VECTORAI_DB", "vectordb"),
        user=os.getenv("VECTORAI_USER", "admin"),
        password=os.getenv("VECTORAI_PASSWORD", "admin"),
    )


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS esg_documents (
            id SERIAL PRIMARY KEY,
            company TEXT,
            sector TEXT,
            doc_type TEXT,
            content TEXT,
            embedding VECTOR(3072),
            source_url TEXT,
            source_title TEXT,
            source_publisher TEXT,
            published_at TEXT,
            retrieved_at TEXT,
            source_type TEXT,
            retrieval_method TEXT,
            content_hash TEXT
        );
        """
    )
    # Backfill compatibility for existing databases created before metadata columns existed.
    for ddl in (
        "ALTER TABLE esg_documents ADD COLUMN IF NOT EXISTS source_url TEXT;",
        "ALTER TABLE esg_documents ADD COLUMN IF NOT EXISTS source_title TEXT;",
        "ALTER TABLE esg_documents ADD COLUMN IF NOT EXISTS source_publisher TEXT;",
        "ALTER TABLE esg_documents ADD COLUMN IF NOT EXISTS published_at TEXT;",
        "ALTER TABLE esg_documents ADD COLUMN IF NOT EXISTS retrieved_at TEXT;",
        "ALTER TABLE esg_documents ADD COLUMN IF NOT EXISTS source_type TEXT;",
        "ALTER TABLE esg_documents ADD COLUMN IF NOT EXISTS retrieval_method TEXT;",
        "ALTER TABLE esg_documents ADD COLUMN IF NOT EXISTS content_hash TEXT;",
    ):
        cur.execute(ddl)
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_esg_documents_content_hash
        ON esg_documents (content_hash);
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS greenwash_examples (
            id SERIAL PRIMARY KEY,
            content TEXT,
            embedding VECTOR(3072)
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()
