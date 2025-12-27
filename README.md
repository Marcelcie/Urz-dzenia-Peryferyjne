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
Aplikacja desktopowa napisana w języku Python, służąca do zaawansowanej obsługi kamer USB. Program umożliwia podgląd na żywo, nagrywanie wideo, wykonywanie zdjęć oraz realizację techniki **HDR (High Dynamic Range)** poprzez łączenie klatek o różnych ekspozycjach.

## 🚀 Możliwości programu

* **Podgląd na żywo** z nakładką OSD (On-Screen Display) informującą o parametrach.
* **Zapis zdjęć** (Snapshot) w formacie PNG.
* **Nagrywanie wideo** w formacie AVI (kodek MJPG).
* **Tryb HDR:** Automatyczne wykonanie serii zdjęć z różną ekspozycją (-7.0, -5.0, -3.0 EV), scalenie ich algorytmem Debevec i mapowanie tonów (Tone Mapping).
* **Zmiana rozdzielczości** w locie (cykliczne przełączanie między 480p, 600p, 720p, 1080p).
* **Sterowanie jasnością** obrazu.
* **Powiadomienia ekranowe** potwierdzające wykonanie akcji (np. "Zapisano HDR").

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
