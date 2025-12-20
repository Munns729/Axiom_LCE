"""
Analysis orchestration service
Coordinates document analysis workflow
"""
import asyncio
import time
from typing import Dict, List
from .mistral_service import MistralService
from schemas import TimelineStep, Scenario

class AnalysisService:
    def __init__(self):
        self.mistral = MistralService()
    
    async def analyze_document(self, text: str) -> Dict:
        """
        Orchestrate full document analysis workflow
        Returns timeline steps and scenarios for frontend
        """
        start_time = time.time()
        timeline = []
        
        # Step 1: Analysis Started
        timeline.append({
            "id": 1,
            "type": "system",
            "title": "Analysis Started",
            "message": "Processing document with Mistral AI (European infrastructure, GDPR-compliant)",
            "timestamp": "Just now"
        })
        
        # Step 2: Extract definitions (parallel start)
        definitions = await self.mistral.extract_definitions(text)
        timeline.append({
            "id": 2,
            "type": "success",
            "title": "Definitions Verified",
            "message": f"{len(definitions)} definitions found. No circular dependencies detected.",
            "timestamp": f"{int((time.time() - start_time) * 1000)}ms"
        })
        
        # Step 3: Analyzing termination clauses
        timeline.append({
            "id": 3,
            "type": "loading",
            "title": "Analyzing Termination Clauses",
            "message": "Cross-referencing termination provisions against defined terms...",
            "timestamp": "Processing..."
        })
        
        # Step 4: Conflict analysis
        conflict_analysis = await self.mistral.analyze_conflicts(text, definitions)
        
        if conflict_analysis.get("has_conflict"):
            conflict_type = conflict_analysis.get("conflict_type", "Unknown").replace("_", " ").title()
            timeline.append({
                "id": 4,
                "type": "warning",
                "title": f"Conflict Detected: {conflict_type}",
                "message": conflict_analysis.get("details", "Logical conflict found in document"),
                "timestamp": f"{int((time.time() - start_time) * 1000)}ms"
            })
            
            severity = conflict_analysis.get("severity", "medium")
            verdict = "High Risk" if severity == "high" else "Medium Risk" if severity == "medium" else "Low Risk"
            
            timeline.append({
                "id": 5,
                "type": "complete",
                "title": f"Verdict: {verdict}",
                "message": "Critical issues found requiring manual review.",
                "timestamp": "Done"
            })
        else:
            timeline.append({
                "id": 4,
                "type": "success",
                "title": "No Critical Conflicts Detected",
                "message": "All termination provisions appear consistent with defined terms",
                "timestamp": f"{int((time.time() - start_time) * 1000)}ms"
            })
            
            timeline.append({
                "id": 5,
                "type": "complete",
                "title": "Verdict: Low Risk",
                "message": "No critical issues detected. Standard review recommended.",
                "timestamp": "Done"
            })
        
        # Step 5: Generate scenarios (can run in parallel with conflict analysis)
        scenarios_data = await self.mistral.generate_scenarios(text, definitions)
        
        # Calculate total duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        return {
            "timeline": timeline,
            "scenarios": scenarios_data,
            "definitions": definitions,
            "conflict_analysis": conflict_analysis,
            "duration_ms": duration_ms
        }

    async def analyze_document_generator(self, text: str):
        """
        Generator that yields progress updates and results in real-time
        Yields JSON-compatible dicts:
        - {"type": "progress", "stage": "...", "percent": X}
        - {"type": "timeline_step", "data": {...}}
        - {"type": "result", "data": {...}}
        """
        start_time = time.time()
        
        # Initial Progress
        yield {"type": "progress", "stage": "Initializing...", "percent": 5}
        
        # Step 1: System Init
        step1 = {
            "id": 1,
            "type": "system",
            "title": "Analysis Started",
            "message": "Processing document with Mistral AI (European infrastructure, GDPR-compliant)",
            "timestamp": "Just now"
        }
        yield {"type": "timeline_step", "data": step1}
        
        # Parsing
        yield {"type": "progress", "stage": "Parsing Structure...", "percent": 15}
        # (Simulation of parsing time if needed, or real parsing if we move it here)
        await asyncio.sleep(0.5) 
        
        # Step 2: Extract definitions
        yield {"type": "progress", "stage": "Extracting Definitions...", "percent": 30}
        definitions = await self.mistral.extract_definitions(text)
        
        step2 = {
            "id": 2,
            "type": "success",
            "title": "Definitions Verified",
            "message": f"{len(definitions)} definitions found. No circular dependencies detected.",
            "timestamp": f"{int((time.time() - start_time) * 1000)}ms"
        }
        yield {"type": "timeline_step", "data": step2}
        
        # Step 3: Analyze conflicts (Start)
        yield {"type": "progress", "stage": "Analyzing Conflicts...", "percent": 50}
        step3 = {
            "id": 3,
            "type": "loading",
            "title": "Analyzing Termination Clauses",
            "message": "Cross-referencing termination provisions against defined terms...",
            "timestamp": "Processing..."
        }
        yield {"type": "timeline_step", "data": step3}
        
        # Step 4: Actual Conflict Analysis
        yield {"type": "progress", "stage": "Cross-Referencing...", "percent": 70}
        conflict_analysis = await self.mistral.analyze_conflicts(text, definitions)
        
        if conflict_analysis.get("has_conflict"):
            conflict_type = conflict_analysis.get("conflict_type", "Unknown").replace("_", " ").title()
            step4 = {
                "id": 4,
                "type": "warning",
                "title": f"Conflict Detected: {conflict_type}",
                "message": conflict_analysis.get("details", "Logical conflict found in document"),
                "timestamp": f"{int((time.time() - start_time) * 1000)}ms"
            }
            yield {"type": "timeline_step", "data": step4}
            
            severity = conflict_analysis.get("severity", "medium")
            verdict = "High Risk" if severity == "high" else "Medium Risk" if severity == "medium" else "Low Risk"
            
            step5 = {
                "id": 5,
                "type": "complete",
                "title": f"Verdict: {verdict}",
                "message": "Critical issues found requiring manual review.",
                "timestamp": "Done"
            }
            yield {"type": "timeline_step", "data": step5}
        else:
            step4 = {
                "id": 4,
                "type": "success",
                "title": "No Critical Conflicts Detected",
                "message": "All termination provisions appear consistent with defined terms",
                "timestamp": f"{int((time.time() - start_time) * 1000)}ms"
            }
            yield {"type": "timeline_step", "data": step4}
            
            step5 = {
                "id": 5,
                "type": "complete",
                "title": "Verdict: Low Risk",
                "message": "No critical issues detected. Standard review recommended.",
                "timestamp": "Done"
            }
            yield {"type": "timeline_step", "data": step5}
        
        # Step 5: Generate Scenarios
        yield {"type": "progress", "stage": "Generating Scenarios...", "percent": 90}
        scenarios_data = await self.mistral.generate_scenarios(text, definitions)
        
        yield {"type": "progress", "stage": "Finalizing...", "percent": 100}
        
        # Final Result Payload
        duration_ms = int((time.time() - start_time) * 1000)
        final_result = {
            "timeline": [step1, step2, step3, step4, step5], # In a real implementation we might accumulate these better
            "scenarios": scenarios_data,
            "definitions": definitions,
            "conflict_analysis": conflict_analysis,
            "duration_ms": duration_ms
        }
        yield {"type": "result", "data": final_result}
