===================================================================
PROJEKT: Komunikacja z Modułem GSM/SIM (Smart Card)
AUTORZY: Marcel Cieśliński, Mateusz Bonifatiuk
DATA KOMPILACJI: 5 Listopada 2025
===================================================================

1. CEL PROJEKTU
Program jest konsolową aplikacją C++, której celem jest ustanowienie połączenia z modułem GSM/SIM lub czytnikiem kart Smart Card (interfejs PC/SC) oraz odczytanie podstawowych informacji (np. ATR).

2. ZAWARTOŚĆ FOLDERU
Ten folder zawiera skompilowany plik wykonywalny, pliki źródłowe oraz dokumentację.

   - GSM SIM Bonifatiuk Cieslinski.exe:  Gotowy program do uruchomienia (Kompilacja Release).
   - GSM SIM Bonifatiuk Cieslinski.sln, .cpp, .vcxproj: Pliki źródłowe i projektowe.
   - [Nazwa Pliku Sprawozdania.pdf]: Sprawozdanie z ćwiczenia.
   - [Inne Pliki .lib/.dll]: Wszelkie biblioteki zewnętrzne potrzebne do komunikacji.

3. KWESTIE TECHNICZNE (Kluczowe dla Uruchomienia)

A. Problem Zależności (Rozwiązany)
   - Program został skompilowany z użyciem statycznego linkowania (opcja /MT) w Visual Studio, co eliminuje błąd braku pliku msvcp140.dll na komputerze docelowym.

B. Błąd NATYCHMIASTOWEGO ZAMYKANIA SIĘ PROGRAMU (Awaria Sprzętowa)
   - Jeśli program uruchamia się i od razu gaśnie, oznacza to, że nie może nawiązać połączenia ze sprzętem GSM/SIM lub czytnikiem Smart Card, co powoduje awarię funkcji API.

4. INSTRUKCJA URUCHOMIENIA I WERYFIKACJA

Aby program zadziałał poprawnie, prosimy o zweryfikowanie następujących punktów:

1. URZĄDZENIE: Upewnij się, że moduł GSM/SIM lub czytnik Smart Card jest poprawnie podłączony i zainstalowany (sterowniki).
2. USŁUGA: Upewnij się, że usługa Windows "Smart Card Service" jest aktywna.
3. PORT COM: W przypadku połączenia przez port szeregowy, proszę sprawdzić w Menedżerze urządzeń (Device Manager), pod jakim numerem portu (np. COM3, COM7) widoczny jest moduł GSM/SIM.

   - Jeśli numer portu jest inny niż ustawiony domyślnie w kodzie, konieczna jest zmiana numeru w pliku źródłowym (\[Nazwa\_Pliku].cpp) i ponowna kompilacja projektu w Visual Studio.

Dziękujemy.