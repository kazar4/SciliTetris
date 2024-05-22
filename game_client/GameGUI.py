import pygame
import sys

from games.tetris import TetrisApp
from games.snake import Snake
from games.canvas import CanvasGame

class Menu:
    def __init__(self, screen_width=800, screen_height=700):
        # Initialize Pygame
        pygame.init()

        # Screen dimensions
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Create the screen object
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Simple Menu')

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.DARK_GRAY = (100, 100, 100)

        # Fonts
        self.font = pygame.font.Font(None, 50)

        # Buttons
        self.buttons = [
            self.Button("Start Game", (300, 150), (200, 100), self.GRAY, self.DARK_GRAY, self.font, self.start_game),
            self.Button("Canvas Game", (300, 300), (200, 100), self.GRAY, self.DARK_GRAY, self.font, self.start_canvas_game),
            self.Button("Quit", (300, 450), (200, 100), self.GRAY, self.DARK_GRAY, self.font, self.quit_game)
        ]

        self.game_instance = None
        self.running = True

    class Button:
        def __init__(self, text, pos, size, color, hover_color, font, callback):
            self.text = text
            self.pos = pos
            self.size = size
            self.color = color
            self.hover_color = hover_color
            self.font = font
            self.callback = callback
            self.rect = pygame.Rect(pos, size)
        
        def draw(self, screen):
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, self.hover_color, self.rect)
            else:
                pygame.draw.rect(screen, self.color, self.rect)
            text_surf = self.font.render(self.text, True, pygame.Color('white'))
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)
        
        def is_clicked(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.callback()

    def start_game(self):
        # self.running = False
        self.game_instance = Game(self.screen)

    def start_canvas_game(self):
        # self.running = False
        self.game_instance = CanvasGame(self.screen)

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def get_board(self):
        if self.game_instance:
            return self.game_instance.get_board()
        return [[]]

    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for button in self.buttons:
                    if button.is_clicked(event):
                        button.callback()

            self.screen.fill(self.WHITE)
            if not self.game_instance:
                for button in self.buttons:
                    button.draw(self.screen)

            pygame.display.flip()
            clock.tick(60) 

            if self.game_instance:
                self.game_instance.run()
                # After game finishes running, return to main menu
                self.game_instance = None


if __name__ == "__main__":
    menu = Menu()
    menu.run()
