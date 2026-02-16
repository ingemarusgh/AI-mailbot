# Docker Deployment Guide

## Snabbstart

### 1. Förberedelser
```bash
# Kopiera och redigera config
cp config.json.example config.json
nano config.json

# Skapa .env med API-nycklar
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Skapa data-mapp för persistent storage
mkdir -p data
```

### 2. Bygg och kör med Docker Compose (rekommenderat)
```bash
# Bygg och starta
docker-compose up -d

# Visa loggar
docker-compose logs -f

# Stoppa
docker-compose down

# Stoppa och radera data
docker-compose down -v
```

### 3. Alternativt: Använd Docker direkt
```bash
# Bygg image
docker build -t ai-mailbot .

# Kör container
docker run -d \
  --name ai-mailbot \
  --restart unless-stopped \
  -v $(pwd)/config.json:/app/config.json:ro \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/data:/app/data \
  ai-mailbot

# Visa loggar
docker logs -f ai-mailbot

# Stoppa container
docker stop ai-mailbot
docker rm ai-mailbot
```

## Deployment-scenarier

### Utveckling (local testing)
```bash
# Starta med live logs
docker-compose up

# Stoppa med Ctrl+C
```

### Produktion (server/cloud)
```bash
# Starta i bakgrunden
docker-compose up -d

# Auto-restart efter systemomstart
# (redan konfigurerat i docker-compose.yml)

# Uppdatera kod
git pull
docker-compose down
docker-compose up -d --build
```

### Raspberry Pi / Home Assistant OS
```bash
# Bygg för ARM-arkitektur (om du bygger på annan maskin)
docker buildx build --platform linux/arm64 -t ai-mailbot .

# Eller bygg direkt på Pi
docker-compose up -d
```

## Hantera flera instanser (flera företag)

### Struktur:
```
mailbot/
├── company1/
│   ├── config.json
│   ├── .env
│   └── docker-compose.yml
├── company2/
│   ├── config.json
│   ├── .env
│   └── docker-compose.yml
└── shared/
    └── Dockerfile (delas mellan alla)
```

### docker-compose.yml för varje företag:
```yaml
version: '3.8'

services:
  mailbot:
    build: ../shared
    container_name: mailbot-company1
    restart: unless-stopped
    volumes:
      - ./config.json:/app/config.json:ro
      - ./.env:/app/.env:ro
      - ./data:/app/data
```

### Kör flera samtidigt:
```bash
cd company1
docker-compose up -d

cd ../company2
docker-compose up -d
```

## Övervakning och underhåll

### Kontrollera status
```bash
# Kontrollera om containern körs
docker-compose ps

# Visa resursutnyttjande
docker stats ai-mailbot
```

### Visa och analysera loggar
```bash
# Realtidsloggar
docker-compose logs -f

# Senaste 100 rader
docker-compose logs --tail=100

# Loggar för specifik tidsperiod
docker-compose logs --since 1h

# Sök i loggar
docker-compose logs | grep ERROR
```

### Backup
```bash
# Backup config och data
tar -czf mailbot-backup-$(date +%Y%m%d).tar.gz config.json .env data/

# Restore
tar -xzf mailbot-backup-YYYYMMDD.tar.gz
```

### Uppdatera mailbot
```bash
# Hämta senaste kod
git pull

# Rebuilda och starta om
docker-compose down
docker-compose up -d --build
```

## Felsökning

### Container startar inte
```bash
# Visa detaljerade felmeddelanden
docker-compose logs

# Kontrollera config-fil
docker-compose config

# Testa att köra interaktivt
docker-compose run --rm mailbot python main.py
```

### IMAP/SMTP-anslutning fungerar inte
```bash
# Testa anslutning från container
docker-compose exec mailbot ping imap.gmail.com
docker-compose exec mailbot nc -zv imap.gmail.com 993

# Om det behövs, lägg till DNS-servrar i docker-compose.yml
services:
  mailbot:
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

### Persistent storage fungerar inte
```bash
# Kontrollera att data-mappen existerar och har rätt permissions
ls -la data/

# Kontrollera mounted volumes
docker-compose exec mailbot ls -la /app/data
```

### Container använder för mycket minne/CPU
```bash
# Lägg till resource limits i docker-compose.yml
services:
  mailbot:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          memory: 256M
```

## Säkerhet

### Best practices:
1. **Använd read-only mounts för config**
   ```yaml
   - ./config.json:/app/config.json:ro
   ```

2. **Skydda .env och config.json**
   ```bash
   chmod 600 config.json .env
   ```

3. **Använd secrets istället för .env i produktion**
   ```yaml
   services:
     mailbot:
       secrets:
         - openai_api_key
   secrets:
     openai_api_key:
       file: ./secrets/openai_key.txt
   ```

4. **Kör som non-root user**
   ```dockerfile
   # Lägg till i Dockerfile
   RUN useradd -m -u 1000 mailbot
   USER mailbot
   ```

5. **Scan för säkerhetsproblem**
   ```bash
   docker scan ai-mailbot
   ```

## Cloud deployment

### AWS ECS
```bash
# Pusha till ECR
aws ecr get-login-password | docker login --username AWS --password-stdin
docker tag ai-mailbot:latest your-account.dkr.ecr.region.amazonaws.com/ai-mailbot
docker push your-account.dkr.ecr.region.amazonaws.com/ai-mailbot
```

### Google Cloud Run
```bash
# Bygg och pusha
gcloud builds submit --tag gcr.io/your-project/ai-mailbot
gcloud run deploy ai-mailbot --image gcr.io/your-project/ai-mailbot
```

### Azure Container Instances
```bash
# Skapa container instance
az container create \
  --resource-group myResourceGroup \
  --name ai-mailbot \
  --image youracr.azurecr.io/ai-mailbot \
  --restart-policy Always
```
