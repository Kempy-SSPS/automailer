import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from lib.form.update.build_update_form_config import build_update_form_config

if not os.path.exists('/.dockerenv'):
    from dotenv import load_dotenv
    try:
        load_dotenv("./.env")
    except Exception as e:
        print(f"Error loading .env file: {str(e)}")
        exit(1)

# Constants
FORM_ID = os.environ.get("FORM_ID")
CREDENTIALS_PATH = 'config/credentials.json'


# Updated scopes for Google Forms API
SCOPES = [
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/forms.responses.readonly',
    'https://www.googleapis.com/auth/drive.file',
]

def get_service():
    """Create and return a Google Forms service object using service account credentials."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH, 
            scopes=SCOPES
        )
        service = build('forms', 'v1', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error creating service: {str(e)}")
        raise

def get_form_item(service, form_id, item_index):
    """Get the form item at the specified index."""
    try:
        form = service.forms().get(formId=form_id).execute()
        if 'items' not in form or item_index >= len(form['items']):
            raise ValueError(f"No question found at index {item_index}, ensure the form has been created and has enough questions")
        return form['items'][item_index]
    except Exception as e:
        print(f"Error getting form item: {str(e)}")
        raise

def update_question_in_place(service, form_id, item_index, question_data):
    """Update a specific question in place without deleting it."""
    try:
        # Get the existing item to preserve its ID
        existing_item = get_form_item(service, form_id, item_index)
        item_id = existing_item['itemId']

        # Prepare the update request based on question type
        update_request = {
            'requests': [{
                'updateItem': {
                    'item': {
                        'itemId': item_id,
                        'title': question_data['name'],
                        'description': question_data['description'],
                        'questionItem': {
                            'question': {
                                'required': question_data.get('required', False),
                            }
                        }
                    },
                    'location': {'index': item_index},
                    'updateMask': 'title,description,questionItem.question.required'
                }
            }]
        }

        # Add type-specific question properties
        if question_data['type'] == 'radio':
            update_request['requests'][0]['updateItem']['item']['questionItem']['question'].update({
                'choiceQuestion': {
                    'type': 'RADIO',
                    'options': [{'value': option} for option in question_data['options']]
                }
            })
            update_request['requests'][0]['updateItem']['updateMask'] += ',questionItem.question.choiceQuestion'
        elif question_data['type'] == 'text':
            update_request['requests'][0]['updateItem']['item']['questionItem']['question'].update({
                'textQuestion': {
                    'paragraph': False
                }
            })
            update_request['requests'][0]['updateItem']['updateMask'] += ',questionItem.question.textQuestion'

        # Execute the update
        response = service.forms().batchUpdate(
            formId=form_id,
            body=update_request
        ).execute()

        return response
    except Exception as e:
        print(f"Error updating question: {str(e)}")
        raise

def validate_question_type(existing_item, new_question_data):
    """Validate that the new question type matches the existing question type."""
    existing_question = existing_item.get('questionItem', {}).get('question', {})
    
    # Determine existing question type
    if 'choiceQuestion' in existing_question:
        existing_type = 'radio'
    elif 'textQuestion' in existing_question:
        existing_type = 'text'
    else:
        raise ValueError("Unsupported existing question type")

    if existing_type != new_question_data['type']:
        raise ValueError(
            f"Question type mismatch: Cannot change from {existing_type} to {new_question_data['type']}. "
            "This would break response collection."
        )

def main():
    
    config = build_update_form_config()
    question_index = config.get('index')
    question_data = config.get('question')

    if question_index is None or question_data is None:
        raise ValueError("Configuration must include 'index' and 'question' fields")

    service = get_service()

    # Get existing question to validate type
    existing_item = get_form_item(service, FORM_ID, question_index)
    validate_question_type(existing_item, question_data)

    # Update the question
    update_question_in_place(service, FORM_ID, question_index, question_data)
    print(f"Successfully updated question at index {question_index}")


if __name__ == "__main__":
    main()