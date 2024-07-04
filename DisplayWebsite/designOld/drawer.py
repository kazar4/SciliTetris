import pygame
import numpy as np
import json

# Initialize Pygame
pygame.init()

# Constants
ROWS, COLS = 15, 10
CELL_SIZE = 40
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 100
WINDOW_WIDTH = COLS * CELL_SIZE
WINDOW_HEIGHT = ROWS * CELL_SIZE + 4 * BUTTON_HEIGHT
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
COLORS = {
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'black': (0, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'purple': (128, 0, 128),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255),
    'orange': (255, 165, 0)
}
color_keys = list(COLORS.keys())
current_color_index = 0
ALPHA = 0.5  # Transparency factor
frames = []  # List to store frames

# Create the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('10x15 Grid Drawer')

# Initialize the grid
grid = np.zeros((ROWS, COLS), dtype=int)
previous_grid = np.zeros((ROWS, COLS), dtype=int)

def draw_grid():
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if grid[y][x] == 0 and previous_grid[y][x] != 0:
                base_color = COLORS[color_keys[previous_grid[y][x] - 1]]
                color = tuple(int(ALPHA * c + (1 - ALPHA) * 255) for c in base_color)
            else:
                color = WHITE if grid[y][x] == 0 else COLORS[color_keys[grid[y][x] - 1]]
            pygame.draw.rect(window, color, rect)
            pygame.draw.rect(window, GRAY, rect, 1)

def toggle_cell(x, y):
    if color_keys[current_color_index] == 'white':
        grid[y][x] = 0
        previous_grid[y][x] = 0
    else:
        if grid[y][x] != 0:
            previous_grid[y][x] = grid[y][x]
        grid[y][x] = (current_color_index + 1)

def export_js_array():
    js_array = "[\n"
    for row in grid:
        js_array += "  [" + ", ".join(map(str, row)) + "],\n"
    js_array = js_array.strip(",\n") + "\n]"
    return js_array

def draw_buttons():
    color_button_width = WINDOW_WIDTH // len(COLORS)
    for i, color in enumerate(color_keys):
        color_button_rect = pygame.Rect(i * color_button_width, ROWS * CELL_SIZE, color_button_width, BUTTON_HEIGHT)
        pygame.draw.rect(window, COLORS[color], color_button_rect)
        pygame.draw.rect(window, BLACK, color_button_rect, 2)

        font = pygame.font.Font(None, 24)
        color_button_text = font.render(color.capitalize(), True, BLACK if color != 'black' else WHITE)
        text_rect = color_button_text.get_rect(center=color_button_rect.center)
        window.blit(color_button_text, text_rect)

    button_width = WINDOW_WIDTH // 2
    export_button_rect = pygame.Rect(0, ROWS * CELL_SIZE + BUTTON_HEIGHT, button_width, BUTTON_HEIGHT)
    clear_button_rect = pygame.Rect(button_width, ROWS * CELL_SIZE + BUTTON_HEIGHT, button_width, BUTTON_HEIGHT)
    
    pygame.draw.rect(window, WHITE, export_button_rect)
    pygame.draw.rect(window, WHITE, clear_button_rect)
    pygame.draw.rect(window, BLACK, export_button_rect, 2)
    pygame.draw.rect(window, BLACK, clear_button_rect, 2)

    font = pygame.font.Font(None, 36)
    export_button_text = font.render('Export JS Array', True, BLACK)
    clear_button_text = font.render('Clear', True, BLACK)

    window.blit(export_button_text, (export_button_rect.x + 10, export_button_rect.y + 10))
    window.blit(clear_button_text, (clear_button_rect.x + 10, clear_button_rect.y + 10))

    next_frame_rect = pygame.Rect(0, ROWS * CELL_SIZE + 2 * BUTTON_HEIGHT, button_width, BUTTON_HEIGHT)
    save_animation_rect = pygame.Rect(button_width, ROWS * CELL_SIZE + 2 * BUTTON_HEIGHT, button_width, BUTTON_HEIGHT)

    pygame.draw.rect(window, WHITE, next_frame_rect)
    pygame.draw.rect(window, WHITE, save_animation_rect)
    pygame.draw.rect(window, BLACK, next_frame_rect, 2)
    pygame.draw.rect(window, BLACK, save_animation_rect, 2)

    next_frame_text = font.render('Next Frame', True, BLACK)
    save_animation_text = font.render('Save Animation', True, BLACK)

    window.blit(next_frame_text, (next_frame_rect.x + 10, next_frame_rect.y + 10))
    window.blit(save_animation_text, (save_animation_rect.x + 10, save_animation_rect.y + 10))

    reset_animation_rect = pygame.Rect(0, ROWS * CELL_SIZE + 3 * BUTTON_HEIGHT, WINDOW_WIDTH, BUTTON_HEIGHT)

    pygame.draw.rect(window, WHITE, reset_animation_rect)
    pygame.draw.rect(window, BLACK, reset_animation_rect, 2)

    reset_animation_text = font.render('Reset Animation', True, BLACK)

    window.blit(reset_animation_text, (reset_animation_rect.x + 10, reset_animation_rect.y + 10))

def save_frame():
    frames.append(grid.copy())

def save_animation():
    frame_data = {'frames': [frame.tolist() for frame in frames]}
    with open('frameData.js', 'w') as f:
        f.write('const frameData = ' + json.dumps(frame_data, indent=2) + ';')

def reset_animation():
    global frames, grid, previous_grid
    frames = []
    grid.fill(0)
    previous_grid.fill(0)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if ROWS * CELL_SIZE <= mouse_y < ROWS * CELL_SIZE + BUTTON_HEIGHT:
                color_button_width = WINDOW_WIDTH // len(COLORS)
                for i in range(len(COLORS)):
                    if i * color_button_width <= mouse_x < (i + 1) * color_button_width:
                        current_color_index = i
                        break
            elif ROWS * CELL_SIZE + BUTTON_HEIGHT <= mouse_y < ROWS * CELL_SIZE + 2 * BUTTON_HEIGHT:
                button_width = WINDOW_WIDTH // 2
                if mouse_x < button_width:
                    print(export_js_array())
                elif mouse_x < 2 * button_width:
                    np.copyto(previous_grid, grid)
                    grid.fill(0)
            elif ROWS * CELL_SIZE + 2 * BUTTON_HEIGHT <= mouse_y < ROWS * CELL_SIZE + 3 * BUTTON_HEIGHT:
                button_width = WINDOW_WIDTH // 2
                if mouse_x < button_width:
                    save_frame()
                elif mouse_x < 2 * button_width:
                    save_animation()
            elif ROWS * CELL_SIZE + 3 * BUTTON_HEIGHT <= mouse_y < ROWS * CELL_SIZE + 4 * BUTTON_HEIGHT:
                reset_animation()
            else:
                grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
                if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                    toggle_cell(grid_x, grid_y)
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_y < ROWS * CELL_SIZE:
                grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
                if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                    toggle_cell(grid_x, grid_y)
    
    window.fill(WHITE)
    draw_grid()
    draw_buttons()
    pygame.display.flip()

pygame.quit()
