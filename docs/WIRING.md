# Kabling og Hardware Guide (Wiring Guide)

Denne guide forklarer trin for trin, hvordan du forbinder din **ESP32**, **12x MX-taster**, **12x dioder**, **4x potentiometre** og **0.96" OLED I2C display**.

---

## 1. Komponentliste (BOM)

* **1x ESP32 NodeMCU / DevKit** (30-pin eller 38-pin version)
* **12x Cherry MX kompatible switches**
* **12x Dioder** (f.eks. standard **1N4148** switching-dioder)
* **4x Drejepotentiometre** (10kΩ lineære anbefales, standard 3-bens)
* **1x 0.96" SSD1306 OLED Display** (128x64, I2C interface med 4 ben: GND, VCC, SCL, SDA)
* Montagetråd / jumper-ledninger
* USB-kabel til strømforsyning (5V USB-oplader eller powerbank)

---

## 2. Pinout Oversigt på ESP32

| Modul | Signal / Funktion | ESP32 GPIO | Note |
| :--- | :--- | :--- | :--- |
| **OLED (SSD1306)** | GND | **GND** | Fælles stel |
| | VCC | **3.3V** | **OBS:** Må ikke sluttes til 5V (kan brænde displayet af) |
| | SCL | **GPIO 22** | Hardware I2C Clock |
| | SDA | **GPIO 21** | Hardware I2C Data |
| **Potentiometer 0 (Master)** | Signal (midterste ben) | **GPIO 32** | ADC1_CH4 (fungerer med Wi-Fi aktivt) |
| **Potentiometer 1 (Discord)** | Signal (midterste ben) | **GPIO 33** | ADC1_CH5 (fungerer med Wi-Fi aktivt) |
| **Potentiometer 2 (Spotify)** | Signal (midterste ben) | **GPIO 34** | ADC1_CH6 (Input-only pin på ESP32) |
| **Potentiometer 3 (App/Browser)** | Signal (midterste ben) | **GPIO 35** | ADC1_CH7 (Input-only pin på ESP32) |
| **Matrix Række 0** | Row 0 (Tast 1, 2, 3, 4) | **GPIO 13** | Output (køres LOW under scan) |
| **Matrix Række 1** | Row 1 (Tast 5, 6, 7, 8) | **GPIO 14** | Output |
| **Matrix Række 2** | Row 2 (Tast 9, 10, 11, 12)| **GPIO 27** | Output |
| **Matrix Kolonne 0** | Col 0 (Tast 1, 5, 9) | **GPIO 18** | Input med intern `INPUT_PULLUP` |
| **Matrix Kolonne 1** | Col 1 (Tast 2, 6, 10) | **GPIO 19** | Input med intern `INPUT_PULLUP` |
| **Matrix Kolonne 2** | Col 2 (Tast 3, 7, 11) | **GPIO 23** | Input med intern `INPUT_PULLUP` |
| **Matrix Kolonne 3** | Col 3 (Tast 4, 8, 12) | **GPIO 25** | Input med intern `INPUT_PULLUP` |

---

## 3. MX Taster & 3x4 Matrix med Dioder

Ved at bruge en **3x4 switch matrix** behøver vi kun 7 GPIO-pins i stedet for 12. Dioderne forhindrer "ghosting", så du kan trykke på flere taster samtidig.

### Dioderetning (Katode mod Række)
En 1N4148 diode har en sort/farvet ring i den ene ende (**katoden**):
```text
        Anode (+)                Katode (-) med ring
          [=====]---------------------[ | ]-----------------> Til Række (Row)
```

### Lodning på hver switch:
1. **Ben 1 på switchen:** Loddes direkte til **Kolonne-ledningen (Col)**.
2. **Ben 2 på switchen:** Loddes til diodens **anode** (enden uden ring).
3. **Diodens katode** (enden med ring): Loddes til **Række-ledningen (Row)**.

### Skematisk diagram:

```text
                  Col 0           Col 1           Col 2           Col 3
                (GPIO 18)       (GPIO 19)       (GPIO 23)       (GPIO 25)
                    |               |               |               |
Row 0 ----------|<--[SW 1]------|<--[SW 2]------|<--[SW 3]------|<--[SW 4]
(GPIO 13)           |               |               |               |
Row 1 ----------|<--[SW 5]------|<--[SW 6]------|<--[SW 7]------|<--[SW 8]
(GPIO 14)           |               |               |               |
Row 2 ----------|<--[SW 9]------|<--[SW 10]-----|<--[SW 11]-----|<--[SW 12]
(GPIO 27)           |               |               |               |
```

### Tast-mapping:
* **Tast 1:** Row 0, Col 0
* **Tast 2:** Row 0, Col 1
* **Tast 3:** Row 0, Col 2
* **Tast 4:** Row 0, Col 3
* **Tast 5:** Row 1, Col 0
* **Tast 6:** Row 1, Col 1
* **Tast 7:** Row 1, Col 2
* **Tast 8:** Row 1, Col 3
* **Tast 9:** Row 2, Col 0
* **Tast 10:** Row 2, Col 1
* **Tast 11:** Row 2, Col 2
* **Tast 12:** Row 2, Col 3

---

## 4. De 4 Potentiometre (Kritisk om ADC1)

Potentiometrene fungerer som spændingsdelere:
* **Venstre ben:** Forbindes til **GND** (fælles stel).
* **Højre ben:** Forbindes til **3.3V** (Brug ALDRIG 5V, da ESP32's analoge indgange max tåler 3.3V).
* **Midterste ben (Wiper / Signal):** Forbindes til de respektive ADC1 pins:
  * Pot 0 -> **GPIO 32**
  * Pot 1 -> **GPIO 33**
  * Pot 2 -> **GPIO 34**
  * Pot 3 -> **GPIO 35**

> **Vigtig ESP32 teknisk note:** 
> ESP32 har to analoge konvertere (ADC1 og ADC2). Når Wi-Fi aktiveres i koden, beslaglægger ESP32's Wi-Fi driver automatisk **ADC2** (GPIO 0, 2, 4, 12, 15, 25, 26). Derfor virker analoge målinger på ADC2 ikke trådløst! Vores opsætning benytter udelukkende **ADC1**, som fungerer 100% stabilt sammen med Wi-Fi.

---

## 5. OLED Display (SSD1306)

* **GND** -> ESP32 GND
* **VCC** -> ESP32 3.3V
* **SCL** -> ESP32 GPIO 22
* **SDA** -> ESP32 GPIO 21
*(Standard I2C adresse er `0x3C`).*
