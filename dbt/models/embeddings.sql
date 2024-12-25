-- models/embeddings.sql
{{ config(
    materialized='table',
    schema=env_var('DBT_SCHEMA')
) }}

SELECT 
    id,
    content,
    masked_content,
    embedding,
    document_hash,
    version,
    processed_at,
    source,
    metadata,
    pii_metadata,
    created_at
FROM {{ source('raw', 'embeddings') }} 