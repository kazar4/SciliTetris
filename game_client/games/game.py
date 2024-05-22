from abc import ABC, abstractmethod
from typing import List
import pygame

class Game(ABC):
    @abstractmethod
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

    @abstractmethod
    def run(self):
        # The main starting point of the game. This is so that GameMaster
        # can tell the game to start running at the appropriate time.
        pass

    @abstractmethod
    def get_board(self) -> List[List[str]]:
        # Return the board state of the game in the current frame. Should be a 2D grid of
        # colors represented as hexadecimals. 
        pass