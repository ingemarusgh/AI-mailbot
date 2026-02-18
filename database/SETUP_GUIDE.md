# 🚀 SUPABASE SETUP - Steg-för-Steg Guide

**Tid: 5-10 minuter** | **Svårighetsgrad: Enkel** ⭐

---

## STEG 1: Skapa Supabase Projekt (2 min)

### 1.1 Gå till Supabase Dashboard
1. Öppna [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Logga in (eller skapa konto om du inte har)

### 1.2 Skapa Nytt Projekt
1. Klicka på **"New project"** (grön knapp)
2. Fyll i:
   - **Name**: `AI Mailbot` (eller valfritt namn)
   - **Database Password**: Välj ett starkt lösenord (SPARA DETTA!)
   - **Region**: Välj närmaste region (t.ex. `Europe West (Frankfurt)` för Sverige)
   - **Pricing Plan**: `Free` (funkar perfekt för start!)
3. Klicka **"Create new project"**
4. ⏳ Vänta 2 minuter medan projektet startar upp

---

## STEG 2: Kör Setup-Script (3 min)

### 2.1 Öppna SQL Editor
1. I vänster sidofält: Klicka på **"SQL Editor"** (ikon ser ut som `</>`))
2. Klicka **"New query"** (eller använd befintlig tom query)

### 2.2 Kopiera Setup-Script
1. Öppna filen **`database/setup.sql`** från din kod
2. Markera **ALLT** innehåll (Ctrl+A)
3. Kopiera (Ctrl+C)

### 2.3 Klistra In och Kör
1. Gå tillbaka till Supabase SQL Editor
2. Klistra in (Ctrl+V) hela scriptet
3. Klicka **"Run"** (eller tryck Ctrl+Enter)
4. ✅ Du ska se: **"Success. No rows returned"**

🎉 **Grattis!** Databasen är nu klar. Alla 7 tabeller är skapade.

---

## STEG 3: Verifiera att Allt Fungerar (1 min)

### 3.1 Kontrollera Tabeller
1. I vänster sidofält: Klicka på **"Table Editor"**
2. Du ska nu se dessa 7 tabeller i listan:
   - ✅ `companies`
   - ✅ `mail_configs`
   - ✅ `ai_configs`
   - ✅ `processed_emails`
   - ✅ `email_stats`
   - ✅ `users`
   - ✅ `company_users`

### 3.2 Klicka på `companies`
- Tabellen ska vara tom (0 rows)
- Du ska se kolumnerna: `id`, `name`, `email`, `status`, `created_at`, `updated_at`

**Om du ser detta: Perfekt! Setup är klar! ✅**

---

## STEG 4: Spara API-Nycklar (2 min)

### 4.1 Hitta API-Nycklar
1. I vänster sidofält: Klicka på **"Settings"** (kugghjul-ikon)
2. Under "Project Settings": Klicka på **"API"**
3. Scrolla ner till **"Project API keys"**

### 4.2 Kopiera Dessa Nycklar

**📋 Du behöver spara TRE saker:**

1. **Project URL** (under "Project URL")
   - Exempel: `https://abcdefghijk.supabase.co`
   - Kopiera detta

2. **anon public** (under "Project API keys")
   - Börjar med `eyJhbG...`
   - Klicka ikonen för att kopiera
   - **Detta är för Lovable frontend** (safe att dela i frontend)

3. **service_role** (under "Project API keys")
   - Börjar med `eyJhbG...`
   - Klicka ikonen för att kopiera
   - **Detta är för Railway backend** ⚠️ HEMLIG! Dela ALDRIG publikt!

### 4.3 Spara Nycklarna
Öppna en textfil och spara:

```
SUPABASE_URL=https://abcdefghijk.supabase.co
SUPABASE_ANON_KEY=eyJhbG... (den korta)
SUPABASE_SERVICE_KEY=eyJhbG... (den långa)
```

**⚠️ VIKTIGT:** Dela ALDRIG `service_role` key publikt! Den ger full databas-access.

---

## STEG 5: (VALFRITT) Lägg Till Testdata

### 5A. Via Lovable Admin UI (Rekommenderat)
👉 Vänta med detta tills Lovable-frontend är redo

### 5B. Manuellt via SQL (Snabbt test)

1. Gå till **SQL Editor** igen
2. Öppna `database/test_data.sql` från din kod
3. **VIKTIG ÄNDRING:** Ersätt dessa värden:
   ```sql
   email_address: 'DIN-EMAIL@example.com'
   email_password: 'DITT-APP-PASSWORD'
   ```
4. Kör första INSERT:
   ```sql
   INSERT INTO companies (name, email, status)
   VALUES ('Test Company AB', 'info@testcompany.se', 'active')
   RETURNING id;
   ```
5. **Kopiera UUID** som returneras (t.ex. `a1b2c3d4-...`)
6. Ersätt `<COMPANY_ID>` i resterande INSERTs med denna UUID
7. Kör resten av scriptet

---

## ✅ KLART! Vad Nu?

Din Supabase-databas är nu redo. Nästa steg:

### 🚂 **Deploy Backend till Railway**
Se [RAILWAY_DEPLOYMENT.md](../RAILWAY_DEPLOYMENT.md) STEG 2

Du behöver sätta dessa environment variables i Railway:
```bash
SUPABASE_URL=https://abcdefghijk.supabase.co  # från STEG 4
SUPABASE_SERVICE_KEY=eyJhbG...               # från STEG 4
OPENAI_API_KEY=sk-proj-...                   # din OpenAI key
```

### 💻 **Bygg Lovable Frontend**
Se [RAILWAY_DEPLOYMENT.md](../RAILWAY_DEPLOYMENT.md) STEG 3

Du behöver sätta dessa i Lovable `.env`:
```bash
VITE_SUPABASE_URL=https://abcdefghijk.supabase.co  # från STEG 4
VITE_SUPABASE_ANON_KEY=eyJhbG...                  # från STEG 4
```

---

## 🐛 Problem? Troubleshooting

### Fel: "relation 'companies' already exists"
✅ **Ignorera detta** - betyder att tabellen redan finns. Allt är OK!

### Fel: "permission denied"
❌ Kontrollera att du är inloggad med rätt konto i Supabase

### Fel: "syntax error"
❌ Se till att du kopierat HELA setup.sql filen (första raden ska börja med `--`)

### Tabellerna syns inte i Table Editor
🔄 Refresh sidan (F5 eller Ctrl+R)

### Vill börja om från scratch?
Kör detta i SQL Editor:
```sql
DROP TABLE IF EXISTS company_users CASCADE;
DROP TABLE IF EXISTS email_stats CASCADE;
DROP TABLE IF EXISTS processed_emails CASCADE;
DROP TABLE IF EXISTS ai_configs CASCADE;
DROP TABLE IF EXISTS mail_configs CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS users CASCADE;
```
Sen kör `setup.sql` igen.

---

## 📞 Behöver Hjälp?

- **Supabase Docs**: https://supabase.com/docs/guides/database
- **SQL Editor Guide**: https://supabase.com/docs/guides/database/overview#the-sql-editor
- **GitHub Issues**: https://github.com/ingemarusgh/AI-mailbot/issues

---

**🎉 Lycka till!** Du är redo för nästa steg: Railway deployment!
