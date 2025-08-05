# AIProxy ESP32 CAM Image Module
# Angepasst für Gemini API

import network
import urequests as requests
import machine
import time
import sys
from settings import *
from umqtt.simple import MQTTClient
import ujson as json
import time
import usocket
import ussl
import ubinascii
import camera  # Passendes Kamera-Modul verwenden

# Blitz-LED (GPIO 4)
flash = machine.Pin(4, machine.Pin.OUT)

# WLAN verbinden
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Verbinde mit WLAN...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Netzwerk config:', wlan.ifconfig())

# Bild aufnehmen mit Blitz
def capture_image():
    try:
        flash.on()
        time.sleep(0.2)
        camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
        camera.framesize(camera.FRAME_XGA)
        camera.quality(10)
        camera.contrast(2)
        camera.brightness(2)
        camera.saturation(-2)
        buf = camera.capture()
        flash.off()
        camera.deinit()
        if not buf:
            print("Fehler bei der Bildaufnahme")
            flash.off
            machine.reset()
        print("Bild aufgenommen")
        return buf
    except Exception as e:
        print("Fehler beim Bild aufnehmen:", e)
        flash.off
        machine.reset()
        return 0

def send_image_to_gemini(image_data, api_key):
    """
    Sendet ein Bild an die Gemini API, um den Zählerstand zu lesen.
    """
    host = "generativelanguage.googleapis.com"
    port = 443
    path = f"/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    # Bild als base64-String kodieren
    # Gemini erwartet nur den base64-Teil ohne den Daten-URI-Präfix
    #image_base64 = ubinascii.b2a_base64(image_data).decode().replace("\n", "")
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
    
    # HTTP-Request aufbauen
    header  = (
        "POST " + path + " HTTP/1.1\r\n" +
        "Host: " + host + "\r\n" +
        "Content-Type: application/json\r\n" +
        "Content-Length: " + str(content_length) + "\r\n" +
        "Connection: close\r\n\r\n"
    )

    try:
        # TLS-Verbindung herstellen
        addr = usocket.getaddrinfo(host, port)[0][-1]
        sock = usocket.socket()
        sock.connect(addr)
        ssl_sock = ussl.wrap_socket(sock, server_hostname=host)

        # Header und Body separat senden
        ssl_sock.write(header)
        ssl_sock.write(json_bytes)

        response = b""
        while True:
            try:
                chunk = ssl_sock.read(1024)
                if not chunk:
                    break
                response += chunk
            except:
                break

        ssl_sock.close()
        response_text = response.decode()
        #print("Antwort:" +response_text)

        # Die Antwort der Gemini API parsen
        # Suchen Sie den Beginn des JSON-Körpers
        body_start = response_text.find("text\":") 
        if body_start != -1:
            body_start += len('"text": "') 
            end = response_text.find('"', body_start)
            result = response_text[body_start:end]
            print("Ergebnis:" + result)
            return result
        else:
            return 0

    except Exception as e:
        print("Fehler beim Senden an Gemini:", e)
        return 0


# ONLY FOR DEBUG!!!
def send_image_to_ai(image_data, backend):
    url = "http://" + backend + "/process_meter_image?mqtt_topic="+MQTT_TOPIC
    
    # Multipart/FormData bauen
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}"
    }
    
    # Multipart body als Bytes zusammensetzen
    body_start = (
        "--{}\r\n".format(boundary) +
        'Content-Disposition: form-data; name="file"; filename="image.jpg"\r\n' +
        "Content-Type: image/jpeg\r\n\r\n"
    ).encode()

    body_end = "\r\n--{}--\r\n".format(boundary).encode()

    body = body_start + image_data + body_end
    
    try:
        response = requests.post(url, headers=headers, data=body)
        print("Status:", response.status_code)
        if response.status_code == 200:
            print("Antwort:", response.text)
        response.close()
    except Exception as e:
        print("Fehler beim Senden:", e)


# SEND TO MQTT
def send_mqtt(zaehlerstand, image_data):
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

        # Das Bild senden (für die Kamera-Entität)
        client.publish(MQTT_TOPIC+"/img", image_data)
        print("MQTT Bild gesendet.")

        client.disconnect()

    except Exception as e:
        print("MQTT Fehler:", e)
        return

# Main-Loop
print("...Smart Meter AI Cam starting...")
connect_wifi(SSID, PASSWORD)
last_reading = 0

while True:
    img = capture_image()
    stand = send_image_to_gemini(img, API_KEY)

    try:
        stand= stand.replace(".", "")
        stand_int = int(stand)
    except:
        print("Ungültiger Zählerstand empfangen:", stand)
        continue

    if stand_int > last_reading:
        send_mqtt(str(stand_int), img)
        last_reading = stand_int
    else:
        print("Zählerstand ist nicht höher – MQTT wird nicht gesendet.")

    print("waiting...")
    time.sleep(3600)
