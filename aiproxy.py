# filename: aiproxy.py
# GPL Mathias Aschhoff 2025 (adapted for Gemini by Gemini)

from fastapi import FastAPI, UploadFile, HTTPException
import requests # Not used in the provided snippet, but often useful in proxies
import os
import base64 # Not directly used for image processing with genai, but for other tasks
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
        # Optional: Raise an exception here if the API key is strictly required for startup
        # raise HTTPException(status_code=500, detail="GOOGLE_API_KEY environment variable not set.")

# Process meter image using Gemini and send via MQTT
@app.post("/process_meter_image")
async def process_meter_image(file: UploadFile):
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=400, detail="GOOGLE_API_KEY not set.")

    # Validate file type if necessary, e.g., only allow images
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

    try:
        # Load the Gemini 1.5 Flash model (current equivalent of "2.0 Flash")
        # For the very latest version, you might also try 'gemini-1.5-flash-latest'
        # or a specific version like 'gemini-1.5-flash-001' if you want a fixed version.
        model = genai.GenerativeModel('gemini-1.5-flash')

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

        # Generate content using the Gemini 1.5 Flash model
        response = await model.generate_content_async(prompt_parts) # Use async version for FastAPI context
        
        # Extract the meter reading from the response
        # Ensure to handle cases where response.text might be empty or not a number
        meter_reading = response.text.strip()
        
        # Optional: Basic validation if the response is numeric
        if not meter_reading.isdigit():
            print(f"WARNUNG: Zählerstand ist keine Zahl: '{meter_reading}'")
            # You might want to handle this more robustly, e.g., retry or log an error
            # For now, we'll still attempt to send it, but it might not be what you expect.
            # Or raise an exception: raise HTTPException(status_code=500, detail=f"Invalid meter reading from AI: {meter_reading}")


        # Send via MQTT
        # Add basic error handling for MQTT connection/publish
        try:
            client = mqtt.Client()
            client.connect(MQTT_BROKER, 1883, 60)
            client.publish(MQTT_TOPIC, meter_reading)
            client.disconnect()
            print(f"Zählerstand erkannt und via MQTT gesendet: {meter_reading}")
        except Exception as mqtt_e:
            print(f"Fehler beim Senden des Zählerstands via MQTT: {mqtt_e}")
            # Decide if you want to fail the API request if MQTT fails
            raise HTTPException(status_code=500, detail=f"Failed to send meter reading via MQTT: {mqtt_e}")


        return {"meter_reading": meter_reading}

    except genai.types.BlockedPromptException as bp_e:
        print(f"Prompt wurde von Gemini blockiert (Sicherheitsgründe): {bp_e}")
        raise HTTPException(status_code=400, detail=f"Prompt blocked by AI (safety reasons): {bp_e}")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        # Return a 500 Internal Server Error for unhandled exceptions
        raise HTTPException(status_code=500, detail=f"Failed to process image with Gemini: {e}")
