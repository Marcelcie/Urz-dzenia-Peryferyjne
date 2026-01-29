# 📡 System Akwizycji Danych (ESP32 + FreeRTOS)

Projekt oprogramowania dla układu SoC **ESP32**, realizujący bezprzewodową akwizycję danych środowiskowych w systemie czasu rzeczywistego z wykorzystaniem wielowątkowości.

---

## ⚙️ Główne funkcjonalności

System opiera się na **FreeRTOS**, co pozwala na równoległe wykonywanie zadań bez blokowania procesora.

### 1. Architektura Wielowątkowa (Tasks)
Program został podzielony na trzy niezależne wątki:
* **`TaskAcquisition`**: Odpowiada za fizyczny odczyt danych z czujnika (np. DHT11 - temperatura/wilgotność).
* **`TaskProcessing`**: Przetwarza surowe dane, dodaje do nich znacznik czasu (timestamp) oraz unikalne ID pakietu.
* **`TaskTransmission`**: Odpowiada za wysłanie gotowej ramki danych przez sieć WiFi.

### 2. Komunikacja i Bezpieczeństwo
* **Protokół:** Transmisja odbywa się po protokole **UDP** (User Datagram Protocol).
* **Port:** Domyślny port nasłuchu/wysyłania to `4210`.
* **Synchronizacja:** Wykorzystanie **Kolejek (Queues)** do bezpiecznej wymiany danych między wątkami (zapobiega to wyścigom danych i kolizjom).

---

## 🛠️ Technologie i Wymagania

### Sprzęt:
* Mikrokontroler **ESP32** (dowolna płytka rozwojowa, np. ESP32 DevKit V1).
* Czujnik środowiskowy (np. **DHT11** / DHT22).

### Software:
* **Środowisko:** Arduino IDE / PlatformIO.
* **Język:** C++.
* **Biblioteki:**
    * `WiFi.h`
    * `WiFiUdp.h`
    * `FreeRTOS` (wbudowany w framework ESP32)

---

## 🚀 Konfiguracja i Uruchomienie

1. Otwórz projekt w Arduino IDE.
2. Skonfiguruj dane sieci WiFi w kodzie źródłowym:
   ```cpp
   const char* ssid = "TWOJA_NAZWA_SIECI";
   const char* password = "TWOJE_HASLO";