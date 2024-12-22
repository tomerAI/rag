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