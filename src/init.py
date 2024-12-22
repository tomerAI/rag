from embedding_processor import DocumentEmbedder
from utils.db import get_db_params, wait_for_db
from utils.logger import setup_logger
import psycopg2
import argparse
import sys
import json

logger = setup_logger(__name__)

def initialize_database(env="prod", source_path=None):
    db_params = get_db_params(env)
    
    if not wait_for_db(db_params):
        logger.error("Failed to connect to database")
        sys.exit(1)

    try:
        embedder = DocumentEmbedder()
        
        # Use default test document if no source path provided
        if not source_path:
            source_path = "src/tests/data/test_document.txt"
            
        embeddings = embedder.process_file(source_path)
        
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                for emb in embeddings:
                    metadata_json = json.dumps(emb.get('metadata', {}))
                    embedding_array = list(emb['embedding'])  # Convert numpy array to list
                    cur.execute("""
                        INSERT INTO raw.embeddings 
                        (content, embedding, document_hash, version, processed_at, source, metadata)
                        VALUES (%s, %s::vector, %s, %s, %s, %s, %s)
                        ON CONFLICT (document_hash) DO NOTHING
                    """, (
                        emb['content'],
                        embedding_array,
                        emb['document_hash'],
                        emb['version'],
                        emb['processed_at'],
                        emb['source'],
                        metadata_json
                    ))
            conn.commit()
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Initialize the database with embeddings')
    parser.add_argument('--env', choices=['prod', 'test'], default='prod', help='Environment to run in')
    parser.add_argument('--source', help='Path to source document')
    args = parser.parse_args()
    
    try:
        initialize_database(env=args.env, source_path=args.source)
    except psycopg2.Error as e:
        logger.error(f"Database error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 