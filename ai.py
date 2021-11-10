import pygame
import neat
import random
import math
import os

pygame.init()
HEIGHT = 600
WIDTH = 1500
win = pygame.display.set_mode((WIDTH, HEIGHT))

RUNNING = [pygame.image.load(os.path.join("img/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("img/Dino", "DinoRun2.png"))]

JUMPING = pygame.image.load(os.path.join("img/Dino", "DinoJump.png"))

CACTUS = [pygame.image.load(os.path.join("img/Cactus", "SmallCactus1.png")),
          pygame.image.load(os.path.join("img/Cactus", "SmallCactus2.png")),
          pygame.image.load(os.path.join("img/Cactus", "SmallCactus3.png")),
          pygame.image.load(os.path.join("img/Cactus", "LargeCactus1.png")),
          pygame.image.load(os.path.join("img/Cactus", "LargeCactus2.png")),
          pygame.image.load(os.path.join("img/Cactus", "LargeCactus3.png"))]

ground = pygame.image.load(os.path.join("img/Other", "Track.png"))
ground = pygame.transform.scale(ground, (WIDTH, 28))

FONT = pygame.font.Font('freesansbold.ttf', 20)


class Dino:
    x = 80
    y = 430
    vel_jump = 6

    def __init__(self, img=RUNNING[0]) -> None:
        self.image = img
        self.dino_run = True
        self.dino_jump = False
        self.jump_vel = self.vel_jump
        self.rect = pygame.Rect(self.x, self.y,
                                img.get_width(), img.get_height())
        self.color = (random.randint(0, 255), random.randint(
            0, 255), random.randint(0, 255))
        self.step_index = 0

    def update(self):
        if self.dino_jump:
            self.jump()
        elif self.dino_run:
            self.run()
        if self.step_index >= 10:
            self.step_index = 0

    def jump(self):
        self.img = JUMPING
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 5
            self.jump_vel -= 0.4
        if self.jump_vel <= -self.vel_jump:
            self.dino_jump = False
            self.jump_vel = self.vel_jump

    def run(self):
        self.image = RUNNING[self.step_index // 5]
        self.rect.x = self.x
        self.rect.y = self.y
        self.step_index += 1

    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))


class Obsticle:
    y = 520

    def __init__(self) -> None:
        self.image = random.choice(CACTUS)
        self.size = self.image.get_size()
        self.x = WIDTH
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.rect = pygame.Rect(self.x, self.y, self.x, self.y-self.size[1])

    def update(self):
        self.x -= 15
        self.rect = pygame.Rect(self.x, self.y, self.x, self.y-self.size[1])

    def draw(self, win):
        win.blit(self.image, (self.x, self.y-self.size[1]))


class BG:
    def __init__(self) -> None:
        self.ground_x = 0
        self.ground_y = 500

    def update(self):
        if self.ground_x <= -WIDTH:
            self.ground_x = 0
        self.ground_x -= 15

    def draw(self, win):
        win.blit(ground, (self.ground_x, self.ground_y))
        win.blit(ground, (WIDTH + self.ground_x, self.ground_y))


def draw(win, dinos, obs, background, score, gen):
    win.fill((255, 255, 255))
    background.draw(win)
    text = FONT.render(f'score:  {str(int(score))}', True, (0, 0, 0))
    win.blit(text, (1300, 50))
    text = FONT.render(f'gen:  {str(int(gen))}', True, (0, 0, 0))
    win.blit(text, (1300, 70))
    for o in obs:
        o.draw(win)
    for dino in dinos:
        dino.draw(win)
    pygame.display.update()


def distance(pos_a, pos_b):
    dx = pos_a[0]-pos_b[0]
    dy = pos_a[1]-pos_b[1]
    return math.sqrt(dx**2+dy**2)


def main(genomes, config):
    clock = pygame.time.Clock()

    FPS = 60
    running = True

    score = 0
    background = BG()
    obs = [Obsticle(), Obsticle()]
    obs[1].x += WIDTH//2

    ge = []
    nets = []
    dinos = []
    for genome_id, genome in genomes:
        dinos.append(Dino())
        ge.append(genome)
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
        for x in range(len(obs)):
            if obs[x].x < 0:
                obs.pop(x)
                obs.append(Obsticle())
            obs[x].update()
        score += 0.05
        if len(dinos) == 0:
            break
        for i, dino in enumerate(dinos):
            output = nets[i].activate((dino.rect.y, distance(
                (dino.rect.x, dino.rect.y), obs[0].rect.midtop)))
            dino.update()
            ge[i].fitness += 0.05
            if output[0] > 0.5 and dino.rect.y == dino.y:
                dino.dino_jump = True
            if dino.rect.colliderect(obs[0].rect):
                ge[i].fitness -= 1
                dinos.pop(i)
                ge.pop(i)
                nets.pop(i)
        if score % 100 == 0:
            FPS += 10
        background.update()
        draw(win, dinos, obs, background, score, pop.generation)


def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    pop.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
