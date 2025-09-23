from fastapi import UploadFile
import json
import os

CONTEXT_FILE_PATH = "user_context.json"  # or use a path under /data/

def export_context():
    if os.path.exists(CONTEXT_FILE_PATH):
        with open(CONTEXT_FILE_PATH, 'r') as f:
            return json.load(f)
    return {}

def import_context(uploaded_file: UploadFile):
    content = uploaded_file.file.read()
    data = json.loads(content)
    with open(CONTEXT_FILE_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    return {"status": "success", "message": "Context imported"}
