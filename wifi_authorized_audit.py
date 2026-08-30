import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import re
import socket
import ipaddress
from datetime import datetime


APP_TITLE = "Wi-Fi Security Lab — Windows Authorized Audit"
SCAN_ROUNDS = 3
SCAN_DELAY = 2
PING_TIMEOUT_MS = 350

# Add your own devices here if you want friendly names.
# MAC addresses are normalized automatically.
KNOWN_DEVICES = {
    # "AA:BB:CC:DD:EE:FF": "My Phone",
    # "11:22:33:44:55:66": "My Laptop",
}


class WiFiSecurityLab(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("1180x760")
        self.minsize(950, 620)

        self.scanning = False
        self.history = {}       # MAC -> tracking information
        self.scan_number = 0

        self.create_ui()

    # =========================================================
    # GUI
    # =========================================================

    def create_ui(self):
        title = ttk.Label(
            self,
            text="Wi-Fi Discovery / Local Network Audit",
            font=("Segoe UI", 18, "bold")
        )
        title.pack(pady=(12, 2))

        subtitle = ttk.Label(
            self,
            text=(
                "Real Windows WLAN discovery + authorized LAN auditing. "
                "No deauthentication, credential capture, or password cracking."
            )
        )
        subtitle.pack(pady=(0, 10))

        buttons = ttk.Frame(self)
        buttons.pack(fill="x", padx=12, pady=5)

        self.nearby_button = ttk.Button(
            buttons, text="Scan Nearby Wi-Fi", command=self.start_wifi_scan
        )
        self.nearby_button.pack(side="left", padx=4)

        self.local_button = ttk.Button(
            buttons, text="Scan My Network", command=self.start_local_scan
        )
        self.local_button.pack(side="left", padx=4)

        self.track_button = ttk.Button(
            buttons, text="Track Clients", command=self.start_tracking
        )
        self.track_button.pack(side="left", padx=4)

        self.current_button = ttk.Button(
            buttons, text="Current Wi-Fi", command=self.show_current_wifi
        )
        self.current_button.pack(side="left", padx=4)

        self.clear_button = ttk.Button(
            buttons, text="Clear", command=self.clear_output
        )
        self.clear_button.pack(side="left", padx=4)

        self.status = ttk.Label(self, text="Ready", anchor="w")
        self.status.pack(fill="x", padx=15, pady=5)

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.output = tk.Text(
            frame,
            wrap="none",
            font=("Consolas", 10)
        )
        self.output.pack(side="left", fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(
            frame, orient="vertical", command=self.output.yview
        )
        scrollbar_y.pack(side="right", fill="y")
        self.output.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(
            self, orient="horizontal", command=self.output.xview
        )
        scrollbar_x.pack(fill="x", padx=12)
        self.output.configure(xscrollcommand=scrollbar_x.set)

        footer = ttk.Label(
            self,
            text=(
                "Authorized discovery only. Nearby APs are not LAN clients. "
                "Client identities are obtained only from information your own "
                "Windows/router exposes."
            ),
            anchor="center"
        )
        footer.pack(fill="x", padx=12, pady=(4, 8))

        self.write(
            "Wi-Fi Security Lab\n"
            "==================\n\n"
            "This program uses the real Windows Wi-Fi adapter.\n"
            "Use the buttons above to inspect your own network.\n"
        )

    # =========================================================
    # Output helpers
    # =========================================================

    def write(self, text):
        self.output.delete("1.0", "end")
        self.output.insert("end", text)
        self.output.see("end")

    def clear_output(self):
        self.output.delete("1.0", "end")
        self.status.config(text="Ready")

    def set_status(self, text):
        self.after(0, lambda: self.status.config(text=text))

    def set_buttons(self, enabled):
        state = "normal" if enabled else "disabled"
        for button in (
            self.nearby_button,
            self.local_button,
            self.track_button,
            self.current_button,
        ):
            button.config(state=state)

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
            "transmit": "",
        }

        for raw in stdout.splitlines():
            line = raw.strip()
            if ":" not in line:
                continue

            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            mapping = {
                "Name": "name",
                "Description": "description",
                "SSID": "ssid",
                "AP BSSID": "bssid",
                "Signal": "signal",
                "Rssi": "rssi",
                "Radio type": "radio",
                "Channel": "channel",
                "Band": "band",
                "Authentication": "authentication",
                "Cipher": "cipher",
                "State": "state",
                "Receive rate (Mbps)": "receive",
                "Transmit rate (Mbps)": "transmit",
            }

            if key in mapping:
                info[mapping[key]] = value

        return info

    def show_current_wifi(self):
        if self.scanning:
            return

        self.scanning = True
        self.set_buttons(False)
        self.status.config(text="Reading current Wi-Fi...")
        threading.Thread(
            target=self.current_wifi_worker, daemon=True
        ).start()

    def current_wifi_worker(self):
        info = self.get_current_wifi()

        output = [
            "CURRENT WI-FI CONNECTION",
            "=" * 90,
            "",
        ]

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
            output.append(f"{key:20}: {value or 'Unknown'}")

        output += [
            "",
            "-" * 90,
            "These values come from Windows WLAN information."
        ]

        self.after(
            0,
            lambda: self.finish(
                "\n".join(output),
                "Current Wi-Fi information retrieved"
            )
        )

    # =========================================================
    # Nearby Wi-Fi
    # =========================================================

    def start_wifi_scan(self):
        if self.scanning:
            return

        self.scanning = True
        self.set_buttons(False)
        self.write(
            "Scanning nearby Wi-Fi networks using Windows WLAN...\n\n"
            f"Performing {SCAN_ROUNDS} scan passes.\n"
        )
        self.status.config(text="Scanning nearby Wi-Fi...")

        threading.Thread(
            target=self.wifi_scan_worker, daemon=True
        ).start()

    def parse_wifi_scan(self, text):
        networks = []
        current = None
        current_bssid = None

        for raw in text.splitlines():
            line = raw.strip()

            match = re.match(r"SSID\s+\d+\s*:\s*(.*)", line, re.I)
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
                    "bssid": "",
                    "stations": "",
                    "utilization": "",
                }
                current_bssid = None
                continue

            if not current:
                continue

            match = re.match(
                r"BSSID\s+\d+\s*:\s*([0-9a-fA-F:-]{17})",
                line, re.I
            )
            if match:
                current_bssid = match.group(1)
                continue

            lower = line.lower()

            def value_after_colon():
                return line.split(":", 1)[1].strip() if ":" in line else ""

            if lower.startswith("authentication"):
                current["authentication"] = value_after_colon()
            elif lower.startswith("encryption"):
                current["encryption"] = value_after_colon()
            elif lower.startswith("signal"):
                current["signal"] = value_after_colon()
            elif lower.startswith("radio type"):
                current["radio"] = value_after_colon()
            elif lower.startswith("band"):
                current["band"] = value_after_colon()
            elif lower.startswith("channel"):
                current["channel"] = value_after_colon()
            elif lower.startswith("connected stations"):
                current["stations"] = value_after_colon()
            elif lower.startswith("channel utilization"):
                current["utilization"] = value_after_colon()

        if current and current_bssid:
            current["bssid"] = current_bssid
            networks.append(current)

        return networks

    def wifi_scan_once(self):
        stdout, stderr, code = self.run_command(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            timeout=30
        )

        if code != 0:
            return [], stderr.strip()

        return self.parse_wifi_scan(stdout), ""

    def wifi_scan_worker(self):
        combined = {}

        for n in range(1, SCAN_ROUNDS + 1):
            self.set_status(f"Wi-Fi scan {n}/{SCAN_ROUNDS}...")

            results, error = self.wifi_scan_once()

            for network in results:
                bssid = network["bssid"].lower()
                if bssid:
                    combined[bssid] = network

            if n < SCAN_ROUNDS:
                time.sleep(SCAN_DELAY)

        current = self.get_current_wifi()

        output = [
            "NEARBY WI-FI NETWORKS",
            "=" * 110,
            "",
            f"Current SSID       : {current['ssid'] or 'Not connected'}",
            f"Current AP BSSID   : {current['bssid'] or 'Unknown'}",
            f"Current Signal     : {current['signal'] or 'Unknown'}",
            "",
            f"Unique BSSIDs seen across {SCAN_ROUNDS} scans: {len(combined)}",
            "",
            f"{'SSID':30} {'BSSID':20} {'SIGNAL':8} "
            f"{'CHANNEL':9} {'BAND':8} {'SECURITY':28} {'STATIONS':9}",
            "-" * 110
        ]

        for network in sorted(
            combined.values(),
            key=lambda x: (x["ssid"].lower(), x["bssid"].lower())
        ):
            security = network["authentication"] or "Unknown"
            if network["encryption"]:
                security += " / " + network["encryption"]

            output.append(
                f"{network['ssid'][:30]:30} "
                f"{network['bssid']:20} "
                f"{network['signal'][:8]:8} "
                f"{network['channel'][:9]:9} "
                f"{network['band'][:8]:8} "
                f"{security[:28]:28} "
                f"{network['stations'][:9]:9}"
            )

        output += [
            "",
            "-" * 110,
            "IMPORTANT:",
            "• BSSID belongs to an access point, not to a client device.",
            "• 'Connected Stations' is AP-reported information when available.",
            "• Windows WLAN does not expose the identity of those stations.",
            "• Nearby Wi-Fi networks are separate from devices on your LAN.",
            "• A Windows scan can temporarily miss an AP."
        ]

        if error:
            output += ["", f"Windows WLAN message: {error}"]

        output += [
            "",
            "Discovery only. No authentication, deauthentication, "
            "handshake capture, or password cracking is performed."
        ]

        self.after(
            0,
            lambda: self.finish(
                "\n".join(output),
                f"Wi-Fi scan complete — {len(combined)} BSSID(s)"
            )
        )

    # =========================================================
    # IP configuration
    # =========================================================

    def get_ipv4_config(self):
        stdout, stderr, code = self.run_command(["ipconfig"])

        local_ip = ""
        subnet_mask = ""
        gateway = ""

        # Find the Wi-Fi adapter block.
        blocks = re.split(r"\r?\n(?=[A-Za-z].*adapter )", stdout, re.I)
        wifi_block = ""

        for block in blocks:
            if re.search(r"adapter\s+Wi-?Fi", block, re.I):
                wifi_block = block
                break

        if not wifi_block:
            wifi_block = stdout

        patterns = [
            (r"IPv4 Address[.\s]*:\s*([0-9.]+)", "ip"),
            (r"Subnet Mask[.\s]*:\s*([0-9.]+)", "mask"),
            (r"Default Gateway[.\s]*:\s*([0-9.]+)", "gw"),
        ]

        for pattern, kind in patterns:
            match = re.search(pattern, wifi_block, re.I)
            if match:
                if kind == "ip":
                    local_ip = match.group(1)
                elif kind == "mask":
                    subnet_mask = match.group(1)
                elif kind == "gw":
                    gateway = match.group(1)

        return local_ip, subnet_mask, gateway

    # =========================================================
    # MAC / hostname helpers
    # =========================================================

    @staticmethod
    def normalize_mac(mac):
        return re.sub(r"[^0-9a-f]", "", mac.lower())

    def get_adapter_mac(self):
        stdout, stderr, code = self.run_command(
            ["getmac", "/fo", "csv", "/nh"]
        )

        for line in stdout.splitlines():
            match = re.search(r'"([0-9A-Fa-f-]{17})"', line)
            if match:
                return match.group(1).upper()

        return "Unknown"

    def hostname_for_ip(self, ip):
        # Try reverse DNS first
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            if hostname and hostname != ip:
                return hostname
        except Exception:
            pass

        # Try Windows NetBIOS
        try:
            result = subprocess.run(
                ["nbtstat", "-A", ip],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=3
            )

            for line in result.stdout.splitlines():
                match = re.match(
                    r"\s*([^\s<]+)\s+<00>\s+UNIQUE",
                    line,
                    re.IGNORECASE
                )
                if match:
                    return match.group(1)

        except Exception:
            pass

        return "Unknown"

    def friendly_name(self, mac, hostname):
        normalized = self.normalize_mac(mac)

        if normalized in KNOWN_DEVICES:
            return KNOWN_DEVICES[normalized]

        if self.normalize_mac(self.get_adapter_mac()) == normalized:
            return f"{hostname} (THIS PC)"

        return hostname if hostname != "Unknown" else "Unknown"

    # =========================================================
    # LAN discovery
    # =========================================================

    def ping_host(self, ip):
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", str(PING_TIMEOUT_MS), str(ip)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False

    def discover_local_hosts(self, network):
        hosts = list(network.hosts())

        # Avoid enormous scans.
        if len(hosts) > 1024:
            hosts = hosts[:1024]

        # A light discovery pass helps populate Windows ARP cache.
        for ip in hosts:
            self.ping_host(ip)

    def get_arp_table(self):
        stdout, stderr, code = self.run_command(["arp", "-a"])

        devices = {}

        for raw in stdout.splitlines():
            line = raw.strip()

            match = re.match(
                r"([0-9.]+)\s+([0-9a-fA-F-]{17})\s+(\w+)",
                line
            )

            if not match:
                continue

            ip = match.group(1)
            mac = match.group(2).upper()
            entry_type = match.group(3)

            if (
                ip.startswith("224.") or
                ip.startswith("239.") or
                ip == "255.255.255.255" or
                mac == "FF-FF-FF-FF-FF-FF"
            ):
                continue

            devices[ip] = {
                "mac": mac,
                "type": entry_type
            }

        return devices

    def local_scan_worker(self):
        local_ip, subnet_mask, gateway = self.get_ipv4_config()
        current = self.get_current_wifi()

        if not local_ip or not subnet_mask:
            self.after(
                0,
                lambda: self.finish(
                    "Could not determine the Wi-Fi IPv4 configuration.\n\n"
                    "Make sure this PC is connected to Wi-Fi.",
                    "Network configuration unavailable"
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

        self.set_status(f"Discovering devices on {network}...")
        self.discover_local_hosts(network)
        arp = self.get_arp_table()

        if gateway and gateway not in arp:
            arp[gateway] = {"mac": "Unknown", "type": "gateway"}

        own_hostname = socket.gethostname()
        own_mac = self.get_adapter_mac()

        output = [
            "MY LOCAL NETWORK",
            "=" * 110,
            "",
            f"Wi-Fi SSID        : {current['ssid'] or 'Unknown'}",
            f"Access Point BSSID: {current['bssid'] or 'Unknown'}",
            f"Computer hostname : {own_hostname}",
            f"Computer IP       : {local_ip}",
            f"Subnet            : {network}",
            f"Gateway           : {gateway or 'Unknown'}",
            "",
            f"{'DEVICE / HOSTNAME':28} {'IP ADDRESS':17} "
            f"{'MAC ADDRESS':20} {'TYPE':18} {'STATUS'}",
            "-" * 110
        ]

        # Always show this PC.
        output.append(
            f"{own_hostname[:28]:28} "
            f"{local_ip:17} "
            f"{own_mac:20} "
            f"THIS PC            ONLINE"
        )

        # Gateway.
        if gateway:
            gateway_mac = arp.get(gateway, {}).get("mac", "Unknown")
            gateway_name = self.hostname_for_ip(gateway)
            if gateway_name == "Unknown":
                gateway_name = "Gateway / Router"

            output.append(
                f"{gateway_name[:28]:28} "
                f"{gateway:17} "
                f"{gateway_mac:20} "
                f"GATEWAY            ONLINE/ROUTER"
            )

        # Other ARP-learned devices.
        other_count = 0
        for ip, data in sorted(
            arp.items(),
            key=lambda item: tuple(int(x) for x in item[0].split("."))
        ):
            if ip in (local_ip, gateway):
                continue

            hostname = self.hostname_for_ip(ip)
            friendly = self.friendly_name(data["mac"], hostname)

            output.append(
                f"{friendly[:28]:28} "
                f"{ip:17} "
                f"{data['mac']:20} "
                f"LOCAL DEVICE       VISIBLE"
            )
            other_count += 1

            self.update_history(
                data["mac"], ip, friendly, True
            )

        output += [
            "",
            "-" * 110,
            f"ARP entries discovered: {len(arp)}",
            f"Other local devices visible: {other_count}",
            "",
            "WHY THIS MAY NOT EQUAL THE ROUTER'S CONNECTED-CLIENT COUNT:",
            "• ARP only contains devices your PC has learned about.",
            "• Client isolation can prevent peer discovery.",
            "• Sleeping/firewalled devices may not answer.",
            "• The router may know clients that Windows does not know.",
            "",
            "For the authoritative list of Wi-Fi stations, use your own",
            "router's connected-client/DHCP page or an authorized router API.",
            "",
            "Tracking is based on observations from this PC; it does not",
            "force clients to respond or disconnect anyone."
        ]

        self.scan_number += 1

        self.after(
            0,
            lambda: self.finish(
                "\n".join(output),
                f"LAN scan complete — {other_count} other device(s) visible"
            )
        )

    def start_local_scan(self):
        if self.scanning:
            return

        self.scanning = True
        self.set_buttons(False)

        self.write(
            "Scanning your local Windows network...\n\n"
            "This performs a bounded discovery pass and reads the Windows ARP table.\n"
        )
        self.status.config(text="Scanning local network...")

        threading.Thread(
            target=self.local_scan_worker, daemon=True
        ).start()

    # =========================================================
    # Client tracking
    # =========================================================

    def update_history(self, mac, ip, name, present):
        key = self.normalize_mac(mac)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        item = self.history.setdefault(
            key,
            {
                "mac": mac,
                "name": name,
                "ip": ip,
                "first_seen": now,
                "last_seen": now,
                "seen": 0,
                "present": False,
                "last_change": "appeared",
            }
        )

        item["mac"] = mac
        item["name"] = name
        item["ip"] = ip

        if present:
            if not item["present"]:
                item["last_change"] = "appeared"
            item["present"] = True
            item["last_seen"] = now
            item["seen"] += 1
        else:
            if item["present"]:
                item["last_change"] = "disappeared"
            item["present"] = False

    def tracking_worker(self):
        local_ip, subnet_mask, gateway = self.get_ipv4_config()

        if not local_ip or not subnet_mask:
            self.after(
                0,
                lambda: self.finish(
                    "Cannot start tracking: Wi-Fi IPv4 configuration "
                    "could not be determined.",
                    "Tracking unavailable"
                )
            )
            return

        try:
            network = ipaddress.IPv4Network(
                f"{local_ip}/{subnet_mask}", strict=False
            )
        except Exception:
            self.after(
                0,
                lambda: self.finish(
                    "Cannot start tracking: invalid local subnet.",
                    "Tracking unavailable"
                )
            )
            return

        # Five observation rounds. This is passive/ordinary LAN discovery;
        # it does not disconnect or authenticate to any client.
        rounds = 5

        for n in range(1, rounds + 1):
            self.set_status(f"Client tracking observation {n}/{rounds}...")
            self.discover_local_hosts(network)
            arp = self.get_arp_table()

            seen_now = set()

            for ip, data in arp.items():
                if ip == local_ip:
                    continue

                mac = data["mac"]
                hostname = self.hostname_for_ip(ip)
                friendly = self.friendly_name(mac, hostname)

                self.update_history(mac, ip, friendly, True)
                seen_now.add(self.normalize_mac(mac))

            # Mark previously observed clients as absent for this observation.
            for key, item in self.history.items():
                if key not in seen_now:
                    self.update_history(
                        item["mac"], item["ip"], item["name"], False
                    )

            if n < rounds:
                time.sleep(3)

        output = [
            "CLIENT APPEARANCE / DISAPPEARANCE TRACKER",
            "=" * 110,
            "",
            "Observation source: Windows ARP-visible LAN devices.",
            "This is not the router's authoritative Wi-Fi association table.",
            "",
            f"{'NAME':28} {'IP':17} {'MAC':20} "
            f"{'STATE':12} {'SEEN':6} {'FIRST SEEN':19} {'LAST SEEN':19}",
            "-" * 110
        ]

        for item in sorted(
            self.history.values(),
            key=lambda x: x["mac"]
        ):
            state = "VISIBLE" if item["present"] else "NOT SEEN"
            output.append(
                f"{item['name'][:28]:28} "
                f"{item['ip']:17} "
                f"{item['mac']:20} "
                f"{state:12} "
                f"{item['seen']:<6} "
                f"{item['first_seen']:19} "
                f"{item['last_seen']:19}"
            )

        output += [
            "",
            "-" * 110,
            "Tracking notes:",
            "• 'VISIBLE' means your PC currently has an ARP observation.",
            "• 'NOT SEEN' does not prove the device disconnected.",
            "• Client isolation, sleep, firewalls and ARP aging affect results.",
            "• For exact Wi-Fi association state, inspect your own router.",
            "",
            "No deauthentication or forced reconnect operation is performed."
        ]

        self.after(
            0,
            lambda: self.finish(
                "\n".join(output),
                f"Tracking complete — {len(self.history)} device record(s)"
            )
        )

    def start_tracking(self):
        if self.scanning:
            return

        self.scanning = True
        self.set_buttons(False)

        self.write(
            "Starting authorized client tracking...\n\n"
            "Five observations will be collected.\n"
            "No clients will be disconnected.\n"
        )
        self.status.config(text="Starting client tracking...")

        threading.Thread(
            target=self.tracking_worker, daemon=True
        ).start()

    # =========================================================
    # Finish
    # =========================================================

    def finish(self, text, status):
        self.write(text)
        self.status.config(text=status)
        self.scanning = False
        self.set_buttons(True)


if __name__ == "__main__":
    app = WiFiSecurityLab()
    app.mainloop()
