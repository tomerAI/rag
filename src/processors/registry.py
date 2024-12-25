from typing import Dict, Type
from .base_processor import BaseProcessor

class ProcessorRegistry:
    _processors: Dict[str, Type[BaseProcessor]] = {}
    
    @classmethod
    def register(cls, processor: Type[BaseProcessor]):
        """Register a processor for its supported extensions"""
        for ext in processor.get_supported_extensions():
            cls._processors[ext.lower()] = processor
        return processor
    
    @classmethod
    def get_processor(cls, file_extension: str) -> Type[BaseProcessor]:
        """Get appropriate processor for a file extension"""
        processor = cls._processors.get(file_extension.lower())
        if not processor:
            raise ValueError(f"No processor registered for extension: {file_extension}")
        return processor 