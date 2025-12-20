"""
Standardized Abstract Syntax Tree (AST) for Legal Documents.
Based on "Loose Akoma Ntoso" principles.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import uuid

class ClauseNode(BaseModel):
    """
    Recursive node representing a structrual element of a legal contract.
    e.g. Article -> Section -> Paragraph -> Point
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Structural Type
    an_type: Literal["document", "article", "section", "paragraph", "point", "clause"]
    
    # Numbering (e.g. "1.1", "(a)")
    an_num: Optional[str] = None
    
    # The actual text content
    # Note: Frontend expects 'text_content', backend parser was using 'text'.
    text_content: str
    
    # Traceback to original XML (for precise editing later)
    original_xml_id: Optional[str] = None
    
    # Recursive children
    children: List['ClauseNode'] = Field(default_factory=list)
    
    # Metadata for AI analysis results (e.g. "risk_score": 90)
    metadata: dict = Field(default_factory=dict)

# Resolve forward reference for recursive model
ClauseNode.update_forward_refs()
