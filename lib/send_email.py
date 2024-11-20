import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


if not os.path.exists('/.dockerenv'):
    from dotenv import load_dotenv
    try:
        load_dotenv(".env")
    except Exception as e:
        print(f"Error loading .env file: {str(e)}")
        exit(1)



SMTP_SERVER=os.environ.get("SMTP_SERVER")
SMTP_PORT=os.environ.get("SMTP_PORT")
SMTP_USERNAME=os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD=os.environ.get("SMTP_PASSWORD")
SENDER_EMAIL=os.environ.get("SENDER_EMAIL")



def send_email(email):

    base_dir = os.getcwd()
    # data_file = os.path.join(base_dir, 'data', 'form_data.json')
    with open(f"{base_dir}/data/mail_log.txt", "a") as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"{timestamp} - Sending email to {email['recipient_address']}\n```{email['body']}```\n\n")


    subject = email["subject"]
    body = email["body"]
    recipient_email = email["recipient_address"]

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())

        print(f"Email sent to {recipient_email} successfully.")

    except Exception as e:
        print(f"Failed to send email. Error: {e}")


