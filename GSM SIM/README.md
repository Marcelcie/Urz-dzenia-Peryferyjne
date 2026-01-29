# 📲 Obsługa Modułu GSM (SIM800/SIM900)

Projekt realizujący komunikację z siecią komórkową przy użyciu modułu GSM (np. SIM800L) oraz mikrokontrolera. Głównym celem jest obsługa wiadomości SMS oraz sterowanie modemem za pomocą komend AT.

---

## ⚙️ Główne funkcjonalności

Aplikacja umożliwia interakcję z modułem GSM poprzez interfejs szeregowy (UART).

### 1. ⌨️ Obsługa Komend AT (Hayes)
* Implementacja terminala do ręcznego wysyłania komend AT.
* Diagnostyka modułu:
    * Sprawdzanie statusu logowania do sieci (`AT+CREG?`).
    * Odczyt poziomu sygnału RSSI (`AT+CSQ`).
    * Sprawdzanie operatora (`AT+COPS?`).

### 2. 📩 Obsługa Wiadomości SMS
* **Wysyłanie SMS:** Konfiguracja modułu w tryb tekstowy (`AT+CMGF=1`) i wysyłanie wiadomości na zdefiniowany numer.
* **Odbieranie SMS:** Odczyt przychodzących wiadomości z bufora karty SIM, parsowanie treści i wyświetlanie ich na konsoli szeregowej.

### 3. 🔌 Komunikacja UART
* Wykorzystanie interfejsu UART do komunikacji między mikrokontrolerem (ESP32) a modułem GSM.
* Obsługa pinów RX/TX z uwzględnieniem konwersji poziomów logicznych (jeśli wymagana).

---

## 🛠️ Sprzęt i Połączenie

### Wymagane elementy:
* **Moduł GSM:** SIM800L / SIM900 / A6.
* **Karta SIM:** Aktywna karta SIM (bez blokady PIN, z obsługą 2G).
* **Zasilanie:** Zewnętrzne źródło zasilania (moduły GSM wymagają wysokiego prądu szczytowego, często >2A, samo zasilanie z USB może być niewystarczające).

### Przykładowy schemat połączeń (ESP32 <-> SIM800L):
| ESP32 | SIM800L | Uwagi |
| :--- | :--- | :--- |
| RX (GPIO 16) | TX | |
| TX (GPIO 17) | RX | Może wymagać dzielnika napięcia |
| GND | GND | Wspólna masa jest kluczowa |
| - | VCC | Zewnętrzne zasilanie (3.7V - 4.2V) |

---

## 🚀 Instrukcja Uruchomienia

1. Włóż kartę SIM do modułu.
2. Podłącz układ zgodnie ze schematem (pamiętaj o wspólnym GND!).
3. Wgraj kod na mikrokontroler
