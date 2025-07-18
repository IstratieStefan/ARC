![Render](https://github.com/IstratieStefan/ARC/blob/main/ARC_website/project/public/HeroRender.PNG)
# ARC – All-in-one Remote Console
[![Designed in - California](https://img.shields.io/badge/Designed_in-California-2ea44f)](https://)
[![Built in - Romania](https://img.shields.io/badge/Built_in-Romania-3876fc)](https://)

[Documentație 🇷🇴](https://github.com/IstratieStefan/ARC/blob/main/Docs/ARC%20Documentation.pdf) 

[Documentation 🇺🇸](https://github.com/IstratieStefan/ARC/blob/main/Docs/ARC%20Documentation%20English.pdf) 

[Pagină oficială](https://arc.istratiestefan.com)  

[Cod sursă](https://github.com/IstratieStefan/ARC)  

[Hardware Repo](https://github.com/IstratieStefan/ARC-Hardware)

---

### **Capitolul I. Utilitate practică**

ARC este un dispozitiv portabil, construit pentru dezvoltatori, cercetători și ingineri care au nevoie de unelte de depanare, comunicație și analiză RF/NFC în teren. Acesta combină un mini calculator cu Linux (Orange Pi Zero 2 W) cu o placă de bază personalizată ce include o tastatură, ecran SPI de 3.5", ieșire audio I²S, baterie și circuite de alimentare.

**Problema rezolvată**: autonom, compact, multifuncțional pentru teste și operații de comunicații în teren (ex. pentesting, sniffing RF, citire/emulare NFC).

**Eficiență față de alternative**: Spre deosebire de un laptop și adaptoare externe, ARC este mult mai portabil, are interfață tactilă și tastatură proprie, fiind gândit pentru sesiuni rapide de lucru sau depanare pe teren.

---

### **Capitolul II. Mecanică**

#### **Secțiunea II.1. Complexitate**

- Nu include componente mecanice active (motoare).
- Componentele mecanice includ: carcasă compactă, tastatură tactilă cu 39 de taste (QWERTY), sistem de fixare pentru display, porturi externe (16 pini (alimentare, uart, SPI, I²C, GPIO), USB-C, jack 3.5mm).

#### **Secțiunea II.2. Eficiență în construcție**

- Carcasă proiectată în Fusion360 printată 3d.
- PCB proiectat în KiCad.
- Autonomie de până la 6-7h în utilizare mixtă.
- Nu are sursă de energie regenerabilă, dar oferă management eficient al consumului (power switch, sleep button, etc.).
---

### **Capitolul III. Electronică**

#### PCB  

#### **Arhitectură**

- **Microprocesor**: Orange Pi Zero 2 W cu procesor quad-core Cortex-A53 1.5 Ghz și 4gb ram.
- **Microcontroller**: RP2040 (Waveshare Pico Mini) pentru tastatură, conectată prin  I²C
- **Circuite auxiliare**:
  - Circuit de alimentare (MCP73833 pentru încărcare, TPS61032PWP pentru ridicarea tensiunii la 5v)
  - Circuit audio (PCM5102A pentru transformarea semnalelor digitale transmise prin protocolul i2s în semnale analog, PAM8302 pentru amplificare și difuzorul pentru redarea sunetului)

- **Module**:
  - Modul NFC (ESP32 S3 Mini + modul PN532 NFC)
  - Modul RF (ESP32 S3 Mini + modul RF sub-GHz CC1101)
  - Modul IR
  - Conexiuni:  I²S (DAC),  I²C (Tastatura, Touch ecran, Module), UART (Module), SPI (Ecran, Module)

#### Componente active

|Nr. Crt.|Denumire|Descriere|
|---|---|---|
|1|Orange pi zero 2w|SBC|
|2|Waveshare 3.5’’ display|Display spi 480x320px|
|3|Buton tactil 4x4mm|Buton tastatura|
|4|MCP73833|IC incarcare Li-ion|
|5|TPS61032PWP|IC 5v boost|
|6|RP2040-tiny|Modul Microcontroller pentru tastatură|
|7|PCM5102A|IC DAC i2s|
|8|PAM8302|IC Amplificator difuzor|
|9|Difuzor 8Ω|Difuzor|
|10|Baterie|Baterie|

#### Conectori

|Nr. Crt.|Denumire|Descriere|
|---|---|---|
|1|Port type c|Alimentare|
|2|Port type c|Date|
|3|Jack 3.5mm|Mufă căști, folosește pinul de detecție pentru a schimba intre audio prin jack sau difuzor|
|4|Headeri IO|2 seturi de pini pentru alimentarea modulelor externe si pentru interfață|
|5|Mini Hdmi|Output Video|

#### Header Stânga

|  **Pin** |  **Net**    |  **Semnal SBC** |  **Funcție**                     |
| ----------- | -------------- | ------------------ | ----------------------------------- |
|  **1**   |  **GND**    |  **GND**        |  **Masă comună pentru extensii** |
|  **2**   |  **+5 V**   |  **5 V out**    |  **Alimentare 5 V neregulată**   |
|  **3**   |  **GPIO12** |  **GPIO12**     |  **GPIO general**                |
|  **4**   |  **GPIO21** |  **GPIO21**     |  **GPIO general**                |
|  **5**   |  **GPIO22** |  **GPIO22**     |  **GPIO general**                |
|  **6**   |  **MOSI**   |  **SPI0 MOSI**  |  **SPI master-out**              |
|  **7**   |  **MISO**   |  **SPI0 MISO**  |  **SPI master-in**               |
|  **8**   |  **SCLK**   |  **SPI0 SCLK**  |  **Clock SPI**                   |

####  Header Dreapta

|### **Pin**| **Net**| **Semnal SBC**| **Funcție**|
|---|---|---|---|
| **1**| **GND**| **GND**| **Masă comună pentru extensii**|
| **2**| **+3.3 V**| **3.3 V out**| **Alimentare 3.3 V neregulată**|
| **3**| **+5 V**| **5 V out**| **Alimentare 5 V neregulată**|
| **4**| **GPIO16**| **GPIO16**| **GPIO general**|
| **5**| **RXD**| **UART0 RX**| **Date seriale IN**|
| **6**| **TXD**| **UART0 TX**| **Date seriale OUT**|
| **7**| **SDA**| **I²C SDA**| **Linie date I²C**|
| **8**| **SCL**| **I²C SCL**| **Linie ceas I²C**|

 
#### **Secțiunea III.1. Complexitate**

- Dispozitiv semi-autonom, dar poate executa taskuri complet independent (ex: scan WiFi, Sniff RF, etc.) prin interfața grafică.

---

### **Capitolul IV. Software**

- Sistemul de operare este o distribuție personalizată bazată pe Armbian cu Openbox + un mediu desktop minimal realizat în python (ARC Desktop Environment).
- Interfața este realizată în Python folosind Pygame.
- Fiecare aplicație este modulară și rulează izolat.
- Fiecare element de ui, aplicațiile integrate, path-uri folosite pentru scripturi și multe altele pot fi modificate prin editarea fisierului _‘arc.yaml’_ care se aflat în  _/.config_
- Firmware-ul tastaturii este realizat în **circuitpython** și transmite codurile matricei de butoane către un script python de pe SBC pentru a emula apăsarea tastelor. Pentru a oferi funcționalitate completă tastaturii, folosim un sistem de layere similar telefoanelor. Layout-ul tastaturii poate fi modificat din scriptul python care interpretează key code-urile.
- Tipuri de aplicații:
  - Terminal
  - Calendar
  - WiFi tools
  - Bluetooth tools
  - Ir tools
  - Rf tools
  - Nfc tools
  - Music player
  - Game launcher

+      alte aplicații linux

#### WiFi Tools – Suport analiză și atac pentru rețele wireless

**WiFi Tools** este o suită grafică de instrumente pentru scanarea, monitorizarea și testarea rețelelor WiFi, concepută pentru sisteme Linux cu interfețe compatibile cu modul monitor. Interfața este realizată în Python folosind pygame, iar funcționalitățile sunt construite peste utilitare clasice precum iwlist, airodump-ng, aireplay-ng și aircrack-ng.

|**Utilitar**|**Pachet**|**Descriere**|
|---|---|---|
|iw|iw|Utilitar modern pentru configurarea interfețelor wireless (moduri, info)|
|iwlist|wireless-tools|Utilitar mai vechi pentru scanarea rețelelor WiFi|
|aircrack-ng|aircrack-ng|Suită completă pentru audit WiFi: handshake capture, cracking, deauth etc.|
|airodump-ng|aircrack-ng|Parte din aircrack-ng: monitorizare rețele și capturare handshake-uri|
|aireplay-ng|aircrack-ng|Parte din aircrack-ng: trimitere pachete de deautentificare (deauth attack)|
|airmon-ng|aircrack-ng|Parte din aircrack-ng: activare/dezactivare mod monitor|
|ip|iproute2|Utilitar standard pentru configurarea interfețelor de rețea|

#### Bluetooth Tools – Utilitare pentru scanare, conectare și testare dispozitive Bluetooth

**Bluetooth Tools** este o interfață grafică care oferă acces rapid la funcții de scanare, conectare, gestionare și testare a dispozitivelor Bluetooth, utilizând bluetoothctl și l2ping în fundal.

|**Utilitar**|**Pachet**|**Descriere**|
|---|---|---|
|bluetoothctl|bluez|Utilitar CLI pentru managementul Bluetooth (scanare, conectare, pairing etc.)|
|l2ping|bluez|Trimite pachete L2CAP către dispozitive Bluetooth (folosit pentru DoS demo)|
|timeout|coreutils|Folosit pentru a limita durata scanărilor cu bluetoothctl scan on|

#### IR, NFC, RF Tools – Interfețe grafice pentru comunicație cu module externe

**IR, NFC și RF Tools** sunt aplicații cu interfață grafică (GUI) care facilitează comunicarea cu module specializate conectate prin UART, precum:

- **Module IR** – pentru transmiterea sau înregistrarea semnalelor infraroșu;
- **Module NFC** – pentru citirea și emularea tagurilor NFC(posibiliități limitate);
- **Module RF** – pentru scanare, captură sau transmitere de semnale radio în frecvențe variate.

#### Music Player – Redare și organizare fișiere audio locale

**Music Player** este o aplicație care permite redarea fișierelor audio locale în formatele .mp3 și .flac, oferind o interfață simplă pentru navigare și control al redării.

**Funcționalități principale:**

- **Sortare după album sau artist** – melodiile sunt organizate automat folosind metadatele din fișiere.
- **Configurare folder muzical** – locația fișierelor audio este specificată în fișierul _arc.yaml_, aflat în directorul _/.config_ al sistemului.
-  **Afișare metadate** – titlul, durata și coperta albumului sunt extrase din metadatele fișierelor folosind biblioteca mutagen.
-  **Interfață de selecție** – utilizatorul poate naviga printre melodii și selecta fișiere pentru redare.
- **Meniu de redare** – permite controlul redării prin funcțiile Play/Pause, Skip Forward și Skip Backward, precum și vizualizarea progresului redării (timpul curent).
- **Afișare copertă album** – imaginea melodiei este afișată în ecranul de redare dacă este disponibilă în metadate.

#### Game Launcher – Lansator de jocuri personalizabil

**Game Launcher** este o aplicație care oferă o interfață grafică simplă pentru lansarea jocurilor instalate local, folosind comenzi Bash definite de utilizator.

Funcționalități principale:

- **Lansare rapidă a jocurilor** – fiecare joc este asociat cu o comandă Bash care va fi executată la selecție.
- **Configurare flexibilă** – jocurile sunt definite într-un fișier games.json, care conține numele și comanda de lansare pentru fiecare joc.
- **Personalizare locație fișier** – locația fișierului games.json poate fi specificată în fișierul arc.yaml, aflat în directorul .config al sistemului.
-  **Interfață simplă** – utilizatorul poate naviga și selecta jocul dorit dintr-o listă interactivă.

Aplicația permite integrarea ușoară a oricărui joc sau emulator instalat pe sistem.

#### ARC Connect

*Nu este forma finala, imaginile sunt pentru a arata design-ul*

**[ARC]** poate fi conectat la o interfață web (server FastApi) unde putem:
- monitoriza utilizarea resurselor, uptime-ul, adresa ip și spațiul de stocare valabil
- utiliza un terminal ssh web (putem rula comenzi direct dintr-un browser)
- transmite fișiere în folderul /uploads

Pentru a ne conecta la acest server trebuie sa fim conectati cu laptopul/telefonul pe aceeași rețea de internet ca și dispozitivul **[ARC]** și să introducem ip-ul, username-ul și parola pe pagina [https://arc.istratiestefan.com/arc-connect](https://arc.istratiestefan.com/arc-connect)

---

### **Capitolul V. Design industrial**
- Carcasa este realizata din 2 bucăți șii poate fi asamblată folosind doar 4 șuruburi, fiind astfel ușor de montat sau reparat.
- Tematica de culori și elementele de design precum grilajul difuzorului sunt inspirate din lucrările lui Dieter Rams
- Circuitul este compact, cu un PCB de 4 straturi, tastatură integrată și circuite de alimentare și audio integrate.
- Poate fi asamblat în regim semi-industrial, cu componente SMD standard.
- Documentația include toate fișierele necesare: schemă, layout PCB, 3D STEP, BOM, etc.

**Cerințe de sistem:**
- 512mb RAM
- Procesor 1Ghz
- Sistem de operare bazat pe linux

**Cerințe de sistem [ARC] connect:**

- Un browser (funcțional) pentru [ARC] connect

**Linkuri utile:**

- Site proiect: [](https://arc.istratiestefan.com)[https://arc.istratiestefan.com](https://arc.istratiestefan.com)
- Cod sursă: [https://github.com/IstratieStefan/ARC](https://github.com/IstratieStefan/ARC)
- Hardware repo: [https://github.com/IstratieStefan/ARC-Hardware](https://github.com/IstratieStefan/ARC-Hardware)
---
