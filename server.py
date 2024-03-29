from websocket_server import WebsocketServer
import sqlite3
import json
import commands

player1 = {"player": None}
espConnections = {}
coordConnections = {}

commands = commands.Commands(player1, espConnections, coordConnections)

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
    global player1

    print("Client(%d) disconnected" % client['id'])

    if client["id"] == player1["player"]:
        player1["player"] = None

    # check if esp disconnected and empty data strucutre
    if client["id"] in espConnections:
        coordToDel = espConnections[client["id"]]["coord"]

        client.pop("id", None)
        if coordToDel in coordConnections:
            coordConnections.pop(coordToDel, None)

    # TODO: Message server so it knows that one of the connections dropped
    

# Called when a client sends a message
def message_received(client, server, message):
    global player1, espConnection, coordConnections

    if len(message) > 200:
        message = message[:200]+'..'
    #print("Client(%d) said: %s" % (client['id'], message))
    #print(espClient, player1)

    print("message: " + message)

    if message == "player1":
        print("Setting client " + str(client["id"]) + " to player1")
        player1 = {"player": (client, client["id"])}
        server.send_message(player1["player"][0], "player1 Connected")
        return

    # Set MAC ADDRESS -> only adds connection if MAC address is sent
    if message[0:2] == "M-":
        print("Setting client " + str(client["id"]) + " Mac Address of: " + message[2:])
        espConnections[str(client["id"])] = {"clientVal": client, "MAC": message[1:], "coord": (None, None), "color": "#000000"}
        #print(espConnections)
        return

    possibleCommands =  {
        "ping": {"func": commands.ping, "args": (message, server)},
        "pong": {"func": commands.pong, "args": (message, client, server)},
        "setCoords": {"func": commands.setCoords, "args": (message, server)},
        "setColor": {"func": commands.setColor, "args": (message, client, server)},
        "getClientState": {"func": commands.getClientState, "args": (client, server)},
        "getLEDState": {"func": commands.getLEDState, "args": (client, server)},
        "loadTest": {"func": commands.loadTest, "args": [server]},
        "allOff": {"func": commands.allOff, "args": [server]}
    }
    
    commands.executeCommands(possibleCommands, message, client, server)

        ## WHOA -> for tetris/snake we will have another websocket that we connect to that is kinda like a
        # ____ (im forgetting the word), so it goes website -> websocket1 > this websocket
        # basically an abstraction as websocket1 will handle all the game coloring so all the website has to do is send
        # colors


PORT=9001
server = WebsocketServer(host='0.0.0.0', port=PORT, key="/ssl/server.key", cert="/ssl/server.crt")
#server = WebsocketServer(port = PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()

# ngrok http --domain=ruling-commonly-cricket.ngrok-free.app 9001