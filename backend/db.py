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
            embedding VECTOR(3072)
        );
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
