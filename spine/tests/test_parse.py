import pytest
import os
from spine.src.document_service import DocumentParser
from spine.src.models import ClauseNode

CORPUS_DIR = os.path.join(os.path.dirname(__file__), 'corpus')

def test_load_messy_1():
    path = os.path.join(CORPUS_DIR, 'messy_1.docx')
    if not os.path.exists(path):
        pytest.skip("Corpus file messy_1.docx not found")
        
    parser = DocumentParser()
    tree = parser.load(path)
    
    assert tree.an_type == "document"
    assert len(tree.children) > 0
    
    # Check for specific known content
    # "Messy Contract 1" -> Heading 1 -> Article
    article = tree.children[0]
    assert article.an_type == "article"
    assert "Messy Contract 1" in article.text

def test_load_messy_2():
    path = os.path.join(CORPUS_DIR, 'messy_2.docx')
    if not os.path.exists(path):
        pytest.skip("Corpus file messy_2.docx not found")
        
    parser = DocumentParser()
    tree = parser.load(path)
    
    # "LEASE AGREEMENT" -> Heading 1 -> Article
    assert tree.children[0].an_type == "article"
    assert "LEASE AGREEMENT" in tree.children[0].text
