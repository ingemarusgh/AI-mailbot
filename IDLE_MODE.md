# 🚀 IMAP IDLE Mode - Real-Time Email Processing

## 📋 Vad är IDLE mode?

**IMAP IDLE** är en RFC 2177 standard som låter din email-klient:
- ✅ Hålla kopplingen öppen till IMAP-servern
- ✅ Få **push-notifikationer** när nya emails kommer (realtid)
- ✅ **Minimal CPU-användning** när idle (nästan 0%)
- ✅ Svara på emails inom **sekunder** istället för minuter

## 🔄 Hur det fungerar

### **Tidigare (Polling)**
```
Loop varje 60 sekunder:
  Koppla upp -> Kolla nya emails -> Koppla ner
  Vänta 60 sekunder... (slösar CPU)
```

**Problem:**
- Railway fakturerar för CPU-tid även när ingenting händer
- Fördröjning 0-60 sekunder mellan email och svar
- Ineffektivt för många företag

---

### **Nu (IDLE Mode)**
```
För varje företag (egen thread):
  Koppla upp -> Säg "jag väntar" (IDLE)
  ... väntar tyst utan CPU ...
  Email kommer! -> Processa -> Tillbaka till IDLE
```

**Fördelar:**
- ⚡ **Realtid:** Email får svar inom 1-5 sekunder
- 💰 **Billigt:** Railway fakturerar endast vid email-processing
- 🎯 **Skalbart:** Varje företag = en thread (minimal overhead)

## 🏗️ Arkitektur

### **Multi-Tenant Threading**
```
Main Thread:
  ├─ Hämta företag från Supabase var 5:e minut
  ├─ Starta IDLE thread för varje företag
  └─ Övervaka thread-hälsa

Company Thread 1 (Företag A):
  └─ IDLE mode → Email → Process → IDLE

Company Thread 2 (Företag B):
  └─ IDLE mode → Email → Process → IDLE

Company Thread 3 (Företag C):
  └─ IDLE mode → Email → Process → IDLE
```

### **Fallback till Polling**
Om IMAP-servern **inte stödjer IDLE**:
- System upptäcker automatiskt detta
- Faller tillbaka till polling var 60:e sekund per företag
- Fortsätter fungera (bara långsammare)

## 📊 Jämförelse

| Metod | Reaktionstid | CPU/Kostnad | Skalbarhet |
|-------|--------------|-------------|------------|
| **Polling (60s)** | 0-60s | Hög (konstant) | Dålig |
| **Polling (5min)** | 0-300s | Medel | OK |
| **IDLE** | 1-5s | Låg (endast vid email) | Utmärkt |

## 🚀 Deployment

### **Railway**
Ingen konfiguration krävs - koden detekterar automatiskt om IDLE stöds.

### **Lokal Test**
```bash
# Aktivera virtual environment
.venv\Scripts\activate

# Kör med IDLE mode
python main_supabase.py
```

Du ska se:
```
[Företag A] Starting IDLE worker thread
[Företag A] Entering IDLE mode...
[Företag A] IDLE mode active, waiting for new emails...
```

Skicka ett test-email → Se realtids-processing!

## 🔧 Tekniska Detaljer

### **IDLE Timeout**
- RFC 2177 kräver att IDLE restarts var 29:e minut
- Implementerat: 29 minuter (1740 sekunder)
- IMAP-servern stänger annars kopplingen

### **Thread Safety**
- Varje företag = separat IMAP-kopppling (thread-safe)
- Supabase-klient är thread-safe
- Ingen race condition mellan företag

### **Error Handling**
```python
# Om thread kraschar:
1. Logga felet
2. Vänta 60 sekunder
3. Starta om automatiskt
```

### **Graceful Shutdown**
- CTRL+C stänger ner alla threads
- IDLE mode avslutas korrekt
- Inga "hängande" kopplingar

## 📝 Kod-exempel

### **IDLE Callback**
```python
def process_emails():
    """Körs när ny email upptäcks"""
    logger.info("New email detected!")
    process_company_emails(company_id)

# Starta IDLE (blockerande)
mail_client.idle_wait(callback=process_emails, timeout=1740)
```

### **Thread per Företag**
```python
for company in companies:
    thread = threading.Thread(
        target=company_idle_worker,
        args=(company['id'], company['name']),
        daemon=True  # Stäng av med main thread
    )
    thread.start()
```

## 🎯 Resultat

Med IDLE mode får du:
- ✅ **Professionell SaaS:** Realtids-respons som Gmail/Outlook
- ✅ **Låga kostnader:** Betala endast för faktisk email-processing
- ✅ **Skalbart:** Kan hantera 100+ företag utan problem
- ✅ **Transparent:** Ingen kod-ändring krävs för kunder

**Detta är exakt hur stora email-providers fungerar!** 🚀
