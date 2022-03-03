
# Importing Libraries and Python Files
import pygame
import os
import sys
import trainingmodel as TrainAI
import testingmodel as TestAI

pygame.init()

# Global Constanst
SCREEN_HEIGHT = 700  # Screen Height of the game window
SCREEN_WIDTH = 1000  # Screen Width of the game window
# pygame.NOFRAME removes the task bar from the game window
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)

# Background image for the main menu
DinoBG = pygame.image.load(os.path.join("./Assets/Mainmenu", "DinoBG.png"))

# Class for the buttons in the main menu


class MenuButton():
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


def MainMenu():
    while True:
        SCREEN.blit(DinoBG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        TRAIN_BUTTON = MenuButton(image=pygame.image.load(
            "./Assets/mainmenu/TrainButton.png"), hoverimage=pygame.image.load(
            "./Assets/mainmenu/TrainButtonHover.png"), pos=(310, 260))
        TEST_BUTTON = MenuButton(image=pygame.image.load(
            "./Assets/mainmenu/TestButton.png"), hoverimage=pygame.image.load(
            "./Assets/mainmenu/TestButtonHover.png"), pos=(310, 393))
        QUIT_BUTTON = MenuButton(image=pygame.image.load(
            "./Assets/mainmenu/QuitButton.png"), hoverimage=pygame.image.load(
            "./Assets/mainmenu/QuitButtonHover.png"), pos=(310, 526))

        # List to contain the buttons
        ButtonList = [TRAIN_BUTTON, TEST_BUTTON, QUIT_BUTTON]

        for button in ButtonList:
            # Changes the color of the buttons on hover
            button.ButtonHover(MENU_MOUSE_POS, button.image, button.hoverimage)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if TRAIN_BUTTON.checkForInput(MENU_MOUSE_POS):
                    TrainAI.trainrun()
                if TEST_BUTTON.checkForInput(MENU_MOUSE_POS):
                    TestAI.testrun()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


if __name__ == "__main__":
    MainMenu()
