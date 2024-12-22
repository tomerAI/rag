from utils.logger import setup_logger
import psycopg2
import time
import os

logger = setup_logger(__name__)

def get_db_params(env="prod"):
    if env == "test":
        return {
            'host': os.getenv('DBT_HOST', 'localhost'),
            'port': os.getenv('DBT_PORT', 5432),
            'user': 'test',
            'password': 'test123',
            'database': 'rag_test'
        }
    return {
        'host': os.getenv('DBT_HOST'),
        'port': os.getenv('DBT_PORT'),
        'user': os.getenv('DBT_USER'),
        'password': os.getenv('DBT_PASSWORD'),
        'database': os.getenv('DBT_DATABASE')
    }

def wait_for_db(db_params, max_retries=30, retry_interval=1):
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**db_params)
            conn.close()
            logger.info("Successfully connected to database")
            return True
        except psycopg2.OperationalError:
            logger.warning(f"Database connection attempt {attempt + 1} failed. Retrying...")
            time.sleep(retry_interval)
    return False 