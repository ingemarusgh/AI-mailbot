# Deployment Guide - Railway + Supabase + Lovable

Complete guide for deploying the multi-tenant AI Mailbot system.

## 🏗️ Architecture Overview

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   Lovable   │ ───── │   Supabase   │ ───── │   Railway   │
│  (Frontend) │       │  (Database)  │       │  (Backend)  │
└─────────────┘       └──────────────┘       └─────────────┘
     Admin UI          Config + Stats         Email Bot
```

- **Lovable**: Admin panel för att lägga till företag och konfigurera AI-prompts
- **Supabase**: PostgreSQL-databas som lagrar konfiguration och statistik
- **Railway**: Backend worker som processar email för alla aktiva företag

## 📋 Prerequisites

- [Supabase](https://supabase.com) account (free tier OK)
- [Railway](https://railway.app) account (free tier OK)
- [Lovable](https://lovable.dev) account
- [OpenAI API](https://platform.openai.com) key
- GitHub account (för kod)

---

## STEG 1: Supabase Setup

### 1.1 Skapa Projekt

1. Gå till [supabase.com](https://supabase.com/dashboard)
2. Klicka "New project"
3. Välj organisation och region (välj närmaste, t.ex. Frankfurt för Sverige)
4. Sätt databas-lösenord (spara detta!)
5. Vänta 2 minuter medan projektet skapas

### 1.2 Applicera Database Schema

1. Gå till **SQL Editor** i Supabase Dashboard
2. Kör `database/schema.sql`:
   - Kopiera innehållet från `database/schema.sql`
   - Klistra in i SQL Editor
   - Klicka "Run" (eller Ctrl+Enter)
3. Kör `database/rls_policies.sql`:
   - Kopiera innehållet från `database/rls_policies.sql`
   - Klistra in i ny query
   - Klicka "Run"

### 1.3 Verifiera Tabeller

Gå till **Table Editor** och verifiera att dessa tabeller finns:
- ✅ companies
- ✅ mail_configs
- ✅ ai_configs
- ✅ processed_emails
- ✅ email_stats
- ✅ users
- ✅ company_users

### 1.4 Spara API-nycklar

Gå till **Settings → API**:

1. **Project URL** (t.ex. `https://xxxyyyzzz.supabase.co`)
2. **anon/public key** (börjar med `eyJhbG...`) - för Lovable frontend
3. **service_role key** (börjar med `eyJhbG...`) - för Railway backend

⚠️ **VIKTIGT**: Service role key är hemlig! Dela aldrig denna publikt.

---

## STEG 2: Railway Setup

### 2.1 Skapa Projekt

1. Gå till [railway.app](https://railway.app)
2. Logga in med GitHub
3. Klicka "New Project" → "Deploy from GitHub repo"
4. Välj din AI-mailbot repository
5. Railway börjar automatiskt bygga projektet

### 2.2 Konfigurera Environment Variables

Gå till projektet → **Variables** → Lägg till:

```bash
SUPABASE_URL=https://xxxyyyzzz.supabase.co
SUPABASE_SERVICE_KEY=eyJhbG...  # service_role key från Supabase
OPENAI_API_KEY=sk-proj-...     # Din OpenAI API-nyckel
```

### 2.3 Konfigurera Start Command

Gå till **Settings** → **Deploy**:
- Start Command: `python main_supabase.py`
- eller låt Railway auto-detecta från `Procfile`

### 2.4 Deploy

Railway deployer automatiskt när du pushar till GitHub.

För manuell deploy:
1. Gå till **Deployments**
2. Klicka "Deploy" på senaste commit

### 2.5 Verifiera Logs

Gå till **Deployments** → Klicka på senaste deployment → **Logs**

Du ska se:
```
AI Mailbot - Multi-Tenant Railway Deployment
Connecting to Supabase...
✓ Supabase connected
LOOP 1 - Checking all active companies
Found 0 active companies
```

✅ Om du ser detta fungerar backend!

---

## STEG 3: Lovable Frontend Setup

### 3.1 Skapa Lovable Projekt

1. Gå till [lovable.dev](https://lovable.dev)
2. Skapa nytt projekt
3. Välj "Blank project" eller "Supabase starter"

### 3.2 Konfigurera Supabase Connection

I Lovable projektet, skapa `.env`:

```bash
VITE_SUPABASE_URL=https://xxxyyyzzz.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbG...  # anon key från Supabase
```

### 3.3 Bygg Admin UI (Exempel)

Skapa dessa sidor i Lovable:

**1. Companies List**
- Visa alla företag från `companies`-tabellen
- Add/Edit/Delete-knappar

**2. Company Config Form**
```typescript
// Exempel: Add Company Form
import { supabase } from './supabase';

async function addCompany(data) {
  // 1. Insert company
  const { data: company } = await supabase
    .from('companies')
    .insert({ name: data.name, email: data.email })
    .select()
    .single();
  
  // 2. Insert mail config
  await supabase.from('mail_configs').insert({
    company_id: company.id,
    imap_host: data.imap_host,
    imap_port: data.imap_port,
    smtp_host: data.smtp_host,
    smtp_port: data.smtp_port,
    email_address: data.email_address,
    email_password: data.email_password
  });
  
  // 3. Insert AI config
  await supabase.from('ai_configs').insert({
    company_id: company.id,
    prompt_template: data.prompt_template,
    signature: data.signature
  });
}
```

**3. Dashboard**
- Visa `email_stats` för alla företag
- Grafer över emails_processed, drafts_created, errors

**4. Logs Viewer (Optional)**
- Visa processed_emails (timestamps)
- Dock: ingen email-innehåll lagrat (privacy!)

### 3.4 Deploy Lovable

1. Klicka "Deploy" i Lovable
2. Du får en URL (t.ex. `https://your-app.lovable.app`)

---

## STEG 4: Lägg till Första Företaget

### 4.1 Via Lovable UI (Rekommenderat)

Använd formuläret du byggde för att lägga till företag.

### 4.2 Via Supabase Dashboard (Snabbt test)

Gå till **Table Editor** → `companies` → Insert row:

```json
{
  "name": "Test Company AB",
  "email": "info@testcompany.se",
  "status": "active"
}
```

Notera `id` som genereras (UUID).

Gå till `mail_configs` → Insert row:
```json
{
  "company_id": "<UUID från ovan>",
  "imap_host": "imap.gmail.com",
  "imap_port": 993,
  "imap_use_ssl": true,
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_use_tls": true,
  "email_address": "test@testcompany.se",
  "email_password": "app-specific-password",
  "inbox_folder": "INBOX"
}
```

Gå till `ai_configs` → Insert row:
```json
{
  "company_id": "<UUID från ovan>",
  "provider": "openai",
  "model": "gpt-3.5-turbo",
  "prompt_template": "You are a helpful assistant for {company_name}. Reply professionally to this email: {email_body}",
  "signature": "Med vänlig hälsning,\nTest Company AB\ntest@testcompany.se",
  "check_interval": 300,
  "max_messages_per_check": 10,
  "create_drafts": true,
  "auto_send": false
}
```

---

## STEG 5: Verifiera att allt fungerar

### 5.1 Check Railway Logs

Gå till Railway → Deployments → Logs

Du ska nu se:
```
LOOP X - Checking all active companies
Found 1 active companies
--- Processing: Test Company AB ---
Processing company: Test Company AB (info@testcompany.se)
No unread messages for Test Company AB
```

### 5.2 Testa Email-flöde

1. Skicka ett test-mail till `test@testcompany.se`
2. Vänta max 5 minuter (check_interval)
3. Kolla Railway logs:
   ```
   Found 1 unread messages for Test Company AB
   Generating reply for: you@example.com - Test Subject
   ✓ Email draft created for: you@example.com
   ```
4. Logga in på test@testcompany.se mailkonto
5. Kolla **Drafts** - AI-svaret ska finnas där!

### 5.3 Kolla Statistik

Gå till Supabase → Table Editor → `email_stats`

Du ska se:
```
company_id | date       | emails_processed | drafts_created | errors
-----------+------------+------------------+----------------+-------
<UUID>     | 2026-02-18 | 1                | 1              | 0
```

---

## 🎯 Arkitektur-flöde (Sammanfattning)

```
1. Admin loggar in på Lovable
2. Lägger till nytt företag via UI
3. Data sparas i Supabase (companies, mail_configs, ai_configs)
4. Railway bot (kör varje 5:e min):
   a. Hämtar alla companies med status='active'
   b. För varje företag:
      - Kopplar till deras mailserver (IMAP/SMTP)
      - Läser olästa mail
      - Genererar AI-svar med företagets prompt
      - Skapar utkast i deras mailkonto
      - Loggar hash av message_id i processed_emails
      - Uppdaterar statistik i email_stats
5. Admin kan se statistik i Lovable Dashboard
```

---

## 🔒 Säkerhet & Privacy

### Email Privacy
✅ **INGEN** email-innehåll lagras i Supabase  
✅ Endast SHA256-hash av message_id (för duplicate-checking)  
✅ `processed_emails` tabellen innehåller BARA hashade IDs och timestamps  

### Credential Security
- Mail-lösenord lagras i Supabase (krypterat via PostgreSQL)
- För extra säkerhet: Använd [Supabase Vault](https://supabase.com/docs/guides/database/vault)
- Backend använder `service_role` key (aldrig exponerad till frontend)
- Frontend använder `anon` key med Row Level Security (RLS)

### Access Control
- RLS policies säkerställer att users bara ser sina egna företags data
- `company_users` tabell kopplar users till companies de har tillgång till

---

## 🐛 Trouble-shooting

### Railway-problem

**Problem**: "Error connecting to Supabase"  
**Fix**: Kontrollera att `SUPABASE_URL` och `SUPABASE_SERVICE_KEY` är rätt satta i Railway Variables

**Problem**: "No active companies found"  
**Fix**: Verifiera att du lagt till företag med `status='active'` i Supabase

**Problem**: "IMAP connection failed"  
**Fix**: Kolla `mail_configs` - verifiera host, port, credentials

### Supabase-problem

**Problem**: "permission denied for table companies"  
**Fix**: Kör `database/rls_policies.sql` igen

**Problem**: "column 'company_id' does not exist"  
**Fix**: Kör `database/schema.sql` igen från scratch

### Email-problem

**Problem**: Drafts skapas inte  
**Fix**: 
1. Kontrollera Railway logs för fel-meddelanden
2. Verifiera email credentials i `mail_configs`
3. För Gmail: Använd app-specific password, inte vanligt lösenord

**Problem**: Duplicerade drafts  
**Fix**: `processed_emails` tabellen ska förhindra detta. Kolla Railway logs om samma message_id processas flera gånger.

---

## 📊 Monitoring & Maintenance

### Daily Checks
- Railway deployments status (ska vara "Active")
- Email stats - ökning varje dag?
- Error rate i `email_stats`

### Weekly Maintenance
- Rensa gamla `processed_emails` (>90 dagar)
- Granska error logs i Railway

### SQL för Clean-up
```sql
-- Ta bort gamla processed_emails (äldre än 90 dagar)
DELETE FROM processed_emails 
WHERE processed_at < NOW() - INTERVAL '90 days';

-- Aggregera gamla email_stats (äldre än 1 år) om du vill
```

---

## 🚀 Nästa Steg

1. ✅ Sätt upp Supabase databas
2. ✅ Deploy backend till Railway
3. ✅ Bygg admin UI i Lovable
4. ⏳ Lägg till fler företag
5. ⏳ Bygg dashboard med grafer
6. ⏳ Lägg till webhook-notifikationer
7. ⏳ Implementera manual draft approval-flow

---

## 💰 Kostnadskalkyl

**Free Tier (0-5 företag):**
- Supabase: Free (500MB databas, 50k API requests/månad)
- Railway: $5/månad ($5 gratis varje månad)
- Lovable: Free (community plan)
- OpenAI: ~$0.002 per email (GPT-3.5-turbo)

**Total: ~$0/månad** (under free tier limits)

**Paid Tier (10+ företag):**
- Supabase Pro: $25/månad (8GB databas, 500k API requests)
- Railway Pro: $20/månad (mer resources)
- OpenAI: Beroende på volym (~100 emails/dag = $6/månad)

**Total: ~$51/månad** för small business deployment

---

## 📞 Support

- Supabase docs: https://supabase.com/docs
- Railway docs: https://docs.railway.app
- Lovable docs: https://docs.lovable.dev

GitHub Issues: https://github.com/ingemarusgh/AI-mailbot/issues
