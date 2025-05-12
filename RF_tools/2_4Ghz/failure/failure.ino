// Hour 5 of trying to make the nrf24l01 work. after many failed attempt, i declare defeat.
// I have tried everything and have started to question my ability to code, 
// cried, had a breakdown and considered quitting altogether. I will no longer spend my time in such wastefull ways 
// and will focus on code that hopefully works. If anyone is willing to try to make it work, it will be greatly appreciated. 
// Until then, this is a emmision transmission test that does not even build properly

// Please increase this time spent counter : 5 hours

#include <Arduino.h>
#include <SPI.h>
#include <CircularBuffer.hpp>
#include <RF24.h>
#include "NRF24_sniff_types.h"

#define CE_PIN       9   // Connect to nRF CE
#define CSN_PIN      10  // Connect to nRF CSN

#ifdef LED_SUPPORTED
  #define LED_RX       A0
  #define LED_TX       A1
  #define LED_FULL     A2
  #define LED_CONFIG   A3
#endif

#define PACKET_BUFFER_SIZE 30

RF24 radio(CE_PIN, CSN_PIN);

static NRF24_packet_t bufferData[PACKET_BUFFER_SIZE];
static CircularBuffer<NRF24_packet_t, PACKET_BUFFER_SIZE> packetBuffer;

// Serial header & configuration
static Serial_header_t serialHdr;
static volatile Serial_config_t conf = {
  76,               // channel
  RF24_1MBPS,       // datarate
  5,                // address length
  4,                // promiscuous length
  0xA8A8E1FC00LL,   // base address
  2,                // CRC length
  32                // max payload
};

static inline uint8_t getPayloadLen(const NRF24_packet_t &pkt) {
  return (pkt.packet[conf.addressLen - conf.addressPromiscLen] & 0xFC) >> 2;
}

inline void dumpBytes(const uint8_t *p, size_t n) {
  Serial.write(p, n);
}

void IRAM_ATTR handleIRQ() {
  while (radio.available()) {
    NRF24_packet_t pkt;
    pkt.timestamp   = micros();
    pkt.packetsLost = 0;
    uint8_t len = radio.getPayloadSize();
    if (len > conf.maxPayloadSize) len = conf.maxPayloadSize;
    radio.read(pkt.packet, len);
    if (!packetBuffer.isFull()) packetBuffer.push(pkt);
  }
  radio.clearInterrupts();
}

void setup() {
  Serial.begin(115200);
  SPI.begin();
  radio.begin();
  radio.setAutoAck(false);
  radio.setRetries(0, 0);

  pinMode(IRQ_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(IRQ_PIN), handleIRQ, FALLING);

  radio.setChannel(conf.channel);
  radio.setDataRate((rf24_datarate_e)conf.rate);
  radio.disableCRC();
  radio.setPayloadSize(conf.maxPayloadSize);
  radio.setAddressWidth(conf.addressPromiscLen);
  radio.openReadingPipe(0, conf.address >> (8*(conf.addressLen - conf.addressPromiscLen)));
  radio.startListening();
}

void loop() {
  while (!packetBuffer.isEmpty()) {
    NRF24_packet_t pkt = packetBuffer.shift();

    serialHdr.timestamp   = pkt.timestamp;
    serialHdr.packetsLost = pkt.packetsLost;
    uint8_t hdrLen = sizeof(serialHdr) - (conf.addressLen - conf.addressPromiscLen);

    uint8_t payloadLen = getPayloadLen(pkt);
    uint16_t totalBits = hdrLen*8 + (conf.addressLen - conf.addressPromiscLen)*8 + 9*8 + payloadLen*8 + conf.crcLength*8;
    uint8_t totalBytes = (totalBits + 7)/8;

    // Send length+type
    uint8_t lt = SET_MSG_TYPE(totalBytes, MSG_TYPE_PACKET);
    dumpBytes(&lt, 1);

    // Send header + packet data
    dumpBytes((uint8_t*)&serialHdr, hdrLen);
    dumpBytes(pkt.packet, totalBytes - hdrLen);
  }
}

