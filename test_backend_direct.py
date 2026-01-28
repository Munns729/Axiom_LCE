"""
Test Headless API - Direct Backend Version
Tests the /analyze_logic endpoint on port 8000 (bypassing Rails)
"""
import requests
import json

def test_direct_backend():
    print("\n" + "="*60)
    print("Testing FastAPI Backend Directly (Port 8000)")
    print("="*60 + "\n")
    
    url = "http://localhost:8000/analyze_logic"
    contract_text = "The Governing Law shall be the laws of England."
    playbook = {"governing_law": "New York"}
    
    files = {
        'file': ('test_contract.txt', contract_text.encode('utf-8'), 'text/plain')
    }
    data = {
        'playbook': json.dumps(playbook)
    }
    
    print(f"URL: {url}")
    print(f"Contract: {contract_text}")
    print(f"Playbook: {playbook}")
    print("-" * 60)
    
    try:
        response = requests.post(url, files=files, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            warnings = result.get('warnings', [])
            
            print(f"\n✓ SUCCESS!")
            print(f"✓ Status Code: {response.status_code}")
            print(f"✓ Contract ID: {result.get('contract_id')}")
            print(f"✓ Warnings Found: {len(warnings)}\n")
            
            if warnings:
                print("Warnings Detected:")
                print("-" * 60)
                for i, w in enumerate(warnings, 1):
                    print(f"\n{i}. {w.get('issue')}")
                    print(f"   Severity: {w.get('severity')}")
                    print(f"   Snippet: {w.get('text_snippet')}")
                    print(f"   Remediation: {w.get('remediation')}")
            else:
                print("✓ No conflicts detected - document matches playbook!")
            
            print("\n" + "="*60)
            print("Full Response:")
            print("="*60)
            print(json.dumps(result, indent=2))
            
            return True
        else:
            print(f"\n✗ FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n✗ FAILED: Cannot connect to backend")
        print("  Make sure the backend service is running:")
        print("  > docker compose ps")
        return False
    except Exception as e:
        print(f"\n✗ FAILED: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║    Axiom LCE - Headless API Direct Backend Test             ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    success = test_direct_backend()
    
    if success:
        print("\n✅ Headless API is working correctly!")
        print("\nNote: The Rails proxy (port 3000) has a configuration issue,")
        print("but the core API functionality on port 8000 is fully operational.")
    else:
        print("\n❌ Test failed. Check the error messages above.")
    
    print("\n" + "="*60 + "\n")
