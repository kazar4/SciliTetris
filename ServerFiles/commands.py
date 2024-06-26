import json
import time
import sqlite3
import threading


class Commands:

    pingTimes = {}
    savedPingTimes = {}

    cacheBool = True

    def __init__(self, admin, player, game, espConnections, coordConnections):
        self.admin = admin
        self.player = player
        self.game = game
        self.espConnections = espConnections
        self.coordConnections = coordConnections
        
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
                server.send_message(client, message)
            except BrokenPipeError as e:
                print(f"client {client} not found, removing it:  {e}")

                if client["id"] in self.espConnections and self.espConnections[str(client["id"])]["coord"][0] != (None, None):
                    coordVal1 = self.espConnections[str(client["id"])]["coord"][0]
                    self.coordConnections.pop(coordVal1, None)
                if client["id"] in self.espConnections and self.espConnections[str(client["id"])]["coord"][1] != (None, None):
                    coordVal2 = self.espConnections[str(client["id"])]["coord"][1]
                    self.coordConnections.pop(coordVal2, None)
                
                self.espConnections.pop(str(client["id"]), None)

                print(self.admin)
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
                
                print("Checking for clients to remove")
                #print(self.pingTimes)
                curTime = time.time()

                pingedToRemove = []
                for pinged in list(self.pingTimes):
                    
                    #print(curTime - self.pingTimes[pinged])
                    if curTime - self.pingTimes[pinged] > 5:
                        # ping not found, removing
                        print(f"ping not found removing {pinged}")

                        pingedToRemove.append(pinged)

                        # REMOVING
                        if pinged in list(self.espConnections) and self.espConnections[pinged]["coord"][0] != (None, None):
                            coordVal1 = self.espConnections[pinged]["coord"][0]
                            self.coordConnections.pop(coordVal1, None)
                        if pinged in list(self.espConnections) and self.espConnections[pinged]["coord"][1] != (None, None):
                            coordVal2 = self.espConnections[pinged]["coord"][1]
                            self.coordConnections.pop(coordVal2, None)
                        
                        if pinged in list(self.espConnections):
                            self.espConnections[pinged]["clientVal"]["handler"].connection.close()
                            self.espConnections.pop(pinged, None)

                for p in list(pingedToRemove):
                    self.pingTimes.pop(p, None)
                
                if len(pingedToRemove) > 0 and self.admin["admin"] != None:
                    self.sendServerGracefully(server, self.admin["admin"][0], json.dumps({"type": "update", "data": ""}))

            except Exception as e:
                print(f"An error occurred in ping_clients: {e}")

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
                self.espConnections[oldClient]["coord"] = [(None, None), (None, None)]
                self.setColor(f"setColor {oldClient} #000000", client, server)

        # client is not in connections
        if clientText not in self.espConnections:
            print(f"ERROR: {clientText} not connected to server yet")
            # server.send_message(client, json.dumps({"ERROR": f"{clientText} not connected to server yet"}))
            ##self.sendServerGracefully(server, client, json.dumps({"ERROR": f"{clientText} not connected to server yet"}))
            return

        if self.cacheBool: # this is also run when server.py enables cache so beware of redudency
            self.setCache(self.espConnections[clientText]["MAC"], x, y)

        # set new coord details
        self.coordConnections[(int(x), int(y))] = {"client" : self.espConnections[clientText]["clientVal"], "clientID": clientText}
        self.coordConnections[(int(x) + 1, int(y))] = {"client" : self.espConnections[clientText]["clientVal"], "clientID": clientText}
        self.espConnections[clientText]["coord"][0] = (int(x), int(y)) # might have to remove this
        self.espConnections[clientText]["coord"][1] = (int(x) + 1, int(y)) # might have to remove this

    #### GETTERS AND SETTERS TO HELP WITH COORD SPACE
    def getLEDColor(self, coord):
        # so if I have (1,0) I need to get 0[1]
        # if I have (2,0) I need to get 1[0]
        # so its like mod 2 of the coord to get which value
        return self.espConnections[self.coordConnections[coord]["clientID"]]["color"][coord[0] % 2]
    
    def setLEDColor(self, coord, color):
        if coord in self.coordConnections:
            self.espConnections[self.coordConnections[coord]["clientID"]]["color"][coord[0] % 2] = color
    
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
        
        if strip not in ["1", "2", "3"]:
            self.sendServerGracefully(server, client, json.dumps({"ERROR": f"{strip} is not a valid strip value"}))
            return

        if strip == "3":
            self.espConnections[clientID]["color"] = [color, color]
        else:
            self.espConnections[clientID]["color"][int(strip) - 1] = color
        #server.send_message(self.espConnections[clientID]["clientVal"], color)
        self.sendServerGracefully(server, self.espConnections[clientID]["clientVal"], f"${strip}{color}")
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

            #print(f"Trying to color of {clientID} to {color}")

            self.espConnections[clientID]["color"][0] = color
            self.espConnections[clientID]["color"][1] = color
            print(f"Trying to color of {clientID} to {color} 2")
            #server.send_message(self.espConnections[clientID]["clientVal"], color)
            self.sendServerGracefully(server, self.espConnections[clientID]["clientVal"], "$3" + color)
            print(f"Set color of {clientID} to {color}")

        # if you are turning on an LED with a set coord
        else:
            cmd, x, y, color = messageSplit
            # coord -> esp - > color,       esp -> color
            if (int(x), int(y)) not in self.coordConnections:
                print(f"ERROR: ({x}, {y}) does not have an ESP set yet!")
                self.sendServerGracefully(server, client, json.dumps({"ERROR": f"({x}, {y}) does not have an ESP set yet!"}))
                return
        
            self.setLEDColor((int(x), int(y)), color)
            stripNum = (int(x) % 2) + 1 # TODO if its not big mode we have to color both here
            self.sendServerGracefully(server, self.getClientObj((int(x), int(y))), f"${stripNum}{color}")
    
    def getClientState(self, client, server):
        # Creates data with from [{id1, x, y, color}, {id2, x, y, color}, ...]
        clientData = []
        for i in self.espConnections.keys():
            if self.espConnections[i]["coord"] != [(None, None), (None, None)]:
                xVal1, yVal1 = self.espConnections[i]["coord"][0][0], self.espConnections[i]["coord"][0][1]
                xVal2, yVal2 = self.espConnections[i]["coord"][1][0], self.espConnections[i]["coord"][1][1]
                color1, color2 = self.espConnections[i]["color"][0], self.espConnections[i]["color"][1]

                ping = None
                if i in self.savedPingTimes:
                    ping = self.savedPingTimes[i]

                clientData.append({"clientName": i, "x1": xVal1, "y1": yVal1, "color1": color1, "x2": xVal2, "y2": yVal2, "color2": color2, "ping": ping})
            else:
                color1, color2 = self.espConnections[i]["color"][0], self.espConnections[i]["color"][1]

                ping = None
                if i in self.savedPingTimes:
                    ping = self.savedPingTimes[i]
                
                clientData.append({"clientName": i, "x1": None, "y1": None, "color1": color1, "x2": None, "y2": None, "color2": color2, "ping": ping})


        #print(self.espConnections)
        clientData = {"type": "getClientState", "data": clientData}

        # print(clientData)

        clientText = json.dumps(clientData)
        #print(clientText)
        #server.send_message(client, clientText)
        self.sendServerGracefully(server, client, clientText)
    
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

    def removeCoord(self, message):
        cmd, clientText = message.split()

        print("Trying to Remove Coord")

        if clientText in self.espConnections:
            oldCoord1 = self.espConnections[clientText]["coord"][0]
            oldCoord2 = self.espConnections[clientText]["coord"][1]
            oldMac = self.espConnections[clientText]["MAC"]

            self.espConnections[clientText]["coord"] = [(None, None), (None, None)]
            # Change color here too?

            if oldCoord1 in self.coordConnections:
                self.coordConnections.pop(oldCoord1, None)
            if oldCoord2 in self.coordConnections:
                self.coordConnections.pop(oldCoord2, None)
            
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
                print(f"client {client} not found, removing it:  {e}")

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
