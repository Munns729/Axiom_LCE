"""
Test the analyze-quick endpoint directly to see the error
"""
import requests

BACKEND_URL = "http://localhost:8000"

print("Testing analyze-quick endpoint...")

try:
    with open("spine/tests/corpus/messy_2.docx", "rb") as f:
        files = {"file": ("messy_2.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        response = requests.post(f"{BACKEND_URL}/api/analyze-quick", files=files)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Success!")
        data = response.json()
        print(f"Analysis ID: {data.get('analysis_id')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print("Response:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Exception: {e}")
