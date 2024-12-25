from datetime import datetime
import os
import magic  # for file type detection

class MetadataHandler:
    def __init__(self):
        self.handlers = {
            '.pdf': self._get_pdf_metadata,
            '.py': self._get_python_metadata,
            '.txt': self._get_text_metadata,
            '.md': self._get_markdown_metadata
        }

    def get_metadata(self, file_path, chunk_index=0, total_chunks=1, chunk_content=""):
        """Get base metadata and combine with file-specific metadata"""
        base_metadata = self._get_base_metadata(file_path, chunk_index, total_chunks)
        
        # Get file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Get specific metadata based on file type
        specific_metadata = {}
        if file_ext in self.handlers:
            specific_metadata = self.handlers[file_ext](file_path, chunk_content)
        
        return {**base_metadata, **specific_metadata}

    def _get_base_metadata(self, file_path, chunk_index, total_chunks):
        """Get base metadata common to all file types"""
        file_stats = os.stat(file_path)
        return {
            'file_size': file_stats.st_size,
            'created_at': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            'file_extension': os.path.splitext(file_path)[1],
            'file_name': os.path.basename(file_path),
            'full_path': os.path.abspath(file_path),
            'chunk_index': chunk_index,
            'total_chunks': total_chunks,
            'mime_type': magic.from_file(file_path, mime=True)
        }

    def _get_pdf_metadata(self, file_path, chunk_content):
        """Extract PDF-specific metadata"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                return {
                    'total_pages': len(pdf.pages),
                    'pdf_info': dict(pdf.metadata or {}),
                    'page_numbers': self._extract_page_numbers(chunk_content)
                }
        except Exception as e:
            return {'pdf_metadata_error': str(e)}

    def _get_python_metadata(self, file_path, chunk_content):
        """Extract Python-specific metadata"""
        try:
            import ast
            with open(file_path, 'r') as file:
                tree = ast.parse(file.read())
                return {
                    'classes': len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
                    'functions': len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
                    'imports': len([node for node in ast.walk(tree) if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)]),
                    'line_numbers': self._extract_line_numbers(chunk_content, file_path)
                }
        except Exception as e:
            return {'python_metadata_error': str(e)}

    def _extract_line_numbers(self, chunk_content, file_path):
        """Extract line numbers for the chunk"""
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                start_idx = content.find(chunk_content)
                if start_idx != -1:
                    preceding_content = content[:start_idx]
                    start_line = preceding_content.count('\n') + 1
                    end_line = start_line + chunk_content.count('\n')
                    return {'start_line': start_line, 'end_line': end_line}
        except Exception:
            pass
        return {'start_line': None, 'end_line': None}

    def _extract_page_numbers(self, chunk_content):
        """Extract page numbers from PDF chunk content"""
        # This would need to be implemented based on how your PDF chunks are created
        # and how page numbers are preserved in the chunk content
        return {'page_number': None} 