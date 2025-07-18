# AIProxy ESP32 CAM Image Module
# Mathias Aschhoff 2025

import network
import urequests
import machine
import time

# Kamera-Setup für ESP32-CAM (Beispiel)
import esp32_camera as camera  # Passendes Kamera-Modul verwenden

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
    camera.init(0, format=camera.JPEG)
    buf = camera.capture()
    camera.deinit()
    flash.off()  # Blitz AUS
    return buf

# Bild an Backend senden
def send_image_to_ai(image_data, backend):
    url = "http://" + backend + "/process_meter_image"
    headers = {
        "Content-Type": "application/octet-stream"
    }
    try:
        response = urequests.post(
            url,
            headers=headers,
            data=image_data
        )
        print("Status:", response.status_code)
        if response.status_code == 200:
            print("Antwort:", response.text)
        response.close()
    except Exception as e:
        print("Fehler beim Senden:", e)

# Main-Loop
SSID = "DEIN_SSID"
PASSWORD = "DEIN_PASSWORT"
BACKEND = "192.168.100.100"

connect_wifi(SSID, PASSWORD)

while True:
    image = capture_image()
    send_image_to_ai(image, BACKEND)
    time.sleep(600)  # alle 10 Minuten
