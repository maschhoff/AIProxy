# AIProxy ESP32 CAM Image Module
# Anpassung für DeepAI OCR

import network
import urequests as requests  # "urequests" für MicroPython
import machine
import time
import sys
from settings import * 

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

# Bild an DeepAI senden
def send_image_to_deepai(image_data, api_key):
    url = "https://api.deepai.org/api/ocr"

    headers = {
        "api-key": api_key,
    }

    # DeepAI erwartet FormData: "image" als Datei
    files = {
        'image': ('image.jpg', image_data, 'image/jpeg')
    }

    # Multipart-Form manuell bauen (MicroPython hat keine requests-toolbelt)
    boundary = "----DeepAIBoundary"
    body = (
        "--" + boundary + "\r\n" +
        'Content-Disposition: form-data; name="image"; filename="image.jpg"\r\n' +
        "Content-Type: image/jpeg\r\n\r\n"
    ).encode() + image_data + ("\r\n--" + boundary + "--\r\n").encode()

    headers["Content-Type"] = "multipart/form-data; boundary=" + boundary

    try:
        response = requests.post(url, headers=headers, data=body)
        print("Status:", response.status_code)
        if response.status_code == 200:
            print("Antwort:", response.text)
        else:
            print("Fehlerantwort:", response.text)
        response.close()
    except Exception as e:
        print("Fehler beim Senden:", e)

# Main-Loop
connect_wifi(SSID, PASSWORD)

while True:
    img = capture_image()
    send_image_to_deepai(img, DEEPAI_API_KEY)
    time.sleep(600)  # alle 10 Minuten
