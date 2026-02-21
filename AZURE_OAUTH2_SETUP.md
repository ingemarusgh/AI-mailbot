# 🔐 Azure AD OAuth2 Setup Guide

**Professionell autentisering för Microsoft 365 mailboxar**

---

## 📋 STEG 1: Skapa Azure AD App

### 1.1 Gå till Azure Portal
1. Öppna [https://portal.azure.com](https://portal.azure.com)
2. Logga in med ditt Microsoft-konto
3. Sök efter **"Azure Active Directory"** (eller "Microsoft Entra ID" i nya portalen)

### 1.2 Registrera ny App
1. Klicka **"App registrations"** i vänstermenyn
2. Klicka **"+ New registration"**
3. Fyll i:
   - **Name:** `AI Mailbot OAuth`
   - **Supported account types:** 
     - Välj: **"Accounts in any organizational directory (Any Azure AD directory - Multitenant)"**
     - Detta tillåter ALLA Microsoft 365-konton att ansluta
   - **Redirect URI:**
     - Platform: **Web**
     - URL: `https://urauulfqtwfxvwmtsomd.supabase.co/auth/v1/callback`
     - (Detta är för Lovable → Supabase integration)
4. Klicka **"Register"**

### 1.3 Kopiera viktiga värden
Efter registrering, på "Overview" sidan:

```
Application (client) ID: [KOPIERA DETTA]
Directory (tenant) ID: [KOPIERA DETTA]
```

**Spara dessa!** Du behöver dem senare.

---

## 📋 STEG 2: Skapa Client Secret

1. I din app, gå till **"Certificates & secrets"** (vänstermeny)
2. Klicka **"+ New client secret"**
3. Fyll i:
   - **Description:** `Mailbot secret`
   - **Expires:** 24 months (rekommenderat)
4. Klicka **"Add"**
5. **KOPIERA "Value" DIREKT** (visas bara en gång!)

```
Client Secret: [KOPIERA DETTA NU - VISAS BARA EN GÅNG]
```

---

## 📋 STEG 3: Konfigurera API Permissions

1. Gå till **"API permissions"** (vänstermeny)
2. Klicka **"+ Add a permission"**
3. Välj **"Microsoft Graph"**
4. Välj **"Delegated permissions"**
5. Lägg till följande permissions:

```
✓ Mail.Read          - Läsa emails
✓ Mail.ReadWrite     - Skapa drafts
✓ Mail.Send          - Skicka emails (om auto-send)
✓ IMAP.AccessAsUser  - IMAP-åtkomst
✓ SMTP.Send          - SMTP-åtkomst
✓ offline_access     - Refresh tokens
✓ openid             - OpenID Connect
✓ profile            - Användarinfo
✓ email              - Email-adress
```

6. Klicka **"Add permissions"**
7. **VIKTIGT:** Klicka **"Grant admin consent for [your org]"**
   - Detta krävs för multi-tenant apps
   - Klicka "Yes" på popup

Du ska nu se gröna checkmarks ✓ på alla permissions.

---

## 📋 STEG 4: Lägg till i Railway Environment Variables

1. Gå till Railway dashboard
2. Klicka på ditt projekt → **Variables**
3. Lägg till:

```bash
AZURE_CLIENT_ID=<din Application (client) ID>
AZURE_CLIENT_SECRET=<din Client Secret>
AZURE_TENANT_ID=<din Directory (tenant) ID>
AZURE_REDIRECT_URI=https://urauulfqtwfxvwmtsomd.supabase.co/auth/v1/callback
```

---

## 📋 STEG 5: Lägg till i Lovable Environment Variables

1. Gå till Lovable projekt → **Settings** → **Environment Variables**
2. Lägg till:

```bash
VITE_AZURE_CLIENT_ID=<din Application (client) ID>
VITE_AZURE_TENANT_ID=<din Directory (tenant) ID>
VITE_AZURE_REDIRECT_URI=https://urauulfqtwfxvwmtsomd.supabase.co/auth/v1/callback
```

**OBS:** Använd INTE Client Secret i frontend (säkerhetsrisk!)

---

## 📋 STEG 6: Uppdatera lokala .env

I din lokala `.env` fil, lägg till:

```bash
# Azure OAuth2
AZURE_CLIENT_ID=your_client_id_here
AZURE_CLIENT_SECRET=your_client_secret_here
AZURE_TENANT_ID=your_tenant_id_here
AZURE_REDIRECT_URI=https://urauulfqtwfxvwmtsomd.supabase.co/auth/v1/callback
```

---

## 🧪 STEG 7: Testa OAuth2 Flow

### I Lovable UI:
1. Klicka "Add Company"
2. Klicka "Connect Microsoft 365"
3. Du redirectas till Microsoft login
4. Logga in med ett Microsoft 365-konto
5. Godkänn permissions
6. Du redirectas tillbaka → Token sparas!

### Vad händer i bakgrunden:
```
1. Lovable → Azure AD login
2. Användare loggar in
3. Azure returnerar authorization code
4. Lovable byter code mot access_token + refresh_token
5. Tokens sparas i Supabase mail_configs tabell
6. Railway använder tokens för IMAP/SMTP
```

---

## 🔄 Token Refresh

Tokens förnyas automatiskt:
- **Access token:** Giltig i ~1 timme
- **Refresh token:** Giltig i 90 dagar (förnyas automatiskt)
- Railway kollar `token_expires_at` innan varje IMAP-anslutning
- Om utgången → använd refresh_token för ny access_token

---

## 🔐 Säkerhet

**✅ SÄKERT:**
- Inga lösenord lagras
- Tokens krypterade i transport (HTTPS)
- Tokens kan revokeras av användare när som helst
- Multi-tenant isolation (varje företag = separat token)

**⚠️ VIKTIGT:**
- **Dela ALDRIG Client Secret** publikt
- Lagra endast i Railway/Supabase (backend)
- Frontend får bara se Client ID (publikt värde)

---

## 📊 Multi-Tenant Support

Din app stödjer nu:
- ✅ Flera företag med olika Microsoft 365-konton
- ✅ Personal Microsoft-konton (@outlook.com, @hotmail.com)
- ✅ Work/School Microsoft-konton (@företag.com via Microsoft 365)
- ✅ Automatisk tenant detection (Azure AD hanterar detta)

---

## 🐛 Troubleshooting

### "AADSTS50011: The redirect URI ... does not match"
→ Dubbelkolla att redirect URI i Azure AD exakt matchar din Supabase URL

### "AADSTS65001: The user or administrator has not consented"
→ Gå tillbaka till API Permissions → Grant admin consent

### "Invalid client secret"
→ Client secret har expirerat (24 månader) → Skapa ny i Azure Portal

### "Token expired"
→ Auto-refresh är aktiverad, kolla Railway logs för felmeddelanden

---

## 📚 Resurser

- [Microsoft Graph API Docs](https://docs.microsoft.com/en-us/graph/)
- [Azure AD OAuth2 Flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [IMAP OAuth2 with Microsoft](https://docs.microsoft.com/en-us/exchange/client-developer/legacy-protocols/how-to-authenticate-an-imap-pop-smtp-application-by-using-oauth)

---

## ✅ CHECKLIST

Före testning, verifiera:
- [ ] Azure AD app skapad
- [ ] Client ID + Secret kopierade
- [ ] API Permissions godkända (gröna checkmarks)
- [ ] Redirect URI korrekt konfigurerad
- [ ] Environment variables i Railway
- [ ] Environment variables i Lovable
- [ ] Supabase schema uppdaterat (se database/oauth2_migration.sql)
- [ ] Railway kod uppdaterad och deployad

**Nu är du redo!** 🚀
