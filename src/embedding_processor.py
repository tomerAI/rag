import os
import hashlib
import argparse
from datetime import datetime
import psycopg2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from utils.logger import setup_logger
from utils.db import get_db_params, wait_for_db
from utils.metrics import EMBEDDING_GENERATION_TIME, EMBEDDING_COUNT, MetricsMiddleware
import json

class DocumentEmbedder:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.logger = setup_logger(__name__)
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.db_params = get_db_params()
    
    def _generate_document_hash(self, content):
        return hashlib.md5(content.encode()).hexdigest()
    
    @MetricsMiddleware.track_time(EMBEDDING_GENERATION_TIME)
    def process_file(self, file_path):
        try:
            loader = TextLoader(file_path)
            documents = loader.load()
            splits = self.text_splitter.split_documents(documents)
            
            embedded_documents = []
            for doc in splits:
                vector = self.embeddings.embed_query(doc.page_content)
                doc_hash = self._generate_document_hash(doc.page_content)
                
                embedded_documents.append({
                    'content': doc.page_content,
                    'embedding': vector,
                    'metadata': doc.metadata,
                    'source': file_path,
                    'document_hash': doc_hash,
                    'version': '1.0',
                    'processed_at': datetime.utcnow().isoformat()
                })
            
            self.logger.info(f"Successfully processed file: {file_path}")
            EMBEDDING_COUNT.inc(len(embedded_documents))
            return embedded_documents
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {str(e)}")
            raise

    def process_directory(self, directory_path):
        all_embeddings = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.txt') or file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    all_embeddings.extend(self.process_file(file_path))
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
                            (content, embedding, document_hash, version, processed_at, source, metadata)
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
    
    for root, _, files in os.walk(args.input_dir):
        for file in files:
            if file.endswith(('.txt', '.py', '.md')):
                file_path = os.path.join(root, file)
                try:
                    embeddings = embedder.process_file(file_path)
                    if embedder.store_embeddings(embeddings):
                        embedder.logger.info(f"Successfully processed and stored embeddings for {file_path}")
                except Exception as e:
                    embedder.logger.error(f"Failed to process {file_path}: {str(e)}")

if __name__ == "__main__":
    main()
        