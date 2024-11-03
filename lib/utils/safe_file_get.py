import os
import json

def safe_file_get(file_path, default_value):
    if not os.path.exists(file_path):
        return default_value
    with open(file_path, 'r') as file:
        file_content = file.read()
        if file_content == "":
            return default_value
        return json.loads(file_content)