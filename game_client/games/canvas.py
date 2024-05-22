from typing import List
import pygame
import sys
from games.game import Game

def color_to_hex(color: pygame.Color) -> str:
    # Get the RGB components of the color
    r = color.r
    g = color.g
    b = color.b
    # Format as a hex string
    return f'#{r:02x}{g:02x}{b:02x}'

class CanvasGame(Game):
    def __init__(self, screen):
        self.screen = screen
        self.grid_width = 11
        self.grid_height = 10
        self.cell_size = 50
        self.x_offset = 125
        # self.colors = [pygame.Color('red'), pygame.Color('green'), pygame.Color('blue')]
        # self.current_color_index = 0
        self.color_wheel = ColorPicker(100, 550, 600, 100)
        self.grid = [[pygame.Color('white') for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.running = True

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            # elif event.key == pygame.K_c:
            #     self.current_color_index = (self.current_color_index + 1) % len(self.colors)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            mouse_x -= self.x_offset
            grid_x = mouse_x // self.cell_size
            grid_y = mouse_y // self.cell_size
            if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                self.grid[grid_y][grid_x] = self.color_wheel.color

    def draw_grid(self):
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = pygame.Rect(x * self.cell_size + self.x_offset, y * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, self.grid[y][x], rect)
                pygame.draw.rect(self.screen, pygame.Color('black'), rect, 1)

    def get_board(self) -> List[List[str]]:
        return [[color_to_hex(x) for x in y] for y in self.grid]

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)

            self.color_wheel.update()
            self.color_wheel.draw(self.screen)

            # self.screen.fill(pygame.Color('white'))
            self.draw_grid()
            pygame.display.flip()
            clock.tick(60)


class ColorPicker:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.Surface((w, h))
        self.image.fill((255, 255, 255))
        self.rad = h//2
        self.pwidth = w-self.rad*2
        for i in range(self.pwidth):
            color = pygame.Color(0)
            color.hsla = (int(360*i/self.pwidth), 100, 50, 100)
            pygame.draw.rect(self.image, color, (i+self.rad, h//3, 1, h-2*h//3))
        self.p = 0
        self.color = self.get_color()

    def get_color(self):
        color = pygame.Color(0)
        color.hsla = (int(self.p * 360), 100, 50, 100)
        return color

    def update(self):
        moude_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if moude_buttons[0] and self.rect.collidepoint(mouse_pos):
            self.p = (mouse_pos[0] - self.rect.left - self.rad) / self.pwidth
            self.p = (max(0, min(self.p, 1)))
            self.color = self.get_color()
        
    def draw(self, surf):
        surf.blit(self.image, self.rect)
        center = self.rect.left + self.rad + self.p * self.pwidth, self.rect.centery
        pygame.draw.circle(surf, self.get_color(), center, self.rect.height // 2)