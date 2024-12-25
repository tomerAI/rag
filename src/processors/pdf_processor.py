from typing import Dict, Any, List
import PyPDF2
from .base_processor import BaseProcessor
from .registry import ProcessorRegistry
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

@ProcessorRegistry.register
class PDFProcessor(BaseProcessor):
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        return ['.pdf']
    
    def process(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, 'rb') as file:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            # Extract text from each page
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        chunks = self.text_splitter.split_text(text)
        return [{'content': chunk, 'metadata': self.get_metadata(file_path)} for chunk in chunks]
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            info = pdf_reader.metadata
            return {
                'file_type': 'pdf',
                'file_name': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'num_pages': len(pdf_reader.pages),
                'author': info.get('/Author', None),
                'creator': info.get('/Creator', None),
                'producer': info.get('/Producer', None),
                'subject': info.get('/Subject', None),
                'title': info.get('/Title', None),
                'creation_date': info.get('/CreationDate', None)
            } 