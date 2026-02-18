import json

SENT_FILE = 'sent_drafts.json'

def load_sent_pairs():
    import os
    print(f"[DEBUG] Söker sent_drafts.json i: {os.getcwd()}")
    if not os.path.exists(SENT_FILE):
        print(f"[DEBUG] Skapar ny sent_drafts.json i: {os.getcwd()}")
        with open(SENT_FILE, 'w') as f:
            json.dump([], f)
        return set()
    try:
        with open(SENT_FILE, 'r') as f:
            data = set(tuple(x) for x in json.load(f))
        print(f"[DEBUG] Laddade sent_pairs: {data}")
        return data
    except Exception as e:
        print(f"[DEBUG] Fel vid laddning av sent_drafts.json: {e}")
        return set()

def save_sent_pairs(sent_pairs):
    import os
    print(f"Sparar sent_drafts.json i: {os.getcwd()}")
    try:
        with open(SENT_FILE, 'w') as f:
            json.dump([list(x) for x in sent_pairs], f)
        print(f"sent_drafts.json sparad!")
    except Exception as e:
        print(f"Fel vid skrivning till {SENT_FILE}: {e}")

def save_sent_ids(sent_ids):
    with open(SENT_FILE, 'w') as f:
        json.dump(list(sent_ids), f)
def has_draft_for_thread(service, thread_id, user_id='me'):
    try:
        drafts = service.users().drafts().list(userId=user_id).execute()
        if 'drafts' not in drafts:
            return False
        for draft in drafts['drafts']:
            draft_data = service.users().drafts().get(userId=user_id, id=draft['id']).execute()
            msg = draft_data.get('message', {})
            if msg.get('threadId') == thread_id:
                return True
        return False
    except Exception:
        return False
from gmail_auth import get_gmail_service
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64

import openai
import os
from dotenv import load_dotenv
def generate_ai_reply(snippet):
    prompt = (
        "Du är Hugo Marklund och svarar på inkommande mail. "
        "Skriv alltid i jag-form, aldrig vi eller oss. "
        "Skriv ett relevant, artigt och naturligt svar på mailet nedan. "
        "Du ska inte härma eller upprepa mailet, utan svara som om du är Hugo. "
        "Var alltid trevlig och anpassa svaret efter innehållet. "
        "Om någon vill boka ett möte, eller frågar om ni kan boka in en tid, föreslå alltid själv en rimlig tid (t.ex. 'Jag kan tisdag kl 14:00, passar det?'). "
        "Avsluta alltid med: Med vänliga hälsningar Hugo Marklund.\n\n"
        f"Mail: {snippet}\n\nSvar:"
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"AI-svar misslyckades: {e}")
        return "Hej! Detta är ett automatiskt svar på ditt mail."

def list_unread_messages(service, user_id='me', max_results=5):
    try:
        results = service.users().messages().list(userId=user_id, labelIds=['INBOX', 'UNREAD'], maxResults=max_results).execute()
        messages = results.get('messages', [])
        return messages
    except HttpError as error:
        print(f'Ett fel uppstod: {error}')
        return []

def get_message_info(service, msg_id, user_id='me'):
    msg_data = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
    snippet = msg_data.get('snippet', '')
    headers = msg_data.get('payload', {}).get('headers', [])
    thread_id = msg_data.get('threadId')
    from_addr = next((h['value'] for h in headers if h['name'] == 'From'), None)
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Svar')
    return snippet, from_addr, subject, thread_id

def create_draft(service, user_id, message, thread_id=None):
    try:
        draft_body = {'message': message}
        if thread_id:
            draft_body['message']['threadId'] = thread_id
        draft = service.users().drafts().create(userId=user_id, body=draft_body).execute()
        print(f"Utkast skapat! ID: {draft['id']}")
    except HttpError as error:
        print(f'Ett fel uppstod: {error}')

def create_message(to, subject, message_text, thread_id=None):
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    msg = {'raw': raw.decode()}
    if thread_id:
        msg['threadId'] = thread_id
    return msg

def main():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    service = get_gmail_service()
    messages = list_unread_messages(service)
    sent_pairs = load_sent_pairs()
    if not messages:
        print('Inga olästa mail.')
        return
    for msg in messages:
        msg_id = msg['id']
        snippet, from_addr, subject, thread_id = get_message_info(service, msg_id)
        pair = (msg_id, thread_id)
        print(f"[DEBUG] Behandlar mail-ID: {msg_id}, thread-ID: {thread_id}")
        if pair in sent_pairs:
            print(f"[DEBUG] Utkast finns redan för mail-ID {msg_id} och tråd {thread_id}, hoppar över.")
            continue
        if has_draft_for_thread(service, thread_id):
            print(f"[DEBUG] Utkast finns redan för tråd {thread_id}, hoppar över.")
            sent_pairs.add(pair)
            save_sent_pairs(sent_pairs)
            continue
        print(f"[DEBUG] Skapar utkast för mail från {from_addr}: {snippet[:200]}")
        autosvar = generate_ai_reply(snippet)
        draft_msg = create_message(from_addr, f"Re: {subject}", autosvar, thread_id)
        create_draft(service, 'me', draft_msg, thread_id)
        sent_pairs.add(pair)
        save_sent_pairs(sent_pairs)

if __name__ == '__main__':
    main()
