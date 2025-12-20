from fastapi.testclient import TestClient
from spine.src.main import app
import os

client = TestClient(app)

CORPUS_DIR = os.path.join(os.path.dirname(__file__), 'corpus')

def test_upload_flow():
    # 1. Upload
    path = os.path.join(CORPUS_DIR, 'messy_1.docx')
    with open(path, "rb") as f:
        response = client.post("/upload", files={"file": ("messy_1.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
    
    assert response.status_code == 200
    data = response.json()
    assert "contract_id" in data
    contract_id = data["contract_id"]
    
    # 2. Get Tree
    tree_resp = client.get(f"/contract/{contract_id}/tree")
    assert tree_resp.status_code == 200
    tree_data = tree_resp.json()
    assert tree_data["an_type"] == "document"
    
    # 3. Query
    query_resp = client.post(f"/contract/{contract_id}/query", json={"query": "Messy"})
    assert query_resp.status_code == 200
    query_data = query_resp.json()
    assert "results" in query_data
    assert len(query_data["results"]) > 0

    # 4. Refactor (Injection)
    # Get a node ID from the tree to target
    # Need to traverse tree_data to find a paragraph
    def find_para_id(node):
        if node['an_type'] == 'paragraph' and node['original_xml_id']:
            return node['original_xml_id']
        for child in node['children']:
            res = find_para_id(child)
            if res: return res
        return None
        
    target_id = find_para_id(tree_data)
    if target_id:
        refactor_payload = {
            "node_id_xml": target_id,
            "action": "inject",
            "injection_text": "API INJECTED CLAUSE"
        }
        ref_resp = client.post(f"/contract/{contract_id}/refactor", json=refactor_payload)
        if ref_resp.status_code != 200:
            print(f"Refactor failed: {ref_resp.text}")
        assert ref_resp.status_code == 200
        ref_data = ref_resp.json()
        assert "new_tree" in ref_data
        
        # Verify injection in new tree
        # This is a weak check (string exists in tree dump) but sufficient for smoke
        import json
        assert "API INJECTED CLAUSE" in json.dumps(ref_data["new_tree"])
