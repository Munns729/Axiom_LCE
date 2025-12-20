import chromadb
from chromadb.config import Settings
from typing import List
from spine.src.models import ClauseNode
import uuid

class RagEngine:
    def __init__(self, persist_path="spine/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name="contract_clauses",
            metadata={"hnsw:space": "cosine"}
        )

    def index_tree(self, root: ClauseNode):
        """
        Recursively indexes all nodes in the tree that have text.
        """
        nodes_to_add = []
        self._collect_nodes(root, nodes_to_add)
        
        if not nodes_to_add:
            return

        ids = [n.id for n in nodes_to_add]
        documents = [n.text for n in nodes_to_add]
        metadatas = [{"an_type": n.an_type, "original_xml_id": str(n.original_xml_id)} for n in nodes_to_add]

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def _collect_nodes(self, node: ClauseNode, collector: List[ClauseNode]):
        if node.text and len(node.text) > 5: # Skip tiny nodes
            collector.append(node)
        for child in node.children:
            self._collect_nodes(child, collector)

    def query(self, query_text: str, n_results=3):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
