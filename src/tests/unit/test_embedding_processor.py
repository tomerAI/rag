import pytest
from unittest.mock import Mock, patch
from embedding_processor import DocumentEmbedder

@pytest.fixture
def embedder():
    return DocumentEmbedder()

def test_generate_document_hash():
    embedder = DocumentEmbedder()
    content = "test content"
    hash1 = embedder._generate_document_hash(content)
    hash2 = embedder._generate_document_hash(content)
    assert hash1 == hash2
    assert isinstance(hash1, str)

@patch('langchain.embeddings.OpenAIEmbeddings')
def test_process_file(mock_embeddings):
    mock_embeddings.embed_query.return_value = [0.1] * 1536
    embedder = DocumentEmbedder()
    
    with patch('langchain.document_loaders.TextLoader') as mock_loader:
        mock_loader.return_value.load.return_value = [
            Mock(page_content="test content", metadata={})
        ]
        
        result = embedder.process_file("test.txt")
        assert len(result) > 0
        assert 'content' in result[0]
        assert 'embedding' in result[0] 