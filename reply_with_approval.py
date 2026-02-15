from gmail_auth import get_gmail_service
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64
import time

def list_unread_messages(service, user_id='me', max_results=5):
    try:
        results = service.users().messages().list(userId=user_id, labelIds=['INBOX', 'UNREAD'], maxResults=max_results).execute()
        messages = results.get('messages', [])
        return messages
    except HttpError as error:
        print(f'Ett fel uppstod: {error}')
        return []

def get_message_snippet(service, msg_id, user_id='me'):
    msg_data = service.users().messages().get(userId=user_id, id=msg_id).execute()
    snippet = msg_data.get('snippet', '')
    return snippet

def create_message(to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': raw.decode()}

def send_message(service, user_id, message):
    try:
        sent_message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"Meddelande skickat! ID: {sent_message['id']}")
    except HttpError as error:
        print(f'Ett fel uppstod: {error}')

def main():
    service = get_gmail_service()
    messages = list_unread_messages(service)
    if not messages:
        print('Inga olästa mail.')
        return
    for msg in messages:
        snippet = get_message_snippet(service, msg['id'])
        print(f"Mail: {snippet[:200]}")
        svar = input('Vill du svara på detta mail? (j/n): ')
        if svar.lower() == 'j':
            to = input('Mottagarens e-post (eller tryck enter för att använda avsändaren): ')
            if not to:
                msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
                headers = msg_data.get('payload', {}).get('headers', [])
                to = next((h['value'] for h in headers if h['name'] == 'From'), None)
            subject = input('Ämne: ')
            body = input('Meddelande: ')
            message = create_message(to, subject, body)
            confirm = input('Skicka detta svar? (j/n): ')
            if confirm.lower() == 'j':
                send_message(service, 'me', message)
            else:
                print('Svar skickades inte.')

if __name__ == '__main__':
    main()
