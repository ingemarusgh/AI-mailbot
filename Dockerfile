FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY config.py .
COPY ai_handler.py .
COPY storage.py .
COPY mail_client.py .
COPY main.py .

# Create directory for data persistence
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main.py"]
