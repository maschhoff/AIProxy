# AIProxy ESP32 CAM Image Module

> **Autor:** Mathias Aschhoff  
> **Version:** 2025  
> **Zweck:** Automatisierte Bilderfassung per ESP32-CAM und Versand an eine AI-Backend-API zur Analyse (z. B. Zählerstände via MQTT).  

---

## 📷 Projektübersicht

Dieses MicroPython-Skript für einen **ESP32-CAM** erfasst in regelmäßigen Abständen Bilder und sendet diese zur Verarbeitung an einen definierten Backend-Server. Es ist ideal für Projekte, bei denen eine Kamera kontinuierlich Daten, wie zum Beispiel Zählerstände, erfassen und an eine zentrale Stelle weitergeben soll.

## Funktionen

* **WLAN-Verbindung:** Stellt eine Verbindung zu einem angegebenen WLAN-Netzwerk her.
* **Bildaufnahme mit Blitz:** Nimmt ein Bild mithilfe des integrierten Blitzes der ESP32-CAM auf.
* **Senden an ein Backend:** Sendet das aufgenommene Bild als `multipart/form-data` an eine definierte REST-API.

## Voraussetzungen

### Hardware

* **ESP32-CAM 8MB PSRAM:** Ein ESP32-Board mit integrierter Kamera und 8MB PSRAM.

### Software

* **MicroPython Firmware:** CAM Firmware min 2.21. (https://github.com/lemariva/micropython-camera-driver)
* **MicroPython:** Das Skript ist für die Ausführung unter MicroPython konzipiert.
* **`camera` Modul:** Ein passendes `camera`-Modul für MicroPython ist erforderlich. Die genaue Implementierung kann je nach ESP32-CAM-Variante variieren.

## Installation und Einrichtung

1.  **WLAN-Konfiguration:**
    Passe die Variablen `SSID` und `PASSWORD` im Skript an, um die WLAN-Zugangsdaten für dein Netzwerk einzutragen.
2.  **Backend-Konfiguration:**
    Setze die Variable `BACKEND` auf die IP-Adresse und den Port deines Backend-Servers.
3.  **MQTT-Topic:**
    Definiere das `MQTT_TOPIC`, das an das Backend übergeben werden soll, um die Bilddaten zu kategorisieren.
4.  **Skript hochladen:**
    Lade das Skript auf deinen ESP32-CAM hoch (z.B. mit `ampy` oder dem `Thonny IDE`).

## Benutzung

Das Skript wird automatisch ausgeführt und führt folgende Schritte in einer Endlosschleife aus:

1.  Verbindet sich mit dem WLAN.
2.  Nimmt ein Bild auf.
3.  Sendet das Bild an das Backend unter der URL `http://BACKEND/process_meter_image?mqtt_topic=MQTT_TOPIC`.
4.  Wartet die im Skript definierte Zeit (standardmäßig 10 Minuten), bevor der Zyklus erneut beginnt.

---

### Autor

Mathias Aschhoff (2025)



