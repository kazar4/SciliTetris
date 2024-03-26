// https://github.com/morrissinger/ESP8266-Websocket/tree/master
// https://stackoverflow.com/questions/59005181/unable-to-connect-https-protocol-with-esp8266-using-wificlientsecure

#include <ESP8266WiFi.h>
#include <WebSocketClient.h>
#include <ESP8266HTTPClient.h>
#include <FastLED.h>

#define DATA_PIN    3
//#define CLK_PIN   4
#define LED_TYPE    WS2811
#define COLOR_ORDER GRB
#define NUM_LEDS    42

CRGBArray<NUM_LEDS> leds;

#define BRIGHTNESS          96
#define FRAMES_PER_SECOND  120

//Brown-Guest
const char* ssid     = "Brown-Guest";
const char* password = "";
char path[] = "/";
char host[] = "kazar4.com";
//"ruling-commonly-cricket.ngrok-free.app";
//"kazar4.com";
  
WebSocketClient webSocketClient;

// Use WiFiClient class to create TCP connections
WiFiClientSecure client;

uint8_t r = 0;
uint8_t g = 0;
uint8_t b = 0;


void setUPLEDs(){ 
  delay(1000); // 3 second delay for recovery
  
  // tell FastLED about the LED strip configuration
  FastLED.addLeds<LED_TYPE,DATA_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  //FastLED.addLeds<LED_TYPE,DATA_PIN,CLK_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);

  // set master brightness control
  FastLED.setBrightness(BRIGHTNESS);

}

void LEDLoop() {
  static uint8_t hue;

  for(int i = 0; i < NUM_LEDS/2; i++) {   
    // fade everything out
    // leds.fadeToBlackBy(40);

    // let's set an led value
    leds[i] = CHSV(r, g, b);

    // now, let's first 20 leds to the top 20 leds, 
    leds(NUM_LEDS/2,NUM_LEDS-1) = leds(NUM_LEDS/2 - 1 ,0);
    FastLED.delay(33);
  }
}


void setup() {
  Serial.begin(9600);
  while (!Serial);
  Serial1.begin(9600); // Initialize TX/RX communication (do not need to wait)
  delay(10);

  Serial.println();
  Serial.print("ESP Board MAC Address:  ");
  Serial.println(WiFi.macAddress());

  // We start by connecting to a WiFi network

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid);

  // Serial.println(WiFi.macAddress());
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  delay(5000);
  
  const char *sslFingerprint = "DB 50 1E 9C 09 6D E5 E3 FF 91 D6 B2 CD B9 BE 9F FA F5 EA 29"; //bottom level kazar4

  //2B 8F 1B 57 33 0D BB A2 D0 7A 6C 51 F7 0E E9 0D DA B9 AD 8E

  //"4E E4 07 83 B5 C6 5C 20 92 3C A2 FB 02 62 2F 6A D1 01 8D B8"; // kazar4
  //const char *sslFingerprint = "7C 31 E3 10 46 64 45 D9 05 1F 98 92 8A DE 7B 2D DC E6 D6 CD"; //ngrok

  // CA BD 2A 79 A1 07 6A 31 F2 1D 25 36 35 CB 03 9D 43 29 A5 E8
  // A0 53 37 5B FE 84 E8 B7 48 78 2C 7C EE 15 82 7A 6A F5 A4 05
  // 7C 31 E3 10 46 64 45 D9 05 1F 98 92 8A DE 7B 2D DC E6 D6 CD

  client.setFingerprint(sslFingerprint);
  // Connect to the websocket server

  //client.connect("kazar4.com", 9001)
  if (client.connect("kazar4.com", 9001)) {
    Serial.println("Connected");
  } else {
    Serial.println("Connection failed.");
    while(1) {
      // Hang on failure
    }
  }

  // Handshake with the server
  webSocketClient.path = path;
  webSocketClient.host = host;
  if (webSocketClient.handshake(client)) {
    Serial.println("Handshake successful");

    setUPLEDs();

    String macAddress = WiFi.macAddress();
    macAddress = "M-" + macAddress;
    webSocketClient.sendData(macAddress);
    
  } else {
    Serial.println("Handshake failed.");
    while(1) {
      // Hang on failure
    }  
  }

}


void loop() {
  String data;

  if (client.connected()) {
    
    webSocketClient.getData(data);
    if (data.length() > 0) {

      int dataLen = data.length();

      //Serial.print("Received data: ");
      //Serial.println(data);
      //Serial.println("Sending data to Arduino Lights");

      if (data == "ping") {
        webSocketClient.sendData("pong");
      }

      if (data.charAt(0) == '#' && dataLen == 7) {
        char buffer[7];
        data.toCharArray(buffer, sizeof(buffer));

        uint8_t r = strtol(buffer + 1, NULL, 16); // Skip the '#' character
        uint8_t g = strtol(buffer + 3, NULL, 16); // Parse two characters for each color component
        uint8_t b = strtol(buffer + 5, NULL, 16);

        Serial.print("Received RGB values: R=");
        Serial.print(r);
        Serial.print(", G=");
        Serial.print(g);
        Serial.print(", B=");
        Serial.println(b);
      }

      Serial.print("<");
      Serial.print(data);
      Serial.println(">");

      //Serial1.write("GOT SOMETHING"); // Sending data to Arduino
    }
    
    LEDLoop();
    
  } else {
    Serial.println("Client disconnected.");
    while (1) {
      // Hang on disconnect.
    }
  }
  
  // wait to fully let the client disconnect
  //delay(3000);
  
}