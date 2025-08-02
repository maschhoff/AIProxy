# AIProxy ESP32 CAM Image Module
# Anpassung für DeepAI OCR

import network
import urequests as requests  # "urequests" für MicroPython
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

#2e1dddc8621f72155f24cf2e0adbde548458d3cab9f00c0139eea840d0ac4746

def send_image_to_replicate(image_data, api_token):
    host = "api.replicate.com"
    port = 443
    path = "/v1/predictions"

    # Bild als base64-String kodieren
    image_base64 = "data:image/jpeg;base64," +ubinascii.b2a_base64(image_data).decode().replace("\n", "")

    # JSON-Body erstellen – Modellabhängig!
    data = {
        "version": "2e1dddc8621f72155f24cf2e0adbde548458d3cab9f00c0139eea840d0ac4746",
        "input": {
            "image_base64": image_base64,
            "prompt": "Lese den Zählerstand und gib ihn als Integer zurück."
        }
    }

    json_data = json.dumps(data)
    json_bytes = json_data.encode()
    content_length = len(json_bytes)

   
   # HTTP-Request aufbauen
    header  = (
        "POST " + path + " HTTP/1.1\r\n" +
        "Host: " + host + "\r\n" +
        "Authorization: Bearer " + api_token + "\r\n" +
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
        ssl_sock.write(json_bytes)  # hier ist wichtig: vollständige Byte-Daten senden

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
        print("Antwort:", response_text)

        if "200 OK" in response_text or "201 Created" in response_text:
            body = response_text.split("\r\n\r\n", 1)[1]
            try:
                parsed = json.loads(body)
                return parsed
            except:
                return body
        else:
            return 0

    except Exception as e:
        print("Fehler beim Senden:", e)
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
    stand=send_image_to_replicate(img, API_KEY)
    send_mqtt(stand,MQTT_BROKER, MQTT_PORT, MQTT_TOPIC)
    time.sleep(600)  # alle 10 Minuten
