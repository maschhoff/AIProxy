# Basis-Image mit Python 3.11
FROM python:3.11-slim

# Arbeitsverzeichnis
WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Restliche App kopieren
COPY aiproxy.py .
# Expose Port
EXPOSE 8000

# Start-Befehl
CMD ["uvicorn", "aiproxy:app", "--host", "0.0.0.0", "--port", "8000"]
