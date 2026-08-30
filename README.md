# 🛡️ Wi-Fi Discovery & Local Network Audit

**Windows Wi-Fi Discovery • Local Network Enumeration • Authorized Security Auditing**

A Python-based cybersecurity learning project for discovering nearby Wi-Fi networks and analyzing the local network in an authorized environment.

---

<p align="center">
  <img src="images/poster.png" alt="Kali Wi-Fi Security Lab" width="500">
</p>

---

## ⚠️ Ethical Use & Legal Notice

> **AUTHORIZED USE ONLY**

This project is intended for:

- Educational cybersecurity laboratories
- Personal networks
- Authorized penetration testing
- Network administration
- Security research
- Defensive security learning

Only scan networks and systems that you **own or have explicit permission to assess**.

Do not use this project to access, disrupt, intercept, or attack networks without authorization.

---

# 📖 Overview

**Wi-Fi Discovery & Local Network Audit** is a Python-based Windows cybersecurity project designed to help students, security researchers, and network administrators understand Wi-Fi visibility and local-network discovery.

The project combines Python automation with native Windows networking commands to provide a simple security-lab environment.

### 🎯 Project Goals

- 📡 Discover nearby Wi-Fi networks
- 🔎 Inspect Wi-Fi security information
- 🌐 Identify the local IPv4 network
- 🖥️ Discover devices visible through the local ARP table
- 📋 Display local network configuration
- 🧪 Practice authorized security auditing
- 🐍 Learn Python security automation
- 🪟 Work with Windows networking and PowerShell
- 🛡️ Understand defensive network-security concepts

---

# 🚀 Features

## 📡 Wi-Fi Discovery

Discover and inspect Wi-Fi information available to the local Windows system.

Information can include:

- SSID
- BSSID
- Signal strength
- Channel
- Radio type
- Authentication
- Encryption

Useful for:

- Wi-Fi visibility
- Network identification
- Security-learning exercises
- Local network troubleshooting

---

## 🌐 Local Network Discovery

The project can inspect the computer's local IPv4 configuration and discover devices visible through the Windows ARP table.

Information can include:

- Computer hostname
- Local IPv4 address
- Subnet
- Default gateway
- MAC addresses
- Local devices
- Hostnames when available

---

## 🖥️ Windows Security Lab GUI

The Windows security-lab application provides a graphical interface for common discovery operations.

Available operations include:

- **Scan Nearby Wi-Fi**
- **Scan My Network**
- **Current Wi-Fi**
- **Clear**

The application is designed for authorized local-network security testing and educational laboratory use.

---

# 🏗️ Project Architecture

The following diagram shows the overall architecture of the project.

<p align="center">
  <img src="images/architecture%20diargam.png" alt="Wi-Fi Discovery and Local Network Audit Architecture Diagram" width="1000">
</p>

### Architecture Overview

```text
┌─────────────────────────┐
│     Wi-Fi Environment   │
│ Access Points / SSIDs   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Wi-Fi Discovery       │
│   Windows WLAN / netsh  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Python Security Lab   │
│   Discovery & Analysis  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Processing & Analysis   │
│ Parse / Organize Data   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Results & Reporting     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Authorized Security     │
│ Review                  │
└─────────────────────────┘
```

---

# 🧱 Architecture Layers

| Layer | Purpose |
|---|---|
| 📡 Target Environment | Wi-Fi networks and local network |
| 🐍 Application Layer | Python scripts and GUI |
| 📶 Discovery Layer | Wi-Fi and local-network discovery |
| ⚙️ Processing Layer | Parse and organize network information |
| 📋 Output Layer | Human-readable scan results |
| 🛡️ Security Layer | Authorized security analysis |

---

# 🔄 Workflow Diagram

The complete workflow of the project is shown below.

<p align="center">
  <img src="images/workflow%20diagram.png" alt="Wi-Fi Discovery and Local Network Audit Workflow Diagram" width="1100">
</p>

---

# 🔬 Project Workflow

```text
┌──────────────────────┐
│       START          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Initialize Python    │
│ Security Lab         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Check Windows Wi-Fi  │
│ Network Interface    │
└──────────┬───────────┘
           │
           ▼
     ┌───────────────┐
     │ Select Action │
     └───────┬───────┘
             │
      ┌──────┼────────┐
      │      │        │
      ▼      ▼        ▼
   Wi-Fi    Local    Current
   Scan    Network    Wi-Fi
      │      │        │
      ▼      ▼        ▼
    netsh  ipconfig   netsh
      │      arp      wlan
      │      ping     interfaces
      │      │        │
      └──────┼────────┘
             │
             ▼
     ┌────────────────┐
     │ Parse Results  │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │ Analyze Data   │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │ Display Output │
     └───────┬────────┘
             │
             ▼
        ┌─────────┐
        │  DONE   │
        └─────────┘
```

---

# 🧪 Cybersecurity Laboratory

This repository contains multiple scripts for practicing cybersecurity concepts in a controlled environment.

The laboratory focus includes:

- Wi-Fi discovery
- Network enumeration
- Local network analysis
- Windows networking
- Security auditing concepts
- Python automation
- Security-tool development
- Defensive security concepts

---

# 📂 Project Structure

```text
wifi-discovery-local-network-audit/
│
├── 📄 README.md
├── 📄 .gitignore
│
├── 🐍 kali_security_lab.py
├── 🪟 kali_security_lab_windows.py
├── 📡 wifi_authorized_audit.py
├── 📶 wifi_handshake_lab.py
│
└── 📁 images/
    ├── architecture diargam.png
    ├── workflow diagram.png
    └── poster.png
```

---

# 🖼️ Project Visuals

## 🛡️ Kali Wi-Fi Security Lab

<p align="center">
  <img src="images/poster.png" alt="Kali Wi-Fi Security Lab Poster" width="900">
</p>

---

## 🏗️ Architecture

<p align="center">
  <img src="images/architecture%20diargam.png" alt="Project Architecture Diagram" width="1000">
</p>

---

## 🔄 Workflow

<p align="center">
  <img src="images/workflow%20diagram.png" alt="Project Workflow Diagram" width="1100">
</p>

---

# 🧰 Scripts

## `wifi_authorized_audit.py`

Wi-Fi and local-network auditing functionality.

Learning areas include:

- Wi-Fi discovery
- Local network information
- Authorized network enumeration
- Security-oriented output

---

## `kali_security_lab.py`

Security-lab functionality for controlled cybersecurity experimentation.

---

## `kali_security_lab_windows.py`

Windows-oriented security-lab implementation.

The application provides a graphical interface with functions such as:

```text
Scan Nearby Wi-Fi
Scan My Network
Current Wi-Fi
Clear
```

---

## `wifi_handshake_lab.py`

Wi-Fi security laboratory component intended for controlled and authorized experimentation.

Use only with networks and wireless equipment that you own or have explicit authorization to test.

---

# 💻 Requirements

## Operating System

Recommended:

```text
Windows 10 / Windows 11
```

## Python

Python 3.x is recommended.

Check your Python installation:

```powershell
python --version
```

or:

```powershell
py --version
```

---

# ⚙️ Installation

Clone the repository:

```powershell
git clone https://github.com/chayanBisai/wifi-discovery-local-network-audit.git
```

Enter the project directory:

```powershell
cd wifi-discovery-local-network-audit
```

Check the project files:

```powershell
dir
```

---

# ▶️ Running the Project

## 🖥️ Windows Security Lab

Run:

```powershell
python kali_security_lab_windows.py
```

or:

```powershell
py kali_security_lab_windows.py
```

---

## 📡 Wi-Fi Authorized Audit

Run:

```powershell
python wifi_authorized_audit.py
```

---

## 🐍 Kali Security Lab

Run:

```powershell
python kali_security_lab.py
```

---

## 🧪 Wi-Fi Handshake Lab

Run:

```powershell
python wifi_handshake_lab.py
```

> Use laboratory functionality only in an isolated or explicitly authorized environment.

---

# 🖥️ Windows Networking Commands

The Windows implementation uses native Windows networking utilities.

### Wi-Fi interface information

```powershell
netsh wlan show interfaces
```

### Nearby Wi-Fi networks

```powershell
netsh wlan show networks mode=bssid
```

### IPv4 configuration

```powershell
ipconfig
```

### ARP table

```powershell
arp -a
```

### Host reachability

```powershell
ping <IP_ADDRESS>
```

### Local MAC information

```powershell
getmac
```

---

# 📊 Information Flow

## Wi-Fi Discovery

```text
Wi-Fi Adapter
      │
      ▼
Windows WLAN
      │
      ▼
Wi-Fi Discovery
      │
      ├── SSID
      ├── BSSID
      ├── Signal
      ├── Channel
      ├── Authentication
      └── Encryption
      │
      ▼
Python Parser
      │
      ▼
Security-Lab Output
```

---

## Local Network Discovery

```text
Windows Network
      │
      ▼
IPv4 Configuration
      │
      ├── IP Address
      ├── Subnet
      └── Gateway
      │
      ▼
Local Host Discovery
      │
      ▼
ARP Table
      │
      ├── IP
      ├── MAC
      └── Device
      │
      ▼
Hostname Resolution
      │
      ▼
Audit Results
```

---

# 🔐 Security Design

This project focuses on **discovery, enumeration, and authorized auditing**.

### The project does NOT provide:

- ❌ Unauthorized network access
- ❌ Deauthentication attacks
- ❌ Credential theft
- ❌ Password cracking
- ❌ Persistence mechanisms
- ❌ Malware deployment

### The project focuses on:

- ✅ Wi-Fi discovery
- ✅ Network enumeration
- ✅ Network visibility
- ✅ Security education
- ✅ Defensive analysis
- ✅ Authorized auditing

---

# 🛡️ Security Considerations

Wi-Fi discovery results are not necessarily a complete representation of the wireless environment.

Windows may temporarily miss networks because of:

- Adapter behavior
- Signal conditions
- Channel availability
- Driver limitations
- Environmental interference

ARP-based discovery also does not guarantee that every device connected to a network will appear.

Possible reasons include:

- Client isolation
- Host firewalls
- Sleep states
- Network configuration
- VLAN boundaries
- Other security controls

---

# 🧪 Example Laboratory Workflow

```text
1. Connect to your authorized Wi-Fi laboratory network
                     │
                     ▼
2. Start the Windows Security Lab
                     │
                     ▼
3. Select "Current Wi-Fi"
                     │
                     ▼
4. Review connection information
                     │
                     ▼
5. Select "Scan Nearby Wi-Fi"
                     │
                     ▼
6. Review visible wireless networks
                     │
                     ▼
7. Select "Scan My Network"
                     │
                     ▼
8. Review local IPv4 and ARP information
                     │
                     ▼
9. Analyze the results
                     │
                     ▼
10. Document security observations
```

---

# 🔒 `.gitignore`

The project excludes sensitive and generated local files.

```gitignore
# Python
__pycache__/
*.pyc
.venv/
venv/

# Secrets
.env
.env.*
*.key
*.pem

# Local scan/output files
pass_10000000_lab.txt
scan_results/
*.log
*.csv
*.json

# Personal configuration
config.local.py
settings.local.py
```

> Never commit passwords, private keys, API tokens, captured credentials, or other sensitive data.

---

# 📚 Learning Objectives

## 🐍 Python

- Functions and classes
- Threading
- Subprocess execution
- Regular expressions
- Network address processing
- GUI development with Tkinter
- Security automation

## 🌐 Networking

- SSID and BSSID
- Wi-Fi channels
- Signal strength
- IPv4 addressing
- Subnets
- Default gateways
- ARP
- MAC addresses
- Hostname resolution

## 🛡️ Cybersecurity

- Reconnaissance concepts
- Network enumeration
- Security auditing
- Asset visibility
- Defensive network analysis
- Authorized penetration-testing methodology

---

# 📖 Key Concepts

| Concept | Description |
|---|---|
| **SSID** | Name of a wireless network |
| **BSSID** | Identifier associated with a Wi-Fi access point |
| **RSSI** | Received signal-strength measurement |
| **ARP** | Protocol used for IPv4 address-to-MAC resolution |
| **Gateway** | Device that forwards traffic outside the local network |
| **Subnet** | Defines the boundaries of an IP network |
| **MAC Address** | Network interface identifier |
| **Network Enumeration** | Collecting information about visible network assets |

---

# 🛠️ Troubleshooting

## Python is not recognized

Try:

```powershell
py --version
```

If that works:

```powershell
py kali_security_lab_windows.py
```

---

## Wi-Fi scan returns no networks

Check:

```powershell
netsh wlan show interfaces
```

Make sure the Windows Wi-Fi adapter is enabled.

Then try:

```powershell
netsh wlan show networks mode=bssid
```

---

## Local network scan cannot determine the network

Run:

```powershell
ipconfig
```

Confirm that the Wi-Fi adapter has:

- IPv4 address
- Subnet mask
- Default gateway

---

## No devices appear in the local scan

Run:

```powershell
arp -a
```

Remember that ARP-based discovery does not guarantee visibility of every device on the network.

---

# 📈 Future Improvements

Possible future development:

- [ ] Export scan results to safe report formats
- [ ] Add network-device categorization
- [ ] Add vendor lookup for MAC addresses
- [ ] Improve Wi-Fi signal visualization
- [ ] Add scan history
- [ ] Add defensive security recommendations
- [ ] Add unit tests
- [ ] Add automated documentation
- [ ] Improve cross-platform support
- [ ] Add dedicated laboratory mode

---

# 🧑‍💻 Technologies

```text
Python 3
Tkinter
Windows WLAN / netsh
IPv4
ARP
PowerShell
Windows Networking
Git
GitHub
```

---

# 🧭 Project Philosophy

```text
        DISCOVER
            ↓
         ANALYZE
            ↓
          AUDIT
            ↓
          SECURE
```

The goal is not simply to scan networks.

The goal is to understand how network information can be collected, interpreted, and used to improve security.

---

# ⚖️ Responsible Security

> **Learn ethically. Test responsibly. Protect privacy.**

Use this project only against:

- Your own devices
- Your own Wi-Fi network
- Your own laboratory environment
- Systems for which you have explicit authorization

Unauthorized access or interference with computer systems and networks may be illegal.

---

# ⭐ Project

If this project helps you learn Python, networking, or cybersecurity, consider giving the repository a ⭐ on GitHub.

---

# 🛡️ Wi-Fi Discovery & Local Network Audit

**Discover • Analyze • Audit • Secure**

Built for cybersecurity education and authorized security testing.
