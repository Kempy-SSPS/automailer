import json
from lib.utils.safe_file_get import safe_file_get


def get_sorted_events_of_type(desired_event_type):
    event_options = []
    EVENTS = safe_file_get("config/events.json", {})
    event_data = safe_file_get("data/event_data.json", {})
    if EVENTS == {}:
        raise Exception("No events were defined")
    
    events_by_type = {}

    for event_name, event_details in EVENTS.items():
        event_type = event_details["event_type"]
        if desired_event_type != event_type:
            continue
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



    return event_options
        




def get_auto_updated_questions():
    auto_update_questions = []
    with open("config/templates/form_template.json", "r") as f:
        form_template = json.loads(f.read())
        for i, question in enumerate(form_template["questions"]):
            if question.get("auto_update", False) is not True:
                continue
            question["index"] = i
            auto_update_questions.append(question)
        return auto_update_questions


def build_update_form_configs():
    update_form_configs = []
    auto_updated_questions = get_auto_updated_questions()
    for auto_updated_question in auto_updated_questions:
        update_form_configs.append(
        {
            "index": auto_updated_question["index"],
            "question": {
                "type": "radio",
                "name": auto_updated_question["name"],
                "description": auto_updated_question["description"],
                "required": auto_updated_question["required"],
                "options": get_sorted_events_of_type(auto_updated_question["auto_update_event_type"]),
            }
        }
        )
    return update_form_configs

