"""
Verification Service for Assertion-Based Logic Checking

This service handles the core "Verification Loop" functionality:
- Parses natural language assertions from users
- Extracts key entities and conditions
- Compares against document AST and definitions
- Generates logic traces showing causality chains
- Streams "thought tokens" during processing
"""

import asyncio
import time
import re
from typing import Dict, List, Optional, AsyncGenerator
from .mistral_service import MistralService


class VerificationService:
    def __init__(self):
        self.mistral = MistralService()
    
    async def verify_assertion_stream(
        self,
        document_text: str,
        assertion_text: str,
        definitions: List[Dict],
        document_tree: Optional[Dict] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Stream verification events in real-time (SSE-compatible)
        
        Yields events:
        - {"type": "thinking", "message": "..."}
        - {"type": "entity_found", "entity": "...", "location": "..."}
        - {"type": "conflict", "severity": "...", "details": "..."}
        - {"type": "trace", "chain": [...]}
        - {"type": "complete", "verdict": "pass|fail|ambiguous", "summary": "..."}
        """
        start_time = time.time()
        
        # Step 1: Initial thinking
        yield {
            "type": "thinking",
            "message": f"Analyzing assertion: \"{assertion_text}\"",
            "timestamp": 0
        }
        
        await asyncio.sleep(0.3)  # Simulate processing
        
        # Step 2: Parse assertion into structured query
        yield {
            "type": "thinking",
            "message": "Extracting key entities and conditions...",
            "timestamp": int((time.time() - start_time) * 1000)
        }
        
        parsed_assertion = await self._parse_assertion(assertion_text)
        
        # Step 3: Search for entities in document
        for entity in parsed_assertion.get("entities", []):
            yield {
                "type": "thinking",
                "message": f"Searching for '{entity}' in document...",
                "timestamp": int((time.time() - start_time) * 1000)
            }
            
            # Find entity in definitions or document
            found_location = self._find_entity_in_document(
                entity, 
                document_text, 
                definitions
            )
            
            if found_location:
                yield {
                    "type": "entity_found",
                    "entity": entity,
                    "location": found_location,
                    "timestamp": int((time.time() - start_time) * 1000)
                }
            
            await asyncio.sleep(0.2)
        
        # Step 4: Build logic trace
        yield {
            "type": "thinking",
            "message": "Building logic chain...",
            "timestamp": int((time.time() - start_time) * 1000)
        }
        
        logic_trace = await self._build_logic_trace(
            parsed_assertion,
            document_text,
            definitions
        )
        
        yield {
            "type": "trace",
            "chain": logic_trace["chain"],
            "timestamp": int((time.time() - start_time) * 1000)
        }
        
        # Step 5: Detect conflicts
        yield {
            "type": "thinking",
            "message": "Checking for logical conflicts...",
            "timestamp": int((time.time() - start_time) * 1000)
        }
        
        conflict_result = await self._detect_conflicts(
            parsed_assertion,
            logic_trace,
            document_text
        )
        
        if conflict_result["has_conflict"]:
            yield {
                "type": "conflict",
                "severity": conflict_result["severity"],
                "details": conflict_result["details"],
                "conflicting_clauses": conflict_result.get("clauses", []),
                "timestamp": int((time.time() - start_time) * 1000)
            }
        
        # Step 6: Final verdict
        verdict = "fail" if conflict_result["has_conflict"] else "pass"
        
        yield {
            "type": "complete",
            "verdict": verdict,
            "summary": conflict_result.get("summary", "Verification complete"),
            "duration_ms": int((time.time() - start_time) * 1000),
            "logic_trace": logic_trace,
            "parsed_assertion": parsed_assertion
        }
    
    async def _parse_assertion(self, assertion_text: str) -> Dict:
        """
        Parse natural language assertion into structured format
        
        Example:
        Input: "Founder keeps shares if Good Reason"
        Output: {
            "entities": ["Founder", "shares", "Good Reason"],
            "condition": "if Good Reason",
            "expected_outcome": "Founder keeps shares",
            "assertion_type": "conditional"
        }
        """
        # Use Mistral to parse the assertion
        result = await self.mistral.parse_assertion(assertion_text)
        return result
    
    def _find_entity_in_document(
        self, 
        entity: str, 
        document_text: str, 
        definitions: List[Dict]
    ) -> Optional[str]:
        """
        Find where an entity is defined or mentioned in the document
        Returns section reference or None
        """
        # First check definitions
        for defn in definitions:
            if entity.lower() in defn.get("term", "").lower():
                return f"Definition: {defn.get('section', 'Unknown')}"
        
        # Then search document text (simple regex for now)
        # In production, use AST node IDs
        pattern = re.compile(rf'\b{re.escape(entity)}\b', re.IGNORECASE)
        match = pattern.search(document_text)
        
        if match:
            # Find approximate section (simplified)
            context_start = max(0, match.start() - 50)
            context = document_text[context_start:match.start() + 50]
            return f"Found in context: ...{context}..."
        
        return None
    
    async def _build_logic_trace(
        self,
        parsed_assertion: Dict,
        document_text: str,
        definitions: List[Dict]
    ) -> Dict:
        """
        Build causality chain showing how assertion flows through document logic
        
        Returns:
        {
            "chain": [
                {"node": "Assertion", "text": "...", "type": "input"},
                {"node": "Definition: Good Reason", "text": "...", "type": "definition"},
                {"node": "Clause 4.2", "text": "...", "type": "clause"},
                {"node": "Outcome", "text": "...", "type": "result"}
            ]
        }
        """
        chain = []
        
        # Start with assertion
        chain.append({
            "node": "User Assertion",
            "text": parsed_assertion.get("expected_outcome", ""),
            "type": "input",
            "status": "neutral"
        })
        
        # Add relevant definitions
        for entity in parsed_assertion.get("entities", []):
            for defn in definitions:
                if entity.lower() in defn.get("term", "").lower():
                    chain.append({
                        "node": f"Definition: {defn['term']}",
                        "text": defn.get("definition", ""),
                        "type": "definition",
                        "status": "neutral",
                        "section": defn.get("section")
                    })
        
        # Use Mistral to find relevant clauses and build chain
        relevant_clauses = await self.mistral.find_relevant_clauses(
            document_text,
            parsed_assertion
        )
        
        for clause in relevant_clauses:
            chain.append({
                "node": clause.get("section", "Unknown Clause"),
                "text": clause.get("text", ""),
                "type": "clause",
                "status": "neutral"
            })
        
        return {"chain": chain}
    
    async def _detect_conflicts(
        self,
        parsed_assertion: Dict,
        logic_trace: Dict,
        document_text: str
    ) -> Dict:
        """
        Detect if the assertion conflicts with document logic
        
        Returns:
        {
            "has_conflict": bool,
            "severity": "high|medium|low",
            "details": "...",
            "clauses": ["4.2", ...],
            "summary": "..."
        }
        """
        # Use Mistral to analyze the logic chain for conflicts
        conflict_analysis = await self.mistral.analyze_assertion_conflict(
            parsed_assertion,
            logic_trace,
            document_text
        )
        
        return conflict_analysis
