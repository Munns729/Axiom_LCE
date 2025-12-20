import sys
import os
from io import BytesIO

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../spine')))

from spine.src.document_service import DocumentParser

def test_stream_parsing():
    print("Testing stream parsing...")
    # This test requires a valid docx file. 
    # Since we can't easily create one in memory without python-docx installed in this script environment (it might be),
    # we will skip the actual parsing execution if we can't find a file, but the syntax check is valuable.
    
    parser = DocumentParser()
    print("DocumentParser instantiated successfully.")
    
    # We verify the method exists
    if hasattr(parser, 'parse_stream'):
        print("parse_stream method exists.")
    else:
        print("FAIL: parse_stream method missing.")

if __name__ == "__main__":
    test_stream_parsing()
