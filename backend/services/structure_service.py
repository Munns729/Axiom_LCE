import json
import asyncio
from typing import Dict, List, Optional
from .mistral_service import MistralService

class DocumentStructureService:
    """
    LLM-powered document structure analysis
    More robust than regex, handles edge cases
    """
    def __init__(self):
        self.mistral = MistralService()

    async def analyze_structure(self, text: str) -> Dict:
        """
        Identify clauses, cross-references, definitions via LLM.
        """
        if not self.mistral.client:
            return {"clauses": [], "cross_references": [], "error": "Mistral client not authenticated"}

        prompt = f"""Analyze this legal document structure.

Document:
{text}

Return JSON mapping each clause to its properties:
{{
  "clauses": [
    {{
      "id": "section_1_2",
      "type": "section",
      "number": "1.2",
      "title": "Definition of Cause",
      "text": "For purposes of this Agreement, 'Cause' shall mean...",
      "start_char": 450,
      "end_char": 678,
      "referenced_by": ["section_4_2", "section_6_1"],
      "references_to": ["section_1_1"]
    }}
  ],
  "cross_references": [
    {{"from": "section_4_2", "to": "section_1_2", "phrase": "as defined in Section 1.2"}}
  ]
}}

Be extremely precise about character positions.
Return ONLY valid JSON.
"""

        try:
            # We use the existing MistralService client
            # mimicking the user's requested call, but adapting to the library we have
            response = await asyncio.to_thread(
                self.mistral.client.chat.complete,
                model=self.mistral.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"} # Attempt to use JSON mode
            )
            
            content = response.choices[0].message.content
            # Use MistralService's cleaner just in case
            content = self.mistral._clean_json_response(content)
            return json.loads(content)
            
        except Exception as e:
            print(f"Error analyzing structure: {e}")
            return {"clauses": [], "cross_references": [], "error": str(e)}

    async def validate_edit(
        self,
        original_text: str,
        structure: Dict,
        clause_id: str,
        new_clause_text: str
    ) -> Dict:
        """
        Validate that replacing a clause won't break the document.
        Checks for: broken references, undefined terms, semantic shifts.
        """
        if not self.mistral.client:
            return {"is_safe": False, "error": "Mistral client unavailable"}

        # Find the clause in the structure
        clauses = structure.get("clauses", [])
        clause = next((c for c in clauses if c["id"] == clause_id), None)
        
        if not clause:
            return {"is_safe": False, "error": f"Clause {clause_id} not found in structure"}

        # Find what references this clause
        referenced_by_ids = clause.get("referenced_by", [])
        referencing_clauses = [c for c in clauses if c["id"] in referenced_by_ids]

        prompt = f"""Validate this legal document edit for safety.

ORIGINAL CLAUSE (Section {clause.get('number', '?')}):
{clause.get('text', '')}

PROPOSED REPLACEMENT:
{new_clause_text}

CLAUSES THAT REFERENCE THIS:
{json.dumps(referencing_clauses, indent=2)}

Check for breaking changes:
1. Does replacement remove defined terms still used elsewhere?
2. Does it change meaning in a way that breaks references?
3. Does it introduce new undefined terms?
4. Does numbering still make sense?

Return ONLY a JSON object:
{{
  "is_safe": true,
  "breaking_changes": [
    {{"issue": "Removes 'Cause' definition still used in Section 4.2", "severity": "high"}}
  ],
  "warnings": [
    {{"message": "New clause is more founder-friendly - verify intent", "severity": "low"}}
  ],
  "required_updates": [
    {{"clause_id": "section_4_2", "reason": "References outdated definition", "suggestion": "Update to reference new clause"}}
  ]
}}
"""
        try:
            response = await asyncio.to_thread(
                self.mistral.client.chat.complete,
                model=self.mistral.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = self.mistral._clean_json_response(response.choices[0].message.content)
            return json.loads(content)
        except Exception as e:
            print(f"Error validating edit: {e}")
            return {"is_safe": False, "error": str(e)}

    async def find_clause_by_conflict(self, text: str, conflict_description: str) -> Optional[Dict]:
        """
        Find the exact clause mentioned in a conflict description
        """
        if not self.mistral.client: return None

        prompt = f"""Given a legal document and a conflict description, identify the specific clause text that causes the conflict.

Document:
{text}

Conflict:
{conflict_description}

Return ONLY a JSON object:
{{
  "id": "section_num_if_available",
  "text": "Exact text of the problematic clause...",
  "number": "4.2"
}}
"""
        try:
            response = await asyncio.to_thread(
                self.mistral.client.chat.complete,
                model=self.mistral.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = self.mistral._clean_json_response(response.choices[0].message.content)
            return json.loads(content)
        except Exception as e:
            print(f"Error finding clause: {e}")
            return None
