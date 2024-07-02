import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Specify the scopes for the API
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate():
    credentials = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(os.path.join("Youtube", "Config", "token.json")):
        credentials = Credentials.from_authorized_user_file(os.path.join("Youtube", "Config", "token.json"), SCOPES)
    
    # If there are no valid credentials available, let the user log in using device flow.
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(os.path.join("Youtube", "Config", "token.json"), SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        flow.run_local_server(port=0)
        credentials = flow.credentials
        # Save the credentials for the next run
        with open(os.path.join("Youtube", "Config", "token.json"), 'w') as token:
            token.write(credentials.to_json())