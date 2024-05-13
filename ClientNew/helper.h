#include <ESP8266WiFi.h>
#include <WebSocketClient.h>
#include <ESP8266HTTPClient.h>

/* HTTP helper function definitions */
void parseRGB();

/* UART helper function definitions */
void connectWifi();
void connectWebSocket();

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

// RGB Color Buffer
char buffer[10];

//Brown-Guest
const char* ssid     = "Brown-Guest";
const char* password = "";
char path[] = "/";
char host[] = "kazar4.com";
