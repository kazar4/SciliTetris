"""
Snake Eater
Made with PyGame
"""

from typing import List
import pygame, sys, time, random
from games.game import Game


# Difficulty settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
difficulty = 3

pixel_size = 10

# Window size
frame_size_x = 50
frame_size_y = 140


# Colors (R, G, B)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)


# Game variables
snake_pos = [20, 50]
snake_body = [[20, 50], [20-10, 50], [20-(2*10), 50]]

food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
food_spawn = True

direction = 'RIGHT'
change_to = direction

score = 0

def rgb_to_hex(rgb):
    """Converts RGB tuple to hexadecimal color code."""
    return '#{0:02x}{1:02x}{2:02x}'.format(rgb[0], rgb[1], rgb[2])

def get_color(color):
    if color == black:
        return (0,0,0)
    elif color == white:
        return (255,255,255)
    elif color == red:
        return (255,0,0)
    elif color == green:
        return (0,255,0)
    elif color == blue:
        return (0,0,255)

class Snake(Game):
    def __init__(self):
        self.init_pygame()

    def init_pygame(self):
        # Checks for errors encountered
        check_errors = pygame.init()
        # pygame.init() example output -> (6, 0)
        # second number in tuple gives number of errors
        if check_errors[1] > 0:
            print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
            sys.exit(-1)
        else:
            print('[+] Game successfully initialised')
        # Initialise game window
        pygame.display.set_caption('Snake Eater')
        self.game_window = pygame.display.set_mode((frame_size_x, frame_size_y))
        # FPS (frames per second) controller
        self.fps_controller = pygame.time.Clock()

    def get_board(self) -> List[List[str]]:
        rows = frame_size_y//pixel_size
        cols = frame_size_x//pixel_size
        board = [[rgb_to_hex(get_color(black)) for _ in range(cols)] for _ in range(rows)]
        for segment in snake_body:
            board[segment[1]//pixel_size][segment[0]//pixel_size] = rgb_to_hex(get_color(green))
        board[food_pos[1]//pixel_size][food_pos[0]//pixel_size] = rgb_to_hex(get_color(white))
        return board

    # Score
    def show_score(self, choice, color, font, size):
        score_font = pygame.font.SysFont(font, size)
        score_surface = score_font.render('Score : ' + str(score), True, color)
        score_rect = score_surface.get_rect()
        if choice == 1:
            score_rect.midtop = (frame_size_x/10, 15)
        else:
            score_rect.midtop = (frame_size_x/2, frame_size_y/1.25)
        self.game_window.blit(score_surface, score_rect)
        # pygame.display.flip()
    
    # Game Over
    def game_over(self):
        my_font = pygame.font.SysFont('times new roman', 90)
        game_over_surface = my_font.render('YOU DIED', True, red)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (frame_size_x/2, frame_size_y/4)
        self.game_window.fill(black)
        self.game_window.blit(game_over_surface, game_over_rect)
        self.show_score(0, red, 'times', 20)
        pygame.display.flip()
        time.sleep(3)
        pygame.quit()
        sys.exit()

    def run(self):
        global change_to, direction, snake_pos, food_pos, snake_body, food_spawn, score
        # Main logic
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Whenever a key is pressed down
                elif event.type == pygame.KEYDOWN:
                    # W -> Up; S -> Down; A -> Left; D -> Right
                    if event.key == pygame.K_UP or event.key == ord('w'):
                        change_to = 'UP'
                    if event.key == pygame.K_DOWN or event.key == ord('s'):
                        change_to = 'DOWN'
                    if event.key == pygame.K_LEFT or event.key == ord('a'):
                        change_to = 'LEFT'
                    if event.key == pygame.K_RIGHT or event.key == ord('d'):
                        change_to = 'RIGHT'
                    # Esc -> Create event to quit the game
                    if event.key == pygame.K_ESCAPE:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

            # Making sure the snake cannot move in the opposite direction instantaneously
            if change_to == 'UP' and direction != 'DOWN':
                direction = 'UP'
            if change_to == 'DOWN' and direction != 'UP':
                direction = 'DOWN'
            if change_to == 'LEFT' and direction != 'RIGHT':
                direction = 'LEFT'
            if change_to == 'RIGHT' and direction != 'LEFT':
                direction = 'RIGHT'

            # Moving the snake
            if direction == 'UP':
                snake_pos[1] -= 10
            if direction == 'DOWN':
                snake_pos[1] += 10
            if direction == 'LEFT':
                snake_pos[0] -= 10
            if direction == 'RIGHT':
                snake_pos[0] += 10

            # Snake body growing mechanism
            snake_body.insert(0, list(snake_pos))
            if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
                score += 1
                food_spawn = False
            else:
                snake_body.pop()

            # Spawning food on the screen
            if not food_spawn:
                food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
            food_spawn = True

            # GFX
            self.game_window.fill(black)
            for pos in snake_body:
                # Snake body
                # .draw.rect(play_surface, color, xy-coordinate)
                # xy-coordinate -> .Rect(x, y, size_x, size_y)
                pygame.draw.rect(self.game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))

            # Snake food
            pygame.draw.rect(self.game_window, white, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

            # Game Over conditions
            # Getting out of bounds
            if snake_pos[0] < 0 or snake_pos[0] > frame_size_x-10:
                self.game_over()
            if snake_pos[1] < 0 or snake_pos[1] > frame_size_y-10:
                self.game_over()
            # Touching the snake body
            for block in snake_body[1:]:
                if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                    self.game_over()

            self.show_score(1, white, 'consolas', 20)
            # Refresh game screen
            pygame.display.update()
            # Refresh rate
            self.fps_controller.tick(difficulty)

if __name__ == '__main__':
    snake = Snake()
    snake.run()