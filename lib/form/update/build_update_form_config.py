import json

def get_auto_updated_question():
    with open("config/templates/form_template.json", "r") as f:
        form_template = json.loads(f.read())
        for i, question in enumerate(form_template["questions"]):
            if question.get("created", False) is not True:
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
            "required": auto_updated_question["required"]
        }
    }
    return update_form_config

