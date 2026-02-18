# AI Mailbot - Multi-Tenant SaaS-lösning

En konfigurerbar mailbot som automatiskt skapar AI-genererade svarsutkast för inkommande mail.

## 🚀 Två Deployment-alternativ

### 🏢 **Multi-Tenant (Nytt!)**
**Railway + Supabase + Lovable** - Professionell SaaS-arkitektur för flera företag

- ✅ En backend-instans processar alla kunder
- ✅ Databas-driven konfiguration (inga filer)
- ✅ Admin UI för att lägga till och konfigurera företag
- ✅ Centraliserad statistik och övervakning
- ✅ **Privacy-first**: Ingen email-data lagras, bara hashade IDs

👉 **[RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)** för komplett guide

### 🖥️ **Single-Tenant (Legacy)**
**Docker/Lokal** - En mailbot per företag, fil-baserad konfiguration

- ✅ Körs lokalt eller i Docker
- ✅ Enkel setup för ett företag
- ✅ Fungerar offline (Raspberry Pi deployment)

👉 **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** eller **[QUICKSTART.md](QUICKSTART.md)**

## 📁 Projektstruktur

### Multi-Tenant (Railway + Supabase):
- **database/** - SQL-scheman för Supabase
  - `schema.sql` - Databas-tabeller
  - `rls_policies.sql` - Row Level Security
- **supabase_client.py** - Databas-operationer
- **supabase_config.py** - Load config från Supabase
- **supabase_storage.py** - Processed emails tracking (hashade IDs)
- **main_supabase.py** - Multi-tenant huvudloop
- **Procfile, railway.toml** - Railway deployment config
- **RAILWAY_DEPLOYMENT.md** - Komplett deployment-guide

### Single-Tenant (Docker/Lokal):
- **config.json.example** - Exempelkonfiguration
- **config.py** - Fil-baserad konfiguration
- **ai_handler.py** - AI-svarsgenereringen
- **storage.py** - Fil-baserad tracking (sent_drafts.json)
- **mail_client.py** - IMAP/SMTP-klient
- **main.py** - Single-tenant huvudloop
- **Dockerfile, docker-compose.yml** - Docker deployment
- **DOCKER_DEPLOYMENT.md, QUICKSTART.md** - Setup-guider

### Delade moduler:
- **ai_handler.py** - AI-svarsgenereringen (används av båda)
- **mail_client.py** - IMAP/SMTP-klient (används av båda)
- **requirements.txt** - Python-beroenden

### Legacy:
- **legacy/** - Ursprunglig Gmail API-implementation

## 🚀 Quick Start

### Multi-Tenant Deployment (Railway + Supabase)

1. **Sätt upp Supabase:**
   - Skapa projekt på [supabase.com](https://supabase.com)
   - Kör `database/schema.sql` i SQL Editor
   - Kör `database/rls_policies.sql`

2. **Deploy till Railway:**
   - Skapa projekt på [railway.app](https://railway.app)
   - Länka till GitHub repo
   - Lägg till environment variables:
     ```
     SUPABASE_URL=...
     SUPABASE_SERVICE_KEY=...
     OPENAI_API_KEY=...
     ```

3. **Bygg Admin UI i Lovable:**
   - Se [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)

📖 **[Läs fullständig guide →](RAILWAY_DEPLOYMENT.md)**

### Single-Tenant Deployment (Docker)

1. Kopiera och redigera config:
```bash
cp config.json.example config.json
nano config.json
```

2. Skapa .env:
```bash
echo "OPENAI_API_KEY=din_nyckel" > .env
```

3. Start med Docker:
```bash
docker-compose up -d
```

📖 **[Läs QUICKSTART.md →](QUICKSTART.md)**

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
nan📊 Status och Roadmap

### ✅ Version 2.0 - Multi-Tenant (2026-02-18)
- ✅ Supabase-integration (PostgreSQL databas)
- ✅ Railway deployment-config
- ✅ Privacy-first arkitektur (hashade IDs, ingen email-data)
- ✅ Multi-tenant support (en backend för alla kunder)
- ✅ Databas-driven konfiguration
- ✅ Row Level Security (RLS) för säker access control
- ✅ Email statistik och övervakning

### ✅ Version 1.0 - Single-Tenant
- ✅ Grundstruktur med config och moduler
- ✅ IMAP/SMTP-klient (Gmail, Office365, Outlook.com)
- ✅ Docker-support och deployment-guide
- ✅ Refaktorerad modulär arkitektur

### 🔄 Pågående
- 🔄 Lovable Admin UI (frontend för företagshantering)
- 🔄 Dashboard med grafer och statistik
- 🔄 Testa med fler mailservrar (Exchange, custom)

### ⏳ Planerat
- ⏳ Manual draft approval-flow
- ⏳ Webhook-integration för externa system
- ⏳ Exchange Web Services (EWS) API-support
- ⏳ Email kategorisering (prioritet, auto-reply vs human review)
- ⏳ Supabase Vault för credential-kryptering
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
