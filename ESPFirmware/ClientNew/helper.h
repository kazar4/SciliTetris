#include <ESP8266WiFi.h>
#include <WebSocketClient.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

#include <WiFiClientSecure.h>
#include <ESP8266httpUpdate.h>  // <-- Important

/* HTTP helper function definitions */
void parseRGB();

/* UART helper function definitions */
void connectWifi();
void connectWebSocket();

long getNextInterval(long epochTime, long intervalDuration);

// WiFi client
WebSocketClient webSocketClient;
WiFiClientSecure client;

// Strip Colors
int r1 = 0;
int g1 = 0;
int b1 = 0;

int r2 = 0;
int g2 = 0;
int b2 = 0;

int tempR;
int tempG;
int tempB;

int BRIGHTNESS = 96;

// RGB Color Buffer
char buffer[10];

//Brown-Guest
// const char* ssid     = "Brown-Guest";
// const char* password = "";

// const char* ssid     = "Verizon_6Y7F3K";
// const char* password = "demur9-jug-code";

const char* ssid     = "257 Thayer Resident";
const char* password = "f.JutTog";

const char* ssid2     = "RLAB";
const char* password2 = "metropolis";

char path[] = "/";
char host[] = "kazar4.com";

const char* server_url = "https://kazar4.com/SciliTetris/ESPFirmware/NewFirmwareUpload/firmware.bin"; 

const char *sslFingerprint = "F6 5E 7E 73 46 05 E9 62 6C 0C ED B4 51 EE 3F 5C 4D B5 07 44";

// timeParsingVals
bool syncOn = true;

long timeVal = 0L;
double timeDif = 0.0;

long lastParse = millis();
long timeOfParse = 0;

long firstInterval = 200;

long lastPing = millis();
