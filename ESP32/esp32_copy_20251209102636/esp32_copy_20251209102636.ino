#include <WiFi.h>
#include <WiFiUdp.h>
#include <DHT.h>

#define DHTPIN 23
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

String data = "";
float h, t;
// ------------------ WiFi settings ------------------
const char* ssid = "linksys";
const char* pass = ""; // jeśli brak hasła – OK

WiFiUDP udp;
const unsigned int udpPort = 4210;
const char* broadcastIP = "192.168.1.20";

// ------------------ Device flag --------------------
bool deviceOn = false;

// ------------------ FreeRTOS QUEUES ----------------
QueueHandle_t qRaw; // kolejka dla danych surowych
QueueHandle_t qProcessed; // kolejka dla danych przetworzonych

// ------------------ Structures ---------------------
typedef struct {
  int randomValue; // symulacja pomiaru
} RawData;

typedef struct {
  int randomValue;
  unsigned long timestamp;
  int id;
} ProcessedData;

// ------------------- Device Control ----------------
void deviceStart() {
  deviceOn = true;
  Serial.println("Urzadzenie wlaczone");
}

void deviceStop() {
  deviceOn = false;
  Serial.println("Urzadzenie wylaczone");
}

// ------------------- WiFi connect ------------------
void connectWiFi() {
  Serial.print("Laczenie z WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, pass);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(1000);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("\nPolaczono z WiFi\nAdres IP ESP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Nie udalo sie polaczyc z WiFi");
  }
}

// ------------------- UDP sending -------------------
void sendUDP(const String& data) {
  if (deviceOn && WiFi.status() == WL_CONNECTED) {
    udp.beginPacket(broadcastIP, udpPort);
    udp.print(data);
    udp.endPacket();

    Serial.print("Wyslano dane: ");
    Serial.println(data);
  } else {
    Serial.println("Nie mozna wyslac danych");
  }
}

// ===================================================
// TASK 1 — AKWIZYCJA
// ===================================================
void taskAcquisition(void *pv) {
  RawData raw;

  for (;;) {
    raw.randomValue = random(0, 100); // symulacja pomiaru

    xQueueSend(qRaw, &raw, portMAX_DELAY);

    Serial.println("Task 1 → surowe dane zapisane");
    vTaskDelay(pdMS_TO_TICKS(2000));
  }
}

// ===================================================
// TASK 2 — PRZETWARZANIE
// ===================================================
void taskProcessing(void *pv) {
  RawData raw;
  ProcessedData proc;
  int counter = 0;

  for (;;) {

    if (xQueueReceive(qRaw, &raw, portMAX_DELAY)) {

      proc.randomValue = raw.randomValue;
      proc.timestamp = millis();
      proc.id = counter++;

      xQueueSend(qProcessed, &proc, portMAX_DELAY);

      Serial.println("Task 2 → dane przetworzone");
    }
  }
}

// ===================================================
// TASK 3 — TRANSMISJA UDP
// ===================================================
void taskTransmission(void *pv) {
  ProcessedData d;
  char buffer[128];

  for (;;) {

    if (xQueueReceive(qProcessed, &d, portMAX_DELAY)) {

      sprintf(buffer,
        "Humidity: %f\nTemperature: %f\n", h, t
      );

      sendUDP(buffer);

      Serial.println("Task 3 → wyslano UDP");
    }
  }
}

// ===================================================
// SETUP
// ===================================================
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("Start programu");

  dht.begin();
  deviceStart();
  connectWiFi();

  udp.begin(udpPort);
  Serial.println("UDP socket started");

  // --- kolejki FreeRTOS ---
  qRaw = xQueueCreate(10, sizeof(RawData));
  qProcessed = xQueueCreate(10, sizeof(ProcessedData));

  // --- trzy zadania ---
  xTaskCreate(taskAcquisition, "Acq", 4096, NULL, 1, NULL);
  xTaskCreate(taskProcessing, "Proc", 4096, NULL, 1, NULL);
  xTaskCreate(taskTransmission, "Send", 4096, NULL, 1, NULL);
}

void loop() {
  h = dht.readHumidity();
  t = dht.readTemperature();
  delay(2000);
  //data = "Humidity: " + h + "\nTemperature: " + t + "\n";
}

