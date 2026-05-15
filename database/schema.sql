CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    ip TEXT NOT NULL,
    user_agent TEXT,
    first_seen TIMESTAMP NOT NULL DEFAULT NOW(),
    last_seen TIMESTAMP NOT NULL DEFAULT NOW(),
    request_count INT NOT NULL DEFAULT 0,
    anomaly_count INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
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
);

CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    request_id INT REFERENCES requests(id) ON DELETE SET NULL,
    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    anomaly_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    action TEXT,
    rule TEXT,
    explanation TEXT NOT NULL,
    recommendation TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_requests_session_id ON requests(session_id);
CREATE INDEX IF NOT EXISTS idx_requests_created_at ON requests(created_at);
CREATE INDEX IF NOT EXISTS idx_requests_anomaly_type ON requests(anomaly_type);
CREATE INDEX IF NOT EXISTS idx_requests_analysis_source ON requests(analysis_source);
CREATE INDEX IF NOT EXISTS idx_requests_payload_embedding ON requests USING GIN(payload_embedding);

CREATE INDEX IF NOT EXISTS idx_anomalies_session_id ON anomalies(session_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_created_at ON anomalies(created_at);
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);
CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies(anomaly_type);
