"""
Simplified verification test - tests verification endpoint directly
Uses mock data instead of requiring full analysis
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_verification_simple():
    """Test verification endpoint with minimal setup"""
    
    print("=" * 60)
    print("VERIFICATION LOOP - Simplified Test")
    print("=" * 60)
    
    # Upload document
    print("\n1. Uploading test document...")
    try:
        with open("spine/tests/corpus/messy_2.docx", "rb") as f:
            files = {"file": ("messy_2.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            upload_response = requests.post(f"{BACKEND_URL}/api/upload", files=files)
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.status_code}")
            return
        
        document_id = upload_response.json()["document_id"]
        print(f"✅ Document uploaded: {document_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test verification directly (will work even without analysis)
    print(f"\n2. Testing verification endpoint...")
    print(f"   Assertion: 'Founder keeps shares if Good Reason'\n")
    
    try:
        verify_response = requests.post(
            f"{BACKEND_URL}/api/verify-assertion/{document_id}",
            json={"assertion_text": "Founder keeps shares if Good Reason"},
            stream=True,
            timeout=30
        )
        
        if verify_response.status_code != 200:
            print(f"❌ Verification failed: {verify_response.status_code}")
            print(verify_response.text)
            return
        
        print("   Streaming events:\n")
        
        for line in verify_response.iter_lines():
            if line:
                try:
                    event = json.loads(line.decode('utf-8'))
                    event_type = event.get('type')
                    
                    if event_type == 'thinking':
                        print(f"   💭 {event.get('message')}")
                    elif event_type == 'entity_found':
                        print(f"   ✓ {event.get('entity')} → {event.get('location', 'Unknown')[:60]}")
                    elif event_type == 'trace':
                        print(f"   🔗 Logic chain: {len(event.get('chain', []))} nodes")
                    elif event_type == 'conflict':
                        print(f"   ⚠️  {event.get('severity').upper()}: {event.get('details')[:80]}")
                    elif event_type == 'complete':
                        verdict = event.get('verdict', 'unknown')
                        icon = '✅' if verdict == 'pass' else '❌' if verdict == 'fail' else '⚪'
                        print(f"\n   {icon} VERDICT: {verdict.upper()}")
                        print(f"   {event.get('summary', 'No summary')[:100]}")
                        print(f"   Duration: {event.get('duration_ms', 0)}ms")
                    elif event_type == 'error':
                        print(f"   ❌ {event.get('message')}")
                        
                except Exception as e:
                    print(f"   ⚠️  Parse error: {e}")
        
        print("\n✅ Verification test complete!")
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_verification_simple()
