import sqlite3, contextlib
from app.config import settings

DB_PATH = settings.database_url.replace("sqlite:///", "")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

@contextlib.contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            page_count INTEGER,
            chunk_count INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS queries (
            id TEXT PRIMARY KEY,
            document_id TEXT,
            mode TEXT DEFAULT 'text',
            transcript TEXT NOT NULL,
            answer TEXT,
            confidence REAL,
            retrieval_latency_ms INTEGER,
            generation_latency_ms INTEGER,
            stt_latency_ms INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS retrieved_chunks (
            id TEXT PRIMARY KEY,
            query_id TEXT NOT NULL,
            chunk_id TEXT,
            rank INTEGER,
            score REAL,
            text TEXT,
            page_number INTEGER
        );
        """)
