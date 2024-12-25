import os
import hashlib
import argparse
from datetime import datetime
import psycopg2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from utils.logger import setup_logger
from utils.db import get_db_params, wait_for_db
from utils.metrics import EMBEDDING_GENERATION_TIME, EMBEDDING_COUNT, MetricsMiddleware
import json
from processors.registry import ProcessorRegistry
import processors
from typing import List, Dict, Any

class DocumentEmbedder:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.embeddings = OpenAIEmbeddings()
        self.db_params = get_db_params()
        
        # Wait for database to be ready
        if not wait_for_db(self.db_params):
            self.logger.error("Failed to connect to database")
            raise RuntimeError("Database connection failed")
    
    def _generate_document_hash(self, content):
        return hashlib.md5(content.encode()).hexdigest()

    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        file_extension = os.path.splitext(file_path)[1]
        processor_class = ProcessorRegistry.get_processor(file_extension)
        processor = processor_class()
        
        try:
            # Process the document into chunks
            chunks = processor.process(file_path)
            
            # Generate embeddings for each chunk
            embedded_documents = []
            for chunk in chunks:
                vector = self.embeddings.embed_query(chunk['content'])
                doc_hash = self._generate_document_hash(chunk['content'])
                
                embedded_documents.append({
                    'content': chunk['content'],
                    'embedding': vector,
                    'document_hash': doc_hash,
                    'metadata': chunk['metadata'],
                    'source': file_path,
                    'version': '1.0',
                    'processed_at': datetime.now().isoformat()
                })
            
            return embedded_documents
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {str(e)}")
            raise

    def process_directory(self, directory_path):
        all_embeddings = []
        supported_extensions = set()
        for processor in ProcessorRegistry._processors.values():
            supported_extensions.update(processor.get_supported_extensions())
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in supported_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        embeddings = self.process_file(file_path)
                        all_embeddings.extend(embeddings)
                    except Exception as e:
                        self.logger.error(f"Failed to process {file_path}: {str(e)}")
        return all_embeddings
        
    def store_embeddings(self, embedded_documents):
        schema = os.getenv('DBT_SCHEMA')
        if not wait_for_db(self.db_params):
            self.logger.error("Failed to connect to database")
            return False

        try:
            with psycopg2.connect(**self.db_params) as conn:
                with conn.cursor() as cur:
                    for emb in embedded_documents:
                        cur.execute(f"""
                            INSERT INTO {schema}.embeddings 
                            (content, embedding, document_hash, 
                             version, processed_at, source, metadata)
                            VALUES (%s, %s::vector, %s, %s, %s, %s, %s)
                            ON CONFLICT (document_hash) DO NOTHING
                        """, (
                            emb['content'],
                            list(emb['embedding']),
                            emb['document_hash'],
                            emb['version'],
                            emb['processed_at'],
                            emb['source'],
                            json.dumps(emb.get('metadata', {}))
                        ))
                conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to store embeddings: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Process documents and store embeddings')
    parser.add_argument('--input-dir', required=True, help='Directory containing documents to process')
    args = parser.parse_args()

    embedder = DocumentEmbedder()
    
    # Get all supported extensions from registered processors
    supported_extensions = set()
    for processor in ProcessorRegistry._processors.values():
        supported_extensions.update(processor.get_supported_extensions())
    
    for root, _, files in os.walk(args.input_dir):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in supported_extensions:
                file_path = os.path.join(root, file)
                try:
                    embeddings = embedder.process_file(file_path)
                    if embedder.store_embeddings(embeddings):
                        embedder.logger.info(f"Successfully processed and stored embeddings for {file_path}")
                except Exception as e:
                    embedder.logger.error(f"Failed to process {file_path}: {str(e)}")

if __name__ == "__main__":
    main()
        