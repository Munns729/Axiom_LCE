from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
import uuid

from spine.src.document_service import DocumentParser
from spine.src.rag_engine import RagEngine
from spine.src.editor import DocumentEditor

app = FastAPI(title="Axiom Spine Service")

# In-memory storage for spike
UPLOAD_DIR = "spine/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
RAG_DIR = "spine/chroma_db"
os.makedirs(RAG_DIR, exist_ok=True)

# Global instances (mock database)
parser = DocumentParser()
rag = RagEngine(persist_path=RAG_DIR)
# Map contract_id -> tree (in memory)
contract_store = {}

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    results: List[str]

class RefactorRequest(BaseModel):
    node_id_xml: str
    action: str = "split" # split, inject
    part_a_text: Optional[str] = None
    part_b_text: Optional[str] = None
    injection_text: Optional[str] = None

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    contract_id = str(uuid.uuid4())
    file_location = os.path.join(UPLOAD_DIR, f"{contract_id}_{file.filename}")
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    # Ingest
    try:
        tree = parser.load(file_location)
        contract_store[contract_id] = tree
        
        # Index
        rag.index_tree(tree)
        
        return {
            "contract_id": contract_id, 
            "message": "Ingested successfully",
            "root_node": tree.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contract/{contract_id}/tree")
async def get_tree(contract_id: str):
    if contract_id not in contract_store:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract_store[contract_id].to_dict()

@app.post("/contract/{contract_id}/query")
async def query_contract(contract_id: str, request: QueryRequest):
    # Note: Currently RAG is global, so queries search ALL docs. 
    # In production, we'd filter by metadata={'contract_id': ...}
    
    results = rag.query(request.query)
    # Chroma returns struct like {'documents': [['text',...]], ...}
    docs = results['documents'][0] if results['documents'] else []
    
    return {"results": docs}

@app.post("/contract/{contract_id}/refactor")
async def refactor_contract(contract_id: str, request: RefactorRequest):
    # This requires looking up the file path from the contract_id. 
    # In a real app we would have a DB. For now, rely on naming convention in UPLOAD_DIR.
    # scan dir
    target_file = None
    for f in os.listdir(UPLOAD_DIR):
        if f.startswith(contract_id):
            target_file = os.path.join(UPLOAD_DIR, f)
            break
            
    if not target_file:
        raise HTTPException(status_code=404, detail="Contract file not found")
        
    editor = DocumentEditor(target_file)
    
    try:
        if request.action == "split":
            if not request.part_a_text or not request.part_b_text:
                raise HTTPException(status_code=400, detail="Split requires part_a_text and part_b_text")
            editor.split_paragraph(request.node_id_xml, request.part_a_text, request.part_b_text)
            
        elif request.action == "inject":
            if not request.injection_text:
                raise HTTPException(status_code=400, detail="Inject requires injection_text")
            editor.inject_paragraph_after(request.node_id_xml, request.injection_text)
            
        else:
             raise HTTPException(status_code=400, detail="Unknown action")
             
        # Save overwrite
        editor.save(target_file)
        
        # Reload tree to reflect changes
        new_tree = parser.load(target_file)
        contract_store[contract_id] = new_tree
        
        return {"message": "Refactor complete", "new_tree": new_tree.to_dict()}
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class Playbook(BaseModel):
    preferences: dict

class LogicWarning(BaseModel):
    id: str
    node_id: str
    text_snippet: str
    issue: str
    severity: str # "High", "Medium", "Low"
    remediation: Optional[str] = None

class AnalysisResponse(BaseModel):
    contract_id: str
    warnings: List[LogicWarning]

@app.post("/analyze_logic")
async def analyze_logic(file: UploadFile = File(...), playbook: Optional[str] = Form(None)):
    # playbook is passed as a JSON string because it's a form-data request alongside the file
    contract_id = str(uuid.uuid4())
    file_location = os.path.join(UPLOAD_DIR, f"{contract_id}_{file.filename}")
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    try:
        # 1. Ingest
        tree = parser.load(file_location)
        contract_store[contract_id] = tree
        rag.index_tree(tree)

        # 2. Parse Playbook
        import json
        user_prefs = {}
        if playbook:
            try:
                user_prefs = json.loads(playbook)
            except:
                pass 

        # 3. Running "The Logic Linter" (Mock implementation for pivot)
        warnings = []
        
        # Example Check: Governing Law
        # In a real app, we would query the RAG engine: "What is the governing law?"
        # Then compare with user_prefs.get('governing_law')
        
        target_law = user_prefs.get('governing_law', 'Delaware') # Default to DE
        
        # Mocking the RAG lookup for demonstration
        # Iterate nodes to find "Governing Law"
        found_law_node = None
        for child in tree.children:
            # simple keyword search on first level for speed
            if "governing law" in child.text.lower() or "jurisdiction" in child.text.lower():
                found_law_node = child
                break
        
        if found_law_node:
            # Check if it matches target (Naive check)
            if target_law.lower() not in found_law_node.text.lower():
                warnings.append(LogicWarning(
                    id=str(uuid.uuid4()),
                    node_id=found_law_node.original_xml_id,
                    text_snippet=found_law_node.text[:50]+"...",
                    issue=f"Governing Law mismatch. Expected {target_law}.",
                    severity="High",
                    remediation=f"Change jurisdiction to {target_law}."
                ))
        
        return AnalysisResponse(contract_id=contract_id, warnings=warnings)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
