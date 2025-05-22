# ARC – All-in-one Remote Console

## 🚀 What is ARC?

**ARC (All-in-one Remote Console)** is a portable, open-source, modular toolkit for makers, hackers, engineers, and anyone passionate about wireless technologies.  
Built around a Raspberry Pi Zero 2 W, ARC brings together NFC, RF, LoRa, GSM, and a full-featured Linux terminal in a single handheld device, complete with a touchscreen, physical keyboard, and battery power.

> **Think of ARC as the Swiss Army knife for wireless tech:** scan NFC tags, analyze RF signals, communicate over LoRa or GSM, and launch custom apps, all from your pocket.

---

## 🎯 Key Features

- **Multi-protocol support:**  
  Interact with and test a huge range of wireless protocols:  
  - **NFC** (read/write/emulate cards)  
  - **RF** (analyze and transmit common signals)  
  - **LoRa** (long-range IoT comms)  
  - **GSM** (SMS, calls, and data via SIM800L)

- **Touchscreen GUI + Full QWERTY Keyboard:**  
  Easy-to-use interface designed for both touchscreen and physical input.

- **Modular software architecture:**  
  Each function (NFC, RF, LoRa, etc.) is its own app, launchable from a custom Python launcher.

- **Portable and battery-powered:**  
  Designed for fieldwork and everyday portability—no need for a laptop or separate adapters.

- **Fully open-source:**  
  Hardware designs, schematics, and all source code are open and customizable.

---

## 🛠️ Technical Overview

- **Core:**  
  - Raspberry Pi Zero 2 W running Debian 11 Lite (32-bit)
  - Custom PCB with 6-layer design for stability

- **Display:**  
  - 3.5" SPI TFT, controlled by `fbcp-ili9341` driver  
  - Touchscreen input

- **User Input:**  
  - Full QWERTY tactile keyboard (RP2040/Pico microcontroller as USB HID)

- **Wireless modules:**  
  - **NFC:** PN532 (UART/I2C/SPI)  
  - **RF:** CC1101/NRF24 (SPI)  
  - **LoRa:** SX1276 (SPI)  
  - **GSM:** SIM800L (UART)

- **Software architecture:**  
  - Linux + Xorg (X11) for GUI
  - NetworkManager (Wi-Fi), Bluez (Bluetooth)
  - Custom launcher and apps written in Python using Pygame
  - Modular structure: new apps and protocols can be added easily

- **Audio:**  
  - I2S audio output (for beeps, music, or voice)

- **Power:**  
  - Li-ion phone battery (with charge and protection circuit, battery gauge)

---

## 🖼️ Screenshots



---

## 💡 Why ARC?

- **All-in-one:** Replace a bag of dongles, adapters, and dev boards with a single device.
- **Open and hackable:** Both hardware and software are easy to modify, expand, and contribute to.
- **Ready for the field:** Compact, battery-powered, and rugged—built to go anywhere.
- **Perfect for:** Security researchers, makers, IoT developers, educators, or anyone who works with modern wireless tech.


