# 🛠️ Urządzenia Peryferyjne - Laboratorium

Repozytorium zawiera projekty i sprawozdania realizowane w ramach kursu **Urządzenia Peryferyjne** na Politechnice Wrocławskiej.

**Autor:**
* Marcel Cieśliński

---

## 📂 Zawartość Repozytorium

### 1. 🛰️ Symulator GPS (Python)
Aplikacja desktopowa napisana w języku **Python** (biblioteka Tkinter), służąca do symulacji i analizy danych GPS w formacie NMEA.

**Główne funkcjonalności:**
* **Parsowanie ramek NMEA:** Odczyt i interpretacja ramek `$GPGGA` z pliku tekstowego.
* **Geolokalizacja:** Wyświetlanie współrzędnych (szerokość/długość) oraz wizualizacja pozycji na Mapach Google (integracja z przeglądarką).
* **Obsługa czasu:** Automatyczne wyliczanie strefy czasowej na podstawie długości geograficznej i konwersja czasu UTC na lokalny.
* **Symulacja wysokości:** Poprawna interpretacja danych wysokościowych (np. dla Szklarskiej Poręby ~689 m n.p.m.).

**Technologie:** `Python`, `Tkinter`, `webbrowser`, `threading`.

---

### 2. 📶 Transmisja WiFi ESP32 (FreeRTOS + UDP)
Projekt oprogramowania dla układu SoC **ESP32**, realizujący bezprzewodową akwizycję danych środowiskowych w systemie czasu rzeczywistego.

**Główne funkcjonalności:**
* **System operacyjny:** Wykorzystanie **FreeRTOS** do zarządzania zadaniami.
* **Architektura wielowątkowa:**
    * `TaskAcquisition`: Odczyt danych z czujnika DHT11.
    * `TaskProcessing`: Przetwarzanie danych, dodawanie timestampu i ID pakietu.
    * `TaskTransmission`: Wysyłanie sformatowanych ramek przez WiFi.
* **Komunikacja:** Protokół **UDP** (User Datagram Protocol) na porcie 4210.
* **Kolejki (Queues):** Bezpieczna wymiana danych między wątkami.

**Technologie:** `C++`, `Arduino IDE`, `FreeRTOS`, `WiFi.h`, `WiFiUdp.h`.

---

### 3. 📷 Kamerki Cyfrowe
Aplikacja desktopowa do zaawansowanej obsługi kamer USB, realizująca podgląd na żywo, rejestrację materiałów oraz cyfrowe przetwarzanie obrazu (High Dynamic Range).

Główne funkcjonalności:

* **Algorytm HDR (High Dynamic Range):** Implementacja sekwencyjnego pobierania klatek z różną ekspozycją, scalania ich (metoda Debeveca) oraz mapowania tonów (Tone Mapping).
* **Rejestracja multimediów:** Zapis strumienia wideo (format AVI, kodek MJPG) oraz wykonywanie zrzutów pojedynczych klatek (PNG).
* **Dynamiczna konfiguracja:** Możliwość zmiany rozdzielczości i sterowania jasnością sensora w czasie rzeczywistym bez przerywania pracy programu.
* **Interfejs OSD (On-Screen Display):** Wyświetlanie kluczowych parametrów (FPS, aktualna rozdzielczość, powiadomienia) bezpośrednio na obrazie wideo.
* **Bezpieczeństwo zapisu:** System zapobiegający uszkodzeniu plików wideo przy nagłej zmianie parametrów strumienia.
* **Technologie:** Python, OpenCV (cv2), NumPy.

## 🛠️ Wymagania i Instalacja

Projekt wymaga zainstalowanego interpretera Python 3 oraz bibliotek `opencv-python` i `numpy`.

### Instalacja zależności:
```bash
pip install opencv-python numpy

## 🚀 Jak uruchomić projekty?

### Symulator GPS:
1. Przejdź do folderu `GPS`.
2. Upewnij się, że masz zainstalowanego Pythona.
3. Uruchom plik główny:
   ```bash
   python np. gps.py
