# ESP32 S3 CAM Image Module
# mpy_cam-v1.25.0-FREENOVE_ESP32S3_CAM.zip -> https://github.com/cnadler86/micropython-camera-API/releases

import neopixel
import network
import urequests
import machine
from machine import Pin
import time
import sys
from settings import *
from umqtt.simple import MQTTClient
import ujson as json
import time
import usocket
#import ussl
import ubinascii
from camera import Camera, GrabMode, PixelFormat, FrameSize, GainCeiling

# Blitz-LED (GPIO 48)
np = neopixel.NeoPixel(Pin(48), 1) 

# WLAN verbinden
def connect_wifi(ssid, password):
    np[0] = (0, 0, 200)
    np.write()
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Verbinde mit WLAN...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():          
            time.sleep(1)
    print('Netzwerk config:', wlan.ifconfig())
    np[0] = (0, 200, 0)
    np.write()

# Bild aufnehmen mit Blitz
def capture_image():
    try:
        #flash on
        np[0] = (200, 200, 200)
        np.write()
        time.sleep(3)
        
        #camera    
        cam = Camera(pixel_format=PixelFormat.JPEG,
            frame_size=FrameSize.XGA,
            jpeg_quality=90,
            fb_count=2,
            grab_mode=GrabMode.WHEN_EMPTY)
        
        #Bild aufnehmen
        buf = cam.capture()

        #flash off
        np[0] = (0, 0, 0)
        np.write()
        
        cam.free_buffer() 

        if not buf:
            print("Fehler bei der Bildaufnahme")
            np[0] = (0, 0, 0)
            np.write()
            machine.reset()
        print("Bild aufgenommen")
        return buf
    except Exception as e:
        print("Fehler beim Bild aufnehmen:", e)
        np[0] = (0, 0, 0)
        np.write()
        machine.reset()
        return 0

def send_image_to_gemini(image_data, api_key):
    print("send_image_to_gemini")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
  
    # Encode image data to base64
    image_base64 = ubinascii.b2a_base64(image_data).strip().decode()

    # JSON-Body für Gemini erstellen
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Lese den Zählerstand ab, es müssen 6 Stellen vor dem Komma sein. Gib das Ergebnis als Zahl aus, keine zusätzlichen Worte oder Zeichen!"
                    },
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": image_base64
                        }
                    }
                ]
            }
        ]
    }
    
    json_data = json.dumps(data)
    json_bytes = json_data.encode()
    content_length = len(json_bytes)
    
    headers = {
        "Content-Type": "application/json",
        "Content-Length": str(content_length)
    }
    
    try:
        response = urequests.post(url, headers=headers, data=json_data)

        if response.status_code == 200:
            try:
                result = response.json()
            except Exception as e:
                print("JSON parse error:", e)
                print("Response text:", response.text)
                response.close()
                return None

            if (
                'candidates' in result and
                result['candidates'] and
                'content' in result['candidates'][0] and
                'parts' in result['candidates'][0]['content'] and
                result['candidates'][0]['content']['parts'] and
                'text' in result['candidates'][0]['content']['parts'][0]
            ):
                meter_reading = result['candidates'][0]['content']['parts'][0]['text']
                print("res...", meter_reading)
                response.close()
                return meter_reading
        else:
            print(f"Error: Status code {response.status_code}")
            print(response.text)

        response.close()
        return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None



# SEND TO MQTT
def send_mqtt(zaehlerstand):
    print("send_mqtt")
    try:
        client = MQTTClient("esp32_cam", MQTT_BROKER, MQTT_PORT)
        client.connect()

        # Zählerstand senden
        client.publish(MQTT_TOPIC, zaehlerstand)
        print("MQTT Zählerstand gesendet:", zaehlerstand)

        # Discovery-Konfiguration senden
        discovery_topic = "homeassistant/sensor/stromzaehler/config"
        discovery_payload = {
            "name": "Stromzähler",
            "unique_id": "esp32_stromzaehler_1",
            "state_topic": MQTT_TOPIC,
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
            "device": {
                "identifiers": ["esp32_stromzaehler_1"],
                "name": "ESP32 Stromzähler",
                "manufacturer": "ESP",
                "model": "ESP32-CAM"
            }
        }

        client.publish(discovery_topic, json.dumps(discovery_payload), retain=True)
        print("MQTT Discovery-Konfiguration gesendet.")

        client.disconnect()

    except Exception as e:
        print("MQTT Fehler:", e)
        return
    
    

# Main-Loop


art = r"""
   .-------------------.
  /  .--------------.  \
 /  /  .---------.   \  \
|  |  |  AI CAM  |   |  |
|  |  '---------'    |  |
|  '-----------------'  |
|   .-._.-.   .-._.-.   |
|  /  o   o \ /  o   o\  |
|  \   .-.   V   .-.   / |
 \  '--' '--' '--' '--' /
  '---------------------'
"""
print(art)

connect_wifi(SSID, PASSWORD)
last_reading = 0

while True:

    try:
        img = capture_image()
        stand = send_image_to_gemini(img, API_KEY)
        stand= stand.replace(".", "")
        stand_int = int(stand)  
    except Exception as e:
        print("Fehler in Main:", e)
        time.sleep(3600)
        continue

    if stand_int > last_reading:
        send_mqtt(str(stand_int))
        last_reading = stand_int
    else:
        print("Zählerstand ist nicht höher – MQTT wird nicht gesendet.")

    print("waiting...")
    time.sleep(3600)




