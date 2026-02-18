# Legacy Files

Denna mapp innehåller gamla filer från den ursprungliga Gmail API-baserade implementationen.

## Gamla filer:

### Python-script:
- **auto_draft_reply.py** - Ursprungliga scriptet med Gmail API
- **gmail_auth.py** - Gmail-specifik autentisering
- **read_mail.py** - Exempel för att läsa mail
- **send_mail.py** - Exempel för att skicka mail
- **reply_with_approval.py** - Manuellt godkännande av svar
- **run_forever.sh** - Loop-script för gamla versionen

### Credentials och data (krävs för att köra gamla scripten):
- **client_secret_*.json** - OAuth2 credentials från Google Cloud Console
- **credentials.json** - Alternativt credentials-filnamn
- **token.pickle** - Sparad autentisering (skapas efter första inloggningen)
- **sent_drafts.json** - Historik över behandlade mail

## Varför flyttades de?

Den nya modulära versionen använder IMAP/SMTP istället för Gmail API, vilket gör den kompatibel med alla mailservrar (Gmail, Office365, Exchange, etc).

## Om du vill använda gamla versionen:

```bash
cd legacy
python auto_draft_reply.py
```

**OBS:** De gamla filerna kräver Gmail API-credentials (credentials.json) och är endast kompatibla med Gmail.

## Rekommendation

Använd den nya modulära versionen i projektets root-mapp för:
- Stöd för alla mailservrar
- Docker-deployment
- Bättre konfigurerbarhet
- Multi-tenant support
