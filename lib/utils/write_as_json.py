import json

def write_as_json(path, data):
    with open(path, 'w') as file:
        file.write(json.dumps(data, indent=4))