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
#define NUM_LEDS    80

CRGBArray<NUM_LEDS> leds;
CRGBArray<NUM_LEDS> leds2;

#define FRAMES_PER_SECOND  120

void setUPLEDs(){ 
  delay(1000); // 3 second delay for recovery

  // To make this work for more than 2 we have to split them
  // Ex: 4 -> LED 1 (1, 2) LED 2 (3, 4)
  // Ex: 6 LED 1 (1, 2, 3) LED 2 (4, 5, 6)
  // Find # of LED command being sent
  // Check if even, split in half (/2), then go in order
  // Do each LED strip seperately, so split 40 LEDs by # for each
  // Ex: 40 // 3 (round it down), last one can take excess


  
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
  ESP.wdtEnable(WDTO_2S);
  
  Serial.begin(115200);
  while (!Serial);
  delay(10);

  setUPLEDs();

  connectWifi();
  
  connectWebSocket();

  lastPing = millis();
}


void loop() {

  if (millis() - lastPing > 200000) {
    Serial.println("Has not pinged 200+ secounds, restarting");
    ESP.reset();
  }

  if (client.connected()) {

    String data;
    
    webSocketClient.getData(data);

    int dataLen = data.length();
    if (dataLen > 0) {

      if (data == "ping") {
        lastPing = millis();
        webSocketClient.sendData("pong");
      }

      if (data == "syncOn") {
        syncOn = true;
      }

      if (data == "syncOff") {
        syncOn = false;
      }

      if (data == "reset") {
        ESP.reset();
      }

      if (data.charAt('L')) {

        // Serial.println(String("L200").substring(1).toInt());
        // Serial.println(String("L10").substring(1).toInt());
        // Serial.println(String("L90").substring(1).toInt());

        //L200 L100 L90
        Serial.print("Updating Delay Interval To: ");
        Serial.println(data.substring(1).toInt());

        firstInterval = data.substring(1).toInt();
      }

      if (data.charAt('B')) {

        Serial.print("Updating Brightness To: ");
        Serial.println(data.substring(1).toInt());
        BRIGHTNESS = data.substring(1).toInt();
        setUPLEDs();
      }

      // Json Data (only want it to do this every 50s sec)
      // I'm assuming parsing JSON is kinda costly
      if ((millis() - lastParse) > 10000 && data.startsWith("{")) {

        // Serial.print("Free Heap:");
        // Serial.println(ESP.getFreeHeap());
        // Serial.print("Heap Frag:");
        // Serial.println(ESP.getHeapFragmentation());

        lastParse = millis();

        JsonDocument doc;
        DeserializationError error =  deserializeJson(doc, data);

        if (error) {
          Serial.print(F("deserializeJson() failed: "));
          Serial.println(error.f_str());
        } else if (doc.containsKey("time") && doc.containsKey("timeDif")) {
            timeVal = doc["time"];
            timeDif = doc["timeDif"];

            timeOfParse = millis();

            Serial.print("time: ");
            Serial.println(timeVal);
            Serial.print("timeDif: ");
            Serial.println(timeDif);
        } else if (doc.containsKey("ERROR")) {

          Serial.print("<");
          Serial.print(data);
          Serial.println(">");
          // This probably means the ESP lagged too long and the website assumed that it is off/gone
          // other errors could happen here I should be ready for them TODO
          ESP.reset();
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

    if (syncOn) {
      long adjustedTime = timeVal + (millis() - timeOfParse) + timeDif;
      if (adjustedTime > firstInterval) {
        LEDLoop();
        firstInterval = getNextInterval(adjustedTime, 200);
        //Serial.println(firstInterval);
      }
    } else {
        // Update Color
        LEDLoop(); 
    }

  } else {
    Serial.println("Client disconnected. Restarting ESP");
    ESP.reset();
  }
  
  // wait to fully let the client disconnect
  //delay(3000);
  
}