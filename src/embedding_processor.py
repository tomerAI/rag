import os
import hashlib
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from utils.logger import setup_logger
from utils.metrics import EMBEDDING_GENERATION_TIME, EMBEDDING_COUNT, MetricsMiddleware

class DocumentEmbedder:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.logger = setup_logger(__name__)
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
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
        