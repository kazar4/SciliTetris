import json
import time
import sqlite3
import threading
import traceback
from rich import print


class Commands:

    pingTimes = {}
    savedPingTimes = {}

    batchedColors = {}

    cacheBool = True
    udpOn = True

    def __init__(self, admin, player, game, espConnections, coordConnections, macConnections, sock, udpPings, LEDPerEsp, batchSendDelay):
        self.admin = admin
        self.player = player
        self.game = game
        self.espConnections = espConnections
        self.coordConnections = coordConnections
        self.macConnections = macConnections

        self.sock = sock

        self.udpPings = udpPings

        self.LEDPerEsp = LEDPerEsp
        self.batchSendDelay = batchSendDelay


        
        self.conn = sqlite3.connect('cache.db')  # Connect to SQLite database
        self.cursor = self.conn.cursor()
        self.create_cache_table()

    def create_cache_table(self):
        # Create cache table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                mac TEXT PRIMARY KEY,
                x INTEGER,
                y INTEGER
            )
        ''')
        self.conn.commit()

    def setCache(self, MAC, x, y):
        # Update cache table
        conn = sqlite3.connect('cache.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO cache (mac, x, y) VALUES (?, ?, ?)
        ''', (MAC, x, y))
        conn.commit()

    def getCache(self, MAC):

        conn = sqlite3.connect('cache.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT x, y FROM cache WHERE mac=?
        ''', (MAC,))
        result = cursor.fetchone()

        if result:
            x, y = result
            return (x, y), True
        else:
            # Handle case where MAC address is not found in cache
            return None, False

    def sendServerGracefully(self, server, client, message):
            try:
                # print("message sending :" + message[0:10])
                server.send_message(client, message)
            except BrokenPipeError as e:
                print(f"client {client.get('id')} not found, removing it: {e}")

                if client["id"] in self.espConnections:
                    for c in self.espConnections[str(client["id"])]["coord"]:
                        if c != (None, None):
                            self.coordConnections.pop(c, None)
                
                self.espConnections.pop(str(client["id"]), None)

                if self.admin["admin"] != None:
                    self.getClientState(self.admin["admin"][0], server)
    
    def ping_clients(self, server):
        while True:
            try:
                print("Checking for clients to remove")
                time.sleep(20)
                for client_id in list(self.espConnections):
                    if client_id not in self.pingTimes:
                        self.ping(f"ping {client_id}", server)
 
                #print(self.pingTimes)
                curTime = time.time()

                pingedToRemove = []
                for pinged in list(self.pingTimes):
                    
                    #print(curTime - self.pingTimes[pinged])
                    if curTime - self.pingTimes[pinged] > 5:
                        # ping not found, removing
                        # print(f"ping not found removing {pinged}")

                        pingedToRemove.append(pinged)

                        if pinged in list(self.espConnections):
                            for c in self.espConnections[pinged]["coord"]:
                                if c != (None, None):
                                    self.coordConnections.pop(c, None)

                        if pinged in list(self.espConnections):
                            self.espConnections[pinged]["clientVal"]["handler"].connection.close()
                            self.espConnections.pop(pinged, None)

                if (len(pingedToRemove) > 0):
                    print("Ping not found, removing the following ESPs: ", pingedToRemove)

                for p in list(pingedToRemove):
                    self.pingTimes.pop(p, None)
                
                if len(pingedToRemove) > 0 and self.admin["admin"] != None:
                    self.sendServerGracefully(server, self.admin["admin"][0], json.dumps({"type": "update", "data": ""}))

            except Exception as e:
                print(f"An error occurred in ping_clients: {e}")
                print(traceback.format_exc())

    def start_ping_thread(self, server):
        ping_thread = threading.Thread(target=self.ping_clients, args=(server,))
        ping_thread.daemon = True
        ping_thread.start()

    def ping(self, message, server):
        cmd, clientID = message.split()

        if clientID not in self.espConnections:
            print(f"ERROR: {clientID} not connected to server yet")
            # server.send_message(client, json.dumps({"ERROR": f"{clientID} not connected to server yet"}))
            self.sendServerGracefully(server, client, json.dumps({"ERROR": f"{clientID} not connected to server yet"}))
            return

        self.pingTimes[clientID] = time.time()

        if self.getIDtoAddr(clientID) != None:
            self.udpPings[self.getIDtoAddr(clientID)]["start"] = self.pingTimes[clientID]

            self.sock.sendto("ping".encode(), self.getIDtoAddr(clientID))
            self.sock.sendto("ping".encode(), self.getIDtoAddr(clientID))

        # server.send_message(self.espConnections[clientID]["clientVal"], "ping")
        self.sendServerGracefully(server, self.espConnections[clientID]["clientVal"], "ping")
    
    def pong(self, message, client, server):
        # Send message to server saying this client has responded

        # self.player1["player"] != None and  (can add this back later once we specifc player1 behavior)
        # self.player1["player"] != None and 
        # print(client["id"], self.pingTimes)
        if str(client["id"]) in self.pingTimes:
            timeDif = time.time() - self.pingTimes[str(client["id"])]

            self.savedPingTimes[str(client["id"])] = int(timeDif * 1000)
            self.pingTimes.pop(str(client["id"]), None)
            clientIDText = str(client["id"])
            #print(f"client {clientIDText} pong timeDif: {int(timeDif * 1000)}")

            # going to send to client for now but change to player1 at some point self.player1["player"][0] /TODO
            # server.send_message(client, json.dumps({"pong": client["id"], "timeDif": int(timeDif * 1000)}))

            # I think for now I actually want this to send to client
            # self.sendServerGracefully(server, client, json.dumps({"pong": client["id"], "timeDif": int(timeDif * 1000)}))
            # self.sendServerGracefully(server, client, "Mili:" + str(timeDif * 1000))
            curTimeMilis = int(time.time() * 1000)
            self.sendServerGracefully(server, client, json.dumps({"time": curTimeMilis % 1000000000, "timeDif": int((timeDif * 1000000))/1000}))
        else: # TODO
            # server.send_message(client, json.dumps({"ERROR": f"{str(client['id'])} did not send a ping"}))
            self.sendServerGracefully(server, client, json.dumps({"ERROR": f"{str(client['id'])} did not send a ping"}))

    def setCoords(self, message, client, server):
        cmd, clientText, x, y = message.split()

        # coord has already been added once so we have to remove old coord color
        if (int(x), int(y)) in self.coordConnections:
            oldClient = self.coordConnections[(int(x), int(y))]["clientID"]

            if oldClient in self.espConnections:
                # THos line would have to be abstracted to include more than 2 coords
                self.espConnections[oldClient]["coord"] = [(None, None)] * self.LEDPerEsp["value"]
                self.setColor(f"setColor {oldClient} #000000", client, server)

        # client is not in connections
        if clientText not in self.espConnections:
            print(f"ERROR: {clientText} not connected to server yet")
            # server.send_message(client, json.dumps({"ERROR": f"{clientText} not connected to server yet"}))
            ##self.sendServerGracefully(server, client, json.dumps({"ERROR": f"{clientText} not connected to server yet"}))
            return

        # IDK why tbut this breaks everything and causes a bunch of resets
        if self.cacheBool: # this is also run when server.py enables cache so beware of redudency
            # print("Trying to CACHCE: " + clientText + " With MAC ADDRESS: "+ self.espConnections[clientText]["MAC"])
            # print(self.getCache(self.espConnections[clientText]["MAC"]))
            # print((x, y))
            #print(self.espConnections)

            res, boolVal = self.getCache(self.espConnections[clientText]["MAC"])

            if (res != (int(x), int(y))):
                self.setCache(self.espConnections[clientText]["MAC"], x, y)

        # so if we want to make this work for a variable number per ESP then we need to
        # If amount changed, remove cache and current list of connected
        # Or have a for loop to go through and reassign
        # The # of ESPs will stay the same so thats constant, but the coords will change
        # Maybe a Tree of ESP and their children coords could help the conversion
        # but tbh espConnections already does that, so it may just need to get abstracted

        # self.LEDsPerESP 

        # So we have set an ESP to a slot, meaning 
        
    
        for i in range(self.LEDPerEsp["value"]):
            # print((int(x) + i, int(y)))
            self.coordConnections[(int(x) + i, int(y))] = {"client" : self.espConnections[clientText]["clientVal"], "clientID": clientText}
            self.espConnections[clientText]["coord"][i] = (int(x) + i, int(y)) # might have to remove this

        # # set new coord details
        # self.coordConnections[(int(x), int(y))] = {"client" : self.espConnections[clientText]["clientVal"], "clientID": clientText}
        # self.coordConnections[(int(x) + 1, int(y))] = {"client" : self.espConnections[clientText]["clientVal"], "clientID": clientText}
        # self.espConnections[clientText]["coord"][0] = (int(x), int(y)) # might have to remove this
        # self.espConnections[clientText]["coord"][1] = (int(x) + 1, int(y)) # might have to remove this

    #### GETTERS AND SETTERS TO HELP WITH COORD SPACE
    def getLEDColor(self, coord):
        # so if I have (1,0) I need to get 0[1]
        # if I have (2,0) I need to get 1[0]
        # so its like mod 2 of the coord to get which value
        return self.espConnections[self.coordConnections[coord]["clientID"]]["color"][coord[0] % self.LEDPerEsp["value"]]
    
    def setLEDColor(self, coord, color):
        if coord in self.coordConnections:
            self.espConnections[self.coordConnections[coord]["clientID"]]["color"][coord[0] % self.LEDPerEsp["value"]] = color
    
    def getClientObj(self, coord):
        return self.espConnections[self.coordConnections[coord]["clientID"]]["clientVal"]
    ############################

    def setStripColor(self, message, client, server):
        messageSplit = message.split()

        cmd, clientID, color, strip = messageSplit
        if clientID not in self.espConnections:
            print(f"ERROR: {clientID} not connected to server yet")
            #server.send_message(client, json.dumps({"ERROR": f"{clientID} not connected to server yet"}))
            self.sendServerGracefully(server, client, json.dumps({"ERROR": f"{clientID} not connected to server yet"}))
            return
        
        if strip not in [str(v + 1) for v in range(1, self.LEDPerEsp["value"] + 1)]:
            self.sendServerGracefully(server, client, json.dumps({"ERROR": f"{strip} is not a valid strip value"}))
            return

        if strip == str(self.LEDPerEsp["value"] + 1): 
            self.espConnections[clientID]["color"] = [color] * self.LEDPerEsp["value"]
        else:
            self.espConnections[clientID]["color"][int(strip) - 1] = color
        #server.send_message(self.espConnections[clientID]["clientVal"], color)
        newColorCommand = "$" + str(self.LEDPerEsp["value"]) + f"-{strip}{color}"

        if (clientID in self.espConnections):
            self.sendServerGracefully(server, self.espConnections[clientID]["clientVal"], newColorCommand)
            print(f"Set color strip {strip} of {clientID} to {color}")


    def setColor(self, message, client, server):
        # if client["id"] == self.game["clientID"]:
        #     print("received setColor from game client")
        #     return
        messageSplit = message.split()

        # if you are trying to turn on a LED that doesnt have a set coord
        if len(messageSplit) == 3:
            cmd, clientID, color = messageSplit
            if clientID not in self.espConnections:
                print(f"ERROR: {clientID} not connected to server yet")
                #server.send_message(client, json.dumps({"ERROR": f"{clientID} not connected to server yet"}))
                self.sendServerGracefully(server, client, json.dumps({"ERROR": f"{clientID} not connected to server yet"}))
                return

            self.espConnections[clientID]["color"] = [color] * self.LEDPerEsp["value"]
            newColorCommand = "$" + str(self.LEDPerEsp["value"]) + "-" + str(self.LEDPerEsp["value"] + 1) + color
            #server.send_message(self.espConnections[clientID]["clientVal"], color)

            self.sendServerGracefully(server, self.espConnections[clientID]["clientVal"], newColorCommand)

            if (clientID in self.espConnections):
                if self.getIDtoAddr(clientID) != None and self.udpOn:
                    self.sock.sendto(newColorCommand.encode(), self.getIDtoAddr(clientID))
                    print(f"[bold][purple on white]🎁 UDP: [/] No Coord Assigned - Set color of {clientID} to [blue on {color}]{color}[/][/bold]")
                else:
                    self.sendServerGracefully(server, self.espConnections[clientID]["clientVal"], newColorCommand)
                    print(f"[bold][green on white]🎁 WS: [/] No Coord Assigned - Set color of {client.get('id')} to [blue on {color}]{color}[/][/bold]")


        # if you are turning on an LED with a set coord
        else:
            cmd, x, y, color = messageSplit
            # coord -> esp - > color,       esp -> color
            if (int(x), int(y)) not in self.coordConnections:
                print(f"ERROR: ({x}, {y}) does not have an ESP set yet!")
                self.sendServerGracefully(server, client, json.dumps({"ERROR": f"({x}, {y}) does not have an ESP set yet!"}))
                return
        
            self.setLEDColor((int(x), int(y)), color)
            stripNum = ((int(x)) % self.LEDPerEsp["value"]) + 1 # TODO if its not big mode we have to color both here

            if self.batchSendDelay["value"] == 0:
                client = self.getClientObj((int(x), int(y)))
                newColorCommand = "$" + str(self.LEDPerEsp["value"]) + f"-{stripNum}{color}"
                
                # Send over UDP
                if self.getIDtoAddr(client["id"]) != None and self.udpOn:
                    print(f"[bold][purple on white]🎁 UDP: [/] Set color of {client.get('id')} to [blue on {color}]{color}[/][/bold]")
                    self.sock.sendto(newColorCommand.encode(), self.getIDtoAddr(client["id"]))
                else:
                    print(f"[bold][green on white]🎁 WS: [/] Set color of {client.get('id')} to [blue on {color}]{color}[/][/bold]")
                    self.sendServerGracefully(server, client, newColorCommand)
            else:
                client = self.getClientObj((int(x), int(y)))
                self.batchedColors.setdefault(client["id"], {"client": client, "batched": []})["batched"].append({"stripNum": stripNum, "color": color})
        
    def getClientState(self, client, server):
        # Creates data with from [{id1, x, y, color}, {id2, x, y, color}, ...]
        clientData = []
        for i in self.espConnections.keys():

            ping = None
            udpPing = None
            if i in self.savedPingTimes:
                ping = self.savedPingTimes[i]
                udpPing = self.udpPings[self.getIDtoAddr(i)]["ping"]
                
            clientData.append({"clientName": i, "ping": ping, "udpPing": udpPing, "colors": self.espConnections[i]["color"], "coords": self.espConnections[i]["coord"]})


        # print(self.espConnections)
        # print(self.macConnections)
        clientData = {"type": "getClientState", "LEDPerEsp": self.LEDPerEsp["value"], "batchDelay": self.batchSendDelay["value"] * 1000, "data": clientData}

        # print(clientData)

        clientText = json.dumps(clientData)
        #print(clientText)
        #server.send_message(client, clientText)
        self.sendServerGracefully(server, client, clientText)

    
    def getInfo(self, message, client, server):
        messageSplit = message.split()

        # Message will either be of format
        # info get ESP#
        # info {json of info}

        # if you are trying to turn on a LED that doesnt have a set coord
        if len(messageSplit) == 3:
            cmd, action, espID = messageSplit

            # in this case the admin is asking us to get info from a specfic ESP
            self.sendServerGracefully(server, self.espConnections[espID]["clientVal"], "info:" + espID)

        else:
            cmd, firemwareJSON = messageSplit
            
            # this means we got info that we need to send to the admin

            self.sendServerGracefully(server, self.admin["admin"][0], firemwareJSON)

    def updateESP(self, message, client, server):
        messageSplit = message.split()

        if len(messageSplit) == 2:
            cmd, espID = messageSplit

            if (espID == "all"):
                for e in self.espConnections:
                    self.sendServerGracefully(server, self.espConnections[e]["clientVal"], "update")
            else:
                self.sendServerGracefully(server, self.espConnections[espID]["clientVal"], "update")
        
        else:

            print("INVALID ESP ID TO UPDATE")
        
    
    def setLEDPerEsp(self, message, client, server):
        messageSplit = message.split()

        if len(messageSplit) == 2:
            cmd, num = messageSplit
            print("Setting LED PER ESP: " + num)

            if int(num) % 2 == 0:

                # we have to reconfigure a lot of stuff here
                oldLedsPerStrip = self.LEDPerEsp["value"]
                self.LEDPerEsp["value"] = int(num)

                # 4 
                self.coordConnections = {}

                for esp in self.espConnections:
                    oldCoords = self.espConnections[esp]["coord"]

                    # 4 - 2 = 2
                    # ([0,0] [0,1]) => ([0,0] [0,1], [0,2] [0,3])

                    # 6 - 2 = 4
                    # ([0,0] [0,1]) => ([0,0] [0,1], [0,2] [0,3], [0,4], [0,5])
                    # [(1,0), (1,1), (1,2)]

                    # going from 8 to 4 or downwards gliches it
                    # lets try 4 2
                    # [(4,0), (5,0), (6,0), (7,0)] => [(2,0), (3,0)]
                    # instead the code is doing 
                    # [(2 * 4 + 0,0), (2 * 4 + 1,0)] => [(8,0), (9,0)]

                    # best way to do this, find where we are X wise in the coord plane

                    # self.coordConnections[(int(x), int(y))] = {"client" : self.espConnections[clientText]["clientVal"], "clientID": clientText}
                    
                    # if oldCoords havent been assigned 
                    if (oldCoords[0][0] == None):
                        self.espConnections[esp]["coord"] = [(None, None)] * self.LEDPerEsp["value"]
                        self.espConnections[esp]["color"] = ["#000000"] * self.LEDPerEsp["value"]
                    else:   
                        # print("BRRUUUH") 
                        # print(oldCoords)
                        # print(oprint(ldLedsPerStrip)
                        coordX = oldCoords[0][0] / oldLedsPerStrip
                        newCoords = [(coordX * self.LEDPerEsp["value"] + i, oldCoords[0][1]) for i in range(0, self.LEDPerEsp["value"])]
                        # print(newCoords)
                        # if (oldCoords[0][0] == 0):
                        #     coordX = 0
                                
                        #print("BRRUUUH")
                        #print(oldCoords)
                        ##newCoords = [(2 * oldCoords[0][0] + i, oldCoords[0][1]) for i in range(0, self.LEDPerEsp["value"])]
                        #print(newCoords)
                        self.espConnections[esp]["coord"] = newCoords
                        self.espConnections[esp]["color"] = ["#000000"] * self.LEDPerEsp["value"]

                        for i, val in enumerate(self.espConnections[esp]["coord"]):
                            self.coordConnections[val] = {"client" : self.espConnections[esp]["clientVal"], "clientID": esp}

                # espConnections = {}
                # coordConnections = {}
                # espConnections[str(client["id"])] = {"clientVal": client, "MAC": MAC, "coord": [(None, None), (None, None)], "color": ["#000000", "#000000"]}

                # go through each of these and reassign based on the new coord 
            
            else:
                print("INVALID STRIP NUM - MUST BE EVEN")

        else:

            print("INVALID STRIP NUM - MUST BE A INT")

    
    def start_batch_color(self, server):
        batch_thread = threading.Thread(target=self.batchColor, args=(server,))
        batch_thread.daemon = True
        batch_thread.start()

    def batchColor(self, server):

        while(True):
            if self.batchSendDelay["value"] > 0:
                time.sleep(self.batchSendDelay["value"])

                clientsToPop = []

                # print("TRYING TO BATCH")
                # print(self.batchedColors)

                for ESPid in self.batchedColors:
                    
                    newColorCommand = "$" + str(self.LEDPerEsp["value"]) + "-" + \
                        "".join([f"{d['stripNum']}{d['color']}" for d in self.batchedColors[ESPid]["batched"]])

                    print("Sending New Batch Command: " + newColorCommand)

                    # Send over UDP
                    if self.getIDtoAddr(ESPid) != None and self.udpOn:
                        self.sock.sendto(newColorCommand.encode(), self.getIDtoAddr(ESPid))
                    else:
                        self.sendServerGracefully(server, self.batchedColors[ESPid]["client"], newColorCommand)
                    
                    #self.sendServerGracefully(server, self.batchedColors[ESPid]["client"], newColorCommand)

                    clientsToPop.append(ESPid)

                for ESPid in clientsToPop:
                    self.batchedColors.pop(ESPid)
    
    def setBatchDelay(self, message, client, server):
        messageSplit = message.split()

        if len(messageSplit) == 2:
            cmd, batchDelayMS = messageSplit

            print(f"Setting Batch Delay to {int(batchDelayMS)}")

            # time.sleep uses seconds so convert from MS to SECONDS
            self.batchSendDelay["value"] = int(batchDelayMS) / 1000
        
        else:

            print("INVALID BATCH DELAY COMMAND")

    def getIDtoAddr(self, clientID):
        if (str(clientID) in self.espConnections):
            return self.macConnections.get(self.espConnections[str(clientID)]["MAC"])["udp"]

        return None
    
    def getLEDState(self, client, server):
        ledState = {f"({coord[0]},{coord[1]})": self.getLEDColor(coord) for coord in self.coordConnections.keys()}
        ledMessage = {"type": "getLEDState", "data": ledState}
        #server.send_message(client, json.dumps(ledMessage))
        self.sendServerGracefully(server, client, json.dumps(ledMessage))
    
    def setAllLedsCoords(self, server, color):
        for coord in self.coordConnections.keys():
            espObj = self.getClientObj(coord)
            # server.send_message(espObj, color)
            self.sendServerGracefully(server, espObj, color)

    def setAllLeds(self, server, color):
        for esp in list(self.espConnections.keys()):
            # server.send_message(self.espConnections[esp]["clientVal"], color)
            # self.espConnections[esp]["color"] = color
            # self.sendServerGracefully(server, self.espConnections[esp]["clientVal"], color)
            self.setColor(f"setColor {esp} {color}", self.espConnections[esp]["clientVal"], server)

    def loadTest(self, server):
        # the time.sleep() makes it so nobody can see the end color
        self.setAllLeds(server, "#FF0000")
        time.sleep(1.5)
        self.setAllLeds(server, "#000000")
        time.sleep(1.5)
        self.setAllLeds(server, "#00FF00")
        time.sleep(1.5)
        self.setAllLeds(server, "#FF00FF")

    def allOff(self, server):
        self.setAllLeds(server, "#000000")

    def cacheOn(self, client, server):
        self.cacheBool = True

        conn = sqlite3.connect('cache.db')
        cursor = conn.cursor()

        espKeys = list(self.espConnections.keys())
        for esp in espKeys:
            espVal = self.espConnections[esp]

            coord, foundCache = self.getCache(espVal["MAC"])
            if foundCache:
                self.setCoords(f"setCoords {esp} {coord[0]} {coord[1]}", client, server)

    def cacheOff(self, server):
        self.cacheBool = False

    def udpToggle(self, server):
        self.udpOn = not self.udpOn
        if self.admin["admin"] != None:
            self.sendServerGracefully(server, self.admin["admin"][0], json.dumps({"type": "udp", "value": self.udpOn}))

    def removeCoord(self, message):
        cmd, clientText = message.split()

        print("Trying to Remove Coord")

        if clientText in self.espConnections:
            oldCoords = self.espConnections[clientText]["coord"]
            oldMac = self.espConnections[clientText]["MAC"]

            self.espConnections[clientText]["coord"] = [(None, None)] * self.LEDPerEsp["value"]
            # Change color here too?

            for oldC in oldCoords:
                if oldC in self.coordConnections:
                    self.coordConnections.pop(oldC, None)

            if self.cacheBool:
                conn = sqlite3.connect('cache.db')
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM cache WHERE mac = ?", (oldMac,))
                result = cursor.fetchone()
            
                if result:
                    # If the MAC address exists, remove it from the database
                    cursor.execute("DELETE FROM cache WHERE mac = ?", (oldMac,))
                    conn.commit()
                    print(f"MAC address {oldMac} removed successfully.")
                else:
                    print(f"MAC address {oldMac} not found in the database.")
            
            




    def checkClientConnections(self, server):
        espToRemove = []
        for esp in self.espConnections.keys():
            print(f"testing {esp}")
            client = self.espConnections[esp]["clientVal"]
            try:
                server.send_message(client, "#FFFF00")
                server.send_message(client, "#FF00FF")
            except BrokenPipeError as e:
                print(f"client {client.get('id')} not found, removing it: {e}")

                if client["id"] in self.espConnections and self.espConnections[str(client["id"])]["coord"] != (None, None):
                    coordVal = self.espConnections[str(client["id"])]["coord"]
                    self.coordConnections.pop(coordVal, None)
                
                espToRemove.append(str(client["id"]))
                client["handler"].connection.close()
                #self.espConnections.pop(str(client["id"]), None)
        
        print(f"removing {len(espToRemove)} values")
        for esp in espToRemove:
            self.espConnections.pop(esp, None)
        
        if self.admin["admin"] != None:
            self.sendServerGracefully(server, self.admin["admin"][0], json.dumps({"type": "update", "data": ""}))

    #### Game Functionality ####
    def receivePlayerInput(self, message, client, server):
        if not self.player["client"] or client["id"] != self.player["clientID"]:
            self.sendServerGracefully(server, client, json.dumps({"ERROR": "not player client or player client not yet connected"}))
        cmd, playerInput = message.split(" ")
        ## Game stuff here
        print(playerInput)


    #########################

    def executeCommands(self, possibleCommands, message, client, server):
        if message == "":
            # server.send_message(client, json.dumps({"ERROR": "invalid command"}))
            self.sendServerGracefully(server, client, json.dumps({"ERROR": "invalid command"}))
            return

        if message.split(" ")[0] not in possibleCommands.keys():
            # server.send_message(client, json.dumps({"ERROR": "invalid command"}))
            self.sendServerGracefully(server, client, json.dumps({"ERROR": "invalid command"}))
            return

        # Command found!
        commandName = message.split(" ")[0]
        commandFunc = possibleCommands[commandName]["func"]
        commandArgs = possibleCommands[commandName]["args"]

        # bug happens if theres only one argument where it splits it into a list
        # print("Command Args: " + str(commandArgs), len(commandArgs))
        # print()
        if len(commandArgs) == 1:
            commandFunc(commandArgs[0])
        else:
            commandFunc(*commandArgs)
