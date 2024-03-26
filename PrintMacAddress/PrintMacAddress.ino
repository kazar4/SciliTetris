// https://github.com/morrissinger/ESP8266-Websocket/tree/master
// https://stackoverflow.com/questions/59005181/unable-to-connect-https-protocol-with-esp8266-using-wificlientsecure

#include <ESP8266WiFi.h>


void setup() {
  Serial.begin(9600);
  while (!Serial);
  Serial1.begin(9600); // Initialize TX/RX communication (do not need to wait)
  delay(10);

  Serial.println();
  Serial.print("ESP Board MAC Address:  ");
  Serial.println(WiFi.macAddress());
}


void loop() {
  
  Serial.println(WiFi.macAddress());
  delay(3000);
  
}