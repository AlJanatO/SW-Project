# SW-Project

# Breif Description:

This project is a FastAPI and PostgreSQL-based web system that simulates both
vulnerable and secure API behavior to demonstrate common backend security risks
and defensive techniques in modern web applications. It exposes multiple API
services where each request is processed through a FastAPI backend responsible
for validation, query execution, and database logging. The system tracks session
activity, including request frequency and payload data, while intentionally
including vulnerable endpoints to demonstrate issues such as SQL injection,
resource exhaustion, and recursive API abuse. A monitoring middleware layer
analyzes requests in real time to detect abnormal behavior, which is then logged
or flagged. Security is enforced through input validation, parameterized SQL
queries, and rate limiting. Optionally, an LLM-powered RAG pipeline analyzes
incoming requests using past logs to classify threats as safe, suspicious, or
malicious based on context retrieved from the database.

# MVC MOdel
                 ┌──────────────────────┐
                 │      VIEW (API)      │
                 │  FastAPI Routes      │
                 │  (HTTP endpoints)    │
                 └─────────┬────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │        CONTROLLER / SERVICE      │
        │  - business logic               │
        │  - security checks              │
        │  - RAG / LLM calls              │
        └─────────┬────────────┬──────────┘
                  │            │
                  ▼            ▼
     ┌────────────────┐  ┌─────────────────┐
     │     MODEL      │  │   SECURITY LAYER │
     │ PostgreSQL DB  │  │ middleware + logs│
     │ queries/data   │  │ threat detection  │
     └────────────────┘  └─────────────────┘


# Download dependencies

pip install uvicorn fastapi psycopg2-binary python-dotenv