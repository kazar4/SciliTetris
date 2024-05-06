import json
import time


class Commands:

    pingTimes = {}

    def __init__(self, player1, espConnections, coordConnections):
        self.player1 = player1
        self.espConnections = espConnections
        self.coordConnections = coordConnections

    def ping(self, message, server):
        cmd, clientID = message.split()

        if clientID not in self.espConnections:
            print(f"ERROR: {clientID} not connected to server yet")
            server.send_message(client, json.dumps({"ERROR": f"{clientID} not connected to server yet"}))
            return

        self.pingTimes[clientID] = time.time()
        server.send_message(self.espConnections[clientID]["clientVal"], "ping")
    
    def pong(self, message, client, server):
        # Send message to server saying this client has responded

        # self.player1["player"] != None and  (can add this back later once we specifc player1 behavior)
        # self.player1["player"] != None and 
        print(client["id"], self.pingTimes)
        if str(client["id"]) in self.pingTimes:
            timeDif = time.time() - self.pingTimes[str(client["id"])]
            self.pingTimes.pop(client["id"], None)
            clientIDText = str(client["id"])
            print(f"client {clientIDText} pong timeDif: {int(timeDif * 1000)}")

            # going to send to client for now but change to player1 at some point self.player1["player"][0] /TODO
            server.send_message(client, json.dumps({"pong": client["id"], "timeDif": int(timeDif * 1000)}))
        else: # TODO
            server.send_message(client, json.dumps({"ERROR": f"{str(client["id"])} did not send a ping"}))

    def setCoords(self, message, server):
        cmd, clientText, x, y = message.split()

        # coord has already been added once so we have to remove old coord color
        if (int(x), int(y)) in self.coordConnections:
            oldClient = self.coordConnections[(int(x), int(y))]["clientID"]
            self.espConnections[oldClient]["coord"] = (None, None)
            self.setColor(f"setColor {oldClient} #000000", server)

        if clientText not in self.espConnections:
            print(f"ERROR: {clientText} not connected to server yet")
            #TODO this should sendback to client that sent it or prob to admin
            #server.send_message(client, json.dumps({"ERROR": f"{clientText} not connected to server yet"}))
            return

        # set new coord details
        self.coordConnections[(int(x), int(y))] = {"client" : self.espConnections[clientText]["clientVal"], "clientID": clientText}
        self.espConnections[clientText]["coord"] = (int(x), int(y)) # might have to remove this

    #### GETTERS AND SETTERS TO HELP WITH COORD SPACE
    def getLEDColor(self, coord):
        return self.espConnections[self.coordConnections[coord]["clientID"]]["color"]
    
    def setLEDColor(self, coord, color):
        self.espConnections[self.coordConnections[coord]["clientID"]]["color"] = color
    
    def getClientObj(self, coord):
        return self.espConnections[self.coordConnections[coord]["clientID"]]["clientVal"]
    ############################

    def setColor(self, message, client, server):
        messageSplit = message.split()

        # if you are trying to turn on a LED that doesnt have a set coord
        if len(messageSplit) == 3:
            cmd, clientID, color = messageSplit
            if clientID not in self.espConnections:
                print(f"ERROR: {clientID} not connected to server yet")
                server.send_message(client, json.dumps({"ERROR": f"{clientID} not connected to server yet"}))
                return

            self.espConnections[clientID]["color"] = color
            server.send_message(self.espConnections[clientID]["clientVal"], "$3" + color)

        # if you are turning on an LED with a set coord
        else:
            cmd, x, y, color = messageSplit
            # coord -> esp - > color,       esp -> color
            if (int(x), int(y)) not in self.coordConnections:
                print(f"ERROR: ({x}, {y}) does not have an ESP set yet!")
                server.send_message(client, json.dumps({"ERROR": f"({x}, {y}) does not have an ESP set yet!"}))
                return
        
            self.setLEDColor((int(x), int(y)), color)
            server.send_message(self.getClientObj((int(x), int(y))), "$3" + color)
    
    def getClientState(self, client, server):
        # Creates data with from [{id1, x, y, color}, {id2, x, y, color}, ...]
        clientData = []
        for i in self.espConnections.keys():
            xVal = self.espConnections[i]["coord"][0]
            yVal = self.espConnections[i]["coord"][1]
            clientData.append({"clientName": i, "x": xVal, "y": yVal, "color": self.espConnections[i]["color"]})

        print(clientData)
        clientData = {"data: ": clientData}

        clientText = json.dumps(clientData)
        print(clientText)
        server.send_message(client, clientText)
    
    def getLEDState(self, client, server):
        ledState = {f"({coord[0]},{coord[1]})": self.getLEDColor(coord) for coord in self.coordConnections.keys()}
        ledState = json.dumps(ledState)
        server.send_message(client, ledState)
    
    def setAllLedsCoords(self, server, color):
        for coord in coordConnections.keys():
            espObj = self.getClientObj(coord)
            server.send_message(espObj, color)

    def setAllLeds(self, server, color):
        for esp in self.espConnections.keys():
            server.send_message(self.espConnections[esp]["clientVal"], "$3" + color)

    def loadTest(self, server):
        self.setAllLeds(server, "#FF0000")
        time.sleep(1.5)
        self.setAllLeds(server, "#000000")
        time.sleep(1.5)
        self.setAllLeds(server, "#00FF00")
        time.sleep(1.5)
        self.setAllLeds(server, "#FF00FF")

    def allOff(self, server):
        self.setAllLeds(server, "#000000")

    def executeCommands(self, possibleCommands, message, client, server):
        if message == "":
            server.send_message(client, "invalid command")
            return

        if message.split(" ")[0] not in possibleCommands.keys():
            server.send_message(client, "invalid command")
            return

        # Command found!
        commandName = message.split(" ")[0]
        commandFunc = possibleCommands[commandName]["func"]
        commandArgs = possibleCommands[commandName]["args"]

        # bug happens if theres only one argument where it splits it into a list
        print("Command Args: " + str(commandArgs), len(commandArgs))
        if len(commandArgs) == 1:
            commandFunc(commandArgs[0])
        else:
            commandFunc(*commandArgs)
