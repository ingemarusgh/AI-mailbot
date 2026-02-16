# Mailserver Configuration Examples

## Gmail (IMAP)

```json
{
  "mail_server": {
    "type": "imap",
    "imap_host": "imap.gmail.com",
    "imap_port": 993,
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your_email@gmail.com",
    "password": "your_app_password",
    "use_ssl": true,
    "drafts_folder": "[Gmail]/Drafts"
  }
}
```

**Setup:**
1. Aktivera 2-faktorautentisering i Google-kontot
2. Skapa ett "App Password" på https://myaccount.google.com/apppasswords
3. Använd App Password som password i config

## Microsoft Office 365

```json
{
  "mail_server": {
    "type": "imap",
    "imap_host": "outlook.office365.com",
    "imap_port": 993,
    "smtp_host": "smtp.office365.com",
    "smtp_port": 587,
    "username": "your_email@company.com",
    "password": "your_password",
    "use_ssl": true,
    "drafts_folder": "Drafts"
  }
}
```

**Setup:**
1. Kontrollera att IMAP är aktiverat i Office 365 admin
2. Använd vanligt lösenord eller app-specific password
3. Vissa organisationer kräver Modern Authentication - kontakta IT-avdelningen

## Microsoft Exchange (lokal server)

```json
{
  "mail_server": {
    "type": "imap",
    "imap_host": "mail.company.com",
    "imap_port": 993,
    "smtp_host": "mail.company.com",
    "smtp_port": 587,
    "username": "username@company.com",
    "password": "your_password",
    "use_ssl": true,
    "drafts_folder": "Drafts"
  }
}
```

**Setup:**
1. Kontrollera att Exchange har IMAP aktiverat
2. Fråga IT om rätt server-adresser och portar
3. Vissa Exchange-servrar använder port 143 (utan SSL)

## Outlook.com / Hotmail

```json
{
  "mail_server": {
    "type": "imap",
    "imap_host": "outlook.office365.com",
    "imap_port": 993,
    "smtp_host": "smtp.office365.com",
    "smtp_port": 587,
    "username": "your_email@outlook.com",
    "password": "your_password",
    "use_ssl": true,
    "drafts_folder": "Drafts"
  }
}
```

## Egna mailservrar (cPanel, Plesk, etc)

```json
{
  "mail_server": {
    "type": "imap",
    "imap_host": "mail.yourserver.com",
    "imap_port": 993,
    "smtp_host": "mail.yourserver.com",
    "smtp_port": 587,
    "username": "info@company.com",
    "password": "your_password",
    "use_ssl": true,
    "drafts_folder": "Drafts"
  }
}
```

**Vanliga varianter:**
- Port 143 för IMAP utan SSL
- Port 465 för SMTP med SSL (istället för 587 med STARTTLS)
- Vissa servrar kan kräva `use_ssl: false`

## Testa anslutning

### Test IMAP-anslutning
```bash
# Linux/Mac
openssl s_client -connect imap.gmail.com:993

# Windows PowerShell
Test-NetConnection -ComputerName imap.gmail.com -Port 993
```

### Test SMTP-anslutning
```bash
# Linux/Mac
openssl s_client -starttls smtp -connect smtp.gmail.com:587

# Windows PowerShell
Test-NetConnection -ComputerName smtp.gmail.com -Port 587
```

## Felsökning

### Vanliga problem:

1. **"Authentication failed"**
   - Kontrollera användarnamn och lösenord
   - Kolla om 2FA är aktiverat (kräver App Password)
   - Kontrollera att IMAP/SMTP är aktiverat på mailservern

2. **"Connection refused"**
   - Kontrollera host och port
   - Testa med `use_ssl: false` om port 143/25 används
   - Kontrollera firewall-regler

3. **"Timed out"**
   - Kontrollera nätverksanslutning
   - Pröva med längre timeout (lägg till i config om det behövs)
   - Vissa företagsnätverk blockerar IMAP/SMTP

4. **"Invalid folder"**
   - Lista mappar med IMAP-klient för att se rätt namn
   - Gmail använder "[Gmail]/Drafts", andra använder "Drafts"
   - Vissa språkversioner har översatta mappnamn

## Rekommendationer per företagstyp

### Små företag (< 50 anställda)
- **Gmail Workspace** - Enklast att sätta upp, bra support
- **Microsoft 365 Business** - Bra integration med Office

### Medelstora företag (50-500)
- **Microsoft 365 Enterprise** - Skalbart, säkert
- **Google Workspace Enterprise** - Flexibelt, molnbaserat

### Stora företag (500+)
- **Exchange Server (on-premise)** - Full kontroll
- **Microsoft 365 Enterprise** - Hybrid-lösningar möjliga

### Budget/Egen hosting
- **Egna mailservrar** med cPanel/Plesk - Billigast
- Kräver mer teknisk kunskap för underhåll
