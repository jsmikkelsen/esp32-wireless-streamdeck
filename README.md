# ESP32 Trådløs Stream Deck & Audio Mixer

Et trådløst, tilpasseligt DIY Stream Deck og 4-kanals audio mixer bygget på en **ESP32**, **12x MX-taster** (i 3x4 anti-ghosting matrix med dioder), **4x potentiometre** og et **SSD1306 128x64 OLED-display**.

Projektet forbinder trådløst til din PC via Wi-Fi og en ultra-lav latens WebSocket-forbindelse. Du kan give enheden strøm fra en hvilken som helst 5V USB-oplader eller powerbank – **uden at have et kabel i computeren**.

---

## 🌟 Nøglefunktioner

* **Trådløs frihed:** Kører over lokalt Wi-Fi (svartid typisk 2-5 ms).
* **4-kanals hardware mixer:** Fysiske drejeknapper til individuel styring af f.eks. Master, Discord, Spotify og Browser.
* **Dynamisk OLED-dashboard:** 128x64 display viser 4 vertikale volumensøjler med live procenttal og kanalnavne.
* **12 programmerbare MX-taster:** 3x4 matrix med 1N4148-dioder for fuld anti-ghosting (N-key rollover).
* **Ingen gen-flashing påkrævet:** Handlinger og app-lydstyring konfigureres i `config.json` på din PC. Ret filen, og ændringerne træder i kraft med det samme!
* **Støjfri potentiometre:** Softwaren benytter Exponential Moving Average (EMA) filtrering og deadband, så lydstyrken aldrig flimrer.

---

## 📁 Projektstruktur

```text
esp32-wireless-streamdeck/
├── 3D/                           # 3D-filer til kabinet (STL, OpenSCAD og generator)
│   ├── streamdeck_top_plate.stl  # Topplade klar til 3D-print
│   ├── streamdeck_bottom_case.stl# Bundkabinet med USB-port klar til 3D-print
│   ├── generate_case.py          # Python STL generator
│   ├── streamdeck_case.scad      # Parametrisk OpenSCAD kildekode
│   └── README.md                 # Print- og monteringsvejledning
├── docs/
│   └── WIRING.md                 # Komplet lodde- og kablingsguide med diagrammer
├── firmware/
│   ├── platformio.ini            # PlatformIO projektfil
│   ├── src/
│   │   └── main.cpp              # C++ firmware kildekode
│   └── firmware.ino              # Samme firmware som Arduino IDE sketch
├── pc_server/
│   ├── config.json               # Konfiguration af taster og lydkanaler (ret her!)
│   ├── requirements.txt          # Python afhængigheder
│   └── streamdeck_server.py      # Baggrundsserver på PC (WebSocket + Audio + Hotkeys)
├── .gitignore
└── README.md
```

---

## 🛠️ Hardware Komponenter

1. **ESP32 DevKit** (NodeMCU-32S / ESP32-WROOM-32)
2. **12x Cherry MX kompatible switches**
3. **12x Dioder** (f.eks. 1N4148)
4. **4x Drejepotentiometre** (10k lineære)
5. **1x 0.96" I2C OLED display (SSD1306 128x64)**

Se [docs/WIRING.md](docs/WIRING.md) for detaljerede instruktioner om pin-forbindelser og lodning.

---

## 🚀 Hurtigstart Guide

### Trin 1: Kabling
Følg oversigten i [docs/WIRING.md](docs/WIRING.md).
* **Vigtigt:** Potentiometre forbindes til **3.3V** og ADC1-pinnene (**GPIO 32, 33, 34, 35**).
* **OLED:** SDA -> GPIO 21, SCL -> GPIO 22.

---

### Trin 2: Flash ESP32 Firmware

Åbn projektet i **PlatformIO** (VS Code) eller **Arduino IDE**:

1. Åbn `firmware/src/main.cpp` (eller `firmware/firmware.ino`).
2. Ret Wi-Fi oplysningerne og din PC's lokale IP-adresse:
   ```cpp
   const char* WIFI_SSID     = "DIT_WIFI_NAVN";      // 2.4 GHz Wi-Fi netværk
   const char* WIFI_PASSWORD = "DIT_WIFI_KODE";
   const char* PC_HOST       = "192.168.1.100";     // Din PC's lokale IPv4 adresse
   const int   WS_PORT       = 8765;
   ```
3. Upload koden til din ESP32.

> **Biblioteker til Arduino IDE:**
> * `Adafruit SSD1306` & `Adafruit GFX Library`
> * `WebSockets` af Markus Sattler
> * `ArduinoJson` (v6 eller nyere)

---

### Trin 3: Start PC Companion Serveren

På din PC (Windows anbefales for app-volumen):

1. Åbn en terminal / kommandoprompt i mappen `pc_server/`.
2. Installer kravene:
   ```bash
   pip install -r requirements.txt
   ```
3. Start serveren:
   ```bash
   python streamdeck_server.py
   ```
Serveren lytter nu på port `8765`. Når din ESP32 tænder, forbinder den automatisk, og skærmen opdateres!

---

### Trin 4: Tilpas dine taster og lydkanaler

Åbn `pc_server/config.json` i din foretrukne teksteditor:

```json
{
  "channels": [
    { "label": "MST", "target": "master" },
    { "label": "DIS", "target": "discord.exe" },
    { "label": "SPT", "target": "spotify.exe" },
    { "label": "APP", "target": "chrome.exe" }
  ],
  "keys": {
    "1": { "name": "Play/Pause", "action": "media_play_pause" },
    "2": { "name": "Mute Mic", "action": "hotkey", "keys": ["ctrl", "shift", "m"] },
    "3": { "name": "Lommeregner", "action": "launch", "cmd": "calc.exe" }
  }
}
```

* **Understøttede handlinger for taster:**
  * `"action": "hotkey"` med `"keys": ["ctrl", "alt", "del"]`
  * `"action": "media_play_pause"`, `"media_next"`, `"media_prev"`, `"media_mute"`
  * `"action": "launch"` med et vilkårligt program eller script i `"cmd"`

---

## 🔍 Fejlfinding

* **ESP32 kan ikke forbinde til Wi-Fi:**
  * ESP32 understøtter kun **2.4 GHz Wi-Fi** (ikke 5 GHz). Sørg for at dit netværk udsender 2.4 GHz.
* **ESP32 viser "Connecting..." på skærmen:**
  * Tjek at `PC_HOST` i firmwaren matcher computerens IP (`ipconfig` i Windows kommandoprompt).
  * Tjek at Windows Firewall ikke blokerer for port `8765`.
* **Potentiometer-værdier virker ikke under Wi-Fi:**
  * Sørg for at potentiometrene er forbundet til GPIO 32-35 (ADC1). Pins på ADC2 (f.eks. GPIO 2, 4, 12-15) virker ikke når Wi-Fi er tændt.

---

## 📜 Licens
MIT
