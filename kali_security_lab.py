#!/usr/bin/env python3
"""
Kali Security Lab
Safe training GUI:
- Local login brute-force simulation against an in-process mock account.
- Wi-Fi discovery/assessment using nmcli (no password cracking or attacks).
- Clear authorization/lab-use boundary.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import subprocess
import threading
import time
import hashlib
import socket
import re

APP_TITLE = "Kali Security Lab — Safe Training"
DEFAULT_USER = "admin"
DEFAULT_PASSWORD = "KaliLab!2026"

class KaliSecurityLab(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x620")
        self.minsize(760, 520)
        self.create_ui()

    def create_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=12)

        login = ttk.Frame(nb, padding=14)
        wifi = ttk.Frame(nb, padding=14)
        nb.add(login, text="Login Lab")
        nb.add(wifi, text="Wi-Fi Audit")

        # Login lab
        ttk.Label(login, text="Local Login Brute-Force Simulation",
                  font=("TkDefaultFont", 15, "bold")).pack(anchor="w")
        ttk.Label(login, text=(
            "This tests only the built-in mock account. It does not send "
            "credentials to websites, SSH, FTP, or other real services."
        ), wraplength=820).pack(anchor="w", pady=(4, 12))

        form = ttk.Frame(login)
        form.pack(fill="x")

        ttk.Label(form, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.user_var = tk.StringVar(value=DEFAULT_USER)
        ttk.Entry(form, textvariable=self.user_var, width=34).grid(row=0, column=1, sticky="w", pady=5)

        ttk.Label(form, text="Password file:").grid(row=1, column=0, sticky="w", pady=5)
        self.passfile_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.passfile_var, width=55).grid(row=1, column=1, sticky="w", pady=5)
        ttk.Button(form, text="Browse", command=self.browse_passfile).grid(row=1, column=2, padx=8)

        ttk.Button(login, text="Run Local Lab Test", command=self.start_login_test).pack(anchor="w", pady=12)

        self.login_progress = ttk.Progressbar(login, mode="determinate")
        self.login_progress.pack(fill="x")

        self.login_output = tk.Text(login, height=19, wrap="word")
        self.login_output.pack(fill="both", expand=True, pady=(10, 0))

        # Wi-Fi audit
        ttk.Label(wifi, text="Wi-Fi Discovery / Security Audit",
                  font=("TkDefaultFont", 15, "bold")).pack(anchor="w")
        ttk.Label(wifi, text=(
            "Discovers networks visible to your machine and reports SSID, "
            "signal, channel and security information. It intentionally "
            "does not deauthenticate clients, capture handshakes, crack "
            "passwords, or attempt unauthorized access."
        ), wraplength=820).pack(anchor="w", pady=(4, 12))

        controls = ttk.Frame(wifi)
        controls.pack(fill="x")
        ttk.Button(
            controls,
            text="Scan Wi-Fi",
            command=self.start_wifi_scan
        ).pack(side="left")

        ttk.Button(
            controls,
            text="My Network Devices",
            command=self.start_network_devices
        ).pack(side="left", padx=8)

        ttk.Button(
            controls,
            text="Clear",
            command=lambda: self.wifi_output.delete("1.0", "end")
        ).pack(side="left", padx=8)

        self.wifi_output = tk.Text(wifi, height=25, wrap="none")
        self.wifi_output.pack(fill="both", expand=True, pady=(10, 0))

        ttk.Label(self, text="Use only on systems and networks you own or are explicitly authorized to test.",
                  anchor="center").pack(fill="x", padx=12, pady=(0, 8))

    def browse_passfile(self):
        path = filedialog.askopenfilename(
            title="Select password list",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self.passfile_var.set(path)

    def log_login(self, text):
        self.login_output.insert("end", text + "\n")
        self.login_output.see("end")
        self.update_idletasks()

    def start_login_test(self):
        path = self.passfile_var.get().strip()
        username = self.user_var.get().strip()

        if not username:
            messagebox.showerror("Input error", "Enter the lab username.")
            return
        if not path or not Path(path).is_file():
            messagebox.showerror("Input error", "Choose a valid password .txt file.")
            return

        self.login_output.delete("1.0", "end")
        self.login_progress["value"] = 0
        threading.Thread(target=self.login_test, args=(username, path), daemon=True).start()

    def login_test(self, username, path):
        # Only this locally defined mock account is tested.
        expected_hash = hashlib.sha256(DEFAULT_PASSWORD.encode()).hexdigest()

        try:
            passwords = Path(path).read_text(errors="replace").splitlines()
        except OSError as exc:
            self.after(0, self.log_login, f"Could not read file: {exc}")
            return

        passwords = [p.strip() for p in passwords if p.strip()]
        total = len(passwords)

        self.after(0, self.log_login, f"Lab target: local mock account '{DEFAULT_USER}'")
        self.after(0, self.log_login, f"Loaded {total} candidate password(s).")
        self.after(0, self.log_login, "No network connection is used.\n")

        for i, candidate in enumerate(passwords, 1):
            time.sleep(0.04)  # makes the lab visible in the GUI
            ok = (
                username == DEFAULT_USER and
                hashlib.sha256(candidate.encode()).hexdigest() == expected_hash
            )
            self.after(0, self.login_progress.configure, {"value": i / max(total, 1) * 100})

            if ok:
                self.after(0, self.log_login,
                           f"[+] MATCH after {i} attempt(s): {candidate}")
                self.after(0, self.log_login, "Lab simulation complete.")
                return

            self.after(0, self.log_login, f"[-] Attempt {i}/{total}: rejected")

        self.after(0, self.log_login, "\n[-] No match found in the supplied lab wordlist.")
        self.after(0, self.log_login,
                   f"Hint for this lab: the mock password is '{DEFAULT_PASSWORD}'.")

    def start_wifi_scan(self):
        self.wifi_output.delete("1.0", "end")
        threading.Thread(target=self.wifi_scan, daemon=True).start()

    def wifi_scan(self):
        self.after(0, self.wifi_log, "Scanning nearby Wi-Fi networks...\n")

        try:
            # Windows Wi-Fi discovery
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20
            )

            if result.returncode != 0:
                error = result.stderr.strip() or result.stdout.strip()
                self.after(
                    0,
                    self.wifi_log,
                    f"Wi-Fi scan failed:\n{error}"
                )
                return

            output = result.stdout.strip()

            if not output:
                self.after(
                    0,
                    self.wifi_log,
                    "No nearby Wi-Fi networks were reported."
                )
                return

            # Display Windows' complete Wi-Fi discovery result.
            self.after(0, self.wifi_log, output)

            self.after(
                0,
                self.wifi_log,
                "\n----------------------------------------\n"
                "Scan complete.\n"
                "This is Wi-Fi discovery only; no authentication,\n"
                "deauthentication, handshake capture, or password\n"
                "cracking is performed."
            )

        except subprocess.TimeoutExpired:
            self.after(
                0,
                self.wifi_log,
                "Wi-Fi scan timed out."
            )

        except FileNotFoundError:
            self.after(
                0,
                self.wifi_log,
                "Windows 'netsh' command was not found."
            )

        except Exception as exc:
            self.after(
                0,
                self.wifi_log,
                f"Wi-Fi scan error: {exc}"
            )

    def start_network_devices(self):
        self.wifi_output.delete("1.0", "end")
        threading.Thread(
            target=self.network_devices_scan,
            daemon=True
        ).start()

    def network_devices_scan(self):
        self.after(
            0,
            self.wifi_log,
            "Scanning devices visible on your local network...\n"
        )

        try:
            # Get this computer's hostname
            local_hostname = socket.gethostname()

            # Get local IPv4 address
            local_ip = socket.gethostbyname(local_hostname)

            # Get ARP table from Windows
            result = subprocess.run(
                ["arp", "-a"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise RuntimeError(
                    result.stderr.strip() or "ARP command failed"
                )

            entries = []

            # Match Windows ARP lines such as:
            # 192.168.1.1    8c-13-e2-50-e8-3a    dynamic
            pattern = re.compile(
                r"^\s*(\d+\.\d+\.\d+\.\d+)\s+"
                r"([0-9a-fA-F-]{17})\s+"
                r"(\w+)\s*$"
            )

            for line in result.stdout.splitlines():
                match = pattern.match(line)

                if not match:
                    continue

                ip = match.group(1)
                mac = match.group(2)
                entry_type = match.group(3)

                # Ignore broadcast/multicast addresses
                first_octet = int(ip.split(".")[0])

                if first_octet >= 224:
                    continue

                # Ignore broadcast MAC
                if mac.lower() == "ff-ff-ff-ff-ff-ff":
                    continue

                entries.append((ip, mac, entry_type))

            # Remove duplicates
            entries = list(dict.fromkeys(entries))

            # Find default gateway
            gateway_ip = None

            gateway_result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Look for Default Gateway
            gateway_matches = re.findall(
                r"Default Gateway[ .:]*:\s*(\d+\.\d+\.\d+\.\d+)",
                gateway_result.stdout,
                re.IGNORECASE
            )

            if gateway_matches:
                gateway_ip = gateway_matches[0]

            # Header
            self.after(
                0,
                self.wifi_log,
                "DEVICE / HOSTNAME       IP ADDRESS        MAC ADDRESS           TYPE"
            )

            self.after(
                0,
                self.wifi_log,
                "-" * 78
            )

            # Show this computer first
            self.after(
                0,
                self.wifi_log,
                f"{local_hostname:<24} "
                f"{local_ip:<17} "
                f"{'This PC':<22} "
                f"local"
            )

            # Display discovered local devices
            for ip, mac, entry_type in entries:

                # Don't show this PC twice
                if ip == local_ip:
                    continue

                # Default gateway
                if gateway_ip and ip == gateway_ip:
                    device_name = "Gateway / Hotspot"
                else:
                    # Try reverse DNS / hostname lookup
                    try:
                        device_name = socket.gethostbyaddr(ip)[0]
                    except (socket.herror, socket.gaierror, OSError):
                        device_name = "Unknown device"

                self.after(
                    0,
                    self.wifi_log,
                    f"{device_name:<24} "
                    f"{ip:<17} "
                    f"{mac:<22} "
                    f"{entry_type}"
                )

            self.after(
                0,
                self.wifi_log,
                "\nNotes:"
            )

            self.after(
                0,
                self.wifi_log,
                "- 'This PC' is your Windows computer."
            )

            self.after(
                0,
                self.wifi_log,
                "- 'Gateway / Hotspot' is the detected default gateway."
            )

            self.after(
                0,
                self.wifi_log,
                "- Unknown device means Windows could not resolve a hostname."
            )

            self.after(
                0,
                self.wifi_log,
                "- ARP shows devices Windows has learned about; it is not "
                "guaranteed to contain every connected device."
            )

        except FileNotFoundError:
            self.after(
                0,
                self.wifi_log,
                "Windows ARP/ipconfig commands could not be found."
            )

        except Exception as exc:
            self.after(
                0,
                self.wifi_log,
                f"Network device scan error: {exc}"
            )

    def wifi_log(self, text):
        self.wifi_output.insert("end", text + "\n")
        self.wifi_output.see("end")

if __name__ == "__main__":
    KaliSecurityLab().mainloop()
