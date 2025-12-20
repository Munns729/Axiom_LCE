import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.structure_service import DocumentStructureService

async def test_structure_analysis():
    print("Initializing DocumentStructureService...")
    service = DocumentStructureService()
    
    # Sample legal text (simulated founder agreement snippet)
    text = """
    1. Definitions.
    1.1 "Cause" shall mean fraud, embezzlement, or conviction of a felony.
    1.2 "Good Reason" shall mean a material reduction in salary or relocation by more than 50 miles.
    
    4. Termination.
    4.1 Termination for Cause. The Company may terminate the Founder's employment for Cause (as defined in Section 1.1) at any time.
    4.2 Voluntary Resignation. If Founder resigns without Good Reason (as defined in Section 1.2), all unvested shares are forfeited.
    """
    
    print("\n--- Analyzing Structure ---")
    print(f"Input text length: {len(text)} chars")
    
    structure = await service.analyze_structure(text)
    
    if "error" in structure:
        print(f"ERROR: {structure['error']}")
        return

    clauses = structure.get("clauses", [])
    refs = structure.get("cross_references", [])
    
    print(f"\n✅ LLM found: {len(clauses)} clauses")
    print(f"✅ Cross-references: {len(refs)}")
    
    print("\nClauses Found:")
    for c in clauses:
        print(f"  [{c.get('number', '?')}] {c.get('type', 'unknown')}: {c.get('text', '')[:50]}...")
        if c.get('references_to'):
            print(f"      -> References: {c['references_to']}")

    print("\nCross-References Found:")
    for r in refs:
        print(f"  {r.get('from')} -> {r.get('to')} ('{r.get('phrase')}')")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_structure_analysis())
