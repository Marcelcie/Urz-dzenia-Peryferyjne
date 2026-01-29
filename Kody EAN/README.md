README.txt (INSTRUKCJA GENERATORA EAN-13)

```
===================================================================
PROJEKT: Generator Kodów Kreskowych EAN-13 (Zadanie Laboratoryjne)
AUTORZY: Marcel Cieśliński, Mateusz Bonifatiuk
JĘZYK: Python
===================================================================

1. CEL PROGRAMU
Program generuje kod kreskowy w standardzie EAN-13 (European Article Numbering) na podstawie 12 lub 13 cyfr wejściowych.

2. WYMAGANIA I TECHNOLOGIA
- Program został skompilowany do pliku EXE za pomocą narzędzia PyInstaller, dzięki czemu działa na systemie Windows bez konieczności instalowania środowiska Python.
- Rysowanie graficznej symboliki kodu (pasków i cyfr) odbywa się przy użyciu biblioteki Pillow (PIL).

3. SPOSÓB URUCHOMIENIA
Uruchom plik: ean13_generator.exe

   - Aplikacja poprosi o podanie 12 lub 13 cyfr.
   - Dla 12 cyfr: Program automatycznie obliczy i wyświetli cyfrę kontrolną (metoda modulo 10) i wygeneruje kod PNG.
   - Dla 13 cyfr: Program zweryfikuje poprawność cyfry kontrolnej przed wygenerowaniem kodu.

4. WYNIK DZIAŁANIA
Wygenerowany obraz kodu EAN-13 (np. ean13_5901234567893.png) jest zapisywany w tym samym katalogu, z którego uruchomiono program.

   - Program odwzorowuje kluczowe elementy normy EAN, w tym wydłużone linie startu/środka/stopu oraz prawidłowy układ bitowy (zestawy A, B, C).

Dziękujemy.
```
