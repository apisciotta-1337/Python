import pygame
import random

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 600, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 102, 204)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Paddle properties
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 10
PADDLE_Y = HEIGHT - 30

# Ball properties
BALL_RADIUS = 8

# Brick properties
BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_WIDTH = 65
BRICK_HEIGHT = 20
BRICK_PADDING = 5
BRICK_OFFSET_TOP = 40
BRICK_OFFSET_LEFT = 20

# Set up font
font = pygame.font.SysFont("comicsansms", 24)

# Draw the bricks and return a list of their rectangles
def create_bricks():
    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
            y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
            bricks.append(pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT))
    return bricks

def main():
    run = True
    clock = pygame.time.Clock()

    # Paddle setup
    paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle_speed = 7

    # Ball setup
    ball_x = WIDTH // 2
    ball_y = PADDLE_Y - BALL_RADIUS
    ball_dx = random.choice([-4, 4])
    ball_dy = -4

    # Bricks setup
    bricks = create_bricks()

    score = 0
    lives = 3

    while run:
        clock.tick(60)  # 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Key presses for paddle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.x -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.x += paddle_speed

        # Move the ball
        ball_x += ball_dx
        ball_y += ball_dy

        # Ball collision with walls
        if ball_x <= BALL_RADIUS or ball_x >= WIDTH - BALL_RADIUS:
            ball_dx *= -1
        if ball_y <= BALL_RADIUS:
            ball_dy *= -1

        # Ball collision with paddle
        if paddle.collidepoint(ball_x, ball_y + BALL_RADIUS):
            ball_dy *= -1
            # Add a little randomness to angle
            ball_dx += random.choice([-1, 0, 1])
            ball_dx = max(-6, min(6, ball_dx))  # Clamp speed

        # Ball collision with bricks
        hit_index = -1
        for i, brick in enumerate(bricks):
            if brick.collidepoint(ball_x, ball_y - BALL_RADIUS):
                hit_index = i
                break
        if hit_index >= 0:
            del bricks[hit_index]
            ball_dy *= -1
            score += 10

        # Ball falls below paddle
        if ball_y > HEIGHT:
            lives -= 1
            if lives == 0:
                run = False
            else:
                # Reset ball and paddle
                ball_x = WIDTH // 2
                ball_y = PADDLE_Y - BALL_RADIUS
                ball_dx = random.choice([-4, 4])
                ball_dy = -4
                paddle.x = WIDTH // 2 - PADDLE_WIDTH // 2
                pygame.time.delay(1000)

        # Draw everything
        win.fill(BLACK)
        pygame.draw.rect(win, BLUE, paddle)
        pygame.draw.circle(win, RED, (int(ball_x), int(ball_y)), BALL_RADIUS)
        for brick in bricks:
            pygame.draw.rect(win, GREEN, brick)
        # Draw score and lives
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        win.blit(score_text, (20, 10))
        win.blit(lives_text, (WIDTH - 120, 10))

        # Win condition
        if not bricks:
            win_text = font.render("You Win!", True, WHITE)
            win.blit(win_text, (WIDTH // 2 - 60, HEIGHT // 2 - 20))
            pygame.display.update()
            pygame.time.delay(2000)
            run = False

        pygame.display.update()

    # Game over
    win.fill(BLACK)
    over_text = font.render("Game Over", True, WHITE)
    win.blit(over_text, (WIDTH // 2 - 70, HEIGHT // 2 - 20))
    pygame.display.update()
    pygame.time.delay(2000)
    pygame.quit()

if __name__ == "__main__":
    main()