import sys
import threading
import time
import websocket
import ssl
import asyncio

from GameGUI import Menu


_polling_rate = 0.1
#_uri = "ws://localhost:9001"
_uri = "wss://kazar4.com:9001"

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    ws.send("game")
    print("Opened connection")

class GameMaster():
    def __init__(self) -> None:
        # self.game = possible_games["Snake"]()
        self.menu = Menu()
        self.prev_frame = None

        self.client_thread = threading.Thread(target=self.connect_to_server)
        self.client_thread.daemon = True
        self.client_thread.start() # Thread to run the game client connection

        self.polling_thread = threading.Thread(target=self.poll_game)
        self.polling_thread.daemon = True
        self.polling_thread.start() # Thread to poll the game

        self.menu.run() # Main thread runs the menu


    def connect_to_server(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(_uri,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})  

    def poll_game(self):
        while not self.ws or not self.ws.sock or not self.ws.sock.connected:
            time.sleep(_polling_rate)
        while True:
            if self.menu.game_instance:
                board = self.menu.game_instance.get_board()
                # new_pixels = 0
                for y in range(len(board)):
                    for x in range(len(board[0])):
                        if not self.prev_frame or self.prev_frame[y][x] != board[y][x]:
                            message = "setColor " + str(x) + " " + str(y) + " " + board[y][x]
                            self.ws.send(message)
                            # new_pixels += 1
                        # print(board[y][x])
                self.prev_frame = board
                time.sleep(_polling_rate)


if __name__ == "__main__":
    gm = GameMaster()
        