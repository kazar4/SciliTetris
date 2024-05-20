from websocket_server import WebsocketServer
import sqlite3
import json
import commands

admin = {"admin": None}
player = {"client": None, "clientID": None}
game = {"game": None, "clientID": None}
espConnections = {}
coordConnections = {}

commands = commands.Commands(admin, player, game, espConnections, coordConnections)

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

    if client["id"] == admin["admin"]:
        admin["admin"] = (None, None)
    if client["id"] == player["clientID"]:
        player["client"] = None
        player["clientID"] = None
    if client["id"] == game["clientID"]:
        game["client"] = None
        game["clientID"] = None

    # check if esp disconnected and empty data strucutre
    if client["id"] in espConnections:
        coordToDel = espConnections[client["id"]]["coord"]

        client.pop("id", None)
        if coordToDel in coordConnections:
            coordConnections.pop(coordToDel, None)

    # TODO: Message server so it knows that one of the connections dropped
    

# Called when a client sends a message
def message_received(client, server, message):
    global espConnection, coordConnections

    if len(message) > 200:
        message = message[:200]+'..'
    #print("Client(%d) said: %s" % (client['id'], message))
    #print(espClient, player1)

    print("message: " + message)

    if message == "admin":
        print("Setting client " + str(client["id"]) + " to admin")
        admin["admin"] = (client, client["id"])
        #server.send_message(admin["admin"][0], "admin Connected")
        return
    
    if message == "player":
        print("Setting client " + str(client["id"]) + " as player")
        # player["player"] = (client, client["id"])
        player["client"] = client
        player["clientID"] = client["id"]
        return
    
    if message == "game":
        print("Setting client " + str(client["id"]) + " as game")
        game["client"] = client
        game["clientID"] = client["id"]
        return

    # Set MAC ADDRESS -> only adds connection if MAC address is sent
    if message[0:2] == "M-":
        MAC = message[2:]
        print("Setting client " + str(client["id"]) + " Mac Address of: " + MAC)
        espConnections[str(client["id"])] = {"clientVal": client, "MAC": MAC, "coord": [(None, None), (None, None)], "color": ["#000000", "#000000"]}
        
        if commands.cacheBool:
            coord, foundCache = commands.getCache(MAC)
            if foundCache:
                commands.setCoords(f"setCoords {client['id']} {coord[0]} {coord[1]}", client, server)

        return
    

    possibleCommands =  {
        "ping": {"func": commands.ping, "args": (message, server)},
        "pong": {"func": commands.pong, "args": (message, client, server)},
        "setCoords": {"func": commands.setCoords, "args": (message, client, server)},
        "setColor": {"func": commands.setColor, "args": (message, client, server)},
        "getClientState": {"func": commands.getClientState, "args": (client, server)},
        "getLEDState": {"func": commands.getLEDState, "args": (client, server)},
        "loadTest": {"func": commands.loadTest, "args": [server]},
        "allOff": {"func": commands.allOff, "args": [server]},
        "checkClientConnections": {"func": commands.checkClientConnections, "args": [server]},
        "cacheOn": {"func": commands.cacheOn, "args": [client, server]},
        "cacheOff": {"func": commands.cacheOff, "args": [server]},
        "removeCoord": {"func": commands.removeCoord, "args": [message]},
        "setStripColor": {"func": commands.setStripColor, "args": (message, client, server)},
        "playerInput": {"func": commands.receivePlayerInput, "args": (message, client, server)}
    }
    
    commands.executeCommands(possibleCommands, message, client, server)

        ## WHOA -> for tetris/snake we will have another websocket that we connect to that is kinda like a
        # ____ (im forgetting the word), so it goes website -> websocket1 > this websocket
        # basically an abstraction as websocket1 will handle all the game coloring so all the website has to do is send
        # colors


#PORT=9001
PORT = 4567
# server = WebsocketServer(host='0.0.0.0', port=PORT, key="/ssl/server.key", cert="/ssl/server.crt")
server = WebsocketServer(host='0.0.0.0', port=PORT, key="/etc/letsencrypt/archive/proteinarium/privkey2.pem", cert="/etc/letsencrypt/archive/proteinarium/cert2.pem")
# server = WebsocketServer(host='localhost', port=PORT)

commands.start_ping_thread(server)

#server = WebsocketServer(port = PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()

# ngrok http --domain=ruling-commonly-cricket.ngrok-free.app 9001