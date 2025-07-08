import pygame
import random
import os

# Setup
WIDTH, HEIGHT, CELL_SIZE, FPS = 600, 400, 20, 10
WHITE, GREEN, RED, BLACK = (255,255,255), (0,255,0), (255,0,0), (0,0,0)

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 25)

class Snake:
    def __init__(self):
        self.body = [(WIDTH // 2, HEIGHT // 2)]
        self.dx = CELL_SIZE
        self.dy = 0

    def move(self):
        head = (self.body[-1][0] + self.dx, self.body[-1][1] + self.dy)
        self.body.append(head)
        self.body.pop(0)

    def grow(self):
        self.body.insert(0, self.body[0])

    def head(self):
        return self.body[-1]

    def hits_self(self):
        return self.head() in self.body[:-1]

    def draw(self):
        for x, y in self.body:
            pygame.draw.rect(screen, GREEN, [x, y, CELL_SIZE, CELL_SIZE])

class Game:
    def __init__(self):
        self.snake = Snake()
        self.score = 0
        self.highscore = self.load_highscore()
        self.paused = False
        self.place_food()

    def place_food(self):
        self.food = (
            random.randrange(0, WIDTH, CELL_SIZE),
            random.randrange(0, HEIGHT, CELL_SIZE)
        )

    def load_highscore(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt") as f:
                return int(f.read().strip())
        return 0

    def save_highscore(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.highscore))

    def toggle_pause(self):
        self.paused = not self.paused

    def msg(self, text, color, pos=(WIDTH//6, HEIGHT//3)):
        screen.blit(font.render(text, True, color), pos)

    def run(self):
        game_over = False
        game_close = False

        while not game_over:
            while game_close:
                if self.score > self.highscore:
                    self.highscore = self.score
                    self.save_highscore()

                screen.fill(WHITE)
                self.msg(f"Game Over! Score: {self.score}  High: {self.highscore}", RED)
                self.msg("Press Q to Quit or C to Play Again", RED, (WIDTH // 6, HEIGHT // 2))
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            return
                        elif event.key == pygame.K_c:
                            self.__init__()
                            return self.run()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.toggle_pause()
                    elif not self.paused:
                        if event.key == pygame.K_LEFT and self.snake.dx == 0:
                            self.snake.dx, self.snake.dy = -CELL_SIZE, 0
                        elif event.key == pygame.K_RIGHT and self.snake.dx == 0:
                            self.snake.dx, self.snake.dy = CELL_SIZE, 0
                        elif event.key == pygame.K_UP and self.snake.dy == 0:
                            self.snake.dx, self.snake.dy = 0, -CELL_SIZE
                        elif event.key == pygame.K_DOWN and self.snake.dy == 0:
                            self.snake.dx, self.snake.dy = 0, CELL_SIZE

            if self.paused:
                self.msg("Paused. Press P to resume.", WHITE)
                pygame.display.update()
                clock.tick(2)
                continue

            self.snake.move()
            hx, hy = self.snake.head()

            if hx < 0 or hx >= WIDTH or hy < 0 or hy >= HEIGHT or self.snake.hits_self():
                game_close = True

            if self.snake.head() == self.food:
                self.snake.grow()
                self.score += 1
                self.place_food()

            screen.fill(BLACK)
            pygame.draw.rect(screen, RED, [*self.food, CELL_SIZE, CELL_SIZE])
            self.snake.draw()
            self.msg(f"Score: {self.score}  High: {self.highscore}", WHITE, (0, 0))
            pygame.display.update()
            clock.tick(FPS)

        pygame.quit()
        quit()

if __name__ == "__main__":
    Game().run()
