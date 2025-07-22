# AIProxy ESP32 CAM Image Module

> **Autor:** Mathias Aschhoff  
> **Version:** 2025  
> **Zweck:** Automatisierte Bilderfassung per ESP32-CAM und Versand an eine AI-Backend-API zur Analyse (z. B. Zählerstände via MQTT).  

---

## 📷 Projektübersicht

Dieses MicroPython-Modul für den ESP32-CAM nimmt in regelmäßigen Intervallen ein Bild auf (z. B. von einem Stromzähler), aktiviert dabei optional den Blitz (LED), und sendet das Bild via HTTP an einen AI-Backend-Server zur weiteren Verarbeitung. Die Ergebnisse können über MQTT bereitgestellt werden.

---

## ⚙️ Voraussetzungen

- **Hardware:**
  - ESP32-CAM Modul
  - LED-Blitz (GPIO 4)
  - WLAN-Zugang
- **Software:**
  - MicroPython Firmware für ESP32-CAM
  - Passendes Kamera-Modul (z. B. `esp32-camera` Bibliothek)
  - ESP32 CAM Firmware mit Micropython 1.21 

---

## Konfiguration

SSID = "xxx"                   # WLAN SSID
PASSWORD = "xxx"              # WLAN Passwort
BACKEND = "192.168.100.109:8000"  # Backend-IP mit Port
MQTT_TOPIC = "zaehler/strom"  # MQTT-Topic zur Ergebnisveröffentlichung



