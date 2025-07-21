# filename: aiproxy.py
# GPL Mathias Aschhoff 2025

from fastapi import FastAPI, UploadFile, HTTPException
import os
import datetime # Import für den Zeitstempel
import json     # Import für JSON-Formatierung
import paho.mqtt.client as mqtt
import google.generativeai as genai
from pathlib import Path

app = FastAPI()

# Make sure to set your Google API Key as an environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_TOPIC =  os.getenv("MQTT_TOPIC") 
DEBUG = os.getenv("DEBUG", "false").lower() in ["1", "true", "yes"]

@app.on_event("startup")
async def startup_event():
    """Initializes the Google Generative AI client on application startup."""
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
    else:
        print("Warning: GOOGLE_API_KEY environment variable not set. Gemini API calls will fail.")

@app.post("/process_meter_image")
async def process_meter_image(file: UploadFile):
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=400, detail="GOOGLE_API_KEY not set.")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

    if not MQTT_TOPIC:
        raise HTTPException(status_code=500, detail="MQTT_TOPIC environment variable not set.")

    # Erfasse den Zeitstempel am Anfang der Verarbeitung
    timestamp = datetime.datetime.now().isoformat()

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        image_bytes = await file.read()

        if DEBUG:
            # --- Bild speichern ---
            save_dir = Path("img")
            save_dir.mkdir(parents=True, exist_ok=True)
        
            timestamp = datetime.datetime.now().isoformat().replace(":", "-").replace(".", "-")
            filename = f"img_{timestamp}.jpg"
            file_path = save_dir / filename
        
            with open(file_path, "wb") as f:
                f.write(image_bytes)

        
        image_part = {
            "mime_type": file.content_type,
            "data": image_bytes
        }

        prompt_parts = [
            image_part,
            "Bitte lies den Zählerstand auf diesem Bild ab. Gib nur die Zahl des Zählerstands zurück, ohne zusätzlichen Text.",
        ]

        response = await model.generate_content_async(prompt_parts)
        
        meter_reading = response.text.strip()
        
        if not meter_reading.isdigit():
            print(f"WARNUNG: Zählerstand ist keine Zahl: '{meter_reading}'. Versuche trotzdem zu senden.")
            # Du könntest hier auch eine HTTPException auslösen, wenn nur numerische Werte erlaubt sind.

        # --- MQTT-Nachricht als JSON senden ---
        mqtt_payload = {
            "timestamp": timestamp,
            "meter_reading": meter_reading
        }
        mqtt_message = json.dumps(mqtt_payload) # Konvertiere das Dictionary in einen JSON-String

        try:
            client = mqtt.Client()
            client.connect(MQTT_BROKER, 1883, 60)
            client.publish(MQTT_TOPIC, mqtt_message) # Sende den JSON-String
            client.disconnect()
            print(f"Zählerstand erkannt: {meter_reading}, Zeitstempel: {timestamp}. Via MQTT gesendet.")
        except Exception as mqtt_e:
            print(f"Fehler beim Senden der MQTT-Nachricht: {mqtt_e}")
            raise HTTPException(status_code=500, detail=f"Failed to send data via MQTT: {mqtt_e}")

        # Die API-Antwort enthält weiterhin nur den Zählerstand, wenn das so gewünscht ist
        return {"meter_reading": meter_reading, "timestamp": timestamp}

    except genai.types.BlockedPromptException as bp_e:
        print(f"Prompt wurde von Gemini blockiert (Sicherheitsgründe): {bp_e}")
        raise HTTPException(status_code=400, detail=f"Prompt blocked by AI (safety reasons): {bp_e}")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process image with Gemini: {e}")
