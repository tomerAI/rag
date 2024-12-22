-- models/embeddings.sql
{{ config(
    materialized='table',
    indexes=[
        {'columns': ['embedding'], 'type': 'ivfflat', 'name': 'embeddings_vector_idx'},
        {'columns': ['document_hash'], 'name': 'document_hash_idx'}
    ]
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