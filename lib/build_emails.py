from jinja2 import Template
from config.templates.email_templates import templates
from lib.utils.get_events import get_events
from lib.utils.safe_file_get import safe_file_get

EVENTS = get_events()
EVENT_DATA = safe_file_get('./data/event_data.json', [])

def get_remaining_places():
    events_remaing_capacity = EVENTS
    for event_name, event_details in EVENTS.items():
        this_event_capacity = EVENTS[event_name]["capacity"]
        events_remaing_capacity[event_name]["remaining"] = this_event_capacity
        if event_name not in EVENT_DATA:
            continue
        events_remaing_capacity[event_name]["remaining"] -= EVENT_DATA[event_name]["signed_up"]
    return events_remaing_capacity

def get_nonfull_events_by_type(event_type, remaining_places=get_remaining_places()):
    nonfull_events = {}
    for event_name, event_details in remaining_places.items():
        if event_details["event_type"] != event_type or event_details["remaining"] == 0:
            continue
        nonfull_events[event_name] = event_details

    return nonfull_events

def build_sub_alternatives(event_type):
    
    alternatives = []
    nonfull_events = get_nonfull_events_by_type(event_type)
    if len(nonfull_events) == 0:
        return None
    for event_name in nonfull_events.keys():
        alternatives.append(event_name)
    return alternatives
    
        


def build_email(response):
    event_name = response["event_name"]
    if response["is_sub"]:
        event_type = EVENTS[event_name]["event_type"]
        email = {
            "recipient_address" : response["participant_email"],
            "subject": Template(templates["sub"]["subject"]).render(event_name=event_name),
            "body": Template(templates["sub"]["body"]).render(
                event_name=event_name,
                event_type=event_type,
                event_date=EVENTS[event_name]["event_date"],
                sub_alternatives=build_sub_alternatives(event_type)
            )
        }
    else: 
        email = {
            "recipient_address" : response["participant_email"],
            "subject": Template(templates["participant"]["subject"]).render(event_name=event_name),
            "body": Template(templates["participant"]["body"]).render(
                event_name=event_name,
                event_type=EVENTS[event_name]["event_type"],
                event_date=EVENTS[event_name]["event_date"]
            )
        }
    emails = []
    emails.append(email)
    parental_email = email
    parental_email["recipient_address"] = response["parent_email"]
    emails.append(parental_email)
    return emails