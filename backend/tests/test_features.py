
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock database module BEFORE importing main
# This prevents create_all() from running against a real or sqlite DB
mock_db_module = MagicMock()
# We need get_db to be a function so Depends(get_db) works and we can override it
def mock_get_db_fn():
    pass
mock_db_module.get_db = mock_get_db_fn
mock_db_module.engine = MagicMock()
sys.modules["database"] = mock_db_module

# Now import main
from main import app, get_db
from fastapi.testclient import TestClient

client = TestClient(app)

# Mock DB Session for dependency override
mock_db_session = MagicMock()
def override_get_db():
    yield mock_db_session

app.dependency_overrides[get_db] = override_get_db

def test_suggest_fixes_endpoint():
    # Mock Analysis and Document queries
    mock_analysis = MagicMock()
    mock_analysis.id = "123"
    mock_analysis.document_id = "doc_123"
    mock_analysis.scenarios = [{"id": "scn_1", "status": "fail", "conflict": "Section 4.2 conflict"}]
    mock_analysis.definitions = []
    
    mock_doc = MagicMock()
    mock_doc.original_text = "Full document text..."
    
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_analysis, # Analysis
        mock_doc,      # Document
        None           # Existing suggestion check
    ]
    
    # Mock Mistral Service
    with patch("main.analysis_service.mistral.generate_clause_suggestions", new_callable=AsyncMock) as mock_mistral:
        mock_mistral.return_value = [
            {
                "type": "founder_friendly",
                "clause_text": "Better clause",
                "rationale": "Fixes it",
                "risk_level": "low",
                "changes_summary": "Improved"
            }
        ]
        
        response = client.post("/api/suggest-fixes/123?scenario_id=scn_1")
        
        if response.status_code != 200:
            print(response.json())
        
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == "scn_1"
        assert len(data["suggestions"]) == 1

def test_create_template_endpoint():
    payload = {
        "name": "Standard Series A",
        "document_category": "founder_agreement",
        "target_terms": {
            "vesting_years": {"target": 4}
        },
        "organization_id": "org_1"
    }
    
    response = client.post("/api/templates/create?name=Standard%20Series%20A&document_category=founder_agreement&organization_id=org_1", json=payload["target_terms"])
    
    if response.status_code != 200:
        print(response.json())
        
    assert response.status_code == 200
    assert response.json()["status"] == "Target position saved"

def test_benchmark_analysis_endpoint():
    mock_analysis = MagicMock()
    mock_doc = MagicMock()
    
    # Reset side effect for this test
    mock_db_session.query.side_effect = None
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_analysis, # Analysis
        mock_doc,      # Document
        MagicMock()    # Template
    ]
    
    # Check if benchmark_service needs to be patched
    # Since we imported main, main imported services...
    # We patch where it is used in main or benchmark_service
    
    with patch("main.benchmark_service.extract_deal_terms") as mock_extract, \
         patch("main.benchmark_service.generate_dual_benchmark_analysis") as mock_generate:
        
        mock_extract.return_value = {"vesting_years": 4}
        mock_generate.return_value = {
            "compliance_score": 90,
            "metrics": {}
        }
        
        response = client.post("/api/benchmark-analysis/123")
        
        if response.status_code != 200:
            print(response.json())

        assert response.status_code == 200
        assert "benchmarks" in response.json()
