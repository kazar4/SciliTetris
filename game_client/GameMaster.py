import sys
import threading
import time
import websockets
import asyncio

sys.path.append('game_client/games')

from games.tetris import TetrisApp

possible_games = {
    "Tetris": TetrisApp
}

_polling_rate = 2
_uri = "ws://localhost:9001"

class GameMaster():
    def __init__(self) -> None:
        # Event loop management for server connections
        # self.loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(self.loop)
        self.connect_to_server()
        # self.loop.run_forever()

        self.game = possible_games["Tetris"]()

        self.polling_thread = threading.Thread(target=self.poll_game)
        self.polling_thread.daemon = True
        self.polling_thread.start()

        self.game.run() # Makes the main thread hang here

    def connect_to_server(self):
        # self.connection = asyncio.run(self.connect_async())
        self.connection = websockets.connect(_uri)
    
    async def connect_async(self):
        websocket = await websockets.connect(_uri)
        await websocket.send("game")
        return websocket

    async def send_to_server(self, message):
        await self.connection.send(message)

    def poll_game(self):
        while True:
            board = self.game.get_board()
            for y in range(len(board)):
                for x in range(len(board[0])):
                    message = "setColor " + str(x) + " " + str(y) + " " + board[y][x]
                    asyncio.run(self.send_to_server(message))
            time.sleep(_polling_rate)


if __name__ == "__main__":
    gm = GameMaster()
        