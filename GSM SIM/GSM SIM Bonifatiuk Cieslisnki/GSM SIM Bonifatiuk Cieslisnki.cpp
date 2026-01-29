#include <windows.h>
#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <sstream>
#include <cwchar>
#include <limits>
#include <winscard.h>
#include <algorithm>
#pragma comment(lib, "Winscard.lib")

// HEX print
static void printHex(const BYTE* buf, DWORD len) {
    for (DWORD i = 0; i < len; ++i)
        std::cout << std::hex << std::uppercase
        << std::setw(2) << std::setfill('0') << (int)buf[i] << ' ';
    std::cout << std::dec << "\n";
}

// Convert GSM 7-bit to string (basic)
static std::string gsm7bitToString(const BYTE* data, DWORD len) {
    std::string result;
    for (DWORD i = 0; i < len; ++i) {
        BYTE b = data[i];
        if (b >= 0x20 && b <= 0x7E) result += (char)b;
        else if (b == 0x0A) result += "[LF]";
        else if (b == 0x0D) result += "[CR]";
        else result += '.';
    }
    return result;
}

// Convert phone number from BCD format
static std::string bcdToString(const BYTE* data, DWORD len) {
    std::string result;
    for (DWORD i = 0; i < len; ++i) {
        BYTE b = data[i];
        int lo = b & 0x0F;
        int hi = (b >> 4) & 0x0F;
        if (lo == 0x0F) {
            if (hi != 0x0F && hi != 0x00) result += char('0' + hi);
            break;
        }
        result += char('0' + lo);
        if (hi != 0x0F && hi != 0x00) result += char('0' + hi);
    }
    // trim trailing Fs/zeros
    while (!result.empty() && (result.back() == '\x0F' || result.back() == '0')) result.pop_back();
    return result;
}

// Display contact in readable format
static void displayContact(const BYTE* data, DWORD len, int index) {
    if (len < 2) return;

    std::cout << "Kontakt #" << index << ":\n";

    // Many ADN formats have name first (fixed length), we'll try simple approach:
    // Often name is stored in first 14..32 bytes, we'll scan for printable ascii
    std::string name;
    for (DWORD i = 0; i < len && i < 32; ++i) {
        if (data[i] == 0xFF || data[i] == 0x00) break;
        if (data[i] >= 0x20 && data[i] <= 0x7E) name += (char)data[i];
        else name += '.';
    }
    std::cout << "  Nazwa: " << (name.empty() ? "[brak]" : name) << "\n";

    // Try to find BCD number in rest of record (common offset 14..)
    bool found = false;
    for (DWORD i = 10; i + 1 < len && !found; ++i) {
        // heuristic: BCD digits + type-of-number (0x91/0x81)
        if ((data[i] == 0x91 || data[i] == 0x81) && i + 2 < len) {
            BYTE numLen = data[i + 1];
            if (i + 2 + numLen <= len) {
                std::string number = bcdToString(&data[i + 2], numLen);
                if (!number.empty()) {
                    std::cout << "  Numer: +" << number << "\n";
                    found = true;
                    break;
                }
            }
        }
    }
    if (!found) {
        // fallback scan for plausible BCD sequence
        for (DWORD i = 10; i + 1 < len && !found; ++i) {
            std::string number = bcdToString(&data[i], std::min<DWORD>(10, len - i));
            if (number.size() >= 3) {
                std::cout << "  Numer (heurystyka): +" << number << "\n";
                found = true;
                break;
            }
        }
    }

    std::cout << "  Dane HEX: ";
    for (DWORD i = 0; i < std::min<DWORD>(len, 32); ++i)
        std::cout << std::hex << std::setw(2) << std::setfill('0') << (int)data[i] << ' ';
    std::cout << std::dec << "\n----------------------------------------\n";
}

// Display SMS in readable format
static void displaySMS(const BYTE* data, DWORD len, int index) {
    if (len < 2) return;

    std::cout << "SMS #" << index << ":\n";

    BYTE status = data[0];
    std::cout << "  Status: ";
    switch (status) {
    case 0x00: std::cout << "Nieprzeczytany"; break;
    case 0x01: std::cout << "Przeczytany"; break;
    case 0x03: std::cout << "Wysłany"; break;
    case 0x07: std::cout << "Nie wysłany"; break;
    default:   std::cout << "Nieznany (0x" << std::hex << (int)status << std::dec << ")"; break;
    }
    std::cout << "\n";

    // Attempt to parse sender (heuristic)
    for (DWORD i = 1; i + 2 < len; ++i) {
        if (data[i] == 0x91 || data[i] == 0x81) {
            BYTE numberLen = data[i + 1];
            if (i + 2 + numberLen <= len) {
                std::string sender = bcdToString(&data[i + 2], numberLen);
                if (!sender.empty()) {
                    std::cout << "  Nadawca: +" << sender << "\n";
                    break;
                }
            }
        }
    }

    if (len >= 7) {
        std::cout << "  Timestamp (raw): ";
        for (DWORD i = (len >= 7 ? len - 7 : 0); i < len; ++i)
            std::cout << std::hex << std::setw(2) << std::setfill('0') << (int)data[i] << ' ';
        std::cout << std::dec << "\n";
    }

    // Find text start (heuristic)
    DWORD textStart = 0;
    for (DWORD i = 10; i + 1 < len; ++i) {
        if (data[i] != 0x00 && data[i] != 0xFF) { textStart = i; break; }
    }
    if (textStart > 0 && textStart < len) {
        DWORD textLen = std::min<DWORD>(len - textStart, 160);
        std::string message = gsm7bitToString(&data[textStart], textLen);
        std::cout << "  Treść: " << message;
        if (textLen < (len - textStart)) std::cout << "...";
        std::cout << "\n";
    }

    std::cout << "  Dane HEX: ";
    for (DWORD i = 0; i < std::min<DWORD>(len, 32); ++i)
        std::cout << std::hex << std::setw(2) << std::setfill('0') << (int)data[i] << ' ';
    std::cout << std::dec << "\n----------------------------------------\n";
}

// Helper: transmit and print (for custom APDU)
static LONG transmitAPDU_and_print(SCARDHANDLE card, DWORD proto, const std::vector<BYTE>& apdu) {
    const SCARD_IO_REQUEST* io = (proto == SCARD_PROTOCOL_T1) ? SCARD_PCI_T1 : SCARD_PCI_T0;

    BYTE resp[512]{};
    DWORD respLen = sizeof(resp);
    LONG rc = SCardTransmit(card, io, apdu.data(), (DWORD)apdu.size(), nullptr, resp, &respLen);
    if (rc != SCARD_S_SUCCESS) {
        std::cout << "SCardTransmit blad: 0x" << std::hex << rc << std::dec << "\n";
        return rc;
    }

    std::cout << "=> APDU: ";
    for (BYTE b : apdu) std::cout << std::hex << std::setw(2) << std::setfill('0') << (int)b << ' ';
    std::cout << std::dec << "\n";

    if (respLen >= 2) {
        DWORD dataLen = respLen - 2;
        BYTE sw1 = resp[respLen - 2], sw2 = resp[respLen - 1];

        std::cout << "<= DATA: ";
        for (DWORD i = 0; i < dataLen; ++i)
            std::cout << std::hex << std::setw(2) << std::setfill('0') << (int)resp[i] << ' ';
        std::cout << std::dec << "\n";

        std::cout << "ASCII: ";
        for (DWORD i = 0; i < dataLen; ++i) {
            unsigned char ch = resp[i];
            std::cout << ((ch >= 32 && ch <= 126) ? (char)ch : '.');
        }
        std::cout << "\n";

        std::cout << "STATUS: " << std::hex << std::setw(2) << std::setfill('0')
            << (int)sw1 << ' ' << (int)sw2 << std::dec << "\n";

        // GET RESPONSE handling if 61 xx
        if (sw1 == 0x61 && sw2 != 0x00) {
            BYTE le = sw2;
            std::vector<BYTE> getResp = { 0x00, 0xC0, 0x00, 0x00, le };
            std::cout << "  (GET RESPONSE " << std::hex << (int)le << std::dec << ")\n";
            respLen = sizeof(resp);
            rc = SCardTransmit(card, io, getResp.data(), (DWORD)getResp.size(), nullptr, resp, &respLen);
            if (rc == SCARD_S_SUCCESS && respLen >= 2) {
                DWORD dlen = respLen - 2;
                std::cout << "GET<= DATA: ";
                for (DWORD i = 0; i < dlen; ++i) std::cout << std::hex << std::setw(2) << std::setfill('0') << (int)resp[i] << ' ';
                std::cout << std::dec << "\n";
                std::cout << "GET<= STATUS: " << std::hex << (int)resp[respLen - 2] << ' ' << (int)resp[respLen - 1] << std::dec << "\n";
            }
            else {
                std::cout << "GET RESPONSE blad: 0x" << std::hex << rc << std::dec << "\n";
            }
        }
    }
    else {
        std::cout << "<= Pusta odpowiedz (respLen=" << respLen << ")\n";
    }
    return SCARD_S_SUCCESS;
}

// Read phonebook contacts (improved: CLA=00, handle 6C XX, log SW)
static void readPhonebook(SCARDHANDLE card, DWORD proto) {
    std::cout << "\n=== ODCZYT KSIĄŻKI TELEFONICZNEJ ===\n";

    // Use CLA=00 selects (more compatible)
    std::vector<BYTE> selectMF = { 0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00 };
    std::vector<BYTE> selectDF = { 0x00, 0xA4, 0x00, 0x00, 0x02, 0x7F, 0x10 };
    std::vector<BYTE> selectADN = { 0x00, 0xA4, 0x00, 0x00, 0x02, 0x6F, 0x3A };

    transmitAPDU_and_print(card, proto, selectMF);
    transmitAPDU_and_print(card, proto, selectDF);
    transmitAPDU_and_print(card, proto, selectADN);

    std::cout << "\n--- KONTAKTY ---\n";
    const SCARD_IO_REQUEST* io = (proto == SCARD_PROTOCOL_T1) ? SCARD_PCI_T1 : SCARD_PCI_T0;

    for (int i = 1; i <= 250; i++) { // iterate more records, break on 6A83 or other stop
        std::vector<BYTE> readRec = { 0x00, 0xB2, (BYTE)i, 0x04, 0x00 }; // Le=0 -> card may respond 6C xx
        BYTE resp[512]; DWORD respLen = sizeof(resp);
        LONG rc = SCardTransmit(card, io, readRec.data(), (DWORD)readRec.size(), nullptr, resp, &respLen);
        if (rc != SCARD_S_SUCCESS) {
            std::cout << "Blad przy SCardTransmit: 0x" << std::hex << rc << std::dec << "\n";
            break;
        }
        if (respLen < 2) {
            std::cout << "Pusta odpowiedz dla rekordu " << i << "\n";
            continue;
        }

        BYTE sw1 = resp[respLen - 2], sw2 = resp[respLen - 1];

        // handle 6Cxx (correct Le)
        if (sw1 == 0x6C) {
            readRec.back() = sw2; // set Le to correct length
            respLen = sizeof(resp);
            rc = SCardTransmit(card, io, readRec.data(), (DWORD)readRec.size(), nullptr, resp, &respLen);
            if (rc != SCARD_S_SUCCESS) {
                std::cout << "Blad SCardTransmit po 6C: 0x" << std::hex << rc << std::dec << "\n";
                break;
            }
            if (respLen >= 2) {
                sw1 = resp[respLen - 2]; sw2 = resp[respLen - 1];
            }
        }

        if (sw1 == 0x90 && sw2 == 0x00 && respLen > 2) {
            displayContact(resp, respLen - 2, i);
        }
        else {
            std::cout << "Rekord " << i << " SW1SW2= "
                << std::hex << std::setw(2) << std::setfill('0') << (int)sw1 << ' '
                << std::setw(2) << (int)sw2 << std::dec << "\n";
            if (sw1 == 0x6A && sw2 == 0x83) { // record not found / out of range
                std::cout << "Koniec rekordow (6A83)\n";
                break;
            }
            if (sw1 == 0x69 && sw2 == 0x82) {
                std::cout << "Brak uprawnien (PIN zablokowany?)\n";
                break;
            }
            // other SW -> continue or break depending
            if (i > 50) break; // safety
        }
    }
}

// Read SMS messages (improved identical strategy)
static void readSMS(SCARDHANDLE card, DWORD proto) {
    std::cout << "\n=== ODCZYT WIADOMOŚCI SMS ===\n";

    std::vector<BYTE> selectMF = { 0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00 };
    std::vector<BYTE> selectDF = { 0x00, 0xA4, 0x00, 0x00, 0x02, 0x7F, 0x10 };
    std::vector<BYTE> selectSMS = { 0x00, 0xA4, 0x00, 0x00, 0x02, 0x6F, 0x3C };

    transmitAPDU_and_print(card, proto, selectMF);
    transmitAPDU_and_print(card, proto, selectDF);
    transmitAPDU_and_print(card, proto, selectSMS);

    std::cout << "\n--- WIADOMOSCI SMS ---\n";
    const SCARD_IO_REQUEST* io = (proto == SCARD_PROTOCOL_T1) ? SCARD_PCI_T1 : SCARD_PCI_T0;

    for (int i = 1; i <= 250; i++) {
        std::vector<BYTE> readRec = { 0x00, 0xB2, (BYTE)i, 0x04, 0x00 };
        BYTE resp[512]; DWORD respLen = sizeof(resp);
        LONG rc = SCardTransmit(card, io, readRec.data(), (DWORD)readRec.size(), nullptr, resp, &respLen);
        if (rc != SCARD_S_SUCCESS) {
            std::cout << "Blad przy SCardTransmit: 0x" << std::hex << rc << std::dec << "\n";
            break;
        }
        if (respLen < 2) {
            std::cout << "Pusta odpowiedz dla SMS " << i << "\n";
            continue;
        }

        BYTE sw1 = resp[respLen - 2], sw2 = resp[respLen - 1];

        if (sw1 == 0x6C) {
            readRec.back() = sw2;
            respLen = sizeof(resp);
            rc = SCardTransmit(card, io, readRec.data(), (DWORD)readRec.size(), nullptr, resp, &respLen);
            if (rc != SCARD_S_SUCCESS) { std::cout << "Blad SCardTransmit po 6C\n"; break; }
            if (respLen >= 2) { sw1 = resp[respLen - 2]; sw2 = resp[respLen - 1]; }
        }

        if (sw1 == 0x90 && sw2 == 0x00 && respLen > 2) {
            displaySMS(resp, respLen - 2, i);
        }
        else {
            std::cout << "SMS " << i << " SW1SW2= "
                << std::hex << std::setw(2) << std::setfill('0') << (int)sw1 << ' '
                << std::setw(2) << (int)sw2 << std::dec << "\n";
            if (sw1 == 0x6A && sw2 == 0x83) { std::cout << "Koniec rekordow (6A83)\n"; break; }
            if (sw1 == 0x69 && sw2 == 0x82) { std::cout << "Brak uprawnien (PIN zablokowany?)\n"; break; }
            if (i > 50) break;
        }
    }
}

// Send custom APDU command (narrow strings)
static void sendCustomAPDU(SCARDHANDLE card, DWORD proto) {
    std::cout << "\n=== WYSYŁANIE WŁASNEJ KOMENDY APDU ===\n";

    std::string line;
    std::cout << "Podaj komendę APDU w HEX (np. 00 A4 00 00 02 3F 00):\n> ";
    if (!std::getline(std::cin, line) || line.empty()) {
        std::cout << "Pusta komenda.\n";
        return;
    }

    std::stringstream ss(line);
    std::string tok;
    std::vector<BYTE> apdu;
    while (ss >> tok) {
        try {
            unsigned int val = std::stoul(tok, nullptr, 16);
            apdu.push_back(static_cast<BYTE>(val & 0xFF));
        }
        catch (...) {
            std::cout << "Bledny format. HEX oddzielony spacjami.\n";
            return;
        }
    }

    if (apdu.empty()) { std::cout << "Pusta komenda.\n"; return; }

    // Use transmitAPDU_and_print for output and GET RESPONSE handling
    transmitAPDU_and_print(card, proto, apdu);
}

int main() {
    std::cout << "=== PROGRAM DO ODCZYTU DANYCH Z KART SIM ===\n\n";

    // 1) KONTEKST
    SCARDCONTEXT ctx;
    LONG st = SCardEstablishContext(SCARD_SCOPE_USER, nullptr, nullptr, &ctx);
    if (st != SCARD_S_SUCCESS) {
        std::cout << "Blad: nie moge nawiazac kontekstu (Smart Card service).\n";
        return 1;
    }

    // 2) LISTA CZYTNIKOW
    LPWSTR readers = nullptr;
    DWORD len = SCARD_AUTOALLOCATE;
    LONG r = SCardListReadersW(ctx, nullptr, (LPWSTR)&readers, &len);
    if (r != SCARD_S_SUCCESS) {
        std::cout << "Nie wykryto podlaczonych czytnikow (lub brak sterownikow).\n";
        SCardReleaseContext(ctx);
        return 1;
    }

    std::vector<std::wstring> lista;
    const wchar_t* p = readers;
    while (*p) {
        lista.emplace_back(p);
        p += wcslen(p) + 1;
    }
    if (lista.empty()) {
        std::cout << "Lista czytnikow pusta.\n";
        SCardFreeMemory(ctx, readers);
        SCardReleaseContext(ctx);
        return 1;
    }

    // a) Wyświetl nazwę podłączonego urządzenia-czytnika
    std::wcout << L"\n(a) Podlaczone urzadzenie-czytnik:\n";
    for (size_t i = 0; i < lista.size(); ++i)
        std::wcout << L"  [" << i << L"] " << lista[i] << L"\n";

    // b) Wybór czytnika (use getline to avoid mixing)
    std::string line;
    size_t idx = 0;
    while (true) {
        std::cout << "\n(b) Wybierz numer czytnika: ";
        if (!std::getline(std::cin, line)) { std::cout << "Blad wejsciowy\n"; return 1; }
        try {
            idx = static_cast<size_t>(std::stoul(line));
            if (idx < lista.size()) break;
        }
        catch (...) {}
        std::cout << "Niepoprawny numer. Sprobuj ponownie.\n";
    }
    std::wcout << L"Wybrano: " << lista[idx] << L"\n";

    // 4) POLACZENIE
    SCARDHANDLE card;
    DWORD proto = 0;
    LONG c = SCardConnectW(ctx, lista[idx].c_str(),
        SCARD_SHARE_SHARED,
        SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1,
        &card, &proto);
    if (c != SCARD_S_SUCCESS) {
        std::cout << "Nie moge polaczyc z karta. Kod: 0x" << std::hex << c << std::dec << "\n";
        SCardFreeMemory(ctx, readers);
        SCardReleaseContext(ctx);
        return 1;
    }
    std::cout << "Polaczono. Protokol: "
        << ((proto & SCARD_PROTOCOL_T0) ? "T0 " : "")
        << ((proto & SCARD_PROTOCOL_T1) ? "T1 " : "") << "\n";

    // 5) ATR
  // ATR
    BYTE atr[64] = {};
    DWORD atrlen = sizeof(atr);
    DWORD state = 0, proto2 = 0;
    LONG s = SCardStatusW(card, nullptr, nullptr, &state, &proto2, atr, &atrlen);
    if (s == SCARD_S_SUCCESS) {
        std::cout << "ATR: ";
        printHex(atr, atrlen);
    }
    else {
        std::cout << "Nie udalo sie pobrac ATR. Kod: 0x" << std::hex << s << std::dec << "\n";
    }

    // MENU GŁÓWNE (use getline for choices)
    int choice = 0;
    do {
        std::cout << "\n=== MENU GLOWNE ===\n";
        std::cout << "1. Wyslij wlasna komende APDU (HEX)\n";
        std::cout << "2. Odczytaj ksiazke telefoniczna\n";
        std::cout << "3. Odczytaj wiadomosci SMS\n";
        std::cout << "4. Wyjscie\n";
        std::cout << "Wybierz opcje: ";

        if (!std::getline(std::cin, line)) break;
        try { choice = std::stoi(line); }
        catch (...) { choice = -1; }

        switch (choice) {
        case 1: sendCustomAPDU(card, proto); break;
        case 2: readPhonebook(card, proto); break;
        case 3: readSMS(card, proto); break;
        case 4: std::cout << "Zamykanie programu...\n"; break;
        default: std::cout << "Niepoprawny wybor.\n"; break;
        }

    } while (choice != 4);

    SCardDisconnect(card, SCARD_LEAVE_CARD);
    SCardFreeMemory(ctx, readers);
    SCardReleaseContext(ctx);
    return 0;
}
