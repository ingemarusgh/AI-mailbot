# 🚀 QUICK START: Azure OAuth2 Setup (15 minuter)

**Följ dessa steg i exakt ordning** ✅

---

## ☑️ STEG 1: Supabase SQL Migration (2 min)

1. Öppna [Supabase SQL Editor](https://supabase.com/dashboard/project/urauulfqtwfxvwmtsomd/sql/new)
2. Kopiera **hela innehållet** från filen `database/oauth2_migration.sql`
3. Klistra in i SQL Editor
4. Klicka **"Run"**
5. Verifiera: Du ska se ✅ "Success. No rows returned"

**Klart?** → Gå vidare till Steg 2

---

## ☑️ STEG 2: Skapa Azure AD App (5 min)

### 2A: Öppna Azure Portal
1. Gå till **https://portal.azure.com**
2. Logga in med ditt Microsoft-konto
3. Sök efter **"Microsoft Entra ID"** (eller "Azure Active Directory")
4. Klicka på den

### 2B: Skapa App
1. I vänstermenyn → **"App registrations"**
2. Klicka **"+ New registration"**
3. Fyll i:
   ```
   Name: AI Mailbot OAuth
   
   Supported account types: 
   ○ Accounts in any organizational directory (Any Azure AD - Multitenant)
   
   Redirect URI:
   Platform: [Web]
   URL: https://urauulfqtwfxvwmtsomd.supabase.co/auth/v1/callback
   ```
4. Klicka **"Register"**

### 2C: Kopiera Client ID & Tenant ID
Nu ser du "Overview" sidan. **KOPIERA DESSA** (behövs senare):

```
Application (client) ID: ________________________
Directory (tenant) ID: __________________________
```

**Klart?** → Gå vidare till Steg 3

---

## ☑️ STEG 3: Skapa Client Secret (2 min)

1. I din app, vänstermeny → **"Certificates & secrets"**
2. Klicka **"+ New client secret"**
3. Fyll i:
   ```
   Description: Mailbot secret
   Expires: 24 months
   ```
4. Klicka **"Add"**
5. **KOPIERA "Value" NU!** (visas bara en gång)

```
Client Secret Value: ________________________________________
```

**Klart?** → Gå vidare till Steg 4

---

## ☑️ STEG 4: Lägg till API Permissions (3 min)

1. Vänstermeny → **"API permissions"**
2. Klicka **"+ Add a permission"**
3. Välj **"Microsoft Graph"**
4. Välj **"Delegated permissions"**
5. Sök och bocka i följande (9 st):

```
☑ Mail.Read
☑ Mail.ReadWrite
☑ Mail.Send
☑ IMAP.AccessAsUser.All
☑ SMTP.Send
☑ offline_access
☑ openid
☑ profile
☑ email
```

6. Klicka **"Add permissions"**
7. **VIKTIGT:** Klicka **"✓ Grant admin consent for [your org]"**
8. Klicka **"Yes"** på popup

Du ska nu se 9 gröna checkmarks ✅

**Klart?** → Gå vidare till Steg 5

---

## ☑️ STEG 5: Uppdatera Railway Variables (2 min)

1. Gå till **Railway dashboard**
2. Öppna ditt projekt → **"Variables"** tab
3. Lägg till dessa (använd värdena du kopierade ovan):

```bash
AZURE_CLIENT_ID=[Din Application (client) ID från Steg 2C]
AZURE_CLIENT_SECRET=[Din Client Secret Value från Steg 3]
AZURE_TENANT_ID=common
AZURE_REDIRECT_URI=https://urauulfqtwfxvwmtsomd.supabase.co/auth/v1/callback
```

4. Klicka **"Save"** eller **"Add variable"** efter varje

Railway kommer automatiskt re-deploya!

**Klart?** → Gå vidare till Steg 6

---

## ☑️ STEG 6: Uppdatera Lovable Variables (2 min)

1. Gå till **Lovable projekt**
2. Öppna **Settings** → **Environment Variables**
3. Lägg till (eller uppdatera):

```bash
VITE_AZURE_CLIENT_ID=[Din Application (client) ID från Steg 2C]
VITE_AZURE_TENANT_ID=common
VITE_AZURE_REDIRECT_URI=https://urauulfqtwfxvwmtsomd.supabase.co/auth/v1/callback
```

**OBS:** Använd INTE Client Secret här (säkerhetsrisk!)

**Klart?** → Azure OAuth2 är nu konfigurerat! ✅

---

## ☑️ STEG 7: Testa OAuth2 Flow (valfritt - finns ännu inget UI)

**När du byggt Lovable UI (nästa steg):**

1. Öppna Lovable preview
2. Klicka "Connect Microsoft 365"
3. Popup öppnas → logga in med Microsoft
4. Godkänn permissions
5. Du redirectas tillbaka
6. Företag sparas i Supabase
7. Railway börjar processa emails!

---

## 📋 CHECKLISTA - Har du gjort allt?

```
☐ Steg 1: SQL migration kördes utan fel
☐ Steg 2: Azure App skapad, Client ID & Tenant ID kopierade
☐ Steg 3: Client Secret skapad och kopierad
☐ Steg 4: 9 API permissions tillagda + admin consent
☐ Steg 5: 4 environment variables i Railway
☐ Steg 6: 3 environment variables i Lovable
☐ Steg 7: Railway re-deployad (sker automatiskt efter Steg 5)
```

---

## 🎯 NÄSTA STEG: Bygg Lovable UI

Nu när OAuth2 är konfigurerat, byggt Lovable-gränssnittet:

1. Öppna Lovable.dev
2. Följ prompten i `LOVABLE_OAUTH2_SETUP.md`
3. Skapa "Connect Microsoft 365" knapp
4. Testa OAuth2-flödet!

---

## ❓ PROBLEM?

### "Invalid redirect URI"
→ Dubbelkolla att redirect URI i Azure exakt matchar:  
`https://urauulfqtwfxvwmtsomd.supabase.co/auth/v1/callback`

### "Admin consent required"
→ Gå tillbaka till Steg 4, klicka "Grant admin consent"

### "Railway visar fel i logs"
→ Kolla att alla 4 AZURE_* variablerna är korrekt ifyllda

### "Kan inte hitta Azure Active Directory"
→ Det heter nu "Microsoft Entra ID" i nya Azure Portal

---

## ✅ DU ÄR KLAR!

**OAuth2 är nu configurerat!**  
Railway kan ansluta till Microsoft 365-mailboxar säkert utan lösenord.

**Nästa:** Bygg Lovable UI för att lägga till företag! 🚀
