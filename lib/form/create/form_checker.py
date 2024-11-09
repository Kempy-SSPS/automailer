from lib.form.create.create_form_from_config import main as create_form
from lib.utils.safe_file_get import safe_file_get
from lib.utils.write_as_json import write_as_json

def form_checker():
    form_data = safe_file_get("data/form_data.json", {})
    form_created = form_data.get("created", False) is True
    if not form_created:
        create_form()



    altered_form_data = form_data
    altered_form_data["created"] = True
    write_as_json("data/form_data.json", altered_form_data)
