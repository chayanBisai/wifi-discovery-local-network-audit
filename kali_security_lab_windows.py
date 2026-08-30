#!/usr/bin/env python3
"""
Kali Security Lab — Windows Safe Training

Windows Wi-Fi discovery + local-network inventory.
Uses Windows' built-in `netsh wlan` and ARP information.

This program performs discovery only:
- No Wi-Fi authentication attempts
- No deauthentication
- No handshake capture
- No password cracking
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import subprocess
import threading
import time
import hashlib
import re
import socket
import ipaddress

APP_TITLE = "Kali Security Lab — Windows Safe Training"
DEFAULT_USER = "admin"
DEFAULT_PASSWORD = "KaliLab!2026"


class KaliSecurityLab(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1000x700")
        self.minsize(820, 580)
        self.create_ui()

    def create_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=12)

        login = ttk.Frame(nb, padding=14)
        wifi = ttk.Frame(nb, padding=14)
        nb.add(login, text="Login Lab")
        nb.add(wifi, text="Wi-Fi Audit")

        ttk.Label(
            login, text="Local Login Brute-Force Simulation",
            font=("TkDefaultFont", 15, "bold")
        ).pack(anchor="w")

        ttk.Label(
            login,
            text=("This tests only the built-in mock account. It does not send "
                  "credentials to websites, SSH, FTP, or other real services."),
            wraplength=900
        ).pack(anchor="w", pady=(4, 12))

        form = ttk.Frame(login)
        form.pack(fill="x")

        ttk.Label(form, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.user_var = tk.StringVar(value=DEFAULT_USER)
        ttk.Entry(form, textvariable=self.user_var, width=34).grid(
            row=0, column=1, sticky="w", pady=5
        )

        ttk.Label(form, text="Password file:").grid(row=1, column=0, sticky="w", pady=5)
        self.passfile_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.passfile_var, width=55).grid(
            row=1, column=1, sticky="w", pady=5
        )
        ttk.Button(form, text="Browse", command=self.browse_passfile).grid(
            row=1, column=2, padx=8
        )

        ttk.Button(
            login, text="Run Local Lab Test",
            command=self.start_login_test
        ).pack(anchor="w", pady=12)

        self.login_progress = ttk.Progressbar(login, mode="determinate")
        self.login_progress.pack(fill="x")

        self.login_output = tk.Text(login, height=19, wrap="word")
        self.login_output.pack(fill="both", expand=True, pady=(10, 0))

        # Wi-Fi audit
        ttk.Label(
            wifi, text="Windows Wi-Fi Discovery / Local Network Audit",
            font=("TkDefaultFont", 15, "bold")
        ).pack(anchor="w")

        ttk.Label(
            wifi,
            text=("Uses Windows WLAN discovery to show nearby access points and "
                  "Windows ARP information to show locally learned devices. "
                  "Nearby APs and LAN devices are separate inventories."),
            wraplength=920
        ).pack(anchor="w", pady=(4, 12))

        controls = ttk.Frame(wifi)
        controls.pack(fill="x")

        ttk.Button(
            controls, text="Scan Nearby Wi-Fi",
            command=self.start_wifi_scan
        ).pack(side="left")

        ttk.Button(
            controls, text="Scan My Local Network",
            command=self.start_local_scan
        ).pack(side="left", padx=8)

        ttk.Button(
            controls, text="Clear",
            command=self.clear_wifi_output
        ).pack(side="left")

        self.wifi_output = tk.Text(wifi, height=28, wrap="none")
        self.wifi_output.pack(fill="both", expand=True, pady=(10, 0))

        ttk.Label(
            self,
            text=("Use only on systems and networks you own or are explicitly "
                  "authorized to test."),
            anchor="center"
        ).pack(fill="x", padx=12, pady=(0, 8))

    def browse_passfile(self):
        path = filedialog.askopenfilename(
            title="Select password list",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self.passfile_var.set(path)

    def clear_wifi_output(self):
        self.wifi_output.delete("1.0", "end")

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

        threading.Thread(
            target=self.login_test,
            args=(username, path),
            daemon=True
        ).start()

    def login_test(self, username, path):
        expected_hash = hashlib.sha256(DEFAULT_PASSWORD.encode()).hexdigest()

        try:
            passwords = Path(path).read_text(errors="replace").splitlines()
        except OSError as exc:
            self.after(0, self.log_login, f"Could not read file: {exc}")
            return

        passwords = [p.strip() for p in passwords if p.strip()]
        total = len(passwords)

        self.after(
            0, self.log_login,
            f"Lab target: local mock account '{DEFAULT_USER}'"
        )
        self.after(0, self.log_login, f"Loaded {total} candidate password(s).")
        self.after(0, self.log_login, "No network connection is used.\n")

        for i, candidate in enumerate(passwords, 1):
            time.sleep(0.04)

            ok = (
                username == DEFAULT_USER and
                hashlib.sha256(candidate.encode()).hexdigest() == expected_hash
            )

            self.after(
                0,
                self.login_progress.configure,
                {"value": i / max(total, 1) * 100}
            )

            if ok:
                self.after(
                    0, self.log_login,
                    f"[+] MATCH after {i} attempt(s): {candidate}"
                )
                self.after(0, self.log_login, "Lab simulation complete.")
                return

            self.after(
                0, self.log_login,
                f"[-] Attempt {i}/{total}: rejected"
            )

        self.after(
            0, self.log_login,
            "\n[-] No match found in the supplied lab wordlist."
        )
        self.after(
            0, self.log_login,
            f"Hint for this lab: the mock password is '{DEFAULT_PASSWORD}'."
        )

    # ---------------- Windows command helpers ----------------

    @staticmethod
    def run_command(command, timeout=30):
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False
        )
        return result.stdout, result.stderr, result.returncode

    @staticmethod
    def parse_netsh_wifi(text):
        """
        Parse `netsh wlan show networks mode=bssid`.

        Important:
        - Only an exact `Channel:` line is accepted.
        - `Channel Utilization:` is NOT treated as the channel.
        """
        networks = []
        current_ssid = None
        current = None

        lines = text.splitlines()

        def finish():
            nonlocal current
            if current and current.get("bssid"):
                networks.append(current)
            current = None

        for raw in lines:
            line = raw.strip()

            if not line:
                continue

            # SSID line: "SSID 1 : S2-5G"
            m = re.match(r"^SSID\s+\d+\s*:\s*(.*)$", line, re.I)
            if m:
                finish()
                current_ssid = m.group(1).strip() or "<hidden>"
                current = {
                    "ssid": current_ssid,
                    "bssid": "",
                    "signal": "",
                    "radio": "",
                    "band": "",
                    "channel": "",
                    "authentication": "",
                    "encryption": "",
                }
                continue

            if current is None:
                continue

            m = re.match(r"^BSSID\s+\d+\s*:\s*(.+)$", line, re.I)
            if m:
                # One SSID can contain multiple BSSIDs.
                if current.get("bssid"):
                    networks.append(current)
                    current = {
                        "ssid": current_ssid,
                        "bssid": "",
                        "signal": "",
                        "radio": "",
                        "band": "",
                        "channel": "",
                        "authentication": "",
                        "encryption": "",
                    }
                current["bssid"] = m.group(1).strip()
                continue

            m = re.match(r"^Signal\s*:\s*(.+)$", line, re.I)
            if m:
                current["signal"] = m.group(1).strip()
                continue

            m = re.match(r"^Radio type\s*:\s*(.+)$", line, re.I)
            if m:
                current["radio"] = m.group(1).strip()
                continue

            m = re.match(r"^Band\s*:\s*(.+)$", line, re.I)
            if m:
                current["band"] = m.group(1).strip()
                continue

            # EXACT Channel line — deliberately excludes Channel Utilization.
            m = re.match(r"^Channel\s*:\s*(.+)$", line, re.I)
            if m:
                current["channel"] = m.group(1).strip()
                continue

            m = re.match(r"^Authentication\s*:\s*(.+)$", line, re.I)
            if m:
                current["authentication"] = m.group(1).strip()
                continue

            m = re.match(r"^Encryption\s*:\s*(.+)$", line, re.I)
            if m:
                current["encryption"] = m.group(1).strip()
                continue

        finish()

        # Deduplicate by BSSID while preserving order.
        unique = {}
        for n in networks:
            key = n["bssid"].lower()
            if key not in unique:
                unique[key] = n

        return list(unique.values())

    def get_current_connection(self):
        stdout, stderr, code = self.run_command(
            ["netsh", "wlan", "show", "interfaces"],
            timeout=20
        )

        info = {
            "ssid": "",
            "bssid": "",
            "signal": "",
            "ip": "",
            "hostname": socket.gethostname(),
            "gateway": "",
            "subnet": "",
        }

        if code != 0:
            return info

        for raw in stdout.splitlines():
            line = raw.strip()
            if ":" not in line:
                continue

            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()

            if key == "ssid":
                info["ssid"] = value
            elif key == "ap bssid":
                info["bssid"] = value
            elif key == "signal":
                info["signal"] = value

        # Get IPv4 configuration.
        out, _, rc = self.run_command(
            ["ipconfig"],
            timeout=20
        )

        if rc == 0:
            in_wifi = False
            for raw in out.splitlines():
                line = raw.strip()

                if line.endswith("Wi-Fi:"):
                    in_wifi = True
                    continue

                if in_wifi and line and not raw.startswith(" "):
                    in_wifi = False

                if in_wifi:
                    m = re.search(r"IPv4 Address[.\s]*:\s*(\d+\.\d+\.\d+\.\d+)", line)
                    if m:
                        info["ip"] = m.group(1)

        return info

    def start_wifi_scan(self):
        self.clear_wifi_output()
        threading.Thread(target=self.wifi_scan, daemon=True).start()

    def wifi_scan(self):
        self.after(
            0, self.wifi_log,
            "Scanning nearby Wi-Fi networks using Windows WLAN...\n"
        )

        try:
            # Ask Windows to initiate a fresh scan.
            _, stderr, code = self.run_command(
                ["netsh", "wlan", "scan", "interface=Wi-Fi"],
                timeout=30
            )

            if code != 0:
                self.after(
                    0, self.wifi_log,
                    "Windows scan request returned an error: "
                    + (stderr.strip() or "unknown error")
                )

            # Give the WLAN service/adapter time to populate results.
            time.sleep(5)

            # Perform several read passes and merge BSSIDs.
            merged = {}

            for round_no in range(1, 4):
                stdout, stderr, code = self.run_command(
                    ["netsh", "wlan", "show", "networks", "mode=bssid"],
                    timeout=30
                )

                if code == 0:
                    found = self.parse_netsh_wifi(stdout)

                    for item in found:
                        key = item["bssid"].lower()
                        if key not in merged:
                            merged[key] = item
                        else:
                            # Fill fields that may be absent in one pass.
                            for field in item:
                                if not merged[key].get(field) and item.get(field):
                                    merged[key][field] = item[field]

                    self.after(
                        0, self.wifi_log,
                        f"Scan pass {round_no}: Windows reported {len(found)} BSSID(s)."
                    )

                if round_no < 3:
                    time.sleep(2)

            networks = list(merged.values())

            current = self.get_current_connection()

            self.after(
                0, self.wifi_log,
                "\nNEARBY WI-FI NETWORKS"
            )
            self.after(
                0, self.wifi_log,
                "=" * 100
            )
            self.after(
                0, self.wifi_log,
                f"Current SSID       : {current['ssid'] or 'Not connected'}"
            )
            self.after(
                0, self.wifi_log,
                f"Current AP BSSID   : {current['bssid'] or 'Unknown'}"
            )
            self.after(
                0, self.wifi_log,
                f"Current Signal     : {current['signal'] or 'Unknown'}"
            )
            self.after(
                0, self.wifi_log,
                f"\nUnique BSSIDs seen across 3 scans: {len(networks)}\n"
            )

            header = (
                f"{'SSID':30} {'BSSID':20} {'SIGNAL':8} "
                f"{'CHANNEL':9} {'BAND':8} SECURITY"
            )
            self.after(0, self.wifi_log, header)
            self.after(0, self.wifi_log, "-" * 120)

            if not networks:
                self.after(
                    0, self.wifi_log,
                    "Windows did not report any nearby access points."
                )
            else:
                for n in sorted(
                    networks,
                    key=lambda x: (
                        x.get("ssid", "").lower(),
                        x.get("bssid", "").lower()
                    )
                ):
                    security = (
                        f"{n['authentication']} / {n['encryption']}"
                        if n["authentication"] or n["encryption"]
                        else "Unknown"
                    )

                    row = (
                        f"{n['ssid'][:30]:30} "
                        f"{n['bssid']:20} "
                        f"{n['signal'][:8]:8} "
                        f"{n['channel'][:9]:9} "
                        f"{n['band'][:8]:8} "
                        f"{security}"
                    )
                    self.after(0, self.wifi_log, row)

            self.after(0, self.wifi_log, "\n" + "-" * 120)
            self.after(
                0, self.wifi_log,
                "Note: this is Windows WLAN discovery. A scan can temporarily "
                "miss an AP because of driver, radio, channel, signal, or OS behavior."
            )
            self.after(
                0, self.wifi_log,
                "Discovery only: no authentication, deauthentication, handshake "
                "capture, or password cracking is performed."
            )

        except FileNotFoundError:
            self.after(
                0, self.wifi_log,
                "netsh was not found. This program requires Windows."
            )
        except Exception as exc:
            self.after(
                0, self.wifi_log,
                f"Wi-Fi scan error: {exc}"
            )

    def start_local_scan(self):
        self.clear_wifi_output()
        threading.Thread(target=self.local_network_scan, daemon=True).start()

    def local_network_scan(self):
        self.after(
            0, self.wifi_log,
            "Scanning devices visible on your local Windows network...\n"
        )

        try:
            current = self.get_current_connection()

            hostname = current["hostname"]
            local_ip = current["ip"]

            # Read Windows ARP cache.
            stdout, stderr, code = self.run_command(
                ["arp", "-a"],
                timeout=20
            )

            entries = []

            if code == 0:
                for raw in stdout.splitlines():
                    line = raw.strip()

                    m = re.match(
                        r"^(\d+\.\d+\.\d+\.\d+)\s+"
                        r"([0-9a-fA-F:-]{17})\s+"
                        r"(\w+)$",
                        line
                    )

                    if not m:
                        continue

                    ip = m.group(1)
                    mac = m.group(2).replace(":", "-").upper()
                    typ = m.group(3).lower()

                    # Exclude broadcast/multicast addresses.
                    if ipaddress.ip_address(ip).is_multicast:
                        continue
                    if ip == "255.255.255.255":
                        continue
                    if mac == "FF-FF-FF-FF-FF-FF":
                        continue

                    entries.append((ip, mac, typ))

            # Deduplicate.
            unique = {}
            for ip, mac, typ in entries:
                unique[ip] = (ip, mac, typ)

            entries = list(unique.values())

            self.after(
                0, self.wifi_log,
                "MY LOCAL NETWORK"
            )
            self.after(
                0, self.wifi_log,
                "=" * 100
            )
            self.after(
                0, self.wifi_log,
                f"\nWi-Fi SSID        : {current['ssid'] or 'Unknown'}"
            )
            self.after(
                0, self.wifi_log,
                f"Access Point BSSID: {current['bssid'] or 'Unknown'}"
            )
            self.after(
                0, self.wifi_log,
                f"Computer hostname : {hostname}"
            )
            self.after(
                0, self.wifi_log,
                f"Computer IP       : {local_ip or 'Unknown'}"
            )

            gateway = self.find_gateway()
            subnet = self.calculate_subnet(local_ip)

            self.after(
                0, self.wifi_log,
                f"Subnet            : {subnet or 'Unknown'}"
            )
            self.after(
                0, self.wifi_log,
                f"Gateway           : {gateway or 'Unknown'}\n"
            )

            self.after(
                0, self.wifi_log,
                f"{'DEVICE / HOSTNAME':28} {'IP ADDRESS':17} "
                f"{'MAC ADDRESS':20} TYPE"
            )
            self.after(0, self.wifi_log, "-" * 100)

            if local_ip:
                self.after(
                    0, self.wifi_log,
                    f"{hostname[:28]:28} {local_ip:17} "
                    f"{self.get_local_mac():20} THIS PC"
                )

            if gateway:
                gateway_mac = next(
                    (mac for ip, mac, typ in entries if ip == gateway),
                    "Unknown"
                )
                self.after(
                    0, self.wifi_log,
                    f"{'Gateway / Router':28} {gateway:17} "
                    f"{gateway_mac:20} GATEWAY"
                )

            for ip, mac, typ in entries:
                if ip == local_ip or ip == gateway:
                    continue

                host = self.resolve_hostname(ip)

                self.after(
                    0, self.wifi_log,
                    f"{host[:28]:28} {ip:17} {mac:20} LOCAL DEVICE"
                )

            self.after(0, self.wifi_log, "\n" + "-" * 100)
            self.after(
                0, self.wifi_log,
                f"ARP entries discovered: {len(entries)}"
            )
            self.after(
                0, self.wifi_log,
                "\nImportant:"
            )
            self.after(
                0, self.wifi_log,
                "• BSSID identifies the Wi-Fi access point."
            )
            self.after(
                0, self.wifi_log,
                "• Client devices have their own MAC addresses."
            )
            self.after(
                0, self.wifi_log,
                "• ARP does not guarantee that every connected device appears."
            )
            self.after(
                0, self.wifi_log,
                "• Nearby Wi-Fi networks are not the same as devices on your LAN."
            )

        except Exception as exc:
            self.after(
                0, self.wifi_log,
                f"Local network scan error: {exc}"
            )

    def find_gateway(self):
        stdout, stderr, code = self.run_command(
            ["ipconfig"],
            timeout=20
        )

        if code != 0:
            return ""

        in_wifi = False

        for raw in stdout.splitlines():
            line = raw.strip()

            if line.endswith("Wi-Fi:"):
                in_wifi = True
                continue

            if in_wifi and line and not raw.startswith(" "):
                in_wifi = False

            if in_wifi:
                m = re.search(
                    r"Default Gateway[.\s]*:\s*(\d+\.\d+\.\d+\.\d+)",
                    line
                )
                if m:
                    return m.group(1)

        return ""

    @staticmethod
    def calculate_subnet(local_ip):
        try:
            # Most home Windows networks use /24. Use it only as a
            # display approximation when the exact prefix isn't available.
            return str(ipaddress.ip_network(local_ip + "/24", strict=False))
        except Exception:
            return ""

    def get_local_mac(self):
        stdout, stderr, code = self.run_command(
            ["getmac", "/fo", "csv", "/nh"],
            timeout=20
        )

        if code != 0:
            return "Unknown"

        for line in stdout.splitlines():
            parts = [p.strip('"') for p in line.split(",")]
            if parts and re.match(
                r"^[0-9A-Fa-f]{2}(-[0-9A-Fa-f]{2}){5}$",
                parts[0]
            ):
                return parts[0].upper()

        return "Unknown"

    @staticmethod
    def resolve_hostname(ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return "Unknown"

    def wifi_log(self, text):
        self.wifi_output.insert("end", text + "\n")
        self.wifi_output.see("end")


if __name__ == "__main__":
    KaliSecurityLab().mainloop()
