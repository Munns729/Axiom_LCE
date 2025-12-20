from fastapi import FastAPI, UploadFile, File, HTTPException
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
