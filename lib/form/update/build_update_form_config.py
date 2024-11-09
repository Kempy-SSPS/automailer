import json
from lib.utils.safe_file_get import safe_file_get


def get_sorted_events():
    event_options = []
    EVENTS = safe_file_get("config/events.json", {})
    event_data = safe_file_get("data/event_data.json", {})
    if EVENTS == {}:
        raise Exception("No events were defined")
    
    events_by_type = {}

    for event_name, event_details in EVENTS.items():
        event_type = event_details["event_type"]
        remaining_places = event_details["capacity"]
        if event_name in event_data:
            remaining_places -= event_data[event_name]["signed_up"]


        if remaining_places <= 0:
            event_message = f"{event_name} (Pouze náhradníci)"
        elif remaining_places == 1:
            event_message = f"{event_name} (Zbývá 1 místo)"
        elif remaining_places < 5:
            event_message = f"{event_name} (Zbývají {remaining_places} místa)"
        else:
            event_message = f"{event_name} (Zbývá {remaining_places} míst)"

        if event_type not in events_by_type:
            events_by_type[event_type] = []
        events_by_type[event_type].append(event_message)


    for event_type, events in events_by_type.items():
        event_options.extend(events)



    print(event_options)
    return event_options
        




def get_auto_updated_question():
    with open("config/templates/form_template.json", "r") as f:
        form_template = json.loads(f.read())
        for i, question in enumerate(form_template["questions"]):
            if question.get("auto_update", False) is not True:
                continue
            question["index"] = i
            return question


def build_update_form_config():
    auto_updated_question = get_auto_updated_question()
    update_form_config = {
        "index": auto_updated_question["index"],
        "question": {
            "type": "radio",
            "name": auto_updated_question["name"],
            "description": auto_updated_question["description"],
            "required": auto_updated_question["required"],
            "options": get_sorted_events(),
        }
    }
    print(update_form_config)
    return update_form_config

