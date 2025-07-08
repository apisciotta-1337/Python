import pygame  # Game library for graphics and input
import random  # For random apple placement

pygame.init()

# Configuration
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
FPS = 10

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 25)

# Draw snake segments
def draw_snake(snake_list):
    for x, y in snake_list:
        pygame.draw.rect(screen, GREEN, [x, y, CELL_SIZE, CELL_SIZE])

# Print message on screen
def message(text, color):
    msg = font.render(text, True, color)
    screen.blit(msg, [WIDTH // 6, HEIGHT // 3])  # FIXED incorrect division

def game_loop():
    game_over = False
    game_close = False

    x, y = WIDTH // 2, HEIGHT // 2
    x_change = 0
    y_change = 0

    snake_list = []
    snake_length = 1

    # Place initial food
    food_x = round(random.randrange(0, WIDTH - CELL_SIZE) / CELL_SIZE) * CELL_SIZE
    food_y = round(random.randrange(0, HEIGHT - CELL_SIZE) / CELL_SIZE) * CELL_SIZE  # FIXED missing closing parenthesis

    while not game_over:
        while game_close:
            screen.fill(WHITE)
            message("Game Over! Press Q to Quit or C to Play Again", RED)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    elif event.key == pygame.K_c:
                        return game_loop()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change, y_change = -CELL_SIZE, 0
                elif event.key == pygame.K_RIGHT:
                    x_change, y_change = CELL_SIZE, 0
                elif event.key == pygame.K_UP:
                    x_change, y_change = 0, -CELL_SIZE
                elif event.key == pygame.K_DOWN:
                    x_change, y_change = 0, CELL_SIZE

        # Update position
        x += x_change
        y += y_change

        # Check wall collision
        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_close = True

        screen.fill(BLACK)

        # Draw food
        pygame.draw.rect(screen, RED, [food_x, food_y, CELL_SIZE, CELL_SIZE])

        # Update snake body
        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        # Check self collision
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True

        draw_snake(snake_list)

        # Display score
        score_text = font.render(f"Score: {snake_length - 1}", True, WHITE)
        screen.blit(score_text, [0, 0])  # FIXED bad list index

        pygame.display.update()

        # Check food collision
        if x == food_x and y == food_y:
            snake_length += 1
            food_x = round(random.randrange(0, WIDTH - CELL_SIZE) / CELL_SIZE) * CELL_SIZE
            food_y = round(random.randrange(0, HEIGHT - CELL_SIZE) / CELL_SIZE) * CELL_SIZE  # FIXED: incorrect use of WIDTH instead of HEIGHT

        clock.tick(FPS)

    pygame.quit()
    quit()

game_loop()
