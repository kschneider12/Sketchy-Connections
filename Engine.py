import pygame
from Button import Button

class Engine():
    def __init__(self):
        # flags
        self.exit = False

        #pygame info
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Sketchy Connections")
        self.clock = pygame.time.Clock()

        # Input management
        self.scene = "welcome"
        self.key_status = {
            pygame.K_s: False,
            pygame.K_w: False,
            pygame.K_SPACE: False
        }
        self.mouse_buttons = [False, False]
        self.mouse_buttons_last_frame = [False, False]
        self.mouse_pos = [0, 0]

        # UI Management
        self.active_buttons = []


    def run(self):
        while True:
            self.mouse_buttons_last_frame[0] = self.mouse_buttons[0]
            self.mouse_buttons_last_frame[1] = self.mouse_buttons[1]
            self.getInputs()
            self.manageButtons()

            # Behaviors depending on scene
            match self.scene:
                case "welcome":
                    self.welcome()
                case "draw":
                    self.draw()
                case "guess":
                    self.guess()
                case "game_over":
                    self.game_over()
            if self.exit:
                pygame.quit()
                break
            # Update the Screen
            self.drawUI()
            pygame.display.flip()
            self.clock.tick(60)

    def getInputs(self):
        self.mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit = True
            elif event.type == pygame.KEYDOWN:
                if event.key in self.key_status:
                    self.key_status[event.key] = True
            elif event.type == pygame.KEYUP:
                if event.key in self.key_status:
                    self.key_status[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_buttons[0] = True
                elif event.button == 3:
                    self.mouse_buttons[1] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_buttons[0] = False
                elif event.button == 3:
                    self.mouse_buttons[1] = False

    def drawUI(self):
        self.screen.fill((0, 0, 0))
        for button in self.active_buttons:
            button.draw(self.screen)

    def manageButtons(self):
        just_clicked = [not self.mouse_buttons_last_frame[0] and self.mouse_buttons[0],
                        not self.mouse_buttons_last_frame[1] and self.mouse_buttons[1]]
        for button in self.active_buttons:
            command = button.behave(self.mouse_pos, just_clicked)
            if command:
                command()


    def welcome(self):
        # This is the game loop for the welcome screen
        print("WELCOMING!")
        if self.key_status[pygame.K_SPACE]:
            self.scene = "draw"
            self.active_buttons = [Button((100,100), (50,30), "C:/Users/Kentd/OneDrive/Desktop/project/assets/photos/block.png", self.switchToGuessing),
                                   Button((250,100), (100,100), "C:/Users/Kentd/OneDrive/Desktop/project/assets/photos/block.png", self.switchToWelcome)]

    def draw(self):
        #print("DRAWING!")
        '''
        Notes on data structure:
            [[index, colorID], [],[],...] in order of pixels added
            index is 0 -> length*width
            -----------------
            -0              -
            -               -
            -            255-
            -----------------
            Keep brush type as a settable variable for easy switching when buttons implemented (including eraser)
        '''
        # This is the game loop for the drawing screen
        return

    def guess(self):
        print("GUESSING!")
        if self.key_status[pygame.K_s]:
            self.scene = "welcome"
            self.active_buttons = []
        # This is the game loop for the guessing screen
        return

    def game_over(self):
        # This is the game loop for the game over screen
        return


#------------------------------------------------------------------------------------------------
#Button Commands listed below (Nothing else under this line!)
#------------------------------------------------------------------------------------------------

    def switchToGuessing(self):
        self.scene = "guess"
        self.active_buttons = []

    def switchToWelcome(self):
        self.scene = "welcome"
        self.active_buttons = []