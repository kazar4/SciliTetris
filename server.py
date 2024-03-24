from websocket_server import WebsocketServer
import sqlite3
import json

player1 = None

espConnections = {}
coordConnections = {}

# CONCLUSION -> Goes to do the SQL caching later when I have a 
# better idea of the structure of everything
# for now i'm fine doing manual reentry
# con = sqlite3.connect("data.db")
# c = con.cursor()

# c.execute('''
#         CREATE TABLE database(
#             mac VARCHAR not null,
#             x VARCHAR,
#             y VARCHAR,
#             PRIMARY KEY(mac))''')

# Connection loop is as follows:
# ESP turns op and connects
# ESP sends MAC Address
# If MAC Address is in database and there exists a X,Y Coord
# If X,Y coord is empty then allow connection and fill in data
# Otherwise, add espConnection() but await X,Y assignment

# Assignment is done via MAC to X,Y
# Grid is defined by GUI, and once grid is set it requires X * Y values to be set

# Question? Do I want controller to be a website or a tkiner
# tkiner is prob easier in most aspects
# but then I have to learn tkiner kinda well
# whereas website I just ooga booga a 

# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])
    #server.send_message_to_all("Hey all, a new client has joined us")

    # technically nothing should happen here

# Called for every client disconnecting
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])

    # check if client was 
    if client["id"] in espConnections:
        coordToDel = espConnections[client["id"]]["coord"]

        client.pop("id", None)
        if coordToDel in coordConnections:
            coordConnections.pop(coordToDel, None)

    # TODO: Message server so it knows that one of the connections dropped
    

# Called when a client sends a message
def message_received(client, server, message):
    if len(message) > 200:
        message = message[:200]+'..'
    #print("Client(%d) said: %s" % (client['id'], message))
    #print(espClient, player1)

    if message == "player1":
        print("Setting client " + str(client["id"]) + " to player1")
        player1 = (client, client["id"])
        server.send_message(player1[0], "player1 Connected")
        return


    # Set MAC ADDRESS -> only adds connection if MAC address is sent
    if message[0:1] == "M-":
        print("Setting client " + str(client["id"]) + "Mac Address of: " + message[1:])
        espConnections[client["id"]] = {"clientVal": client, "MAC": message[1:], "coord": (None, None)}
        return

    possibleCommands = ["ping", "pong", "setCoords", "setColor", "getClientState", "getLEDState"]
    if client["id"] in espConnections:
        if message not in possibleCommands:
            server.send_message(client, "invalid command")
            return

        # Possible commands here are: setCoords(client), setColor((x,y)), getClientState() -> client, x,y, color, getLEDState() -> x,y, color

        # check if a specfic client is currently responding       
        if "ping" in message:
            cmd, client = message.split()

            server.send_message(espConnections[client]["clientVal"], "Ping!")

        if "ping" in message:
            cmd = message.split() 
            # Send message to server saying this client has responded

        if "setCoords" in message:
            cmd, clientText, x, y = message.split()
            coordConnections[(int(x), int(y))] = {"client" : espConnections[clientText]["clientVal"], "color": '#000000'}
            espConnections[espConnections[clientText]]["coord"] = (int(x), int(y)) # might have to remove this
        
        if "setColor" in message:
            cmd, x, y, color = message.split()
            if (int(x), int(y)) not in coordConnections:
                print(f"ERROR: ({x}, {y}) does not have an ESP set yet!")
                return # TODO eventually send am essage back to user
            
            coordConnections[(int(x), int(y))]["coord"] = color
        
        if "getClientState" in message:

            # Creates data with from [{id1, x, y, color}, {id2, x, y, color}, ...]
            clientData = []
            for i in espConnections.keys():
                xVal = espConnections[i]["coord"][0]
                yVal = espConnections[i]["coord"][1]
                clientData.append({"clientName": i, "x": xVal, "y": yVal, "color": coordConnections.get((xVal, yVal), None)})

            clientData = {"data: ": clientData}

            clientText = json.dumps(clientData)
            server.send_message(client, clientText)
        
        if "getLEDState" in message:

            ledState = json.dumps({f"{coord[0]}-{coord[1]}":coordConnections[coord]["color"] for coord in coordConnections.keys()})
            server.send_message(client, ledState)



        ## WHOA -> for tetris/snake we will have another websocket that we connect to that is kinda like a
        # ____ (im forgetting the word), so it goes website -> websocket1 > this websocket
        # basically an abstraction as websocket1 will handle all the game coloring so all the website has to do is send
        # colors



PORT=9001
server = WebsocketServer(host='0.0.0.0', port=PORT)
                         #, key="/ssl/server.key", cert="/ssl/server.crt")
#server = WebsocketServer(port = PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()

# ngrok http --domain=ruling-commonly-cricket.ngrok-free.app 9001