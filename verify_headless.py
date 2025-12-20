import requests
import json
import time
import sys

# wait for services to be ready
print("Waiting 5s for services to stabilize...")
time.sleep(5)

url = "http://localhost:3000/analyze_logic"
contract_text = "The Governing Law shall be the laws of England."
playbook = {"governing_law": "New York"}

files = {
    'file': ('test_contract.txt', contract_text.encode('utf-8'), 'text/plain')
}
data = {
    'playbook': json.dumps(playbook)
}

print(f"Test Configuration:")
print(f"  Target: {url}")
print(f"  Contract Text: '{contract_text}'")
print(f"  Playbook: {playbook}")
print("-" * 50)

try:
    print(f"Sending POST request...")
    response = requests.post(url, files=files, data=data)
    
    print(f"Status Code: {response.status_code}")
    print("-" * 50)
    
    if response.status_code == 200:
        print("SUCCESS! Response JSON:")
        print(json.dumps(response.json(), indent=2))
    else:
        print("FAILED. Response Body:")
        print(response.text)

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    sys.exit(1)
