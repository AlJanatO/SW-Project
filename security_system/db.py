import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    # Database settings come from .env so local passwords are not stored in project files.
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )


def run_sql(query, params=None):
    # All database access goes through this helper so parameterized queries stay consistent.
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
    # Startup creates the tables needed for the demo. database/schema.sql mirrors this structure.
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
            analysis_source TEXT DEFAULT 'rule-based',
            llm_used BOOLEAN NOT NULL DEFAULT FALSE,
            payload_embedding JSONB DEFAULT '[]'::jsonb,
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
            action TEXT,
            rule TEXT,
            explanation TEXT NOT NULL,
            recommendation TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """,
        "ALTER TABLE requests ADD COLUMN IF NOT EXISTS analysis_source TEXT DEFAULT 'rule-based'",
        "ALTER TABLE requests ADD COLUMN IF NOT EXISTS llm_used BOOLEAN NOT NULL DEFAULT FALSE",
        "ALTER TABLE requests ADD COLUMN IF NOT EXISTS payload_embedding JSONB DEFAULT '[]'::jsonb",
        "ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS action TEXT",
        "ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS rule TEXT",
        "ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS recommendation TEXT",
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_requests_session_id'
            ) THEN
                ALTER TABLE requests
                ADD CONSTRAINT fk_requests_session_id
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                ON DELETE CASCADE NOT VALID;
            END IF;
        END $$;
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_anomalies_session_id'
            ) THEN
                ALTER TABLE anomalies
                ADD CONSTRAINT fk_anomalies_session_id
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                ON DELETE CASCADE NOT VALID;
            END IF;
        END $$;
        """,
        "CREATE INDEX IF NOT EXISTS idx_requests_session_id ON requests(session_id)",
        "CREATE INDEX IF NOT EXISTS idx_requests_created_at ON requests(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_requests_anomaly_type ON requests(anomaly_type)",
        "CREATE INDEX IF NOT EXISTS idx_requests_analysis_source ON requests(analysis_source)",
        "CREATE INDEX IF NOT EXISTS idx_requests_payload_embedding ON requests USING GIN(payload_embedding)",
        "CREATE INDEX IF NOT EXISTS idx_anomalies_session_id ON anomalies(session_id)",
        "CREATE INDEX IF NOT EXISTS idx_anomalies_created_at ON anomalies(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity)",
        "CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies(anomaly_type)",
    ]

    for statement in statements:
        run_sql(statement)