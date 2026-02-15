from gmail_auth import get_gmail_service
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64

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
    to = input('Mottagarens e-post: ')
    subject = input('Ämne: ')
    body = input('Meddelande: ')
    message = create_message(to, subject, body)
    send_message(service, 'me', message)

if __name__ == '__main__':
    main()
