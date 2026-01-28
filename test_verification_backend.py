"""
Quick test script for Verification Loop backend
Tests the /api/verify-assertion endpoint with a sample assertion
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_ASSERTION = "Founder keeps shares if Good Reason"

def test_verification_endpoint():
    """Test the verification endpoint with streaming"""
    
    print("=" * 60)
    print("VERIFICATION LOOP - Backend Test")
    print("=" * 60)
    
    # Step 1: Upload a test document
    print("\n1. Uploading test document...")
    
    try:
        with open("spine/tests/corpus/messy_2.docx", "rb") as f:
            files = {"file": ("messy_2.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            upload_response = requests.post(f"{BACKEND_URL}/api/upload", files=files)
            
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.status_code}")
            print(upload_response.text)
            return
        
        upload_data = upload_response.json()
        document_id = upload_data["document_id"]
        print(f"✅ Document uploaded: {document_id}")
        print(f"   Filename: {upload_data['filename']}")
        
    except FileNotFoundError:
        print("❌ Test document not found: spine/tests/corpus/messy_2.docx")
        return
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Step 2: Analyze the document (to get definitions)
    print("\n2. Analyzing document...")
    
    try:
        with open("spine/tests/corpus/messy_2.docx", "rb") as f:
            files = {"file": ("messy_2.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            analyze_response = requests.post(f"{BACKEND_URL}/api/analyze-quick", files=files)
        
        if analyze_response.status_code != 200:
            print(f"❌ Analysis failed: {analyze_response.status_code}")
            return
        
        print("✅ Document analyzed")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return
    
    # Step 3: Test verification endpoint
    print(f"\n3. Verifying assertion: '{TEST_ASSERTION}'")
    print("   Streaming events:\n")
    
    try:
        verify_response = requests.post(
            f"{BACKEND_URL}/api/verify-assertion/{document_id}",
            json={"assertion_text": TEST_ASSERTION},
            stream=True
        )
        
        if verify_response.status_code != 200:
            print(f"❌ Verification failed: {verify_response.status_code}")
            print(verify_response.text)
            return
        
        # Process streaming events
        event_count = 0
        for line in verify_response.iter_lines():
            if line:
                event_count += 1
                try:
                    event = json.loads(line.decode('utf-8'))
                    event_type = event.get('type', 'unknown')
                    
                    if event_type == 'thinking':
                        print(f"   💭 {event.get('message')}")
                    elif event_type == 'entity_found':
                        print(f"   ✓ Found entity: {event.get('entity')} at {event.get('location')}")
                    elif event_type == 'trace':
                        chain_length = len(event.get('chain', []))
                        print(f"   🔗 Logic chain built ({chain_length} nodes)")
                    elif event_type == 'conflict':
                        print(f"   ⚠️  CONFLICT: {event.get('details')}")
                        print(f"      Severity: {event.get('severity')}")
                    elif event_type == 'complete':
                        verdict = event.get('verdict')
                        summary = event.get('summary')
                        duration = event.get('duration_ms', 0)
                        
                        print(f"\n   {'✅' if verdict == 'pass' else '❌'} VERDICT: {verdict.upper()}")
                        print(f"   Summary: {summary}")
                        print(f"   Duration: {duration}ms")
                        print(f"   Verification ID: {event.get('verification_id')}")
                    elif event_type == 'error':
                        print(f"   ❌ ERROR: {event.get('message')}")
                        
                except json.JSONDecodeError as e:
                    print(f"   ⚠️  Failed to parse event: {line}")
        
        print(f"\n✅ Verification complete ({event_count} events received)")
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    print("\nStarting backend test...")
    print("Make sure backend is running: docker compose up backend\n")
    time.sleep(1)
    
    test_verification_endpoint()
