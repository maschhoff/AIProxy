# filename: aiproxy_deepai.py
# GPL Mathias Aschhoff 2025

from fastapi import FastAPI, UploadFile, HTTPException, File, Query
import os
import datetime
import json
import paho.mqtt.client as mqtt
import requests
from pathlib import Path

app = FastAPI()

DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY")
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_TOPIC = "zaehler/stand"
DEBUG = os.getenv("DEBUG", "false").lower() in ["1", "true", "yes"]

@app.post("/process_meter_image")
async def process_meter_image(file: UploadFile = File(...), mqtt_topic: str = Query(...)):
    if not DEEPAI_API_KEY:
        raise HTTPException(status_code=400, detail="DEEPAI_API_KEY not set.")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

    if not mqtt_topic:
        raise HTTPException(status_code=400, detail="mqtt_topic parameter is required.")

    MQTT_TOPIC = mqtt_topic
    timestamp = datetime.datetime.now().isoformat()

    try:
        image_bytes = await file.read()

        if DEBUG:
            save_dir = Path("img")
            save_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.datetime.now().isoformat().replace(":", "-").replace(".", "-")
            filename = f"img_{ts}.jpg"
            file_path = save_dir / filename
            with open(file_path, "wb") as f:
                f.write(image_bytes)

        # DeepAI API-Aufruf
        response = requests.post(
            "https://api.deepai.org/api/image-to-text",
            files={"image": image_bytes},
            headers={"api-key": DEEPAI_API_KEY}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="DeepAI API call failed")

        result = response.json()
        detected_text = result.get("output", "").strip()

        if DEBUG:
            print(f"DeepAI erkannter Text: '{detected_text}'")

        # Extrahiere nur Ziffern aus dem erkannten Text
        import re
        numbers = re.findall(r'\d+', detected_text)
        if not numbers:
            meter_reading = "false"
        else:
            meter_reading = max(numbers, key=len)  # Längste gefundene Zahl

        # --- MQTT-Nachricht senden ---
        mqtt_payload = {
            "timestamp": timestamp,
            "meter_reading": meter_reading
        }
        mqtt_message = json.dumps(mqtt_payload)

        try:
            client = mqtt.Client()
            client.connect(MQTT_BROKER, 1883, 60)
            client.publish(MQTT_TOPIC, mqtt_message)
            client.disconnect()
            print(f"Zählerstand erkannt: {meter_reading}, Zeitstempel: {timestamp}. Via MQTT gesendet.")
        except Exception as mqtt_e:
            print(f"Fehler beim Senden der MQTT-Nachricht: {mqtt_e}")
            raise HTTPException(status_code=500, detail=f"Failed to send data via MQTT: {mqtt_e}")

        return {"meter_reading": meter_reading, "timestamp": timestamp}

    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process image with DeepAI: {e}")
