# ⚡ ESP32 - Podstawy i Konfiguracja

Katalog zawiera zbiór kodów źródłowych i ćwiczeń wstępnych, mających na celu zapoznanie się z architekturą mikrokontrolera **ESP32**, obsługą podstawowych peryferiów (GPIO) oraz konfiguracją środowiska.

---

## 📂 Zakres realizowanych zadań

Projekty w tym folderze obejmują następujące zagadnienia:

### 1. 🚦 Obsługa GPIO (General Purpose Input/Output)
* Sterowanie wyjściami cyfrowymi (sterowanie diodami LED).
* Odczyt stanów wejściowych (obsługa przycisków fizycznych).
* Eliminacja drgań styków (debouncing).

### 2. 🎛️ Sygnały i Przetworniki
* **ADC (Analog-to-Digital Converter):** Odczyt wartości z czujników analogowych (np. potencjometr, fotorezystor).
* **PWM (Pulse Width Modulation):** Generowanie sygnału PWM (przy użyciu sterownika `ledc`) do płynnej regulacji jasności diody.

### 3. 📡 Podstawy WiFi
* Skanowanie dostępnych sieci bezprzewodowych w otoczeniu.
* Nawiązywanie prostego połączenia z punktem dostępowym (Access Point).
* Odczyt siły sygnału (RSSI).

---

## 🛠️ Środowisko i Sprzęt

### Wymagania sprzętowe:
* Płytka rozwojowa: **ESP32 DevKit V1** (lub odpowiednik).
* Elementy pasywne: Diody LED, rezystory (220Ω, 10kΩ), przyciski tact-switch, płytka stykowa.

### Konfiguracja Arduino IDE:
Aby poprawnie skompilować kod, należy w Menedżerze Płytek zainstalować **esp32 by Espressif Systems**.

---

## 🚀 Jak uruchomić przykłady?

1. Otwórz wybrany plik `.ino` w Arduino IDE.
2. Wybierz odpowiedni model płytki: `Tools` -> `Board` -> `DOIT ESP32 DEVKIT V1`.
3. Ustaw prędkość portu szeregowego na **115200 bodów**.
4. Skompiluj i wgraj program na mikrokontroler.
