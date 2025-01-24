import pygame as pg
import math
import time
import sys
import json
from random import randint


WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1080
GROUND_LEVEL = WINDOW_HEIGHT / 2
FPS = 60


class Game:
    def __init__(self):
        self.score = 0
        self.highscore = 0
        self.velocity = 0
        self.acceleration = -10
        self.lower_obstruction_spawn_time = 1000
        self.upper_obstruction_spawn_time = 0

    def choose_difficulty(self):
        difficulty = input("Choose difficulty (easy/medium/hard): ").strip().lower()
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

    def get_highscore(self):
        with open("highscore.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.highscore = data["highscore"]

    def update_highscore(self, score):
        new_highscore = { "highscore": score }
        with open("highscore.json", "w", encoding="utf-8") as f:
            json.dump(new_highscore, f, indent=4)

    def update_score(self, dino, obstructions):
        for o in obstructions:
            if o.pos.x + o.width < dino.pos.x - dino.radius and not o.passed_dino:
                self.score += 1
                o.passed_dino = True


class Dino:
    def __init__(self):
        self.radius = 50
        self.pos = pg.Vector2(WINDOW_WIDTH / 4, GROUND_LEVEL - self.radius)
        self.jumping = False
        self.peak_jump_time = 0.5
        self.jump_height = 300

    def jump(self, elapsed_time):
        a = self.jump_height / (self.peak_jump_time ** 2)
        y = (GROUND_LEVEL - self.radius) - (-a * (elapsed_time - self.peak_jump_time) ** 2 + self.jump_height)
        self.pos.y = min(y, GROUND_LEVEL - self.radius)

        if self.pos.y >= GROUND_LEVEL - self.radius and elapsed_time > self.peak_jump_time * 2:
            self.pos.y = GROUND_LEVEL - self.radius
            self.jumping = False

    def collision(self, obstruction):
        x = math.floor(self.pos.x)
        y = math.floor(self.pos.y)
        closest_x = max(obstruction.pos.x, min(x, obstruction.pos.x + obstruction.width))
        closest_y = max(obstruction.pos.y, min(y, obstruction.pos.y + obstruction.height))
        distance = math.sqrt((closest_x - x) ** 2 + (closest_y - y) ** 2)
        
        return distance <= self.radius


class Obstruction:
    def __init__(self):
        self.height = 120
        self.width = 60
        self.pos = pg.Vector2(WINDOW_WIDTH, GROUND_LEVEL - self.height)
        self.passed_dino = False

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


if __name__ == "__main__":
    print("------- DINO GAME -------")
    game = Game()
    game.choose_difficulty()
    game.get_highscore()
    dino = Dino()
    obstructions = []

    pg.init()
    pg.display.set_caption("Dino-game")
    window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    font = pg.font.Font('freesansbold.ttf', 64)

    CREATE_OBSTRUCTION = pg.USEREVENT + 1
    pg.time.set_timer(CREATE_OBSTRUCTION, 1000)
    
    DELAY_UPPER_OBSTRUCTION_SPAWN_TIME = pg.USEREVENT + 2
    pg.time.set_timer(DELAY_UPPER_OBSTRUCTION_SPAWN_TIME, 1000)

    dt = 0
    start_time = time.time()
     
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit("You exited the window")
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
        pg.draw.circle(window, "black", (dino.pos.x, dino.pos.y), dino.radius)

        if dino.jumping:
            jump_elapsed_time = time.time() - jump_start_time
            dino.jump(jump_elapsed_time)
       
        obstructions = remove_oob(obstructions)
        game.update_score(dino, obstructions)

        for o in obstructions:
            if dino.collision(o):
                if game.score > game.highscore:
                    game.update_highscore(game.score)
                    sys.exit(f"New highscore! Congratulation, you got {game.score} points")
                sys.exit(f"You got {game.score} points.")

            pg.draw.rect(window, "green", (o.pos.x, o.pos.y, o.width, o.height))
            o.move(game.velocity, dt)
       
        game.velocity += game.acceleration * dt
       
        score_widget = font.render(f"{game.score} | {game.highscore}", True, "white", "aqua")
        score_rect = score_widget.get_rect()
        score_rect.center = (WINDOW_WIDTH / 2, 100)
        window.blit(score_widget, score_rect)
        
        elapsed_time = time.time() - start_time
        elapsed_time_widget = font.render(f"{round(elapsed_time, 1)}", True, "white", "aqua")
        elapsed_time_rect = elapsed_time_widget.get_rect()
        elapsed_time_rect.center = (WINDOW_WIDTH - 100, 100)
        window.blit(elapsed_time_widget, elapsed_time_rect)
        
        dt = pg.time.Clock().tick(FPS) / 1000
        pg.display.flip()

    pg.quit()
