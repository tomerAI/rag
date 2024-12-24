-- models/embeddings.sql
{{ config(
    materialized='table',
    schema=env_var('DBT_SCHEMA')
) }}

SELECT 
    id,
    content,
    embedding,
    document_hash,
    version,
    processed_at,
    source,
    metadata,
    created_at
FROM {{ source('raw', 'embeddings') }} 