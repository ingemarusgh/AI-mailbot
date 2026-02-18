# AI Mailbot med Gmail API

Detta projekt är en Python-baserad mailbot som använder Gmail API för att läsa, skicka och hantera e-postmeddelanden.


## Funktioner
- Autentisering med OAuth2
- Läsa inkommande mail
- Skicka mail
- Lista olästa mail och föreslå svar
- Manuellt godkännande innan svar skickas
- Grundstruktur för vidareutveckling


## Kom igång
1. Klona projektet
2. Installera beroenden: `pip install -r requirements.txt`
3. Skapa och ladda ner din credentials.json från Google Cloud Console (se nedan)
4. Placera credentials.json i projektmappen
5. Kör valfritt script, t.ex. `python read_mail.py` eller `python reply_with_approval.py`

### Skapa credentials.json
1. Gå till Google Cloud Console: https://console.cloud.google.com/
2. Skapa ett nytt projekt (eller välj ett befintligt)
3. Aktivera "Gmail API" under "API & Tjänster"
4. Skapa OAuth-klient (typ: Skrivbordsapp) och ladda ner credentials.json
5. Placera filen i projektmappen


## Säkerhet
Projektet använder Gmail API:s inbyggda säkerhet och autentisering. Dela aldrig dina credentials offentligt.


## Användning

### Läsa mail
Kör `python read_mail.py` för att lista de senaste mailen.

### Skicka mail
Kör `python send_mail.py` och följ instruktionerna i terminalen.

### Svara på mail med manuellt godkännande
Kör `python reply_with_approval.py` för att lista olästa mail. Du får möjlighet att svara på varje mail och måste godkänna innan svaret skickas.

## Vidareutveckling
- Lägg till fler funktioner för att hantera mail
- Integrera med andra tjänster
