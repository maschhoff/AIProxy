# AIProxy ESP32 CAM Image Module
# Mathias Aschhoff 2025

import network
import requests # https://github.com/micropython/micropython-lib/tree/master/python-ecosys/requests
import machine
import time
import sys
from settings import * 

# Kamera-Setup für ESP32-CAM (Beispiel)
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

# Foto aufnehmen mit Blitz
def capture_image():
    flash.on()  # Blitz AN
    time.sleep(0.2)  # kurze Einschaltzeit vor Foto
    camera.init()
    buf = camera.capture()
    flash.off()  # Blitz AUS
    camera.deinit()
    if not buf:
        print("Fehler bei der Bildaufnahme")
        sys.exit()
    else:
        print("Bild aufgenommen")
        return buf

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


# Main-Loop

connect_wifi(SSID, PASSWORD)

while True:
    image = capture_image()
    send_image_to_ai(image, BACKEND)
    time.sleep(600)  # alle 10 Minuten
