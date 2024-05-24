from typing import List
import pygame
import sys
import random
import time
from games.game import Game

def color_to_hex(color: pygame.Color) -> str:
    # Get the RGB components of the color
    r = color.r
    g = color.g
    b = color.b
    # Format as a hex string
    return f'#{r:02x}{g:02x}{b:02x}'

def get_random_color():
    """Returns a random color using pygame.Color."""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return pygame.Color(r, g, b)

class CanvasGame(Game):
    def __init__(self, source, offset):
        self.screen_offset = offset
        self.source = source
        self.screen = pygame.Surface((800,700))
        self.screen.fill((255,255,255))
        self.grid_width = 10
        self.grid_height = 11
        self.cell_height = 50
        self.cell_width = 25
        self.x_offset = 275
        self.color_wheel = ColorPicker(100, 550, 600, 100)
        self.grid = [[pygame.Color('black') for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.light_show_button = Button("Light Show", (550, 300), (200, 100), (200, 200, 200), (100, 100, 100), pygame.font.Font(None, 30), self.light_show_toggle)
        self.preset_display = False
        self.prev_time = None
        self.running = True

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not self.preset_display:
            mouse_x, mouse_y = event.pos
            mouse_x -= self.x_offset
            grid_x = mouse_x // self.cell_width
            grid_y = mouse_y // self.cell_height
            if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                self.grid[grid_y][grid_x] = self.color_wheel.color

    def draw_grid(self):
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = pygame.Rect(x * self.cell_width + self.x_offset, y * self.cell_height, self.cell_width, self.cell_height)
                pygame.draw.rect(self.screen, self.grid[y][x], rect)
                pygame.draw.rect(self.screen, pygame.Color('white'), rect, 1)

    def get_board(self) -> List[List[str]]:
        return [[color_to_hex(x) for x in y] for y in self.grid]
    
    def light_show_toggle(self):
        if self.preset_display:
            self.grid = [[pygame.Color('black') for _ in range(self.grid_width)] for _ in range(self.grid_height)]
            self.preset_display = False
        else:
            self.prev_time = int(time.time() * 1000)
            self.light_show()
            self.preset_display = True
        # self.preset_display = not self.preset_display
    
    def light_show(self):
        ignore_2 = [(0,1), (1,0), (2,0), (3,1), (2,2), (1,3), (0,4), (1,4), (2,4), (3,4)] 
        ignore_2_again = [(x[0]*2+1, x[1]) for x in ignore_2]
        ignore_4 = [(1,6), (1,7), (1,8), (3,6), (3,7), (3,8), (2,8), (4,8), (3,9), (3,10)]
        ignore_4_again = [(x[0]*2+1, x[1]) for x in ignore_4]
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                # if (x, y) in ignore_2+ignore_2_again:
                #     color = pygame.Color(0,255,255)
                # elif (x, y) in ignore_4+ignore_4_again:
                #     color = pygame.Color(255,0,0)
                # else:
                color = get_random_color()
                self.grid[y][x] = color

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
                if self.light_show_button.is_clicked(event):
                    self.light_show_button.callback()

            self.color_wheel.update()
            self.color_wheel.draw(self.screen)
            self.light_show_button.draw(self.screen)

            # Timer system for light show
            curr_time = int(time.time() * 1000)
            if self.preset_display and curr_time - self.prev_time >= 1000:
                self.prev_time = curr_time
                self.light_show()

            self.draw_grid()
            self.source.blit(self.screen, self.screen_offset)
            pygame.display.flip()
            pygame.display.update()
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