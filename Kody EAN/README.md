# 📷 Obsługa Kamer Cyfrowych i Algorytmy HDR

Aplikacja desktopowa napisana w języku **Python**, służąca do zaawansowanej obsługi kamer USB. Projekt realizuje podgląd na żywo, rejestrację materiałów wideo oraz cyfrowe przetwarzanie obrazu, ze szczególnym naciskiem na techniki **High Dynamic Range (HDR)**.

---

## ⚙️ Główne funkcjonalności

System oferuje szereg narzędzi do analizy i akwizycji obrazu w czasie rzeczywistym.

### 1. 🎨 Algorytm HDR (High Dynamic Range)
Implementacja techniki zwiększania rozpiętości tonalnej obrazu:
* **Sekwencyjne pobieranie klatek:** Automatyczne przejmowanie klatek z różnymi parametrami ekspozycji.
* **Scalanie obrazów:** Wykorzystanie **metody Debeveca** do łączenia klatek w jeden obraz o wysokiej dynamice.
* **Tone Mapping:** Mapowanie tonów w celu poprawnego wyświetlenia obrazu HDR na standardowych monitorach.

### 2. 🎥 Rejestracja Multimediów
* **Wideo:** Zapis strumienia wideo do formatu `.avi` z wykorzystaniem kodeka **MJPG**.
* **Zdjęcia:** Wykonywanie zrzutów pojedynczych klatek (snapshots) do formatu `.png`.
* **Bezpieczeństwo zapisu:** Zaimplementowano system zapobiegający uszkodzeniu plików wideo w przypadku nagłej zmiany parametrów strumienia lub przerwania pracy.

### 3. 🖥️ Interfejs i Konfiguracja (OSD)
* **On-Screen Display (OSD):** Wyświetlanie kluczowych parametrów bezpośrednio na obrazie wideo (liczba klatek na sekundę - FPS, aktualna rozdzielczość, powiadomienia systemowe).
* **Dynamiczna konfiguracja:** Możliwość zmiany rozdzielczości kamery oraz sterowania jasnością sensora w czasie rzeczywistym, bez konieczności restartowania aplikacji.

---

## 🛠️ Technologie i Wymagania

Projekt wymaga zainstalowanego interpretera **Python 3**.

### Biblioteki:
Podstawą działania są biblioteki do obliczeń numerycznych i przetwarzania obrazu:
* **OpenCV (`cv2`)**: Obsługa strumienia wideo, operacje na macierzach obrazu, algorytmy HDR.
* **NumPy**: Operacje macierzowe niezbędne do szybkiego przetwarzania pikseli.

### Instalacja zależności:
Aby uruchomić projekt, zainstaluj wymagane pakiety komendą:
```bash
pip install opencv-python numpy
