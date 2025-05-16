import pygame
from typing import List, Tuple
from games.game import Game

CELL_WIDTH = 20
CELL_HEIGHT = 20
GRID_WIDTH = 30
GRID_HEIGHT = 11
SCREEN_WIDTH = GRID_WIDTH * CELL_WIDTH
SCREEN_HEIGHT = GRID_HEIGHT * CELL_HEIGHT

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)
RED = (255, 80, 80)

def rgb_to_hex(rgb):
    return '#{0:02x}{1:02x}{2:02x}'.format(*rgb)

def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))

class Tron(Game):
    def __init__(self, source: pygame.Surface, offset: Tuple[int, int]):
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.source = source
        self.offset = offset
        self.clock = pygame.time.Clock()
        self.running = True
        self.reset()

    def reset(self):
        self.board = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.p1_pos = [2, GRID_HEIGHT // 2]
        self.p2_pos = [GRID_WIDTH - 3, GRID_HEIGHT // 2]
        self.p1_dir = (1, 0)
        self.p2_dir = (-1, 0)
        self.board[self.p1_pos[1]][self.p1_pos[0]] = BLUE
        self.board[self.p2_pos[1]][self.p2_pos[0]] = RED


    def get_board(self) -> List[List[str]]:
        result = [[rgb_to_hex(BLACK) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board[y][x]:
                    result[y][x] = rgb_to_hex(self.board[y][x])
        return result

    def run(self):
        MOVE_INTERVAL = 200  # milliseconds between moves
        last_move_time = pygame.time.get_ticks()

        while self.running:
            now = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    self.running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] and self.p1_dir != (0, 1): self.p1_dir = (0, -1)
            if keys[pygame.K_s] and self.p1_dir != (0, -1): self.p1_dir = (0, 1)
            if keys[pygame.K_a] and self.p1_dir != (1, 0): self.p1_dir = (-1, 0)
            if keys[pygame.K_d] and self.p1_dir != (-1, 0): self.p1_dir = (1, 0)

            if keys[pygame.K_UP] and self.p2_dir != (0, 1): self.p2_dir = (0, -1)
            if keys[pygame.K_DOWN] and self.p2_dir != (0, -1): self.p2_dir = (0, 1)
            if keys[pygame.K_LEFT] and self.p2_dir != (1, 0): self.p2_dir = (-1, 0)
            if keys[pygame.K_RIGHT] and self.p2_dir != (-1, 0): self.p2_dir = (1, 0)

            if now - last_move_time >= MOVE_INTERVAL:
                self.update()
                last_move_time = now

            self.draw()
            self.clock.tick(60)  # high frame rate for smooth input


    def update(self):
        for player, pos, direction, color in [
            ("P1", self.p1_pos, self.p1_dir, BLUE),
            ("P2", self.p2_pos, self.p2_dir, RED),
        ]:
            if direction == (0, 0):
                continue  # Skip if no direction yet

            new_x = pos[0] + direction[0]
            new_y = pos[1] + direction[1]

            if not (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT) or self.board[new_y][new_x]:
                print(f"{player} crashed!")
                self.running = False
                return

            pos[0], pos[1] = new_x, new_y
            self.board[new_y][new_x] = color


    def draw(self):
        self.screen.fill(BLACK)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.board[y][x]
                if color:
                    pygame.draw.rect(
                        self.screen, color,
                        pygame.Rect(x * CELL_WIDTH, y * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)
                    )
        pygame.display.flip()
        self.source.blit(self.screen, self.offset)
