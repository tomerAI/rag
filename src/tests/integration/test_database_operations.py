import pytest
import psycopg2
from embedding_processor import DocumentEmbedder
from query_processor import QueryProcessor

@pytest.fixture
def db_params():
    return {
        'host': 'localhost',
        'port': 5432,
        'user': 'test',
        'password': 'test123',
        'database': 'rag_test'
    }

def test_embedding_storage_and_retrieval(db_params):
    embedder = DocumentEmbedder()
    processor = QueryProcessor(db_params)
    
    # Generate and store embeddings
    embeddings = embedder.process_file("test_document.txt")
    
    # Query the stored embeddings
    results = processor.query_database("test query")
    assert len(results) > 0 