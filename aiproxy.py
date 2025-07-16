# filename: proxy_server.py

from fastapi import FastAPI, UploadFile
import requests
import os
import base64
import paho.mqtt.client as mqtt

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_TOPIC = "zaehler/stand"

# OpenAI Vision verarbeiten und per MQTT senden
@app.post("/process_meter_image")
async def process_meter_image(file: UploadFile):
    if not OPENAI_API_KEY:
        return {"error": "OPENAI_API_KEY not set"}

    image_bytes = await file.read()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Bitte lies den Zählerstand auf diesem Bild ab."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        json=payload,
        headers=headers
    )

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    meter_reading = result["choices"][0]["message"]["content"].strip()

    # Per MQTT senden
    client = mqtt.Client()
    client.connect(MQTT_BROKER, 1883, 60)
    client.publish(MQTT_TOPIC, meter_reading)
    client.disconnect()

    print(f"Zählerstand erkannt: {meter_reading}")
    return {"meter_reading": meter_reading}
