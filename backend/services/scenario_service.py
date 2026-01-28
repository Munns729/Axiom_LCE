from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models import ScenarioTemplate, ScenarioTest, Analysis, Document
from .mistral_service import MistralService
import json
import uuid
import asyncio

class ScenarioService:
    def __init__(self):
        self.mistral = MistralService()
    
    async def generate_all_scenarios(
        self,
        analysis_id: str,
        document_text: str,
        transaction_type: str,
        db: Session
    ) -> List[ScenarioTest]:
        """
        Generate complete set of scenarios:
        1. Template scenarios (top 5 by priority)
        2. Contract-specific scenarios (3-5 based on document)
        3. Return all for testing
        """
        
        scenarios = []
        
        # TIER 1: Get template scenarios
        template_scenarios = await self._get_template_scenarios(
            transaction_type, 
            document_text,
            db
        )
        scenarios.extend(template_scenarios)
        
        # TIER 2: Generate contract-specific scenarios
        custom_scenarios = await self._generate_contract_specific_scenarios(
            document_text,
            transaction_type
        )
        scenarios.extend(custom_scenarios)
        
        # Test all scenarios
        tested_scenarios = []
        for scenario in scenarios:
            result = await self._test_scenario(
                scenario,
                document_text,
                analysis_id,
                db
            )
            tested_scenarios.append(result)
        
        return tested_scenarios
    
    async def _get_template_scenarios(
        self,
        transaction_type: str,
        document_text: str,
        db: Session,
        max_count: int = 5
    ) -> List[Dict]:
        """
        Get top template scenarios for transaction type
        Uses LLM to determine which templates are most relevant
        """
        
        # Get all templates for this transaction type
        templates = db.query(ScenarioTemplate).filter(
            ScenarioTemplate.transaction_type == transaction_type,
            ScenarioTemplate.is_active == True
        ).order_by(
            ScenarioTemplate.priority.desc()
        ).all()
        
        if not templates:
            return []
        
        # Let LLM select most relevant templates based on document content
        prompt = f"""Analyze this legal document and select the {max_count} most relevant scenario tests.

Document (first 6000 chars):
{document_text[:6000]}

Available scenario templates:
{json.dumps([{
    "id": str(t.id),
    "name": t.name,
    "description": t.description,
    "category": t.category
} for t in templates], indent=2)}

Consider:
1. What provisions exist in the document?
2. Which scenarios test the most critical risks?
3. Which scenarios are most likely to reveal conflicts?

Return JSON array of template IDs in priority order:
[
  "template-uuid-1",
  "template-uuid-2",
  ...
]

Return ONLY the JSON array, max {max_count} items."""
        
        # Check if Mistral client is available
        if not self.mistral.client:
           # Fallback: Just return top priority templates
           return [{
                "source_type": "template",
                "template_id": t.id,
                "name": t.name,
                "description": t.description,
                "trigger_event": t.trigger_event,
                "expected_behavior": t.expected_behavior,
                "test_strategy": t.test_strategy
            } for t in templates[:max_count]]

        response = await asyncio.to_thread(
            self.mistral.client.chat.complete,
            model=self.mistral.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        content = self.mistral._clean_json_response(response.choices[0].message.content)
        selected_ids = json.loads(content)
        
        # Build scenario objects from selected templates
        scenarios = []
        for template_id in selected_ids[:max_count]:
            template = next((t for t in templates if str(t.id) == template_id), None)
            if template:
                scenarios.append({
                    "source_type": "template",
                    "template_id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "trigger_event": template.trigger_event,
                    "expected_behavior": template.expected_behavior,
                    "test_strategy": template.test_strategy
                })
        
        return scenarios
    
    async def _generate_contract_specific_scenarios(
        self,
        document_text: str,
        transaction_type: str,
        max_count: int = 3
    ) -> List[Dict]:
        """
        Generate scenarios based on specific provisions in THIS contract
        E.g., if earnout exists, generate earnout scenarios
        """
        if not self.mistral.client:
             return []

        prompt = f"""Analyze this {transaction_type} document and identify unique provisions that need scenario testing.

Document:
{document_text[:10000]}

Look for:
1. Earnout clauses → Generate earnout scenarios
2. Milestone payments → Generate milestone scenarios
3. Specific performance metrics → Generate metric scenarios
4. Unusual termination conditions → Generate custom termination scenarios
5. Special acceleration triggers → Generate acceleration scenarios

For each unique provision, create a scenario that tests edge cases or failure modes.

Return JSON array (max {max_count} scenarios):
[
  {{
    "name": "Achieves 2/3 of EBITDA earnout target",
    "description": "Company hits $6.6M EBITDA instead of target $10M",
    "trigger_event": "EBITDA reaches 66% of target in Year 1",
    "provision_tested": "Section 3.2 - Earnout calculation",
    "edge_case": "Does partial achievement trigger partial payment or nothing?",
    "expected_behavior": "Should have pro-rata earnout for partial achievement or clear threshold"
  }}
]

Only generate scenarios for provisions that actually exist in this document.
Return ONLY valid JSON array."""
        
        response = await asyncio.to_thread(
            self.mistral.client.chat.complete,
            model=self.mistral.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        
        content = self.mistral._clean_json_response(response.choices[0].message.content)
        scenarios_data = json.loads(content)
        
        # Format as scenario objects
        scenarios = []
        for s in scenarios_data[:max_count]:
            scenarios.append({
                "source_type": "contract_generated",
                "template_id": None,
                "name": s["name"],
                "description": s["description"],
                "trigger_event": s["trigger_event"],
                "expected_behavior": s.get("expected_behavior", ""),
                "test_strategy": {
                    "provision_tested": s.get("provision_tested"),
                    "edge_case": s.get("edge_case")
                }
            })
        
        return scenarios
    
    async def _test_scenario(
        self,
        scenario: Dict,
        document_text: str,
        analysis_id: str,
        db: Session
    ) -> ScenarioTest:
        """
        Test a single scenario against the document
        Returns pass/fail with reasoning
        """
        
        if not self.mistral.client:
             # Fallback mock result
            return ScenarioTest(
                analysis_id=analysis_id,
                source_type=scenario["source_type"],
                template_id=scenario.get("template_id"),
                name=scenario["name"],
                description=scenario.get("description"),
                trigger_event=scenario["trigger_event"],
                status="warning",
                reasoning={"details": "AI client not available for testing"},
                severity="medium"
            )

        prompt = f"""Test this scenario against the legal document.

DOCUMENT:
{document_text[:10000]}

SCENARIO TO TEST:
Name: {scenario['name']}
Trigger: {scenario['trigger_event']}
Expected Behavior: {scenario.get('expected_behavior', 'Document should handle this scenario fairly')}

{f"Test Strategy: {json.dumps(scenario.get('test_strategy', {}), indent=2)}" if scenario.get('test_strategy') else ""}

Analyze:
1. Does the document address this scenario?
2. What actually happens according to the contract?
3. Is there a conflict or gap?
4. Does it match expected behavior?

Return JSON:
{{
  "status": "pass" | "fail" | "warning",
  "decision_reasoning": "Why pass or fail",
  "relevant_clauses": ["Section 4.2", "Section 1.4"],
  "actual_outcome": "What the contract says happens",
  "conflict_if_any": "Description of conflict or gap",
  "severity": "critical" | "high" | "medium" | "low"
}}

Return ONLY valid JSON."""
        
        response = await asyncio.to_thread(
            self.mistral.client.chat.complete,
            model=self.mistral.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        content = self.mistral._clean_json_response(response.choices[0].message.content)
        result = json.loads(content)
        
        # Create ScenarioTest record
        scenario_test = ScenarioTest(
            analysis_id=analysis_id,
            source_type=scenario["source_type"],
            template_id=scenario.get("template_id"),
            name=scenario["name"],
            description=scenario.get("description"),
            trigger_event=scenario["trigger_event"],
            status=result["status"],
            reasoning=result,
            severity=result.get("severity", "medium"),
            affected_clauses=result.get("relevant_clauses", [])
        )
        
        db.add(scenario_test)
        db.commit()
        db.refresh(scenario_test)
        
        return scenario_test
    
    async def test_custom_scenario(
        self,
        analysis_id: str,
        natural_language_scenario: str,
        db: Session
    ) -> ScenarioTest:
        """
        User submits scenario in natural language
        Convert to structured format, then test
        """
        
        # Get analysis and document
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise ValueError("Analysis not found")
        
        document = db.query(Document).filter(
            Document.id == analysis.document_id
        ).first()
        
        if not self.mistral.client:
             raise ValueError("AI client unavailable")

        # Convert natural language to structured scenario
        prompt = f"""Convert this user's scenario question into a structured test case.

User's Question: "{natural_language_scenario}"

Return JSON:
{{
  "name": "Brief name for this scenario",
  "description": "Detailed description of what happens",
  "trigger_event": "Specific event that occurs",
  "expected_behavior": "What should happen in a fair contract"
}}

Examples:
User: "What if I get cancer and can't work for 6 months?"
→ {{
    "name": "Medical leave due to cancer",
    "description": "Founder diagnosed with cancer, requires 6 months treatment and recovery",
    "trigger_event": "Unable to perform duties due to serious medical condition",
    "expected_behavior": "Should not be terminated or lose shares due to medical leave; should have disability protection"
}}

Return ONLY valid JSON."""
        
        response = await asyncio.to_thread(
            self.mistral.client.chat.complete,
            model=self.mistral.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        content = self.mistral._clean_json_response(response.choices[0].message.content)
        structured_scenario = json.loads(content)
        
        # Add source info
        structured_scenario["source_type"] = "user_custom"
        structured_scenario["template_id"] = None
        
        # Test the scenario
        result = await self._test_scenario(
            structured_scenario,
            document.original_text,
            analysis_id,
            db
        )
        
        return result
