from lib.get_new_responses import main as get_new_responses
from lib.build_email import build_email
from lib.send_email import send_email

def main():
    new_responses = get_new_responses()
    print(f"Found these new responses: {str(new_responses)}")
    for new_reponse in new_responses:
        email = build_email(new_reponse)
        send_email(email)
        
        
