#include <WiFi.h>

const char* ssid = "linksys";
const char* password = ""; // Upewnij się, że sieć jest otwarta, jeśli hasło jest puste

// Adres komputera/serwera, który odbierze dane
const char* host = "192.168.1.13"; 
const uint16_t port = 12345;

WiFiClient client;

void activateDevice() {
  Serial.println("= URZĄDZENIE AKTYWOWANE (Start) =");
  pinMode(2, OUTPUT);
  digitalWrite(2, HIGH); // Dioda ON
  delay(200);
  digitalWrite(2, LOW);  // Dioda OFF
  
}

//  funkcja realizująca koniec pracy (pkt a - wyłączenie)
void deactivateDevice() {
  Serial.println("\n= DEAKTYWACJA URZĄDZENIA =");
  if (client.connected()) client.stop(); // Zamknij połączenie TCP
  WiFi.disconnect(true);  // Rozłącz WiFi 
  WiFi.mode(WIFI_OFF);    // Wyłącz moduł WiFi całkowicie
  Serial.println("WiFi wyłączone. Program zakończony.");
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // 1. Aktywacja (pkt a)
  activateDevice();
  
  // 2. Uruchomienie WiFi (pkt b)
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);

  Serial.printf("Próba połączenia z siecią: %s\n", ssid);
  
  // 3. Połączenie z WiFi (pkt c)
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(" POŁĄCZONO Z WIFI!");
    Serial.print("Adres IP ESP32: ");
    Serial.println(WiFi.localIP());

    // 4. Przesłanie danych (pkt d) 
    Serial.printf("\nŁączenie z serwerem danych %s:%d ...\n", host, port);
    
    if (client.connect(host, port)) {
      Serial.println(" Połączono z serwerem! Wysyłanie danych...");
      
      // Wysyłamy przykładowe dane
      client.println("Witaj!"); 
      client.printf("Mój sygnał RSSI: %d dBm\n", WiFi.RSSI());
      client.println("Koniec transmisji.");
      
      // Czekamy chwilę  odpowiedź 
      delay(100); 
      
    } else {
      Serial.println(" Nie można połączyć z serwerem docelowym.");
    }

  } else {
    Serial.println(" Nie udało się połączyć");
  }

  // 5. Wyłączenie (pkt a - część druga)
  deactivateDevice();
}

void loop() {
  delay(1000);
}