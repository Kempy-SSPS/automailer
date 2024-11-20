import os
import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from lib.utils.get_events import get_events
from lib.utils.safe_file_get import safe_file_get
from lib.form.update.update_form import main as update_form

if not os.path.exists('/.dockerenv'):
    from dotenv import load_dotenv
    try:
        load_dotenv("./.env")
    except Exception as e:
        print(f"Error loading .env file: {str(e)}")
        exit(1)
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
RANGE_NAME = os.environ.get("RANGE_NAME")
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def safe_get_index(array, index):
    try:
        value = array[index]
        return value
    except IndexError:
        return None

def simplify_response(response):
    simplified_response = {
        "response_events": response["response_events"],
        "participant_email": response["participant_email"],
        "parent_email": response["parent_email"],
    }
    return simplified_response

def get_purpose_indecies():
    purpose_indecies = {}
    with open("config/templates/form_template.json", "r") as f:
        form_template = json.loads(f.read())
    for index, question in enumerate(form_template["questions"]):
        if "purpose" not in question:
            continue
        purpose_indecies[question["purpose"]] = index
    return purpose_indecies


def get_event_names(raw_response):
    event_names = []
    purpose_indecies = get_purpose_indecies()
    camp_names = ["event_name_hcw", "event_name_hln", "event_name_t"]
    for camp_name in camp_names:
        if camp_name not in purpose_indecies:
            continue
        event_name_date = raw_response[purpose_indecies[camp_name]].split(" (")[0]
        if event_name_date == "":
            continue
        event_names.append(event_name_date)
    # for camp_name in camp_names:
    #     if camp_name not in raw_response:
    #         continue
    #     event_names.append(raw_response[camp_name])
    print(f"got event name: {event_names}")
    return event_names


# def determine_sub(event_name):
#     is_sub: bool
#     current_event_data = safe_file_get('./data/event_data.json', {})
#     EVENTS = get_events()
#     requested_event_data = current_event_data.get(
#     event_name, {"signed_up": 0, "subs": 0})
#     requested_event_full = requested_event_data["signed_up"] >= EVENTS[event_name]["capacity"]
#     is_sub = requested_event_full
#     if requested_event_full:
#         requested_event_data["subs"] += 1
#     else:
#         requested_event_data["signed_up"] += 1
#     current_event_data[event_name] = requested_event_data
#     with open('./data/event_data.json', 'w') as file:
#         file.write(json.dumps(current_event_data, indent=4))
#     return is_sub


def determine_sub(event_name):
    is_sub: bool
    current_event_data = safe_file_get('./data/event_data.json', {})
    EVENTS = get_events()
    
    if isinstance(event_name, dict):
        event_name = event_name.get("event_name", "")
    
    requested_event_data = current_event_data.get(event_name, {"signed_up": 0, "subs": 0})
    requested_event_full = requested_event_data["signed_up"] >= EVENTS[event_name]["capacity"]
    is_sub = requested_event_full
    if requested_event_full:
        requested_event_data["subs"] += 1
    else:
        requested_event_data["signed_up"] += 1
    current_event_data[event_name] = requested_event_data
    with open('./data/event_data.json', 'w') as file:
        file.write(json.dumps(current_event_data, indent=4))
    return is_sub


def get_response_events(event_names):
    response_events = []
    for event_name in event_names:
        response_events.append(
            {
                "event_name": event_name,
                "is_sub": determine_sub(event_name),
            }
        )

    return response_events



def main():
    creds = Credentials.from_service_account_file(
        './config/credentials.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    all_responses = result.get('values', [])
    for response in all_responses:
        print(response)

    current_responses = safe_file_get('./data/responses.json', [])
    # current_event_data = safe_file_get('./data/event_data.json', {})
    purpose_indecies = get_purpose_indecies()
    
    new_responses = []
    for raw_response in all_responses:
        if raw_response == []:
            continue
        response = {
            "response_events": get_response_events(get_event_names(raw_response)),
            "participant_email": raw_response[purpose_indecies["participant_email"]],
            "parent_email": raw_response[purpose_indecies["parent_email"]],
        }
        is_continue = False
        for current_response in current_responses:
            if simplify_response(current_response) == simplify_response(response):
                is_continue = True
        if is_continue:
            continue
        for single_event_name in response["response_events"]:
            singlefied_response = response.copy()
            singlefied_response["response_events"] = single_event_name
            singlefied_response["is_sub"] = determine_sub(single_event_name)
            # requested_event_data = current_event_data.get(
            #     singlefied_response['event_name'], {"signed_up": 0, "subs": 0})
            # requested_event_full = requested_event_data["signed_up"] >= EVENTS[singlefied_response['event_name']]["capacity"]
            # singlefied_response['is_sub'] = requested_event_full
            # if requested_event_full:
            #     requested_event_data["subs"] += 1
            # else:
            #     requested_event_data["signed_up"] += 1
            # current_event_data[singlefied_response['event_name']] = requested_event_data
            # with open('./data/event_data.json', 'w') as file:
            #     file.write(json.dumps(current_event_data, indent=4))
        new_responses.append(response)

    with open('./data/responses.json', 'w') as file:
        file.write(json.dumps(current_responses + new_responses, indent=4))
    update_form()

    return(new_responses)

