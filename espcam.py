import network
import urequests
import machine
import time

# Kamera-Setup für ESP32-CAM (Beispiel)
import esp32_camera as camera  # Passendes Kamera-Modul verwenden

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

# Foto aufnehmen
def capture_image():
    camera.init(0, format=camera.JPEG)
    buf = camera.capture()
    camera.deinit()
    return buf

# Bild an deinen Backend-Endpoint schicken
def send_image_to_chatgpt(image_data):
    url = "http://DEIN_BACKEND/process_meter_image"  # Dein Proxy-Server!
    headers = {
        "Content-Type": "application/octet-stream"
    }
    try:
        response = urequests.post(
            url + "?prompt=Bitte lies den Zählerstand auf diesem Bild ab",
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

connect_wifi(SSID, PASSWORD)

while True:
    image = capture_image()
    send_image_to_chatgpt(image)
    time.sleep(600)  # 600 Sekunden = 10 Minuten
