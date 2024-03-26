from websocket_server import WebsocketServer

espClient = None
player1 = None

# Called for every client connecting (after handshake)
def new_client(client, server):
    global espClient, player1
    print("New client connected and was given id %d" % client['id'])
    #server.send_message_to_all("Hey all, a new client has joined us")


    # # TODO MAKE IT CHECK FOR CORRECT MAC ADDRESS
    # if espClient == None:
    #     espClient = (client, client['id'])
    # elif player1 == None:
    #     player1 = (client, client['id'])	


# Called for every client disconnecting
def client_left(client, server):
    global espClient, player1
    print("Client(%d) disconnected" % client['id'])

    if player1 != None and client["id"] == player1[1]:
        print("player1 disconnected")
        player1 = None
    
    # TODO GAME ERROR IF ESP DISCONNECTS RESTART GAME
    if espClient != None and client["id"] == espClient[1]:
        print("esp disconnected")
        espClient = None


# Called when a client sends a message
def message_received(client, server, message):
    global espClient, player1
    if len(message) > 200:
        message = message[:200]+'..'
    #print("Client(%d) said: %s" % (client['id'], message))
    #print(espClient, player1)

    if message == "ESP":
        print("Setting client " + str(client["id"]) + " to ESP")
        espClient = (client, client["id"])
        server.send_message(espClient[0], "ESP Connected")
        return
    if message == "player1":
        print("Setting client " + str(client["id"]) + " to player1")
        player1 = (client, client["id"])
        server.send_message(player1[0], "player1 Connected")
        return

    # TODOS
    # if any client says DISCONNECT ALL then disconnect all
    # server.clients = [] and set variables to None

    # Button to check that ESP is connected
    # sends a message to ESP "ping + ID"
    # then itll send back "pong + ID" and send back pong to that ID

    possibleCommands = ["U", "D", "L", "R", "Graphics", "SNAKE", "Ping", "Rainbow", "Glitter", "F", "S", "G", "WDT", "CB"]
    # only run back and forth if esp and player1 are connected
    if player1 != None and espClient != None and message:
        if message not in possibleCommands:
            server.send_message(client, "invalid command")
            return

        if client["id"] == espClient[1]:
            print("esp -> player: " + message)
            server.send_message(player1[0], message)
            return
        if client["id"] == player1[1]:
            print("player -> esp: " + message)
            server.send_message(espClient[0], message)
            return

PORT=9001
server = WebsocketServer(host='0.0.0.0', port=PORT, key="/ssl/server.key", cert="/ssl/server.crt")
#server = WebsocketServer(port = PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()

# ngrok http --domain=ruling-commonly-cricket.ngrok-free.app 9001