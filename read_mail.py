from gmail_auth import get_gmail_service
from googleapiclient.errors import HttpError


def list_messages(service, user_id='me', max_results=5):
    try:
        results = service.users().messages().list(userId=user_id, maxResults=max_results).execute()
        messages = results.get('messages', [])
        if not messages:
            print('Inga mail hittades.')
            return
        print('Senaste mail:')
        for msg in messages:
            msg_data = service.users().messages().get(userId=user_id, id=msg['id']).execute()
            snippet = msg_data.get('snippet', '')
            print(f"- {snippet[:100]}")
    except HttpError as error:
        print(f'Ett fel uppstod: {error}')


def main():
    service = get_gmail_service()
    list_messages(service)

if __name__ == '__main__':
    main()
