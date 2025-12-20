import requests
import os

def test_live():
    url = "http://localhost:8000/upload"
    file_path = "spine/tests/corpus/messy_1.docx"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Uploading {file_path} to {url}...")
    with open(file_path, "rb") as f:
        files = {"file": ("messy_1.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        try:
            response = requests.post(url, files=files)
            print(f"Status Code: {response.status_code}")
            print("Response Body:")
            data = response.json()
            print(data)
            
            if "contract_id" in data:
                with open("latest_contract_id.txt", "w") as f:
                    f.write(data["contract_id"])
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    test_live()
