import json
def get_events():
    with open('./config/events.json', 'r') as file:
        events = json.loads(file.read())
        return events