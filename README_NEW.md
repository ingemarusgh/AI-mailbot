# AI Mailbot - Generell Företagslösning

En konfigurerbar mailbot som automatiskt skapar AI-genererade svarsutkast för inkommande mail.

## Ny Modulär Struktur

### Filer och moduler:
- **config.json.example** - Exempelkonfiguration (kopiera till config.json och anpassa)
- **config.py** - Läser och validerar konfiguration
- **ai_handler.py** - Hanterar AI-svarsgenereringen
- **storage.py** - Spårar bearbetade mail (dubblettkontroll)
- **mail_client.py** - Mail-hantering (IMAP/SMTP) - kommer snart
- **main.py** - Huvudloop - refaktoreras snart

### Gamla filer (kommer fasas ut):
- **auto_draft_reply.py** - Nuvarande Gmail API-baserade script
- **gmail_auth.py** - Gmail-specifik autentisering

## Installation

1. Kopiera config-filen:
```bash
cp config.json.example config.json
```

2. Redigera config.json med dina inställningar:
   - Företagsinformation (namn, email, signatur)
   - Mailserver (IMAP/SMTP-inställningar)
   - AI-inställningar (modell, prompt-mall)

3. Skapa .env-fil med API-nycklar:
```bash
OPENAI_API_KEY=din_openai_nyckel
```

4. Installera beroenden:
```bash
pip install -r requirements.txt
```

## Konfiguration

### Företagsprofil
Anpassa företagsnamn, signatur och AI-prompt i `config.json`:
```json
{
  "company": {
    "name": "Ditt Företag AB",
    "email": "info@dittforetag.se",
    "signature": "Med vänliga hälsningar\\nDitt Företag AB"
  }
}
```

### Mailserver
Konfigurera IMAP/SMTP-inställningar för din mailserver:
```json
{
  "mail_server": {
    "type": "imap",
    "imap_host": "imap.dittforetag.se",
    "imap_port": 993,
    "smtp_host": "smtp.dittforetag.se",
    "smtp_port": 587,
    "username": "info@dittforetag.se",
    "password": "ditt_lösenord"
  }
}
```

**Testade mailservrar:**
- ✅ Gmail (IMAP)
- ✅ Microsoft Office 365
- ✅ Outlook.com
- 🔄 Exchange Server (lokal)
- 🔄 Egna mailservrar (cPanel/Plesk)

Se [MAILSERVER_EXAMPLES.md](MAILSERVER_EXAMPLES.md) för konfigurationsexempel.

### AI-prompt
Anpassa hur AI:n svarar via prompt-mallen i `config.json`:
```json
{
  "ai": {
    "prompt_template": "Du är {company_name} och svarar på mail..."
  }
}
```

## Användning

### Rekommenderat: Kör med Docker
```bash
# Skapa config och .env
cp config.json.example config.json
nano config.json
echo "OPENAI_API_KEY=your_key" > .env

# Starta med Docker Compose
docker-compose up -d

# Visa loggar
docker-compose logs -f
```

Se [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) för detaljerad guide.

### Alternativt: Kör direkt med Python
```bash
python main.py
```

### Köra gamla Gmail API-versionen:
```bash
python auto_draft_reply.py
```

## Status och nästa steg

### ✅ Klart
1. Grundstruktur med config och moduler
2. IMAP/SMTP-klient (fungerar med de flesta mailservrar)
3. Refaktorerad main.py till modulär version
4. Docker-support och deployment-guide
5. Testdokumentation för olika mailservrar

### 🔄 Pågående
6. Testa med olika mailservrar (Exchange, egna servrar)
7. Utökad felhantering och retry-logik

### ⏳ Planerat
8. Webbgränssnitt för admin/övervakning
9. Stöd för Exchange Web Services (EWS) API
10. Multi-tenant support (flera företag i samma installation)
11. Webhook-integration för externa system
12. Avancerad AI-konfiguration (olika modeller per företag)

## För utvecklare

### Testning av nya moduler:
```python
from config import Config
from ai_handler import AIHandler
from storage import Storage

# Ladda config
config = Config('config.json')

# Testa AI-handler
ai = AIHandler(config)
reply = ai.generate_reply("Hej, kan vi boka ett möte?")
print(reply)

# Testa storage
storage = Storage(config)
if not storage.is_processed("msg123", "thread123"):
    storage.mark_processed("msg123", "thread123")
```
