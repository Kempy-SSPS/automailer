# Automailer
~~a simple~~ tool for automating sending confirmation emails and updating forms

## Setup (10 steps)

### 1: Create an empty Google form
- Visit [Google Forms](https://docs.google.com/forms/)
- Create a new form
- In the "Responses" tab, click "Link with sheets"
- Note the Form ID and the sheet ID from the URLs
```
https://docs.google.com/forms/d/FORM_ID/edit
https://docs.google.com/spreadsheets/d/SHEET_ID/edit
```
- Add them into the .env file under the `FORM_ID` and `SPREADSHEET_ID` keys

### 2: Fill in the SMTP credentials
- Add all the nessecary keys for SMTP into the .env
```
SMTP_SERVER="mail.example.com"
SMTP_PORT="465"
SMTP_USERNAME="info"
SMTP_PASSWORD="abc"
SENDER_EMAIL="info@example.com"
```

### 3: Setup Google API
- Go to the [Google Cloud Console](https://console.cloud.google.com) (Works best on Chromium browsers)
- Click on "Select Project" and create a new project
- After creating the project, select it in the dropdown menu
- Click on "API and Services"
- Search for and enable:
    - "Google Forms API"
    - "Google Sheets API"
    - "Google Drive API"
- Switch to the "Credentials" section
- Click on "Manage Service Accounts", then "Create Service Account"
- Give it a name and an ID, then click "Create and Continue"
- Search for the "Editor" role and assign it
- Click "Done"
- In the account list, click the one you just created
- Click on "Keys", then "Add Key", then "Create Key", then "JSON"
- You will be prompted to download a file, rename it to "credentials.json" and save it into `config/credentials.json`

### 4: Share the Form and Sheet
- In the `credentials.json` file that you just downloaded, copy the value of `client_email`
- Go back to the page with the Form, click the three dots, then "Add collaborators" and paste in the email
- In the responses spreadsheet, click "Share" and paste the same email
- In the bottom of the form, note the name of the current page and update the `RANGE_NAME` accordingly, it shlould look something like `"Form Responses 1!B2:G"`

### 5: Fill in the templates
- Place the form configuration into `config/templates/form_template.json`
- Place the email configuration into `config/templates/email_template.py`

### 6: Define events
- Place the event definitions into `config/events.json`

### 7: Add Google Script to form
- Copy the script from `scripts/form.gs` fill in the endpoint address and the form ID
- Click the three dots on the form
- Click "Script Editor"
- Paste the code in
- Save it and select the `onFormSubmit` function to run on form submit
- Authorize the script and deny any security warnings

### 8: (Optional) Customize form
- If you upload a custom header image, you can also choose a cutom theme color

### 9: Run Automailer
- You can use Docker by running `docker compose up -d`
- Or you can run it locally by installing the dependencies and running `python3 main.py`