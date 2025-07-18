
-----

# AIProxy - AI-Zählerstandserfassung via MQTT Proxy

-----

## Projektübersicht

Dieses Projekt ist ein **FastAPI-basierter AI-Proxy**, der speziell dafür entwickelt wurde, Zählerstandsbilder z.B der ESP32 CAM zu verarbeiten. Es nutzt die fortschrittlichen **Google Gemini-Modelle (speziell `gemini-1.5-flash`)**, um Zählerstände aus hochgeladenen Bildern zu erkennen. Der erkannte Zählerstand wird zusammen mit einem Zeitstempel über **MQTT** (Message Queuing Telemetry Transport) an ein IoT-System gesendet.

Ideal für Smart-Home-Lösungen wie Home Assistant, Energieüberwachung oder industrielle Anwendungen, bei denen physische Zählerstände digital erfasst und zentralisiert werden müssen.

-----

## Funktionen

  * **AI-gestützte Zählerstandserkennung:** Nutzt das leistungsstarke Gemini 1.5 Flash-Modell für genaue Ablesungen von Zählerbildern.
  * **FastAPI-Schnittstelle:** Bietet einen einfachen und robusten REST-API-Endpunkt für den Bild-Upload.
  * **MQTT-Integration:** Sendet den erkannten Zählerstand und einen Zeitstempel im JSON-Format an einen konfigurierbaren MQTT-Broker.
  * **Umgebungsvariablen-Konfiguration:** Einfache Einrichtung durch Umgebungsvariablen für API-Schlüssel und MQTT-Details.
  * **Fehlerbehandlung:** Robuste Fehlerbehandlung für API-Aufrufe, Bildverarbeitung und MQTT-Kommunikation.

-----

## Erste Schritte

### Voraussetzungen

Stell sicher, dass die folgenden Komponenten installiert sind:

  * Python 3.9+
  * Ein Google Cloud-Konto mit aktiviertem Zugriff auf die [Generative Language API](https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com) und einem generierten API-Schlüssel.
  * Ein funktionierender MQTT-Broker (z.B. Mosquitto), entweder lokal oder remote.

### Installation

X. **Docker**

-----

```bash
docker run -d \
  -p 8000:8000 \
  --name aiproxy \
  -e GOOGLE_API_KEY="sk-..." \
  -e MQTT_BROKER="192.168.x.x" \
  knex666/aiproxy:latest-dev
```

-----


1.  **Repository klonen:**

    ```bash
    git clone https://github.com/DEIN_USERNAME/DEIN_REPO_NAME.git
    cd DEIN_REPO_NAME
    ```

    (Ersetze `DEIN_USERNAME` und `DEIN_REPO_NAME` durch deine tatsächlichen Daten.)

2.  **Virtuelle Umgebung erstellen und aktivieren (empfohlen):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Unter Linux/macOS
    # .\venv\Scripts\activate  # Unter Windows
    ```

3.  **Abhängigkeiten installieren:**

    ```bash
    pip install -r requirements.txt
    ```

    Falls du keine `requirements.txt` hast, erstelle eine mit:

    ```bash
    pip install fastapi uvicorn google-generative-ai paho-mqtt python-dotenv
    pip freeze > requirements.txt
    ```

### Konfiguration

Erstelle eine `.env`-Datei im Stammverzeichnis deines Projekts und füge die folgenden Umgebungsvariablen hinzu:

```dotenv
GOOGLE_API_KEY="DEIN_GOOGLE_API_SCHLUESSEL"
MQTT_BROKER="localhost" # Oder die IP/Hostname deines MQTT-Brokers
MQTT_TOPIC="zaehler/stand" # Der MQTT-Topic, auf dem die Daten veröffentlicht werden
```

**Wichtig:** Ersetze `"DEIN_GOOGLE_API_SCHLUESSEL"` durch deinen echten Google API-Schlüssel. Behandle diesen Schlüssel vertraulich und gib ihn nicht öffentlich frei.

### Ausführung

1.  **Server starten:**
    Starte die FastAPI-Anwendung mit Uvicorn:

    ```bash
    uvicorn aiproxy:app --host 0.0.0.0 --port 8000 --reload
    ```

    Der `--reload`-Parameter ist nützlich für die Entwicklung und startet den Server bei Codeänderungen neu.

2.  **API-Dokumentation:**
    Nach dem Start des Servers ist die interaktive API-Dokumentation (Swagger UI) unter `http://localhost:8000/docs` verfügbar.

-----

## Nutzung

Sende eine `POST`-Anfrage an den `/process_meter_image`-Endpunkt mit dem Zählerbild als `multipart/form-data`.

### Beispiel mit `curl`

```bash
curl -X POST "http://localhost:8000/process_meter_image" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/pfad/zu/deinem/zaehlerbild.jpg;type=image/jpeg"
```

Ersetze `/pfad/zu/deinem/zaehlerbild.jpg` durch den tatsächlichen Pfad zu deinem Bild. Stell sicher, dass der `type` (z.B. `image/jpeg` oder `image/png`) dem tatsächlichen Bildtyp entspricht.


### MQTT-Nachricht

Der Proxy veröffentlicht die Daten im folgenden JSON-Format an den konfigurierten `MQTT_TOPIC` (standardmäßig `zaehler/stand`):

```json
{
  "timestamp": "2025-07-18T19:41:47.123456",
  "meter_reading": "12345"
}
```

-----

## Fehlerbehebung

  * **`[Errno 111] Connection refused`**: Dies deutet oft auf Netzwerkprobleme, eine blockierende Firewall oder einen nicht erreichbaren MQTT-Broker/Google API-Server hin. Überprüfe deine Internetverbindung, Firewall-Einstellungen und die Erreichbarkeit deines MQTT-Brokers.
  * **`GOOGLE_API_KEY not set`**: Stell sicher, dass die `.env`-Datei korrekt ist und sich im selben Verzeichnis wie die `aiproxy.py`-Datei befindet, oder dass die Umgebungsvariable manuell gesetzt wurde, bevor du Uvicorn startest.
  * **`Prompt blocked by AI (safety reasons)`**: Das Gemini-Modell hat integrierte Sicherheitsfilter. Wenn das Bild oder der implizite Inhalt als unangemessen oder schädlich eingestuft wird, kann die Anfrage blockiert werden.

-----

## Lizenz

Dieses Projekt ist unter der [GNU General Public License v3.0 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.html) lizenziert. 
-----

## Beitragen

Beiträge sind willkommen\! Wenn du Fehler findest oder Verbesserungen vorschlagen möchtest, öffne bitte ein Issue oder sende einen Pull Request.

