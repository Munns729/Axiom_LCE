"""
Simple Headless API Test Script
Tests the /analyze_logic endpoint with different scenarios
"""
import requests
import json
import sys

def test_scenario(name, contract_text, playbook, expected_warnings=True):
    """Test a single scenario"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Contract: {contract_text[:100]}...")
    print(f"Playbook: {playbook}")
    print("-" * 60)
    
    url = "http://localhost:3000/analyze_logic"
    
    files = {
        'file': ('test_contract.txt', contract_text.encode('utf-8'), 'text/plain')
    }
    data = {
        'playbook': json.dumps(playbook)
    }
    
    try:
        response = requests.post(url, files=files, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            warnings = result.get('warnings', [])
            
            print(f"✓ Status: SUCCESS")
            print(f"✓ Contract ID: {result.get('contract_id')}")
            print(f"✓ Warnings Found: {len(warnings)}")
            
            if warnings:
                print("\nWarnings:")
                for i, w in enumerate(warnings, 1):
                    print(f"\n  {i}. {w.get('issue')}")
                    print(f"     Severity: {w.get('severity')}")
                    print(f"     Snippet: {w.get('text_snippet')}")
                    print(f"     Fix: {w.get('remediation')}")
            else:
                print("\n✓ No conflicts detected - document matches playbook!")
            
            # Validate expectation
            if expected_warnings and not warnings:
                print("\n⚠️  WARNING: Expected warnings but got none!")
            elif not expected_warnings and warnings:
                print("\n⚠️  WARNING: Expected no warnings but got some!")
            else:
                print("\n✓ Result matches expectation")
                
            return True
        else:
            print(f"✗ FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ FAILED: Cannot connect to server")
        print("  Make sure Docker services are running:")
        print("  > docker compose up")
        return False
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║         Axiom LCE - Headless API Test Suite                 ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Test 1: Mismatch - Should produce warning
    test_scenario(
        name="Governing Law Mismatch",
        contract_text="This Agreement shall be governed by the laws of England and Wales.",
        playbook={"governing_law": "New York"},
        expected_warnings=True
    )
    
    # Test 2: Match - Should NOT produce warning
    test_scenario(
        name="Governing Law Match",
        contract_text="This Agreement shall be governed by the laws of New York.",
        playbook={"governing_law": "New York"},
        expected_warnings=False
    )
    
    # Test 3: Different jurisdiction mismatch
    test_scenario(
        name="Delaware vs California",
        contract_text="The Governing Law shall be the State of Delaware.",
        playbook={"governing_law": "California"},
        expected_warnings=True
    )
    
    # Test 4: No governing law clause
    test_scenario(
        name="No Governing Law Clause",
        contract_text="This is a simple agreement about services. Payment is due in 30 days.",
        playbook={"governing_law": "New York"},
        expected_warnings=False
    )
    
    # Test 5: Complex contract
    test_scenario(
        name="Complex Contract",
        contract_text="""
        MASTER SERVICE AGREEMENT
        
        1. PARTIES
        This Agreement is entered into between Company A and Company B.
        
        2. SERVICES
        The Provider shall deliver consulting services as described in Exhibit A.
        
        3. PAYMENT TERMS
        Payment shall be made within 30 days of invoice.
        
        4. GOVERNING LAW
        This Agreement shall be governed by and construed in accordance with 
        the laws of the State of Delaware, without regard to its conflict of law provisions.
        
        5. TERMINATION
        Either party may terminate this Agreement with 30 days written notice.
        """,
        playbook={"governing_law": "New York"},
        expected_warnings=True
    )
    
    print(f"\n{'='*60}")
    print("Testing Complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
