import os
import sys
import time

from lib.form.create.create_form_from_config import main as create_form
from lib.utils.safe_file_get import safe_file_get
from lib.utils.write_as_json import write_as_json

def form_checker():
    time.sleep(5)

    # Determine the base directory of the script
    base_dir = os.getcwd()
    data_file = os.path.join(base_dir, 'data', 'form_data.json')
    # Safely load the form data
    form_data = safe_file_get(data_file, {})

    # Check if the form has already been created
    form_created = form_data.get("created", False)

    # Attempt to create the form if it hasn't been created yet
    if not form_created:
        form_create_success = create_form()

        # Handle unsuccessful form creation
        if not form_create_success:
            print("Form creation failed.")
            sys.exit(1)

        # Update the form data to reflect the creation
        form_data["created"] = True
        write_as_json(data_file, form_data)
        print("Form created and form_data.json updated.")

    time.sleep(10)