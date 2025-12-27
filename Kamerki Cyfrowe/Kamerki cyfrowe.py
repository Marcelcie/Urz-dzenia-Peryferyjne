#!/usr/bin/env python3
# cw7_final_poprawiony_v3.py
# -*- coding: utf-8 -*-
"""
Wersja finalna: Zadanie 1 + Zadanie 2 (HDR) + Powiadomienia na ekranie.
Zawiera ostateczną poprawkę błędu "Nagrywanie zatrzymane (zmiana rozdzielczości)".

Wymaga: OpenCV (cv2) i numpy.
Instalacja: pip install opencv-python numpy
"""

import cv2
import os
import time
import argparse
from datetime import datetime
import numpy as np
import sys


# -------------------- KONFIGURACJA --------------------

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


# Katalog bazowy (tam gdzie .exe lub .py)
BASE_DIR = get_base_dir()

# Zapisujemy wszystko do głównego folderu
DIR_SNAPSHOTS = os.path.join(BASE_DIR, "zdjecia")
DIR_VIDEOS = os.path.join(BASE_DIR, "filmy")
DIR_HDR = os.path.join(BASE_DIR, "zdjecia_hdr")

MAX_CAMERA_INDEX_DETECT = 8
DEFAULT_FOURCC = "MJPG"
DEFAULT_FPS = 25.0

AVAILABLE_RESOLUTIONS = [
    (640, 480),
    (1280, 720),
    (1920, 1080),
    (800, 600)
]

BRIGHTNESS_STEP = 10


# -------------------- POMOCNICZE FUNKCJE --------------------
def ensure_dir(path):
    """Tworzy katalog, jeśli nie istnieje."""
    if not path:
        return
    os.makedirs(path, exist_ok=True)


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def list_usb_cameras(max_index=MAX_CAMERA_INDEX_DETECT):
    found = []
    for i in range(max_index + 1):
        try:
            cap = cv2.VideoCapture(i)
            if cap is None or not cap.isOpened():
                continue
            ret, frame = cap.read()
            if not ret:
                cap.release()
                continue
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
            fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
            found.append((i, w, h, fps))
            cap.release()
        except Exception:
            continue
    return found


def open_usb_camera(index=0):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        return None
    time.sleep(0.3)
    return cap


def set_camera_parameters(cap, params: dict):
    results = {}
    mapping = {
        'szerokosc': cv2.CAP_PROP_FRAME_WIDTH,
        'wysokosc': cv2.CAP_PROP_FRAME_HEIGHT,
        'jasnosc': cv2.CAP_PROP_BRIGHTNESS,
        'eksplozja': cv2.CAP_PROP_EXPOSURE,
    }
    for k, v in params.items():
        if k not in mapping: continue
        try:
            cap.set(mapping[k], float(v))
            results[k] = True
        except Exception:
            results[k] = False
    return results


def get_camera_parameters(cap):
    props = {
        'szerokosc': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0),
        'wysokosc': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0),
        'fps': cap.get(cv2.CAP_PROP_FPS) or 0.0,
        'jasnosc': cap.get(cv2.CAP_PROP_BRIGHTNESS),
        'eksplozja': cap.get(cv2.CAP_PROP_EXPOSURE)
    }
    return props


# -------------------- ZAPIS I NAGRYWANIE --------------------
def save_frame(frame, path):
    ensure_dir(os.path.dirname(path))
    return cv2.imwrite(path, frame)


def start_video_recording(path, fourcc=DEFAULT_FOURCC, fps=DEFAULT_FPS, frame_size=(640, 480), is_color=True):
    ensure_dir(os.path.dirname(path))
    fourcc_code = cv2.VideoWriter_fourcc(*fourcc)
    writer = cv2.VideoWriter(path, fourcc_code, fps, frame_size, isColor=is_color)
    return writer


def stop_video_recording(writer):
    if writer is not None:
        writer.release()


# -------------------- IMPLEMENTACJA HDR (Zadanie II.2) --------------------
def capture_exposure_series(cap, exposures):
    """Rejestruje serię klatek dla różnych ekspozycji."""
    original_exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
    frames = []

    print("\n--- Rozpoczynam rejestracje serii HDR (Ekspozycje:", exposures, ") ---")
    time.sleep(1.0)

    for exp_val in exposures:
        print(f" -> Ustawiam ekspozycje na: {exp_val}")
        set_camera_parameters(cap, {'eksplozja': exp_val})
        time.sleep(1.5)
        for _ in range(5):
            ret, frame = cap.read()

        if ret:
            frames.append(frame)
            print(" -> Klatka zarejestrowana.")
        else:
            print(f" !!! Nie udalo sie pobrac klatki dla ekspozycji {exp_val}.")

    set_camera_parameters(cap, {'eksplozja': original_exposure})
    print(" Przywrocono oryginalna ekspozycje.")

    return frames


def process_hdr(frames):
    """Łączy serię klatek w jeden obraz HDR i mapuje tony (tone mapping)."""
    if len(frames) < 3:
        print("Błąd HDR: Za mało klatek do połączenia (wymagane min. 3).")
        return False, None

    times = np.array([1 / 4.0, 1.0, 4.0], dtype=np.float32)
    times = times[:len(frames)]

    try:
        # 1. Kalibracja (oczekuje 8-bit)
        calibrate_debevec = cv2.createCalibrateDebevec()
        response = calibrate_debevec.process(frames, times)

        # 2. Łączenie (oczekuje 8-bit, wg logów błędu)
        merge_debevec = cv2.createMergeDebevec()
        hdr_image = merge_debevec.process(frames, times, response)

        # 3. Mapowanie tonów (oczekuje float32)
        hdr_image = hdr_image.astype('float32')
        tonemap = cv2.createTonemapReinhard(gamma=2.2)
        ldr_image = tonemap.process(hdr_image)

        ldr_image = (ldr_image * 255).astype('uint8')

        return True, ldr_image
    except Exception as e:
        print(f" !!! Błąd podczas przetwarzania HDR: {e}")
        return False, None


# -------------------- APLIKACJA KONSOLIOWA --------------------
def interactive_capture_loop(source_index=0):
    """
    Interaktywny podgląd i sterowanie:
    """
    cap = open_usb_camera(source_index)
    if cap is None:
        print("Nie można otworzyć kamery o indeksie", source_index)
        return

    props = get_camera_parameters(cap)
    print("Otwarto kamerę:", source_index, "parametry początkowe:", props)

    window = "Kamerka cyfrowa - nacisnij 'h' aby otworzyc okno pomocnicze."
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window, 800, 600)

    recording = False
    writer = None

    # === NOWA POPRAWKA: Zmienne do przechowywania rozmiaru VideoWritera ===
    writer_width = 0
    writer_height = 0

    HELP_LINES = [
        "Sterowanie:",
        " c - zapisz zdjecie (.PNG)",
        " v - start/stop nagrywania (.AVI)",
        " r - zrob i przetworz zdjecie HDR",
        " p - pokaz/ukryj aktualne parametry kamery",
        " s - zmien rozdzielczosc (1080p,720p,600p,480p)",
        " +/= - zwieksz jasnosc",
        " -/_ - zmniejsz jasnosc",
        " h - pokaz/ukryj pomoc",
        " q / ESC - zakoncz program"
    ]
    show_info = True
    info_lines = HELP_LINES
    fps_measured = None
    frame_count = 0
    last_time = time.time()

    w_current = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h_current = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    try:
        current_res_index = AVAILABLE_RESOLUTIONS.index((w_current, h_current))
    except ValueError:
        current_res_index = 0
        set_camera_parameters(cap, {
            'szerokosc': AVAILABLE_RESOLUTIONS[0][0],
            'wysokosc': AVAILABLE_RESOLUTIONS[0][1]
        })

    ret, frame = False, None

    # Zmienne do powiadomień na ekranie
    notification_message = ""
    notification_timer = 0.0
    NOTIFICATION_DURATION = 3.0  # 3 sekundy

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Błąd odczytu klatki. Zamykanie...")
            break

        frame_count += 1
        now = time.time()
        if now - last_time >= 1.0:
            fps_measured = frame_count / (now - last_time)
            frame_count = 0
            last_time = now

        display = frame.copy()

        # Rysowanie powiadomienia
        if time.time() < notification_timer:
            cv2.putText(display, notification_message, (10, display.shape[0] - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        # Rysowanie informacji (Pomocy lub Parametrów) - POPRAWIONE WCIĘCIE
        if show_info:
            y0, dy = 20, 22
            for i, ln in enumerate(info_lines):
                cv2.putText(display, ln, (10, y0 + i * dy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1,
                            cv2.LINE_AA)

        if fps_measured is not None and show_info:
            cv2.putText(display, f"FPS (ilosc klatek na sekunde): {fps_measured:.1f}", (10, display.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1, cv2.LINE_AA)  # Zmieniono kolor na biały

        cv2.imshow(window, display)
        key = cv2.waitKey(1) & 0xFF

        # --- Obsługa klawiszy ---
        if key in (ord('q'), 27):
            break
        if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
            break
        elif key == ord('h'):
            if show_info and info_lines == HELP_LINES:
                show_info = False
            else:
                info_lines = HELP_LINES
                show_info = True

        elif key == ord('c'):
            ret_snap, snap = cap.read()
            if ret_snap:
                fname = os.path.join(DIR_SNAPSHOTS, f"snapshot_{timestamp()}.png")
                save_frame(snap, fname)
                print("Zapisano pojedynczą klatkę:", fname)
                notification_message = f"Zapisano: {os.path.basename(fname)}"
                notification_timer = time.time() + NOTIFICATION_DURATION

        elif key == ord('v'):
            if not recording:
                if frame is None:
                    print("Błąd: Nie odczytano jeszcze klatki. Spróbuj ponownie.")
                    continue

                # === POPRAWKA: Używamy h, w z frame.shape i zapisujemy je ===
                h, w, _ = frame.shape
                writer_width = w
                writer_height = h

                fps_cap = cap.get(cv2.CAP_PROP_FPS) or DEFAULT_FPS
                video_path = os.path.join(DIR_VIDEOS, f"video_{timestamp()}.avi")

                writer = start_video_recording(video_path, fourcc=DEFAULT_FOURCC, fps=fps_cap,
                                               frame_size=(writer_width, writer_height))

                if writer is None or not writer.isOpened():
                    print("Nie można utworzyć VideoWriter (sprawdź kodeki).")
                    writer = None
                    notification_message = "Blad: Nie mozna rozpoczac nagrywania!"
                else:
                    recording = True
                    print("Rozpoczęto nagrywanie do:", video_path)
                    notification_message = f"Nagrywanie START: {os.path.basename(video_path)}"
                notification_timer = time.time() + NOTIFICATION_DURATION
            else:
                recording = False
                stop_video_recording(writer)
                writer = None
                print("Zakończono nagrywanie.")
                notification_message = "Nagrywanie STOP"
                notification_timer = time.time() + NOTIFICATION_DURATION

        elif key == ord('r'):
            exposures = [-7.0, -5.0, -3.0]
            notification_message = "Przetwarzanie HDR... (trzy ekspozycje)"
            notification_timer = time.time() + 5.0

            cv2.putText(display, notification_message, (10, display.shape[0] - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow(window, display)
            cv2.waitKey(1)

            hdr_frames = capture_exposure_series(cap, exposures)

            if len(hdr_frames) >= 3:
                print("Rozpoczynam proces łączenia HDR...")
                ok, final_hdr = process_hdr(hdr_frames)

                if ok:
                    fname = os.path.join(DIR_HDR, f"hdr_final_{timestamp()}.png")
                    save_frame(final_hdr, fname)
                    print(f"Zapisano obraz HDR: {fname}")
                    cv2.imshow("Obraz HDR (Tone Mapped)", final_hdr)
                    notification_message = f"Zapisano HDR: {os.path.basename(fname)}"
                else:
                    print(" !!! Proces HDR nie powiodl sie.")
                    notification_message = "Blad: Proces HDR nie powiodl sie."
            else:
                print(" !!! Zarejestrowano za malo klatek. Przerwano proces HDR.")
                notification_message = "Blad: Nie mozna bylo zarejestrowac klatek HDR."

            notification_timer = time.time() + NOTIFICATION_DURATION

        elif key == ord('p'):
            if show_info and info_lines != HELP_LINES:
                show_info = False
            else:
                props = get_camera_parameters(cap)
                print("Odswiezono parametry:", props)
                param_lines = ["--- Aktualne Parametry ---"]
                for key, val in props.items():
                    if isinstance(val, float):
                        param_lines.append(f" - {key}: {val:.1f}")
                    else:
                        param_lines.append(f" - {key}: {val}")

                info_lines = param_lines
                show_info = True

        elif key == ord('s'):
            current_res_index = (current_res_index + 1) % len(AVAILABLE_RESOLUTIONS)
            new_w, new_h = AVAILABLE_RESOLUTIONS[current_res_index]

            print(f"\n--- ZMIANA ROZDZIELCZOSCI na {new_w}x{new_h} ---")
            notification_message = f"Zmiana rozdzielczosci na {new_w}x{new_h}..."
            notification_timer = time.time() + NOTIFICATION_DURATION

            if recording:
                recording = False
                stop_video_recording(writer)
                writer = None
                print("Zatrzymano nagrywanie z powodu zmiany rozdzielczości.")

            cap.release()
            cap = open_usb_camera(source_index)
            if cap is None:
                print(" !!! FATALNY BLAD: Nie udalo sie ponownie otworzyc kamery.")
                break

            res = set_camera_parameters(cap, {'szerokosc': new_w, 'wysokosc': new_h})
            print(f"Wynik zmiany: {res}")
            time.sleep(1.0)

            props = get_camera_parameters(cap)
            print(f" (i) Nowe odczytane parametry: {props['szerokosc']}x{props['wysokosc']}")

            if props['szerokosc'] != new_w or props['wysokosc'] != new_h:
                print(" !!! OSTRZEZENIE: Sterownik kamery nie zaakceptowal nowej rozdzielczosci.")
                notification_message = f"Blad: Kamera odrzucila rozdzielczosc {new_w}x{new_h}"
                try:
                    current_res_index = AVAILABLE_RESOLUTIONS.index((props['szerokosc'], props['wysokosc']))
                except ValueError:
                    current_res_index = 0
            else:
                notification_message = f"Rozdzielczosc ustawiona na {props['szerokosc']}x{props['wysokosc']}"

            notification_timer = time.time() + NOTIFICATION_DURATION


        elif key == ord('+') or key == ord('='):
            current_b = cap.get(cv2.CAP_PROP_BRIGHTNESS)
            new_b = min(current_b + BRIGHTNESS_STEP, 255)
            set_camera_parameters(cap, {'jasnosc': new_b})
            new_val = cap.get(cv2.CAP_PROP_BRIGHTNESS)
            print(f"Jasnosc: {new_val}")
            notification_message = f"Jasnosc: {new_val}"
            notification_timer = time.time() + NOTIFICATION_DURATION

        elif key == ord('-') or key == ord('_'):  # Dodano '_' dla klawiatur bez numpada
            current_b = cap.get(cv2.CAP_PROP_BRIGHTNESS)
            new_b = max(current_b - BRIGHTNESS_STEP, -255)
            set_camera_parameters(cap, {'jasnosc': new_b})
            new_val = cap.get(cv2.CAP_PROP_BRIGHTNESS)
            print(f"Jasnosc: {new_val}")
            notification_message = f"Jasnosc: {new_val}"
            notification_timer = time.time() + NOTIFICATION_DURATION

        # === NOWA POPRAWKA: Używamy zapisanych writer_width/height ===
        if recording and writer is not None:
            if (frame.shape[1] == writer_width and
                    frame.shape[0] == writer_height):
                writer.write(frame)
            else:
                # Ten błąd może się zdarzyć, jeśli kamera nagle zmieni rozmiar klatki w locie
                recording = False
                stop_video_recording(writer)
                writer = None
                print(" !!! Krytyczny blad: Rozmiar klatki (frame.shape) nie zgadza sie z rozmiarem VideoWritera.")
                notification_message = "Blad krytyczny: Nagrywanie zatrzymane (niezgodnosc klatek)"
                notification_timer = time.time() + NOTIFICATION_DURATION

    # cleanup
    if writer is not None:
        stop_video_recording(writer)
    cap.release()
    cv2.destroyAllWindows()


# -------------------- SKRYPT GŁÓWNY --------------------
def main():
    parser = argparse.ArgumentParser(description="Ćwiczenie: rejestracja obrazu z kamery USB (Windows)")
    parser.add_argument('--list', action='store_true', help='Wypisz dostępne kamery USB')
    parser.add_argument('--max-index', type=int, default=MAX_CAMERA_INDEX_DETECT,
                        help='Maksymalny indeks do sprawdzenia')
    parser.add_argument('--index', type=int, default=None,
                        help='Indeks kamery do otwarcia')
    args = parser.parse_args()

    # Tworzenie folderów przy starcie (dla wersji .exe)
    ensure_dir(DIR_SNAPSHOTS)
    ensure_dir(DIR_VIDEOS)
    ensure_dir(DIR_HDR)

    if args.list:
        cams = list_usb_cameras(max_index=args.max_index)
        if not cams:
            print("Brak wykrytych kamer USB.")
        else:
            print("Wykryte kamery (index, szerokosc, wysokosc, fps):")
            for c in cams:
                print(" ", c)
        return

    # wybór kamery
    cams = list_usb_cameras(max_index=args.max_index)
    chosen = args.index
    if chosen is None:
        if cams:
            chosen = cams[0][0]
            print("Automatycznie wybrano kamerę o indeksie", chosen)
        else:
            print("Nie wykryto kamer. Użyj --list aby sprawdzić dostępne urządzenia.")
            return

    interactive_capture_loop(chosen)


if __name__ == "__main__":
    main()