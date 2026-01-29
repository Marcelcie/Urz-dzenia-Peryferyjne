// Listing 1: Kod programu dla ESP32 (FreeRTOS + WiFi)
#include <WiFi.h>
#include <DHT.h>

const char* ssid = "";
const char* password = "";           
const char* host = ""; // IP telefonu
const uint16_t port = 8080;

#define DHTPIN 13 
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

struct SensorData { float temperature; float humidity; };
QueueHandle_t queueRawData;
QueueHandle_t queueFormatted;

void taskAcquisition(void *pvParameters) {
  SensorData data;
  for(;;) {
    data.temperature = dht.readTemperature();
    data.humidity = dht.readHumidity();
    if (!isnan(data.temperature)) xQueueSend(queueRawData, &data, pdMS_TO_TICKS(10));
    vTaskDelay(2000 / portTICK_PERIOD_MS);
  }
}

void taskProcessing(void *pvParameters) {
  SensorData receivedData;
  char messageBuffer[128];
  for(;;) {
    if (xQueueReceive(queueRawData, &receivedData, portMAX_DELAY) == pdPASS) {
      snprintf(messageBuffer, sizeof(messageBuffer), "[%lu ms] Temp: %.1f C", millis(), receivedData.temperature);
      xQueueSend(queueFormatted, &messageBuffer, pdMS_TO_TICKS(10));
    }
  }
}

void taskTransmission(void *pvParameters) {
  char textToSend[128];
  WiFiClient client;
  for(;;) {
    if (xQueueReceive(queueFormatted, &textToSend, portMAX_DELAY) == pdPASS) {
      if (client.connect(host, port)) {
        client.println(textToSend);
        client.stop();
      }
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  WiFi.begin(ssid, password);
  queueRawData = xQueueCreate(10, sizeof(SensorData));
  queueFormatted = xQueueCreate(10, sizeof(char) * 128);
  xTaskCreate(taskAcquisition, "Akwizycja", 4096, NULL, 1, NULL);
  xTaskCreate(taskProcessing, "Przetwarzanie", 4096, NULL, 2, NULL);
  xTaskCreate(taskTransmission, "Transmisja", 4096, NULL, 3, NULL);
}
void loop() { vTaskDelete(NULL); }
