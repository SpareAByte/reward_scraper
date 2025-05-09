"""Beware this assumes a 8 digit code, further work will need to be done per request"""

import re
import os.path
import base64
import email

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

#Establishing paths for creds and base dir.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CRED_PATH = os.path.join(BASE_DIR, 'credentials/credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'credentials/token.json')

class Check2fa:
    def __init__(self):
        self.verif_code = None

    def get_verification_code(self):
        return self.verif_code

    def check2fa(self):
        creds = None
        #Check if token exists, if so, proceed.
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        #If token does not exist, create a new one.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CRED_PATH, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        try:
            #Check inbox for the first message in the list. Handler should give enough time for this to be recieved correctly, if not, adjust sleep.
            service = build("gmail", "v1", credentials=creds)
            results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=1).execute()
            messages = results.get("messages", [])

            for m in messages:
                m_id = m["id"]
                message = service.users().messages().get(userId="me", id=m_id).execute()

                parts = message['payload'].get('parts')
                if parts:
                    for part in parts:
                        if part['mimeType'] == 'text/plain':
                            data = part['body']['data']
                            text = base64.urlsafe_b64decode(data).decode('utf-8')
                            break
                else:
                    data = message['payload']['body']['data']
                    text = base64.urlsafe_b64decode(data).decode('utf-8')

                extract_code = re.search(r'(\d{8})', text)
                if extract_code:
                    self.verif_code = extract_code.group(0)
                    print(f"2FA Code: {self.verif_code}")
                else:
                    print("No 2FA code found in the email.")

        except HttpError as error:
            print(f"An error occurred: {error}")


if __name__ == "__main__":
    checker = Check2fa()
    checker.check2fa()
    print(checker.get_verification_code())
