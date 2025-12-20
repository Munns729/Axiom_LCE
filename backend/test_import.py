
import sys
import os
print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")
try:
    import models
    print(f"Imported models: {models}")
    print(f"Models file: {models.__file__}")
except Exception as e:
    print(f"Error importing models: {e}")

try:
    import models.schemas
    print(f"Imported models.schemas: {models.schemas}")
except Exception as e:
    print(f"Error importing models.schemas: {e}")
