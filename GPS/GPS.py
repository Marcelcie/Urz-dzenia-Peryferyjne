import tkinter as tki
from tkinter import scrolledtext
import serial
import time
import threading
import webbrowser


class SymulatorGPS:
    def __init__(self):
        self.dane = [
            "$GPRMC,120001,A,5049.5000,N,01532.1000,E,0.5,0.0,141125,,,A*70",
            "$GPGGA,120001,5049.5000,N,01532.1000,E,1,08,0.9,689.0,M,40.0,M,,*4B",
            "$GPGSA,A,3,04,05,09,12,24,25,28,29,,,,,1.5,0.9,1.2*3E",
            "$GPGSV,3,1,11,03,03,111,00,04,15,270,00,06,01,010,00,13,06,292,00*75",
            "$GPGLL,5049.5000,N,01532.1000,E,120001,A,A*50",

            "$GPRMC,120002,A,5049.5050,N,01532.1050,E,0.6,0.0,141125,,,A*71",
            "$GPGGA,120002,5049.5050,N,01532.1050,E,1,09,0.9,689.2,M,40.0,M,,*46",
            "$GPGSA,A,3,04,05,09,12,24,25,28,29,30,,,,1.4,0.9,1.1*3F",
            "$GPGLL,5049.5050,N,01532.1050,E,120002,A,A*51",

            "$GPRMC,120003,A,5049.5100,N,01532.1100,E,0.5,0.0,141125,,,A*72",
            "$GPGGA,120003,5049.5100,N,01532.1100,E,1,09,0.9,689.5,M,40.0,M,,*46",
            "$GPGLL,5049.5100,N,01532.1100,E,120003,A,A*52"
        ]
        self.idx = 0
        self.is_open = True

    @property
    def in_waiting(self):
        return 1

    def readline(self):
        if not self.is_open: return b''
        line = self.dane[self.idx]
        self.idx = (self.idx + 1) % len(self.dane)
        time.sleep(0.2)
        return line.encode('ascii')

    def close(self):
        self.is_open = False


class GPSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GPS NMEA Reader & Visualizer")
        self.root.geometry("600x550")

        self.is_running = False
        self.serial_conn = None
        self.current_lat = 0.0
        self.current_lon = 0.0

        control_frame = tki.LabelFrame(root, text="Konfiguracja Połączenia", padx=10, pady=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        tki.Label(control_frame, text="Port COM:").grid(row=0, column=0, padx=5)
        self.port_entry = tki.Entry(control_frame, width=10)
        self.port_entry.insert(0, "COM3")
        self.port_entry.grid(row=0, column=1, padx=5)

        self.sim_var = tki.BooleanVar(value=True)
        tki.Checkbutton(control_frame, text="Tryb Symulacji", variable=self.sim_var).grid(row=0, column=2, padx=10)

        self.btn_connect = tki.Button(control_frame, text="POŁĄCZ", command=self.toggle_connection, bg="#4CAF50",
                                      fg="white", width=15)
        self.btn_connect.grid(row=0, column=3, padx=10)

        data_frame = tki.LabelFrame(root, text="Odczytane Dane (GPGGA)", padx=10, pady=10)
        data_frame.pack(fill="x", padx=10, pady=5)

        self.lbl_time = self.create_display_field(data_frame, "Czas UTC:", 0, 0)
        self.lbl_sats = self.create_display_field(data_frame, "Satelity:", 0, 1)
        self.lbl_lat = self.create_display_field(data_frame, "Szerokość:", 1, 0)
        self.lbl_lon = self.create_display_field(data_frame, "Długość:", 1, 1)
        self.lbl_alt = self.create_display_field(data_frame, "Wysokość (m):", 2, 0)
        self.lbl_zone = self.create_display_field(data_frame, "Strefa Czasowa:", 2, 1)

        self.btn_map = tki.Button(root, text="Otwórz pozycję w Google Maps 🌍", command=self.open_map, state="disabled",
                                  bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        self.btn_map.pack(pady=10, ipadx=10, ipady=5)

        log_frame = tki.LabelFrame(root, text="Logi NMEA (Wszystkie zdania)", padx=5, pady=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, state='disabled', font=("Consolas", 8))
        self.log_area.pack(fill="both", expand=True)

    def create_display_field(self, parent, label_text, r, c):
        tki.Label(parent, text=label_text, font=("Arial", 10, "bold")).grid(row=r, column=c * 2, sticky="e", padx=5,
                                                                            pady=5)
        lbl_val = tki.Label(parent, text="---", font=("Arial", 10), fg="blue")
        lbl_val.grid(row=r, column=c * 2 + 1, sticky="w", padx=5, pady=5)
        return lbl_val

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tki.END, message + "\n")
        self.log_area.see(tki.END)
        self.log_area.config(state='disabled')

    def toggle_connection(self):
        if not self.is_running:
            self.is_running = True
            self.btn_connect.config(text="ROZŁĄCZ", bg="#f44336")
            self.thread = threading.Thread(target=self.read_gps_loop)
            self.thread.daemon = True
            self.thread.start()
        else:
            self.is_running = False
            self.btn_connect.config(text="POŁĄCZ", bg="#4CAF50")
            if self.serial_conn:
                self.serial_conn.close()
            self.log("Połączenie zakończone.")

    def nmea_to_decimal(self, value, direction):
        if not value: return 0.0
        try:
            dot = value.find('.')
            if dot == -1: return 0.0
            deg = float(value[:dot - 2])
            min = float(value[dot - 2:])
            res = deg + (min / 60.0)
            if direction in ['S', 'W']: res = -res
            return res
        except:
            return 0.0

    def open_map(self):
        if self.current_lat != 0.0:
            url = f"https://www.google.com/maps/search/?api=1&query={self.current_lat},{self.current_lon}"
            webbrowser.open(url)
            self.log(f"Otwieram mapę: {url}")

    def read_gps_loop(self):
        port = self.port_entry.get()
        is_sim = self.sim_var.get()

        try:
            if is_sim:
                self.log("Uruchamianie SYMULATORA...")
                self.serial_conn = SymulatorGPS()
            else:
                self.log(f"Łączenie z {port}...")
                self.serial_conn = serial.Serial(port, 9600, timeout=1)

            self.log("Połączono! Oczekiwanie na dane...")

            while self.is_running:
                if self.serial_conn.in_waiting > 0:
                    raw = self.serial_conn.readline()
                    try:
                        line = raw.decode('ascii', errors='replace').strip()
                        if not line: continue

                        self.log(line)

                        if line.startswith('$GPGGA'):
                            self.parse_gpgga(line)

                    except Exception as e:
                        self.log(f"Błąd danych: {e}")

                if not is_sim:
                    time.sleep(0.1)

        except Exception as e:
            self.log(f"Błąd połączenia: {e}")
            self.is_running = False

    def parse_gpgga(self, line):
        parts = line.split(',')
        if len(parts) < 10: return

        try:
            time_utc = parts[1]
            lat_raw, lat_dir = parts[2], parts[3]
            lon_raw, lon_dir = parts[4], parts[5]
            sats = parts[7]
            alt = parts[9]

            lat = self.nmea_to_decimal(lat_raw, lat_dir)
            lon = self.nmea_to_decimal(lon_raw, lon_dir)

            time_zone_offset = int(lon / 15)
            sign_str = "+" if time_zone_offset >= 0 else ""
            zone_str = f"UTC{sign_str}{time_zone_offset}"

            hh_utc = int(time_utc[:2])
            mm = time_utc[2:4]
            ss = time_utc[4:6]

            hh_local = (hh_utc + time_zone_offset) % 24
            formatted_time = f"{hh_local:02d}:{mm}:{ss}"

            self.lbl_time.config(text=formatted_time)
            self.lbl_sats.config(text=sats)
            self.lbl_lat.config(text=f"{lat:.6f}")
            self.lbl_lon.config(text=f"{lon:.6f}")
            self.lbl_alt.config(text=f"{alt}")
            self.lbl_zone.config(text=zone_str)

            self.current_lat = lat
            self.current_lon = lon

            if lat != 0.0:
                self.btn_map.config(state="normal")

        except Exception:
            pass


if __name__ == "__main__":
    root = tki.Tk()
    app = GPSApp(root)
    root.mainloop()
