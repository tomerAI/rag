
  
    

  create  table "rag"."raw_raw"."embeddings__dbt_tmp"
  
  
    as
  
  (
    -- models/embeddings.sql


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
FROM "rag"."raw"."embeddings"
  );
  