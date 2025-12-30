# Systemy Nawigacji Satelitarnej (GPS) - NMEA Decoder 🛰️

Projekt realizowany w ramach przedmiotu Urządzenia Peryferyjne (Laboratorium 3).
Aplikacja okienkowa (GUI) służąca do obsługi modułów GPS, dekodowania ramek NMEA 0183 oraz wizualizacji pozycji na mapach.

---

📋 Opis Projektu

Program łączy się z odbiornikiem GPS poprzez port szeregowy (Bluetooth SPP lub USB), pobiera surowy strumień danych i przetwarza go w czasie rzeczywistym. Aplikacja została wyposażona w **tryb symulacji**, co pozwala na testowanie funkcjonalności bez fizycznego dostępu do sprzętu.

 Główne funkcjonalności:
* **Transmisja danych:** Obsługa portów COM (biblioteka `pyserial`) z wykorzystaniem wielowątkowości (brak "zamrażania" GUI).
* **Parser NMEA:** Filtrowanie i dekodowanie ramek `$GPGGA` (Global Positioning System Fix Data).
* **Konwersja współrzędnych:** Przeliczanie formatu NMEA (`DDMM.MMMM`) na stopnie dziesiętne (`DD.DDDD`) wymagane przez API mapowe.
* **Wizualizacja:** Dynamiczne generowanie linków do Google Maps wskazujących dokładną pozycję.
* **GUI:** Czytelny interfejs użytkownika wyświetlający czas UTC, liczbę satelitów, wysokość n.p.m. oraz współrzędne.

---

## 🛠️ Technologie

* **Język:** Python 3.13
* **GUI:** Tkinter (wbudowany)
* **Komunikacja:** `pyserial`
* **Wątkowość:** `threading`

---

## ⚙️ Instalacja i Uruchomienie

1.  **Sklonuj repozytorium:**
    ```bash
    git clone [https://github.com/TWOJ_NICK/UrzadzeniaPeryferyjne.git](https://github.com/TWOJ_NICK/UrzadzeniaPeryferyjne.git)
    ```

2.  **Zainstaluj wymagane biblioteki:**
    Projekt wymaga biblioteki do obsługi portów szeregowych.
    ```bash
    pip install pyserial
    ```

3.  **Uruchom program:**
    ```bash
    python GPS.py
    ```

---

## 📖 Instrukcja Obsługi

### Tryb Symulacji (Domyślny)
Idealny do sprawdzenia działania aplikacji bez sprzętu.
1.  Uruchom program.
2.  Upewnij się, że checkbox **"Tryb Symulacji"** jest zaznaczony.
3.  Kliknij **POŁĄCZ**.
4.  Program zacznie generować przykładową trasę. Kliknij **"Otwórz pozycję w Google Maps"**, aby zobaczyć lokalizację.

### Tryb Rzeczywisty (Z modułem GPS)
1.  Sparuj moduł GPS z komputerem (np. przez Bluetooth).
2.  Sprawdź numer portu w Menedżerze Urządzeń (np. `COM3`).
3.  W programie **odznacz** "Tryb Symulacji".
4.  Wpisz poprawny port i kliknij **POŁĄCZ**.

---

## 📂 Struktura Projektu

* `GPS.py` - Główny kod aplikacji.

---

## 👥 Autor

* **Marcel Cieśliński** (280871)

Politechnika Wrocławska, Wydział Informatyki i Telekomunikacji.
