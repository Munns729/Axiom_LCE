from docx import Document
from typing import Dict, List, Optional
import io

class SafeDocxEditor:
    """
    Safe document editing using python-docx with preservation of formatting.
    """
    
    def __init__(self, docx_content: bytes):
        self.doc = Document(io.BytesIO(docx_content))
        # We don't cache text here because it might change after edits
        
    def replace_clause(
        self, 
        clause_text: str, 
        new_text: str
    ) -> Dict:
        """
        Replace a clause text with new text while trying to preserve formatting.
        Finds the paragraph containing the clause text (fuzzy match could be added).
        """
        target_para = self._find_paragraph_by_text(clause_text)
        
        if not target_para:
            return {"success": False, "error": "Could not locate clause in document"}
        
        # Replace text while preserving formatting of the first run
        self._replace_paragraph_text(target_para, new_text)
        
        return {"success": True}
    
    def _find_paragraph_by_text(self, text: str):
        """Find paragraph by matching text (exact or contained)"""
        # Clean for comparison
        clean_target = " ".join(text.split())
        
        for para in self.doc.paragraphs:
            clean_para = " ".join(para.text.split())
            if clean_target in clean_para or clean_para in clean_target:
                # Basic match. For production, we might need stricter matching 
                # to avoid false positives in similar clauses
                return para
        return None
    
    def _replace_paragraph_text(self, para, new_text):
        """
        Replace paragraph text while preserving formatting
        """
        # Keep the styles of the paragraph
        # If runs exist, try to keep the first run's style (bold, italic, etc)
        if para.runs:
            first_run = para.runs[0]
            # Clear all runs
            # We can't clear the list directly easily, so we set text to empty
            for run in para.runs:
                run.text = ""
            # Set new text on first run
            first_run.text = new_text
        else:
            para.text = new_text

    def save_to_bytes(self) -> bytes:
        """Save modified document to bytes"""
        target_stream = io.BytesIO()
        self.doc.save(target_stream)
        target_stream.seek(0)
        return target_stream.read()
