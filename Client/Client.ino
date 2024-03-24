// https://github.com/morrissinger/ESP8266-Websocket/tree/master
// https://stackoverflow.com/questions/59005181/unable-to-connect-https-protocol-with-esp8266-using-wificlientsecure

#include <ESP8266WiFi.h>
#include <WebSocketClient.h>
#include <ESP8266HTTPClient.h>

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

    webSocketClient.sendData("ESP");
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
      //Serial.print("Received data: ");
      //Serial.println(data);
      //Serial.println("Sending data to Arduino Lights");

      Serial.print("<");
      Serial.print(data);
      Serial.print(">");

      //Serial1.write("GOT SOMETHING"); // Sending data to Arduino
    }

    if (Serial1.available() > 0) {
      Serial.println(Serial1.readString());
      // Serial1.readStringUntil('<');
      // String message = Serial1.readStringUntil('>');
      // Serial.println(message);
      // webSocketClient.sendData(message);
    }
    
    // capture the value of analog 1, send it along
    // pinMode(1, INPUT);
    // data = String(analogRead(1));
    // webSocketClient.sendData("POG");
    
    
  } else {
    Serial.println("Client disconnected.");
    while (1) {
      // Hang on disconnect.
    }
  }
  
  // wait to fully let the client disconnect
  //delay(3000);
  
}