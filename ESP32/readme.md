# AIProxy ESP32 CAM Image Module

> **Autor:** Mathias Aschhoff  
> **Version:** 2025  
> **Zweck:** Automatisierte Bilderfassung per ESP32-CAM und Versand an ein AI zur Analyse (z. B. Zählerstände via MQTT).  

---

## 📷 Projektübersicht

Dieses MicroPython-Skript für einen **ESP32-CAM** oder **ESP32-S3-CAM** erfasst in regelmäßigen Abständen Bilder und sendet diese zur Verarbeitung an Gemini AI. Es ist ideal für Projekte, bei denen eine Kamera kontinuierlich Daten, wie zum Beispiel Zählerstände, erfassen und an eine zentrale Stelle weitergeben soll.

## Funktionen

* **WLAN-Verbindung:** Stellt eine Verbindung zu einem angegebenen WLAN-Netzwerk her.
* **Bildaufnahme mit Blitz:** Nimmt ein Bild mithilfe des integrierten Blitzes der ESP32-CAM auf.
* **Senden an ein Gemini:** Sendet das aufgenommene Bild als `multipart/form-data` an die API.

## Voraussetzungen

### Hardware

* **ESP32-CAM 8MB PSRAM:** Ein ESP32-Board mit integrierter Kamera und 8MB PSRAM.
* **ESP32-S3-CAM 8MB PSRAM:** 

### Software

* **MicroPython Firmware:** CAM Firmware -> (https://github.com/cnadler86/micropython-camera-API/releases/)
* **MicroPython:** Das Skript ist für die Ausführung unter MicroPython konzipiert.
* **`camera` Modul:** Ein passendes `camera`-Modul für MicroPython ist erforderlich. Die genaue Implementierung kann je nach ESP32-CAM-Variante variieren.

## Installation und Einrichtung

1.  **WLAN-Konfiguration:**
    Passe die Variablen `SSID` und `PASSWORD` im Skript an, um die WLAN-Zugangsdaten für dein Netzwerk einzutragen.
2.  **Gemini-Konfiguration:**
    Setze die Variable `API-KEY` für den Gemini API Key. Den bekommst du kostenlos unter https://aistudio.google.com/app/apikey
3.  **MQTT-Topic:**
    Definiere das `MQTT_TOPIC`, das an das Backend übergeben werden soll, um die Bilddaten zu kategorisieren.
4.  **Skript hochladen:**
    Flashe die Firmware mit Thonny und lade das Skript auf deinen ESP32-CAM hoch (z.B. mit `Thonny IDE`).

## Benutzung

Das Skript wird automatisch ausgeführt und führt folgende Schritte in einer Endlosschleife aus:

1.  Verbindet sich mit dem WLAN.
2.  Nimmt ein Bild auf.
3.  Sendet das Bild an Gemini.
4.  Wartet die im Skript definierte Zeit (standardmäßig 60 Minuten), bevor der Zyklus erneut beginnt.

## Home Assistant Integration

Füge dies zur configuration.yaml hinzu:

"""
mqtt:
  sensor:
    - name: "Stromzählerstand"
      state_topic: "zaehlerstand/Strom"
      unit_of_measurement: "kWh"
      device_class: energy
      state_class: total_increasing
"""


---

### Autor

Mathias Aschhoff (2025)



