// https://github.com/morrissinger/ESP8266-Websocket/tree/master
// https://stackoverflow.com/questions/59005181/unable-to-connect-https-protocol-with-esp8266-using-wificlientsecure
//https://github.com/datacute/DoubleResetDetector/

#include <FastLED.h>
#include "helper.h"

#define DATA_STRIP1    2
#define DATA_STRIP2    0
//#define CLK_PIN   4
#define LED_TYPE    WS2811
#define COLOR_ORDER GRB
#define NUM_LEDS    45

CRGBArray<NUM_LEDS> leds;
CRGBArray<NUM_LEDS> leds2;

#define BRIGHTNESS          96
#define FRAMES_PER_SECOND  120

void setUPLEDs(){ 
  delay(1000); // 3 second delay for recovery
  
  // tell FastLED about the LED strip configuration
  FastLED.addLeds<LED_TYPE,DATA_STRIP1,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.addLeds<LED_TYPE,DATA_STRIP2,COLOR_ORDER>(leds2, NUM_LEDS).setCorrection(TypicalLEDStrip);
  //FastLED.addLeds<LED_TYPE,DATA_PIN,CLK_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);

  // set master brightness control
  FastLED.setBrightness(BRIGHTNESS);

}

void LEDLoop() {
  for(int i = 0; i < NUM_LEDS; i++) {   
    // let's set an led value
    leds[i] = CRGB(r1, g1, b1);
    leds2[i] = CRGB(r2, g2, b2);
  }
  FastLED.show();
  FastLED.delay(1000 / 100);
}

void setup() {
  ESP.wdtEnable(5000);
  
  Serial.begin(9600);
  while (!Serial);
  Serial1.begin(9600); // Initialize TX/RX communication (do not need to wait)
  delay(10);

  setUPLEDs();

  connectWifi();
  
  connectWebSocket();
}


void loop() {

  if (client.connected()) {

    String data;
    
    webSocketClient.getData(data);

    int dataLen = data.length();
    if (dataLen > 0) {

      if (data == "ping") {
        webSocketClient.sendData("pong");
      }

      // Json Data
      if (data.startsWith("{")) {
        JsonDocument doc;
        DeserializationError error =  deserializeJson(doc, data);

        if (error) {
          Serial.print(F("deserializeJson() failed: "));
          Serial.println(error.f_str());
        } else {
            long time = doc["time"];
            long timeDif = doc["timeDif"];

            Serial.print("time: ");
            Serial.println(time);
            Serial.print("timeDif: ");
            Serial.println(timeDif);
        }
      }

      if (data.charAt(0) == '$' && dataLen == 9) {
        data.toCharArray(buffer, sizeof(buffer));
        parseRGB();
      }

      Serial.print("<");
      Serial.print(data);
      Serial.println(">");
    }
    
    // Update Color
    LEDLoop();

  } else {
    Serial.println("Client disconnected. Restarting ESP");
    ESP.reset();
  }
  
  // wait to fully let the client disconnect
  //delay(3000);
  
}