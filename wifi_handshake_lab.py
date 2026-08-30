import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import re
import socket
import ipaddress


APP_TITLE = "Wi-Fi Security Lab — Windows Authorized Audit"
SCAN_ROUNDS = 3
SCAN_DELAY = 2


class WiFiSecurityLab(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("1100x720")
        self.minsize(900, 600)

        self.scanning = False
        self.create_ui()

    # =========================================================
    # GUI
    # =========================================================

    def create_ui(self):

        title = ttk.Label(
            self,
            text="Wi-Fi Security Lab",
            font=("Segoe UI", 18, "bold")
        )
        title.pack(pady=(12, 2))

        subtitle = ttk.Label(
            self,
            text=(
                "Real Windows Wi-Fi discovery and authorized local-network "
                "device auditing"
            )
        )
        subtitle.pack(pady=(0, 10))

        buttons = ttk.Frame(self)
        buttons.pack(fill="x", padx=12, pady=5)

        self.nearby_button = ttk.Button(
            buttons,
            text="Scan Nearby Wi-Fi",
            command=self.start_wifi_scan
        )
        self.nearby_button.pack(side="left", padx=5)

        self.local_button = ttk.Button(
            buttons,
            text="Scan My Network",
            command=self.start_local_scan
        )
        self.local_button.pack(side="left", padx=5)

        self.current_button = ttk.Button(
            buttons,
            text="Current Wi-Fi",
            command=self.show_current_wifi
        )
        self.current_button.pack(side="left", padx=5)

        self.clear_button = ttk.Button(
            buttons,
            text="Clear",
            command=self.clear_output
        )
        self.clear_button.pack(side="left", padx=5)

        self.status = ttk.Label(
            self,
            text="Ready",
            anchor="w"
        )
        self.status.pack(fill="x", padx=15, pady=5)

        self.output = tk.Text(
            self,
            wrap="none",
            font=("Consolas", 10)
        )
        self.output.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=8
        )

        scrollbar_y = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.output.yview
        )
        scrollbar_y.place(
            relx=0.985,
            rely=0.17,
            relheight=0.76
        )

        self.output.configure(
            yscrollcommand=scrollbar_y.set
        )

        footer = ttk.Label(
            self,
            text=(
                "Authorized discovery only — no deauthentication, "
                "credential capture, or password cracking."
            ),
            anchor="center"
        )
        footer.pack(fill="x", padx=12, pady=(0, 8))

        self.write(
            "Wi-Fi Security Lab\n"
            "==================\n\n"
            "This program uses your real Windows Wi-Fi adapter.\n\n"
            "Choose an operation above.\n"
        )

    # =========================================================
    # Output
    # =========================================================

    def write(self, text):

        self.output.delete("1.0", "end")
        self.output.insert("end", text)
        self.output.see("end")

    def clear_output(self):

        self.output.delete("1.0", "end")
        self.status.config(text="Ready")

    def set_status(self, text):

        self.after(
            0,
            lambda: self.status.config(text=text)
        )

    # =========================================================
    # Command runner
    # =========================================================

    def run_command(self, command, timeout=30):

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )

            return result.stdout, result.stderr, result.returncode

        except subprocess.TimeoutExpired:

            return "", "Command timed out", 1

        except Exception as exc:

            return "", str(exc), 1

    # =========================================================
    # Current Wi-Fi
    # =========================================================

    def get_current_wifi(self):

        stdout, stderr, code = self.run_command(
            ["netsh", "wlan", "show", "interfaces"]
        )

        info = {
            "name": "",
            "description": "",
            "ssid": "",
            "bssid": "",
            "signal": "",
            "rssi": "",
            "radio": "",
            "channel": "",
            "band": "",
            "authentication": "",
            "cipher": "",
            "state": "",
            "receive": "",
            "transmit": ""
        }

        for raw in stdout.splitlines():

            line = raw.strip()

            if ":" not in line:
                continue

            key, value = line.split(":", 1)

            key = key.strip()
            value = value.strip()

            if key == "Name":
                info["name"] = value

            elif key == "Description":
                info["description"] = value

            elif key == "SSID":
                info["ssid"] = value

            elif key == "AP BSSID":
                info["bssid"] = value

            elif key == "Signal":
                info["signal"] = value

            elif key == "Rssi":
                info["rssi"] = value

            elif key == "Radio type":
                info["radio"] = value

            elif key == "Channel":
                info["channel"] = value

            elif key == "Band":
                info["band"] = value

            elif key == "Authentication":
                info["authentication"] = value

            elif key == "Cipher":
                info["cipher"] = value

            elif key == "State":
                info["state"] = value

            elif key == "Receive rate (Mbps)":
                info["receive"] = value

            elif key == "Transmit rate (Mbps)":
                info["transmit"] = value

        return info

    def show_current_wifi(self):

        self.status.config(text="Reading current Wi-Fi connection...")

        thread = threading.Thread(
            target=self.current_wifi_worker,
            daemon=True
        )

        thread.start()

    def current_wifi_worker(self):

        info = self.get_current_wifi()

        output = []

        output.append("CURRENT WI-FI CONNECTION")
        output.append("=" * 70)
        output.append("")

        fields = [
            ("Interface", info["name"]),
            ("Adapter", info["description"]),
            ("State", info["state"]),
            ("SSID", info["ssid"]),
            ("AP BSSID", info["bssid"]),
            ("Signal", info["signal"]),
            ("RSSI", info["rssi"]),
            ("Band", info["band"]),
            ("Channel", info["channel"]),
            ("Radio", info["radio"]),
            ("Authentication", info["authentication"]),
            ("Cipher", info["cipher"]),
            ("Receive rate", info["receive"]),
            ("Transmit rate", info["transmit"]),
        ]

        for key, value in fields:

            output.append(
                f"{key:20}: {value or 'Unknown'}"
            )

        output.append("")
        output.append("-" * 70)
        output.append(
            "These values come directly from Windows WLAN information."
        )

        self.after(
            0,
            lambda: self.finish(
                "\n".join(output),
                "Current Wi-Fi information retrieved"
            )
        )

    # =========================================================
    # Nearby Wi-Fi scanning
    # =========================================================

    def start_wifi_scan(self):

        if self.scanning:
            return

        self.scanning = True

        self.nearby_button.config(state="disabled")
        self.local_button.config(state="disabled")
        self.current_button.config(state="disabled")

        self.write(
            "Scanning nearby Wi-Fi networks...\n\n"
            f"Performing {SCAN_ROUNDS} Windows WLAN scans.\n"
            "This may take several seconds.\n"
        )

        self.status.config(
            text="Scanning nearby Wi-Fi..."
        )

        thread = threading.Thread(
            target=self.wifi_scan_worker,
            daemon=True
        )

        thread.start()

    def parse_wifi_scan(self, text):

        networks = []

        current = None
        current_bssid = None

        for raw in text.splitlines():

            line = raw.strip()

            # New SSID
            match = re.match(
                r"SSID\s+\d+\s*:\s*(.*)",
                line,
                re.IGNORECASE
            )

            if match:

                if current and current_bssid:

                    current["bssid"] = current_bssid
                    networks.append(current)

                current = {
                    "ssid": match.group(1).strip(),
                    "authentication": "",
                    "encryption": "",
                    "signal": "",
                    "radio": "",
                    "band": "",
                    "channel": "",
                    "bssid": ""
                }

                current_bssid = None
                continue

            if not current:
                continue

            # BSSID
            match = re.match(
                r"BSSID\s+\d+\s*:\s*([0-9a-fA-F:-]{17})",
                line,
                re.IGNORECASE
            )

            if match:

                current_bssid = match.group(1)
                continue

            if line.lower().startswith("authentication"):

                if ":" in line:
                    current["authentication"] = \
                        line.split(":", 1)[1].strip()

            elif line.lower().startswith("encryption"):

                if ":" in line:
                    current["encryption"] = \
                        line.split(":", 1)[1].strip()

            elif line.lower().startswith("signal"):

                if ":" in line:
                    current["signal"] = \
                        line.split(":", 1)[1].strip()

            elif line.lower().startswith("radio type"):

                if ":" in line:
                    current["radio"] = \
                        line.split(":", 1)[1].strip()

            elif line.lower().startswith("band"):

                if ":" in line:
                    current["band"] = \
                        line.split(":", 1)[1].strip()

            elif line.lower().startswith("channel"):

                if ":" in line:
                    current["channel"] = \
                        line.split(":", 1)[1].strip()

        # Last network
        if current and current_bssid:

            current["bssid"] = current_bssid
            networks.append(current)

        return networks

    def wifi_scan_once(self):

        stdout, stderr, code = self.run_command(
            [
                "netsh",
                "wlan",
                "show",
                "networks",
                "mode=bssid"
            ],
            timeout=30
        )

        if code != 0:

            return []

        return self.parse_wifi_scan(stdout)

    def wifi_scan_worker(self):

        combined = {}

        for round_number in range(
            1,
            SCAN_ROUNDS + 1
        ):

            self.set_status(
                f"Wi-Fi scan {round_number}/{SCAN_ROUNDS}..."
            )

            results = self.wifi_scan_once()

            for network in results:

                bssid = network["bssid"].lower()

                if not bssid:
                    continue

                combined[bssid] = network

            if round_number < SCAN_ROUNDS:

                time.sleep(SCAN_DELAY)

        current = self.get_current_wifi()

        output = []

        output.append("NEARBY WI-FI NETWORKS")
        output.append("=" * 100)
        output.append("")

        output.append(
            f"Current SSID       : "
            f"{current['ssid'] or 'Not connected'}"
        )

        output.append(
            f"Current AP BSSID   : "
            f"{current['bssid'] or 'Unknown'}"
        )

        output.append(
            f"Current Signal     : "
            f"{current['signal'] or 'Unknown'}"
        )

        output.append("")

        output.append(
            f"Unique BSSIDs seen across "
            f"{SCAN_ROUNDS} scans: {len(combined)}"
        )

        output.append("")

        output.append(
            f"{'SSID':30} "
            f"{'BSSID':20} "
            f"{'SIGNAL':8} "
            f"{'CHANNEL':9} "
            f"{'SECURITY'}"
        )

        output.append("-" * 100)

        networks = sorted(
            combined.values(),
            key=lambda x: (
                x["ssid"].lower(),
                x["bssid"].lower()
            )
        )

        for network in networks:

            security = network["authentication"]

            if network["encryption"]:
                security += " / " + network["encryption"]

            output.append(
                f"{network['ssid'][:30]:30} "
                f"{network['bssid']:20} "
                f"{network['signal']:8} "
                f"{network['channel']:9} "
                f"{security}"
            )

        output.append("")
        output.append("-" * 100)

        output.append(
            "CURRENT CONNECTION"
        )

        output.append(
            f"SSID : {current['ssid'] or 'Unknown'}"
        )

        output.append(
            f"BSSID: {current['bssid'] or 'Unknown'}"
        )

        output.append("")

        output.append(
            "Note: repeated scans reduce temporary scan misses, "
            "but Windows cannot guarantee that every nearby AP "
            "will be detected on every scan."
        )

        output.append("")
        output.append(
            "Discovery only. No authentication attempts, "
            "deauthentication, handshake capture, or password "
            "cracking is performed."
        )

        self.after(
            0,
            lambda: self.finish(
                "\n".join(output),
                f"Wi-Fi scan complete — {len(networks)} BSSID(s) observed"
            )
        )

    # =========================================================
    # IP configuration
    # =========================================================

    def get_ipv4_config(self):

        stdout, stderr, code = self.run_command(
            ["ipconfig"]
        )

        local_ip = ""
        subnet = ""
        gateway = ""

        # Prefer Wi-Fi section
        sections = re.split(
            r"\r?\n(?=[A-Za-z].*adapter )",
            stdout
        )

        wifi_section = ""

        for section in sections:

            if "Wi-Fi" in section:

                wifi_section = section
                break

        if not wifi_section:
            wifi_section = stdout

        match = re.search(
            r"IPv4 Address[.\s]*:\s*([0-9.]+)",
            wifi_section,
            re.IGNORECASE
        )

        if match:
            local_ip = match.group(1)

        match = re.search(
            r"Subnet Mask[.\s]*:\s*([0-9.]+)",
            wifi_section,
            re.IGNORECASE
        )

        if match:
            subnet = match.group(1)

        match = re.search(
            r"Default Gateway[.\s]*:\s*([0-9.]+)",
            wifi_section,
            re.IGNORECASE
        )

        if match:
            gateway = match.group(1)

        return local_ip, subnet, gateway

    # =========================================================
    # ARP
    # =========================================================

    def get_arp_table(self):

        stdout, stderr, code = self.run_command(
            ["arp", "-a"]
        )

        devices = {}

        for raw in stdout.splitlines():

            line = raw.strip()

            match = re.match(
                r"([0-9.]+)\s+"
                r"([0-9a-fA-F-]{17})\s+"
                r"(\w+)",
                line
            )

            if not match:
                continue

            ip = match.group(1)
            mac = match.group(2)
            device_type = match.group(3)

            # Ignore broadcast/multicast entries
            if (
                ip.startswith("224.") or
                ip.startswith("239.") or
                ip == "255.255.255.255"
            ):
                continue

            if mac.lower() == "ff-ff-ff-ff-ff-ff":
                continue

            devices[ip] = {
                "mac": mac,
                "type": device_type
            }

        return devices

    # =========================================================
    # Hostname
    # =========================================================

    def hostname_for_ip(self, ip):

        try:

            hostname = socket.gethostbyaddr(ip)[0]

            if hostname == ip:
                return "Unknown"

            return hostname

        except Exception:

            return "Unknown"

    # =========================================================
    # Ping local network
    # =========================================================

    def ping_host(self, ip):

        try:

            result = subprocess.run(
                [
                    "ping",
                    "-n",
                    "1",
                    "-w",
                    "250",
                    str(ip)
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2
            )

            return result.returncode == 0

        except Exception:

            return False

    def discover_local_hosts(self, network):

        # Keep the scan bounded.
        hosts = list(network.hosts())

        if len(hosts) > 1024:

            hosts = hosts[:1024]

        # Sequential discovery is intentionally simple and
        # avoids creating a large number of simultaneous requests.
        for ip in hosts:

            self.ping_host(ip)

    # =========================================================
    # Local network scan
    # =========================================================

    def start_local_scan(self):

        if self.scanning:
            return

        self.scanning = True

        self.nearby_button.config(state="disabled")
        self.local_button.config(state="disabled")
        self.current_button.config(state="disabled")

        self.write(
            "Scanning devices visible on your local network...\n\n"
            "This checks your own local IPv4 network.\n"
            "Please wait...\n"
        )

        self.status.config(
            text="Scanning local network..."
        )

        thread = threading.Thread(
            target=self.local_scan_worker,
            daemon=True
        )

        thread.start()

    def local_scan_worker(self):

        local_ip, subnet_mask, gateway = \
            self.get_ipv4_config()

        current = self.get_current_wifi()

        if not local_ip or not subnet_mask:

            self.after(
                0,
                lambda: self.finish(
                    "Could not determine the Wi-Fi IPv4 configuration.\n\n"
                    "Make sure the computer is connected to Wi-Fi.",
                    "Could not determine network configuration"
                )
            )

            return

        try:

            network = ipaddress.IPv4Network(
                f"{local_ip}/{subnet_mask}",
                strict=False
            )

        except Exception as exc:

            self.after(
                0,
                lambda: self.finish(
                    f"Could not calculate local network:\n{exc}",
                    "Network calculation error"
                )
            )

            return

        self.set_status(
            f"Discovering devices on {network}..."
        )

        # Generate traffic on the local subnet so that
        # reachable devices may populate the ARP cache.
        self.discover_local_hosts(network)

        arp = self.get_arp_table()

        # Make sure gateway is represented.
        if gateway and gateway not in arp:

            arp[gateway] = {
                "mac": "Unknown",
                "type": "gateway"
            }

        output = []

        output.append("MY LOCAL NETWORK")
        output.append("=" * 100)
        output.append("")

        output.append(
            f"Wi-Fi SSID        : "
            f"{current['ssid'] or 'Unknown'}"
        )

        output.append(
            f"Access Point BSSID: "
            f"{current['bssid'] or 'Unknown'}"
        )

        output.append(
            f"Computer hostname : "
            f"{socket.gethostname()}"
        )

        output.append(
            f"Computer IP       : "
            f"{local_ip}"
        )

        output.append(
            f"Subnet            : "
            f"{network}"
        )

        output.append(
            f"Gateway           : "
            f"{gateway or 'Unknown'}"
        )

        output.append("")

        output.append(
            f"{'DEVICE / HOSTNAME':28} "
            f"{'IP ADDRESS':17} "
            f"{'MAC ADDRESS':20} "
            f"{'TYPE'}"
        )

        output.append("-" * 100)

        # This computer
        own_hostname = socket.gethostname()

        own_mac = self.get_own_mac()

        output.append(
            f"{own_hostname[:28]:28} "
            f"{local_ip:17} "
            f"{own_mac:20} "
            f"THIS PC"
        )

        # Gateway
        if gateway:

            gateway_mac = arp.get(
                gateway,
                {}
            ).get(
                "mac",
                "Unknown"
            )

            gateway_name = self.hostname_for_ip(
                gateway
            )

            if gateway_name == "Unknown":

                gateway_name = "Gateway / Router"

            output.append(
                f"{gateway_name[:28]:28} "
                f"{gateway:17} "
                f"{gateway_mac:20} "
                f"GATEWAY"
            )

        # Other ARP devices
        sorted_devices = sorted(
            arp.items(),
            key=lambda item: tuple(
                int(part)
                for part in item[0].split(".")
            )
        )

        for ip, data in sorted_devices:

            if ip == local_ip:
                continue

            if ip == gateway:
                continue

            hostname = self.hostname_for_ip(ip)

            output.append(
                f"{hostname[:28]:28} "
                f"{ip:17} "
                f"{data['mac']:20} "
                f"LOCAL DEVICE"
            )

        output.append("")
        output.append("-" * 100)

        output.append(
            f"ARP entries discovered: {len(arp)}"
        )

        output.append("")
        output.append(
            "Important:"
        )

        output.append(
            "• BSSID identifies the Wi-Fi access point."
        )

        output.append(
            "• A client device has its own MAC address."
        )

        output.append(
            "• ARP does not guarantee that every connected device "
            "will appear."
        )

        output.append(
            "• Devices may be hidden by client isolation, firewalls, "
            "sleep mode, or other network configuration."
        )

        output.append(
            "• Nearby Wi-Fi networks are not the same as devices "
            "on your LAN."
        )

        self.after(
            0,
            lambda: self.finish(
                "\n".join(output),
                f"Local network scan complete — {len(arp)} ARP entries"
            )
        )

    # =========================================================
    # Own MAC
    # =========================================================

    def get_own_mac(self):

        stdout, stderr, code = self.run_command(
            ["getmac", "/fo", "csv", "/nh"]
        )

        for line in stdout.splitlines():

            match = re.search(
                r'"([0-9A-Fa-f-]{17})"',
                line
            )

            if match:

                return match.group(1)

        return "Unknown"

    # =========================================================
    # Finish operation
    # =========================================================

    def finish(self, text, status):

        self.write(text)

        self.status.config(
            text=status
        )

        self.scanning = False

        self.nearby_button.config(
            state="normal"
        )

        self.local_button.config(
            state="normal"
        )

        self.current_button.config(
            state="normal"
        )


# =============================================================
# Main
# =============================================================

if __name__ == "__main__":

    app = WiFiSecurityLab()

    app.mainloop()