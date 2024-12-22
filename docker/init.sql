DO $$
BEGIN
    -- Create thn user if not exists
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'thn') THEN
        CREATE USER thn WITH PASSWORD 'test123';
    END IF;

    -- Create test user if not exists
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'test') THEN
        CREATE USER test WITH PASSWORD 'test123';
    END IF;
END
$$;

-- Create database if not exists
SELECT 'CREATE DATABASE rag_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'rag_test');

-- Connect to the database
\c rag_test

-- Grant privileges (will not error if already granted)
GRANT ALL PRIVILEGES ON DATABASE rag_test TO thn;
GRANT ALL PRIVILEGES ON DATABASE rag_test TO test;

-- Create extension if not exists (will not error if already exists)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    document_hash TEXT NOT NULL,
    version TEXT,
    processed_at TIMESTAMP,
    source TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

GRANT ALL PRIVILEGES ON SCHEMA raw TO test;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA raw TO test;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw GRANT ALL PRIVILEGES ON TABLES TO test;

GRANT ALL PRIVILEGES ON SCHEMA raw TO thn;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA raw TO thn;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw GRANT ALL PRIVILEGES ON TABLES TO thn;
