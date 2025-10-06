#include <Wire.h>
#include <Adafruit_PN532.h>

// I2C pins for ESP32
#define PN532_SDA 8
#define PN532_SCL 9

// Create PN532 I2C interface
Adafruit_PN532 nfc(PN532_SDA, PN532_SCL);

void setup() {
  delay(2000);
  Serial.begin(115200);
  Serial.println("PN532 NFC Serial Interface via I2C");

  nfc.begin();

  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.println("Didn't find PN532 board");
    while (1);
  }

  nfc.SAMConfig();
  Serial.println("PN532 NFC ready.");
}

void scanForTags() {
  Serial.println("Scanning for NFC tags...");
  uint8_t uid[7];
  uint8_t uidLength;

  if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 2000)) {
    Serial.print("Found tag UID: ");
    for (uint8_t i = 0; i < uidLength; i++) {
      Serial.print(uid[i], HEX);
      Serial.print(" ");
    }
    Serial.println();
  } else {
    Serial.println("No tag found.");
  }
}

void readTagData() {
  Serial.println("Reading data from NFC tag...");
  uint8_t uid[7];
  uint8_t uidLength;

  if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 2000)) {
    uint8_t data[16];
    if (nfc.mifareclassic_AuthenticateBlock(uid, uidLength, 4, 0, (uint8_t*)"\xFF\xFF\xFF\xFF\xFF\xFF") &&
        nfc.mifareclassic_ReadDataBlock(4, data)) {
      Serial.print("Data: ");
      for (int i = 0; i < 16; i++) {
        Serial.print((char)data[i]);
      }
      Serial.println();
    } else {
      Serial.println("Read failed.");
    }
  } else {
    Serial.println("No tag found.");
  }
}

void writeTagData(const char* data) {
  Serial.println("Writing data to NFC tag...");
  uint8_t uid[7];
  uint8_t uidLength;

  uint8_t buffer[16];
  memset(buffer, 0, 16);
  strncpy((char*)buffer, data, 16);

  if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 2000)) {
    if (nfc.mifareclassic_AuthenticateBlock(uid, uidLength, 4, 0, (uint8_t*)"\xFF\xFF\xFF\xFF\xFF\xFF") &&
        nfc.mifareclassic_WriteDataBlock(4, buffer)) {
      Serial.println("Write successful.");
    } else {
      Serial.println("Write failed.");
    }
  } else {
    Serial.println("No tag found.");
  }
}

void authenticateSector() {
  Serial.println("Authenticating sector 1...");
  uint8_t uid[7];
  uint8_t uidLength;

  if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 2000)) {
    if (nfc.mifareclassic_AuthenticateBlock(uid, uidLength, 4, 0, (uint8_t*)"\xFF\xFF\xFF\xFF\xFF\xFF")) {
      Serial.println("Authentication successful.");
    } else {
      Serial.println("Authentication failed.");
    }
  } else {
    Serial.println("No tag found.");
  }
}

void peerToPeerExchange() {
  Serial.println("Note: Peer-to-Peer is only partially supported by PN532 and not implemented in Adafruit library.");
  Serial.println("For P2P, use libnfc or NXP libraries on Linux platforms.");
}

void listTagTypes() {
  Serial.println("Supported tag types (detected via UID format):");
  Serial.println(" - MIFARE Classic 1K/4K");
  Serial.println(" - MIFARE Ultralight");
  Serial.println(" - NTAG203/213/215/216");
  Serial.println(" - ISO14443A (partial support for ISO14443B)");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');

    if (command == "scan") {
      scanForTags();
    } else if (command == "read") {
      readTagData();
    } else if (command.startsWith("write ")) {
      command.remove(0, 6);
      writeTagData(command.c_str());
    } else if (command == "auth") {
      authenticateSector();
    } else if (command == "p2p") {
      peerToPeerExchange();
    } else if (command == "list") {
      listTagTypes();
    } else if (command == "open") {
      writeTagData("https://github.com/IstratieStefan/ARC");
    } else {
      Serial.println("Available commands:");
      Serial.println(" - scan");
      Serial.println(" - read");
      Serial.println(" - write <data>");
      Serial.println(" - auth");
      Serial.println(" - p2p");
      Serial.println(" - list");
      Serial.println(" - open");
    }
  }
}