
# LIBRARY IMPORTS
import pygame  # pygame module
import sys
import os
import neat
import time
import random
import mainmenu
import pickle  # use this module to save the best bird into a file and then you can load in the file and use the neural network associated with it


pygame.font.init()
pygame.init()
# sets the title to the text within the quotes
pygame.display.set_caption("FlappyBirdAI (NEAT)")

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)

FONT = pygame.font.SysFont("comicsans", 50)
FONT2 = pygame.font.Font('freesansbold.ttf', 20)
FONT3 = pygame.font.SysFont("comicsans", 35)

GEN = 0  # keeping track of the current generation for visual purpose

# tranform.scale2x enlarges the image
BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("./imgs", "bird1.png"))
                             ), pygame.transform.scale2x(pygame.image.load(os.path.join("./imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("./imgs", "bird3.png")))
]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(
    os.path.join("./imgs", "pipe.png")))

BASE_IMG = pygame.transform.scale2x(pygame.image.load(
    os.path.join("./imgs", "base.png")))


background_image = pygame.image.load(
    os.path.join("./imgs", "bg.png"))

BG_IMG = pygame.transform.scale(background_image, (500, 700))

TrainBG = pygame.image.load(os.path.join(
    "./imgs", "TrainingStatsRect.png"))


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # Will be used to tilt the bird up and down
    ROT_VEL = 20  # Rotation velocity
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self. y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0  # keeps track of when we last jumped
        self.height = self.y

    def move(self):
        self.tick_count += 1

        displacement = self.vel*self.tick_count + 1.5*self.tick_count**2

        if displacement >= 16:  # defining the terminal velocity here
            displacement = 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        # tilting conditions defined below
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > - 90:
                self.tilt -= self.ROT_VEL

    def draw(self, SCREEN):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]

        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]

        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]

        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]

        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # this if statement prevents the bird from flapping when it's doing a 90 degree nose dive downwards
        if self.tilt <= -90:

            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # rotates the bird on its center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)

        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center)

        SCREEN.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200  # the space between the 2 pipes
    VEL = 5  # the speed at which the pipes will move across the screen

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        # this line flips the pipe image for the top pipe
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False  # This is set to true if the bird has already passed the pipe
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)

        # math for setting the top pipe below
        self.top = self.height - self.PIPE_TOP.get_height()

        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.PIPE_TOP, (self.x, self.top))  # displays the top pipe

        SCREEN.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        # in this project, we will you masks for pixel perfect collisions
        # mask is basically an array/list of location of the pixels inside of a box

        bird_mask = bird.get_mask()

        top_pipe_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_pipe_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # we have to calculate the offset.
        # An offset is how far these masks are from eachother. The distance between an 2 left hand corners in the case of pygame

        # the offset of the bird from the top pipe
        top_offset = (self.x - bird.x, self.top - round(bird.y))

        # the offset of the bird from the bottom pipe
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # returns None if they don't collide
        bottom_point = bird_mask.overlap(bottom_pipe_mask, bottom_offset)

        top_point = bird_mask.overlap(top_pipe_mask, top_offset)

        # if there is a collision, it returns True otherwise it returns False
        if top_point or bottom_point:
            return True

        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # these statements creates the infinite moving background
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, SCREEN):
        SCREEN.blit(self.IMG, (self.x1, self.y))
        SCREEN.blit(self.IMG, (self.x2, self.y))


class MenuButton():  # Custom class for buttons in pygame
    # Init method defined
    def __init__(self, image, hoverimage, pos):
        self.image = image
        self.hoverimage = hoverimage
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    # Method to update the button
    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)

    # Method to checkout for mouse inputs
    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    # Method to change the text color of the button on hover
    def ButtonHover(self, position, image, hoverimage):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.image = hoverimage
        else:
            self.image = image


def draw_window(SCREEN, birds, pipes, base, score, ButtonList, MENU_MOUSE_POS):
    global population

    SCREEN.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(SCREEN)

    base.draw(SCREEN)

    for bird in birds:
        bird.draw(SCREEN)

    # Renders the Training Stats Rectangle on the screen
    SCREEN.blit(TrainBG, (500, 0))

    score_text = FONT3.render(str(score), True, (255, 255, 255))
    SCREEN.blit(score_text, (880, 52))

    generation_text = FONT.render(
        "Generation: " + str(population.generation + 1), 1, "#AD06E8")
    SCREEN.blit(generation_text, (640, 350))

    population_text = FONT.render(
        "Birds Remaining: " + str(len(birds)), 1, "#AD06E8")
    SCREEN.blit(population_text, (590, 450))

    for button in ButtonList:
        # Changes the color of the buttons on hover
        button.ButtonHover(MENU_MOUSE_POS, button.image, button.hoverimage)
        button.update(SCREEN)

    pygame.display.update()


# this fitness function was orginally named main()
def FitnessFunction(genomes, config):
    global nets, ge, birds, population

    nets = []
    ge = []
    birds = []  # bird = Bird(210, 300) # orginal code line

    # genomes returns a tuple (id, object). We only need the object
    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(210, 300))
        ge.append(genome)
        genome.fitness = 0  # setting the initial fitness of our birds to 0

    base = Base(620)
    pipes = [Pipe(550)]
    clock = pygame.time.Clock()

    score = 0

    run = True

    while run:
        clock.tick(30)

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        # this code tackles the problem where there are 2 pairs of pipes on the screen and the bird doesn't know which to calculate the distance from
        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1

        else:  # if there are no birds, we quit this generation/running the game
            run = False
            break

        # inputs to the neural network
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1  # initial survival fitness given to the bird

            # Activating the neural network with our inputs

            # The comment below talks about the distance calculation of the bird from the top and bottom pipes.
            #  abs(bird.y - pipes[pipe_index].height) - height here gives us the location of the top pipe, abs(bird.y - pipe[pipe_index].bottom) - bottom gives us the location of the bottom pipe

            output = nets[x].activate((bird.y, abs(
                bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))

            if output[0] > 0.5:  # output is a list
                bird.jump()

        add_pipe = False
        remove_pipe = []
        for pipe in pipes:

            for x, bird in enumerate(birds):

                if pipe.collide(bird):
                    # decrements the fitness if a bird hits a pipe
                    ge[x].fitness -= 1

                    # removing bird, its neural net, and its genes from the 3 lists
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipe.append(pipe)

            pipe.move()

        # appends a new pipe for display once we pass a pipe and adds the scores
        if add_pipe:

            for g in ge:
                g.fitness += 5  # incrementing the fitness of a bird if it passes thru a pipe succesfully

                # Awards fitness Threshold if the Game Score is 20
                if score == 20:
                    g.fitness += 100
                    break

            score += 1

            pipes.append(Pipe(550))

        # removes the passed pipes from the remove_pipe list
        for r in remove_pipe:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            # checks whether the bird has hit the floor
            if bird.y + bird.img.get_height() >= 620 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()  # displays the animation of the moving base

        BACK_BUTTON = MenuButton(image=pygame.image.load(
            "./imgs/GameBackButton.png"), hoverimage=pygame.image.load(
            "./imgs/GameBackButtonHover.png"), pos=(600, 635))
        QUIT_BUTTON = MenuButton(image=pygame.image.load(
            "./imgs/GameQuitButton.png"), hoverimage=pygame.image.load(
            "./imgs/GameQuitButtonHover.png"), pos=(900, 635))

        # List to contain the buttons
        ButtonList = [BACK_BUTTON, QUIT_BUTTON]

        draw_window(SCREEN, birds, pipes, base,
                    score, ButtonList, MENU_MOUSE_POS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                    mainmenu.MainMenu()
                    pass
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()


def run(config_path):
    global population

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    population = neat.Population(config)

    # adding stats reporters. These are optional
    # these give us some statistical output whenever we run the program
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    FlappyBirdWinner = population.run(FitnessFunction, 4)

    # Saving the model using the pickle module
    with open('BestBirdNN', 'wb') as f:
        pickle.dump(FlappyBirdWinner, f)
        # f.close()


def trainrun():
    # this gives us the path to our local/working/current directory
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'trainconfig.txt')

    run(config_path)


if __name__ == "__main__":
    trainrun()
