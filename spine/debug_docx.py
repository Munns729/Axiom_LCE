from docx import Document
import os

path = "spine/tests/corpus/messy_1.docx"
doc = Document(path)

for p in doc.paragraphs:
    print(f"Text: {p.text[:20]}")
    print(f"Dir element: {dir(p._element)}")
    # Try to find an ID
    # print(f"Element ID property: {p._element.id}") # This likely crashes if it doesn't exist
    print(f"Get paraId: {p._element.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}paraId')}")
    print("-" * 20)
