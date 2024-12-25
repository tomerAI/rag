from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseProcessor(ABC):
    """Base class for all content processors"""
    
    @abstractmethod
    def process(self, file_path: str) -> List[Dict[str, Any]]:
        """Process the content and return list of chunks with embeddings"""
        pass
    
    @abstractmethod
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata specific to the content type"""
        pass
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Return list of supported file extensions"""
        pass 