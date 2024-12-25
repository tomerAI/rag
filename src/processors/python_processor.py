from typing import Dict, Any, List
import ast
from .base_processor import BaseProcessor
from .registry import ProcessorRegistry
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

@ProcessorRegistry.register
class PythonProcessor(BaseProcessor):
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\nclass ", "\ndef ", "\n\n", "\n", " ", ""]
        )
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        return ['.py']
    
    def process(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = self.text_splitter.split_text(content)
        return [{'content': chunk, 'metadata': self.get_metadata(file_path)} for chunk in chunks]
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            return {
                'file_type': 'python',
                'file_name': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'classes': len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
                'functions': len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
                'imports': len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])
            }
        except Exception as e:
            return {
                'file_type': 'python',
                'file_name': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'parse_error': str(e)
            } 