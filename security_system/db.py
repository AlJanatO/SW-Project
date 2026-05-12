import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )


def run_sql(query, params=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, params or ())

    try:
        result = cur.fetchall()
    except Exception:
        result = []

    conn.commit()
    cur.close()
    conn.close()

    return result


def ensure_schema():
    statements = [
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            session_id TEXT UNIQUE NOT NULL,
            ip TEXT NOT NULL,
            user_agent TEXT,
            first_seen TIMESTAMP NOT NULL DEFAULT NOW(),
            last_seen TIMESTAMP NOT NULL DEFAULT NOW(),
            request_count INT NOT NULL DEFAULT 0,
            anomaly_count INT NOT NULL DEFAULT 0
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS requests (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            ip TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            method TEXT NOT NULL,
            payload JSONB DEFAULT '{}'::jsonb,
            status_code INT,
            anomaly_type TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS anomalies (
            id SERIAL PRIMARY KEY,
            request_id INT REFERENCES requests(id) ON DELETE SET NULL,
            session_id TEXT NOT NULL,
            anomaly_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            explanation TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            payload JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """,
    ]

    for statement in statements:
        run_sql(statement)