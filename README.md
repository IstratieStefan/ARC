![Render](https://github.com/IstratieStefan/ARC/blob/main/ARC_website/project/public/HeroRender.PNG)
# ARC – All-in-one Remote Console
[![Designed in - California](https://img.shields.io/badge/Designed_in-California-2ea44f)](https://)
[![Built in - Romania](https://img.shields.io/badge/Built_in-Romania-3876fc)](https://)

## 🚨 IMPORTANT: Fix Import Errors

If you're seeing `ModuleNotFoundError: No module named 'config'` on your Raspberry Pi:

```bash
cd /home/admin/ARC
git pull
```

**All import statements have been fixed!** See [`FIX_NOW.md`](FIX_NOW.md) for details.

## ⚙️ Configuration for Your Installation

The default configuration is set for `/home/admin/ARC` on Raspberry Pi.

If you've installed ARC in a different location, update the app paths:

```bash
cd /home/admin/ARC  # or your installation path
./generate_config.sh
```

This ensures all apps launch correctly from anywhere, using the virtual environment. 

**Quick References:**
- [`RPI_COMMANDS.md`](RPI_COMMANDS.md) - All Raspberry Pi commands
- [`IMPORT_FIX_SUMMARY.md`](IMPORT_FIX_SUMMARY.md) - Import fixes explained

---

[Documentation 🇷🇴](https://github.com/IstratieStefan/ARC/blob/main/Docs/ARC%20Documentation.pdf)

[Documentation 🇺🇸](https://github.com/IstratieStefan/ARC/blob/main/Docs/ARC%20Documentation%20English.pdf)

[Official Page](https://arc.istratiestefan.com)

[Source Code](https://github.com/IstratieStefan/ARC)

[Hardware Repo](https://github.com/IstratieStefan/ARC-Hardware)

---

### **Chapter I. Practical Utility**

ARC is a portable device built for developers, researchers, and engineers who need debugging, communication, and RF/NFC analysis tools in the field. It combines a Linux-based mini-computer (Orange Pi Zero 2 W) with a custom motherboard that includes a keyboard, a 3.5" SPI screen, I²S audio output, a battery, and power circuits.

**Problem Solved**: It's an autonomous, compact, and multifunctional device for field testing and communication operations (e.g., pentesting, RF sniffing, NFC reading/emulation).

**Efficiency Compared to Alternatives**: Unlike a laptop with external adapters, ARC is much more portable, has a tactile interface and its own keyboard, and is designed for quick work or debugging sessions in the field.

---

### **Chapter II. Mechanics**

#### **Section II.1. Complexity**

- Does not include active mechanical components (motors).
- Mechanical components include: a compact enclosure, a 39-key tactile keyboard (QWERTY), a mounting system for the display, and external ports (16-pin for power, UART, SPI, I²C, GPIO; USB-C; 3.5mm jack).

#### **Section II.2. Construction Efficiency**

- The enclosure is designed in Fusion360 and 3D printed.
- The PCB is designed in KiCad.
- Up to 6-7 hours of battery life in mixed use.
- It does not have a renewable energy source but offers efficient power management (power switch, sleep button, etc.).

---

### **Chapter III. Electronics**

#### PCB

#### **Architecture**

- **Microprocessor**: Orange Pi Zero 2 W with a quad-core Cortex-A53 1.5 GHz processor and 4GB of RAM.
- **Microcontroller**: RP2040 (Waveshare Pico Mini) for the keyboard, connected via I²C.
- **Auxiliary Circuits**:
    - Power circuit (MCP73833 for charging, TPS61032PWP for boosting the voltage to 5V).
    - Audio circuit (PCM5102A to convert digital signals transmitted via the I2S protocol into analog signals, PAM8302 for amplification, and a speaker for sound output).
- **Modules**:
    - NFC Module (ESP32 S3 Mini + PN532 NFC module).
    - RF Module (ESP32 S3 Mini + Sub-GHz CC1101 RF module).
    - IR Module.
- **Connections**: I²S (DAC), I²C (Keyboard, Screen Touch, Modules), UART (Modules), SPI (Screen, Modules).

#### Active Components

| No. | Name | Description |
| --- | --- | --- |
| 1 | Orange Pi Zero 2W | SBC |
| 2 | Waveshare 3.5’’ display | 480x320px SPI Display |
| 3 | 4x4mm Tactile Button | Keyboard button |
| 4 | MCP73833 | Li-ion charging IC |
| 5 | TPS61032PWP | 5V boost IC |
| 6 | RP2040-tiny | Microcontroller Module for keyboard |
| 7 | PCM5102A | I²S DAC IC |
| 8 | PAM8302 | Speaker Amplifier IC |
| 9 | 8Ω Speaker | Speaker |
| 10 | Battery | Battery |

#### Connectors

| No. | Name | Description |
| --- | --- | --- |
| 1 | Type-C Port | Power |
| 2 | Type-C Port | Data |
| 3 | 3.5mm Jack | Headphone jack, uses the detection pin to switch between jack and speaker audio |
| 4 | IO Headers | 2 sets of pins for powering external modules and for interface |
| 5 | Mini HDMI | Video Output |

#### Left Header

| **Pin** | **Net** | **SBC Signal** | **Function** |
| :---: | :---: | :---: | :---: |
| **1** | **GND** | **GND** | **Common ground for extensions** |
| **2** | **+5 V** | **5 V out** | **Unregulated 5V power supply** |
| **3** | **GPIO12** | **GPIO12** | **General Purpose GPIO** |
| **4** | **GPIO21** | **GPIO21** | **General Purpose GPIO** |
| **5** | **GPIO22** | **GPIO22** | **General Purpose GPIO** |
| **6** | **MOSI** | **SPI0 MOSI** | **SPI master-out** |
| **7** | **MISO** | **SPI0 MISO** | **SPI master-in** |
| **8** | **SCLK** | **SPI0 SCLK** | **SPI clock** |

#### Right Header

| **Pin** | **Net** | **SBC Signal** | **Function** |
| :---: | :---: | :---: | :---: |
| **1** | **GND** | **GND** | **Common ground for extensions** |
| **2** | **+3.3 V** | **3.3 V out** | **Unregulated 3.3V power supply** |
| **3** | **+5 V** | **5 V out** | **Unregulated 5V power supply** |
| **4** | **GPIO16** | **GPIO16** | **General Purpose GPIO** |
| **5** | **RXD** | **UART0 RX** | **Serial Data IN** |
| **6** | **TXD** | **UART0 TX** | **Serial Data OUT** |
| **7** | **SDA** | **I²C SDA** | **I²C Data line** |
| **8** | **SCL** | **I²C SCL** | **I²C Clock line** |

#### **Section III.1. Complexity**

- Semi-autonomous device, but it can execute tasks completely independently (e.g., WiFi scanning, RF Sniffing, etc.) through its graphical interface.

---

### **Chapter IV. Software**

- The operating system is a custom distribution based on Armbian with Openbox + a minimal desktop environment built in Python (ARC Desktop Environment).
- The interface is created in Python using Pygame.
- Each application is modular and runs in isolation.
- Every UI element, integrated application, script path, and more can be modified by editing the *'arc.yaml'* file located in */.config*.
- The keyboard firmware is written in **CircuitPython** and transmits the button matrix codes to a Python script on the SBC to emulate key presses. To provide full functionality, the keyboard uses a layer system similar to smartphones. The keyboard layout can be modified from the Python script that interprets the key codes.
- Application Types:
    - Terminal
    - Calendar
    - WiFi tools
    - Bluetooth tools
    - IR tools
    - RF tools
    - NFC tools
    - Music player
    - Game launcher
    - Other Linux applications

#### WiFi Tools – Support for Wireless Network Analysis and Attacks

**WiFi Tools** is a graphical suite of tools for scanning, monitoring, and testing WiFi networks, designed for Linux systems with interfaces compatible with monitor mode. The interface is built in Python using Pygame, and the functionalities are built on top of classic utilities like `iwlist`, `airodump-ng`, `aireplay-ng`, and `aircrack-ng`.

| **Utility** | **Package** | **Description** |
| --- | --- | --- |
| iw | iw | Modern utility for configuring wireless interfaces (modes, info) |
| iwlist | wireless-tools | Older utility for scanning WiFi networks |
| aircrack-ng | aircrack-ng | Complete suite for WiFi auditing: handshake capture, cracking, deauth, etc. |
| airodump-ng | aircrack-ng | Part of aircrack-ng: monitors networks and captures handshakes |
| aireplay-ng | aircrack-ng | Part of aircrack-ng: sends deauthentication packets (deauth attack) |
| airmon-ng | aircrack-ng | Part of aircrack-ng: enables/disables monitor mode |
| ip | iproute2 | Standard utility for configuring network interfaces |

#### Bluetooth Tools – Utilities for Scanning, Connecting, and Testing Bluetooth Devices

**Bluetooth Tools** is a graphical interface that provides quick access to functions for scanning, connecting, managing, and testing Bluetooth devices, using `bluetoothctl` and `l2ping` in the background.

| **Utility** | **Package** | **Description** |
| --- | --- | --- |
| bluetoothctl | bluez | CLI utility for Bluetooth management (scanning, connecting, pairing, etc.) |
| l2ping | bluez | Sends L2CAP packets to Bluetooth devices (used for DoS demo) |
| timeout | coreutils | Used to limit the duration of scans with `bluetoothctl scan on` |

#### IR, NFC, RF Tools – Graphical Interfaces for Communication with External Modules

**IR, NFC, and RF Tools** are applications with a graphical user interface (GUI) that facilitate communication with specialized modules connected via UART, such as:

- **IR Modules** – for transmitting or recording infrared signals.
- **NFC Modules** – for reading and emulating NFC tags (with limited capabilities).
- **RF Modules** – for scanning, capturing, or transmitting radio signals in various frequencies.

#### Music Player – Play and Organize Local Audio Files

**Music Player** is an application that allows playing local audio files in .mp3 and .flac formats, offering a simple interface for navigation and playback control.

**Main Features:**

- **Sort by album or artist** – songs are automatically organized using metadata from the files.
- **Configure music folder** – the location of the audio files is specified in the *arc.yaml* file, located in the */.config* directory.
- **Display metadata** – title, duration, and album art are extracted from file metadata using the `mutagen` library.
- **Selection interface** – the user can browse through songs and select files for playback.
- **Playback menu** – allows control over playback with Play/Pause, Skip Forward, and Skip Backward functions, as well as viewing playback progress (current time).
- **Display album art** – the song's cover image is displayed on the playback screen if available in the metadata.

#### Game Launcher – Customizable Game Launcher

**Game Launcher** is an application that provides a simple graphical interface for launching locally installed games using user-defined Bash commands.

**Main Features:**

- **Quick game launching** – each game is associated with a Bash command that will be executed upon selection.
- **Flexible configuration** – games are defined in a `games.json` file, which contains the name and launch command for each game.
- **Custom file location** – the location of the `games.json` file can be specified in the *arc.yaml* file, located in the system's `.config` directory.
- **Simple interface** – the user can browse and select the desired game from an interactive list.

The application allows for easy integration of any game or emulator installed on the system.

#### ARC Connect

*This is not the final version; the images are to show the design concept.*

**[ARC]** can be connected to a web interface (FastAPI server) where we can:
- Monitor resource usage, uptime, IP address, and available storage space.
- Use a web-based SSH terminal (we can run commands directly from a browser).
- Transfer files to the `/uploads` folder.

To connect to this server, you must be connected with your laptop/phone to the same network as the **[ARC]** device and enter the IP, username, and password on the page [https://arc.istratiestefan.com/arc-connect](https://arc.istratiestefan.com/arc-connect).

---

### **Chapter V. Industrial Design**
- The enclosure is made of 2 parts and can be assembled using only 4 screws, making it easy to assemble or repair.
- The color scheme and design elements, such as the speaker grille, are inspired by the works of Dieter Rams.
- The circuit is compact, with a 4-layer PCB, an integrated keyboard, and integrated power and audio circuits.
- It can be assembled in a semi-industrial setting with standard SMD components.
- The documentation includes all necessary files: schematic, PCB layout, 3D STEP, BOM, etc.

**System Requirements:**
- 512MB RAM
- 1Ghz Processor
- Linux-based operating system

**[ARC] Connect System Requirements:**
- A (functional) browser for [ARC] connect

**Useful Links:**
- Project Site: [https://arc.istratiestefan.com](https://arc.istratiestefan.com)
- Source Code: [https://github.com/IstratieStefan/ARC](https://github.com/IstratieStefan/ARC)
- Hardware Repo: [https://github.com/IstratieStefan/ARC-Hardware](https://github.com/IstratieStefan/ARC-Hardware)
