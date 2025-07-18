# filename: aiproxy.py
# GPL Mathias Aschhoff 2025 (adapted for Gemini by Gemini)

from fastapi import FastAPI, UploadFile
import requests
import os
import base64
import paho.mqtt.client as mqtt
import google.generativeai as genai

app = FastAPI()

# Make sure to set your Google API Key as an environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_TOPIC = "zaehler/stand"

@app.on_event("startup")
async def startup_event():
    """Initializes the Google Generative AI client on application startup."""
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
    else:
        print("Warning: GOOGLE_API_KEY environment variable not set. Gemini API calls will fail.")

# Process meter image using Gemini and send via MQTT
@app.post("/process_meter_image")
async def process_meter_image(file: UploadFile):
    if not GOOGLE_API_KEY:
        return {"error": "GOOGLE_API_KEY not set"}

    try:
        # Load the Gemini Pro Vision model
        model = genai.GenerativeModel('gemini-2.0-flash')

        image_bytes = await file.read()
        
        # Create an image part for Gemini from the bytes
        image_part = {
            "mime_type": file.content_type,
            "data": image_bytes
        }

        # Construct the content for the model
        prompt_parts = [
            image_part,
            "Bitte lies den Zählerstand auf diesem Bild ab. Gib nur die Zahl des Zählerstands zurück, ohne zusätzlichen Text.",
        ]

        # Generate content using the Gemini 1.5 Pro Vision model
        response = model.generate_content(prompt_parts)
        
        # Extract the meter reading from the response
        meter_reading = response.text.strip()

        # Send via MQTT
        client = mqtt.Client()
        client.connect(MQTT_BROKER, 1883, 60)
        client.publish(MQTT_TOPIC, meter_reading)
        client.disconnect()

        print(f"Zählerstand erkannt: {meter_reading}")
        return {"meter_reading": meter_reading}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": f"Failed to process image with Gemini: {e}"}
