# Snabbstart - AI Mailbot

## 5-minuters setup

### 1. Förberedelser (2 min)
```bash
# Klona/ladda ner projektet
cd AI-mailbot

# Kopiera konfigurationsmall
cp config.json.example config.json
```

### 2. Konfigurera (2 min)

**Redigera config.json:**
```bash
nano config.json  # eller använd valfri editor
```

**Minimal konfiguration:**
```json
{
  "company": {
    "name": "Ditt Namn",
    "email": "din@email.com",
    "signature": "Med vänliga hälsningar\nDitt Namn"
  },
  "mail_server": {
    "type": "imap",
    "imap_host": "imap.gmail.com",
    "imap_port": 993,
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "din@email.com",
    "password": "ditt_app_password"
  }
}
```

**Skapa .env med OpenAI API-nyckel:**
```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

### 3. Kör (1 min)

**Med Docker (rekommenderat):**
```bash
docker-compose up -d
docker-compose logs -f
```

**Utan Docker:**
```bash
pip install -r requirements.txt
python main.py
```

## Testa att det fungerar

1. Skicka ett testmail till din konfigurerade adress
2. Vänta 1 minut
3. Kolla i "Drafts" - ett AI-genererat svar ska finnas där!

## Gmail-specifik setup

### Steg 1: Aktivera IMAP i Gmail
1. Gå till Gmail → Settings (kugghjulet) → See all settings
2. Klicka på fliken "Forwarding and POP/IMAP"
3. Under "IMAP access", välj "Enable IMAP"
4. Klicka "Save Changes"

### Steg 2: Skapa App Password
1. Gå till https://myaccount.google.com/security
2. Under "Signing in to Google", välj "2-Step Verification" (aktivera om det inte är aktivt)
3. Gå tillbaka och välj "App passwords"
4. Välj "Mail" och din enhet
5. Kopiera det genererade lösenordet (16 tecken)
6. Använd detta som `password` i config.json

## Office 365-specifik setup

### Steg 1: Kontrollera IMAP-status
1. Logga in på Office 365 webmail
2. Gå till Settings → Mail → General → POP and IMAP
3. Säkerställ att IMAP är aktiverat

### Steg 2: Konfigurera
```json
{
  "mail_server": {
    "imap_host": "outlook.office365.com",
    "imap_port": 993,
    "smtp_host": "smtp.office365.com",
    "smtp_port": 587,
    "username": "din@foretag.com",
    "password": "ditt_lösenord"
  }
}
```

## Vanliga problem och lösningar

### "Authentication failed"
- **Gmail:** Använd App Password, inte vanligt lösenord
- **Office 365:** Kontrollera att Modern Authentication är tillåtet
- **Alla:** Dubbelkolla användarnamn och lösenord

### "Connection refused"
- Kontrollera att IMAP/SMTP är aktiverat på mailservern
- Testa anslutning: `telnet imap.gmail.com 993`
- Kontrollera firewall-inställningar

### "No module named 'openai'"
```bash
pip install -r requirements.txt
```

### "Config file not found"
```bash
cp config.json.example config.json
# Redigera sedan config.json
```

### Container startar inte (Docker)
```bash
# Visa felmeddelanden
docker-compose logs

# Testa manuellt
docker-compose run --rm mailbot python main.py
```

## Nästa steg

När grundfunktionen fungerar, utforska:
- [MAILSERVER_EXAMPLES.md](MAILSERVER_EXAMPLES.md) - Konfiguration för olika mailservrar
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Avancerade deployment-scenarier
- [README_NEW.md](README_NEW.md) - Fullständig dokumentation

## Support

Om du kör fast:
1. Kontrollera loggarna (kör med `docker-compose logs -f` eller läs utdata från `python main.py`)
2. Sök i loggarna efter `[ERROR]` eller `[FATAL]`
3. Konsultera felsökningsguiden ovan
4. Öppna ett issue på GitHub med loggutdrag
