import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build



if not os.path.exists('/.dockerenv'):
    from dotenv import load_dotenv
    try:
        load_dotenv("./.env")
    except Exception as e:
        print(f"Error loading .env file: {str(e)}")
        exit(1)

FORM_ID = os.environ.get("FORM_ID")
CREDENTIALS_PATH = 'config/credentials.json'
TEMPLATE_PATH = "config/templates/form_template.json"
with open(TEMPLATE_PATH, "r") as f:
    FROM_TEMPLATE = json.loads(f.read())


SCOPES = [
    'https://www.googleapis.com/auth/forms.body',  # Permission to read/write form content
    'https://www.googleapis.com/auth/forms.responses.readonly',  # Permission to read responses
    'https://www.googleapis.com/auth/drive.file',  # Permission to access specific files
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

def delete_all_questions(service, form_id):
    """Delete all existing questions in the form."""
    try:
        # Get current form
        form = service.forms().get(formId=form_id).execute()
        
        # If there are items, delete them
        if 'items' in form:
            # Create delete requests for each item, using index-based deletion
            delete_requests = [
                {
                    'deleteItem': {
                        'location': {'index': 0}  # Always delete at index 0 since items shift up
                    }
                } 
                for _ in form['items']
            ]
            
            if delete_requests:
                update = {'requests': delete_requests}
                service.forms().batchUpdate(formId=form_id, body=update).execute()
    except Exception as e:
        print(f"Error deleting questions: {str(e)}")
        raise

def update_form_title(service, form_id, title, description):
    """Update the form title and description."""
    try:
        update = {
            'requests': [{
                'updateFormInfo': {
                    'info': {
                        'title': title,
                        'description': description
                    },
                    'updateMask': 'title,description'
                }
            }]
        }
        service.forms().batchUpdate(formId=form_id, body=update).execute()
    except Exception as e:
        print(f"Error updating form title: {str(e)}")
        raise

def create_question(question_data, index):
    """Create a question request based on the question type."""
    base_question = {
        'createItem': {
            'item': {
                'title': question_data['name'],
                'description': question_data['description'],
                'questionItem': {
                    'question': {
                        'required': question_data.get('required', False),
                    }
                }
            },
            'location': {'index': index}
        }
    }

    if question_data['type'] == 'radio':
        base_question['createItem']['item']['questionItem']['question'].update({
            'choiceQuestion': {
                'type': 'RADIO',
                'options': [{'value': option} for option in question_data['options']]
            }
        })
    elif question_data['type'] == 'text':
        base_question['createItem']['item']['questionItem']['question'].update({
            'textQuestion': {
                'paragraph': False
            }
        })

    return base_question

def update_form(form_id, form_config):
    """Update the form with the provided configuration."""
    try:
        service = get_service()
        
        # Delete existing questions
        delete_all_questions(service, form_id)
        
        # Update form title and description
        update_form_title(service, form_id, form_config['title'], form_config['description'])
        
        # Create new questions
        requests = [
            create_question(question, index) 
            for index, question in enumerate(form_config['questions'])
        ]
        
        # Submit all questions in one batch update
        if requests:
            update = {'requests': requests}
            service.forms().batchUpdate(formId=form_id, body=update).execute()
            
        return True
    except Exception as e:
        print(f"Error updating form: {str(e)}")
        return False

def main():

    success = update_form(FORM_ID, FROM_TEMPLATE)
    if success:
        print("Form created successfully!")
    else:
        print("Failed to update form. Check the error messages above.")

if __name__ == "__main__":
    main()