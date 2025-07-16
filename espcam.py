import network
import urequests
import machine
import time
import esp32_camera as camera  # Beispiel! Passendes Kamera-Modul laden

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

# Bild an Proxy-Server schicken
def send_image(image_data):
    url = "http://DEIN_PROXY_SERVER_IP:8000/process_meter_image"
    headers = {
        "Content-Type": "application/octet-stream"
    }
    response = urequests.post(url, headers=headers, data=image_data)
    print("Status:", response.status_code)
    print("Antwort:", response.text)
    response.close()

# MAIN
SSID = "DEIN_SSID"
PASSWORD = "DEIN_WLAN_PASSWORT"

connect_wifi(SSID, PASSWORD)
image = capture_image()
send_image(image)
