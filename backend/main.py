"""
Axiom LCE FastAPI Backend
European AI-powered legal document analysis with data sovereignty
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from dotenv import load_dotenv
import os
import time
import json
import uuid
import statistics
from io import BytesIO
from datetime import datetime

from database import get_db, engine

from models import (
    Base, Document, Analysis, ClauseSuggestion, 
    DealTemplate, DealMetrics, BenchmarkInsight, MarketBenchmark,
    ScenarioTemplate
)
from services.document_service import DocumentService
from services.analysis_service import AnalysisService
from services.benchmark_service import BenchmarkService
from services.scenario_service import ScenarioService
from services.structure_service import DocumentStructureService
from schemas import (
    DocumentUploadResponse,
    AnalysisResponse,
    DocumentListItem,
    HealthCheckResponse
)

# Load environment variables
from pathlib import Path
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Create database tables (optional - only if DATABASE_URL is configured)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Database not available - {e}")
    print("Running in database-free mode. Some features may be limited.")

# Initialize FastAPI
app = FastAPI(
    title="Axiom LCE API",
    version="1.0.0",
    description="European AI-powered legal contract analysis with data sovereignty"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_service = DocumentService()
analysis_service = AnalysisService()
benchmark_service = BenchmarkService()
scenario_service = ScenarioService()

# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Axiom LCE API - European Legal Contract Intelligence",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    Verifies database connection and Mistral API configuration
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
        
        # Check Mistral API key
        mistral_configured = bool(os.getenv("MISTRAL_API_KEY"))
        
        return {
            "status": "healthy",
            "database": db_status,
            "mistral_configured": mistral_configured
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )

# ============================================================================
# HEADLESS / WORD ADD-IN ENDPOINTS
# ============================================================================

class HeadlessLogicWarning(BaseModel):
    id: str
    node_id: str
    text_snippet: str
    issue: str
    severity: str 
    remediation: Optional[str] = None

class HeadlessAnalysisResponse(BaseModel):
    contract_id: str
    warnings: List[HeadlessLogicWarning]

@app.post("/analyze_logic")
async def analyze_logic_headless(
    file: UploadFile = File(...),
    playbook: Optional[str] = Form(None)
):
    """
    Headless analysis endpoint for Word Add-in.
    Accepts config/playbook via 'playbook' form field.
    """
    try:
        # Mock Logic for Demo
        # In real implementation, we would use document_service.extract_text and analysis_service
        
        content = await file.read()
        text, tree = document_service.extract_text(file.filename, content)
        
        # Parse playbook
        user_prefs = {}
        if playbook:
            try:
                user_prefs = json.loads(playbook)
            except:
                pass 
                
        target_law = user_prefs.get('governing_law', 'Delaware')
        
        warnings = []
        
        # Simple string search over text (faster than tree for simple keywords)
        # Mock finding a clause
        if "governing law" in text.lower():
            # Find the specific segment/sentence?
            # For this mock, just flag it if target_law isn't near "governing law"
            import re
            # Find sentence containing "governing law"
            sentences = re.split(r'[.!?]', text)
            for s in sentences:
                if "governing law" in s.lower():
                     if target_law.lower() not in s.lower():
                         warnings.append(HeadlessLogicWarning(
                            id=str(uuid.uuid4()),
                            node_id="mock-id", 
                            text_snippet=s.strip()[:100] + "...",
                            issue=f"Governing Law mismatch. Expected {target_law}.",
                            severity="High",
                            remediation=f"Change jurisdiction to {target_law}."
                         ))
                         break
        
        return HeadlessAnalysisResponse(contract_id=str(uuid.uuid4()), warnings=warnings)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================

@app.post("/api/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse a legal document (DOCX, PDF, or TXT)
    Stores document in database and returns document_id for analysis
    """
    try:
        # Read file content
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(400, "File is empty")
        
        # Extract text and structure
        text, tree = document_service.extract_text(file.filename, content)
        
        # Validate text length
        if not text or len(text.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Document appears to be empty or too short (minimum 100 characters)"
            )
        
        # Format file size
        file_size = document_service.format_file_size(len(content))
        
        # Save to database
        doc = Document(
            filename=file.filename,
            original_text=text,
            tree=tree, # Save parsed structure
            file_content=content, # Save original binary
            file_type=file.filename.split('.')[-1].lower(),
            file_size=file_size
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        return DocumentUploadResponse(
            document_id=str(doc.id),
            filename=doc.filename,
            length=len(text),
            preview=text[:500] + "..." if len(text) > 500 else text,
            uploaded_at=doc.uploaded_at.isoformat()
        )
    
    except ValueError as e:
        # Document parsing error
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

@app.get("/api/documents", response_model=List[DocumentListItem])
async def list_documents(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List all uploaded documents with analysis counts
    Returns most recent documents first
    """
    try:
        # Query documents with analysis counts
        docs = db.query(
            Document,
            func.count(Analysis.id).label('analysis_count')
        ).outerjoin(
            Analysis
        ).group_by(
            Document.id
        ).order_by(
            Document.uploaded_at.desc()
        ).limit(limit).all()
        
        return [
            DocumentListItem(
                id=str(doc.id),
                filename=doc.filename,
                uploaded_at=doc.uploaded_at.isoformat(),
                file_type=doc.file_type,
                analysis_count=analysis_count
            )
            for doc, analysis_count in docs
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )

# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/api/analyze/{document_id}", response_model=AnalysisResponse)
async def analyze_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Analyze a previously uploaded document
    Uses Mistral AI to extract definitions, detect conflicts, and generate scenarios
    Saves results to database
    """
    try:
        # Get document from database
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(404, "Document not found. Please upload first.")
        
        # Run basic analysis (definitions, conflicts, timeline)
        start_time = time.time()
        result = await analysis_service.analyze_document(doc.original_text)
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Save analysis to database (initial save)
        analysis = Analysis(
            document_id=doc.id,
            timeline=result["timeline"],
            scenarios=[], # Will be populated by scenario service
            definitions=result.get("definitions", []),
            conflict_analysis=result.get("conflict_analysis", {}),
            analysis_duration_ms=f"{duration_ms}ms"
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Generate and test scenarios (3-Tier System)
        scenario_tests = await scenario_service.generate_all_scenarios(
            analysis_id=str(analysis.id),
            document_text=doc.original_text,
            transaction_type="founder_agreement", # Default to founder agreement for now
            db=db
        )
        
        # Format scenarios for frontend/JSON column
        formatted_scenarios = [{
            "id": str(st.id),
            "name": st.name,
            "status": st.status,
            "description": st.description,
            "trigger_event": st.trigger_event if st.status == "fail" else None,
            "conflict": st.reasoning.get("conflict_if_any") if st.status == "fail" else None,
            "outcome": st.reasoning.get("actual_outcome") if st.status == "fail" else None,
            "expected_outcome": st.reasoning.get("expected_behavior") if st.status == "fail" else None,
            "source_type": st.source_type,
            "severity": st.severity
        } for st in scenario_tests]
        
        # Update analysis with formatted scenarios
        analysis.scenarios = formatted_scenarios
        db.commit()
        
        return AnalysisResponse(
            document_id=document_id,
            analysis_id=str(analysis.id),
            timeline=analysis.timeline,
            scenarios=analysis.scenarios,
            tree=doc.tree or {}, # Return stored tree
            analysis_complete=True,
            created_at=analysis.created_at.isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@app.post("/api/analyze-quick", response_model=AnalysisResponse)
async def analyze_quick(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze in one request (convenience endpoint)
    Recommended for demos and testing
    """
    try:
        # Upload document
        upload_result = await upload_document(file, db)
        
        # Analyze immediately
        return await analyze_document(upload_result.document_id, db)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quick analysis failed: {str(e)}"
        )

@app.post("/api/analyze-quick-stream")
async def analyze_quick_stream(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Streaming version of analyze-quick.
    Yields NDJSON events:
    {"type": "progress", ...}
    {"type": "timeline_step", ...}
    {"type": "result", ...}
    """
    try:
        # Upload is still synchronous/blocking for now (it is fast usually)
        upload_result = await upload_document(file, db)
        document = db.query(Document).filter(Document.id == upload_result.document_id).first()
        
        async def event_generator():
             # Basic info first
             yield json.dumps({
                 "type": "doc_info", 
                 "data": {
                     "document_id": upload_result.document_id,
                     "filename": upload_result.filename,
                     "tree": document.tree
                 }
             }) + "\n"

             async for event in analysis_service.analyze_document_generator(document.original_text):
                 # Save results to DB if it's the final result
                 if event["type"] == "result":
                     result = event["data"]
                     analysis = Analysis(
                        document_id=document.id,
                        timeline=result["timeline"],
                        scenarios=result["scenarios"],
                        definitions=result.get("definitions", []),
                        conflict_analysis=result.get("conflict_analysis", {}),
                        analysis_duration_ms=f"{result['duration_ms']}ms"
                     )
                     # We need a new DB session or careful handling for async generator? 
                     # Actually, `db` dependency is thread-local mostly safe, but prolonged stream might be tricky.
                     # For now, let's assume it's fine or create a fresh validation at end.
                     # Re-querying to be safe if session detached (though usually fine in same request context)
                     db.add(analysis)
                     db.commit()
                     db.refresh(analysis)
                     
                     # Add analysis_id to the result
                     event["data"]["analysis_id"] = str(analysis.id)
                 
                 yield json.dumps(event) + "\n"

        return StreamingResponse(event_generator(), media_type="application/x-ndjson")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Streaming analysis failed: {str(e)}"
        )

@app.get("/api/analyses/{document_id}")
async def get_analyses(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all analyses for a specific document
    Returns analysis history ordered by most recent first
    """
    try:
        analyses = db.query(Analysis).filter(
            Analysis.document_id == document_id
        ).order_by(
            Analysis.created_at.desc()
        ).all()
        
        if not analyses:
            return []
        
        return [
            {
                "id": str(a.id),
                "created_at": a.created_at.isoformat(),
                "model_used": a.model_used,
                "duration": a.analysis_duration_ms,
                "timeline": a.timeline,
                "scenarios": a.scenarios,
                "has_conflicts": a.conflict_analysis.get("has_conflict", False) if a.conflict_analysis else False
            }
            for a in analyses
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analyses: {str(e)}"
        )

# ============================================================================
# SCENARIO ENDPOINTS
# ============================================================================

@app.post("/api/test-custom-scenario/{analysis_id}")
async def test_custom_scenario(
    analysis_id: str,
    scenario_text: str = Body(..., embed=True), # Expect JSON: { "scenario_text": "..." }
    db: Session = Depends(get_db)
):
    """
    User submits a custom scenario in natural language
    """
    try:
        result = await scenario_service.test_custom_scenario(
            analysis_id=analysis_id,
            natural_language_scenario=scenario_text,
            db=db
        )
        
        return {
            "scenario_id": str(result.id),
            "name": result.name,
            "status": result.status,
            "reasoning": result.reasoning,
            "severity": result.severity,
            "source_type": result.source_type
        }
    
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Custom scenario test failed: {str(e)}")

@app.get("/api/scenario-templates/{transaction_type}")
async def get_scenario_templates(
    transaction_type: str,
    db: Session = Depends(get_db)
):
    """
    Get available scenario templates for a transaction type
    """
    try:
        templates = db.query(ScenarioTemplate).filter(
            ScenarioTemplate.transaction_type == transaction_type,
            ScenarioTemplate.is_active == True
        ).order_by(
            ScenarioTemplate.priority.desc()
        ).all()
        
        return [{
            "id": str(t.id),
            "name": t.name,
            "description": t.description,
            "category": t.category,
            "priority": t.priority
        } for t in templates]
    
    except Exception as e:
        raise HTTPException(500, f"Failed to get templates: {str(e)}")


@app.post("/api/suggest-fixes/{analysis_id}")
async def suggest_clause_fixes(
    analysis_id: str,
    scenario_id: str,  # e.g., "scenario-4"
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered clause suggestions to fix a detected conflict
    """
    try:
        # Get analysis
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(404, "Analysis not found")
        
        # Get document
        document = db.query(Document).filter(Document.id == analysis.document_id).first()
        if not document:
            raise HTTPException(404, "Document not found")
        
        # Find the failed scenario
        scenario = next(
            (s for s in analysis.scenarios if s.get('id') == scenario_id),
            None
        )
        if not scenario or scenario.get('status') != 'fail':
            raise HTTPException(400, "Scenario not found or not failed")
        
        # Extract relevant information
        conflict_type = scenario.get('conflict', 'unknown_conflict')
        
        # Try to extract the problematic clause from document using LLM-powered structure service
        # This is the "Modern Approach" replacing regex
        found_clause = await structure_service.find_clause_by_conflict(
            document.original_text,
            scenario.get('conflict', '')
        )

        if found_clause and found_clause.get('text'):
            original_clause = found_clause['text']
            section_number = found_clause.get('number', 'unknown')
        else:
             # Fallback to legacy regex if LLM fails (e.g. network issue)
            print("Warning: structure_service failed to find clause, falling back to regex")
            original_clause = extract_clause_from_conflict(
                document.original_text,
                scenario.get('conflict', '')
            )
            section_number = extract_section_number(scenario.get('conflict', ''))
        
        # Check if suggestions already exist
        existing = db.query(ClauseSuggestion).filter(
            ClauseSuggestion.analysis_id == analysis_id,
            ClauseSuggestion.scenario_id == scenario_id
        ).first()
        
        if existing:
            # Return cached suggestions
            return {
                "suggestion_id": str(existing.id),
                "scenario_id": scenario_id,
                "original_clause": existing.original_clause_text,
                "suggestions": existing.suggestions,
                "cached": True
            }
        
        # Generate new suggestions
        start_time = time.time()
        
        suggestions = await analysis_service.mistral.generate_clause_suggestions(
            original_clause=original_clause,
            conflict_type=conflict_type,
            section_number=section_number,
            full_document_context=document.original_text,
            definitions=analysis.definitions or []
        )
        
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        # Save to database
        clause_suggestion = ClauseSuggestion(
            analysis_id=analysis.id,
            scenario_id=scenario_id,
            original_clause_text=original_clause,
            original_section=section_number,
            conflict_type=conflict_type,
            suggestions=suggestions,
            generation_time_ms=generation_time_ms
        )
        db.add(clause_suggestion)
        db.commit()
        db.refresh(clause_suggestion)
        
        return {
            "suggestion_id": str(clause_suggestion.id),
            "scenario_id": scenario_id,
            "original_clause": original_clause,
            "original_section": section_number,
            "conflict_type": conflict_type,
            "suggestions": suggestions,
            "generation_time_ms": generation_time_ms,
            "cached": False
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate suggestions: {str(e)}"
        )

@app.post("/api/select-suggestion/{suggestion_id}")
async def select_suggestion(
    suggestion_id: str,
    selected_type: str,  # "founder_friendly", "market_standard", or "company_friendly"
    db: Session = Depends(get_db)
):
    """
    Record which suggestion the user selected
    """
    try:
        suggestion = db.query(ClauseSuggestion).filter(
            ClauseSuggestion.id == suggestion_id
        ).first()
        
        if not suggestion:
            raise HTTPException(404, "Suggestion not found")
        
        # Validate selection
        valid_types = ["founder_friendly", "market_standard", "company_friendly"]
        if selected_type not in valid_types:
            raise HTTPException(400, f"Invalid type. Must be one of: {valid_types}")
        
        # Update selection
        suggestion.selected_option = selected_type
        suggestion.selected_at = datetime.utcnow()
        db.commit()
        
        return {
            "suggestion_id": suggestion_id,
            "selected": selected_type,
            "message": "Selection recorded"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to record selection: {str(e)}")

from services.docx_editor import SafeDocxEditor

@app.post("/api/export-with-fix/{suggestion_id}")
async def export_document_with_fix(
    suggestion_id: str,
    selected_type: str,
    db: Session = Depends(get_db)
):
    """
    Generate a new DOCX with the selected clause fix applied using SafeDocxEditor.
    Preserves original formatting.
    """
    try:
        # Get suggestion
        suggestion = db.query(ClauseSuggestion).filter(
            ClauseSuggestion.id == suggestion_id
        ).first()
        if not suggestion:
            raise HTTPException(404, "Suggestion not found")
        
        # Get analysis and document
        analysis = db.query(Analysis).filter(
            Analysis.id == suggestion.analysis_id
        ).first()
        document = db.query(Document).filter(
            Document.id == analysis.document_id
        ).first()
        
        if not document.file_content:
             raise HTTPException(400, "Original document content not found (re-upload required for old docs)")

        # Get selected suggestion
        selected_suggestion = next(
            (s for s in suggestion.suggestions if s['type'] == selected_type),
            None
        )
        if not selected_suggestion:
            raise HTTPException(400, "Invalid suggestion type")
            
        # Initialize Safe Editor with original content
        editor = SafeDocxEditor(document.file_content)
        
        # Apply the fix (replace original text with new text)
        result = editor.replace_clause(
            suggestion.original_clause_text,
            selected_suggestion['clause_text']
        )
        
        if not result["success"]:
            # Fallback or error?
            # For now, let's error to be safe, or we could try fuzzy matching more aggressively
             raise HTTPException(400, f"Could not apply fix: {result.get('error')}")

        # In a full implementations, we would run structure_service.validate_edit() here too
        # validation = await structure_service.validate_edit(...)
        # if not validation['is_safe']: ...

        # Get modified bytes
        doc_bytes = editor.save_to_bytes()
        file_stream = BytesIO(doc_bytes)
        
        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=Revised_{document.filename}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Export failed: {str(e)}")

# ============================================================================
# BENCHMARKING ENDPOINTS
# ============================================================================

@app.post("/api/templates/create")
async def create_deal_template(
    name: str,
    document_category: str,
    target_terms: dict,
    organization_id: str = "default_org",
    db: Session = Depends(get_db)
):
    """
    Create a target position template for your organization
    """
    try:
        # Deactivate any existing active templates for this category
        db.query(DealTemplate).filter(
            DealTemplate.organization_id == organization_id,
            DealTemplate.document_category == document_category,
            DealTemplate.active == True
        ).update({"active": False})
        
        # Create new template
        template = DealTemplate(
            organization_id=organization_id,
            name=name,
            document_category=document_category,
            template_type="target_position",
            target_terms=target_terms,
            active=True
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return {
            "template_id": str(template.id),
            "name": name,
            "status": "Target position saved"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to create template: {str(e)}")

@app.post("/api/benchmark-analysis/{analysis_id}")
async def get_benchmark_analysis(
    analysis_id: str,
    organization_id: str = "default_org",
    db: Session = Depends(get_db)
):
    """
    Get dual-layer benchmark analysis for a document
    """
    try:
        # Get analysis
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(404, "Analysis not found")
        
        # Get document
        document = db.query(Document).filter(Document.id == analysis.document_id).first()
        
        # Extract deal terms
        extracted_terms = benchmark_service.extract_deal_terms(
            analysis,
            document.original_text
        )
        
        # Generate dual benchmark analysis
        benchmark_analysis = benchmark_service.generate_dual_benchmark_analysis(
            extracted_terms=extracted_terms,
            organization_id=organization_id,
            document_category="founder_agreement",
            db=db
        )
        
        # Save as deal metrics
        template = db.query(DealTemplate).filter(
            DealTemplate.organization_id == organization_id,
            DealTemplate.active == True
        ).first()
        
        if template:
            deal_metrics = DealMetrics(
                analysis_id=analysis.id,
                organization_id=organization_id,
                deal_name=f"Deal - {document.filename}",
                document_category="founder_agreement",
                terms=extracted_terms,
                deal_type="Series A",
                deal_stage="proposed",
                template_id=template.id,
                compliance_score=benchmark_analysis.get('compliance_score'),
                deviations=benchmark_analysis.get('deviations')
            )
            db.add(deal_metrics)
            db.commit()
        
        return {
            "analysis_id": analysis_id,
            "benchmarks": benchmark_analysis
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Benchmark analysis failed: {str(e)}")

@app.get("/api/insights/historical/{organization_id}")
async def get_historical_insights(
    organization_id: str,
    document_category: str = "founder_agreement",
    db: Session = Depends(get_db)
):
    """
    Get historical negotiation performance insights
    """
    try:
        # Get active template
        template = db.query(DealTemplate).filter(
            DealTemplate.organization_id == organization_id,
            DealTemplate.document_category == document_category,
            DealTemplate.active == True
        ).first()
        
        if not template:
            return {"error": "No active template found"}
        
        # Calculate insights for each metric
        insights = {}
        
        for metric_name in template.target_terms.keys():
            historical = benchmark_service.calculate_historical_performance(
                metric_name,
                organization_id,
                document_category,
                db
            )
            
            achievement_rate = benchmark_service.calculate_target_achievement_rate(
                metric_name,
                organization_id,
                template,
                db
            )
            
            target_spec = template.target_terms[metric_name]
            
            insights[metric_name] = {
                "target": target_spec.get('target'),
                "average_achieved": historical.get('average'),
                "median_achieved": historical.get('median'),
                "success_rate": achievement_rate,
                "sample_size": historical.get('sample_size'),
                "typical_concession": (
                    target_spec.get('target') - historical.get('average')
                    if historical.get('average') else None
                )
            }
        
        # Generate overall insights
        all_rates = [v['success_rate'] for v in insights.values() if v['success_rate']]
        avg_success_rate = statistics.mean(all_rates) if all_rates else 0
        
        return {
            "template_name": template.name,
            "overall_compliance": avg_success_rate,
            "metrics": insights,
            "recommendations": generate_strategic_recommendations(insights, template)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to generate insights: {str(e)}")

def generate_strategic_recommendations(insights: Dict, template: DealTemplate) -> List[str]:
    """Generate strategic recommendations based on historical performance"""
    recommendations = []
    
    for metric_name, data in insights.items():
        success_rate = data.get('success_rate', 0)
        
        if success_rate > 85:
            recommendations.append(
                f"✓ Strong position on {metric_name}: {success_rate:.0f}% success rate. Maintain firm stance."
            )
        elif success_rate < 50:
            recommendations.append(
                f"⚠️ Frequent concessions on {metric_name}: Only {success_rate:.0f}% success rate. "
                f"Consider making this a must-have or adjusting target."
            )
    
    return recommendations

# Helper functions
def extract_clause_from_conflict(document_text: str, conflict_description: str) -> str:
    """
    Extract the problematic clause from document
    This is a simplified version - production would use more sophisticated NLP
    """
    # Look for section numbers in conflict description
    import re
    section_match = re.search(r'Section (\d+\.?\d*)', conflict_description)
    
    if section_match:
        section_num = section_match.group(1)
        # Try to find this section in document
        section_pattern = rf'(?:Section |§\s*){section_num}[:\.]?\s*(.+?)(?=Section |\n\n|$)'
        clause_match = re.search(section_pattern, document_text, re.DOTALL | re.IGNORECASE)
        
        if clause_match:
            return clause_match.group(1).strip()[:500]  # Limit to 500 chars
    
    # Fallback: return a snippet around "Bad Leaver" or other keywords
    keywords = ['Bad Leaver', 'Good Reason', 'voluntary resignation', 'forfeiture']
    for keyword in keywords:
        if keyword.lower() in document_text.lower():
            idx = document_text.lower().index(keyword.lower())
            return document_text[max(0, idx-200):min(len(document_text), idx+300)]
    
    return "Could not extract specific clause - please review full document"

def extract_section_number(conflict_description: str) -> str:
    """Extract section number from conflict description"""
    import re
    match = re.search(r'Section (\d+\.?\d*)', conflict_description)
    return match.group(1) if match else "Unknown"
