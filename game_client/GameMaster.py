import sys
import threading
import time
import websocket
import ssl
import asyncio

sys.path.append('game_client/games')

from games.tetris import TetrisApp
from games.snake import Snake

# Want to implement command line arguments to see which game to
# run, not yet implemented
possible_games = {
    "Tetris": TetrisApp,
    "Snake": Snake
}

_polling_rate = 0.1
# _uri = "ws://localhost:9001"
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
        self.game = possible_games["Snake"]()

        self.client_thread = threading.Thread(target=self.connect_to_server)
        self.client_thread.daemon = True
        self.client_thread.start() # Thread to run the game client connection

        self.polling_thread = threading.Thread(target=self.poll_game)
        self.polling_thread.daemon = True
        self.polling_thread.start() # Thread to poll the game

        self.game.run() # Main thread runs the game


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
            board = self.game.get_board()
            for y in range(len(board)):
                for x in range(len(board[0])):
                    message = "setColor " + str(x) + " " + str(y) + " " + board[y][x]
                    self.ws.send(message)
            time.sleep(_polling_rate)


if __name__ == "__main__":
    gm = GameMaster()
        