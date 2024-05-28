from typing import List
import pygame
import random
from games.game import Game

# Initialize Pygame
# pygame.init()

# Constants
CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 11
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
BALL_SIZE = CELL_SIZE
PADDLE_WIDTH = CELL_SIZE * 3
PADDLE_HEIGHT = CELL_SIZE
PADDLE_SPEED = CELL_SIZE / 5
BALL_SPEED_X = CELL_SIZE / 10
BALL_SPEED_Y = CELL_SIZE / 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def rgb_to_hex(rgb):
    """Converts RGB tuple to hexadecimal color code."""
    return '#{0:02x}{1:02x}{2:02x}'.format(rgb[0], rgb[1], rgb[2])

def bind_horizontal(x):
    return min(max(x, 0), GRID_WIDTH-1)

def bind_vertical(y):
    return min(max(y, 0), GRID_HEIGHT-1)

class Pong(Game):
    def __init__(self, source: pygame.Surface, offset: tuple) -> None:
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.source = source
        self.offset = offset
        self.initialize_game()

    def initialize_game(self):
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Vertical Pong')
        # Ball
        self.ball = pygame.Rect((SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2), (BALL_SIZE, BALL_SIZE))
        # Paddles
        self.top_paddle = pygame.Rect((SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, 0), (PADDLE_WIDTH, PADDLE_HEIGHT))
        self.bottom_paddle = pygame.Rect((SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - PADDLE_HEIGHT), (PADDLE_WIDTH, PADDLE_HEIGHT))
        # Ball speed
        self.ball_speed_x = BALL_SPEED_X * random.choice((-1, 1))
        self.ball_speed_y = BALL_SPEED_Y * random.choice((-1, 1))
        # Paddle speed
        self.top_paddle_speed = 0
        self.bottom_paddle_speed = 0
        # Scores
        self.top_score = 0
        self.bottom_score = 0
        # Font for scoring
        self.font = pygame.font.Font(None, 74)
        self.running = True

    def get_board(self) -> List[List[str]]:
        board = [[rgb_to_hex(BLACK) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Mark the ball position
        ball_grid_x = bind_horizontal(self.ball.x // CELL_SIZE)
        ball_grid_y = bind_vertical((self.ball.y+10) // CELL_SIZE) # Add a slight offset to make the ball appear at the bottom more
        board[ball_grid_y][ball_grid_x] = rgb_to_hex(WHITE)
        
        # Mark the top paddle position
        top_paddle_grid_x = bind_horizontal(self.top_paddle.x // CELL_SIZE)
        for i in range(PADDLE_WIDTH // CELL_SIZE):
            board[0][top_paddle_grid_x + i] = rgb_to_hex(WHITE)
        
        # Mark the bottom paddle position
        bottom_paddle_grid_x = bind_horizontal(self.bottom_paddle.x // CELL_SIZE)
        for i in range(PADDLE_WIDTH // CELL_SIZE):
            board[GRID_HEIGHT - 1][bottom_paddle_grid_x + i] = rgb_to_hex(WHITE)
        
        return board
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.running = False

                    # Check the state of the keys
                    keys = pygame.key.get_pressed()
                    
                    # Update the top paddle speed based on key presses
                    if keys[pygame.K_a]:
                        self.top_paddle_speed = -PADDLE_SPEED
                    elif keys[pygame.K_d]:
                        self.top_paddle_speed = PADDLE_SPEED
                    else:
                        self.top_paddle_speed = 0

                    # Update the bottom paddle speed based on key presses
                    if keys[pygame.K_LEFT]:
                        self.bottom_paddle_speed = -PADDLE_SPEED
                    elif keys[pygame.K_RIGHT]:
                        self.bottom_paddle_speed = PADDLE_SPEED
                    else:
                        self.bottom_paddle_speed = 0
            
            # Move paddles
            self.top_paddle.x += self.top_paddle_speed
            self.bottom_paddle.x += self.bottom_paddle_speed
            
            # Ensure paddles stay on screen
            if self.top_paddle.left < 0:
                self.top_paddle.left = 0
            if self.top_paddle.right > SCREEN_WIDTH:
                self.top_paddle.right = SCREEN_WIDTH
            if self.bottom_paddle.left < 0:
                self.bottom_paddle.left = 0
            if self.bottom_paddle.right > SCREEN_WIDTH:
                self.bottom_paddle.right = SCREEN_WIDTH
            
            # Move ball
            self.ball.x += self.ball_speed_x
            self.ball.y += self.ball_speed_y
            
            # Ball collision with left/right walls
            if self.ball.left <= 0 or self.ball.right >= SCREEN_WIDTH:
                self.ball_speed_x *= -1
            
            # Ball collision with paddles
            if self.ball.colliderect(self.top_paddle) or self.ball.colliderect(self.bottom_paddle):
                if self.ball.top < self.top_paddle.bottom:
                    self.ball.y = self.top_paddle.bottom
                if self.ball.bottom > self.bottom_paddle.top:
                    self.ball.y = self.bottom_paddle.top - CELL_SIZE
                self.ball_speed_y *= -1
            
            # Ball out of bounds
            if self.ball.top <= 0:
                self.bottom_score += 1
                self.reset_ball()
            if self.ball.bottom >= SCREEN_HEIGHT:
                self.top_score += 1
                self.reset_ball()
            
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(60)


    def reset_ball(self):
        self.ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.ball_speed_x = BALL_SPEED_X * random.choice((-1, 1))
        self.ball_speed_y = BALL_SPEED_Y * random.choice((-1, 1))

    def draw(self):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, self.top_paddle)
        pygame.draw.rect(self.screen, WHITE, self.bottom_paddle)
        pygame.draw.rect(self.screen, WHITE, self.ball)
        
        top_text = self.font.render(str(self.top_score), True, WHITE)
        self.screen.blit(top_text, (SCREEN_WIDTH // 4 - top_text.get_width() // 2, SCREEN_HEIGHT // 2 - top_text.get_height() // 2))
        
        bottom_text = self.font.render(str(self.bottom_score), True, WHITE)
        self.screen.blit(bottom_text, (3 * SCREEN_WIDTH // 4 - bottom_text.get_width() // 2, SCREEN_HEIGHT // 2 - bottom_text.get_height() // 2))
        
        pygame.display.flip()
        # Write to main display
        self.source.blit(self.screen, self.offset)

