import sys
sys.path.append('game_client/games')

from games.tetris import TetrisApp

possible_games = {
    "Tetris": TetrisApp
}

class GameMaster():
    def __init__(self) -> None:
        self.game = possible_games["Tetris"]()
        self.game.run()


if __name__ == "__main__":
    gm = GameMaster()
