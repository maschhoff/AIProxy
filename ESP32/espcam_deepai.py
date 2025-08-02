# AIProxy ESP32 CAM Image Module
# Anpassung für DeepAI OCR

import network
import urequests as requests  # "urequests" für MicroPython
import machine
import time
import sys
from settings_deep import * 
from umqtt.simple import MQTTClient

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

def send_image_to_deepai(image_data, api_key):
    url = "https://api.deepai.org/api/openai-vision"

    headers = {
        "api-key": api_key,
        "Content-Type": "multipart/form-data; boundary=----DeepAIBoundary"
    }

    boundary = "----DeepAIBoundary"

    prompt_text = "Lies den Zählerstand ab und gib den Wert als Integer zurück"

    # Multipart-Body manuell bauen
    body = (
        "--" + boundary + "\r\n" +
        'Content-Disposition: form-data; name="image"; filename="image.jpg"\r\n' +
        "Content-Type: image/jpeg\r\n\r\n"
    ).encode() + image_data + (
        "\r\n--" + boundary + "\r\n" +
        'Content-Disposition: form-data; name="text"\r\n\r\n' +
        prompt_text + "\r\n" +
        "--" + boundary + "--\r\n"
    ).encode()

    try:
        response = requests.post(url, headers=headers, data=body)
        print("Status:", response.status_code)
        if response.status_code == 200:
            print("Antwort:", response.text)
            return response.text
        else:
            print("Fehlerantwort:", response.text)
            return 0
        response.close()
    except Exception as e:
        print("Fehler beim Senden:", e)

def send_mqtt(zaehlerstand, broker, port, topic):
    try:
        client = MQTTClient("esp32_cam", broker, port)
        client.connect()
        client.publish(topic, zaehlerstand)
        print("Zählerstand per MQTT gesendet:", zaehlerstand)
        client.disconnect()
    except Exception as e:
        print("MQTT Fehler:", e)

# Main-Loop
connect_wifi(SSID, PASSWORD)

while True:
    img = capture_image()
    stand=send_image_to_deepai(img, DEEPAI_API_KEY)
    send_mqtt(stand,MQTT_BROKER, MQTT_PORT, MQTT_TOPIC)
    time.sleep(600)  # alle 10 Minuten
