import time
import psycopg2
from utils.logger import setup_logger
from embedding_processor import DocumentEmbedder

logger = setup_logger(__name__)

def wait_for_db(db_params, max_retries=5, retry_interval=10):
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**db_params)
            conn.close()
            return True
        except psycopg2.OperationalError:
            logger.warning(f"Database connection attempt {attempt + 1} failed. Retrying...")
            time.sleep(retry_interval)
    return False

def init_database(db_params, source_url):
    if not wait_for_db(db_params):
        raise Exception("Could not connect to database")

    try:
        embedder = DocumentEmbedder()
        embedded_docs = embedder.process_file(source_url)
        
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                for doc in embedded_docs:
                    cur.execute("""
                        INSERT INTO raw.embeddings 
                        (content, embedding, document_hash, version, processed_at, source, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (document_hash) DO NOTHING
                    """, (
                        doc['content'], 
                        doc['embedding'], 
                        doc['document_hash'],
                        doc['version'],
                        doc['processed_at'],
                        doc['source'],
                        doc['metadata']
                    ))
            conn.commit()
        
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise 