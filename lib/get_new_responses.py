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
        "event_name": response["event_name"],
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



def main():
    creds = Credentials.from_service_account_file(
        './config/credentials.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    all_responses = result.get('values', [])

    current_responses = safe_file_get('./data/responses.json', [])
    current_event_data = safe_file_get('./data/event_data.json', {})
    purpose_indecies = get_purpose_indecies()
    EVENTS = get_events()
    new_responses = []
    for raw_response in all_responses:
        if raw_response == []:
            continue
        response = {
            "event_name": raw_response[purpose_indecies["event_name"]].split("(")[0].strip(),
            "participant_email": raw_response[purpose_indecies["participant_email"]],
            "parent_email": raw_response[purpose_indecies["parent_email"]],
            "day_before_notified": False
        }
        is_continue = False
        for current_response in current_responses:
            if simplify_response(current_response) == simplify_response(response):
                is_continue = True
        if is_continue:
            continue
        requested_event_data = current_event_data.get(
            response['event_name'], {"signed_up": 0, "subs": 0})
        requested_event_full = requested_event_data["signed_up"] >= EVENTS[response['event_name']]["capacity"]
        response['is_sub'] = requested_event_full
        if requested_event_full:
            requested_event_data["subs"] += 1
        else:
            requested_event_data["signed_up"] += 1
        current_event_data[response['event_name']] = requested_event_data
        new_responses.append(response)
        with open('./data/event_data.json', 'w') as file:
            file.write(json.dumps(current_event_data, indent=4))

    with open('./data/responses.json', 'w') as file:
        file.write(json.dumps(current_responses + new_responses, indent=4))
    update_form()

    return(new_responses)

