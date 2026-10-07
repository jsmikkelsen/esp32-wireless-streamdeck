# 3D Print Ergonomisk Kabinet (Wedge Enclosure)

Denne mappe indeholder de færdige 3D-filer samt kildekoden til det vinklede skrivebordskabinet til **ESP32 Wireless Stream Deck & Audio Mixer**.

Designet er udformet som en klassisk ergonomisk **wedge/kile** med en hældningsvinkel på ca. **22 grader** mod brugeren, præcis som professionelle Stream Decks og macropads:

* **Ergonomisk vinkel:** Lav forkant (**18 mm**) for behagelig håndstilling og høj bagkant (**50 mm**) for optimal synsvinkel til OLED-displayet og tasterne.
* **Planforsænket topplade:** Toppladen med taster og potentiometre hviler på en 3 mm forsænket indvendig hylde med en flot omkransende kant.
* **Layout (venstre):** 12x Cherry MX switches i 4x3 matrix (14.2 mm snap-fit huller med standard 19.05 mm pitch).
* **Layout (højre):**
  * **Øverst:** 2x Potentiometre (Master & Discord) med 7.5 mm huller.
  * **Midt:** 1x 0.96" SSD1306 OLED-display (26 x 14 mm vindue).
  * **Nederst:** 2x Potentiometre (Spotify & Browser/App) med 7.5 mm huller.
* **Bagvæg:** 14.0 x 8.0 mm USB-port udskæring til strømforsyning af ESP32'eren.

---

## 📦 Filer i mappen

* `streamdeck_top_plate.stl` - Færdig, lukket (manifold) STL til toppladen.
* `streamdeck_bottom_case.stl` - Færdig, lukket (manifold) STL til det vinklede wedge-kabinet med USB-port og indvendig hylde.
* `generate_case.py` - Python-script der genererer de to 100% vandtætte/manifold STL-filer fra bunden (kræver ingen eksterne biblioteker).
* `streamdeck_case.scad` - Parametrisk OpenSCAD-kildekode til justering af vinkel, dimensioner eller tolerancer.

---

## 🖨️ Anbefalede 3D Print Indstillinger

| Indstilling | Anbefaling |
| :--- | :--- |
| **Materiale** | PLA eller PETG |
| **Lagtykkelse (Layer Height)** | `0.20 mm` |
| **Perimeters / Vægge** | `3` til `4` perimetre for maksimal styrke |
| **Top / Bund lag** | `4` eller `5` lag |
| **Infill** | `20%` (Gyroid eller Grid) |
| **Supports (Understøttelse)** | **Ingen nødvendig!** Begge dele er designet til at printe helt uden supports. |

### Orienteringsguide på byggepladen:
* **Top-plade (`streamdeck_top_plate.stl`):** Lægges fladt ned på byggepladen.
* **Bund-kabinet (`streamdeck_bottom_case.stl`):** Printes stående fladt på bunden. Da alle yder- og indervægge er lodrette og overkanten blot skråner 22°, kræves der **ingen support-materiale overhovedet**.

---

## 🔧 Montering og Samling

1. **MX Taster:** Trykkes i toppladen fra oversiden (klikker fast i 14.2 x 14.2 mm åbningerne).
2. **Potentiometre:** Føres op igennem 7.5 mm hullerne fra bagsiden og spændes fast med de medfølgende M7 møtrikker og skiver.
3. **OLED Skærm:** Monteres under displayvinduet med en lille dråbe varmelim eller dobbeltsidet tape mod skærmens PCB-ramme.
4. **Lodning:** Følg kablingen i [docs/WIRING.md](../docs/WIRING.md) (diodekatode mod rækker, potentiometre til ADC1 GPIO 32-35).
5. **ESP32:** Lægges i bunden af kabinettet, så USB-porten peger ud gennem åbningen på bagvæggen.
6. **Samling:** Toppladen lægges ned på den indvendige hylde i kabinettet og fastgøres med 4 stk. **M3 skruer** i hjørnerne.
