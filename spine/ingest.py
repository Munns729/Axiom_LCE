import sys
import os
# Add the current directory to sys.path so we can import spine
sys.path.append(os.getcwd())

from spine.src.document_service import DocumentParser

def main():
    if len(sys.argv) < 2:
        print("Usage: python spine/ingest.py <path_to_docx>")
        sys.exit(1)

    filepath = sys.argv[1]
    print(f"Ingesting: {filepath}")

    parser = DocumentParser()
    try:
        tree = parser.load(filepath)
        print("Parsing Successful! Tree Structure:")
        parser.print_tree(tree)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
