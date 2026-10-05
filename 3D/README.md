# 3D Print Kabinet (Enclosure Guide)

Denne mappe indeholder de færdige 3D-filer samt kildekoden til kabinettet for **ESP32 Wireless Stream Deck & Audio Mixer**.

Designet er skræddersyet til at matche det fysiske layout:
* **Venstre side:** 12x Cherry MX switches i et 4x3 gitter (standard 19.05 mm pitch).
* **Højre side:**
  * **Øverst:** 2x Potentiometre (Master & Discord)
  * **Midt:** 1x 0.96" SSD1306 OLED display
  * **Nederst:** 2x Potentiometre (Spotify & Browser/App)
* **Bagvæg:** 14.0 x 7.5 mm USB-udskæring til strømforsyning af ESP32'eren.
* **Montage:** 4x M3 hjørneskruer der forbinder toppladen sikkert med bunden.

---

## 📦 Filer i mappen

* `streamdeck_top_plate.stl` - Færdig, lukket (manifold) STL til toppladen med udskæringer til taster, potentiometre og skærm.
* `streamdeck_bottom_case.stl` - Færdig, lukket (manifold) STL til bund-kabinettet med USB-port, ESP32-sokkel og hjørnetårne.
* `generate_case.py` - Python-script der genererer de to 100% vandtætte/manifold STL-filer fra bunden (kræver ingen eksterne biblioteker).
* `streamdeck_case.scad` - Parametrisk OpenSCAD-kildekode, hvis du ønsker at justere mål, vægtykkelser eller tolerancer.

---

## 🖨️ Anbefalede 3D Print Indstillinger

| Indstilling | Anbefaling |
| :--- | :--- |
| **Materiale** | PLA eller PETG (PETG giver ekstra slidstyrke og fleksibilitet ved taster) |
| **Lagtykkelse (Layer Height)** | `0.20 mm` (eller `0.16 mm` for ekstra fine overflader) |
| **Perimeters / Vægge** | `3` til `4` perimetre for maksimal vridningsstabilitet |
| **Top / Bund lag** | `4` eller `5` lag |
| **Infill** | `20%` (Gyroid eller Grid anbefales) |
| **Supports (Understøttelse)** | **Ingen nødvendig!** Begge dele er flade og kan printes direkte på byggepladen uden supports. |

### Orienteringsguide på byggepladen:
* **Top-plade:** Læg den fladt ned på byggepladen. Hvis du vil have en flot tekstureret forside, kan du vende oversiden ned mod en PEI/tekstureret plade.
* **Bund-boks:** Printes stående på sin bund (fladt mod byggepladen).

---

## 🔧 Montering og Samling

1. **MX Taster:** Trykkes ned i de 14.2 x 14.2 mm huller på toppladen, indtil de klikker i lås.
2. **Potentiometre:** Føres op igennem 7.5 mm hullerne fra bagsiden og spændes fast med de medfølgende M7 møtrikker og skiver på oversiden.
3. **OLED Skærm:** Skærmen fastgøres under skærmvinduet (kan holdes fast med en lille dråbe varmelim eller dobbeltsidet monteringstape mod PCB'ens bagside).
4. **Lodning:** Forbind dioder, taster, potentiometre og skærm ifølge [docs/WIRING.md](../docs/WIRING.md).
5. **ESP32:** Placeres i bunden af kabinettet, så USB-porten flugter med udskæringen på bagvæggen.
6. **Samling:** Skru toppladen fast i bundens 4 hjørnetårne med 4 stk. **M3 x 10 mm** eller **M3 x 12 mm** skruer (f.eks. cylindriske eller undersænkede).
