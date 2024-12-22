from embedding_processor import DocumentEmbedder
import psycopg2
import os
import time

def wait_for_postgres():
    db_params = {
        'host': os.getenv('DBT_HOST'),
        'port': os.getenv('DBT_PORT'),
        'user': os.getenv('DBT_USER'),
        'password': os.getenv('DBT_PASSWORD'),
        'database': os.getenv('DBT_DATABASE')
    }
    
    max_retries = 30
    for _ in range(max_retries):
        try:
            conn = psycopg2.connect(**db_params)
            conn.close()
            return True
        except psycopg2.OperationalError:
            time.sleep(1)
    return False

def main():
    if not wait_for_postgres():
        raise Exception("Could not connect to PostgreSQL")

    # Initialize embedder
    embedder = DocumentEmbedder()
    
    # Process local test document instead of URL
    test_file_path = "src/tests/data/test_document.txt"
    embeddings = embedder.process_file(test_file_path)
    
    # Store embeddings in database
    db_params = {
        'host': os.getenv('DBT_HOST'),
        'port': os.getenv('DBT_PORT'),
        'user': os.getenv('DBT_USER'),
        'password': os.getenv('DBT_PASSWORD'),
        'database': os.getenv('DBT_DATABASE')
    }
    
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            for emb in embeddings:
                cur.execute("""
                    INSERT INTO raw_embeddings (content, embedding, source)
                    VALUES (%s, %s, %s)
                """, (emb['content'], emb['embedding'], emb['source']))
        conn.commit()

if __name__ == "__main__":
    main() 