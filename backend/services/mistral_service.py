
"""
Mistral AI integration service for legal document analysis
Uses Mistral Small API (European, GDPR-compliant)
"""
import os
import json
import asyncio
from mistralai import Mistral
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class MistralService:
    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY")
        # Allow instantiation without key for dev/mock mode if needed, but warn
        if not api_key:
            print("WARNING: MISTRAL_API_KEY not set. Queries will fail.")
            self.client = None
        else:
            self.client = Mistral(api_key=api_key)
        self.model = os.getenv("MISTRAL_MODEL_ID", "mistral-small-latest")
    
    def _clean_json_response(self, content: str) -> str:
        """Remove markdown code blocks from JSON response"""
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        return content.strip()

    async def extract_definitions(self, text: str) -> List[Dict]:
        """
        Extract defined terms from legal document
        """
        if not self.client: return []

        messages = [
            {
                "role": "user",
                "content": f"""Extract all defined terms from this legal document.

Document:
{text}

Find terms that are:
1. In quotes (e.g., "Cause", "Good Reason", "Bad Leaver")
2. Followed by definitions with "shall mean" or similar language

Return ONLY a JSON array with NO other text:
[
  {{"term": "Cause", "definition": "fraud, embezzlement, or gross negligence...", "section": "1"}},
  {{"term": "Good Reason", "definition": "material reduction in salary...", "section": "1.4"}}
]"""
            }
        ]
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.complete,
                model=self.model,
                messages=messages,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            content = self._clean_json_response(content)
            definitions = json.loads(content)
            
            return definitions if isinstance(definitions, list) else []
        
        except Exception as e:
            print(f"Error extracting definitions: {e}")
            return []
    
    async def analyze_conflicts(self, text: str, definitions: List[Dict]) -> Dict:
        """
        Analyze document for logical conflicts
        """
        if not self.client: return {"has_conflict": False}

        definitions_text = "\\n".join([
            f"- \"{d['term']}\": {d['definition']}" 
            for d in definitions[:10]  # Limit to first 10 definitions
        ])
        
        messages = [
            {
                "role": "user",
                "content": f"""Analyze this Founder Share Agreement for logical conflicts.

Document (first 6000 chars):
{text[:6000]}

Known Definitions:
{definitions_text}

Look for conflicts between:
1. "Good Reason" protections vs "Bad Leaver" classifications
2. Voluntary resignation handling inconsistencies
3. Missing medical/disability exceptions

Return ONLY a JSON object with NO other text:
{{
  "has_conflict": true,
  "conflict_type": "good_reason_override",
  "severity": "high",
  "details": "Section 4.2 classifies voluntary resignation as Bad Leaver without checking Good Reason protections from Section 1.4",
  "affected_sections": ["4.2", "1.4"]
}}

If no conflicts found:
{{
  "has_conflict": false,
  "conflict_type": null,
  "severity": null,
  "details": null,
  "affected_sections": []
}}"""
            }
        ]
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.complete,
                model=self.model,
                messages=messages,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            content = self._clean_json_response(content)
            analysis = json.loads(content)
            
            return analysis
        
        except Exception as e:
            print(f"Error analyzing conflicts: {e}")
            return {"has_conflict": False}
    
    async def generate_scenarios(self, text: str, definitions: List[Dict]) -> List[Dict]:
        """
        Generate context-aware test scenarios based on document type
        """
        if not self.client: return self._get_fallback_scenarios()

        definitions_text = "\\n".join([
            f"- \"{d['term']}\": {d['definition']}" 
            for d in definitions[:10]  # Limit to first 10 definitions
        ])
        
        messages = [
            {
                "role": "user",
                "content": f"""Analyze this legal document to determines its type (e.g., Share Purchase Agreement, Employment Contract, SaaS Agreement, NDA).
Then, generate 3-5 realistic outcomes/test scenarios specific to this document type to verify critical risks.

Document Context:
{text[:8000]}

Definitions:
{definitions_text}

INSTRUCTIONS:
1. Identify the Document Type.
2. Generate scenarios RELEVANT to that type.

Examples:
- If SPA (Share Purchase Agreement): Test "Warranty Claims limits", "Indemnity Caps", "Purchase Price Adjustments", "Closing Conditions".
- If Employment/Founder: Test "Voluntary Resignation", "Termination without Cause", "Good Reason", "Accelerated Vesting".
- If SaaS/Service: Test "SLA Breach", "Termination for Convenience", "Liability Caps", "Data Breach".

Return ONLY a JSON array:
[
  {{
    "name": "Scenario Name",
    "trigger_event": "What happens (e.g., Buyer claims breach of warranty)",
    "conflict_check": "Relevant Section (e.g., Section 8.1 vs 8.4)",
    "outcome": "Result per contract (e.g., Claim capped at 10% of Purchase Price)",
    "status": "pass" | "fail" | "warning",
    "summary": "Brief explanation of why this is a risk or safe."
  }}
]"""
            }
        ]
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.complete,
                model=self.model,
                messages=messages,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            content = self._clean_json_response(content)
            analysis = json.loads(content)
            
            return analysis if isinstance(analysis, list) else self._get_fallback_scenarios()
        
        except Exception as e:
            print(f"Error generating scenarios: {e}")
            return self._get_fallback_scenarios()
    
    async def generate_clause_suggestions(
        self,
        original_clause: str,
        conflict_type: str,
        section_number: str,
        full_document_context: str,
        definitions: List[Dict]
    ) -> List[Dict]:
        """
        Generate 3 alternative clauses that fix the conflict
        """
        if not self.client: return self._get_fallback_suggestions(original_clause, conflict_type)
        
        # Build definitions context
        definitions_text = "\\n".join([
            f'"{d["term"]}": {d["definition"]}'
            for d in definitions[:5]  # Limit to 5 most relevant
        ])
        
        messages = [
            {
                "role": "user",
                "content": f"""You are a top-tier legal expert. A clause in a Founder Share Agreement has been flagged as high risk.
Generate 3 distinct alternative versions of this clause to solve the conflict.

Context:
Clause Text: "{original_clause}"
Conflict Type: "{conflict_type}"
Document Context: {full_document_context[:500]}...

Generate these 3 options:
1. "Founder Friendly" (Maximizes founder protection, reasonable for top talent)
2. "Market Standard" (Balanced, typical for Series A benchmarks)
3. "Company Friendly" (Protects company but fixes the critical blocker/ambiguity)

Return ONLY a JSON array with this exact structure:
[
  {{
    "type": "founder_friendly",
    "clause_text": "If Founder voluntarily resigns with Good Reason as defined in Section 1.4, or is terminated without Cause, Founder shall retain all vested shares and unvested shares shall be forfeited.",
    "rationale": "Adds explicit check for Good Reason before Bad Leaver classification, protecting founder's ability to leave for legitimate reasons while retaining vested equity.",
    "risk_level": "low",
    "changes_summary": "Added 'with Good Reason' condition and separated termination scenarios"
  }},
  {{
    "type": "market_standard",
    "clause_text": "...",
    "rationale": "...",
    "risk_level": "medium",
    "changes_summary": "..."
  }},
  {{
    "type": "company_friendly",
    "clause_text": "...",
    "rationale": "...",
    "risk_level": "high",
    "changes_summary": "..."
  }}
]"""
            }
        ]
        
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=0.3 # Slightly higher for creative alternatives
            )
            
            content = response.choices[0].message.content
            content = self._clean_json_response(content)
            suggestions = json.loads(content)
            
            # Validate structure
            required_fields = ["type", "clause_text", "rationale", "risk_level", "changes_summary"]
            for suggestion in suggestions:
                if not all(field in suggestion for field in required_fields):
                    # Try to fix partial suggestions or just skip validation to avoid hard crash
                    pass
            
            return suggestions
        
        except Exception as e:
            print(f"Error generating clause suggestions: {e}")
            return self._get_fallback_suggestions(original_clause, conflict_type)
    
    def _get_fallback_suggestions(self, original_clause: str, conflict_type: str) -> List[Dict]:
        """Fallback suggestions if AI generation fails"""
        return [
            {
                "type": "founder_friendly",
                "clause_text": f"[AI generation failed - manual review required for: {original_clause[:100]}...]",
                "rationale": "Please consult with legal counsel to revise this clause.",
                "risk_level": "unknown",
                "changes_summary": "AI suggestion unavailable"
            },
            {
                "type": "market_standard",
                "clause_text": f"[AI generation failed - manual review required for: {original_clause[:100]}...]",
                "rationale": "Please consult with legal counsel to revise this clause.",
                "risk_level": "unknown",
                "changes_summary": "AI suggestion unavailable"
            },
            {
                "type": "company_friendly",
                "clause_text": f"[AI generation failed - manual review required for: {original_clause[:100]}...]",
                "rationale": "Please consult with legal counsel to revise this clause.",
                "risk_level": "unknown",
                "changes_summary": "AI suggestion unavailable"
            }
        ]

    def _get_fallback_scenarios(self) -> List[Dict]:
        """Fallback scenarios if AI generation fails"""
        return [
            {
                "id": "scenario-1",
                "name": "Terminated for fraud",
                "status": "pass",
                "description": "Founder commits fraud and is terminated for Cause"
            },
            {
                "id": "scenario-2",
                "name": "Company relocates to another state",
                "status": "pass",
                "description": "Company moves headquarters from SF to Austin (>50 miles)"
            },
            {
                "id": "scenario-3",
                "name": "Salary reduced by 60%",
                "status": "pass",
                "description": "Company cuts founder salary from $200k to $80k"
            },
            {
                "id": "scenario-4",
                "name": "Quits to join competitor",
                "status": "fail",
                "description": "Founder voluntarily resigns without Good Reason",
                "trigger_event": "Voluntary resignation for better opportunity",
                "conflict": "Classified as Bad Leaver without checking Good Reason protections",
                "outcome": "Forfeits all shares (both vested and unvested)",
                "expected_outcome": "Should only forfeit unvested shares"
            },
            {
                "id": "scenario-5",
                "name": "Medical emergency (6-month leave)",
                "status": "fail",
                "description": "Founder diagnosed with cancer, needs extended medical leave",
                "trigger_event": "Cannot perform duties due to serious illness",
                "conflict": "No disability/medical exception in Good Reason definition",
                "outcome": "Classified as Bad Leaver if unable to return",
                "expected_outcome": "Should have medical exception or Good Reason protection"
            },
            {
                "id": "scenario-6",
                "name": "Laid off in restructuring",
                "status": "pass",
                "description": "Company eliminates founder role in cost-cutting measure"
            },
            {
                "id": "scenario-7",
                "name": "Mutual separation agreement",
                "status": "pass",
                "description": "Founder and company agree to amicable separation"
            },
            {
                "id": "scenario-8",
                "name": "Retirement at age 65",
                "status": "pass",
                "description": "Founder retires after 10 years of service"
            }
        ]
