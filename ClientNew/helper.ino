
void connectWifi() {
  Serial.println();
  Serial.print("ESP Board MAC Address:  ");
  Serial.println(WiFi.macAddress());

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  ESP.wdtFeed();
  delay(2000);
}

void connectWebSocket() {
  // SSL fingerprint for bottom level cert kazar4.com
  const char *sslFingerprint = "DB 50 1E 9C 09 6D E5 E3 FF 91 D6 B2 CD B9 BE 9F FA F5 EA 29";

  client.setFingerprint(sslFingerprint);

  if (client.connect("kazar4.com", 9001)) {
    Serial.println("Connected");
  } else {
    Serial.println("Websocket Connection failed. Resetting ESP");
    while(1) {
      // Hang on failure
      ESP.reset();
    }
  }

  // Handshake with the server
  webSocketClient.path = path;
  webSocketClient.host = host;
  if (webSocketClient.handshake(client)) {
    Serial.println("Handshake successful");

    String macAddress = WiFi.macAddress();
    macAddress = "M-" + macAddress;
    webSocketClient.sendData(macAddress);
    
  } else {
    Serial.println("Handshake failed. Resetting ESP");
    while(1) {
      // Hang on failure
      ESP.reset();
    }  
  }
}

void parseRGB() {
  // Ex: $3#FF00FF
  char ledStrip;

  sscanf(buffer, "$%1c#%02hhx%02hhx%02hhx", &ledStrip, &tempR, &tempG, &tempB);
  Serial.print("Coloring Strip [");
  Serial.print(ledStrip);
  Serial.println("]");
  Serial.print("Parsed Colors R=");
  Serial.print(tempR);
  Serial.print(", G=");
  Serial.print(tempG);
  Serial.print(", B=");
  Serial.println(tempB);

  if (ledStrip == '1') {
    r1 = tempR;
    g1 = tempG;
    b1 = tempB;
  } else if (ledStrip == '2') {
    r2 = tempR;
    g2 = tempG;
    b2 = tempB;
  } else {
    r1 = tempR;
    g1 = tempG;
    b1 = tempB;

    r2 = tempR;
    g2 = tempG;
    b2 = tempB;
  }
}