-- First set the variables
\set DBT_USER `echo "$DBT_USER"`
\set DBT_PASSWORD `echo "$DBT_PASSWORD"`
\set DBT_DATABASE `echo "$DBT_DATABASE"`
\set DBT_SCHEMA `echo "$DBT_SCHEMA"`

-- Store variables in temporary tables for validation and later use
CREATE TEMPORARY TABLE IF NOT EXISTS temp_vars (
    var_name text PRIMARY KEY,
    var_value text
);

INSERT INTO temp_vars VALUES 
    ('dbt_user', :'DBT_USER'),
    ('dbt_password', :'DBT_PASSWORD'),
    ('dbt_database', :'DBT_DATABASE'),
    ('dbt_schema', :'DBT_SCHEMA')
ON CONFLICT (var_name) DO UPDATE SET var_value = EXCLUDED.var_value;

-- Validate variables
DO $$
DECLARE
    v_user text;
    v_password text;
    v_database text;
    v_schema text;
BEGIN
    SELECT var_value INTO v_user FROM temp_vars WHERE var_name = 'dbt_user';
    SELECT var_value INTO v_password FROM temp_vars WHERE var_name = 'dbt_password';
    SELECT var_value INTO v_database FROM temp_vars WHERE var_name = 'dbt_database';
    SELECT var_value INTO v_schema FROM temp_vars WHERE var_name = 'dbt_schema';

    IF v_user IS NULL OR v_user = '' THEN
        RAISE EXCEPTION 'DBT_USER environment variable is not set';
    END IF;
    IF v_password IS NULL OR v_password = '' THEN
        RAISE EXCEPTION 'DBT_PASSWORD environment variable is not set';
    END IF;
    IF v_database IS NULL OR v_database = '' THEN
        RAISE EXCEPTION 'DBT_DATABASE environment variable is not set';
    END IF;
    IF v_schema IS NULL OR v_schema = '' THEN
        RAISE EXCEPTION 'DBT_SCHEMA environment variable is not set';
    END IF;
END
$$;

-- Create DBT user
DO $$
DECLARE
    v_user text;
    v_password text;
BEGIN
    SELECT var_value INTO v_user FROM temp_vars WHERE var_name = 'dbt_user';
    SELECT var_value INTO v_password FROM temp_vars WHERE var_name = 'dbt_password';

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = v_user) THEN
        EXECUTE format('CREATE USER %I WITH PASSWORD %L', v_user, v_password);
    END IF;
END
$$;

-- Create database (outside of DO block)
SELECT format('CREATE DATABASE %I', var_value) 
FROM temp_vars 
WHERE var_name = 'dbt_database' 
AND NOT EXISTS (
    SELECT FROM pg_database WHERE datname = var_value
)\gexec

-- Connect to the DBT database
\c :DBT_DATABASE

-- Recreate temporary table in new connection
CREATE TEMPORARY TABLE IF NOT EXISTS temp_vars (
    var_name text PRIMARY KEY,
    var_value text
);

INSERT INTO temp_vars VALUES 
    ('dbt_user', :'DBT_USER'),
    ('dbt_password', :'DBT_PASSWORD'),
    ('dbt_database', :'DBT_DATABASE'),
    ('dbt_schema', :'DBT_SCHEMA')
ON CONFLICT (var_name) DO UPDATE SET var_value = EXCLUDED.var_value;

-- Create extensions and schema
CREATE EXTENSION IF NOT EXISTS vector;

DO $$
DECLARE
    v_user text;
    v_database text;
    v_schema text;
BEGIN
    SELECT var_value INTO v_user FROM temp_vars WHERE var_name = 'dbt_user';
    SELECT var_value INTO v_database FROM temp_vars WHERE var_name = 'dbt_database';
    SELECT var_value INTO v_schema FROM temp_vars WHERE var_name = 'dbt_schema';

    -- Create schema
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', v_schema);
    
    -- Grant privileges
    EXECUTE format('GRANT ALL PRIVILEGES ON DATABASE %I TO %I', v_database, v_user);
    EXECUTE format('GRANT ALL PRIVILEGES ON SCHEMA %I TO %I', v_schema, v_user);
    EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT ALL ON TABLES TO %I', v_schema, v_user);
END
$$;

-- Create embeddings table
CREATE TABLE IF NOT EXISTS :DBT_SCHEMA.embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    document_hash TEXT UNIQUE NOT NULL,
    version TEXT,
    processed_at TIMESTAMP,
    source TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissions on the embeddings table
DO $$
DECLARE
    v_user text;
    v_schema text;
BEGIN
    SELECT var_value INTO v_user FROM temp_vars WHERE var_name = 'dbt_user';
    SELECT var_value INTO v_schema FROM temp_vars WHERE var_name = 'dbt_schema';
    
    EXECUTE format('GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA %I TO %I', v_schema, v_user);
    EXECUTE format('GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA %I TO %I', v_schema, v_user);
END
$$;
