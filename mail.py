
import os.path
import base64
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from datetime import datetime

from email.message import EmailMessage

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Authorizes the user and stores the token and refresh token in token.json
def auth():
  creds = None
  # If token.json already exists, use it as the credential
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
  # Log the user in and request credentials if credentials are invalid or non-existent
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
      creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
      token.write(creds.to_json())
  return creds

# Send a message given the specified information.
def send_message(subject, content):
  # Ensure user is authorized.
  creds = auth()
  
  #Create message.
  try:
    # Call the Gmail API
    service = build('gmail', 'v1', credentials=creds)
    
    # Message metadata
    message = EmailMessage()
    message.set_content(content)
    
    profile = service.users().getProfile(userId='me').execute()
    message['To'] = profile['emailAddress']
    message['From'] = profile['emailAddress']
    message['Subject'] = subject
    
    # Encode message. 
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {
        'raw': encoded_message
    }
    
    # Send message.
    message_sent = (service.users().messages().send(userId="me", body=create_message).execute())
    print(F'Message Id: {message_sent["id"]}')
  
  except HttpError as error:
    print(F'An error occured: {error}')
    message_sent = None
  return send_message
  
# Send a message given the specified template.
def send_template(template):
  # Read template file
  f = open(template, "r")
  _ = f.readlines()
  
  #Get current date and time.
  now = datetime.now()
  time = now.strftime("%m/%d/%Y: %H:%M:%S")
  # Create email.
  subject, content = _[0].format(date=time), _[1].format(date=time)
  send_message(subject, content)

# Check arguments, run auth, send emails if neccessary.
def main():
  # If there are no arguments specified, run authentication.
  if len(sys.argv) == 1:
    auth()
    return
  
  # If arguments are supplied, send an email alert if template file exists.
  for i in range(1, len(sys.argv)):
    arg = sys.argv[i]
    if os.path.exists(arg):
      send_template(arg)
    else:
      print('ERR: Template not found.')
    
if __name__ == '__main__':
    main()