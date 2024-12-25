from .text_processor import TextProcessor
from .python_processor import PythonProcessor
from .pdf_processor import PDFProcessor
from .docx_processor import DocxProcessor

# This import will trigger the registration of all processors
__all__ = ['TextProcessor', 'PythonProcessor', 'PDFProcessor', 'DocxProcessor'] 