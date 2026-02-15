import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def gmail_authenticate():
    creds = None
    # Token sparas efter första inloggningen
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # Om inga (eller ogiltiga) credentials, logga in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def get_gmail_service():
    creds = gmail_authenticate()
    service = build('gmail', 'v1', credentials=creds)
    return service

if __name__ == '__main__':
    service = get_gmail_service()
    print('Gmail API är nu autentiserat och klart!')
