from typing import Dict, Any, List
from .base_processor import BaseProcessor
from .registry import ProcessorRegistry
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

@ProcessorRegistry.register
class TextProcessor(BaseProcessor):
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        return ['.txt']
    
    def process(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        chunks = self.text_splitter.split_text(text)
        return [{'content': chunk, 'metadata': self.get_metadata(file_path)} for chunk in chunks]
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        return {
            'file_type': 'text',
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path)
        } 