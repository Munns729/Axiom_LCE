import asyncio
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.verification_service import VerificationService
from services.document_service import DocumentService

async def main():
    service = VerificationService()
    
    # Path to the complex doc
    doc_path = os.path.join(os.getcwd(), 'spine', 'tests', 'corpus', 'series_a_complex.docx')
    
    from docx import Document
    doc = Document(doc_path)
    full_text = "\n".join([p.text for p in doc.paragraphs])
    
    # Mock definitions
    definitions = [
        {"term": "Bad Leaver", "definition": "voluntary resignation or dismissal for Cause", "section": "1.1"},
        {"term": "Good Reason", "definition": "material reduction in duties...", "section": "1.1"},
        {"term": "Founder", "definition": "John Doe and Jane Smith", "section": "1.1"}
    ]
    
    assertions = [
        "Founder keeps shares if Good Reason",  # Expected: FAIL (due to 4.3 override)
        "Governing law is Delaware",             # Expected: PASS
        "The Founders liability is capped",       # Expected: PASS (Section 5.2/5.3)
        "Shares are subject to reverse vesting"   # Expected: PASS (Section 3.1)
    ]
    
    with open('assertion_test_results.log', 'w') as f:
        for assertion in assertions:
            log_line = f"\nTesting assertion: '{assertion}'\n" + "-"*50 + "\n"
            print(log_line, end='')
            f.write(log_line)
            
            async for event in service.verify_assertion_stream(full_text, assertion, definitions):
                if event['type'] == 'thinking':
                    pass
                elif event['type'] == 'entity_found':
                    msg = f"[ENTITY] {event['entity']} -> {event['location']}\n"
                    print(msg, end='')
                    f.write(msg)
                elif event['type'] == 'conflict':
                    msg = f"[CONFLICT] {event['severity'].upper()}: {event['details']}\n"
                    print(msg, end='')
                    f.write(msg)
                elif event['type'] == 'complete':
                    msg = f"[RESULT] Verdict: {event['verdict'].upper()}\n"
                    msg += f"[RESULT] Summary: {event['summary']}\n"
                    if event.get('details'):
                        msg += f"[DETAILS] {event['details']}\n"
                    if event.get('expected_outcome'):
                        msg += f"[EXPECTED] {event['expected_outcome']}\n"
                    if event.get('actual_outcome'):
                        msg += f"[ACTUAL] {event['actual_outcome']}\n"
                    print(msg, end='')
                    f.write(msg)

if __name__ == "__main__":
    asyncio.run(main())
