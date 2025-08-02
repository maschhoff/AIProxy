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
    flash.on()
    time.sleep(0.2)
    camera.init(0, format=camera.JPEG)
    buf = camera.capture()
    flash.off()
    camera.deinit()
    if not buf:
        print("Fehler bei der Bildaufnahme")
        sys.exit()
    print("Bild aufgenommen")
    return buf

def send_image_to_gemini(image_data, api_key):
    """
    Sendet ein Bild an die Gemini API, um den Zählerstand zu lesen.
    """
    host = "generativelanguage.googleapis.com"
    port = 443
    path = f"/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"

    # Bild als base64-String kodieren
    # Gemini erwartet nur den base64-Teil ohne den Daten-URI-Präfix
    image_base64 = ubinascii.b2a_base64(image_data).decode().replace("\n", "")

    # JSON-Body für Gemini erstellen
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Lese den Zählerstand und gib ihn nur als Integer zurück."
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

def send_mqtt(zaehlerstand, broker, port, topic):
    try:
        # Zeit holen im Format ISO 8601
        t = time.localtime()
        timestamp = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(*t[:6])

        payload = {
            "timestamp": timestamp,
            "zaehlerstand": zaehlerstand
        }

        msg = json.dumps(payload)

        client = MQTTClient("esp32_cam", broker, port)
        client.connect()
        client.publish(topic, msg)
        print("MQTT gesendet:", msg)
        client.disconnect()

    except Exception as e:
        print("MQTT Fehler:", e)

# Main-Loop
connect_wifi(SSID, PASSWORD)

while True:
    img = capture_image()
    # Der Rückgabewert der Gemini-Funktion ist direkt der Zählerstand als Integer
    stand = send_image_to_gemini(img, API_KEY)
    send_mqtt(stand, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC)
    time.sleep(600)  # alle 10 Minuten

