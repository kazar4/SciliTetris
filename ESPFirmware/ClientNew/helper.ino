
void connectWifi() {
  Serial.println();
  Serial.print("ESP Board MAC Address:  ");
  Serial.println(WiFi.macAddress());

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  // WiFi.begin(ssid, password);
  WiFi.begin(ssid);

  long connectTime = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");

    if (millis() - connectTime > 30000) {
      Serial.print("-");
      WiFi.begin(ssid2, password2);
    }

    if (millis() - connectTime > 100000) {
      Serial.println("Took to long to connect to wifi resetting");
      ESP.reset();
    }
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
  //const char *sslFingerprint = "F6 5E 7E 73 46 05 E9 62 6C 0C ED B4 51 EE 3F 5C 4D B5 07 44";
  // const char *sslFingerprint = "DB 50 1E 9C 09 6D E5 E3 FF 91 D6 B2 CD B9 BE 9F FA F5 EA 29";
  //const char *sslFingerprint = "BF ED 16 67 BD BD AB D9 A0 9B 5D BF 38 E0 2A EA B7 61 D2 ED";

  client.setFingerprint(sslFingerprint);

  //client.connect("kazar4.com", 9001)
  //client.connect("proteinarium.brown.edu", 4567)

  bool connectplz = client.connect("kazar4.com", 9001);
  //bool connectplz = client.connect("proteinarium.brown.edu", 4567);

  if (connectplz) {
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

void connectUDP() {
  Udp.begin(localUdpPort);
  Serial.printf("Now listening at IP %s, UDP port %d\n", WiFi.localIP().toString().c_str(), localUdpPort);

  String macAddress = WiFi.macAddress();
  macAddress = "M-" + macAddress;

  // Send a message to the server
  Udp.beginPacket(udpAddress, udpPort);
  Udp.write(macAddress.c_str());
  Udp.endPacket();

  Serial.println("Finished Connecting UDP");
}

void startOTAUpdate() {
  Serial.println("Starting OTA update...");
  t_httpUpdate_return ret = ESPhttpUpdate.update(client, server_url);

  switch (ret) {
    case HTTP_UPDATE_FAILED:
      Serial.printf("HTTP_UPDATE_FAILED Error (%d): %s\n", ESPhttpUpdate.getLastError(), ESPhttpUpdate.getLastErrorString().c_str());
      break;

    case HTTP_UPDATE_NO_UPDATES:
      Serial.println("HTTP_UPDATE_NO_UPDATES");
      break;

    case HTTP_UPDATE_OK:
      Serial.println("HTTP_UPDATE_OK — Update successful. Rebooting...");
      break;
  }
}

void parseRGB() {
  // Ex: $3#FF00FF
  // New Version: $4-3#FF00FF
  // 4 is the number of Leds (so 2 per strip)
  
  int newStripCount;

  Serial.println(buffer);

  sscanf(buffer, "$%d-", &newStripCount);

  Serial.printf("NewStripCount %d", newStripCount);
  Serial.println("");

  // If new strip count is chosen empty array
  if (newStripCount != numStripCount) {
    // New Array Size, but we need to empty the old array or atleast turn them to off
    for (int i = 0; i < MAX_ROWS; i++) {
      for (int j = 0; j < MAX_COLS; j++) {
          rgbArr[i][j] = 0;  // or any value you consider "empty"
      }
    }

    numStripCount = newStripCount;
  }

  // Now move the pointer past the header
  char* ptr = strchr(buffer, '-');
  if (ptr == nullptr) return; // error
  ptr++; // Move past the first #

 while (*ptr) {
  int logicalIndex;
  char hexColor[7] = {0};

  // Parse like: 3#FF00FF
  int charsParsed = 0;
  if (sscanf(ptr, "%d#%6s%n", &logicalIndex, hexColor, &charsParsed) == 2) {
    // Convert hex to RGB
    uint8_t r, g, b;
    sscanf(hexColor, "%02hhx%02hhx%02hhx", &r, &g, &b);
    Serial.printf("LED %d -> R=%d G=%d B=%d\n", logicalIndex, r, g, b);

    // If higher than count, fill all
    if (logicalIndex > numStripCount) {
      for (int i = 0; i < MAX_ROWS; i++) {
        rgbArr[i][0] = r;
        rgbArr[i][1] = g;
        rgbArr[i][2] = b;
      }
      break;
    } else {
      rgbArr[logicalIndex - 1][0] = r;
      rgbArr[logicalIndex - 1][1] = g;
      rgbArr[logicalIndex - 1][2] = b;
    }

    // Move pointer forward by the number of characters we just parsed
    ptr += charsParsed;
  } else {
    break; // failed to parse
  }
}
  buffer[0] = '\0';

  // sscanf(buffer, "$%d-%d#%02hhx%02hhx%02hhx", &newStripCount, &ledStrip, &tempR, &tempG, &tempB);
  // char colorHex[7] = {0}; 
  // sscanf(buffer, "$%1d-%1d#%6s", &newStripCount, &ledStrip, colorHex);

  // // Now manually split into R/G/B
  // char rStr[3] = {colorHex[0], colorHex[1], 0};
  // char gStr[3] = {colorHex[2], colorHex[3], 0};
  // char bStr[3] = {colorHex[4], colorHex[5], 0};

  // uint8_t tempR = strtol(rStr, NULL, 16);
  // uint8_t tempG = strtol(gStr, NULL, 16);
  // uint8_t tempB = strtol(bStr, NULL, 16);

  // Serial.print("Number of Pixels: ");
  // Serial.println(newStripCount);
  // Serial.print("Coloring Strip [");
  // Serial.print(ledStrip);
  // Serial.println("]");
  // Serial.print("Parsed Colors R=");
  // Serial.print(tempR);
  // Serial.print(", G=");
  // Serial.print(tempG);
  // Serial.print(", B=");
  // Serial.println(tempB);

  // // Empty buffer
  // buffer[0] = '\0';

  // if (newStripCount != numStripCount) {
  //   // New Array Size, but we need to empty the old array or atleast turn them to off
  //   for (int i = 0; i < MAX_ROWS; i++) {
  //     for (int j = 0; j < MAX_COLS; j++) {
  //         rgbArr[i][j] = 0;  // or any value you consider "empty"
  //     }
  //   }

  //   numStripCount = newStripCount;
  // }

  // int chosenStrip = ledStrip;

  // if (chosenStrip > numStripCount) {
  //   for (int i = 0; i < MAX_ROWS; i++) {
  //     rgbArr[i][0] = tempR;
  //     rgbArr[i][1] = tempG;
  //     rgbArr[i][2] = tempB;
  //   }
  // } else {
  //   rgbArr[chosenStrip - 1][0] = tempR;
  //   rgbArr[chosenStrip - 1][1] = tempG;
  //   rgbArr[chosenStrip - 1][2] = tempB;
  // }

  // if (ledStrip == '1') {
  //   r1 = tempR;
  //   g1 = tempG;
  //   b1 = tempB;
  // } else if (ledStrip == '2') {
  //   r2 = tempR;
  //   g2 = tempG;
  //   b2 = tempB;
  // } else {
  //   r1 = tempR;
  //   g1 = tempG;
  //   b1 = tempB;

  //   r2 = tempR;
  //   g2 = tempG;
  //   b2 = tempB;
  // }
}


long getNextInterval(long epochTime, long intervalDuration) {
  // Calculate the remainder when dividing epoch time by interval duration
  long remainder = epochTime % intervalDuration;
  
  // Calculate the next interval start by adding the difference between interval duration and remainder
  long nextIntervalStart = epochTime + (intervalDuration - remainder);
  
  return nextIntervalStart;
}
