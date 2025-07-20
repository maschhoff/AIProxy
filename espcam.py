# AIProxy ESP32 CAM Image Module
# Mathias Aschhoff 2025

import network
import socket
import machine
import time

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

def capture_image():
    flash.on()  # Blitz AN
    time.sleep(0.2)  # kurze Einschaltzeit vor Foto
    camera.init()
    buf = camera.capture()
    if not buf:
        print("Fehler bei der Bildaufnahme")
        return buf
    else:
        camera.deinit()
        flash.off()  # Blitz AUS
        print("Bild aufgenommen "+len(buf))
        return buf

# Bild an Backend senden
import socket

def send_image_to_ai(image_data, backend):
    # KEIN "http://" im backend
    host = backend  # z. B. "192.168.1.42"
    path = "/process_meter_image"
    port = 8000

    try:
        # DNS-Auflösung
        addr_info = socket.getaddrinfo(host, port)
        if not addr_info:
            print("Fehler: konnte Host nicht auflösen")
            return

        addr = addr_info[0][-1]
        s = socket.socket()
        s.connect(addr)

        # Header bauen
        content_length = len(image_data)
        headers = (
            "POST {} HTTP/1.1\r\n"
            "Host: {}\r\n"
            "Content-Type: application/octet-stream\r\n"
            "Content-Length: {}\r\n"
            "Connection: close\r\n\r\n"
        ).format(path, host, content_length)

        s.send(headers.encode('utf-8'))
        s.send(image_data)

        # Antwort empfangen
        response = b""
        while True:
            chunk = s.recv(512)
            if not chunk:
                break
            response += chunk

        s.close()

        # Ausgabe
        response_str = response.decode("utf-8", "ignore")
        print("Antwort:", response_str.split("\r\n\r\n", 1)[-1])

    except Exception as e:
        print("Fehler beim Senden:", e)


# Main-Loop
SSID = "xxx"
PASSWORD = "xxx"
BACKEND = "192.168.100.109"

connect_wifi(SSID, PASSWORD)

while True:
    image = capture_image()
    send_image_to_ai(image, BACKEND)
    time.sleep(600)  # alle 10 Minuten
