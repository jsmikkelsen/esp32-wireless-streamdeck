#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ==========================================
// KONFIGURATION (Rettes til dit netværk / PC)
// ==========================================
const char* WIFI_SSID     = "DIT_WIFI_NAVN";
const char* WIFI_PASSWORD = "DIT_WIFI_KODE";
const char* PC_HOST       = "192.168.1.100"; // Din PC's lokale IP-adresse
const int   WS_PORT       = 8765;

// ==========================================
// OLED DISPLAY (SSD1306 128x64 I2C)
// ==========================================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ==========================================
// HARDWARE PINS
// ==========================================
// Potentiometre SKAL sidde på ADC1 (GPIO 32-39), da ADC2 deaktiveres ved Wi-Fi brug!
const int POT_PINS[4] = {32, 33, 34, 35};

// 3x4 Switch Matrix (Row-driven LOW, Cols INPUT_PULLUP med dioder)
const int ROW_PINS[3] = {13, 14, 27};
const int COL_PINS[4] = {18, 19, 23, 25};

// ==========================================
// TILSTAND OG VARIABLER
// ==========================================
WebSocketsClient webSocket;
bool wsConnected = false;

// Volumen- og kanaldata (0-100%)
int currentVolume[4] = {50, 50, 50, 50};
int lastFilteredPot[4] = {-1, -1, -1, -1};
float potSmoothed[4] = {50.0, 50.0, 50.0, 50.0};
char channelLabels[4][8] = {"MST", "DIS", "SPT", "APP"};

// Matrix tilstand
bool keyState[3][4] = {false};
unsigned long lastDebounceTime[3][4] = {0};
const unsigned long DEBOUNCE_DELAY = 25; // ms

// ==========================================
// OLED TEGNERUTINE
// ==========================================
void drawDashboard() {
  display.clearDisplay();

  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  for (int i = 0; i < 4; i++) {
    int colWidth = 32;
    int x = i * colWidth;

    // Kanalnavn (f.eks. MST, DIS, SPT, APP)
    display.setCursor(x + 4, 0);
    display.print(channelLabels[i]);

    // Lydstyrke i procent (0-100)
    display.setCursor(x + 4, 11);
    if (currentVolume[i] < 10) {
      display.print(" ");
    }
    display.print(currentVolume[i]);
    display.print("%");

    // Lydsøjle ramme (bredde: 16px, højde: 42px, y: 22 til 63)
    display.drawRect(x + 8, 21, 16, 43, SSD1306_WHITE);

    // Beregn fyldhøjde (0 til 39 pixels indvendigt)
    int fillHeight = map(currentVolume[i], 0, 100, 0, 39);
    fillHeight = constrain(fillHeight, 0, 39);

    if (fillHeight > 0) {
      display.fillRect(x + 10, 21 + (39 - fillHeight) + 2, 12, fillHeight, SSD1306_WHITE);
    }
  }

  // Lille forbindelsesindikator i bunden hvis WebSocket ikke er forbundet
  if (!wsConnected) {
    display.fillRect(0, 62, 128, 2, SSD1306_WHITE);
  }

  display.display();
}

// ==========================================
// WEBSOCKET HÅNDTERING
// ==========================================
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("[WS] Disconnected!");
      wsConnected = false;
      drawDashboard();
      break;

    case WStype_CONNECTED:
      Serial.printf("[WS] Connected to: %s\n", payload);
      wsConnected = true;
      drawDashboard();
      break;

    case WStype_TEXT: {
      StaticJsonDocument<512> doc;
      DeserializationError err = deserializeJson(doc, payload);
      if (!err) {
        // Opdater kanal-volumen sendt fra PC
        if (doc.containsKey("vol") && doc.containsKey("ch")) {
          int ch = doc["ch"];
          int vol = doc["vol"];
          if (ch >= 0 && ch < 4) {
            currentVolume[ch] = constrain(vol, 0, 100);
            drawDashboard();
          }
        }
        // Opdater kanalnavne hvis sendt fra PC
        if (doc.containsKey("labels")) {
          JsonArray labels = doc["labels"].as<JsonArray>();
          for (int i = 0; i < 4 && i < (int)labels.size(); i++) {
            const char* lbl = labels[i];
            strncpy(channelLabels[i], lbl, sizeof(channelLabels[i]) - 1);
            channelLabels[i][sizeof(channelLabels[i]) - 1] = '\0';
          }
          drawDashboard();
        }
      }
      break;
    }

    default:
      break;
  }
}

// ==========================================
// 3x4 MATRIX SCANNER (MED DIODER & DEBOUNCE)
// ==========================================
void scanMatrix() {
  unsigned long now = millis();

  for (int r = 0; r < 3; r++) {
    digitalWrite(ROW_PINS[r], LOW);
    delayMicroseconds(5);

    for (int c = 0; c < 4; c++) {
      bool isReadingLow = (digitalRead(COL_PINS[c]) == LOW);

      if (isReadingLow != keyState[r][c]) {
        if ((now - lastDebounceTime[r][c]) > DEBOUNCE_DELAY) {
          lastDebounceTime[r][c] = now;
          keyState[r][c] = isReadingLow;

          int keyNum = (r * 4) + c + 1;

          StaticJsonDocument<128> doc;
          doc["type"] = "key";
          doc["key"] = keyNum;
          doc["state"] = isReadingLow ? "down" : "up";

          String jsonStr;
          serializeJson(doc, jsonStr);

          if (wsConnected) {
            webSocket.sendTXT(jsonStr);
          }
          Serial.printf("Key %d: %s\n", keyNum, isReadingLow ? "PRESSED" : "RELEASED");
        }
      }
    }

    digitalWrite(ROW_PINS[r], HIGH);
  }
}

// ==========================================
// POTENTIOMETER FILTER & AFLÆSNING
// ==========================================
void readPotentiometers() {
  static unsigned long lastCheck = 0;
  if (millis() - lastCheck < 30) return;
  lastCheck = millis();

  for (int i = 0; i < 4; i++) {
    int raw = analogRead(POT_PINS[i]);

    // Exponential moving average filter (EMA)
    potSmoothed[i] = (0.25f * raw) + (0.75f * potSmoothed[i]);

    int val = map((int)potSmoothed[i], 20, 4075, 0, 100);
    val = constrain(val, 0, 100);

    if (abs(val - lastFilteredPot[i]) >= 2) {
      lastFilteredPot[i] = val;
      currentVolume[i] = val;

      StaticJsonDocument<128> doc;
      doc["type"] = "pot";
      doc["pot"] = i;
      doc["val"] = val;

      String jsonStr;
      serializeJson(doc, jsonStr);

      if (wsConnected) {
        webSocket.sendTXT(jsonStr);
      }

      drawDashboard();
    }
  }
}

// ==========================================
// SETUP
// ==========================================
void setup() {
  Serial.begin(115200);

  Wire.begin(21, 22);
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("SSD1306 init failed!");
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(10, 15);
  display.println("ESP32 StreamDeck");
  display.setCursor(10, 35);
  display.println("Connecting WiFi...");
  display.display();

  for (int r = 0; r < 3; r++) {
    pinMode(ROW_PINS[r], OUTPUT);
    digitalWrite(ROW_PINS[r], HIGH);
  }
  for (int c = 0; c < 4; c++) {
    pinMode(COL_PINS[c], INPUT_PULLUP);
  }

  for (int i = 0; i < 4; i++) {
    pinMode(POT_PINS[i], INPUT);
    int initialRaw = analogRead(POT_PINS[i]);
    potSmoothed[i] = initialRaw;
    int initialVal = map(initialRaw, 20, 4075, 0, 100);
    initialVal = constrain(initialVal, 0, 100);
    lastFilteredPot[i] = initialVal;
    currentVolume[i] = initialVal;
  }

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(300);
    attempts++;
  }

  display.clearDisplay();
  display.setCursor(10, 20);
  if (WiFi.status() == WL_CONNECTED) {
    display.println("WiFi OK!");
    display.setCursor(10, 35);
    display.print("IP: ");
    display.println(WiFi.localIP());
  } else {
    display.println("WiFi Failed!");
    display.setCursor(10, 35);
    display.println("Check SSID/Pass");
  }
  display.display();
  delay(1000);

  webSocket.begin(PC_HOST, WS_PORT, "/");
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(3000);

  drawDashboard();
}

void loop() {
  webSocket.loop();
  scanMatrix();
  readPotentiometers();
}
