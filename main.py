import pygame as pg
import math
import time
import sys
from random import randint

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
GROUND_LEVEL = WINDOW_HEIGHT / 2
FPS = 60

class Game:
    def __init__(self):
        self.score = 0
        self.lower_obstruction_spawn_time = 1000
        self.acceleration = -10
        self.upper_obstruction_spawn_time = None
        self.velocity = None

    def choose_difficulty(self):
        difficulty = input("choose difficulty (easy/medium/hard): ").strip().lower()
        match difficulty:
            case "easy":
                self.velocity = -250
                self.upper_obstruction_spawn_time = 5000
            case "medium":
                self.velocity = -300
                self.upper_obstruction_spawn_time = 4500
            case "hard":
                self.velocity = -350
                self.upper_obstruction_spawn_time = 4000
            case _:
                sys.exit(f"ERROR: `{difficulty}` is not an option")

class Dino:
    def __init__(self):
        self.color = "black"
        self.radius = 50
        self.pos = pg.Vector2(WINDOW_WIDTH / 4, GROUND_LEVEL - self.radius)
        self.jumping = False
        self.peak_jump_time = 0.5
        self.jump_height = 300

    def jump(self, time):
        a = self.jump_height / (self.peak_jump_time ** 2)
        y = (GROUND_LEVEL - self.radius) - (-a * (time - self.peak_jump_time) ** 2 + self.jump_height)
        self.pos.y = min(y, GROUND_LEVEL - self.radius)

    def collision(self, obstruction):
        x = math.floor(self.pos.x)
        y = math.floor(self.pos.y)
        closest_x = max(obstruction.pos.x, min(x, obstruction.pos.x + obstruction.width))
        closest_y = max(obstruction.pos.y, min(y, obstruction.pos.y + obstruction.height))
        distance = math.sqrt((closest_x - x) ** 2 + (closest_y - y) ** 2)
        
        return distance <= self.radius

class Obstruction:
    def __init__(self):
        self.passed_dino = False
        self.color = "green"
        self.height = 120
        self.width = 60
        self.pos = pg.Vector2(WINDOW_WIDTH, GROUND_LEVEL - self.height)

    def move(self, vel, dt):
        self.pos.x += vel * dt

    def oob(self):
        return self.pos.x < -self.width 

def remove_oob(obstructions):
    for i in range(len(obstructions) - 1):
        if obstructions[i].oob():
            obstructions.pop(i)
            i -= 1
    return obstructions

def main():
    print("------- DINO GAME -------")
    game = Game()
    game.choose_difficulty()
    dino = Dino()
    obstructions = []

    pg.init()
    pg.display.set_caption("dino game")
    window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    font = pg.font.Font("/home/perfimreite/.local/share/fonts/Iosevka/IosevkaNerdFontPropo-Regular.ttf", 64)

    CREATE_OBSTRUCTION = pg.USEREVENT + 1
    pg.time.set_timer(CREATE_OBSTRUCTION, 1000)
    
    DELAY_UPPER_OBSTRUCTION_SPAWN_TIME = pg.USEREVENT + 2
    pg.time.set_timer(DELAY_UPPER_OBSTRUCTION_SPAWN_TIME, 1000)

    clock = pg.time.Clock()
    dt = 0
    start_time = time.time()
     
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == CREATE_OBSTRUCTION:
                pg.time.set_timer(CREATE_OBSTRUCTION, randint(game.lower_obstruction_spawn_time, game.upper_obstruction_spawn_time))
                obstructions.append(Obstruction())
            elif event.type == DELAY_UPPER_OBSTRUCTION_SPAWN_TIME:
                pg.time.set_timer(DELAY_UPPER_OBSTRUCTION_SPAWN_TIME, 1000)
                if game.upper_obstruction_spawn_time > game.lower_obstruction_spawn_time + 200:
                    game.upper_obstruction_spawn_time -= 25
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE and not dino.jumping:
                    dino.jumping = True
                    jump_start_time = time.time()
        
        window.fill("aqua")
        pg.draw.rect(window, "bisque", (0, WINDOW_HEIGHT / 2, WINDOW_WIDTH, WINDOW_HEIGHT / 2))

        if dino.jumping:
            elapsed_time = time.time() - jump_start_time
            dino.jump(elapsed_time)
            if dino.pos.y >= GROUND_LEVEL - dino.radius and elapsed_time > dino.peak_jump_time * 2:
                dino.jumping = False
                dino.pos.y = GROUND_LEVEL - dino.radius
       
        obstructions = remove_oob(obstructions)

        for o in obstructions:
            if o.pos.x < dino.pos.x - dino.radius and not o.passed_dino:
                game.score += 1
                o.passed_dino = True

        for o in obstructions:
            if dino.collision(o):
                sys.exit(f"loser, you only got {game.score} points...")
                # TODO: fix how the game ends

            pg.draw.rect(window, o.color, (o.pos.x, o.pos.y, o.width, o.height))
            o.move(game.velocity, dt)
       
        game.velocity += game.acceleration * dt

        pg.draw.circle(window, dino.color, (dino.pos.x, dino.pos.y), dino.radius)
       
        score = font.render(f"{game.score}", True, "white", "aqua")
        score_rect = score.get_rect()
        score_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 5)
        window.blit(score, score_rect)
        
        elapsed_time = time.time() - start_time
        time_since_start = font.render(f"{round(elapsed_time, 2)}", True, "white", "aqua")
        time_rect = time_since_start.get_rect()
        time_rect.center = (WINDOW_WIDTH - 100, 100)
        window.blit(time_since_start, time_rect)
        
        pg.display.flip()
        dt = clock.tick(FPS) / 1000

if __name__ == "__main__":
    main()
    pg.quit()
