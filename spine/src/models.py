from dataclasses import dataclass, field
from typing import List, Optional
import uuid

@dataclass
class ClauseNode:
    """
    Represents a node in the 'Loose Akoma Ntoso' tree.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    an_type: str = "paragraph"  # article, section, paragraph, point
    an_num: Optional[str] = None # e.g. "1.1", "a", "4.2.1"
    text: str = ""
    original_xml_id: Optional[str] = None # Traceback to docx <w:p>
    children: List['ClauseNode'] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "id": self.id,
            "an_type": self.an_type,
            "an_num": self.an_num,
            "text": self.text,
            "original_xml_id": self.original_xml_id,
            "children": [child.to_dict() for child in self.children],
            "metadata": self.metadata
        }
